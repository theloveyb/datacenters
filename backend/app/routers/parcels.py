"""
Parcel endpoints -- list, filter, and detail views as GeoJSON.
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.functions import ST_AsGeoJSON, ST_DWithin, ST_Intersects
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Parcel, ParcelScore, Substation, Zoning
from app.schemas import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    ParcelDetailResponse,
    ScoreResponse,
)

router = APIRouter(prefix="/parcels", tags=["parcels"])

# Conversion constant: 1 acre = 4046.86 m^2
ACRES_TO_SQM = 4046.86
M_PER_KM = 1000.0


def _parcel_feature(parcel_row) -> GeoJSONFeature:
    """Build a GeoJSON Feature from a query row containing (Parcel, geojson)."""
    parcel: Parcel = parcel_row[0]
    geojson_str: str = parcel_row[1]

    geometry = GeoJSONGeometry(**json.loads(geojson_str))

    return GeoJSONFeature(
        id=parcel.id,
        geometry=geometry,
        properties={
            "id": parcel.id,
            "pin": parcel.pin,
            "municipality": parcel.municipality,
            "area_sqm": parcel.area_sqm,
            "area_acres": parcel.area_acres,
            "current_use": parcel.current_use,
            "updated_at": parcel.updated_at.isoformat() if parcel.updated_at else None,
        },
    )


@router.get("", response_model=GeoJSONFeatureCollection)
def list_parcels(
    # Filter parameters as individual query params.
    power_proximity_km: Optional[float] = Query(None, ge=0),
    min_area_acres: Optional[float] = Query(None, ge=0),
    max_area_acres: Optional[float] = Query(None, ge=0),
    zoning_types: Optional[str] = Query(
        None, description="Comma-separated zoning codes"
    ),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    municipality: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Return parcels as a GeoJSON FeatureCollection with optional filters."""

    stmt = select(Parcel, func.ST_AsGeoJSON(Parcel.geom).label("geojson"))

    # --- Municipality filter ---
    if municipality:
        stmt = stmt.where(Parcel.municipality.ilike(f"%{municipality}%"))

    # --- Area filters (convert acres to sqm for DB comparison) ---
    if min_area_acres is not None:
        stmt = stmt.where(Parcel.area_sqm >= min_area_acres * ACRES_TO_SQM)
    if max_area_acres is not None:
        stmt = stmt.where(Parcel.area_sqm <= max_area_acres * ACRES_TO_SQM)

    # --- Power proximity filter ---
    # Keep only parcels within N km of at least one substation.
    if power_proximity_km is not None:
        substation_exists = (
            select(Substation.id)
            .where(
                func.ST_DWithin(
                    func.cast(Parcel.geom, func.Geography()),
                    func.cast(Substation.geom, func.Geography()),
                    power_proximity_km * M_PER_KM,
                )
            )
            .correlate(Parcel)
            .exists()
        )
        stmt = stmt.where(substation_exists)

    # --- Zoning type filter ---
    if zoning_types:
        codes = [c.strip() for c in zoning_types.split(",") if c.strip()]
        if codes:
            zoning_match = (
                select(Zoning.id)
                .where(
                    func.ST_Intersects(Parcel.geom, Zoning.geom),
                    Zoning.zone_code.in_(codes),
                )
                .correlate(Parcel)
                .exists()
            )
            stmt = stmt.where(zoning_match)

    # --- Minimum score filter ---
    if min_score is not None:
        # Join to the latest score row.
        latest_score = (
            select(ParcelScore.parcel_id)
            .where(
                ParcelScore.parcel_id == Parcel.id,
                ParcelScore.overall_score >= min_score,
            )
            .correlate(Parcel)
            .exists()
        )
        stmt = stmt.where(latest_score)

    stmt = stmt.order_by(Parcel.id).offset(offset).limit(limit)

    rows = db.execute(stmt).all()
    features = [_parcel_feature(row) for row in rows]

    return GeoJSONFeatureCollection(features=features)


@router.get("/{parcel_id}", response_model=ParcelDetailResponse)
def get_parcel(parcel_id: int, db: Session = Depends(get_db)):
    """Return full detail for a single parcel, including its latest score."""

    row = db.execute(
        select(Parcel, func.ST_AsGeoJSON(Parcel.geom).label("geojson"))
        .where(Parcel.id == parcel_id)
    ).first()

    if row is None:
        raise HTTPException(status_code=404, detail="Parcel not found")

    feature = _parcel_feature(row)

    # Fetch latest score.
    score_row = db.execute(
        select(ParcelScore)
        .where(ParcelScore.parcel_id == parcel_id)
        .order_by(ParcelScore.computed_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    score_response = None
    if score_row:
        score_response = ScoreResponse(
            parcel_id=score_row.parcel_id,
            overall_score=score_row.overall_score,
            power_score=score_row.power_score,
            fiber_score=score_row.fiber_score,
            zoning_score=score_row.zoning_score,
            size_score=score_row.size_score,
            constraint_score=score_row.constraint_score,
            nearest_substation_km=score_row.nearest_substation_km,
            nearest_substation_kv=score_row.nearest_substation_kv,
            nearest_fiber_km=score_row.nearest_fiber_km,
            risk_flags=score_row.risk_flags,
            computed_at=score_row.computed_at,
        )

    return ParcelDetailResponse(feature=feature, score=score_response)
