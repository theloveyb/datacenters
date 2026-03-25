"""
FastAPI application entry point for the Data Center Site Intelligence API.

Configures middleware, registers routers, and handles startup initialisation
(table creation via SQLAlchemy).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import infrastructure, parcels, scores

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup (idempotent)."""
    logger.info("Creating database tables (if they do not exist)...")
    # Import models so SQLAlchemy registers them with Base.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("Database tables ready.")
    yield
    logger.info("Application shutting down.")


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Backend API for the Ontario Data Center Site Intelligence Dashboard. "
        "Provides parcel scoring, infrastructure layers, and spatial queries "
        "powered by PostgreSQL/PostGIS."
    ),
    docs_url=f"{settings.API_PREFIX}/docs",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(parcels.router, prefix=settings.API_PREFIX)
app.include_router(scores.router, prefix=settings.API_PREFIX)
app.include_router(infrastructure.router, prefix=settings.API_PREFIX)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
