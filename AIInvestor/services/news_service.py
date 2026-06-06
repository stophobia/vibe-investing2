"""§News — Finnhub 미국 금융 뉴스 → DeepSeek 한국어 요약 → Cloudflare Worker POST.

흐름:
  1) Finnhub GET /api/v1/news?category=general
  2) Blob "news/processed/<YYYY-MM-DD>.json" 으로 dedup
     (오늘 + 어제 KST를 함께 읽어 자정 경계에서도 중복 발송 방지)
  3) 새 뉴스 0 → DeepSeek 호출 없이 조기 종료 (비용 가드)
  4) DeepSeek 1 회 호출 (json_object, max_tokens=800, temp=0.3)
     사실 요약만 — 의견/전망/투자조언 금지 (시스템 프롬프트로 강제)
  5) Cloudflare Worker 로 POST
     headers: X-Timestamp, X-Signature = hex(HMAC_SHA256(secret, "<ts>.<body>"))
     body: {ts, market_summary, items:[{id, ts, title_ko, summary_ko,
                                        category, tickers, source, url}]}
  6) 2xx 응답 시에만 processed-IDs blob 갱신 (실패 → 다음 cron 에서 재시도)

비용 가드:
  - 새 뉴스 0 → DeepSeek 호출 안 함
  - 1 회 호출당 max_tokens=800
  - 입력 batch 25 건으로 제한 (헤드라인 240자, 요약 600자 truncate)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

CONTAINER = "news"
KST = timezone(timedelta(hours=9))
FINNHUB_URL = "https://finnhub.io/api/v1/news"
MAX_ITEMS_TO_SUMMARIZE = 25
HTTP_TIMEOUT_S = 20.0

SYSTEM_PROMPT = "당신은 금융 뉴스 요약기입니다. 의견·전망·투자조언을 생성하지 마세요."

ALLOWED_CATEGORIES = {"거시경제", "실적", "반도체", "AI", "금리", "지정학", "기타"}


# ──────────────────────────────────────────────────────────────────────────────
# Pure helpers (testable without IO)
# ──────────────────────────────────────────────────────────────────────────────
def _kst_date_str(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(KST)
    return dt.astimezone(KST).strftime("%Y-%m-%d")


def _processed_blob_path(date_str: str) -> str:
    return f"processed/{date_str}.json"


def _sign_payload(secret: str, ts: str, raw_body: bytes) -> str:
    """HMAC-SHA256 over "<ts>.<raw_body>". Hex digest."""
    mac = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.".encode("utf-8") + raw_body,
        hashlib.sha256,
    )
    return mac.hexdigest()


def _build_user_prompt(items: list[dict[str, Any]]) -> str:
    """JSON-only Korean summary request. Schema embedded in the prompt."""
    lines = [
        "다음 미국 금융 뉴스 목록을 한국어로 요약하세요.",
        "출력은 JSON 한 덩어리, 아래 스키마를 정확히 따르세요:",
        '{ "market_summary": "<오늘의 시장 흐름 2~3문장 요약>",',
        '  "items": [',
        '    { "id": "<원본 id 그대로>",',
        '      "title_ko": "<한국어 제목>",',
        '      "summary_ko": "<한국어 1~2문장 요약>",',
        '      "category": "<거시경제|실적|반도체|AI|금리|지정학|기타 중 하나>",',
        '      "tickers": ["<관련 미국 티커, 없으면 빈 배열>"] }',
        '  ] }',
        "추측·전망·투자조언 금지. 사실만 한국어로 요약하세요.",
        "",
        "원문 뉴스:",
    ]
    for it in items:
        lines.append(json.dumps({
            "id": str(it.get("id")),
            "headline": (it.get("headline") or "")[:240],
            "summary": (it.get("summary") or "")[:600],
            "source": it.get("source", ""),
            "category": it.get("category", ""),
            "related": it.get("related", ""),
        }, ensure_ascii=False))
    return "\n".join(lines)


def _parse_summary_json(text: str) -> dict[str, Any]:
    """Tolerant JSON parse — returns empty shell on malformed output."""
    try:
        parsed = json.loads((text or "").strip())
    except json.JSONDecodeError:
        logger.warning("news_service: DeepSeek returned non-JSON, treating as empty")
        return {"market_summary": "", "items": []}
    if not isinstance(parsed, dict):
        return {"market_summary": "", "items": []}
    if not isinstance(parsed.get("items"), list):
        parsed["items"] = []
    parsed.setdefault("market_summary", "")
    return parsed


def _merge_summary_with_originals(
    summary: dict[str, Any],
    originals_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Stitch LLM summary fields (title_ko/summary_ko/category/tickers)
    back onto the original Finnhub item's ts/source/url. Drops IDs the LLM
    invented (not in originals_by_id)."""
    out: list[dict[str, Any]] = []
    for it in summary.get("items", []):
        if not isinstance(it, dict):
            continue
        rid = str(it.get("id", ""))
        orig = originals_by_id.get(rid)
        if not orig:
            continue
        cat = it.get("category", "기타")
        if cat not in ALLOWED_CATEGORIES:
            cat = "기타"
        tickers = it.get("tickers") or []
        if not isinstance(tickers, list):
            tickers = []
        out.append({
            "id": rid,
            "ts": int(orig.get("datetime") or 0),
            "title_ko": str(it.get("title_ko", ""))[:200],
            "summary_ko": str(it.get("summary_ko", ""))[:600],
            "category": cat,
            "tickers": [str(t)[:16] for t in tickers if t][:8],
            "source": str(orig.get("source", "")),
            "url": str(orig.get("url", "")),
        })
    return out


