"""
Abstract base class for all ETL pipelines.

Provides a standardised lifecycle: fetch -> parse -> validate -> transform -> load,
with automatic retry logic, local file caching, and structured logging.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, TypeVar

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal

T = TypeVar("T")

CACHE_DIR = Path(settings.DATA_DIR) / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("etl")


class PipelineError(Exception):
    """Raised when a pipeline step fails irrecoverably."""


class BasePipeline(ABC):
    """Abstract ETL pipeline with retry, caching, and logging."""

    # Subclasses must set these.
    pipeline_name: str = "base"
    default_source_url: str = ""

    # Retry configuration.
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    retry_backoff_factor: float = 2.0

    # Cache TTL – fetched data is reused if fresher than this.
    cache_ttl: timedelta = timedelta(hours=24)

    def __init__(self, *, use_mock: bool = False) -> None:
        self.use_mock = use_mock
        self.logger = logging.getLogger(f"etl.{self.pipeline_name}")
        self._configure_logging()

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _configure_logging(self) -> None:
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(name)-28s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _cache_key(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _cache_path(self, url: str) -> Path:
        return CACHE_DIR / f"{self.pipeline_name}_{self._cache_key(url)}.json"

    def _read_cache(self, url: str) -> dict | list | None:
        path = self._cache_path(url)
        if not path.exists():
            return None
        age = datetime.utcnow() - datetime.utcfromtimestamp(path.stat().st_mtime)
        if age > self.cache_ttl:
            self.logger.debug("Cache expired for %s (age=%s)", url, age)
            return None
        self.logger.info("Using cached data for %s", url)
        with open(path, "r") as fh:
            return json.load(fh)

    def _write_cache(self, url: str, data: Any) -> None:
        path = self._cache_path(url)
        with open(path, "w") as fh:
            json.dump(data, fh)
        self.logger.debug("Cached data written to %s", path)

    # ------------------------------------------------------------------
    # HTTP helper with retries
    # ------------------------------------------------------------------

    def _http_get(self, url: str, *, params: dict | None = None, timeout: float = 60.0) -> Any:
        """Fetch JSON data from *url* with exponential-backoff retries."""
        cached = self._read_cache(url)
        if cached is not None:
            return cached

        delay = self.retry_delay_seconds
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info("HTTP GET %s (attempt %d/%d)", url, attempt, self.max_retries)
                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    resp = client.get(url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    self._write_cache(url, data)
                    return data
            except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError) as exc:
                last_exc = exc
                self.logger.warning(
                    "Attempt %d failed: %s – retrying in %.1fs",
                    attempt,
                    exc,
                    delay,
                )
                time.sleep(delay)
                delay *= self.retry_backoff_factor

        raise PipelineError(
            f"Failed to fetch {url} after {self.max_retries} attempts"
        ) from last_exc

    # ------------------------------------------------------------------
    # Pipeline lifecycle (template method pattern)
    # ------------------------------------------------------------------

    @abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data (from network or mock generator)."""

    @abstractmethod
    def parse(self, raw_data: Any) -> list[dict]:
        """Parse raw data into a list of normalised dictionaries."""

    def validate(self, records: list[dict]) -> list[dict]:
        """Drop or fix records that fail basic validation.

        The default implementation keeps every record; subclasses override to
        add domain-specific checks (e.g. bounding-box, required fields).
        """
        valid: list[dict] = []
        for rec in records:
            if self._validate_record(rec):
                valid.append(rec)
            else:
                self.logger.warning("Dropped invalid record: %s", rec)
        return valid

    def _validate_record(self, record: dict) -> bool:
        """Return True if *record* passes basic checks. Override for custom logic."""
        return True

    @abstractmethod
    def transform(self, records: list[dict]) -> list[Any]:
        """Convert validated dicts into SQLAlchemy model instances."""

    @abstractmethod
    def load(self, session: Session, models: list[Any]) -> int:
        """Persist model instances to the database. Returns rows upserted."""

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Execute the full ETL lifecycle and return a summary dict."""
        started = time.monotonic()
        self.logger.info("=== %s pipeline started ===", self.pipeline_name)

        try:
            raw = self.fetch()
            records = self.parse(raw)
            self.logger.info("Parsed %d records", len(records))

            valid = self.validate(records)
            self.logger.info("Validated %d / %d records", len(valid), len(records))

            models = self.transform(valid)
            self.logger.info("Transformed %d model instances", len(models))

            session = SessionLocal()
            try:
                count = self.load(session, models)
                session.commit()
                self.logger.info("Loaded %d rows", count)
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

            elapsed = time.monotonic() - started
            summary = {
                "pipeline": self.pipeline_name,
                "status": "success",
                "fetched": len(records),
                "validated": len(valid),
                "loaded": count,
                "elapsed_seconds": round(elapsed, 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.logger.info("=== %s pipeline finished in %.2fs ===", self.pipeline_name, elapsed)
            return summary

        except Exception as exc:
            elapsed = time.monotonic() - started
            self.logger.exception("Pipeline %s failed after %.2fs", self.pipeline_name, elapsed)
            return {
                "pipeline": self.pipeline_name,
                "status": "error",
                "error": str(exc),
                "elapsed_seconds": round(elapsed, 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
