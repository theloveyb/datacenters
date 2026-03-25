"""
ETL pipeline: Municipal zoning data.

Primary source: Municipal open-data portals (Toronto, York Region, Durham, etc.)
Fallback: mock zoning polygons with realistic zone code classification.
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Zoning
from etl.base import BasePipeline

# Toronto Open Data zoning by-law (representative; each municipality has its own).
TORONTO_ZONING_URL = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
    "?id=zoning-by-law"
)

# Zone codes considered data-center-compatible (industrial).
DC_COMPATIBLE_CODES = frozenset({
    "M1", "M2", "M3", "M4", "M5",       # General / heavy industrial
    "EL", "EH",                          # Employment light / heavy
    "E1", "E2", "E3",                    # Employment zones (York Region)
    "EM", "EM1", "EM2",                  # Employment
    "MU", "MU1", "MU2",                  # Mixed-use (sometimes compatible)
    "PI",                                # Prestige industrial
    "GE", "GE-1", "GE-2",               # General employment
    "IN", "IN1", "IN2",                  # Industrial (Durham)
    "I", "I1", "I2",                     # Industrial (generic)
})

# Categories for classification.
ZONE_CATEGORIES: dict[str, str] = {}
for _code in ("M1", "M2", "M3", "M4", "M5", "EL", "EH", "E1", "E2", "E3",
               "EM", "EM1", "EM2", "PI", "GE", "GE-1", "GE-2", "IN", "IN1",
               "IN2", "I", "I1", "I2"):
    ZONE_CATEGORIES[_code] = "industrial"
for _code in ("C1", "C2", "C3", "C4", "CR", "CG", "CO"):
    ZONE_CATEGORIES[_code] = "commercial"
for _code in ("R1", "R2", "R3", "R4", "R5", "RM", "RD", "RT"):
    ZONE_CATEGORIES[_code] = "residential"
for _code in ("A", "A1", "A2", "AG", "RU"):
    ZONE_CATEGORIES[_code] = "agricultural"
for _code in ("MU", "MU1", "MU2"):
    ZONE_CATEGORIES[_code] = "mixed_use"
for _code in ("OS", "OS1", "OS2", "G", "P"):
    ZONE_CATEGORIES[_code] = "open_space"


def classify_zone(code: str) -> tuple[bool, str]:
    """Return (dc_compatible, category) for a zone code string."""
    normalised = code.strip().upper().split("-")[0].split(" ")[0]
    # Check progressively shorter prefixes.
    for length in (len(normalised), 3, 2, 1):
        prefix = normalised[:length]
        if prefix in DC_COMPATIBLE_CODES:
            return True, ZONE_CATEGORIES.get(prefix, "industrial")
        if prefix in ZONE_CATEGORIES:
            return prefix in DC_COMPATIBLE_CODES, ZONE_CATEGORIES[prefix]
    return False, "other"


class ZoningPipeline(BasePipeline):
    """Ingest municipal zoning polygon data into PostGIS."""

    pipeline_name = "zoning"
    default_source_url = TORONTO_ZONING_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_zoning
            self.logger.info("Using mock zoning data")
            return {"type": "FeatureCollection", "features": generate_zoning()}
        try:
            return self._http_get(self.default_source_url)
        except Exception as exc:
            self.logger.warning("Live fetch failed (%s), falling back to mock data", exc)
            from etl.mock_data import generate_zoning
            return {"type": "FeatureCollection", "features": generate_zoning()}

    def parse(self, raw_data: Any) -> list[dict]:
        records: list[dict] = []
        features = raw_data.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})

            if geom.get("type") not in ("Polygon", "MultiPolygon"):
                continue
            coords = geom.get("coordinates")
            if not coords:
                continue
            if geom["type"] == "MultiPolygon":
                coords = coords[0]

            zone_code = (
                props.get("ZONE_CODE")
                or props.get("zone_code")
                or props.get("ZN_ZONE")
                or "Unknown"
            )
            dc_compatible, category = classify_zone(zone_code)

            records.append({
                "zone_code": zone_code.strip().upper(),
                "zone_description": props.get("ZONE_DESC", props.get("zone_description", "")),
                "municipality": props.get("MUNICIPALITY", props.get("municipality", "")),
                "dc_compatible": dc_compatible,
                "zone_category": category,
                "bylaw_number": props.get("BYLAW", props.get("bylaw_number")),
                "source": props.get("source", "municipal_opendata"),
                "source_id": str(
                    props.get("OBJECTID")
                    or props.get("source_id")
                    or f"zone_{hash(str(coords)) % 10**8}"
                ),
                "coordinates": coords,
            })
        return records

    def _validate_record(self, record: dict) -> bool:
        coords = record.get("coordinates", [])
        if not coords or not coords[0]:
            return False
        first = coords[0][0] if isinstance(coords[0][0], (list, tuple)) else coords[0]
        lon, lat = first[0], first[1]
        if not (-95.2 <= lon <= -74.3 and 41.7 <= lat <= 56.9):
            return False
        return True

    def transform(self, records: list[dict]) -> list[dict]:
        transformed: list[dict] = []
        for rec in records:
            try:
                polygon = Polygon(rec["coordinates"][0])
                if not polygon.is_valid:
                    polygon = polygon.buffer(0)
            except Exception:
                continue

            transformed.append({
                "zone_code": rec["zone_code"],
                "zone_desc": rec.get("zone_description", ""),
                "municipality": rec["municipality"],
                "dc_compatible": rec["dc_compatible"],
                "source_id": rec["source_id"],
                "geom": from_shape(polygon, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(Zoning.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "zone_code": stmt.excluded.zone_code,
                "zone_desc": stmt.excluded.zone_desc,
                "municipality": stmt.excluded.municipality,
                "dc_compatible": stmt.excluded.dc_compatible,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
