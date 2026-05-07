"""§T2E-B — Daily prediction missions.

Three markets, one mission each per KST day:
  KOSPI   — close-direction UP/DOWN, deadline KST 09:00, resolved KST 16:00
  NASDAQ  — close-direction UP/DOWN, deadline KST 22:30, resolved next-day KST 06:00
  BTC     — hourly price match (±0.5%), deadline = top of hour -1min,
            resolved at top of hour +1min

Storage:
  predictions/{user_id}/{market}-{kst_window_id}.json   (one per user × market × window)
  predictions/_resolved/{kst_window_id}.json            (aggregate resolved state)

Idempotency: a user can only submit ONE prediction per (market, window). The
unique key prevents A→B flip after deadline (cheating). After resolve, the
profile blob's daily prediction counter is bumped for the leaderboard.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from .gamification_config import POINTS, kst_now, kst_today_str
from .point_ledger import add_points

logger = logging.getLogger(__name__)

CONTAINER = "predictions"

# Market windows (KST hour boundaries) + yfinance ticker for resolution.
# kospi: deadline 14:00 KST (relaxed from 09:00 — users can predict during
#        the trading session with a smaller reward window). Resolved at 16:00
#        KST after market close at 15:30.
# nasdaq: deadline 22:30 KST (US market open), resolved next-day 06:00 KST.
# Individual tickers (TSLA, NVDA) share NASDAQ's window.
MARKET_WINDOWS = {
    "kospi":  {"deadline_kst_hour": 14, "deadline_kst_min": 0,
               "resolve_kst_hour": 16,  "resolve_kst_min": 0,
               "yf_ticker": "^KS11", "label": "KOSPI"},
    "nasdaq": {"deadline_kst_hour": 22, "deadline_kst_min": 30,
               "resolve_kst_hour": 6,   "resolve_kst_min": 0,
               "resolve_next_day": True, "yf_ticker": "^IXIC", "label": "NASDAQ"},
    "TSLA":   {"deadline_kst_hour": 22, "deadline_kst_min": 30,
               "resolve_kst_hour": 6,   "resolve_kst_min": 0,
               "resolve_next_day": True, "yf_ticker": "TSLA", "label": "Tesla"},
    "NVDA":   {"deadline_kst_hour": 22, "deadline_kst_min": 30,
               "resolve_kst_hour": 6,   "resolve_kst_min": 0,
               "resolve_next_day": True, "yf_ticker": "NVDA", "label": "NVIDIA"},
    # BTC handled separately (hourly UP/DOWN — see _btc functions below)
}

# Per-market reward keys (for participate / correct points lookup)
def _reward_keys(market: str) -> tuple[str, str]:
    if market in ("kospi", "nasdaq"):
        return f"predict_{market}_participate", f"predict_{market}_correct"
    # Per-ticker NASDAQ TOP 10 — share a single reward (10/100 P)
    return "predict_nasdaq_participate", "predict_nasdaq_top10_correct"


@dataclass
class Prediction:
    user_id: str           # internal user_key (tg:<id>)
    anon_user_id: str      # for the resolved aggregate (privacy-safe)
    market: str            # "kospi" | "nasdaq" | "btc"
    window_id: str         # e.g. "2026-05-07" for daily, "2026-05-07T15" for BTC hourly
    direction: str = ""    # "up" | "down" for daily; ignored for BTC
    predicted_price: float | None = None  # BTC only
    submitted_at: str = ""
    resolved: bool = False
    actual_direction: str = ""
    actual_price: float | None = None
    correct: bool = False
    resolved_at: str = ""


def _kst_dt(year, month, day, hour, minute) -> datetime:
    """Build a KST datetime, return as UTC-aware datetime."""
    return datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))


def _within_submission_window(market: str) -> tuple[bool, datetime, str]:
    """For daily markets, return (open_now, resolve_dt_utc, window_id)."""
    cfg = MARKET_WINDOWS.get(market)
    if not cfg:
        raise ValueError(f"unknown market: {market}")

    kst = kst_now()
    today_id = kst.date().isoformat()
    deadline_kst = _kst_dt(kst.year, kst.month, kst.day,
                           cfg["deadline_kst_hour"], cfg["deadline_kst_min"])
    if cfg.get("resolve_next_day"):
        resolve_kst = _kst_dt(kst.year, kst.month, kst.day,
                              cfg["resolve_kst_hour"], cfg["resolve_kst_min"]) + timedelta(days=1)
    else:
        resolve_kst = _kst_dt(kst.year, kst.month, kst.day,
                              cfg["resolve_kst_hour"], cfg["resolve_kst_min"])

    now_kst = kst.replace(tzinfo=timezone(timedelta(hours=9)))
    open_now = now_kst < deadline_kst
    return open_now, resolve_kst.astimezone(timezone.utc), today_id


def _btc_window_id() -> str:
    """Current BTC hourly window: 'YYYY-MM-DD HH' KST. Submission window
    closes at HH:59 KST (= 1 minute before next top-of-hour)."""
    kst = kst_now()
    return f"{kst.year:04d}-{kst.month:02d}-{kst.day:02d}T{kst.hour:02d}"


# ──────────────────────────────────────────────────────────
# Submit + read
# ──────────────────────────────────────────────────────────

async def submit_daily_prediction(
    storage_account_name: str,
    user_key: str,
    anon_user_id: str,
    market: str,
    direction: str,
    *,
    repo,
    usage_logger=None,
    credential=None,
) -> tuple[bool, str, dict | None]:
    """Submit KOSPI or NASDAQ daily UP/DOWN prediction.

    Returns (success, error_code, payload).
    Error codes: window_closed | already_submitted | invalid_direction | unknown_market
    """
    if market not in MARKET_WINDOWS:
        return False, "unknown_market", None
    if direction not in ("up", "down"):
        return False, "invalid_direction", None

    open_now, resolve_dt, window_id = _within_submission_window(market)
    if not open_now:
        return False, "window_closed", None

    blob_path = f"{user_key.replace('tg:', '')}/{market}-{window_id}.json"

    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            client = svc.get_blob_client(CONTAINER, blob_path)

            # Idempotency: refuse if already submitted for this window
            try:
                await client.get_blob_properties()
                return False, "already_submitted", None
            except ResourceNotFoundError:
                pass

            prediction = Prediction(
                user_id=user_key, anon_user_id=anon_user_id,
                market=market, window_id=window_id, direction=direction,
                submitted_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
            await client.upload_blob(
                json.dumps(asdict(prediction), ensure_ascii=False).encode(),
                overwrite=False, content_type="application/json",
            )
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    # Award participation points
    p_key, c_key = _reward_keys(market)
    await add_points(
        repo, user_key, POINTS[p_key],
        reason=p_key, ref=f"{market}-{window_id}",
        usage_logger=usage_logger,
    )

    # §T2E-C — first-mission completion may unlock inviter's verified bonus
    try:
        from .invite_service import maybe_validate_first_mission
        await maybe_validate_first_mission(repo, user_key, usage_logger=usage_logger)
    except Exception:
        logger.exception("invite validation hook failed (non-fatal)")

    return True, "", {
        "market": market, "window_id": window_id, "direction": direction,
        "participation_points": POINTS[p_key],
        "potential_correct_points": POINTS[c_key],
        "resolves_at": resolve_dt.isoformat(),
    }


async def submit_btc_hourly_prediction(
    storage_account_name: str,
    user_key: str,
    anon_user_id: str,
    direction: str,
    *,
    repo,
    usage_logger=None,
    credential=None,
    anchor_price: float | None = None,
) -> tuple[bool, str, dict | None]:
    """Submit a BTC UP/DOWN prediction for the next hour.

    Resolves at HH+1:01 by comparing the user's submitted_price (anchor at
    submission time) to BTC price at HH+1:00. UP/DOWN like KOSPI/NASDAQ.
    """
    if direction not in ("up", "down"):
        return False, "invalid_direction", None

    # Submission window: now until HH:59 KST (1 min before next top of hour)
    kst = kst_now()
    if kst.minute >= 59:
        return False, "window_closed", None

    window_id = _btc_window_id()  # current hour
    blob_path = f"{user_key.replace('tg:', '')}/btc-{window_id}.json"

    # Capture current BTC price as the user's anchor (price at submit time).
    # Resolution compares this anchor to the price at the next top-of-hour.
    if anchor_price is None or anchor_price <= 0:
        try:
            import yfinance as yf
            import asyncio as _asyncio
            info = await _asyncio.to_thread(lambda: yf.Ticker("BTC-USD").fast_info)
            anchor_price = float(info.last_price) if info and info.last_price else 0.0
        except Exception:
            anchor_price = 0.0
    if not anchor_price:
        return False, "btc_price_unavailable", None

    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            client = svc.get_blob_client(CONTAINER, blob_path)
            try:
                await client.get_blob_properties()
                return False, "already_submitted", None
            except ResourceNotFoundError:
                pass

            prediction = Prediction(
                user_id=user_key, anon_user_id=anon_user_id,
                market="btc", window_id=window_id,
                direction=direction,
                predicted_price=float(anchor_price),   # anchor, not a guess
                submitted_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
            await client.upload_blob(
                json.dumps(asdict(prediction), ensure_ascii=False).encode(),
                overwrite=False, content_type="application/json",
            )
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    await add_points(
        repo, user_key, POINTS["predict_btc_participate"],
        reason="predict_btc_participate", ref=f"btc-{window_id}",
        usage_logger=usage_logger,
    )

    # §T2E-C — first-mission completion may unlock inviter's verified bonus
    try:
        from .invite_service import maybe_validate_first_mission
        await maybe_validate_first_mission(repo, user_key, usage_logger=usage_logger)
    except Exception:
        logger.exception("invite validation hook failed (non-fatal)")

    return True, "", {
        "market": "btc", "window_id": window_id,
        "direction": direction, "anchor_price": anchor_price,
        "participation_points": POINTS["predict_btc_participate"],
        "potential_correct_points": POINTS["predict_btc_correct"],
    }


# ──────────────────────────────────────────────────────────
# Resolve (called from Timer triggers)
# ──────────────────────────────────────────────────────────

async def resolve_market_predictions(
    storage_account_name: str,
    market: str,
    actual_direction: str,
    window_id: str,
    *,
    repo,
    usage_logger=None,
    credential=None,
) -> dict[str, int]:
    """Mark all unresolved predictions for (market, window_id) as resolved
    and credit correct guesses. Returns {anon_user_id: points_awarded} for telemetry."""
    creds = credential or DefaultAzureCredential()
    awarded: dict[str, int] = {}
    _, c_key = _reward_keys(market)
    correct_pts = POINTS[c_key]

    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            async for blob in container.list_blobs():
                # Match {user_id}/{market}-{window_id}.json
                if not blob.name.endswith(f"/{market}-{window_id}.json"):
                    continue
                client = container.get_blob_client(blob.name)
                try:
                    stream = await client.download_blob()
                    body = await stream.readall()
                    pred = Prediction(**json.loads(body))
                except Exception:
                    logger.exception("failed reading prediction %s", blob.name)
                    continue

                if pred.resolved:
                    continue

                pred.resolved = True
                pred.actual_direction = actual_direction
                pred.correct = (pred.direction == actual_direction)
                pred.resolved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

                if pred.correct:
                    try:
                        await add_points(
                            repo, pred.user_id, correct_pts,
                            reason=c_key,
                            ref=f"{market}-{window_id}",
                            usage_logger=usage_logger,
                        )
                        awarded[pred.anon_user_id] = correct_pts
                    except Exception:
                        logger.exception("failed awarding correct points to %s", pred.user_id)

                await client.upload_blob(
                    json.dumps(asdict(pred), ensure_ascii=False).encode(),
                    overwrite=True, content_type="application/json",
                )
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    return awarded


async def resolve_btc_hourly_predictions(
    storage_account_name: str,
    actual_price: float,
    window_id: str,
    *,
    repo,
    usage_logger=None,
    credential=None,
) -> dict[str, int]:
    """Resolve all BTC hourly UP/DOWN predictions for the given window.

    Each prediction has its own anchor (price at submit time). Correct iff
    direction matches the price movement from anchor to actual_price.
    """
    creds = credential or DefaultAzureCredential()
    awarded: dict[str, int] = {}
    correct_pts = POINTS["predict_btc_correct"]

    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            async for blob in container.list_blobs():
                if not blob.name.endswith(f"/btc-{window_id}.json"):
                    continue
                client = container.get_blob_client(blob.name)
                try:
                    stream = await client.download_blob()
                    body = await stream.readall()
                    pred = Prediction(**json.loads(body))
                except Exception:
                    continue
                if pred.resolved:
                    continue

                anchor = pred.predicted_price or 0.0
                pred.resolved = True
                pred.actual_price = actual_price
                pred.resolved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
                # Direction-based check
                if anchor > 0:
                    actual_dir = "up" if actual_price > anchor else "down"
                    pred.actual_direction = actual_dir
                    pred.correct = (pred.direction == actual_dir)
                else:
                    pred.correct = False

                if pred.correct:
                    try:
                        await add_points(
                            repo, pred.user_id, correct_pts,
                            reason="predict_btc_correct",
                            ref=f"btc-{window_id}",
                            usage_logger=usage_logger,
                        )
                        awarded[pred.anon_user_id] = correct_pts
                    except Exception:
                        logger.exception("BTC correct-points award failed")

                await client.upload_blob(
                    json.dumps(asdict(pred), ensure_ascii=False).encode(),
                    overwrite=True, content_type="application/json",
                )
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    return awarded
