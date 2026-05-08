"""§6 P1 — Multi-axis ranking with Wilson lower-bound scoring.

Wilson score handles small-sample fairness: 10/10 wins beats 1/1 win even
though both are 100%. We use 95% CI lower bound (z=1.96).

Two ranking kinds:
  - "predictions" : Wilson(wins, total) over settled+win/lose predictions
  - "referrers"   : weighted score over verified referees + their activity

Three periods: daily (24h) / weekly (7d) / monthly (30d).

Idempotent: writes to rankings/<kind>/<period>.json and rebuild_rankings_timer
is safe to re-run (just overwrites).
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

CONTAINER = "rankings"


@dataclass
class RankingRow:
    rank: int
    anon_short: str          # 8-char anon for public display
    score: float             # Wilson score for predictions, weighted score for referrers
    wins: int = 0
    total: int = 0
    win_rate: float = 0.0
    referees: int = 0
    referees_active: int = 0
    referees_donated: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# Wilson score (95% lower bound)
# ─────────────────────────────────────────────────────────────────────────────
def wilson_score_lower_bound(wins: int, total: int, z: float = 1.96) -> float:
    """Lower bound of Wilson score 95% confidence interval.

    Returns 0.0 when total = 0. Handles tiny samples gracefully (10/10 > 1/1).
    """
    if total <= 0:
        return 0.0
    p = wins / total
    z2 = z * z
    n = total
    centre = p + z2 / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z2 / (4 * n)) / n)
    return (centre - margin) / (1 + z2 / n)


# ─────────────────────────────────────────────────────────────────────────────
# Period helper
# ─────────────────────────────────────────────────────────────────────────────
def _cutoff_iso(period: str, now_utc: datetime | None = None) -> str:
    """Returns ISO UTC cutoff for the period."""
    now_utc = now_utc or datetime.now(timezone.utc)
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 1)
    return (now_utc - timedelta(days=days)).isoformat(timespec="seconds")


# ─────────────────────────────────────────────────────────────────────────────
# Build prediction ranking
# ─────────────────────────────────────────────────────────────────────────────
async def build_prediction_ranking(account_name: str, period: str,
                                   credential=None,
                                   limit: int = 100) -> list[RankingRow]:
    """Aggregate settled predictions in window → Wilson rank list."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    from .prediction_repo import _to_prediction

    cutoff = _cutoff_iso(period)
    creds = credential or DefaultAzureCredential()
    by_anon: dict[str, dict[str, int]] = {}  # anon[:8] → {wins, total}

    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("predictions")
            try:
                await container.create_container()
            except Exception:
                pass
            async for blob in container.list_blobs():
                if not blob.name.endswith(".json"):
                    continue
                try:
                    body = await (await container.get_blob_client(blob.name)
                                  .download_blob()).readall()
                    p = _to_prediction(json.loads(body))
                except Exception:
                    continue
                if p.status != "settled":
                    continue
                if not p.settled_at or p.settled_at < cutoff:
                    continue
                key = (p.anon_user_id or "")[:8]
                if not key:
                    continue
                slot = by_anon.setdefault(key, {"wins": 0, "total": 0})
                slot["total"] += 1
                if p.result == "win":
                    slot["wins"] += 1
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    rows: list[RankingRow] = []
    for key, agg in by_anon.items():
        score = wilson_score_lower_bound(agg["wins"], agg["total"])
        rows.append(RankingRow(
            rank=0, anon_short=key, score=round(score, 4),
            wins=agg["wins"], total=agg["total"],
            win_rate=round(agg["wins"] / agg["total"], 4) if agg["total"] else 0,
        ))
    rows.sort(key=lambda r: (-r.score, -r.total))
    for i, r in enumerate(rows[:limit], 1):
        r.rank = i
    return rows[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# Build referrer ranking
# ─────────────────────────────────────────────────────────────────────────────
async def build_referrer_ranking(account_name: str, period: str,
                                 credential=None,
                                 limit: int = 100) -> list[RankingRow]:
    """Score = verified_referees × 1.0 + active_referees × 0.5
              + donated_referees × 2.0
    All counts come from user profiles (invite_validated_count etc.) so this
    is approximate per-period — exact per-period attribution requires a
    separate referrals/ ledger which §7 may add."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    creds = credential or DefaultAzureCredential()
    rows: list[RankingRow] = []
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("users")
            try:
                await container.create_container()
            except Exception:
                pass
            async for blob in container.list_blobs():
                if not blob.name.endswith(".json"):
                    continue
                try:
                    body = await (await container.get_blob_client(blob.name)
                                  .download_blob()).readall()
                    d = json.loads(body)
                except Exception:
                    continue
                anon_short = (d.get("anon_user_id") or "")[:8]
                if not anon_short:
                    continue
                verified = int(d.get("invite_validated_count") or 0)
                if verified == 0:
                    continue
                # MVP: treat invite_validated_count as the verified count.
                # active/donated come from referee profiles which require a
                # cross-scan — deferred to §7's referrals ledger.
                score = verified * 1.0
                rows.append(RankingRow(
                    rank=0, anon_short=anon_short, score=round(score, 2),
                    referees=verified,
                ))
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    rows.sort(key=lambda r: (-r.score, -r.referees))
    for i, r in enumerate(rows[:limit], 1):
        r.rank = i
    return rows[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# Persist
# ─────────────────────────────────────────────────────────────────────────────
async def write_ranking_blob(account_name: str, period: str, kind: str,
                             rows: list[RankingRow], credential=None) -> None:
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    payload = {
        "kind": kind,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ranking": [asdict(r) for r in rows],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
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
            bc = container.get_blob_client(f"{kind}/{period}.json")
            await bc.upload_blob(body, overwrite=True)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def read_ranking_blob(account_name: str, period: str, kind: str,
                            credential=None) -> dict | None:
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            bc = svc.get_blob_client(CONTAINER, f"{kind}/{period}.json")
            try:
                body = await (await bc.download_blob()).readall()
            except ResourceNotFoundError:
                return None
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
    return json.loads(body)
