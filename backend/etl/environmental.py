"""
ETL pipeline: Environmental constraints (floodplains, wetlands, conservation areas).

Primary source: Ontario GeoHub – various environmental layers
Fallback: mock constraint polygons along Ontario waterways and flood-prone areas.
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Constraint
from etl.base import BasePipeline

# Ontario GeoHub endpoints for environmental data.
FLOODPLAIN_URL = (
    "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/"
    "LIO_OPEN_DATA/LIO_Open01/MapServer/3/query"
)
WETLAND_URL = (
    "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/"
    "LIO_OPEN_DATA/LIO_Open01/MapServer/6/query"
)
GEOHUB_PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
    "resultRecordCount": "2000",
}

# Severity classification rules.
CONSTRAINT_SEVERITY: dict[str, str] = {
    # Floodplain types
    "floodway": "hard_block",
    "flood_fringe": "soft_block",
    "special_policy_area": "review_required",
    # Wetland types
    "provincially_significant_wetland": "hard_block",
    "wetland": "soft_block",
    "evaluated_wetland": "soft_block",
    "unevaluated_wetland": "review_required",
    # Conservation
    "conservation_area": "review_required",
    "ansi_life_science": "soft_block",
    "ansi_earth_science": "review_required",
    # Species
    "endangered_species_habitat": "hard_block",
    "threatened_species_habitat": "soft_block",
}


def classify_severity(constraint_type: str) -> str:
    """Return severity level for a constraint type string."""
    normalised = constraint_type.lower().strip().replace(" ", "_").replace("-", "_")
    if normalised in CONSTRAINT_SEVERITY:
        return CONSTRAINT_SEVERITY[normalised]
    # Heuristic fallback.
    if "flood" in normalised and "way" in normalised:
        return "hard_block"
    if "flood" in normalised:
        return "soft_block"
    if "wetland" in normalised and "significant" in normalised:
        return "hard_block"
    if "wetland" in normalised:
        return "soft_block"
    if "endangered" in normalised:
        return "hard_block"
    return "review_required"


class EnvironmentalPipeline(BasePipeline):
    """Ingest environmental constraint polygons into PostGIS."""

    pipeline_name = "environmental"
    default_source_url = FLOODPLAIN_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_environmental_constraints
            self.logger.info("Using mock environmental constraint data")
            return {
                "type": "FeatureCollection",
                "features": generate_environmental_constraints(),
            }

        all_features: list[dict] = []

        # Attempt to fetch from multiple layers.
        for url, label in [
            (FLOODPLAIN_URL, "floodplains"),
            (WETLAND_URL, "wetlands"),
        ]:
            try:
                data = self._http_get(url, params=GEOHUB_PARAMS)
                features = data.get("features", [])
                self.logger.info("Fetched %d %s features", len(features), label)
                all_features.extend(features)
            except Exception as exc:
                self.logger.warning("Failed to fetch %s: %s", label, exc)

        if not all_features:
            self.logger.warning("No live data fetched, falling back to mock data")
            from etl.mock_data import generate_environmental_constraints
            return {
                "type": "FeatureCollection",
                "features": generate_environmental_constraints(),
            }

        return {"type": "FeatureCollection", "features": all_features}

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

            constraint_type = (
                props.get("CONSTRAINT_TYPE")
                or props.get("constraint_type")
                or props.get("WETLAND_TYPE")
                or props.get("FLOOD_TYPE")
                or "unknown"
            )
            severity = classify_severity(constraint_type)

            name = (
                props.get("NAME")
                or props.get("name")
                or props.get("WETLAND_NAME")
                or props.get("AREA_NAME")
                or f"{constraint_type} area"
            )

            records.append({
                "name": str(name).strip(),
                "constraint_type": constraint_type.lower().strip().replace(" ", "_"),
                "severity": severity,
                "description": props.get("DESCRIPTION", props.get("description")),
                "authority": (
                    props.get("AUTHORITY")
                    or props.get("authority")
                    or props.get("CONSERVATION_AUTHORITY")
                ),
                "regulation": props.get("REGULATION", props.get("regulation")),
                "source": props.get("source", "ontario_geohub"),
                "source_id": str(
                    props.get("OBJECTID")
                    or props.get("source_id")
                    or f"env_{hash(str(coords)) % 10**8}"
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
                "constraint_type": rec["constraint_type"],
                "severity": rec["severity"],
                "source_id": rec["source_id"],
                "geom": from_shape(polygon, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(Constraint.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "constraint_type": stmt.excluded.constraint_type,
                "severity": stmt.excluded.severity,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
