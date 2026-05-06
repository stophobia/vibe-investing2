"""§T2E-C — Friend invite system.

Reward split (anti-abuse):
  Immediate, on `/start ref_<code>` link click:
    inviter:  +30 P  (capped at 10 landings/day to prevent spam)
    invitee:  +200 P (signup_with_invite, 100 base + 100 invite-bonus)

  Deferred, on invitee's first mission completion (within 7d):
    inviter:  +470 P  (= total 500 with the 30 already paid)
    invitee:  unlocks normal earning paths

Anti-abuse:
  • Self-invite refused (inviter == invitee)
  • Already-invited refused (invitee.invited_by_anon set)
  • 24-hour minimum between signup and first earning to discourage
    multi-account farming (deferred to gating layer at top of features)
  • Zombie detection: if invitee has 0 missions completed after 7 days,
    inviter penalty -30 P + zombie_count++. After 5+ landings with >50%
    zombie ratio → flag for admin review.
"""

from __future__ import annotations

import logging
import secrets
import string
from datetime import datetime, timezone, timedelta

from .gamification_config import POINTS, DAILY_LIMITS, kst_today_str
from .point_ledger import add_points, adjust_for_penalty
from .user_profile import UserProfile

logger = logging.getLogger(__name__)


def _generate_invite_code() -> str:
    """8-char alphanumeric, capitals + digits."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


async def get_or_create_invite_code(repo, user_key: str) -> str:
    """Lazy-generate the invite code on first use. Persists to profile."""
    profile = repo.get_or_create(user_key=user_key, default_language="en", default_persona="buffett")
    if hasattr(profile, "__await__"):
        profile = await profile
    if profile.invite_code:
        return profile.invite_code

    # Generate + persist (with collision retry — extremely rare for 8-char × 36 alphabet)
    for _ in range(5):
        code = _generate_invite_code()
        # Optimistic: just set and trust uniqueness; on collision the inviter lookup
        # would find the OTHER user. To harden, check existing users — but that
        # requires a per-code index; we accept the ~1 in 2.8 trillion collision risk.
        update_res = repo.update(user_key, invite_code=code)
        if hasattr(update_res, "__await__"):
            await update_res
        return code
    raise RuntimeError("invite code generation failed")


async def find_inviter_by_code(repo, invite_code: str) -> UserProfile | None:
    """Find the user who owns this invite code. Returns None if unknown."""
    code = invite_code.strip().upper()
    if not code or len(code) != 8:
        return None
    # SQLite has an index on invite_code; we use raw SQL via the connect helper.
    if hasattr(repo, "_connect"):
        with repo._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE invite_code = ? LIMIT 1", (code,)).fetchone()
        if row is None:
            return None
        from .user_profile import _row_to_profile
        return _row_to_profile(row)
    # Blob backend has no secondary index — scan would be too expensive at scale.
    # Defer to a lightweight "code → user_key" reverse-index blob (TODO when on Blob).
    logger.warning("find_inviter_by_code: Blob backend reverse-lookup not implemented")
    return None


async def setup_invitee_with_referral(
    repo,
    new_user_key: str,
    inviter_anon: str,
    *,
    usage_logger=None,
) -> tuple[bool, UserProfile | None, str]:
    """Mark a new user as referred + grant the invitee welcome bonus.

    Returns (success, profile, error). Errors:
      already_invited | self_invite | invalid_inviter
    """
    invitee = repo.get_or_create(user_key=new_user_key, default_language="ko", default_persona="buffett")
    if hasattr(invitee, "__await__"):
        invitee = await invitee

    if invitee.invited_by_anon:
        # Already credited a different inviter — silently keep first one
        return False, invitee, "already_invited"
    if invitee.anon_user_id == inviter_anon:
        return False, invitee, "self_invite"

    # Tag the invitee with the inviter's anon_user_id (not user_key — we keep
    # raw user_keys out of cross-user state)
    update_res = repo.update(
        new_user_key,
        invited_by_anon=inviter_anon,
    )
    if hasattr(update_res, "__await__"):
        invitee = await update_res
    else:
        invitee = update_res

    # Grant the welcome bonus (signup_with_invite = 200 = 100 signup + 100 invite-bonus)
    invitee = await add_points(
        repo, new_user_key, POINTS["signup_with_invite"],
        reason="signup_with_invite",
        ref=f"inviter={inviter_anon[:8]}",
        usage_logger=usage_logger,
    )
    return True, invitee, ""


async def reward_inviter_immediate(
    repo,
    inviter_user_key: str,
    invitee_anon: str,
    *,
    usage_logger=None,
    blob_account: str | None = None,
) -> tuple[bool, int, str]:
    """Pay the +30 P landing bonus to the inviter, capped at 10/day.

    Returns (paid, count_today, reason).
    Reasons: ok | over_daily_limit | counter_failed
    """
    from .blob_counter import increment_daily_counter
    counter_name = f"invite_immediate:{inviter_user_key}"
    try:
        count = await increment_daily_counter(counter_name, account_name=blob_account)
    except Exception:
        # If counter fails, be conservative — don't pay (avoids double-pay on retry)
        logger.exception("invite_immediate counter failed for %s", inviter_user_key)
        return False, 0, "counter_failed"

    cap = DAILY_LIMITS["invite_immediate_count"]
    if count > cap:
        logger.info("inviter %s exceeded daily landing cap (%d > %d)",
                    inviter_user_key, count, cap)
        return False, count, "over_daily_limit"

    await add_points(
        repo, inviter_user_key, POINTS["invite_landing"],
        reason="invite_landing",
        ref=f"invitee_anon={invitee_anon[:8]}",
        usage_logger=usage_logger,
    )

    # Bump landing counter on inviter profile
    profile = repo.get(inviter_user_key)
    if hasattr(profile, "__await__"):
        profile = await profile
    update_res = repo.update(
        inviter_user_key,
        invite_landings_count=profile.invite_landings_count + 1,
    )
    if hasattr(update_res, "__await__"):
        await update_res

    return True, count, "ok"


async def reward_inviter_verified(
    repo,
    inviter_user_key: str,
    invitee_anon: str,
    invitee_user_key: str,
    *,
    usage_logger=None,
) -> bool:
    """Pay the deferred +470 P bonus when the invitee completes their first
    mission. Idempotent — won't double-pay if invitee_validated_at is set."""
    invitee = repo.get(invitee_user_key)
    if hasattr(invitee, "__await__"):
        invitee = await invitee

    if invitee.invite_validated_at:
        return False  # already validated

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    update_res = repo.update(invitee_user_key, invite_validated_at=now)
    if hasattr(update_res, "__await__"):
        await update_res

    inviter = repo.get(inviter_user_key)
    if hasattr(inviter, "__await__"):
        inviter = await inviter

    await add_points(
        repo, inviter_user_key, POINTS["invite_verified"],
        reason="invite_verified",
        ref=f"invitee_anon={invitee_anon[:8]}",
        usage_logger=usage_logger,
    )
    update_res = repo.update(
        inviter_user_key,
        invite_validated_count=inviter.invite_validated_count + 1,
    )
    if hasattr(update_res, "__await__"):
        await update_res
    return True


