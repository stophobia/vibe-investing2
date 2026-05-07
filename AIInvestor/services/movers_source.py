"""Top-mover source for matchup predictions.

For both stock and crypto pools we fetch the latest two daily closes via
yfinance, compute the % change, and rank. Results are cached in blob
storage per KST date so we batch-fetch at most once per day.

Stock pool: tickers from data/stock_elements.csv (the same universe we
use for Saju recommendations — ~296 names from S&P500 + NASDAQ top 300).
Crypto pool: top-30 by market cap (yfinance "<SYMBOL>-USD" tickers,
stablecoins excluded since they don't move).
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Universe
# ─────────────────────────────────────────────────────────────────────────────
_STOCK_CSV = Path(__file__).resolve().parent.parent / "data" / "stock_elements.csv"

# Top ~30 crypto by market cap (excluding stablecoins). yfinance tickers.
CRYPTO_UNIVERSE: tuple[str, ...] = (
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "DOGE-USD", "ADA-USD", "TRX-USD", "AVAX-USD", "SHIB-USD",
    "LINK-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "BCH-USD",
    "NEAR-USD", "ATOM-USD", "UNI-USD", "XLM-USD", "ETC-USD",
    "FIL-USD", "APT-USD", "ARB-USD", "OP-USD", "IMX-USD",
    "INJ-USD", "RNDR-USD", "TON-USD", "HBAR-USD", "ICP-USD",
)

# Display names for the well-known coins (for UI).
CRYPTO_NAMES: dict[str, str] = {
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "BNB-USD": "BNB",
    "SOL-USD": "Solana", "XRP-USD": "XRP", "DOGE-USD": "Dogecoin",
    "ADA-USD": "Cardano", "TRX-USD": "TRON", "AVAX-USD": "Avalanche",
    "SHIB-USD": "Shiba Inu", "LINK-USD": "Chainlink", "DOT-USD": "Polkadot",
    "MATIC-USD": "Polygon", "LTC-USD": "Litecoin", "BCH-USD": "Bitcoin Cash",
    "NEAR-USD": "NEAR", "ATOM-USD": "Cosmos", "UNI-USD": "Uniswap",
    "XLM-USD": "Stellar", "ETC-USD": "Ethereum Classic", "FIL-USD": "Filecoin",
    "APT-USD": "Aptos", "ARB-USD": "Arbitrum", "OP-USD": "Optimism",
    "IMX-USD": "Immutable", "INJ-USD": "Injective", "RNDR-USD": "Render",
    "TON-USD": "Toncoin", "HBAR-USD": "Hedera", "ICP-USD": "Internet Computer",
}

# In-process cache to avoid re-reading CSV
_stock_universe_cache: tuple[str, ...] | None = None
_stock_names_cache: dict[str, str] = {}


def _load_stock_universe() -> tuple[tuple[str, ...], dict[str, str]]:
    global _stock_universe_cache, _stock_names_cache
    if _stock_universe_cache is not None:
        return _stock_universe_cache, _stock_names_cache
    tickers: list[str] = []
    names: dict[str, str] = {}
    if not _STOCK_CSV.exists():
        logger.warning("stock_elements.csv missing — empty stock universe")
        _stock_universe_cache = tuple()
        return _stock_universe_cache, _stock_names_cache
    with _STOCK_CSV.open(encoding="utf-8") as f:
        cleaned = (ln for ln in f if ln.strip() and not ln.lstrip().startswith("#"))
        for row in csv.DictReader(cleaned):
            t = row["ticker"].strip().upper()
            if not t:
                continue
            tickers.append(t)
            names[t] = row.get("name", "").strip() or t
    _stock_universe_cache = tuple(tickers)
    _stock_names_cache = names
    logger.info("Loaded %d stock tickers for movers", len(tickers))
    return _stock_universe_cache, _stock_names_cache


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Mover:
    ticker: str
    name: str
    kind: str             # "stock" | "crypto"
    last_close: float     # most recent close
    pct_change: float     # vs prior close (e.g. 0.045 = +4.5%)


@dataclass
class MoversSnapshot:
    kst_date: str
    fetched_at: str       # ISO UTC
    stocks: list[Mover] = field(default_factory=list)
    cryptos: list[Mover] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Fetch (yfinance batch)
# ─────────────────────────────────────────────────────────────────────────────
def _kst_today_iso() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


def _fetch_pct_changes_sync(tickers: list[str]) -> list[tuple[str, float, float]]:
    """yfinance batch download. Returns list of (ticker, last_close, pct_change).
    Skipped if data unavailable.
    """
    import yfinance as yf
    if not tickers:
        return []
    out: list[tuple[str, float, float]] = []
    # yfinance batch — period 5d gives us at least 2 closes even on holidays
    try:
        df = yf.download(tickers, period="5d", interval="1d",
                         group_by="ticker", auto_adjust=False,
                         progress=False, threads=True)
    except Exception:
        logger.exception("yf.download failed for %d tickers", len(tickers))
        return []

    for t in tickers:
        try:
            # df can be either MultiIndex columns (multi-ticker) or flat (single)
            if len(tickers) == 1:
                closes = df["Close"].dropna()
            else:
                closes = df[t]["Close"].dropna()
            if len(closes) < 2:
                continue
            prev = float(closes.iloc[-2])
            last = float(closes.iloc[-1])
            if prev <= 0:
                continue
            pct = (last - prev) / prev
            out.append((t, last, pct))
        except (KeyError, IndexError, ValueError):
            continue
    return out


async def fetch_movers_snapshot() -> MoversSnapshot:
    """Fetch top movers for both pools. Heavy — call once per day."""
    stock_tickers, stock_names = _load_stock_universe()
    crypto_tickers = list(CRYPTO_UNIVERSE)

    # Run yfinance in thread pool (sync API)
    stock_results, crypto_results = await asyncio.gather(
        asyncio.to_thread(_fetch_pct_changes_sync, list(stock_tickers)),
        asyncio.to_thread(_fetch_pct_changes_sync, crypto_tickers),
    )

    stocks = [
        Mover(t, stock_names.get(t, t), "stock", last, pct)
        for (t, last, pct) in stock_results
    ]
    cryptos = [
        Mover(t, CRYPTO_NAMES.get(t, t), "crypto", last, pct)
        for (t, last, pct) in crypto_results
    ]
    # Sort by absolute pct_change desc — biggest movers (gainers + losers)
    stocks.sort(key=lambda m: abs(m.pct_change), reverse=True)
    cryptos.sort(key=lambda m: abs(m.pct_change), reverse=True)

    return MoversSnapshot(
        kst_date=_kst_today_iso(),
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        stocks=stocks,
        cryptos=cryptos,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Blob persistence
# ─────────────────────────────────────────────────────────────────────────────
CONTAINER = "matchup-movers"


def _blob_path(kst_date: str) -> str:
    return f"{kst_date}.json"


async def write_snapshot(account_name: str, snap: MoversSnapshot, credential=None) -> None:
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    creds = credential or DefaultAzureCredential()
    payload = {
        "kst_date": snap.kst_date,
        "fetched_at": snap.fetched_at,
        "stocks": [asdict(m) for m in snap.stocks],
        "cryptos": [asdict(m) for m in snap.cryptos],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
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
            await container.upload_blob(_blob_path(snap.kst_date), body,
                                         overwrite=True)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def read_snapshot(account_name: str, kst_date: str | None = None,
                        credential=None) -> MoversSnapshot | None:
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    if kst_date is None:
        kst_date = _kst_today_iso()
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            blob = svc.get_blob_client(CONTAINER, _blob_path(kst_date))
            try:
                download = await blob.download_blob()
                body = await download.readall()
            except ResourceNotFoundError:
                return None
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
    data = json.loads(body)
    return MoversSnapshot(
        kst_date=data["kst_date"],
        fetched_at=data["fetched_at"],
        stocks=[Mover(**m) for m in data["stocks"]],
        cryptos=[Mover(**m) for m in data["cryptos"]],
    )


async def get_or_fetch_movers(account_name: str, credential=None) -> MoversSnapshot:
    """Return today's snapshot from blob, or fetch fresh and persist."""
    cached = await read_snapshot(account_name, credential=credential)
    if cached is not None:
        return cached
    snap = await fetch_movers_snapshot()
    try:
        await write_snapshot(account_name, snap, credential=credential)
    except Exception:
        logger.exception("write_snapshot failed (non-fatal)")
    return snap