# ──────────────────────────────────────────────────────────────────────────────
# IO helpers (each opens & closes its own client — test seams)
# ──────────────────────────────────────────────────────────────────────────────
async def _fetch_finnhub_news(api_key: str) -> list[dict[str, Any]]:
    timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT_S)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(FINNHUB_URL,
                               params={"category": "general", "token": api_key}) as r:
            r.raise_for_status()
            data = await r.json()
    if not isinstance(data, list):
        logger.warning("news_service: Finnhub returned non-list (%s)", type(data).__name__)
        return []
    cleaned: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict) and item.get("id") is not None:
            cleaned.append(item)
    return cleaned


async def _load_processed_ids_for_date(account_name: str, date_str: str) -> set[str]:
    """Read one day's processed-IDs blob. Missing blob → empty set."""
    from azure.core.exceptions import ResourceNotFoundError
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    creds = DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            bc = svc.get_blob_client(CONTAINER, _processed_blob_path(date_str))
            try:
                body = await (await bc.download_blob()).readall()
            except ResourceNotFoundError:
                return set()
    finally:
        if hasattr(creds, "close"):
            await creds.close()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        logger.warning("news_service: processed blob for %s corrupt, ignoring", date_str)
        return set()
    return {str(x) for x in data.get("ids", [])}


