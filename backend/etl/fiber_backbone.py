"""
ETL pipeline: Fiber-optic backbone routes.

Primary sources: CRTC broadband availability data, known carrier backbone maps.
Fallback: mock data for major Ontario fiber corridors (Bell, Rogers, Cogeco, Zayo).
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import FiberRoute
from etl.base import BasePipeline

# CRTC Open Data portal (broadband availability).  The real dataset is a CSV;
# for the GeoJSON pipeline we rely on mock/cached data until a proper spatial
# source is published.
CRTC_URL = (
    "https://open.canada.ca/data/api/3/action/package_show"
    "?id=broadband-coverage"
)


class FiberBackbonePipeline(BasePipeline):
    """Ingest fiber backbone route data into PostGIS."""

    pipeline_name = "fiber_backbone"
    default_source_url = CRTC_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_fiber_routes
            self.logger.info("Using mock fiber backbone data")
            return {"type": "FeatureCollection", "features": generate_fiber_routes()}
        # The CRTC dataset does not currently publish spatial GeoJSON, so we
        # always fall back to mock data for now.  When a proper source becomes
        # available, swap in the real fetch here.
        try:
            return self._http_get(self.default_source_url)
        except Exception as exc:
            self.logger.warning(
                "Live fetch failed or unsupported (%s), using mock data", exc
            )
            from etl.mock_data import generate_fiber_routes
            return {"type": "FeatureCollection", "features": generate_fiber_routes()}

    def parse(self, raw_data: Any) -> list[dict]:
        records: list[dict] = []
        features = raw_data.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])
            if not coords or len(coords) < 2:
                continue

            records.append({
                "name": props.get("name", "Unknown Route"),
                "provider": props.get("provider", "Unknown"),
                "route_type": props.get("route_type", "backbone"),
                "capacity_gbps": (
                    float(props["capacity_gbps"]) if props.get("capacity_gbps") else None
                ),
                "lit": props.get("lit", "unknown"),
                "source": props.get("source", "crtc_broadband"),
                "source_id": str(
                    props.get("source_id")
                    or f"fiber_{hash(str(coords)) % 10**8}"
                ),
                "coordinates": coords,
            })
        return records

    def _validate_record(self, record: dict) -> bool:
        coords = record.get("coordinates", [])
        if len(coords) < 2:
            return False
        lon, lat = coords[0][0], coords[0][1]
        if not (-95.2 <= lon <= -74.3 and 41.7 <= lat <= 56.9):
            return False
        return True

    def transform(self, records: list[dict]) -> list[dict]:
        transformed: list[dict] = []
        for rec in records:
            line = LineString(rec["coordinates"])
            transformed.append({
                "provider": rec["provider"],
                "route_type": rec["route_type"],
                "source_id": rec["source_id"],
                "geom": from_shape(line, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(FiberRoute.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "provider": stmt.excluded.provider,
                "route_type": stmt.excluded.route_type,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
