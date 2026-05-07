"""Minimal HTTP clients for TON + TRON to fetch incoming USDT transfers.

Both classes expose `recent_incoming_usdt(wallet) -> list[IncomingTx]` for
the donation verification cron. Free public endpoints are used by default
(no API key required) — they are rate-limited but the cron only fires
every 5 min so we stay under the limit.

Override `endpoint` / `api_key` if you have a paid plan.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import aiohttp

from .donation_service import IncomingTx

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TON — TonAPI v2 (https://tonapi.io/docs)
# ─────────────────────────────────────────────────────────────────────────────
TON_USDT_JETTON = "0:b113a994b5024a16719f69139328eb759596c38a25f59028b146fecdc3621dfe"  # USD₮ master


class TonClient:
    """Wraps TonAPI /accounts/<addr>/jettons/history for USDT transfers."""

    def __init__(self, endpoint: str = "https://tonapi.io/v2",
                 api_key: str | None = None,
                 timeout_s: float = 10.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout_s)

    def _headers(self) -> dict:
        h = {"Accept": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    async def recent_incoming_usdt(self, wallet: str,
                                   limit: int = 25) -> list[IncomingTx]:
        """Fetch recent USDT (Jetton) transfers received by `wallet`."""
        url = f"{self._endpoint}/accounts/{wallet}/jettons/{TON_USDT_JETTON}/history"
        params = {"limit": limit}
        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as sess:
                async with sess.get(url, params=params, headers=self._headers()) as r:
                    if r.status != 200:
                        logger.warning("TonAPI HTTP %d for %s", r.status, wallet)
                        return []
                    data = await r.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("TonAPI request failed: %s", exc)
            return []
        return _parse_ton_jetton_events(data, wallet)


def _parse_ton_jetton_events(data: dict, wallet: str) -> list[IncomingTx]:
    """Parse TonAPI jettons/history response into IncomingTx list.

    The response shape (TonAPI v2): {"events": [{
       "event_id": "...",
       "timestamp": 1715050800,
       "actions": [{"type":"JettonTransfer", "JettonTransfer":{
            "sender":{"address":"..."},"recipient":{"address":"..."},
            "amount":"1000000","comment":"vinv-XXXX"
       }}]
    }]}
    """
    out: list[IncomingTx] = []
    target = wallet.lower()
    for ev in data.get("events", []):
        ts = ev.get("timestamp", 0)
        for action in ev.get("actions", []):
            if action.get("type") != "JettonTransfer":
                continue
            jt = action.get("JettonTransfer", {})
            recipient = (jt.get("recipient") or {}).get("address", "").lower()
            if recipient and target not in recipient and recipient not in target:
                continue
            raw_amount = jt.get("amount", "0")
            try:
                # USDT TON jetton has 6 decimals
                amount = int(raw_amount) / 1_000_000
            except (TypeError, ValueError):
                continue
            comment = jt.get("comment") or ""
            tx_hash = ev.get("event_id", "")
            seen = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds") if ts else ""
            out.append(IncomingTx(
                tx_hash=tx_hash, amount_usdt=amount,
                memo=comment, chain="ton", seen_at=seen,
            ))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# TRON — TronGrid (https://developers.tron.network/reference/get-trc20-transactions)
# ─────────────────────────────────────────────────────────────────────────────
TRON_USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


class TronClient:
    """Wraps TronGrid /v1/accounts/<addr>/transactions/trc20 for USDT-TRC20."""

    def __init__(self, endpoint: str = "https://api.trongrid.io",
                 api_key: str | None = None,
                 timeout_s: float = 10.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout_s)

    def _headers(self) -> dict:
        h = {"Accept": "application/json"}
        if self._api_key:
            h["TRON-PRO-API-KEY"] = self._api_key
        return h

    async def recent_incoming_usdt(self, wallet: str,
                                   limit: int = 50) -> list[IncomingTx]:
        url = f"{self._endpoint}/v1/accounts/{wallet}/transactions/trc20"
        params = {
            "limit": limit,
            "only_to": "true",
            "contract_address": TRON_USDT_CONTRACT,
        }
        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as sess:
                async with sess.get(url, params=params, headers=self._headers()) as r:
                    if r.status != 200:
                        logger.warning("TronGrid HTTP %d for %s", r.status, wallet)
                        return []
                    data = await r.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("TronGrid request failed: %s", exc)
            return []
        return _parse_tron_trc20(data, wallet)


def _parse_tron_trc20(data: dict, wallet: str) -> list[IncomingTx]:
    """Parse TronGrid /v1/accounts/<addr>/transactions/trc20 response.

    Shape: {"data":[{"transaction_id":"...","value":"50000731","to":"...",
                     "block_timestamp":1715050800000}]}
    """
    out: list[IncomingTx] = []
    target = wallet.lower()
    for tx in data.get("data", []):
        to_addr = (tx.get("to") or "").lower()
        if to_addr and to_addr != target:
            continue
        raw = tx.get("value", "0")
        try:
            # USDT TRC20 has 6 decimals
            amount = int(raw) / 1_000_000
        except (TypeError, ValueError):
            continue
        ts_ms = tx.get("block_timestamp", 0)
        seen = (datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
                .isoformat(timespec="seconds")) if ts_ms else ""
        out.append(IncomingTx(
            tx_hash=tx.get("transaction_id", ""),
            amount_usdt=amount,
            memo="",
            chain="tron",
            seen_at=seen,
        ))
    return out
