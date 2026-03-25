"""
Default scoring weights and configuration for the site-suitability engine.

Weights are normalised so that the five category scores sum to 100.
Individual sub-component parameters live here so they can be tuned
without touching engine logic.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Default category weights (must sum to 100)
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS: dict[str, float] = {
    "power": 30.0,
    "fiber": 20.0,
    "zoning": 20.0,
    "size": 15.0,
    "constraint": 15.0,
}


# ---------------------------------------------------------------------------
# Power scoring parameters
# ---------------------------------------------------------------------------

# Voltage tier multipliers -- higher voltage substations are more valuable
# because they can deliver more power with less new infrastructure.
VOLTAGE_TIER_MULTIPLIERS: dict[str, float] = {
    "500kv": 1.0,   # Ideal -- bulk transmission
    "230kv": 0.85,
    "115kv": 0.65,
    "below": 0.40,  # < 115 kV -- likely distribution level
}

# Distance decay for power (km).  Score falls linearly from 1.0 at 0 km
# to 0.0 at MAX_POWER_DISTANCE_KM.
MAX_POWER_DISTANCE_KM: float = 50.0


# ---------------------------------------------------------------------------
# Fiber scoring parameters
# ---------------------------------------------------------------------------

MAX_FIBER_DISTANCE_KM: float = 25.0
MULTI_PROVIDER_BONUS: float = 0.15  # Bonus (0-1 scale) for 2+ providers


# ---------------------------------------------------------------------------
# Size scoring parameters (acres)
# ---------------------------------------------------------------------------

OPTIMAL_MIN_ACRES: float = 20.0
OPTIMAL_MAX_ACRES: float = 200.0
PENALTY_BELOW_ACRES: float = 10.0   # Hard minimum -- score drops steeply
PENALTY_ABOVE_ACRES: float = 500.0  # Diminishing returns above this


# ---------------------------------------------------------------------------
# Constraint severity deductions (fraction of constraint score removed)
# ---------------------------------------------------------------------------

CONSTRAINT_DEDUCTIONS: dict[str, float] = {
    "prohibitive": 1.0,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
}


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass
class WeightConfig:
    """Mutable weight configuration for a scoring run."""

    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    max_power_distance_km: float = MAX_POWER_DISTANCE_KM
    max_fiber_distance_km: float = MAX_FIBER_DISTANCE_KM
    voltage_tiers: dict[str, float] = field(
        default_factory=lambda: dict(VOLTAGE_TIER_MULTIPLIERS)
    )
    multi_provider_bonus: float = MULTI_PROVIDER_BONUS
    optimal_min_acres: float = OPTIMAL_MIN_ACRES
    optimal_max_acres: float = OPTIMAL_MAX_ACRES
    penalty_below_acres: float = PENALTY_BELOW_ACRES
    penalty_above_acres: float = PENALTY_ABOVE_ACRES
    constraint_deductions: dict[str, float] = field(
        default_factory=lambda: dict(CONSTRAINT_DEDUCTIONS)
    )

    def validate(self) -> None:
        """Ensure weights sum to 100."""
        total = sum(self.weights.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(
                f"Category weights must sum to 100, got {total:.2f}"
            )
