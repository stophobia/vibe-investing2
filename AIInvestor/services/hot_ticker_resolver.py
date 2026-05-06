"""Resolve the current HOT_TICKERS list — combines two signals:

  1. Static preference (data/korean_favorite_tickers.csv) — editorial weight
     based on publicly-known retail bias. Top-rank tickers get higher score.

  2. Dynamic frequency (logs/yyyy/mm/dd/HH.ndjson tier=*_hit/live counts) —
     real traffic from the last N days. Updates the ranking automatically.

The combined score is normalized so each signal contributes ~50% of the final
ordering. The top K (default 50) are exposed as HOT_TICKERS for downstream
consumers (prewarm_service, ticker_data_cache).

Spec: report-generation-policy-v1.0-ko.md §5
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KOREAN_FAVORITES_CSV = DATA_DIR / "korean_favorite_tickers.csv"

LOGS_CONTAINER = "logs"


@dataclass
class TickerEntry:
    ticker: str
    name_kr: str = ""
    name_en: str = ""
    reason_kr: str = ""
    preference_rank: int = 0     # 1-based; 0 = not in favorites list
    frequency_count: int = 0     # last 7d webhook count
    score: float = 0.0           # final combined


# -----------------------------------------------------------------------
# Static preference loader
# -----------------------------------------------------------------------

def load_korean_favorites() -> dict[str, TickerEntry]:
    """Load the editorial top-K Korean retail favorites with rank."""
    out: dict[str, TickerEntry] = {}
    if not KOREAN_FAVORITES_CSV.exists():
        logger.warning("korean_favorite_tickers.csv missing")
        return out
    with KOREAN_FAVORITES_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rank = int(row["rank"])
            except (KeyError, ValueError):
                continue
            ticker = (row.get("ticker") or "").strip().upper()
            if not ticker:
                continue
            out[ticker] = TickerEntry(
                ticker=ticker,
                name_kr=(row.get("name_kr") or "").strip(),
                name_en=(row.get("name_en") or "").strip(),
                reason_kr=(row.get("reason_kr") or "").strip(),
                preference_rank=rank,
            )
    return out


# -----------------------------------------------------------------------
# Dynamic frequency loader (reads logs/ NDJSON)
# -----------------------------------------------------------------------

async def load_frequency_counts(
    storage_account_name: str,
    days: int = 7,
    credential=None,
) -> dict[str, int]:
    """Walk logs/yyyy/mm/dd/*.ndjson over the last `days` days and count
    each ticker's appearance (any tier). Returns {ticker: count}."""
    creds = credential or DefaultAzureCredential()
    counts: dict[str, int] = {}
    now = datetime.now(timezone.utc)
    earliest = now - timedelta(days=days)

    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(LOGS_CONTAINER)
            async for blob in container.list_blobs():
                # path: yyyy/mm/dd/HH.ndjson
                try:
                    parts = blob.name.split("/")
                    blob_dt = datetime(
                        int(parts[0]), int(parts[1]), int(parts[2]),
                        int(parts[3].split(".")[0]),
                        tzinfo=timezone.utc,
                    )
                    if blob_dt < earliest - timedelta(hours=1):
                        continue
                except (ValueError, IndexError):
                    continue

                try:
                    client = container.get_blob_client(blob.name)
                    stream = await client.download_blob()
                    body = await stream.readall()
                    for line in body.decode("utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            evt = json.loads(line)
                            tk = (evt.get("ticker") or "").strip().upper()
                            if tk and len(tk) <= 12:
                                counts[tk] = counts.get(tk, 0) + 1
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    logger.debug("failed reading log blob %s", blob.name)
                    continue
    except Exception as exc:
        logger.warning("frequency count walk failed: %s", exc)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    return counts


# -----------------------------------------------------------------------
# Combined score
# -----------------------------------------------------------------------

def combine_scores(
    favorites: dict[str, TickerEntry],
    frequency: dict[str, int],
    extra_pool: Iterable[str] = (),
) -> list[TickerEntry]:
    """Combine static and dynamic signals into a unified ranking.

    Score = 0.5 × preference_score + 0.5 × frequency_score
      preference_score: 14 - rank (so rank-1 = 13, rank-14 = 0)
      frequency_score : count / max_count × 14

    Tickers in favorites only:    score = preference_score (frequency=0)
    Tickers in frequency only:    score = frequency_score (rank=0)
    Tickers in both:              full combined
    """
    universe: dict[str, TickerEntry] = {}

    # Seed with favorites
    for tk, fav in favorites.items():
        universe[tk] = TickerEntry(
            ticker=tk,
            name_kr=fav.name_kr,
            name_en=fav.name_en,
            reason_kr=fav.reason_kr,
            preference_rank=fav.preference_rank,
        )

    # Add frequency entries (and merge)
    max_count = max(frequency.values()) if frequency else 1
    for tk, count in frequency.items():
        entry = universe.setdefault(tk, TickerEntry(ticker=tk))
        entry.frequency_count = count

    # Add extra_pool (e.g. priority_tickers.csv pool) without scores
    for tk in extra_pool:
        tk = tk.strip().upper()
        if tk and tk not in universe:
            universe[tk] = TickerEntry(ticker=tk)

    # Compute scores
    fav_size = max(len(favorites), 1)
    for entry in universe.values():
        pref_score = (fav_size - entry.preference_rank + 1) if entry.preference_rank else 0
        freq_score = (entry.frequency_count / max_count) * fav_size
        entry.score = 0.5 * pref_score + 0.5 * freq_score

    # Sort descending by score (then preference_rank, then ticker for stability)
    return sorted(
        universe.values(),
        key=lambda e: (-e.score, e.preference_rank or 999, e.ticker),
    )


# -----------------------------------------------------------------------
# Public API — used by the daily hot-rotation timer (paper_plan §16.4)
# -----------------------------------------------------------------------

async def resolve_hot_tickers(
    storage_account_name: str | None,
    top_k: int = 50,
    credential=None,
) -> list[str]:
    """Return the top-K hot tickers as a list, in priority order.

    If storage_account_name is None or logs are empty, falls back to the
    static favorites list (good for first-deploy / cold-start).
    """
    favorites = load_korean_favorites()
    frequency: dict[str, int] = {}
    if storage_account_name:
        try:
            frequency = await load_frequency_counts(storage_account_name, credential=credential)
        except Exception:
            logger.exception("frequency load failed; using favorites only")

    ranked = combine_scores(favorites, frequency)
    return [e.ticker for e in ranked[:top_k]]


# -----------------------------------------------------------------------
# §9 Weekly cache pool expansion — 22 → 50 → 100 → 200 over weeks
#
#   Pool size depends on the previous-7-day distinct user count:
#     <50 users   → 22  (default — cold start / soft launch)
#     50–199      → 50  (early traction)
#     200–999     → 100 (growth)
#     ≥1000       → 200 (scale)
#
#   Why not jump straight to 200 ?
#     - prewarm cost is ~3 × pool_size LLM calls per 4h cycle
#     - blob storage churn scales linearly
#     - we want pool size to match real demand, not theoretical max
# -----------------------------------------------------------------------

POOL_TIERS = [
    (1000, 200),
    (200,  100),
    (50,    50),
    (0,     22),
]


def determine_pool_size(weekly_distinct_users: int) -> int:
    """Map weekly user count → hot pool size. Step function, not interpolated."""
    for threshold, size in POOL_TIERS:
        if weekly_distinct_users >= threshold:
            return size
    return POOL_TIERS[-1][1]


async def count_weekly_distinct_users(
    storage_account_name: str,
    credential=None,
) -> int:
    """Count distinct anon_user_id values in logs over the last 7 days."""
    creds = credential or DefaultAzureCredential()
    seen: set[str] = set()
    now = datetime.now(timezone.utc)
    earliest = now - timedelta(days=7)

    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(LOGS_CONTAINER)
            async for blob in container.list_blobs():
                try:
                    parts = blob.name.split("/")
                    blob_dt = datetime(
                        int(parts[0]), int(parts[1]), int(parts[2]),
                        int(parts[3].split(".")[0]),
                        tzinfo=timezone.utc,
                    )
                    if blob_dt < earliest - timedelta(hours=1):
                        continue
                except (ValueError, IndexError):
                    continue
                try:
                    client = container.get_blob_client(blob.name)
                    stream = await client.download_blob()
                    body = await stream.readall()
                    for line in body.decode("utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            evt = json.loads(line)
                            anon = evt.get("anon")
                            if anon:
                                seen.add(anon)
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    continue
    except Exception as exc:
        logger.warning("count_weekly_distinct_users failed: %s", exc)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    return len(seen)


async def resolve_pool_size(
    storage_account_name: str | None,
    credential=None,
) -> tuple[int, int]:
    """Determine current hot-pool size based on weekly traffic.

    Returns (pool_size, weekly_distinct_users).
    """
    if not storage_account_name:
        return POOL_TIERS[-1][1], 0
    try:
        weekly = await count_weekly_distinct_users(storage_account_name, credential)
    except Exception:
        logger.exception("weekly user count failed; using default pool size")
        return POOL_TIERS[-1][1], 0
    return determine_pool_size(weekly), weekly
