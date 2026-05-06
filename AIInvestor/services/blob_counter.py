"""§T2E-M — Blob-based atomic counter primitives.

Two strategies depending on accuracy vs. throughput trade-off:

  increment_daily_counter()      Lease-based, strict accuracy. Use when the
                                 caller will reject on overflow (rate limits,
                                 quota gates, point deduction).

  increment_daily_counter_etag() ETag-based optimistic. Slightly cheaper
                                 under contention but a small fraction of
                                 increments may be lost. Use for soft
                                 metrics (notification throttle, share
                                 counts).

Both produce the same blob layout:
    counters/<counter_name>/<KST_date>.json   →  {"count": N, "created":..., "updated":...}

The KST date keying makes lifecycle cleanup trivial — any blob older than
2 days under counters/ can be deleted by Blob Lifecycle Management policy.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
)
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobLeaseClient, BlobServiceClient

logger = logging.getLogger(__name__)

CONTAINER = "counters"
LEASE_DURATION_S = 15
LEASE_RETRY_MAX = 5
LEASE_RETRY_DELAY = 0.3


def _kst_today() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


def _service_client(account_name: str | None = None, credential=None) -> BlobServiceClient:
    account = account_name or os.getenv("STORAGE_ACCOUNT_NAME", "").strip()
    if not account:
        raise RuntimeError("STORAGE_ACCOUNT_NAME not set")
    return BlobServiceClient(
        account_url=f"https://{account}.blob.core.windows.net",
        credential=credential or DefaultAzureCredential(),
    )


async def _ensure_counter_blob(blob_client) -> None:
    """Initialize a 0-count blob if it doesn't exist. Idempotent under races
    — concurrent creators see ResourceExistsError and just continue."""
    try:
        await blob_client.get_blob_properties()
    except ResourceNotFoundError:
        try:
            await blob_client.upload_blob(
                json.dumps({
                    "count": 0,
                    "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }).encode(),
                overwrite=False,
            )
        except ResourceExistsError:
            pass


async def increment_daily_counter(
    counter_name: str,
    account_name: str | None = None,
    credential=None,
) -> int:
    """Strict atomic increment via Blob Lease. Returns the new count.

    Used when the caller will gate on the value (e.g. "deny if > 10").
    Slower than ETag under contention because each lease holds a lock for
    the read+write cycle, but never loses an increment.

    Raises RuntimeError if lease cannot be acquired within LEASE_RETRY_MAX
    attempts — caller should treat that as an infrastructure error.
    """
    date = _kst_today()
    blob_path = f"{counter_name}/{date}.json"

    creds = credential or DefaultAzureCredential()
    try:
        async with _service_client(account_name, creds) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            blob_client = svc.get_blob_client(CONTAINER, blob_path)
            await _ensure_counter_blob(blob_client)

            lease = BlobLeaseClient(client=blob_client)
            acquired = False
            for attempt in range(LEASE_RETRY_MAX):
                try:
                    await lease.acquire(lease_duration=LEASE_DURATION_S)
                    acquired = True
                    break
                except (ResourceExistsError, Exception) as exc:  # 412 lease conflict
                    if "lease" not in str(exc).lower() and not isinstance(exc, ResourceExistsError):
                        raise
                    await asyncio.sleep(LEASE_RETRY_DELAY * (attempt + 1))
            if not acquired:
                raise RuntimeError(f"counter lease timeout: {counter_name}")

            try:
                stream = await blob_client.download_blob()
                data = json.loads(await stream.readall())
                new_count = int(data.get("count", 0)) + 1
                data["count"] = new_count
                data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                await blob_client.upload_blob(
                    json.dumps(data, ensure_ascii=False).encode(),
                    overwrite=True,
                    lease=lease.id,
                )
                return new_count
            finally:
                try:
                    await lease.release()
                except Exception:
                    pass
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def increment_daily_counter_etag(
    counter_name: str,
    max_retries: int = 3,
    account_name: str | None = None,
    credential=None,
) -> int:
    """Optimistic ETag-based increment. Lighter than lease but a fraction of
    increments may be lost under heavy contention. Use only for soft
    metrics.

    On extreme contention (>3 concurrent retries), the last write wins —
    so the 'count' is best-effort, not exact. For exact counts use
    increment_daily_counter().
    """
    date = _kst_today()
    blob_path = f"{counter_name}/{date}.json"

    creds = credential or DefaultAzureCredential()
    try:
        async with _service_client(account_name, creds) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            blob_client = svc.get_blob_client(CONTAINER, blob_path)

            for attempt in range(max_retries):
                try:
                    try:
                        prop = await blob_client.get_blob_properties()
                        etag = prop.etag
                        stream = await blob_client.download_blob()
                        data = json.loads(await stream.readall())
                        new_count = int(data.get("count", 0)) + 1
                    except ResourceNotFoundError:
                        # Race: someone else may also be initializing.
                        try:
                            await blob_client.upload_blob(
                                json.dumps({
                                    "count": 1,
                                    "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                }).encode(),
                                overwrite=False,
                            )
                            return 1
                        except ResourceExistsError:
                            continue  # retry: read again

                    data["count"] = new_count
                    data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    await blob_client.upload_blob(
                        json.dumps(data, ensure_ascii=False).encode(),
                        overwrite=True,
                        etag=etag,
                        match_condition=MatchConditions.IfNotModified,
                    )
                    return new_count
                except ResourceModifiedError:
                    if attempt == max_retries - 1:
                        # Give up — return current value (lossy)
                        try:
                            stream = await blob_client.download_blob()
                            data = json.loads(await stream.readall())
                            return int(data.get("count", 0))
                        except Exception:
                            return 0
                    await asyncio.sleep(0.3 * (attempt + 1))
        return 0
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


async def get_daily_counter(
    counter_name: str,
    account_name: str | None = None,
    credential=None,
) -> int:
    """Read current count without incrementing. 0 if not yet written."""
    date = _kst_today()
    blob_path = f"{counter_name}/{date}.json"
    creds = credential or DefaultAzureCredential()
    try:
        async with _service_client(account_name, creds) as svc:
            blob_client = svc.get_blob_client(CONTAINER, blob_path)
            try:
                stream = await blob_client.download_blob()
                data = json.loads(await stream.readall())
                return int(data.get("count", 0))
            except ResourceNotFoundError:
                return 0
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()
