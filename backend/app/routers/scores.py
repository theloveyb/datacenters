"""
Score endpoints -- top parcels, statistics, and recomputation trigger.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ParcelScore
from app.schemas import MessageResponse, ScoreResponse, ScoreStatsResponse
from app.scoring.engine import ScoringEngine

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/top", response_model=list[ScoreResponse])
def top_scores(
    limit: int = Query(20, ge=1, le=200),
    min_score: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Return the highest-scoring parcels.

    Only the most recent score per parcel is considered.  Results are
    ordered by overall_score descending.
    """
    # Subquery: latest score per parcel.
    latest = (
        select(
            ParcelScore.parcel_id,
            func.max(ParcelScore.computed_at).label("max_computed"),
        )
        .group_by(ParcelScore.parcel_id)
        .subquery()
    )

    stmt = (
        select(ParcelScore)
        .join(
            latest,
            (ParcelScore.parcel_id == latest.c.parcel_id)
            & (ParcelScore.computed_at == latest.c.max_computed),
        )
        .where(ParcelScore.overall_score >= min_score)
        .order_by(ParcelScore.overall_score.desc())
        .limit(limit)
    )

    rows = db.execute(stmt).scalars().all()

    return [
        ScoreResponse(
            parcel_id=r.parcel_id,
            overall_score=r.overall_score,
            power_score=r.power_score,
            fiber_score=r.fiber_score,
            zoning_score=r.zoning_score,
            size_score=r.size_score,
            constraint_score=r.constraint_score,
            nearest_substation_km=r.nearest_substation_km,
            nearest_substation_kv=r.nearest_substation_kv,
            nearest_fiber_km=r.nearest_fiber_km,
            risk_flags=r.risk_flags,
            computed_at=r.computed_at,
        )
        for r in rows
    ]


@router.get("/stats", response_model=ScoreStatsResponse)
def score_stats(db: Session = Depends(get_db)):
    """Aggregate score statistics across all scored parcels.

    Includes mean, median, min, max, std-dev, and histogram buckets.
    """
    # Subquery: latest score per parcel.
    latest = (
        select(
            ParcelScore.parcel_id,
            func.max(ParcelScore.computed_at).label("max_computed"),
        )
        .group_by(ParcelScore.parcel_id)
        .subquery()
    )

    scores_q = (
        select(ParcelScore.overall_score)
        .join(
            latest,
            (ParcelScore.parcel_id == latest.c.parcel_id)
            & (ParcelScore.computed_at == latest.c.max_computed),
        )
        .subquery()
    )

    agg = db.execute(
        select(
            func.count().label("cnt"),
            func.avg(scores_q.c.overall_score).label("mean"),
            func.min(scores_q.c.overall_score).label("min_s"),
            func.max(scores_q.c.overall_score).label("max_s"),
            func.stddev(scores_q.c.overall_score).label("std"),
        )
    ).first()

    total = agg.cnt if agg else 0

    # Compute median using percentile_cont (PostgreSQL).
    median_val = None
    if total > 0:
        median_row = db.execute(
            select(
                func.percentile_cont(0.5)
                .within_group(scores_q.c.overall_score)
                .label("median")
            )
        ).first()
        median_val = round(float(median_row.median), 2) if median_row and median_row.median is not None else None

    # Build histogram buckets.
    buckets: dict[str, int] = {}
    if total > 0:
        bucket_ranges = [
            ("0-20", 0, 20),
            ("20-40", 20, 40),
            ("40-60", 40, 60),
            ("60-80", 60, 80),
            ("80-100", 80, 100.01),
        ]
        for label, lo, hi in bucket_ranges:
            cnt = db.execute(
                select(func.count()).select_from(scores_q).where(
                    scores_q.c.overall_score >= lo,
                    scores_q.c.overall_score < hi,
                )
            ).scalar()
            buckets[label] = cnt or 0

    return ScoreStatsResponse(
        total_scored=total,
        mean_score=round(float(agg.mean), 2) if agg and agg.mean is not None else None,
        median_score=median_val,
        min_score=round(float(agg.min_s), 2) if agg and agg.min_s is not None else None,
        max_score=round(float(agg.max_s), 2) if agg and agg.max_s is not None else None,
        std_dev=round(float(agg.std), 2) if agg and agg.std is not None else None,
        score_buckets=buckets,
    )


def _run_recompute(db_session_factory):
    """Background task: open a fresh session and recompute all scores."""
    db = db_session_factory()
    try:
        engine = ScoringEngine(db)
        count = engine.compute_all_scores()
    finally:
        db.close()


@router.post("/recompute", response_model=MessageResponse)
def recompute_scores(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger an asynchronous recomputation of all parcel scores.

    The recomputation runs in a background task so the request returns
    immediately.
    """
    from app.database import SessionLocal

    background_tasks.add_task(_run_recompute, SessionLocal)

    return MessageResponse(
        message="Score recomputation started",
        detail="Scores will be updated in the background.",
    )
