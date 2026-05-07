"""Azure Cost Management — fetch month-to-date spend for the dashboard.

Free tier covers most of our usage but a few items leak (Storage operations
above free quota, Application Insights ingestion, outbound bandwidth, etc.).
We surface those on the admin dashboard so cost surprises are visible early.

Auth: DefaultAzureCredential (managed identity in production, az login locally).
The identity needs the `Cost Management Reader` role on the subscription.

Endpoint: https://management.azure.com/subscriptions/{sub_id}/providers/
          Microsoft.CostManagement/query?api-version=2023-11-01

Result is cached in-process for 30 min so the dashboard refresh doesn't
hammer ARM (which has its own rate limits).
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 1800  # 30 min
ARM_SCOPE = "https://management.azure.com/.default"
COST_QUERY_API_VERSION = "2023-11-01"


@dataclass
class BillingSnapshot:
    subscription_id: str
    currency: str
    month_to_date_total: float
    by_service: dict[str, float] = field(default_factory=dict)  # serviceName → cost
    by_resource_group: dict[str, float] = field(default_factory=dict)
    fetched_at: str = ""
    error: str = ""


_cache: tuple[float, BillingSnapshot] | None = None


def _get_subscription_id() -> str:
    return (os.getenv("AZURE_SUBSCRIPTION_ID")
            or os.getenv("SUBSCRIPTION_ID") or "").strip()


async def _fetch_token() -> str:
    """Acquire ARM access token via DefaultAzureCredential."""
    from azure.identity.aio import DefaultAzureCredential
    creds = DefaultAzureCredential()
    try:
        token = await creds.get_token(ARM_SCOPE)
        return token.token
    finally:
        await creds.close()


async def _query(sub_id: str, body: dict) -> dict:
    """POST a Cost Management query and return the parsed response."""
    import aiohttp
    url = (f"https://management.azure.com/subscriptions/{sub_id}"
           f"/providers/Microsoft.CostManagement/query"
           f"?api-version={COST_QUERY_API_VERSION}")
    token = await _fetch_token()
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json"}
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as sess:
        async with sess.post(url, json=body, headers=headers) as r:
            text = await r.text()
            if r.status != 200:
                logger.warning("Cost Management HTTP %d: %s", r.status, text[:200])
                return {}
            import json as _json
            return _json.loads(text)


def _build_query(grouping_dim: str) -> dict:
    """Cost Management query body — month-to-date, grouped by one dimension."""
    return {
        "type": "Usage",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {
                "totalCost": {"name": "Cost", "function": "Sum"},
            },
            "grouping": [{"type": "Dimension", "name": grouping_dim}],
        },
    }


def _parse_result(data: dict) -> tuple[float, dict[str, float], str]:
    """Parse {properties:{rows:[[cost, dimension, currency], ...]}} → totals.
    Cost Management returns rows in column order matching `properties.columns`."""
    props = data.get("properties", {})
    cols = [c.get("name", "") for c in props.get("columns", [])]
    rows = props.get("rows", [])
    if not cols or not rows:
        return 0.0, {}, "USD"

    # Find indices for Cost / dimension / Currency
    try:
        i_cost = next(i for i, c in enumerate(cols) if c.lower() == "cost")
    except StopIteration:
        return 0.0, {}, "USD"
    try:
        i_curr = next(i for i, c in enumerate(cols) if c.lower() == "currency")
    except StopIteration:
        i_curr = -1
    # Dimension column = whichever isn't Cost or Currency
    dim_indices = [i for i, c in enumerate(cols)
                   if c.lower() not in ("cost", "currency")]
    i_dim = dim_indices[0] if dim_indices else -1

    by_dim: dict[str, float] = {}
    total = 0.0
    currency = "USD"
    for row in rows:
        try:
            cost = float(row[i_cost])
        except (TypeError, ValueError, IndexError):
            continue
        total += cost
        if i_dim >= 0 and i_dim < len(row):
            key = str(row[i_dim] or "(none)")
            by_dim[key] = by_dim.get(key, 0.0) + cost
        if i_curr >= 0 and i_curr < len(row):
            currency = str(row[i_curr] or currency)
    return total, by_dim, currency


async def fetch_billing_snapshot(force: bool = False) -> BillingSnapshot:
    """Return current month-to-date Azure spend, cached 30 min in-process."""
    global _cache
    now = time.monotonic()
    if not force and _cache is not None and (now - _cache[0]) < CACHE_TTL_SECONDS:
        return _cache[1]

    sub_id = _get_subscription_id()
    if not sub_id:
        snap = BillingSnapshot(subscription_id="", currency="USD",
                               month_to_date_total=0.0,
                               error="AZURE_SUBSCRIPTION_ID not set")
        return snap

    try:
        # Two queries in parallel: by service + by resource group
        import asyncio
        svc_data, rg_data = await asyncio.gather(
            _query(sub_id, _build_query("ServiceName")),
            _query(sub_id, _build_query("ResourceGroup")),
            return_exceptions=True,
        )
    except Exception as exc:
        logger.exception("billing query failed")
        return BillingSnapshot(subscription_id=sub_id, currency="USD",
                               month_to_date_total=0.0, error=str(exc))

    if isinstance(svc_data, Exception):
        return BillingSnapshot(subscription_id=sub_id, currency="USD",
                               month_to_date_total=0.0,
                               error=f"svc query: {svc_data}")
    total, by_service, currency = _parse_result(svc_data or {})
    by_rg: dict[str, float] = {}
    if not isinstance(rg_data, Exception):
        _t, by_rg, _c = _parse_result(rg_data or {})

    snap = BillingSnapshot(
        subscription_id=sub_id,
        currency=currency,
        month_to_date_total=round(total, 4),
        by_service={k: round(v, 4) for k, v in by_service.items()},
        by_resource_group={k: round(v, 4) for k, v in by_rg.items()},
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    _cache = (now, snap)
    return snap
