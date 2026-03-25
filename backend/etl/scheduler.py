"""
APScheduler configuration for periodic ETL pipeline execution.

Schedules:
  - Power infrastructure (substations, transmission lines): weekly
  - Fiber backbone: weekly
  - Land parcels: monthly
  - Zoning: monthly
  - Environmental constraints: monthly

After each full ETL cycle, the scoring engine is triggered to recompute
site suitability scores.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("etl.scheduler")

# ---------------------------------------------------------------------------
# Pipeline runners – each wraps the pipeline class with error isolation.
# ---------------------------------------------------------------------------


def _run_pipeline(pipeline_cls: type, use_mock: bool = False) -> dict[str, Any]:
    """Instantiate and run a single pipeline, returning its summary."""
    try:
        pipeline = pipeline_cls(use_mock=use_mock)
        return pipeline.run()
    except Exception as exc:
        logger.exception("Unhandled error in %s", pipeline_cls.__name__)
        return {
            "pipeline": getattr(pipeline_cls, "pipeline_name", pipeline_cls.__name__),
            "status": "error",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }


def run_power_pipelines(use_mock: bool = False) -> list[dict]:
    """Run all power-infrastructure ETL pipelines."""
    from etl.hydro_substations import HydroSubstationsPipeline
    from etl.ieso_tx_lines import TransmissionLinesPipeline

    results = [
        _run_pipeline(HydroSubstationsPipeline, use_mock=use_mock),
        _run_pipeline(TransmissionLinesPipeline, use_mock=use_mock),
    ]
    logger.info("Power pipelines completed: %s", [r["status"] for r in results])
    return results


def run_fiber_pipeline(use_mock: bool = False) -> list[dict]:
    """Run the fiber backbone ETL pipeline."""
    from etl.fiber_backbone import FiberBackbonePipeline

    results = [_run_pipeline(FiberBackbonePipeline, use_mock=use_mock)]
    logger.info("Fiber pipeline completed: %s", [r["status"] for r in results])
    return results


def run_land_pipelines(use_mock: bool = False) -> list[dict]:
    """Run parcels and zoning ETL pipelines."""
    from etl.parcels import ParcelsPipeline
    from etl.zoning import ZoningPipeline

    results = [
        _run_pipeline(ParcelsPipeline, use_mock=use_mock),
        _run_pipeline(ZoningPipeline, use_mock=use_mock),
    ]
    logger.info("Land pipelines completed: %s", [r["status"] for r in results])
    return results


def run_environmental_pipeline(use_mock: bool = False) -> list[dict]:
    """Run the environmental constraints ETL pipeline."""
    from etl.environmental import EnvironmentalPipeline

    results = [_run_pipeline(EnvironmentalPipeline, use_mock=use_mock)]
    logger.info("Environmental pipeline completed: %s", [r["status"] for r in results])
    return results


def run_scoring_engine() -> None:
    """Trigger the scoring engine to recompute site suitability scores.

    This is called after ETL pipelines complete to keep scores current.
    """
    try:
        # Import dynamically to avoid circular imports and to handle the case
        # where the scoring module is not yet implemented.
        from app.scoring import engine  # type: ignore[attr-defined]

        if hasattr(engine, "recompute_all"):
            logger.info("Triggering scoring engine recomputation")
            engine.recompute_all()
            logger.info("Scoring engine completed successfully")
        else:
            logger.info("Scoring engine not yet implemented, skipping")
    except (ImportError, AttributeError):
        logger.info("Scoring engine module not available, skipping")
    except Exception:
        logger.exception("Scoring engine failed")


def run_full_etl_cycle(use_mock: bool = False) -> list[dict]:
    """Run all ETL pipelines followed by score recomputation."""
    logger.info("=== Starting full ETL cycle ===")
    all_results: list[dict] = []
    all_results.extend(run_power_pipelines(use_mock=use_mock))
    all_results.extend(run_fiber_pipeline(use_mock=use_mock))
    all_results.extend(run_land_pipelines(use_mock=use_mock))
    all_results.extend(run_environmental_pipeline(use_mock=use_mock))

    # Recompute scores with fresh data.
    run_scoring_engine()

    successes = sum(1 for r in all_results if r["status"] == "success")
    failures = len(all_results) - successes
    logger.info(
        "=== Full ETL cycle complete: %d succeeded, %d failed ===",
        successes,
        failures,
    )
    return all_results


# ---------------------------------------------------------------------------
# Scheduler setup
# ---------------------------------------------------------------------------


def create_scheduler(use_mock: bool = False) -> BackgroundScheduler:
    """Create and configure the APScheduler instance.

    Returns the scheduler *without* starting it so the caller can start/stop
    it as part of the application lifecycle.
    """
    scheduler = BackgroundScheduler(
        job_defaults={
            "coalesce": True,          # Collapse missed runs into one.
            "max_instances": 1,        # Never run the same job concurrently.
            "misfire_grace_time": 3600,  # Allow 1 hour of misfire tolerance.
        }
    )

    # --- Weekly jobs (power and fiber) – Sunday 02:00 ET ---
    scheduler.add_job(
        run_power_pipelines,
        trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="etl_power_weekly",
        name="Power Infrastructure ETL (weekly)",
        kwargs={"use_mock": use_mock},
        replace_existing=True,
    )
    scheduler.add_job(
        run_fiber_pipeline,
        trigger=CronTrigger(day_of_week="sun", hour=2, minute=30),
        id="etl_fiber_weekly",
        name="Fiber Backbone ETL (weekly)",
        kwargs={"use_mock": use_mock},
        replace_existing=True,
    )

    # --- Monthly jobs (parcels, zoning, environmental) – 1st of month 03:00 ET ---
    scheduler.add_job(
        run_land_pipelines,
        trigger=CronTrigger(day=1, hour=3, minute=0),
        id="etl_land_monthly",
        name="Land Parcels & Zoning ETL (monthly)",
        kwargs={"use_mock": use_mock},
        replace_existing=True,
    )
    scheduler.add_job(
        run_environmental_pipeline,
        trigger=CronTrigger(day=1, hour=3, minute=30),
        id="etl_environmental_monthly",
        name="Environmental Constraints ETL (monthly)",
        kwargs={"use_mock": use_mock},
        replace_existing=True,
    )

    # --- Scoring recomputation after monthly cycle – 1st of month 04:00 ET ---
    scheduler.add_job(
        run_scoring_engine,
        trigger=CronTrigger(day=1, hour=4, minute=0),
        id="scoring_recompute_monthly",
        name="Scoring Engine Recomputation (monthly)",
        replace_existing=True,
    )

    logger.info(
        "Scheduler configured with %d jobs: %s",
        len(scheduler.get_jobs()),
        [j.name for j in scheduler.get_jobs()],
    )
    return scheduler
