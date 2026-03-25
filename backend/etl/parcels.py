"""
ETL pipeline: Ontario land parcels.

Primary source: Ontario GeoHub – Ontario Parcel dataset
Fallback: mock parcel polygons in key data-center-friendly municipalities.
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, shape
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Parcel
from etl.base import BasePipeline

GEOHUB_URL = (
    "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/"
    "LIO_OPEN_DATA/LIO_Open01/MapServer/25/query"
)
GEOHUB_PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
    "resultRecordCount": "2000",
}

# Conversion constants.
SQM_PER_ACRE = 4046.8564224


class ParcelsPipeline(BasePipeline):
    """Ingest Ontario land parcel data into PostGIS."""

    pipeline_name = "parcels"
    default_source_url = GEOHUB_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_parcels
            self.logger.info("Using mock parcel data")
            return {"type": "FeatureCollection", "features": generate_parcels()}
        try:
            return self._http_get(self.default_source_url, params=GEOHUB_PARAMS)
        except Exception as exc:
            self.logger.warning("Live fetch failed (%s), falling back to mock data", exc)
            from etl.mock_data import generate_parcels
            return {"type": "FeatureCollection", "features": generate_parcels()}

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

            # Normalise MultiPolygon to first polygon.
            if geom["type"] == "MultiPolygon":
                coords = coords[0]

            pin = props.get("PIN", props.get("pin"))
            arn = props.get("ARN", props.get("arn"))
            municipality = (
                props.get("MUNICIPALITY", "")
                or props.get("municipality", "")
                or props.get("MUNIC_NAME", "")
            )
            area_sqm = props.get("AREA_SQM", props.get("area_sqm"))
            area_acres = props.get("area_acres")
            if area_sqm and not area_acres:
                area_acres = float(area_sqm) / SQM_PER_ACRE
            elif area_acres:
                area_acres = float(area_acres)
                area_sqm = area_acres * SQM_PER_ACRE

            records.append({
                "pin": str(pin) if pin else None,
                "arn": str(arn) if arn else None,
                "municipality": str(municipality).strip(),
                "address": props.get("ADDRESS", props.get("address")),
                "area_acres": round(area_acres, 2) if area_acres else None,
                "area_sqm": round(float(area_sqm), 2) if area_sqm else None,
                "current_use": props.get("CURRENT_USE", props.get("current_use")),
                "owner_type": props.get("OWNER_TYPE", props.get("owner_type", "private")),
                "source": "ontario_geohub",
                "source_id": str(
                    props.get("OBJECTID")
                    or props.get("source_id")
                    or f"parcel_{pin or hash(str(coords)) % 10**8}"
                ),
                "coordinates": coords,
            })
        return records

    def _validate_record(self, record: dict) -> bool:
        coords = record.get("coordinates", [])
        if not coords or not coords[0]:
            return False
        # Check first vertex is within Ontario.
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
                "pin": rec["pin"],
                "municipality": rec["municipality"],
                "area_sqm": rec["area_sqm"],
                "current_use": rec["current_use"],
                "source_id": rec["source_id"],
                "geom": from_shape(polygon, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(Parcel.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "pin": stmt.excluded.pin,
                "municipality": stmt.excluded.municipality,
                "area_sqm": stmt.excluded.area_sqm,
                "current_use": stmt.excluded.current_use,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
