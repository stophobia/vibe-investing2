"""§3 — Daily-fortune service: risk-pool loading + per-user picks + unlock.

Glue layer between fortune_match.py (pure determinism) and the storage /
endpoint side. Loads data/risk_pools.json once per process.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .fortune_match import FortuneResult, select_daily_free_stock
from .point_ledger import deduct_points
from .user_profile import UserProfile

logger = logging.getLogger(__name__)

UNLOCK_COST_POINTS = 100   # per spec §3.6

_POOL_PATH = Path(__file__).resolve().parent.parent / "data" / "risk_pools.json"
_pool_cache: dict[str, list[str]] | None = None


def get_risk_pool() -> dict[str, list[str]]:
    """Load + cache risk_pools.json (hot reload not needed — restart Functions)."""
    global _pool_cache
    if _pool_cache is not None:
        return _pool_cache
    with _POOL_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    _pool_cache = {k: v for k, v in raw.items() if not k.startswith("_")}
    return _pool_cache


# ─────────────────────────────────────────────────────────────────────────────
# Date helpers
# ─────────────────────────────────────────────────────────────────────────────
def _kst_today_compact() -> str:
    """KST today as YYYYMMDD (no separators) — used as fortune seed component."""
    return (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y%m%d")


def _kst_today_iso() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


def _normalize_birth_for_seed(profile: UserProfile) -> tuple[str, str]:
    """Convert profile's stored birth fields → (YYYYMMDD, HHMM|"9999")."""
    birth_date = (profile.saju_birth_date or "").replace("-", "")
    if profile.saju_birth_hour < 0:
        birth_time = "9999"
    else:
        birth_time = f"{profile.saju_birth_hour:02d}00"
    return birth_date, birth_time


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def select_for_user(profile: UserProfile) -> FortuneResult | None:
    """Run today's fortune match for the user, or None if birth data missing."""
    if not profile.saju_birth_date:
        return None
    birth_date, birth_time = _normalize_birth_for_seed(profile)
    pool = get_risk_pool()
    return select_daily_free_stock(
        birth_date=birth_date, birth_time=birth_time,
        today_kst=_kst_today_compact(), risk_pool=pool,
    )


def is_age_19_or_older(birth_date_iso: str, today_iso: str | None = None) -> bool:
    """Korean 만나이 ≥ 19 — civil age computed by full-year offset.

    birth_date_iso: YYYY-MM-DD
    """
    try:
        b = datetime.strptime(birth_date_iso, "%Y-%m-%d").date()
    except ValueError:
        return False
    today_iso = today_iso or _kst_today_iso()
    today = datetime.strptime(today_iso, "%Y-%m-%d").date()
    years = today.year - b.year
    if (today.month, today.day) < (b.month, b.day):
        years -= 1
    return years >= 19


def is_already_unlocked_today(profile: UserProfile, ticker: str) -> bool:
    """Idempotency check — same risk re-unlocked today should not re-charge."""
    today = _kst_today_iso()
    return (profile.saju_unlocked_date_kst == today
            and ticker in (profile.saju_unlocked_today or []))


async def unlock_via_points(repo, profile: UserProfile,
                            ticker: str, *, usage_logger=None) -> tuple[bool, str, UserProfile | None]:
    """Channel='points' — deduct UNLOCK_COST_POINTS and add ticker to today's set.
    Idempotent for same-day re-unlocks (no re-charge).
    Returns (ok, reason, updated_profile)."""
    if is_already_unlocked_today(profile, ticker):
        return True, "already_unlocked", profile

    new_profile = await deduct_points(
        repo, profile.user_key, UNLOCK_COST_POINTS,
        reason="fortune_unlock_points", ref=ticker, usage_logger=usage_logger,
    )
    if new_profile is None:
        return False, "insufficient_points", None

    today = _kst_today_iso()
    updates = list(new_profile.saju_unlocked_today or [])
    if ticker not in updates:
        updates.append(ticker)
    update_call = repo.update(
        new_profile.user_key,
        saju_unlocked_today=updates,
        saju_unlocked_date_kst=today,
    )
    final = await update_call if hasattr(update_call, "__await__") else update_call
    return True, "ok", final


