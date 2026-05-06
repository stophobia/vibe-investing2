"""§T2E-A — Daily attendance + streak bonus.

Once per KST day, a user can claim a base point grant (10 P) plus a
streak bonus (+5 P per consecutive day, capped at +50 P). The streak
resets if the user skips a day.

Idempotency: profile.last_attendance_kst stores the KST date string of
the last successful claim. Comparing against the current KST date makes
double-claim trivial to detect — no Blob counter needed.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import NamedTuple

from .gamification_config import POINTS, kst_today_str, kst_now
from .point_ledger import add_points
from .user_profile import UserProfile

logger = logging.getLogger(__name__)


class AttendanceResult(NamedTuple):
    success: bool
    base_points: int
    streak_bonus: int
    streak_days: int
    profile: UserProfile | None
    reason: str  # "ok" | "already_today"


def _yesterday_kst_str() -> str:
    return ((kst_now().date()) - timedelta(days=1)).isoformat()


async def daily_check_in(
    repo,
    user_key: str,
    *,
    usage_logger=None,
) -> AttendanceResult:
    """Claim today's attendance + streak bonus. Idempotent within a KST day."""
    today_kst = kst_today_str()
    profile = repo.get(user_key)
    if hasattr(profile, "__await__"):
        profile = await profile

    if profile.last_attendance_kst == today_kst:
        return AttendanceResult(
            success=False, base_points=0, streak_bonus=0,
            streak_days=profile.consecutive_login_days,
            profile=profile, reason="already_today",
        )

    # Streak: consecutive only if last attendance was yesterday KST
    if profile.last_attendance_kst == _yesterday_kst_str():
        new_streak = profile.consecutive_login_days + 1
    else:
        new_streak = 1

    base = POINTS["daily_attendance"]
    bonus_per_day = POINTS["consecutive_attendance_step"]
    bonus_cap = POINTS["consecutive_attendance_cap"]
    # Streak bonus = (streak - 1) × step, capped (so day 1 = 0 bonus, day 11+ caps)
    streak_bonus = min((new_streak - 1) * bonus_per_day, bonus_cap)

    total = base + streak_bonus
    profile = await add_points(
        repo, user_key, total,
        reason="daily_attendance",
        ref=today_kst,
        usage_logger=usage_logger,
    )

    # Update attendance markers
    update_res = repo.update(
        user_key,
        last_attendance_kst=today_kst,
        consecutive_login_days=new_streak,
    )
    if hasattr(update_res, "__await__"):
        profile = await update_res
    else:
        profile = update_res

    # §T2E-C — first-mission completion may unlock the inviter's verified bonus
    try:
        from .invite_service import maybe_validate_first_mission
        await maybe_validate_first_mission(repo, user_key, usage_logger=usage_logger)
    except Exception:
        logger.exception("invite validation hook failed (non-fatal)")

    return AttendanceResult(
        success=True, base_points=base, streak_bonus=streak_bonus,
        streak_days=new_streak, profile=profile, reason="ok",
    )
