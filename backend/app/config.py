"""
Application configuration using pydantic-settings.

Loads settings from environment variables and .env file with sensible defaults
for local development targeting Ontario, Canada data center site analysis.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Data Center Site Intelligence API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/datacenters"
    )

    # --- API ---
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Data Center Site Intelligence Dashboard"
    DEBUG: bool = False

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # --- Data ---
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"

    # --- Scoring defaults ---
    DEFAULT_SEARCH_RADIUS_KM: float = 50.0

    # --- Ontario bounding box (used for data validation) ---
    ONTARIO_BBOX: dict = {
        "min_lon": -95.2,
        "max_lon": -74.3,
        "min_lat": 41.7,
        "max_lat": 56.9,
    }


settings = Settings()