async def _save_processed_ids(account_name: str, date_str: str, ids: set[str]) -> None:
    """Overwrite the day's blob with the sorted ID list."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient

    body = json.dumps({"ids": sorted(ids)}, ensure_ascii=False).encode("utf-8")
    creds = DefaultAzureCredential()
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
            await container.get_blob_client(
                _processed_blob_path(date_str)
            ).upload_blob(body, overwrite=True)
    finally:
        if hasattr(creds, "close"):
            await creds.close()


async def _summarize_with_deepseek(
    api_key: str, base_url: str, model: str, items: list[dict[str, Any]]
) -> dict[str, Any]:
    """One DeepSeek call. Returns parsed JSON (or empty shell on bad output)."""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    try:
        resp = await client.chat.completions.create(
            model=model,
            temperature=0.3,
            max_tokens=800,
            timeout=30.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(items)},
            ],
        )
    finally:
        await client.close()
    content = (resp.choices[0].message.content or "").strip()
    return _parse_summary_json(content)


async def _post_to_cf_worker(
    url: str, secret: str, payload: dict[str, Any]
) -> tuple[int, str]:
    """HMAC-signed POST. Returns (status_code, response_body[:512])."""
    raw_body = json.dumps(payload, ensure_ascii=False,
                          separators=(",", ":")).encode("utf-8")
    ts = str(int(time.time()))
    sig = _sign_payload(secret, ts, raw_body)
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Signature": sig,
    }
    timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT_S)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, data=raw_body, headers=headers) as r:
            text = await r.text()
            return r.status, (text or "")[:512]


# ──────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────────────────────────────────────
async def collect_and_post_news(config) -> dict[str, Any]:
    """Single run. Never raises — failures are caught and reported in return dict."""
    if not (config.finnhub_key and config.cf_ingest_url and config.ingest_secret):
        logger.warning("news_service: missing FINNHUB_KEY / CF_INGEST_URL / INGEST_SECRET — skipping")
        return {"skipped": "missing-config"}
    if not config.storage_account_name:
        logger.warning("news_service: storage account not set — skipping")
        return {"skipped": "missing-storage"}

    now_kst = datetime.now(KST)
    today = _kst_date_str(now_kst)
    yesterday = _kst_date_str(now_kst - timedelta(days=1))
    result: dict[str, Any] = {"kst_date": today}

    # 1) Finnhub fetch
    try:
        raw_items = await _fetch_finnhub_news(config.finnhub_key)
    except Exception:
        logger.exception("news_service: Finnhub fetch failed")
        return {**result, "error": "finnhub-fetch"}
    result["fetched"] = len(raw_items)

    # 2) Dedup against today + yesterday (KST midnight boundary)
    try:
        seen_today = await _load_processed_ids_for_date(config.storage_account_name, today)
        seen_yesterday = await _load_processed_ids_for_date(config.storage_account_name, yesterday)
    except Exception:
        logger.exception("news_service: processed-id load failed")
        return {**result, "error": "processed-load"}
    all_seen = seen_today | seen_yesterday
    unprocessed = [it for it in raw_items if str(it.get("id")) not in all_seen]
    result["new"] = len(unprocessed)
    if not unprocessed:
        result["skipped"] = "no-new-items"
        return result

    unprocessed.sort(key=lambda it: it.get("datetime") or 0, reverse=True)
    batch = unprocessed[:MAX_ITEMS_TO_SUMMARIZE]
    originals_by_id = {str(it.get("id")): it for it in batch}

    # 3) DeepSeek summary (one call)
    try:
        summary = await _summarize_with_deepseek(
            config.deepseek_api_key, config.deepseek_base_url,
            config.deepseek_model, batch,
        )
    except Exception:
        logger.exception("news_service: DeepSeek summarize failed")
        return {**result, "error": "deepseek-failed"}

    merged = _merge_summary_with_originals(summary, originals_by_id)
    if not merged:
        result["skipped"] = "empty-summary"
        return result

    payload = {
        "ts": int(time.time()),
        "market_summary": str(summary.get("market_summary", ""))[:1500],
        "items": merged,
    }

    # 4) POST to CF Worker
    try:
        status, body = await _post_to_cf_worker(
            config.cf_ingest_url, config.ingest_secret, payload,
        )
    except Exception:
        logger.exception("news_service: CF POST failed")
        return {**result, "error": "cf-post"}
    result["cf_status"] = status
    result["sent"] = len(merged)

    # 5) Save processed IDs only on 2xx
    if 200 <= status < 300:
        seen_today.update(str(it.get("id")) for it in batch)
        try:
            await _save_processed_ids(config.storage_account_name, today, seen_today)
        except Exception:
            logger.exception("news_service: save processed-ids failed")
            result["error"] = "save-processed"
    else:
        logger.warning("news_service: CF non-2xx %d body=%s", status, body[:200])
        result["error"] = f"cf-{status}"

    return result
