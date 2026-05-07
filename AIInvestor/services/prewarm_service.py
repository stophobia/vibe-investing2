"""Pre-warming daemon — populates Blob cache for popular tickers.

Schedule (function_app.py timer triggers):
    snapshots:    every 4 hours    (yfinance batch download for ~250 tickers)
    commentaries: every 4 hours    (DeepSeek for TOP_50 × 3 personas × 4 langs = 600 blobs)

Layout (in storage account, container 'prewarm'):
    prewarm/snapshots/<TICKER>.json
    prewarm/commentary/<TICKER>.<persona>.<lang>.json

Read path (handler):
    1. Try commentary blob → if hit, send rendered_text directly. No LLM call.
    2. Try snapshot blob → if hit, skip yfinance, still call LLM.
    3. Fallback: existing live yfinance + DeepSeek path.
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from .i18n import t as i18n
from .market_report import _ndx100_moves  # not strictly needed but keep helper consistent
from .persona_engine import PersonaEngine, list_personas
from .stock_service import StockService, StockSnapshot, StockServiceError

logger = logging.getLogger(__name__)

PREWARM_CONTAINER = "prewarm"

PRIORITY_CSV = Path(__file__).resolve().parent.parent / "data" / "priority_tickers.csv"

LANGUAGES = ("ko", "en", "ja", "zh")


def load_priority_tickers() -> tuple[list[str], list[str]]:
    """Returns (priority_pool ~250 tickers, top_50 hot tickers)."""
    if not PRIORITY_CSV.exists():
        logger.warning("priority_tickers.csv missing at %s", PRIORITY_CSV)
        return [], []

    pool: list[str] = []
    top50: list[str] = []
    with PRIORITY_CSV.open() as f:
        reader = csv.DictReader(line for line in f if line.strip() and not line.lstrip().startswith("#"))
        for row in reader:
            ticker = (row.get("ticker") or "").strip().upper()
            tier = (row.get("tier") or "").strip().lower()
            if not ticker:
                continue
            pool.append(ticker)
            if tier == "top50":
                top50.append(ticker)
    logger.info("priority pool=%d, top50=%d", len(pool), len(top50))
    return pool, top50


# Prewarm DeepSeek API calls are logged to the usage NDJSON with this tier
# value so the dashboard can report them as a separate "cache feed" cost
# (distinct from user-driven LLM calls).
PREWARM_TIER = "prewarm_llm"


class PrewarmService:
    """Builds and uploads pre-warmed Blob cache. Called by Timer triggers."""

    def __init__(
        self,
        storage_account_name: str,
        persona_engine: PersonaEngine,
        stock_service: StockService,
        credential=None,
        usage_logger=None,
    ) -> None:
        self._account_url = f"https://{storage_account_name}.blob.core.windows.net"
        self._engine = persona_engine
        self._stock = stock_service
        self._credential = credential or DefaultAzureCredential()
        self._service: BlobServiceClient | None = None
        # Optional — when supplied, every successful prewarm LLM call is
        # logged to usage NDJSON with tier=prewarm_llm so the V2 dashboard
        # can show prewarm cost separately from user-driven LLM calls.
        self._usage_logger = usage_logger

    async def _client(self) -> BlobServiceClient:
        if self._service is None:
            self._service = BlobServiceClient(account_url=self._account_url, credential=self._credential)
        return self._service

    async def aclose(self) -> None:
        if self._service is not None:
            await self._service.close()
        if hasattr(self._credential, "close"):
            await self._credential.close()

    # ------------------------------------------------------------
    # Snapshots (every 4h)
    # ------------------------------------------------------------

    async def refresh_snapshots(self, tickers: Iterable[str]) -> dict[str, StockSnapshot]:
        """Fetch fundamental+price snapshot for each ticker, upload to Blob.

        Sequential fetches (yfinance batch is unreliable for `.info`).
        Returns dict of successfully-fetched snapshots for downstream commentary.
        """
        results: dict[str, StockSnapshot] = {}
        succeeded = 0
        failed = 0
        client = await self._client()
        start = time.monotonic()

        for ticker in tickers:
            try:
                snapshot = await asyncio.to_thread(self._stock.get_snapshot, ticker)
            except StockServiceError as exc:
                logger.warning("prewarm snapshot skip %s: %s", ticker, exc)
                failed += 1
                continue
            except Exception:
                logger.exception("prewarm snapshot error %s", ticker)
                failed += 1
                continue

            results[ticker] = snapshot
            try:
                blob = client.get_blob_client(PREWARM_CONTAINER, f"snapshots/{ticker}.json")
                await blob.upload_blob(
                    json.dumps(asdict(snapshot), ensure_ascii=False).encode("utf-8"),
                    overwrite=True,
                    content_type="application/json",
                )
                succeeded += 1
            except Exception:
                logger.exception("prewarm snapshot upload failed %s", ticker)
                failed += 1

        elapsed = time.monotonic() - start
        logger.info(
            "refresh_snapshots done — succeeded=%d failed=%d elapsed=%.1fs",
            succeeded, failed, elapsed,
        )
        return results

    # ------------------------------------------------------------
    # Commentaries (every 4h, 30 min after snapshots)
    # ------------------------------------------------------------

    async def refresh_commentaries(
        self,
        snapshots: dict[str, StockSnapshot],
        top_tickers: Iterable[str],
    ) -> int:
        """For each (ticker, persona, language), generate commentary and upload."""
        client = await self._client()
        succeeded = 0
        start = time.monotonic()

        # Fan out (ticker × persona × lang) calls but cap concurrency.
        sem = asyncio.Semaphore(4)
        tasks = []

        async def _build_one(ticker: str, persona, lang: str) -> bool:
            snapshot = snapshots.get(ticker)
            if snapshot is None:
                return False
            async with sem:
                t0 = time.monotonic()
                try:
                    rendered = await self._engine.generate(
                        persona=persona, snapshot=snapshot, language=lang, interests=None,
                    )
                except Exception:
                    logger.exception("prewarm commentary LLM failed %s/%s/%s",
                                     ticker, persona.key, lang)
                    return False
                # Track this prewarm DeepSeek API call so the dashboard can
                # report cache-feed cost. We approximate token counts since
                # the OpenAI client doesn't expose them on success here —
                # rendered length is a reasonable proxy.
                if self._usage_logger is not None:
                    try:
                        # Rough token estimate: 1 token ≈ 4 chars (conservative)
                        approx_out = max(1, len(rendered) // 4)
                        approx_in  = 800   # snapshot block + persona + instruction
                        await self._usage_logger.record(
                            anon="system_prewarm", lang=lang,
                            persona=persona.key, ticker=ticker,
                            tier=PREWARM_TIER,
                            duration_ms=int((time.monotonic() - t0) * 1000),
                            llm_in=approx_in, llm_out=approx_out,
                        )
                    except Exception:
                        logger.debug("prewarm usage logging failed (non-fatal)", exc_info=True)
                try:
                    payload = {
                        "ticker": ticker,
                        "persona_key": persona.key,
                        "persona_name": persona.name(lang),
                        "language": lang,
                        "rendered_text": f"[{persona.name(lang)} · {ticker}]\n\n{rendered}",
                        "generated_at": int(time.time()),
                    }
                    blob = client.get_blob_client(
                        PREWARM_CONTAINER,
                        f"commentary/{ticker}.{persona.key}.{lang}.json",
                    )
                    await blob.upload_blob(
                        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        overwrite=True,
                        content_type="application/json",
                    )
                    return True
                except Exception:
                    logger.exception("prewarm commentary upload failed %s/%s/%s",
                                     ticker, persona.key, lang)
                    return False

        for ticker in top_tickers:
            for persona in list_personas():
                for lang in LANGUAGES:
                    tasks.append(_build_one(ticker, persona, lang))

        outcomes = await asyncio.gather(*tasks, return_exceptions=False)
        succeeded = sum(1 for ok in outcomes if ok)
        elapsed = time.monotonic() - start
        logger.info(
            "refresh_commentaries done — succeeded=%d/%d elapsed=%.1fs",
            succeeded, len(outcomes), elapsed,
        )
        return succeeded


# ------------------------------------------------------------
# Read path — used by handlers
# ------------------------------------------------------------

async def cache_commentary(
    storage_account_name: str,
    ticker: str,
    persona_key: str,
    language: str,
    rendered_text: str,
    credential=None,
) -> None:
    """Write a commentary blob so a subsequent fetch_cached_commentary hits.
    Used when an on-demand /persona/analyze call generates fresh content —
    feeds the cache so repeated requests for the same (ticker, persona, lang)
    skip the DeepSeek roundtrip until the prewarm timer rotates the entry."""
    creds = credential or DefaultAzureCredential()
    payload = {
        "ticker": ticker,
        "persona_key": persona_key,
        "language": language,
        "rendered_text": rendered_text,
        "generated_at": int(time.time()),
    }
    path = f"commentary/{ticker}.{persona_key}.{language}.json"
    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            client = svc.get_blob_client(PREWARM_CONTAINER, path)
            await client.upload_blob(
                json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                overwrite=True, content_type="application/json",
            )
    except Exception:
        logger.exception("cache_commentary write failed %s", path)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def fetch_cached_commentary(
    storage_account_name: str,
    ticker: str,
    persona_key: str,
    language: str,
    credential=None,
) -> str | None:
    """Return rendered_text from prewarm/commentary blob, or None on miss."""
    creds = credential or DefaultAzureCredential()
    path = f"commentary/{ticker}.{persona_key}.{language}.json"
    async with BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=creds,
    ) as svc:
        client = svc.get_blob_client(PREWARM_CONTAINER, path)
        try:
            data = await client.download_blob()
            body = await data.readall()
            return json.loads(body).get("rendered_text")
        except ResourceNotFoundError:
            return None
        except Exception as exc:
            logger.debug("prewarm commentary fetch err path=%s err=%s", path, exc)
            return None


async def fetch_cached_snapshot(
    storage_account_name: str,
    ticker: str,
    credential=None,
) -> StockSnapshot | None:
    """Return StockSnapshot from prewarm/snapshots blob, or None on miss."""
    creds = credential or DefaultAzureCredential()
    path = f"snapshots/{ticker}.json"
    async with BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=creds,
    ) as svc:
        client = svc.get_blob_client(PREWARM_CONTAINER, path)
        try:
            data = await client.download_blob()
            body = await data.readall()
            return StockSnapshot(**json.loads(body))
        except ResourceNotFoundError:
            return None
        except Exception as exc:
            logger.debug("prewarm snapshot fetch err path=%s err=%s", path, exc)
            return None
