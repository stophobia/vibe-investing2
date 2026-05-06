"""§T2E-A — Single source of truth for gamification rules.

All point/tier/reward constants live here so that changes don't
require hunting through services/ + bot/ + tests/. Imports stay
trivial (constants only, no IO).
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta


# ─────────────────────────────────────────────────────────────
# Point earning rules (§3.1 of t2e-gamification-architecture v2.0)
# ─────────────────────────────────────────────────────────────

POINTS = {
    # signup + attendance
    "signup":                      100,
    "signup_with_invite":          200,   # invitee bonus
    "daily_attendance":            10,
    "consecutive_attendance_step": 5,     # +5 per consecutive day, cap +50
    "consecutive_attendance_cap":  50,

    # daily prediction missions (§5)
    "predict_kospi_participate":   10,
    "predict_kospi_correct":       200,
    "predict_nasdaq_participate":  10,
    "predict_nasdaq_correct":      200,
    "predict_btc_participate":     5,
    "predict_btc_correct":         30,
    "predict_nasdaq_top10_correct":  100,   # per ticker
    "predict_nasdaq_top10_perfect":  1000,  # 10/10 bonus

    # invite system (§6)
    "invite_landing":         30,    # immediate when ref_ link clicked
    "invite_verified":        470,   # deferred bonus (total = 500 with landing)
    "invite_zombie_penalty": -30,    # 7-day inactive invitee → claw back

    # social / sharing
    "sns_share":          50,
    "share_card_create":  20,    # creating a brag card
    "share_card_clicked": 30,    # someone clicks it (capped per day)

    # bot interaction quality
    "persona_5x_used":  30,
    "deep_analysis":    20,    # consuming a deep dive (paid via daily_deep_count quota)

    # staking welcome bonus per $100 USDT
    "staking_welcome_per_100usdt": 1000,

    # welcome BTC mini-event (§5.9 — 30-min BTC price guess)
    "welcome_event_participate": 50,
    "welcome_event_correct":     500,
}


# Daily caps to prevent grinding
DAILY_LIMITS = {
    "predict_kospi":          1,
    "predict_nasdaq":         1,
    "predict_btc":            24,
    "sns_share_per_platform": 1,
    "deep_analysis":          5,
    "invite_immediate_count": 10,    # how many ref_ landings can pay 30 P/day
    "hourly_bet":             30,
}


# ─────────────────────────────────────────────────────────────
# Point spending rules (§3.2)
# ─────────────────────────────────────────────────────────────

POINT_COSTS = {
    "premium_1d":      1000,
    "premium_7d":      5000,
    "premium_30d":     15000,
    "extra_deep":      200,
    "persona_swap":    500,
    "new_persona_try": 300,
}


# ─────────────────────────────────────────────────────────────
# Tier system (§4)
# ─────────────────────────────────────────────────────────────

TIER_ORDER = ["bronze", "silver", "gold", "platinum", "diamond"]

# Cumulative thresholds for each tier (in Points)
TIER_THRESHOLDS_CUMULATIVE = {
    "bronze":   (0,        2_999),
    "silver":   (3_000,    9_999),
    "gold":     (10_000,   29_999),
    "platinum": (30_000,   99_999),
    "diamond":  (100_000,  float("inf")),
}

# Seasonal thresholds (used together with cumulative — lower of the two wins)
TIER_THRESHOLDS_SEASONAL = {
    "bronze":   (0,        999),
    "silver":   (1_000,    2_999),
    "gold":     (3_000,    9_999),
    "platinum": (10_000,   29_999),
    "diamond":  (30_000,   float("inf")),
}

# Diamond-internal stages (the only tier with absolute thresholds —
# others are span-based via compute_tier_stage).
DIAMOND_STAGE_THRESHOLDS = [100_000, 250_000, 500_000, 1_000_000, 2_000_000]

# Visual stage labels (▼▼ → ▲▲)
STAGE_LABELS = ["▼▼", "▼", "●", "▲", "▲▲"]


# ─────────────────────────────────────────────────────────────
# Premium activation paths (§2.3)
# ─────────────────────────────────────────────────────────────

PREMIUM_SOURCES = {"invite", "staking", "subscription", "point_redemption", "paid_trial"}


# ─────────────────────────────────────────────────────────────
# KST helpers (used everywhere for season + daily reset boundaries)
# ─────────────────────────────────────────────────────────────

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def kst_today_str() -> str:
    return (now_utc() + timedelta(hours=9)).date().isoformat()


def kst_now() -> datetime:
    return now_utc() + timedelta(hours=9)


def current_season_id() -> str:
    """Quarterly season — '2026-Q2' style. Used for points_this_season reset."""
    kst = kst_now()
    quarter = (kst.month - 1) // 3 + 1
    return f"{kst.year}-Q{quarter}"


def next_kst_midnight_utc() -> datetime:
    """Next 00:00 KST expressed as a UTC datetime. Daily reset boundary
    for daily_deep_count, daily prediction caps, etc."""
    kst = kst_now()
    next_kst = (kst.replace(hour=0, minute=0, second=0, microsecond=0)
                + timedelta(days=1))
    return next_kst - timedelta(hours=9)