async def maybe_validate_first_mission(
    repo,
    user_key: str,
    *,
    usage_logger=None,
) -> bool:
    """Called whenever a user completes any mission. If they were invited
    AND haven't been validated yet, fire reward_inviter_verified."""
    profile = repo.get(user_key)
    if hasattr(profile, "__await__"):
        profile = await profile

    if not profile.invited_by_anon or profile.invite_validated_at:
        return False

    # Find the inviter user_key by their anon (need reverse lookup)
    if hasattr(repo, "_connect"):
        with repo._connect() as conn:
            row = conn.execute(
                "SELECT user_key FROM users WHERE anon_user_id = ? LIMIT 1",
                (profile.invited_by_anon,),
            ).fetchone()
        if not row:
            return False
        inviter_user_key = row["user_key"]
    else:
        # Blob — reverse lookup deferred
        return False

    await reward_inviter_verified(
        repo, inviter_user_key, profile.invited_by_anon, user_key,
        usage_logger=usage_logger,
    )
    return True


# ──────────────────────────────────────────────────────────
# Zombie detection (Timer trigger consumes this)
# ──────────────────────────────────────────────────────────

async def detect_zombies(
    repo,
    *,
    usage_logger=None,
    days_threshold: int = 7,
) -> int:
    """Find invitees with 0 missions after `days_threshold` days; penalize their
    inviter -30 P. Returns count of zombies processed."""
    if not hasattr(repo, "_connect"):
        return 0  # Blob version deferred

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).isoformat()
    processed = 0

    with repo._connect() as conn:
        rows = conn.execute(
            """
            SELECT user_key, anon_user_id, invited_by_anon, points_cumulative, created_at
            FROM users
            WHERE invited_by_anon != ''
              AND invite_validated_at = ''
              AND created_at < ?
              AND points_cumulative <= 200    -- only signup bonus claimed
            """,
            (cutoff,),
        ).fetchall()

    for row in rows:
        # Find inviter by anon
        if not hasattr(repo, "_connect"):
            continue
        with repo._connect() as conn:
            inviter_row = conn.execute(
                "SELECT user_key FROM users WHERE anon_user_id = ? LIMIT 1",
                (row["invited_by_anon"],),
            ).fetchone()
        if not inviter_row:
            continue
        inviter_user_key = inviter_row["user_key"]

        # Mark this invitee processed (set invite_validated_at to a sentinel)
        update_res = repo.update(row["user_key"], invite_validated_at="zombie")
        if hasattr(update_res, "__await__"):
            await update_res

        # Penalty
        try:
            await adjust_for_penalty(
                repo, inviter_user_key, abs(POINTS["invite_zombie_penalty"]),
                reason="invite_zombie_penalty",
                ref=f"zombie_anon={row['anon_user_id'][:8]}",
                usage_logger=usage_logger,
            )
            inviter = repo.get(inviter_user_key)
            if hasattr(inviter, "__await__"):
                inviter = await inviter
            update_res = repo.update(
                inviter_user_key,
                invite_zombie_count=inviter.invite_zombie_count + 1,
            )
            if hasattr(update_res, "__await__"):
                await update_res
            processed += 1
        except Exception:
            logger.exception("zombie penalty failed for inviter=%s", inviter_user_key)

    return processed
