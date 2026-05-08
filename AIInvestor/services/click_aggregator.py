"""§5 P1 — Third-party prediction click aggregator.

`POST /api/predictions/<id>/click` writes a tiny NDJSON record. Every 15 min
this aggregator scans the last N hours of click logs, dedups by viewer_id
within (prediction_id), and updates each Prediction's `click_count`
monotonically.

Eventually consistent — that's OK by spec. The click endpoint must stay
<50ms p95 (single Blob append + in-memory rate-limit check), so we never
do the dedup synchronously.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .prediction_repo import PredictionRepo

logger = logging.getLogger(__name__)

CLICKS_CONTAINER = "logs"
CLICKS_PREFIX = "clicks"


def _click_log_path(now_utc: datetime | None = None) -> str:
    """clicks/YYYY/MM/DD/HH.ndjson — partitioned by UTC hour."""
    now_utc = now_utc or datetime.now(timezone.utc)
    return (f"{CLICKS_PREFIX}/{now_utc.year:04d}/{now_utc.month:02d}/"
            f"{now_utc.day:02d}/{now_utc.hour:02d}.ndjson")


# ─────────────────────────────────────────────────────────────────────────────
# In-memory rate limit (same viewer × prediction 1× per 30s)
# ─────────────────────────────────────────────────────────────────────────────
_RECENT_CLICKS: dict[tuple[str, str], float] = {}
_RATE_WINDOW_S = 30


def is_rate_limited(viewer_id: str, prediction_id: str) -> bool:
    import time
    key = (viewer_id, prediction_id)
    now = time.monotonic()
    last = _RECENT_CLICKS.get(key)
    if last and (now - last) < _RATE_WINDOW_S:
        return True
    _RECENT_CLICKS[key] = now
    # Soft eviction: drop entries older than 5min to bound dict size
    if len(_RECENT_CLICKS) > 5000:
        cutoff = now - 300
        for k in list(_RECENT_CLICKS.keys()):
            if _RECENT_CLICKS[k] < cutoff:
                _RECENT_CLICKS.pop(k, None)
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Append a click record (used by /api/predictions/<id>/click)
# ─────────────────────────────────────────────────────────────────────────────
async def append_click(account_name: str, prediction_id: str,
                       viewer_id: str, country: str = "",
                       credential=None) -> None:
    """Append-blob single line. Best-effort, swallows errors (logs only)."""
    from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prediction_id": prediction_id,
        "viewer_id": viewer_id[:8],
        "country": country,
    }
    line = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CLICKS_CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            except Exception:
                pass
            bc = container.get_blob_client(_click_log_path())
            try:
                await bc.create_append_blob()
            except ResourceExistsError:
                pass
            await bc.append_block(line)
    except Exception:
        logger.warning("append_click failed for %s", prediction_id, exc_info=True)
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()


# ─────────────────────────────────────────────────────────────────────────────
# Aggregate (15-min cron)
# ─────────────────────────────────────────────────────────────────────────────
async def aggregate_clicks(repo: PredictionRepo, account_name: str,
                           window_hours: int = 24,
                           credential=None) -> dict:
    """Scan recent click NDJSON, dedup viewers per prediction, update counts.

    Returns {predictions_updated, total_clicks_seen}.
    """
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    now = datetime.now(timezone.utc)
    window_paths = []
    for h in range(window_hours):
        ts = now - timedelta(hours=h)
        window_paths.append(_click_log_path(ts))

    # prediction_id → set(viewer_id)
    viewers: dict[str, set[str]] = defaultdict(set)
    total_lines = 0

    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            for path in window_paths:
                bc = svc.get_blob_client(CLICKS_CONTAINER, path)
                try:
                    body = await (await bc.download_blob()).readall()
                except ResourceNotFoundError:
                    continue
                except Exception:
                    logger.debug("click log read failed %s", path, exc_info=True)
                    continue
                for line in body.decode("utf-8", errors="replace").splitlines():
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    pid = rec.get("prediction_id")
                    vid = rec.get("viewer_id")
                    if pid and vid:
                        viewers[pid].add(vid)
                    total_lines += 1
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    # For each prediction with ≥1 unique viewer, fetch + monotonic update.
    # We need the anon (owner) — encoded in prediction_id is NOT possible,
    # so we rely on the repo to find the prediction via brute scan. Light
    # enough for early MVP since prediction count is low.
    updated = 0
    if viewers:
        from .prediction_repo import _to_prediction
        # Walk all predictions to map prediction_id → anon
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=(credential or DefaultAzureCredential()),
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
                    bc = container.get_blob_client(blob.name)
                    body = await (await bc.download_blob()).readall()
                    p = _to_prediction(json.loads(body))
                except Exception:
                    continue
                if p.prediction_id not in viewers:
                    continue
                count = len(viewers[p.prediction_id])
                if count > p.click_count:
                    if await repo.increment_click_count(
                        p.anon_user_id, p.prediction_id, count,
                    ):
                        updated += 1

    return {"predictions_updated": updated, "total_clicks_seen": total_lines}
