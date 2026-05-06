"""3-tier ticker price cache for the public /api/data/{ticker} endpoint.

Tier 1: process-local dict       (~5ms)    cleared on instance restart
Tier 2: Blob 'ticker-cache/...'  (~50ms)   survives instance restart
Tier 3: yfinance live fetch      (~500ms)  always-fresh fallback

A separate Timer Trigger pre-warms HOT_TICKERS every 30 min so the
common cases never see Tier 3 latency.

This is a *lightweight* feed (price, %change, market cap, PE) — distinct
from prewarm/snapshots/ which holds the full 21-field fundamental
StockSnapshot used by the persona LLM. Different consumers, different
update cadence.

Spec: AIInvestor/ticker-data-caching-architecture-v1.0-ko.md (옵션 C)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any

import yfinance as yf
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logger = logging.getLogger(__name__)

CONTAINER = "ticker-cache"

# §1.2 적응형 TTL
DEFAULT_TTL_SECONDS = 1800   # 30분 — hot tickers
LONG_TTL_SECONDS = 14400     # 4시간 — long-tail tickers
WEEKEND_TTL_SECONDS = 86400  # 24시간 — markets closed

# §4.2 핫 티커 (Korean retail bias). yfinance symbol form.
HOT_TICKERS = (
    "NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AVGO",
    "QQQ", "SPY",
    "BTC-USD", "ETH-USD",
    "005930.KS",   # Samsung Electronics
    "000660.KS",   # SK Hynix
)
HOT_TICKER_SET = frozenset(HOT_TICKERS)


# ──────────────────────────────────────────────────────────
# Tier 1 — process-local cache
# ──────────────────────────────────────────────────────────
_MEMORY_CACHE: dict[str, dict] = {}     # ticker → {"ts": float, "data": dict}
_LOCKS: dict[str, asyncio.Lock] = {}    # per-ticker stampede guard


def _get_lock(ticker: str) -> asyncio.Lock:
    if ticker not in _LOCKS:
        _LOCKS[ticker] = asyncio.Lock()
    return _LOCKS[ticker]


def get_ttl_seconds(ticker: str) -> int:
    """Adaptive TTL — hot 티커는 30분, 그 외 4시간, 주말은 24시간."""
    now = datetime.now(timezone.utc)
    # Saturday=5, Sunday=6 (UTC). Markets globally idle.
    if now.weekday() >= 5:
        return WEEKEND_TTL_SECONDS
    if ticker.upper() in HOT_TICKER_SET:
        return DEFAULT_TTL_SECONDS
    return LONG_TTL_SECONDS


def is_market_closed_kst() -> bool:
    """True during KST 16:00–22:30 (KR closed, US not yet open)."""
    kst = datetime.now(timezone.utc) + timedelta(hours=9)
    return 16 <= kst.hour < 22 or (kst.hour == 22 and kst.minute < 30)


# ──────────────────────────────────────────────────────────
# Public API — used by HTTP trigger
# ──────────────────────────────────────────────────────────

async def get_or_fetch(
    ticker: str, storage_account_name: str, credential=None,
) -> tuple[dict, str]:
    """3-tier lookup. Returns (data_dict, source) where source is one of:
    'memory', 'blob', 'origin'.
    """
    ticker = ticker.upper().strip()
    ttl = get_ttl_seconds(ticker)
    now = time.time()

    # Tier 1
    cached = _MEMORY_CACHE.get(ticker)
    if cached and (now - cached["ts"]) < ttl:
        return cached["data"], "memory"

    async with _get_lock(ticker):
        # Double-check after lock
        cached = _MEMORY_CACHE.get(ticker)
        if cached and (time.time() - cached["ts"]) < ttl:
            return cached["data"], "memory"

        # Tier 2 — Blob
        creds = credential or DefaultAzureCredential()
        try:
            blob_entry = await _read_blob(storage_account_name, ticker, creds)
            if blob_entry and (time.time() - blob_entry["ts"]) < ttl:
                _MEMORY_CACHE[ticker] = blob_entry
                return blob_entry["data"], "blob"

            # Tier 3 — origin (yfinance)
            data = await asyncio.to_thread(_fetch_from_yfinance, ticker, ttl)
            entry = {"ts": time.time(), "data": data}
            _MEMORY_CACHE[ticker] = entry
            await _write_blob(storage_account_name, ticker, entry, creds)
            return data, "origin"
        finally:
            if hasattr(creds, "close") and credential is None:
                await creds.close()


# ──────────────────────────────────────────────────────────
# Public API — used by Timer trigger
# ──────────────────────────────────────────────────────────

async def refresh_hot_tickers(
    storage_account_name: str, credential=None,
) -> dict[str, str]:
    """Refresh HOT_TICKERS in parallel. Returns {ticker: 'ok'|error_msg}.
    Skips during weekend or market-closed window (§1.2)."""
    if datetime.now(timezone.utc).weekday() >= 5:
        logger.info("weekend — skipping hot ticker refresh")
        return {}
    if is_market_closed_kst():
        logger.info("KST 16:00–22:30 closed window — skipping hot refresh")
        return {}

    creds = credential or DefaultAzureCredential()
    results: dict[str, str] = {}
    sem = asyncio.Semaphore(4)

    async def _refresh_one(ticker: str) -> None:
        async with sem:
            try:
                ttl = get_ttl_seconds(ticker)
                data = await asyncio.to_thread(_fetch_from_yfinance, ticker, ttl)
                entry = {"ts": time.time(), "data": data}
                _MEMORY_CACHE[ticker] = entry
                await _write_blob(storage_account_name, ticker, entry, creds)
                results[ticker] = "ok"
            except Exception as exc:
                logger.exception("refresh_hot_tickers failed %s", ticker)
                results[ticker] = f"err:{type(exc).__name__}"

    try:
        await asyncio.gather(*[_refresh_one(t) for t in HOT_TICKERS])
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
    return results


# ──────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────

async def _read_blob(account_name: str, ticker: str, creds) -> dict | None:
    async with BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=creds,
    ) as svc:
        client = svc.get_blob_client(CONTAINER, f"{ticker}.json")
        try:
            stream = await client.download_blob()
            body = await stream.readall()
            return json.loads(body)
        except ResourceNotFoundError:
            return None
        except Exception as exc:
            logger.warning("blob read failed for %s: %s", ticker, exc)
            return None


async def _write_blob(account_name: str, ticker: str, entry: dict, creds) -> None:
    async with BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=creds,
    ) as svc:
        client = svc.get_blob_client(CONTAINER, f"{ticker}.json")
        try:
            ttl = entry["data"].get("ttl_seconds", DEFAULT_TTL_SECONDS)
            await client.upload_blob(
                json.dumps(entry, ensure_ascii=False).encode("utf-8"),
                overwrite=True,
                content_type="application/json",
                # Browser/CDN cache up to TTL
                # (matches the fetched_at timestamp inside)
            )
        except Exception as exc:
            logger.warning("blob write failed for %s: %s", ticker, exc)


def _fetch_from_yfinance(ticker: str, ttl: int) -> dict:
    """Lightweight price feed — no .history() roundtrip, .info only."""
    t = yf.Ticker(ticker)
    try:
        info = t.info or {}
    except Exception:
        info = {}

    fast = {}
    try:
        fast = t.fast_info or {}
    except Exception:
        pass

    fetched_at_dt = datetime.now(timezone.utc)
    next_refresh = fetched_at_dt + timedelta(seconds=ttl)

    price = (
        _maybe_float(info.get("currentPrice"))
        or _maybe_float(info.get("regularMarketPrice"))
        or _maybe_float(getattr(fast, "last_price", None))
        or _maybe_float(info.get("previousClose"))
    )

    prev_close = (
        _maybe_float(info.get("previousClose"))
        or _maybe_float(getattr(fast, "previous_close", None))
    )

    change_24h_pct = None
    if price and prev_close:
        change_24h_pct = round((price - prev_close) / prev_close * 100, 2)

    return {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "price": price,
        "currency": info.get("currency", "USD"),
        "change_percent_24h": change_24h_pct,
        "market_cap": _maybe_float(info.get("marketCap")),
        "pe_ratio": _maybe_float(info.get("trailingPE")),
        "fetched_at": fetched_at_dt.isoformat(timespec="seconds"),
        "next_refresh_at": next_refresh.isoformat(timespec="seconds"),
        "ttl_seconds": ttl,
        "ttl_minutes": ttl // 60,
        "source": "yfinance",
    }


def _maybe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        if f != f:  # NaN
            return None
        return f
    except (TypeError, ValueError):
        return None
