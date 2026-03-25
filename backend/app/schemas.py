"""
Pydantic v2 schemas for API request/response serialisation.

GeoJSON structures follow RFC 7946.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# GeoJSON primitives
# ---------------------------------------------------------------------------

class GeoJSONGeometry(BaseModel):
    """A GeoJSON Geometry object."""
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    """A single GeoJSON Feature."""
    type: str = "Feature"
    id: int | str | None = None
    geometry: GeoJSONGeometry
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    """A GeoJSON FeatureCollection."""
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Filter parameters
# ---------------------------------------------------------------------------

class FilterParams(BaseModel):
    """Query-parameter filter model for parcel search."""
    power_proximity_km: float | None = Field(
        default=None, ge=0, description="Max distance to nearest substation (km)"
    )
    min_area_acres: float | None = Field(
        default=None, ge=0, description="Minimum parcel size in acres"
    )
    max_area_acres: float | None = Field(
        default=None, ge=0, description="Maximum parcel size in acres"
    )
    zoning_types: list[str] | None = Field(
        default=None, description="Allowed zoning codes"
    )
    min_score: float | None = Field(
        default=None, ge=0, le=100, description="Minimum overall score"
    )
    municipality: str | None = Field(
        default=None, description="Filter by municipality name"
    )

    @model_validator(mode="after")
    def check_area_range(self):
        if (
            self.min_area_acres is not None
            and self.max_area_acres is not None
            and self.min_area_acres > self.max_area_acres
        ):
            raise ValueError("min_area_acres must be <= max_area_acres")
        return self


# ---------------------------------------------------------------------------
# Bounding box filter
# ---------------------------------------------------------------------------

class BBoxParams(BaseModel):
    """Bounding box for spatial viewport queries (EPSG:4326)."""
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)


# ---------------------------------------------------------------------------
# Score responses
# ---------------------------------------------------------------------------

class ScoreResponse(BaseModel):
    """Score breakdown for a single parcel."""
    parcel_id: int
    overall_score: float
    power_score: float
    fiber_score: float
    zoning_score: float
    size_score: float
    constraint_score: float
    nearest_substation_km: float | None
    nearest_substation_kv: float | None
    nearest_fiber_km: float | None
    risk_flags: dict[str, Any] | None
    computed_at: datetime


class ScoreStatsResponse(BaseModel):
    """Aggregate statistics across all scored parcels."""
    total_scored: int
    mean_score: float | None
    median_score: float | None
    min_score: float | None
    max_score: float | None
    std_dev: float | None
    score_buckets: dict[str, int] = Field(
        default_factory=dict,
        description="Count of parcels in score ranges (e.g. '0-20': 14)"
    )


# ---------------------------------------------------------------------------
# Parcel responses
# ---------------------------------------------------------------------------

class ParcelProperties(BaseModel):
    """Non-geometry properties returned for a parcel."""
    id: int
    pin: str | None
    municipality: str | None
    area_sqm: float | None
    area_acres: float | None
    current_use: str | None
    updated_at: datetime | None


class ParcelDetailResponse(BaseModel):
    """Full parcel detail including the latest score breakdown."""
    feature: GeoJSONFeature
    score: ScoreResponse | None = None


# ---------------------------------------------------------------------------
# Infrastructure responses
# ---------------------------------------------------------------------------

class SubstationProperties(BaseModel):
    id: int
    name: str
    voltage_kv: float
    capacity_mva: float | None
    owner: str | None


class FiberRouteProperties(BaseModel):
    id: int
    provider: str | None
    route_type: str | None


class TransmissionLineProperties(BaseModel):
    id: int
    name: str | None
    voltage_kv: float
    owner: str | None


# ---------------------------------------------------------------------------
# Generic message
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    """Simple status / message envelope."""
    message: str
    detail: Any = None
