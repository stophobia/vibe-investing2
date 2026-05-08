"""§7 — Referrer milestone bonuses for referee donations.

When a refereed user crosses a $100/$500/$1k/$5k cumulative donation
threshold, the referrer gets a scheduled bonus paid out 30 days later
(holding period — protects against donation→refund abuse).

Storage: referrer_rewards/<referrer>/<referee>.<milestone>.json
Each blob: {referrer, referee, milestone, amount_p, scheduled_at, paid_at}.

Daily cron at KST 04:00 walks all pending entries, pays out any with
scheduled_at <= now, then moves the record to referrer_rewards/paid/.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

CONTAINER = "referrer-rewards"
HOLDING_DAYS = 30

# Cumulative donation thresholds → referrer P bonus
MILESTONES = {
    100:  500,
    500:  2000,
    1000: 5000,
    5000: 25000,
}


@dataclass
class MilestoneRecord:
    referrer_anon: str          # 8-char anon prefix of referrer
    referee_user_key: str       # full user_key of referee (for credit lookup)
    referrer_user_key: str      # full user_key of referrer (target of payout)
    milestone_usdt: int         # 100 | 500 | 1000 | 5000
    amount_p: int
    scheduled_at: str           # ISO UTC, payout earliest at this time
    triggered_at: str           # when referee crossed the threshold
    paid_at: str = ""


def _kst_today_iso() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


def _path_pending(referrer_anon: str, referee_anon: str, milestone: int) -> str:
    return f"pending/{referrer_anon}/{referee_anon}.{milestone}.json"


def _path_paid(referrer_anon: str, referee_anon: str, milestone: int) -> str:
    return f"paid/{referrer_anon}/{referee_anon}.{milestone}.json"


# ─────────────────────────────────────────────────────────────────────────────
# Schedule (called by donation_service after a confirmed donation)
# ─────────────────────────────────────────────────────────────────────────────
async def schedule_for_donation(account_name: str, referee_profile,
                                referrer_user_key: str,
                                new_total_usdt: float,
                                old_total_usdt: float,
                                credential=None) -> list[int]:
    """Detect milestones crossed by `new_total - old_total`, schedule payouts.

    Returns the list of crossed milestone amounts.
    """
    crossed = [m for m in MILESTONES
               if old_total_usdt < m <= new_total_usdt]
    if not crossed:
        return []

    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    # Resolve referrer anon[:8] for blob path partition
    from .user_profile import make_anon_user_id
    # We don't have salt here directly — caller supplies referrer_user_key,
    # we derive anon from the referee_profile (the referrer's anon is stored
    # in referee_profile.invited_by_anon)
    referrer_anon_short = (referee_profile.invited_by_anon or "")[:8]
    if not referrer_anon_short:
        return []

    referee_anon_short = (referee_profile.anon_user_id or "")[:8]
    now = datetime.now(timezone.utc)
    scheduled_at = (now + timedelta(days=HOLDING_DAYS)).isoformat(timespec="seconds")
    triggered_at = now.isoformat(timespec="seconds")

    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except Exception:
                pass
            for ms in crossed:
                rec = MilestoneRecord(
                    referrer_anon=referrer_anon_short,
                    referee_user_key=referee_profile.user_key,
                    referrer_user_key=referrer_user_key,
                    milestone_usdt=ms,
                    amount_p=MILESTONES[ms],
                    scheduled_at=scheduled_at,
                    triggered_at=triggered_at,
                )
                bc = container.get_blob_client(
                    _path_pending(referrer_anon_short, referee_anon_short, ms))
                await bc.upload_blob(
                    json.dumps(asdict(rec), ensure_ascii=False).encode(),
                    overwrite=False,  # idempotent: same milestone twice → 409
                )
    except Exception:
        logger.warning("milestone schedule write failed", exc_info=True)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    return crossed


# ─────────────────────────────────────────────────────────────────────────────
# Payout (KST 04:00 cron)
# ─────────────────────────────────────────────────────────────────────────────
async def pay_due_milestones(repo, account_name: str, *,
                             usage_logger=None, credential=None) -> dict:
    """Walk pending/, pay any with scheduled_at <= now, move to paid/.

    Returns {paid: int, skipped_future: int, errors: int}.
    """
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    from .point_ledger import add_points

    counts = {"paid": 0, "skipped_future": 0, "errors": 0}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except Exception:
                pass
            async for blob in container.list_blobs(name_starts_with="pending/"):
                if not blob.name.endswith(".json"):
                    continue
                try:
                    bc = container.get_blob_client(blob.name)
                    body = await (await bc.download_blob()).readall()
                    d = json.loads(body)
                    if d.get("scheduled_at", "") > now:
                        counts["skipped_future"] += 1
                        continue
                    await add_points(
                        repo, d["referrer_user_key"], int(d["amount_p"]),
                        reason=f"referrer_milestone_{d['milestone_usdt']}",
                        ref=d.get("referee_user_key", ""),
                        usage_logger=usage_logger,
                    )
                    d["paid_at"] = now
                    paid_bc = container.get_blob_client(_path_paid(
                        d["referrer_anon"],
                        (d.get("referee_user_key") or "").split("tg:")[-1][:8],
                        int(d["milestone_usdt"]),
                    ))
                    await paid_bc.upload_blob(
                        json.dumps(d, ensure_ascii=False).encode(),
                        overwrite=True,
                    )
                    await bc.delete_blob()
                    counts["paid"] += 1
                except Exception:
                    logger.exception("milestone payout failed for %s", blob.name)
                    counts["errors"] += 1
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# Donation tier (Supporter / Patron / Benefactor / Champion)
# ─────────────────────────────────────────────────────────────────────────────
def donation_tier(total_usdt: float) -> str:
    """Map cumulative USDT donation to tier label."""
    if total_usdt >= 5000:
        return "champion"
    if total_usdt >= 1000:
        return "benefactor"
    if total_usdt >= 500:
        return "patron"
    if total_usdt >= 1:
        return "supporter"
    return "none"


def is_supporter_or_higher(total_usdt: float) -> bool:
    return total_usdt >= 1.0
