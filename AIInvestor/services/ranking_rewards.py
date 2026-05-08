"""§6 P1 — Daily reward payout for top-10 rankings.

Reward tables per work-priority §6.4:
  predictions:
    daily   1=500 / 2-3=200 / 4-10=100
    weekly  1=2000 / 2-3=1000 / 4-10=500
    monthly 1=10000 / 2-3=5000 / 4-10=2000
  referrers: 2× the prediction tier

Idempotent: rankings/rewards_paid/<period>/<date>.json prevents double-pay.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from .point_ledger import add_points

logger = logging.getLogger(__name__)


PREDICTION_REWARDS = {
    "daily":   {1: 500,  **{i: 200  for i in (2, 3)}, **{i: 100  for i in range(4, 11)}},
    "weekly":  {1: 2000, **{i: 1000 for i in (2, 3)}, **{i: 500  for i in range(4, 11)}},
    "monthly": {1: 10000, **{i: 5000 for i in (2, 3)}, **{i: 2000 for i in range(4, 11)}},
}
REFERRER_REWARDS = {p: {r: v * 2 for r, v in tiers.items()}
                    for p, tiers in PREDICTION_REWARDS.items()}


def _kst_today_iso() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


async def _already_paid(account_name: str, period: str, kind: str,
                        date_iso: str, credential=None) -> bool:
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            bc = svc.get_blob_client(
                "rankings", f"rewards_paid/{kind}/{period}/{date_iso}.json")
            try:
                await bc.get_blob_properties()
                return True
            except ResourceNotFoundError:
                return False
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def _mark_paid(account_name: str, period: str, kind: str, date_iso: str,
                     payouts: list[dict], credential=None) -> None:
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    creds = credential or DefaultAzureCredential()
    payload = {
        "kind": kind, "period": period, "date": date_iso,
        "payouts": payouts,
        "paid_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("rankings")
            try:
                await container.create_container()
            except Exception:
                pass
            bc = container.get_blob_client(
                f"rewards_paid/{kind}/{period}/{date_iso}.json")
            await bc.upload_blob(body, overwrite=False)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def _resolve_user_key_by_anon_short(account_name: str, anon_short: str,
                                          credential=None) -> str | None:
    """Find user_key by 8-char anon prefix scan. O(N) — N small in MVP."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("users")
            async for blob in container.list_blobs(name_starts_with=f"{anon_short[:2]}/"):
                if not blob.name.endswith(".json"):
                    continue
                try:
                    body = await (await container.get_blob_client(blob.name)
                                  .download_blob()).readall()
                    d = json.loads(body)
                    if (d.get("anon_user_id") or "").startswith(anon_short):
                        return d.get("user_key") or None
                except Exception:
                    continue
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
    return None


async def pay_rewards(repo, account_name: str, kind: str, period: str,
                     ranking: list[dict], *, usage_logger=None,
                     credential=None) -> dict:
    """Pay top-10 rewards for one (kind, period). Idempotent per KST date."""
    table = (PREDICTION_REWARDS if kind == "predictions"
             else REFERRER_REWARDS).get(period, {})
    if not table:
        return {"paid": 0, "skipped": "no_reward_table"}

    date_iso = _kst_today_iso()
    if await _already_paid(account_name, period, kind, date_iso,
                           credential=credential):
        return {"paid": 0, "skipped": "already_paid_today"}

    payouts: list[dict] = []
    for row in ranking[:10]:
        rank = row.get("rank", 0)
        if rank not in table:
            continue
        anon_short = row.get("anon_short") or ""
        user_key = await _resolve_user_key_by_anon_short(
            account_name, anon_short, credential=credential)
        if not user_key:
            continue
        amount = table[rank]
        try:
            await add_points(
                repo, user_key, amount,
                reason=f"ranking_{kind}_{period}_rank{rank}",
                ref=date_iso, usage_logger=usage_logger,
            )
            payouts.append({
                "anon_short": anon_short, "user_key_hash": user_key[:12],
                "rank": rank, "amount_p": amount,
            })
        except Exception:
            logger.exception("ranking reward credit failed for %s", anon_short)

    if payouts:
        await _mark_paid(account_name, period, kind, date_iso, payouts,
                         credential=credential)

    return {"paid": len(payouts), "date_iso": date_iso}