# ─────────────────────────────────────────────────────────────────────────────
# §7 — Donation / Invite unlock channels (no point deduction)
# ─────────────────────────────────────────────────────────────────────────────
async def unlock_via_donation(repo, account_name: str, profile: UserProfile,
                              ticker: str) -> tuple[bool, str, UserProfile | None]:
    """Channel='donation' — eligible if user has any confirmed donation.

    The donation system itself credits P via add_points; this channel
    skips that double-charge by spending the P-equivalent already credited
    (i.e. donation already paid for the unlock implicitly). For MVP we just
    check existence of a confirmed donation and unlock for free.
    """
    if is_already_unlocked_today(profile, ticker):
        return True, "already_unlocked", profile

    # Scan donation-intents for any confirmed by this user
    has_donation = False
    try:
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        import json as _json
        creds = DefaultAzureCredential()
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("donation-intents")
            try:
                async for blob in container.list_blobs():
                    if not blob.name.endswith(".json"):
                        continue
                    body = await (await container.get_blob_client(blob.name)
                                  .download_blob()).readall()
                    d = _json.loads(body)
                    if (d.get("user_key") == profile.user_key and
                            d.get("status") == "confirmed"):
                        has_donation = True
                        break
            except Exception:
                pass
        await creds.close()
    except Exception:
        logger.exception("donation channel scan failed")

    if not has_donation:
        return False, "no_confirmed_donation", None

    today = _kst_today_iso()
    updates = list(profile.saju_unlocked_today or [])
    if ticker not in updates:
        updates.append(ticker)
    call = repo.update(
        profile.user_key,
        saju_unlocked_today=updates,
        saju_unlocked_date_kst=today,
    )
    final = await call if hasattr(call, "__await__") else call
    return True, "ok", final


async def unlock_via_invite(repo, profile: UserProfile,
                            ticker: str) -> tuple[bool, str, UserProfile | None]:
    """Channel='invite' — eligible if user has ≥1 verified referee."""
    if is_already_unlocked_today(profile, ticker):
        return True, "already_unlocked", profile

    if (profile.invite_validated_count or 0) < 1:
        return False, "no_verified_referee", None

    today = _kst_today_iso()
    updates = list(profile.saju_unlocked_today or [])
    if ticker not in updates:
        updates.append(ticker)
    call = repo.update(
        profile.user_key,
        saju_unlocked_today=updates,
        saju_unlocked_date_kst=today,
    )
    final = await call if hasattr(call, "__await__") else call
    return True, "ok", final


REROLL_COST_POINTS = 10
SUPPORTER_FREE_REROLLS_PER_DAY = 1


async def reroll_fortune(repo, profile: UserProfile, *,
                         usage_logger=None) -> tuple[bool, str, UserProfile | None]:
    """§7 — Reroll today's lucky number.

    Supporter+ tier (donation_total_usdt ≥ $1) gets SUPPORTER_FREE_REROLLS_PER_DAY
    free reroll(s) per KST day. Beyond that — and for non-supporters — it costs
    REROLL_COST_POINTS (10 P) per reroll.
    """
    from .referrer_milestones import is_supporter_or_higher
    today = _kst_today_iso()

    # Reset counter if it's a new KST day
    used_today = profile.fortune_reroll_count_today
    if profile.fortune_reroll_date_kst != today:
        used_today = 0

    is_supporter = is_supporter_or_higher(profile.donation_total_usdt or 0)
    free_remaining = max(0, SUPPORTER_FREE_REROLLS_PER_DAY - used_today) if is_supporter else 0

    if free_remaining > 0:
        # Free path — just bump counter
        update_call = repo.update(
            profile.user_key,
            fortune_reroll_count_today=used_today + 1,
            fortune_reroll_date_kst=today,
        )
        final = await update_call if hasattr(update_call, "__await__") else update_call
        return True, "ok_free", final

    new_profile = await deduct_points(
        repo, profile.user_key, REROLL_COST_POINTS,
        reason="fortune_reroll", ref="", usage_logger=usage_logger,
    )
    if new_profile is None:
        return False, "insufficient_points", None

    # Bump reroll counter on the fresh profile
    update_call = repo.update(
        profile.user_key,
        fortune_reroll_count_today=used_today + 1,
        fortune_reroll_date_kst=today,
    )
    final = await update_call if hasattr(update_call, "__await__") else update_call
    return True, "ok", final
