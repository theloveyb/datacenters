"""
ETL pipeline: IESO / Hydro One transmission lines.

Primary source: Ontario GeoHub – Transmission Lines layer
Fallback: mock data following major Ontario transmission corridors.
"""

from __future__ import annotations

from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import TransmissionLine
from etl.base import BasePipeline

GEOHUB_URL = (
    "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/"
    "LIO_OPEN_DATA/LIO_Open01/MapServer/16/query"
)
GEOHUB_PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
    "resultRecordCount": "2000",
}


class TransmissionLinesPipeline(BasePipeline):
    """Ingest IESO transmission line segments into PostGIS."""

    pipeline_name = "ieso_tx_lines"
    default_source_url = GEOHUB_URL

    def fetch(self) -> Any:
        if self.use_mock:
            from etl.mock_data import generate_transmission_lines
            self.logger.info("Using mock transmission line data")
            return {"type": "FeatureCollection", "features": generate_transmission_lines()}
        try:
            return self._http_get(self.default_source_url, params=GEOHUB_PARAMS)
        except Exception as exc:
            self.logger.warning("Live fetch failed (%s), falling back to mock data", exc)
            from etl.mock_data import generate_transmission_lines
            return {"type": "FeatureCollection", "features": generate_transmission_lines()}

    def parse(self, raw_data: Any) -> list[dict]:
        records: list[dict] = []
        features = raw_data.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])
            if not coords or len(coords) < 2:
                continue

            name = (
                props.get("LINE_NAME")
                or props.get("name")
                or props.get("NAME")
                or "Unknown Line"
            )
            voltage = (
                props.get("VOLTAGE_KV")
                or props.get("voltage_kv")
                or props.get("VOLTAGE")
            )

            records.append({
                "name": str(name).strip(),
                "owner": props.get("OWNER", props.get("owner", "Hydro One")),
                "voltage_kv": float(voltage) if voltage else None,
                "circuit_id": props.get("CIRCUIT_ID", props.get("circuit_id")),
                "from_station": props.get("FROM_STATION", props.get("from_station")),
                "to_station": props.get("TO_STATION", props.get("to_station")),
                "source": "ontario_geohub",
                "source_id": str(
                    props.get("OBJECTID")
                    or props.get("source_id")
                    or f"tx_{hash(str(coords)) % 10**8}"
                ),
                "coordinates": coords,
            })
        return records

    def _validate_record(self, record: dict) -> bool:
        coords = record.get("coordinates", [])
        if len(coords) < 2:
            return False
        # Check at least the first point is in Ontario.
        lon, lat = coords[0][0], coords[0][1]
        if not (-95.2 <= lon <= -74.3 and 41.7 <= lat <= 56.9):
            return False
        return True

    def transform(self, records: list[dict]) -> list[dict]:
        transformed: list[dict] = []
        for rec in records:
            line = LineString(rec["coordinates"])
            length_km = line.length * 111.0  # rough degree-to-km at Ontario latitudes
            transformed.append({
                "name": rec["name"],
                "owner": rec["owner"],
                "voltage_kv": rec["voltage_kv"],
                "source_id": rec["source_id"],
                "geom": from_shape(line, srid=4326),
            })
        return transformed

    def load(self, session: Session, models: list[dict]) -> int:
        if not models:
            return 0
        stmt = pg_insert(TransmissionLine.__table__).values(models)
        stmt = stmt.on_conflict_do_update(
            index_elements=["source_id"],
            set_={
                "name": stmt.excluded.name,
                "owner": stmt.excluded.owner,
                "voltage_kv": stmt.excluded.voltage_kv,
                "geom": stmt.excluded.geom,
            },
        )
        result = session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
