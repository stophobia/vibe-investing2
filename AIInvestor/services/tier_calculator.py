"""§T2E-A — Tier + stage computation from cumulative + seasonal points.

The "lower of the two wins" rule prevents users from coasting on lifetime
P after a quarter-end reset — they have to keep earning to stay at
tier. Cumulative is the floor (you don't drop below what you've ever
earned, just because the season just started).
"""

from __future__ import annotations

from .gamification_config import (
    DIAMOND_STAGE_THRESHOLDS,
    STAGE_LABELS,
    TIER_ORDER,
    TIER_THRESHOLDS_CUMULATIVE,
    TIER_THRESHOLDS_SEASONAL,
)


def _tier_from(points: int, table: dict[str, tuple[float, float]]) -> str:
    for name in reversed(TIER_ORDER):  # check highest first
        lo, _hi = table[name]
        if points >= lo:
            return name
    return "bronze"


def compute_tier(
    cumulative_points: int,
    seasonal_points: int,
) -> str:
    """Return the tier the user qualifies for.

    Rule: lower of (tier_from_cumulative, tier_from_seasonal). User keeps
    historic floor but must keep earning each season to maintain tier.
    """
    cum_tier = _tier_from(cumulative_points, TIER_THRESHOLDS_CUMULATIVE)
    season_tier = _tier_from(seasonal_points, TIER_THRESHOLDS_SEASONAL)
    return min(cum_tier, season_tier, key=TIER_ORDER.index)


def compute_tier_stage(
    cumulative_points: int,
    seasonal_points: int,
) -> tuple[str, int, str]:
    """Return (tier, stage_0_to_4, visual_label).

    Stage divides each tier's cumulative span into 5 buckets so users see
    progress within their tier. Diamond is special (uses absolute
    thresholds since the high end is unbounded).
    """
    tier = compute_tier(cumulative_points, seasonal_points)

    if tier == "diamond":
        stage = sum(1 for t in DIAMOND_STAGE_THRESHOLDS if cumulative_points >= t) - 1
        stage = max(0, min(4, stage))
    else:
        lo, hi = TIER_THRESHOLDS_CUMULATIVE[tier]
        if hi == float("inf"):
            stage = 4
        else:
            span = hi - lo + 1
            stage = min(4, max(0, int((cumulative_points - lo) * 5 // span)))

    return tier, stage, STAGE_LABELS[stage]


def next_tier_threshold(current_tier: str) -> int | None:
    """Cumulative point threshold for the next tier up. None if at top."""
    try:
        idx = TIER_ORDER.index(current_tier)
    except ValueError:
        return None
    if idx >= len(TIER_ORDER) - 1:
        return None
    next_tier = TIER_ORDER[idx + 1]
    return int(TIER_THRESHOLDS_CUMULATIVE[next_tier][0])


def points_to_next_tier(
    cumulative_points: int,
    seasonal_points: int,
) -> int:
    """How many more cumulative points to reach the next tier. 0 if maxed."""
    tier = compute_tier(cumulative_points, seasonal_points)
    next_th = next_tier_threshold(tier)
    if next_th is None:
        return 0
    return max(0, next_th - cumulative_points)
