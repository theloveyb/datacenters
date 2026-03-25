"""
Scoring engine for data-center site suitability analysis.

Computes a composite 0-100 score for each parcel by evaluating five
categories (power, fiber, zoning, size, constraints) using PostGIS
spatial queries and configurable weights.
"""

import logging
from datetime import datetime, timezone

from geoalchemy2.functions import (
    ST_DWithin,
    ST_Distance,
    ST_Intersects,
)
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.models import (
    Constraint,
    FiberRoute,
    Parcel,
    ParcelScore,
    Substation,
    Zoning,
)
from app.scoring.weights import WeightConfig

logger = logging.getLogger(__name__)

# Metres-per-kilometre constant for geography casts.
M_PER_KM = 1000.0


class ScoringEngine:
    """Evaluate parcels for data-center suitability."""

    def __init__(self, db: Session, config: WeightConfig | None = None):
        self.db = db
        self.config = config or WeightConfig()
        self.config.validate()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_all_scores(self) -> int:
        """Score every parcel in the database.  Returns the count scored."""
        parcels = self.db.execute(select(Parcel)).scalars().all()
        count = 0
        for parcel in parcels:
            self._score_parcel(parcel)
            count += 1
            # Flush in batches to keep memory reasonable.
            if count % 200 == 0:
                self.db.flush()
        self.db.commit()
        logger.info("Scored %d parcels", count)
        return count

    def compute_parcel_score(self, parcel_id: int) -> ParcelScore | None:
        """Score a single parcel by ID.  Returns the new ParcelScore row."""
        parcel = self.db.get(Parcel, parcel_id)
        if parcel is None:
            logger.warning("Parcel %d not found", parcel_id)
            return None
        score = self._score_parcel(parcel)
        self.db.commit()
        return score

    # ------------------------------------------------------------------
    # Internal scoring pipeline
    # ------------------------------------------------------------------

    def _score_parcel(self, parcel: Parcel) -> ParcelScore:
        """Run all sub-scores, persist, and return the ParcelScore."""
        power_result = self._power_score(parcel)
        fiber_result = self._fiber_score(parcel)
        zoning_raw = self._zoning_score(parcel)
        size_raw = self._size_score(parcel)
        constraint_result = self._constraint_score(parcel)

        w = self.config.weights
        overall = (
            power_result["score"] * (w["power"] / 100)
            + fiber_result["score"] * (w["fiber"] / 100)
            + zoning_raw * (w["zoning"] / 100)
            + size_raw * (w["size"] / 100)
            + constraint_result["score"] * (w["constraint"] / 100)
        )
        # Scale to 0-100.
        overall = round(min(max(overall * 100, 0), 100), 2)

        score = ParcelScore(
            parcel_id=parcel.id,
            overall_score=overall,
            power_score=round(power_result["score"] * 100, 2),
            fiber_score=round(fiber_result["score"] * 100, 2),
            zoning_score=round(zoning_raw * 100, 2),
            size_score=round(size_raw * 100, 2),
            constraint_score=round(constraint_result["score"] * 100, 2),
            nearest_substation_km=power_result.get("nearest_km"),
            nearest_substation_kv=power_result.get("nearest_kv"),
            nearest_fiber_km=fiber_result.get("nearest_km"),
            risk_flags=constraint_result.get("flags"),
            computed_at=datetime.now(timezone.utc),
        )
        self.db.add(score)
        return score

    # ------------------------------------------------------------------
    # Category scorers (each returns a 0-1 normalised value)
    # ------------------------------------------------------------------

    def _power_score(self, parcel: Parcel) -> dict:
        """Score based on distance to nearest substation, weighted by voltage.

        Uses PostGIS geography cast (::geography) for metre-accurate distance
        on SRID 4326 data.
        """
        max_dist_m = self.config.max_power_distance_km * M_PER_KM

        # Find substations within search radius, ordered by distance.
        stmt = (
            select(
                Substation.voltage_kv,
                func.ST_Distance(
                    func.cast(parcel.geom, func.Geography()),
                    func.cast(Substation.geom, func.Geography()),
                ).label("dist_m"),
            )
            .where(
                func.ST_DWithin(
                    func.cast(parcel.geom, func.Geography()),
                    func.cast(Substation.geom, func.Geography()),
                    max_dist_m,
                )
            )
            .order_by("dist_m")
            .limit(5)
        )
        rows = self.db.execute(stmt).all()

        if not rows:
            return {"score": 0.0, "nearest_km": None, "nearest_kv": None}

        best_score = 0.0
        nearest_km = rows[0].dist_m / M_PER_KM
        nearest_kv = rows[0].voltage_kv

        for row in rows:
            dist_km = row.dist_m / M_PER_KM
            # Linear distance decay.
            proximity = max(
                1.0 - dist_km / self.config.max_power_distance_km, 0.0
            )
            # Voltage tier multiplier.
            tier = self._voltage_tier(row.voltage_kv)
            candidate = proximity * tier
            if candidate > best_score:
                best_score = candidate
                nearest_km = dist_km
                nearest_kv = row.voltage_kv

        return {
            "score": min(best_score, 1.0),
            "nearest_km": round(nearest_km, 2),
            "nearest_kv": nearest_kv,
        }

    def _voltage_tier(self, kv: float) -> float:
        """Map a voltage in kV to its tier multiplier."""
        tiers = self.config.voltage_tiers
        if kv >= 500:
            return tiers["500kv"]
        elif kv >= 230:
            return tiers["230kv"]
        elif kv >= 115:
            return tiers["115kv"]
        else:
            return tiers["below"]

    def _fiber_score(self, parcel: Parcel) -> dict:
        """Score based on distance to nearest fiber route.

        Awards a bonus when multiple providers are reachable.
        """
        max_dist_m = self.config.max_fiber_distance_km * M_PER_KM

        stmt = (
            select(
                FiberRoute.provider,
                func.ST_Distance(
                    func.cast(parcel.geom, func.Geography()),
                    func.cast(FiberRoute.geom, func.Geography()),
                ).label("dist_m"),
            )
            .where(
                func.ST_DWithin(
                    func.cast(parcel.geom, func.Geography()),
                    func.cast(FiberRoute.geom, func.Geography()),
                    max_dist_m,
                )
            )
            .order_by("dist_m")
            .limit(10)
        )
        rows = self.db.execute(stmt).all()

        if not rows:
            return {"score": 0.0, "nearest_km": None}

        nearest_km = rows[0].dist_m / M_PER_KM
        proximity = max(
            1.0 - nearest_km / self.config.max_fiber_distance_km, 0.0
        )

        # Count distinct providers within range.
        providers = {r.provider for r in rows if r.provider}
        bonus = (
            self.config.multi_provider_bonus if len(providers) >= 2 else 0.0
        )

        score = min(proximity + bonus, 1.0)
        return {"score": score, "nearest_km": round(nearest_km, 2)}

    def _zoning_score(self, parcel: Parcel) -> float:
        """Score based on zoning compatibility.

        1.0 -- parcel intersects a dc_compatible industrial zone
        0.7 -- parcel intersects a dc_compatible zone (non-industrial)
        0.3 -- parcel intersects a zone that is not flagged dc_compatible
        0.0 -- no zoning information available
        """
        stmt = (
            select(Zoning.dc_compatible, Zoning.zone_code)
            .where(func.ST_Intersects(parcel.geom, Zoning.geom))
        )
        rows = self.db.execute(stmt).all()

        if not rows:
            return 0.0

        best = 0.0
        for row in rows:
            if row.dc_compatible:
                code = (row.zone_code or "").upper()
                # Industrial codes typically start with M or I.
                if code.startswith(("M", "I", "EMP", "IND")):
                    best = max(best, 1.0)
                else:
                    best = max(best, 0.7)
            else:
                best = max(best, 0.3)
        return best

    def _size_score(self, parcel: Parcel) -> float:
        """Score based on parcel area.

        Optimal range: 20-200 acres (full score).
        Penalty below 10 acres or above 500 acres.
        """
        acres = parcel.area_acres
        if acres is None or acres <= 0:
            return 0.0

        cfg = self.config
        if cfg.optimal_min_acres <= acres <= cfg.optimal_max_acres:
            return 1.0
        elif acres < cfg.penalty_below_acres:
            # Steep ramp from 0 at 0 acres to ~0.5 at penalty threshold.
            return 0.5 * (acres / cfg.penalty_below_acres)
        elif acres < cfg.optimal_min_acres:
            # Ramp from 0.5 at penalty threshold to 1.0 at optimal min.
            ratio = (acres - cfg.penalty_below_acres) / (
                cfg.optimal_min_acres - cfg.penalty_below_acres
            )
            return 0.5 + 0.5 * ratio
        elif acres <= cfg.penalty_above_acres:
            # Gentle decline from 1.0 at optimal max to 0.6 at penalty max.
            ratio = (acres - cfg.optimal_max_acres) / (
                cfg.penalty_above_acres - cfg.optimal_max_acres
            )
            return 1.0 - 0.4 * ratio
        else:
            # Beyond penalty_above_acres -- diminishing score.
            return max(0.6 - 0.1 * ((acres - cfg.penalty_above_acres) / 100), 0.1)

    def _constraint_score(self, parcel: Parcel) -> dict:
        """Deduct for overlapping environmental / regulatory constraints.

        Starts at 1.0 and subtracts per overlapping constraint based on
        severity.  Returns risk_flags dict for transparency.
        """
        stmt = (
            select(Constraint.constraint_type, Constraint.severity)
            .where(func.ST_Intersects(parcel.geom, Constraint.geom))
        )
        rows = self.db.execute(stmt).all()

        if not rows:
            return {"score": 1.0, "flags": {}}

        deductions = self.config.constraint_deductions
        total_deduction = 0.0
        flags: dict[str, str] = {}
        for row in rows:
            severity = row.severity.lower() if row.severity else "medium"
            deduction = deductions.get(severity, 0.5)
            total_deduction += deduction
            flags[row.constraint_type] = severity

        score = max(1.0 - total_deduction, 0.0)
        return {"score": score, "flags": flags}
