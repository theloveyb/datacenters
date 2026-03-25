"""
ETL pipeline: Hydro One / IESO electrical substations.

Primary source: Ontario GeoHub – Hydro One Transmission Stations
Fallback: mock data generated from known Ontario substation locations.
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Substation
from etl.base import BasePipeline

# Ontario GeoHub ArcGIS REST endpoint for Hydro One transmission stations.
GEOHUB_URL = (
    "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/"
    "LIO_OPEN_DATA/LIO_Open01/MapServer/17/query"
)
GEOHUB_PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
    "resultRecordCount": "2000",
}


class HydroSubstationsPipeline(BasePipeline):
    """Ingest Hydro One / IESO substation data into PostGIS."""

    pipeline_name = "hydro_substations"
    default_source_url = GEOHUB_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_substations
            self.logger.info("Using mock substation data")
            return {"type": "FeatureCollection", "features": generate_substations()}
        try:
            return self._http_get(self.default_source_url, params=GEOHUB_PARAMS)
        except Exception as exc:
            self.logger.warning("Live fetch failed (%s), falling back to mock data", exc)
            from etl.mock_data import generate_substations
            return {"type": "FeatureCollection", "features": generate_substations()}

    def parse(self, raw_data: Any) -> list[dict]:
        records: list[dict] = []
        features = raw_data.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            name = (
                props.get("STATION_NAME")
                or props.get("name")
                or props.get("NAME")
                or "Unknown"
            )
            voltage = (
                props.get("VOLTAGE_KV")
                or props.get("voltage_kv")
                or props.get("VOLTAGE")
            )
            capacity = (
                props.get("CAPACITY_MVA")
                or props.get("capacity_mva")
            )

            records.append({
                "name": str(name).strip(),
                "owner": props.get("OWNER", props.get("owner", "Hydro One")),
                "voltage_kv": float(voltage) if voltage else None,
                "capacity_mva": float(capacity) if capacity else None,
                "status": props.get("STATUS", props.get("status", "active")),
                "source": "ontario_geohub",
                "source_id": str(
                    props.get("OBJECTID")
                    or props.get("source_id")
                    or f"sub_{coords[0]:.4f}_{coords[1]:.4f}"
                ),
                "lon": float(coords[0]),
                "lat": float(coords[1]),
            })
        return records

    def _validate_record(self, record: dict) -> bool:
        lon, lat = record.get("lon"), record.get("lat")
        if lon is None or lat is None:
            return False
        if not (-95.2 <= lon <= -74.3 and 41.7 <= lat <= 56.9):
            self.logger.debug("Substation outside Ontario bbox: %s", record["name"])
            return False
        return True

    def transform(self, records: list[dict]) -> list[dict]:
        """Return dicts ready for upsert (geometry encoded)."""
        transformed: list[dict] = []
        for rec in records:
            point = Point(rec["lon"], rec["lat"])
            transformed.append({
                "name": rec["name"],
                "owner": rec["owner"],
                "voltage_kv": rec["voltage_kv"],
                "capacity_mva": rec["capacity_mva"],
                "source_id": rec["source_id"],
                "geom": from_shape(point, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(Substation.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "name": stmt.excluded.name,
                "owner": stmt.excluded.owner,
                "voltage_kv": stmt.excluded.voltage_kv,
                "capacity_mva": stmt.excluded.capacity_mva,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
