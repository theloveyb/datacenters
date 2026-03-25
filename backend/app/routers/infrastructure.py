"""
Infrastructure endpoints -- substations, transmission lines, fiber routes.

All endpoints return GeoJSON FeatureCollections and support optional
bounding-box filters for viewport-driven map queries.
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FiberRoute, Substation, TransmissionLine
from app.schemas import GeoJSONFeature, GeoJSONFeatureCollection, GeoJSONGeometry

router = APIRouter(tags=["infrastructure"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bbox_filter(geom_col, min_lon, min_lat, max_lon, max_lat):
    """Return a PostGIS envelope intersection filter for a bounding box.

    Constructs an ST_MakeEnvelope in SRID 4326 and tests intersection
    against the given geometry column.
    """
    envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    return func.ST_Intersects(geom_col, envelope)


def _make_feature(row_id: int, geojson_str: str, properties: dict) -> GeoJSONFeature:
    geometry = GeoJSONGeometry(**json.loads(geojson_str))
    return GeoJSONFeature(id=row_id, geometry=geometry, properties=properties)


# ---------------------------------------------------------------------------
# Substations
# ---------------------------------------------------------------------------

@router.get("/substations", response_model=GeoJSONFeatureCollection)
def list_substations(
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lat: Optional[float] = Query(None, ge=-90, le=90),
    min_voltage_kv: Optional[float] = Query(None, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Return substations as GeoJSON, optionally filtered by bounding box."""

    stmt = select(
        Substation,
        func.ST_AsGeoJSON(Substation.geom).label("geojson"),
    )

    if all(v is not None for v in (min_lon, min_lat, max_lon, max_lat)):
        stmt = stmt.where(
            _bbox_filter(Substation.geom, min_lon, min_lat, max_lon, max_lat)
        )

    if min_voltage_kv is not None:
        stmt = stmt.where(Substation.voltage_kv >= min_voltage_kv)

    stmt = stmt.order_by(Substation.voltage_kv.desc()).limit(limit)
    rows = db.execute(stmt).all()

    features = [
        _make_feature(
            row[0].id,
            row[1],
            {
                "id": row[0].id,
                "name": row[0].name,
                "voltage_kv": row[0].voltage_kv,
                "capacity_mva": row[0].capacity_mva,
                "owner": row[0].owner,
            },
        )
        for row in rows
    ]

    return GeoJSONFeatureCollection(features=features)


# ---------------------------------------------------------------------------
# Transmission lines
# ---------------------------------------------------------------------------

@router.get("/transmission-lines", response_model=GeoJSONFeatureCollection)
def list_transmission_lines(
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lat: Optional[float] = Query(None, ge=-90, le=90),
    min_voltage_kv: Optional[float] = Query(None, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    """Return transmission lines as GeoJSON, optionally filtered by bounding box."""

    stmt = select(
        TransmissionLine,
        func.ST_AsGeoJSON(TransmissionLine.geom).label("geojson"),
    )

    if all(v is not None for v in (min_lon, min_lat, max_lon, max_lat)):
        stmt = stmt.where(
            _bbox_filter(
                TransmissionLine.geom, min_lon, min_lat, max_lon, max_lat
            )
        )

    if min_voltage_kv is not None:
        stmt = stmt.where(TransmissionLine.voltage_kv >= min_voltage_kv)

    stmt = stmt.order_by(TransmissionLine.voltage_kv.desc()).limit(limit)
    rows = db.execute(stmt).all()

    features = [
        _make_feature(
            row[0].id,
            row[1],
            {
                "id": row[0].id,
                "name": row[0].name,
                "voltage_kv": row[0].voltage_kv,
                "owner": row[0].owner,
            },
        )
        for row in rows
    ]

    return GeoJSONFeatureCollection(features=features)


# ---------------------------------------------------------------------------
# Fiber routes
# ---------------------------------------------------------------------------

@router.get("/fiber-routes", response_model=GeoJSONFeatureCollection)
def list_fiber_routes(
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lat: Optional[float] = Query(None, ge=-90, le=90),
    provider: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    """Return fiber routes as GeoJSON, optionally filtered by bounding box."""

    stmt = select(
        FiberRoute,
        func.ST_AsGeoJSON(FiberRoute.geom).label("geojson"),
    )

    if all(v is not None for v in (min_lon, min_lat, max_lon, max_lat)):
        stmt = stmt.where(
            _bbox_filter(FiberRoute.geom, min_lon, min_lat, max_lon, max_lat)
        )

    if provider:
        stmt = stmt.where(FiberRoute.provider.ilike(f"%{provider}%"))

    stmt = stmt.order_by(FiberRoute.id).limit(limit)
    rows = db.execute(stmt).all()

    features = [
        _make_feature(
            row[0].id,
            row[1],
            {
                "id": row[0].id,
                "provider": row[0].provider,
                "route_type": row[0].route_type,
            },
        )
        for row in rows
    ]

    return GeoJSONFeatureCollection(features=features)
