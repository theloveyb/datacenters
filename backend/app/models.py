"""
SQLAlchemy + GeoAlchemy2 ORM models for the Data Center Site Intelligence DB.

All geometries use SRID 4326 (WGS 84). Distance calculations cast to
geography or use ST_Transform to a metre-based projection as needed.
"""

from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Power infrastructure
# ---------------------------------------------------------------------------

class Substation(Base):
    """High-voltage electrical substation."""

    __tablename__ = "substations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    voltage_kv: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_mva: Mapped[float | None] = mapped_column(Float, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        Index("idx_substations_geom", geom, postgresql_using="gist"),
    )


class TransmissionLine(Base):
    """High-voltage transmission line segment."""

    __tablename__ = "transmission_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    voltage_kv: Mapped[float] = mapped_column(Float, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        Index("idx_transmission_lines_geom", geom, postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Fiber / connectivity
# ---------------------------------------------------------------------------

class FiberRoute(Base):
    """Fiber-optic cable route."""

    __tablename__ = "fiber_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    route_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g. "long-haul", "metro"
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        Index("idx_fiber_routes_geom", geom, postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Land parcels
# ---------------------------------------------------------------------------

class Parcel(Base):
    """Land parcel sourced from Ontario MPAC / municipal open data."""

    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pin: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    municipality: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_use: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    scores: Mapped[list["ParcelScore"]] = relationship(
        back_populates="parcel", cascade="all, delete-orphan"
    )

    @property
    def area_acres(self) -> float | None:
        """Convert stored square-metre area to acres."""
        if self.area_sqm is None:
            return None
        return self.area_sqm * 0.000247105

    __table_args__ = (
        Index("idx_parcels_geom", geom, postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Zoning
# ---------------------------------------------------------------------------

class Zoning(Base):
    """Municipal zoning polygon."""

    __tablename__ = "zoning"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    municipality: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    zone_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zone_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    dc_compatible: Mapped[bool] = mapped_column(Boolean, default=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        Index("idx_zoning_geom", geom, postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Environmental / regulatory constraints
# ---------------------------------------------------------------------------

class Constraint(Base):
    """Area constraint (floodplain, wetland, conservation area, etc.)."""

    __tablename__ = "constraints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    constraint_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "floodplain", "wetland", "conservation", "heritage"
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium"
    )  # "low", "medium", "high", "prohibitive"
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        Index("idx_constraints_geom", geom, postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Scoring results
# ---------------------------------------------------------------------------

class ParcelScore(Base):
    """Composite suitability score for a parcel."""

    __tablename__ = "parcel_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parcel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    power_score: Mapped[float] = mapped_column(Float, default=0.0)
    fiber_score: Mapped[float] = mapped_column(Float, default=0.0)
    zoning_score: Mapped[float] = mapped_column(Float, default=0.0)
    size_score: Mapped[float] = mapped_column(Float, default=0.0)
    constraint_score: Mapped[float] = mapped_column(Float, default=0.0)
    nearest_substation_km: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    nearest_substation_kv: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    nearest_fiber_km: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    risk_flags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    parcel: Mapped["Parcel"] = relationship(back_populates="scores")

    __table_args__ = (
        Index("idx_parcel_scores_parcel", "parcel_id"),
        Index("idx_parcel_scores_overall", "overall_score"),
    )
