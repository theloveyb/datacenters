# Phase 3 — Scoring Model

## Overview

Each land parcel receives a composite score from 0–100 indicating its suitability for data center development. The score is a weighted sum of five sub-scores, each normalized to 0–100.

## Formula

```
overall_score = (
    power_score   × 0.35 +
    fiber_score   × 0.20 +
    zoning_score  × 0.20 +
    size_score    × 0.15 +
    constraint_score × 0.10
)
```

## Weight Justification

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Power | 0.35 | Power is the #1 driver. A 100MW data center needs direct access to high-voltage transmission. Without nearby substations, a site is non-viable regardless of other factors. |
| Fiber | 0.20 | Redundant fiber connectivity is essential but more easily extended than power. Major backbone proximity matters but is less binary than power. |
| Zoning | 0.20 | Zoning determines permitting timeline and cost. Industrial-zoned land is immediately buildable; agricultural requires rezoning (12-24 months). |
| Size | 0.15 | Campus-scale data centers need 20-200 acres. Too small limits expansion; too large suggests remote/agricultural land with poor infrastructure. |
| Constraints | 0.10 | Environmental constraints (floodplains, wetlands) can block or delay development but affect fewer parcels than other factors. |

## Sub-Score Calculations

### Power Score (0–100)

Based on distance to nearest substation, weighted by substation voltage class.

```python
def power_score(nearest_substation_km, voltage_kv):
    # Voltage multiplier: higher voltage = more capacity available
    voltage_mult = {500: 1.0, 230: 0.75, 115: 0.5}.get(voltage_kv, 0.3)

    # Distance decay: exponential falloff
    if nearest_substation_km <= 2:
        distance_score = 100
    elif nearest_substation_km <= 5:
        distance_score = 90 - (nearest_substation_km - 2) * 5
    elif nearest_substation_km <= 15:
        distance_score = 75 - (nearest_substation_km - 5) * 4
    elif nearest_substation_km <= 30:
        distance_score = 35 - (nearest_substation_km - 15) * 1.5
    else:
        distance_score = max(0, 12 - (nearest_substation_km - 30) * 0.3)

    return distance_score * voltage_mult
```

**Rationale:** Within 2km of a 500kV substation is ideal (direct tap possible). Beyond 30km, building new transmission infrastructure becomes cost-prohibitive for most projects.

### Fiber Score (0–100)

```python
def fiber_score(nearest_fiber_km, provider_count_within_10km):
    # Distance component
    if nearest_fiber_km <= 0.5:
        distance_score = 100
    elif nearest_fiber_km <= 2:
        distance_score = 85 - (nearest_fiber_km - 0.5) * 10
    elif nearest_fiber_km <= 10:
        distance_score = 70 - (nearest_fiber_km - 2) * 5
    else:
        distance_score = max(0, 30 - (nearest_fiber_km - 10) * 2)

    # Redundancy bonus: multiple providers reduce single-point-of-failure risk
    redundancy_bonus = min(20, provider_count_within_10km * 7)

    return min(100, distance_score + redundancy_bonus)
```

**Rationale:** Fiber can be extended but at ~$30-50K/km. Multiple providers within range enable path diversity, which enterprise customers require.

### Zoning Score (0–100)

```python
ZONING_SCORES = {
    'heavy_industrial': 100,   # M3 — data centers explicitly permitted
    'light_industrial': 90,    # M1/M2 — typically permitted, may need site plan
    'prestige_industrial': 85, # Business park zones
    'commercial': 60,          # May require rezoning or special use
    'mixed_use': 50,           # Possible but complex approvals
    'rural': 30,               # Requires rezoning, slower process
    'agricultural': 15,        # Significant regulatory hurdles in Ontario
    'residential': 5,          # Extremely unlikely to be rezoned
    'unknown': 25,             # Conservative default
}

def zoning_score(zone_type, dc_compatible_flag):
    base = ZONING_SCORES.get(zone_type, 25)
    if dc_compatible_flag:
        base = max(base, 80)  # Override if explicitly marked compatible
    return base
```

**Rationale:** Ontario's Planning Act makes rezoning from Agricultural to Industrial very difficult (Provincial Policy Statement protections). Industrial land is premium.

### Size Score (0–100)

```python
def size_score(area_acres):
    # Optimal range: 20-200 acres for campus-scale DC
    if 20 <= area_acres <= 200:
        return 100
    elif 10 <= area_acres < 20:
        return 60 + (area_acres - 10) * 4  # 60-100 linear
    elif 200 < area_acres <= 500:
        return 100 - (area_acres - 200) * 0.15  # Slight penalty for very large
    elif 5 <= area_acres < 10:
        return 30 + (area_acres - 5) * 6  # 30-60 linear
    elif area_acres > 500:
        return max(40, 55 - (area_acres - 500) * 0.03)
    else:
        return max(0, area_acres * 6)  # < 5 acres: very low score
```

**Rationale:** Hyperscale campuses (AWS, Google, Microsoft) target 50-200 acres. Smaller operators need 10-30 acres minimum. Parcels under 5 acres can't fit even a single building with required setbacks and cooling infrastructure.

### Constraint Score (0–100)

```python
def constraint_score(overlapping_constraints):
    """
    Start at 100, deduct for each overlapping constraint.
    """
    score = 100
    deductions = {
        'floodway': 80,           # Hard block — virtually unbuildable
        'floodplain': 40,         # Requires expensive mitigation
        'wetland': 50,            # Provincial protection, very hard to develop
        'heritage': 30,           # Delays and design restrictions
        'conservation_area': 60,  # Major regulatory barrier
        'endangered_species': 45, # ESA triggers lengthy process
    }
    for constraint in overlapping_constraints:
        score -= deductions.get(constraint['type'], 10)

    return max(0, score)
```

**Rationale:** Floodway is essentially a hard block — no amount of engineering makes it economic. Wetlands are protected under Ontario's Provincial Policy Statement. Stacking multiple constraints makes a site increasingly risky.

## Risk Flags

In addition to numeric scores, each parcel gets qualitative risk flags:

| Flag | Trigger | Severity |
|------|---------|----------|
| `floodplain_overlap` | Any floodplain intersection | High |
| `wetland_overlap` | Any wetland intersection | High |
| `small_parcel` | < 10 acres | Medium |
| `agricultural_zone` | Zoned agricultural | Medium |
| `no_nearby_power` | No substation within 30km | High |
| `no_nearby_fiber` | No fiber within 15km | Medium |
| `low_voltage_only` | Nearest substation < 230kV | Low |
| `single_provider_fiber` | Only 1 fiber provider nearby | Low |

## Tradeoffs

1. **Power dominance:** 35% weight means a site far from power can't score above ~65 even if everything else is perfect. This is intentional — power is non-negotiable.

2. **Zoning vs. opportunity:** Agricultural land scores low on zoning but may score high on power/size. This identifies "rezoning opportunity" parcels that show up in the 40-60 range — worth investigating manually.

3. **Linear vs. exponential decay:** We use piecewise linear decay for distance scores rather than smooth exponential. This makes the scoring more interpretable and the breakpoints correspond to real cost thresholds in utility construction.

4. **No land cost factor:** We intentionally exclude land price from scoring. The goal is to find sites that are *undervalued relative to their infrastructure score*. Land price is overlaid separately by the analyst.
