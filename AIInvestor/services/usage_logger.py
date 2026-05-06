"""§17.3 usage logger — appends one NDJSON event per webhook handled.

Layout:
  logs/yyyy/mm/dd/HH.ndjson    (one append-blob per UTC hour)

Each event line:
  {"ts":"...","anon":"82ec62f2","lang":"ko","persona":"buffett",
   "ticker":"NVDA","tier":"commentary_hit",
   "duration_ms":1247,"llm_in":0,"llm_out":0}

`tier` enum:
  commentary_hit  — Tier 1 prewarm cache hit, zero LLM
  snapshot_hit    — Tier 2 snapshot cache hit, LLM called
  live            — full live path (yfinance + LLM)
  deep            — user pressed "deeper analysis"
  intent_unrecognized — natural-language fallback
  ticker_not_found    — unrecognized symbol
  sector_compare      — sector follow-up shown
  feedback            — /feedback command

Failures are logged at WARNING but never raised; telemetry must never
break the user-facing path.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

logger = logging.getLogger(__name__)

CONTAINER = "logs"


def _path_for_now() -> str:
    n = datetime.now(timezone.utc)
    return f"{n.year:04d}/{n.month:02d}/{n.day:02d}/{n.hour:02d}.ndjson"


class UsageLogger:
    """In-instance buffered NDJSON appender. Flushes every 60s OR 50 events."""

    FLUSH_SECONDS = 60
    FLUSH_EVENTS = 50

    def __init__(self, storage_account_name: str, credential=None) -> None:
        self._account_url = f"https://{storage_account_name}.blob.core.windows.net"
        self._credential = credential or DefaultAzureCredential()
        self._service: Optional[BlobServiceClient] = None
        self._buffer: list[str] = []
        self._lock = asyncio.Lock()
        self._last_flush = time.monotonic()

    async def _client(self) -> BlobServiceClient:
        if self._service is None:
            self._service = BlobServiceClient(account_url=self._account_url, credential=self._credential)
        return self._service

    async def aclose(self) -> None:
        # Flush any remaining buffered events before tearing down
        try:
            await self.flush(force=True)
        finally:
            if self._service is not None:
                await self._service.close()
            if hasattr(self._credential, "close"):
                await self._credential.close()

    async def record(
        self,
        anon: str,
        lang: str,
        persona: str,
        ticker: str,
        tier: str,
        duration_ms: int,
        llm_in: int = 0,
        llm_out: int = 0,
    ) -> None:
        evt = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "anon": anon[:8] if anon else "",  # double-truncate for log-side k-anonymity
            "lang": lang,
            "persona": persona,
            "ticker": ticker,
            "tier": tier,
            "duration_ms": duration_ms,
            "llm_in": llm_in,
            "llm_out": llm_out,
        }
        async with self._lock:
            self._buffer.append(json.dumps(evt, ensure_ascii=False))
            should_flush = (
                len(self._buffer) >= self.FLUSH_EVENTS
                or (time.monotonic() - self._last_flush) >= self.FLUSH_SECONDS
            )
        if should_flush:
            await self.flush()

    async def flush(self, force: bool = False) -> None:
        async with self._lock:
            if not self._buffer:
                return
            payload = "\n".join(self._buffer) + "\n"
            self._buffer.clear()
            self._last_flush = time.monotonic()

        try:
            client = await self._client()
            path = _path_for_now()
            blob = client.get_blob_client(CONTAINER, path)
            # Append blob: create if missing then append a chunk
            try:
                await blob.create_append_blob()
            except ResourceExistsError:
                pass
            await blob.append_block(payload.encode("utf-8"))
        except Exception:
            logger.exception("usage_logger flush failed (events lost: %d)", len(payload.split('\n')))
