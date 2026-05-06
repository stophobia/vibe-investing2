# 종목 티커 데이터 캐싱 아키텍처 결정 문서

**대상 엔드포인트**: `https://black-plant-0f73c5e00.7.azurestaticapps.net/data/{ticker}`
**리프레시 주기**: 30분 ~ 4시간 (적응형, 본 문서 §1 참조)
**문서 버전**: v1.0 (2026-05-05)
**관련 문서**: `jeunggwon-architecture-v3.0-ko.md` (§8 적응형 캐싱, §12 Cosmos TTL)

---

## 0. 결론 요약 (TL;DR)

| 질문 | 답 |
|---|---|
| Azure Functions에서 인메모리 캐싱이 가능한가? | **가능**. Python `dict` 또는 `functools.lru_cache`를 모듈 전역으로 두면 인스턴스 생존 기간 동안 유지됨. 단, 멀티 인스턴스 간 공유 안 됨. |
| 콜드 스타트 시 초기화는 허용 가능한가? | **허용 가능**. 콜드 스타트 시 첫 요청만 LLM/외부 API를 호출하고 이후 N분간 캐시 히트. 사용자 체감 영향 미미. |
| Static Web Apps + Blob JSON 단독 운영이 가능한가? | **가능, 그러나 권장 안 함**. Static Web Apps는 정적 파일만 서빙하므로 동적 갱신을 위한 외부 트리거(Functions)가 결국 필요. |
| **권장 아키텍처는?** | **3-tier 하이브리드**: Static Web Apps (CDN 엣지) ← Blob JSON (영속 캐시) ← Azure Functions in-memory (핫 캐시). 갱신은 Timer Trigger로 30분~4시간 단위. |

---

## 1. 요구사항 정리

### 1.1 엔드포인트 형태

```
GET https://black-plant-0f73c5e00.7.azurestaticapps.net/data/{ticker}
```

응답 예시 (JSON):

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "price_usd": 487.32,
  "change_percent_24h": 2.18,
  "market_cap_usd": 1198000000000,
  "pe_ratio": 33.9,
  "fetched_at": "2026-05-05T14:23:11Z",
  "next_refresh_at": "2026-05-05T14:53:11Z",
  "ttl_minutes": 30,
  "source": "alpha_vantage"
}
```

### 1.2 리프레시 주기 정책 (§8 적응형 캐싱과 정렬)

| 종목 분류 | TTL | 사유 |
|---|---|---|
| 핵심 종목 (NVDA, TSLA, AAPL, BTC, ETH 등 상위 20개) | **30분** | 트래픽 집중, 가격 변동 민감, 사용자 기대 정밀도 높음 |
| 일반 인기 종목 (S&P 100, KOSPI 50) | **60분** | 적당한 트래픽, 일반적 정밀도 |
| 롱테일 종목 (그 외) | **4시간** | 트래픽 낮음, API 호출 비용 절감 |
| 시장 마감 시간대 (KST 16:00~22:30) | 모두 **4시간** | 가격 변동 없음 (한국·미국 모두 마감) |
| 주말 (UTC 토일) | 모두 **24시간** | 거래소 휴장 |

이 정책은 §8.2 마일 타이밍 군집 캐싱과 일관됩니다.

### 1.3 트래픽 가정

| 단계 | 일 호출 | 피크 RPS |
|---|---|---|
| MVP (DAU 500) | 5,000 | 5 |
| 성장기 (DAU 3,000) | 30,000 | 30 |
| 성숙기 (DAU 10,000) | 120,000 | 120 |
| 대규모 (DAU 50,000) | 600,000 | 600 |

피크 600 RPS까지는 단일 Azure Functions 인스턴스(2GB)로 처리 가능합니다(Flex Consumption HTTP 트리거 기본 동시성 100 가정 시 6 인스턴스 스케일아웃).

---

## 2. Azure Functions 인메모리 캐싱 구조 검증

### 2.1 핵심 사실

Azure Functions Flex Consumption 플랜에서 동일 인스턴스 내 모든 전역 변수는 **인스턴스 생명주기 동안 유지**됩니다. 즉:

- HTTP 트리거 함수 모듈의 `cache: dict = {}` 같은 전역 변수는 **첫 요청에서 채워지고, 이후 같은 인스턴스로 라우팅된 요청은 캐시 히트**.
- 인스턴스가 스케일인되거나 재배포될 때 캐시 사라짐.
- 새 인스턴스가 스케일아웃되면 **캐시 미스로 시작**, 첫 요청에서 다시 채워짐.

### 2.2 가장 단순한 구현

```python
# function_app.py
import azure.functions as func
import time
import httpx
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# 모듈 전역 캐시 (인스턴스 의존 동안 유지)
TICKER_CACHE: dict[str, dict] = {}
CACHE_LOCK_PER_TICKER: dict[str, "asyncio.Lock"] = {}

DEFAULT_TTL_SECONDS = 1800   # 30분
LONG_TTL_SECONDS = 14400     # 4시간

HOT_TICKERS = {"NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META",
               "BTC", "ETH", "SOL", "005930", "000660"}

def get_ttl(ticker: str) -> int:
    """티커별 TTL 결정"""
    if ticker.upper() in HOT_TICKERS:
        return DEFAULT_TTL_SECONDS  # 30분
    return LONG_TTL_SECONDS  # 4시간

@app.route(route="data/{ticker}", methods=["GET"])
async def get_ticker_data(req: func.HttpRequest) -> func.HttpResponse:
    ticker = req.route_params.get("ticker", "").upper()

    if not ticker or len(ticker) > 12:
        return func.HttpResponse(
            json.dumps({"error": "invalid ticker"}),
            status_code=400,
            mimetype="application/json"
        )

    now = time.time()
    ttl = get_ttl(ticker)

    # 인메모리 캐시 조회
    cached = TICKER_CACHE.get(ticker)
    if cached and (now - cached["fetched_at_ts"]) < ttl:
        return func.HttpResponse(
            json.dumps(cached["data"]),
            status_code=200,
            mimetype="application/json",
            headers={"X-Cache": "HIT", "Cache-Control": f"public, max-age={ttl}"}
        )

    # 캐시 미스 - 외부 API 호출
    data = await fetch_from_provider(ticker)
    TICKER_CACHE[ticker] = {
        "fetched_at_ts": now,
        "data": data
    }

    return func.HttpResponse(
        json.dumps(data),
        status_code=200,
        mimetype="application/json",
        headers={"X-Cache": "MISS", "Cache-Control": f"public, max-age={ttl}"}
    )


async def fetch_from_provider(ticker: str) -> dict:
    """Alpha Vantage 또는 한국투자증권 API 호출"""
    # ... 실제 구현 ...
    return {
        "ticker": ticker,
        "price_usd": 487.32,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ttl_minutes": get_ttl(ticker) // 60
    }
```

이 코드는 **약 30~40줄**로 인메모리 캐싱이 완성됩니다. Redis나 별도 캐시 서비스 불필요.

### 2.3 동시성 제어 (Cache Stampede 방지)

캐시 만료 직후 100명이 동시에 같은 티커를 요청하면 외부 API가 100번 호출되는 문제 (cache stampede)가 발생할 수 있습니다. `asyncio.Lock`으로 티커별 단일 fetch를 보장합니다.

```python
import asyncio

CACHE_LOCKS: dict[str, asyncio.Lock] = {}

def get_lock(ticker: str) -> asyncio.Lock:
    if ticker not in CACHE_LOCKS:
        CACHE_LOCKS[ticker] = asyncio.Lock()
    return CACHE_LOCKS[ticker]

@app.route(route="data/{ticker}", methods=["GET"])
async def get_ticker_data(req: func.HttpRequest) -> func.HttpResponse:
    ticker = req.route_params.get("ticker", "").upper()
    now = time.time()
    ttl = get_ttl(ticker)

    # 1차 캐시 조회 (lock 없이)
    cached = TICKER_CACHE.get(ticker)
    if cached and (now - cached["fetched_at_ts"]) < ttl:
        return _cached_response(cached["data"], ttl, hit=True)

    # 캐시 미스 - lock으로 단일 fetcher 보장
    async with get_lock(ticker):
        # double-check (다른 코루틴이 그새 채웠을 수 있음)
        cached = TICKER_CACHE.get(ticker)
        if cached and (time.time() - cached["fetched_at_ts"]) < ttl:
            return _cached_response(cached["data"], ttl, hit=True)

        data = await fetch_from_provider(ticker)
        TICKER_CACHE[ticker] = {"fetched_at_ts": time.time(), "data": data}
        return _cached_response(data, ttl, hit=False)
```

### 2.4 인스턴스 메모리 한계

Flex Consumption 인스턴스는 512MB / 2GB / 4GB 옵션. 본 용도에는 **2GB가 적정**합니다.

| 항목 | 추정 메모리 |
|---|---|
| Functions 런타임 + Python | ~250 MB |
| 핫 티커 100개 × 1KB JSON | ~100 KB |
| 롱테일 티커 5,000개 × 1KB JSON (캐시되면) | ~5 MB |
| `asyncio.Lock` 5,000개 | ~1 MB |
| 여유 + 다른 코드 | ~1.6 GB |

**메모리는 충분**. 5,000개 티커 전부 캐시해도 6 MB 미만입니다.

### 2.5 다중 인스턴스 캐시 일관성

Flex Consumption은 트래픽에 따라 자동 스케일아웃됩니다. 인스턴스가 2개로 늘면 두 인스턴스의 인메모리 캐시는 **독립적**입니다.

| 시나리오 | 결과 |
|---|---|
| 인스턴스 1만 NVDA를 캐시하고, 인스턴스 2로 라우팅된 요청 | 인스턴스 2가 외부 API를 다시 호출 (stale 응답이 아니라 fresh fetch) |
| 인스턴스 1과 2 모두 NVDA 캐시. 인스턴스 1만 만료. | 인스턴스 1로 라우팅된 요청은 새로 fetch, 인스턴스 2는 여전히 캐시 히트 |
| 사용자 입장에서 불일치 우려 | 두 응답 모두 30분~4시간 윈도우 내 가격이므로 차이는 미미. **저정도 정책은 허용 가능**. |

> **핵심 통찰**: 인스턴스 간 캐시 분기는 외부 API 호출 횟수를 약간 늘릴 뿐, 사용자 응답 품질에는 영향 없음. 본 용도에서는 무시 가능.

### 2.6 Always Ready 인스턴스로 콜드 스타트 완화

Flex Consumption의 Always Ready 옵션을 활성화하면 최소 N개 인스턴스가 항상 떠 있어 콜드 스타트 없이 캐시 히트가 가능합니다.

| Always Ready 인스턴스 수 | 월 비용 (2GB 기준) | 효과 |
|---|---|---|
| 0 | $0 (요청 시에만 과금) | 콜드 스타트 발생, 캐시 자주 초기화 |
| 1 | 약 $35 (Baseline 요금) | 콜드 스타트 없음, 캐시 항상 살아 있음 |
| 2 | 약 $70 | 고가용성 |

> MVP 단계에서는 Always Ready 0으로 시작하고, 트래픽이 늘면 1로 올리는 것이 저비용 운영 원칙에 부합합니다.

---

## 3. Static Web Apps 단독 vs Blob JSON 캐시 vs 하이브리드 비교

세 가지 후보 아키텍처를 비교합니다.

### 3.1 후보 A: Static Web Apps + 미리 빌드된 JSON 파일

```
[빌드 시점]                    [런타임]
GitHub Actions로 30분마다       Azure Static Web Apps 엣지에서
모든 티커 JSON을 미리 빌드 →    /data/{ticker}.json 정적 서빙
```

**장점**:
- 응답 시간 가장 빠름 (CDN 엣지 hit, 보통 50ms 이내)
- 대역폭 비용 매우 저렴 (Free 티어 100 GB/월)
- 인프라 단순 (Functions 불필요)
- 다운타임 없음

**단점**:
- **갱신 주기가 GitHub Actions 빌드 주기에 묶임**. 30분마다 빌드 = 일 약 1,440회 빌드 (GitHub Actions Free 2,000분/월 한도와 거리가 있음)
- 5,000개 티커 × 30분 = 매번 5,000개 외부 API 호출 (Alpha Vantage 무료 한도 일 500회 초과)
- 티커별 다른 TTL 적용 어려움 (모두 같은 빌드 주기)
- 신규 티커 추가 시 즉시 반영 불가

**적합한 경우**: 티커 수가 100개 이하이고 1시간 이상 단일 TTL로 충분한 경우.

### 3.2 후보 B: Static Web Apps + Blob JSON + Functions 갱신

```
[Timer Trigger]                  [Static Web Apps]
Azure Functions가 30분/4시간     /data/{ticker} →
마다 Blob의 JSON 갱신        →    Blob의 JSON을 프록시 또는 redirect
```

**장점**:
- 갱신 로직과 서빙 분리, 깔끔한 책임 분리
- Blob Storage는 사실상 무한 확장
- TTL을 티커별로 다르게 적용 가능 (Functions에서 결정)
- 신규 티커는 첫 요청 시 Functions가 즉시 갱신

**단점**:
- Static Web Apps는 정적 파일만 직접 서빙. 외부 Blob을 프록시하려면 routes 설정 또는 client-side fetch 필요
- 응답 흐름: User → SWA → Blob (1~2 hop, 100~200ms)
- Blob에 매번 쓰는 비용 + 트랜잭션 비용 발생 (월 ~$3)

**적합한 경우**: 티커 수 1,000개 이상, 영속성이 중요한 경우.

### 3.3 후보 C: Static Web Apps + Functions 인메모리 캐시 + Blob 백업 (하이브리드, 권장)

```
[Timer Trigger]                  [HTTP Trigger]                    [Static Web Apps]
30분/4시간마다 핫 티커     +     /data/{ticker} 요청 시:           /data/{ticker} →
미리 갱신 (워밍)                  1. 인메모리 캐시 확인              SWA Routes로 Functions 백엔드 라우팅
                                  2. miss → Blob 확인
                                  3. miss → 외부 API + Blob 저장 + 메모리 저장
```

**장점**:
- 핫 캐시: 인메모리 (50ms 이내 응답)
- 웜 캐시: Blob (100~200ms, 인스턴스 재시작 후에도 살아 있음)
- 콜드: 외부 API (실시간 fetch)
- TTL 티커별 적용
- 인스턴스 재시작/스케일아웃 시 Blob에서 즉시 복구 (cold start 영향 최소화)
- 신규 티커 즉시 처리 가능

**단점**:
- 코드 복잡도 가장 높음 (3 단계 캐시 로직)
- Blob 트랜잭션 비용 (월 ~$3)

**적합한 경우**: **본 프로젝트에 권장 구성**.

### 3.4 비교표

| 차원 | A: SWA만 | B: SWA + Blob | C: SWA + Functions + Blob (권장) |
|---|---|---|---|
| 첫 응답 지연 (cold) | N/A (빌드된 정적) | 200~500ms | 200~500ms (외부 API) |
| 캐시된 응답 지연 | **~50ms** (CDN) | 100~200ms | **~50ms (메모리), 100~200ms (Blob)** |
| 갱신 주기 유연성 | 낮음 (빌드 단위) | 높음 (Timer Trigger) | **높음** |
| 티커별 다른 TTL | 어려움 | 가능 | **가능** |
| 인스턴스 재시작 영향 | 없음 | 없음 | **Blob 백업으로 최소화** |
| 신규 티커 즉시 처리 | 불가 | 가능 | **가능** |
| 외부 API 호출 횟수 | 매 빌드마다 전수 | 매 Timer마다 전수 | **요청 발생 종목만** (효율적) |
| Cosmos DB 필요 여부 | 불필요 | 불필요 | 불필요 |
| 운영 복잡도 | 낮음 | 중간 | 중상 |
| 월 인프라 비용 (DAU 3,000 가정) | $0~5 | $5~10 | **$10~20** |
| MVP 적합성 | 좋음 (티커 100개 이하 시) | 중간 | **좋음 (5,000개 티커도 처리)** |

---

## 4. 권장 아키텍처 (후보 C 상세)

### 4.1 전체 흐름도

```
사용자 브라우저
       │
       │ GET /data/NVDA
       ▼
Azure Static Web Apps (CDN 엣지)
   - staticwebapp.config.json의 routes로 /data/* 요청을 백엔드 Functions로 프록시
       │
       ▼
Azure Functions (Linked Backend, Flex Consumption)
       │
       ├─[1단계] 인메모리 캐시 조회
       │     hit + fresh → 즉시 반환 (~5ms 처리)
       │     miss or stale ↓
       │
       ├─[2단계] Blob Storage 캐시 조회
       │     hit + fresh → 메모리에 채우고 반환 (~50ms)
       │     miss or stale ↓
       │
       ├─[3단계] 외부 API 호출 (Alpha Vantage / KIS)
       │     fetch + Blob 저장 + 메모리 저장 → 반환 (~200ms)
       │
       │
       │ [별도 Timer Trigger, 병렬 실행]
       ▼
30분/4시간마다 핫 티커 일괄 갱신
   - HOT_TICKERS 리스트의 모든 종목을 외부 API에서 갱신
   - Blob과 메모리 모두 업데이트 (사용자 요청 발생 전 미리 데이터 준비)
```

### 4.2 코드 골격

```python
# function_app.py
import azure.functions as func
import json
import time
import asyncio
import httpx
from azure.storage.blob.aio import BlobServiceClient
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

BLOB_CONN = os.environ["BLOB_STORAGE_CONNECTION_STRING"]
BLOB_CONTAINER = "ticker-cache"

# 모듈 전역 (인스턴스 의존 동안 유지)
TICKER_CACHE: dict[str, dict] = {}
CACHE_LOCKS: dict[str, asyncio.Lock] = {}

HOT_TICKERS = {"NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META",
               "BTC", "ETH", "SOL", "005930", "000660"}

def get_ttl_seconds(ticker: str) -> int:
    if ticker.upper() in HOT_TICKERS:
        return 1800   # 30분
    return 14400      # 4시간

def get_lock(ticker: str) -> asyncio.Lock:
    if ticker not in CACHE_LOCKS:
        CACHE_LOCKS[ticker] = asyncio.Lock()
    return CACHE_LOCKS[ticker]

# ────────────────────────────────────────────────────────
# HTTP Trigger: /data/{ticker}
# ────────────────────────────────────────────────────────
@app.route(route="data/{ticker}", methods=["GET"])
async def get_ticker(req: func.HttpRequest) -> func.HttpResponse:
    ticker = req.route_params.get("ticker", "").upper()

    if not ticker or not ticker.replace(".", "").isalnum() or len(ticker) > 12:
        return _error_response(400, "invalid ticker")

    ttl = get_ttl_seconds(ticker)
    now = time.time()

    # 1단계: 인메모리
    cached = TICKER_CACHE.get(ticker)
    if cached and (now - cached["ts"]) < ttl:
        return _ok_response(cached["data"], ttl, source="memory")

    # 2단계: Blob (lock 안에서)
    async with get_lock(ticker):
        # double-check
        cached = TICKER_CACHE.get(ticker)
        if cached and (time.time() - cached["ts"]) < ttl:
            return _ok_response(cached["data"], ttl, source="memory")

        # Blob 시도
        blob_data = await _read_blob(ticker)
        if blob_data and (time.time() - blob_data["ts"]) < ttl:
            TICKER_CACHE[ticker] = blob_data
            return _ok_response(blob_data["data"], ttl, source="blob")

        # 3단계: 외부 API
        fresh = await _fetch_from_provider(ticker)
        entry = {"ts": time.time(), "data": fresh}
        TICKER_CACHE[ticker] = entry
        await _write_blob(ticker, entry)
        return _ok_response(fresh, ttl, source="origin")


# ────────────────────────────────────────────────────────
# Timer Trigger: 30분마다 핫 티커 일괄 갱신
# ────────────────────────────────────────────────────────
@app.schedule(schedule="0 */30 * * * *", arg_name="t")
async def refresh_hot_tickers(t: func.TimerRequest) -> None:
    """매 30분마다 HOT_TICKERS 일괄 갱신 (사전 워밍)"""
    if _is_market_closed_kst():
        return  # 마감 시간대에는 skip

    for ticker in HOT_TICKERS:
        try:
            fresh = await _fetch_from_provider(ticker)
            entry = {"ts": time.time(), "data": fresh}
            TICKER_CACHE[ticker] = entry
            await _write_blob(ticker, entry)
        except Exception as e:
            logging.warning(f"refresh failed for {ticker}: {e}")


# ────────────────────────────────────────────────────────
# Timer Trigger: 4시간마다 일반 티커 갱신 (선택사항)
# ────────────────────────────────────────────────────────
@app.schedule(schedule="0 0 */4 * * *", arg_name="t")
async def refresh_warm_tickers(t: func.TimerRequest) -> None:
    """4시간마다 사용 빈도 높았던 일반 티커 갱신"""
    # 최근 24시간 사용 통계에서 인기 종목 추출 (선택적 구현)
    pass


# ────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────
async def _read_blob(ticker: str) -> dict | None:
    try:
        client = BlobServiceClient.from_connection_string(BLOB_CONN)
        blob = client.get_blob_client(BLOB_CONTAINER, f"{ticker}.json")
        content = await (await blob.download_blob()).readall()
        return json.loads(content)
    except Exception:
        return None

async def _write_blob(ticker: str, entry: dict) -> None:
    try:
        client = BlobServiceClient.from_connection_string(BLOB_CONN)
        blob = client.get_blob_client(BLOB_CONTAINER, f"{ticker}.json")
        await blob.upload_blob(json.dumps(entry).encode(), overwrite=True)
    except Exception as e:
        logging.warning(f"blob write failed for {ticker}: {e}")

async def _fetch_from_provider(ticker: str) -> dict:
    """Alpha Vantage 또는 한국투자증권 API 호출"""
    # 실제 구현은 14장 데이터 수집 모듈 참조
    return {
        "ticker": ticker,
        "price_usd": 0,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def _ok_response(data: dict, ttl: int, source: str) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(data, ensure_ascii=False),
        status_code=200,
        mimetype="application/json",
        headers={
            "Cache-Control": f"public, max-age={ttl}, stale-while-revalidate=60",
            "X-Cache-Source": source,
            "Access-Control-Allow-Origin": "*"
        }
    )

def _error_response(status: int, msg: str) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"error": msg}),
        status_code=status,
        mimetype="application/json"
    )

def _is_market_closed_kst() -> bool:
    """KST 16:00~22:30은 한국·미국 모두 마감 시간대"""
    from datetime import datetime, timezone, timedelta
    kst = datetime.now(timezone.utc) + timedelta(hours=9)
    return 16 <= kst.hour < 22 or (kst.hour == 22 and kst.minute < 30)
```

### 4.3 Static Web Apps Routes 설정

`staticwebapp.config.json`을 저장소 루트에 배치하여 `/data/*` 요청을 Functions 백엔드로 프록시합니다.

```json
{
  "routes": [
    {
      "route": "/data/*",
      "rewrite": "/api/data/{ticker}",
      "allowedRoles": ["anonymous"]
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/data/*", "/api/*", "*.{json,css,js}"]
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/404.html"
    }
  },
  "globalHeaders": {
    "Access-Control-Allow-Origin": "*"
  }
}
```

> **중요**: Static Web Apps Free 플랜은 **Linked Backend 기능을 지원합니다**. Standard 플랜이 필요한 기능은 BYO Functions(이미 별도로 운영 중인 Functions 앱 연결)이고, Free 플랜에서는 SWA가 직접 프로비전하는 Managed Functions는 사용 가능합니다.

### 4.4 SWA Free 플랜 한계 점검

| 플랜 항목 | Free 플랜 | 본 용도 적합성 |
|---|---|---|
| 대역폭 | 100 GB/월 | 충분 (응답 1KB × 30만/월 = 300MB) |
| 사이트 수 | 무제한 | 무관 |
| 사용자 정의 도메인 | 2개 | 충분 |
| Managed Functions (linked) | 지원 | 본 용도 적합 |
| BYO Functions (linked external) | Standard 플랜 필요 | 별도 Functions 앱과 연결하려면 Standard 필요 |
| SLA | 없음 | MVP 단계 허용 가능 |
| 인증 (AAD, GitHub) | 지원 | 무관 |

**결론**: Free 플랜으로 시작 가능. Functions를 SWA의 Managed Functions로 함께 배포하는 구조면 추가 비용 없음. 별도로 Functions 앱을 두고 BYO 연결하려면 Standard ($9/월).

---

## 5. 비용 비교 (DAU 3,000 가정, 월 30만 호출)

| 항목 | A: SWA만 | B: SWA + Blob | C: SWA + Functions + Blob (권장) |
|---|---|---|---|
| Static Web Apps Free | $0 | $0 | $0 |
| GitHub Actions (빌드) | ~$0 (Free 플랜 내) | ~$0 | ~$0 |
| Azure Functions 실행 | $0 | $0 | $0~5 (월 25만 무료 초과분만) |
| Azure Functions 메모리 (GB-s) | $0 | $0 | $0~3 |
| Blob Storage (저장 + 트랜잭션) | $0 | $1~3 | $1~3 |
| 외부 API (Alpha Vantage 무료) | $0 | $0 | $0 |
| **합계 (월)** | **$0~3** | **$5~10** | **$5~15** |

C가 약간 비싸지만 **유연성·정확도·확장성에서 압도적**으로 유리합니다.

---

## 6. 정성 평가 — 권장 기준

본 프로젝트의 저비용 운영 원칙과 다른 요구사항을 종합 고려:

| 평가 차원 | 후보 A | 후보 B | 후보 C |
|---|---|---|---|
| 비용 | A+ | A | B+ |
| 정정도 (티커별 TTL) | C | A | A+ |
| 응답 속도 | A+ | A | A (메모리 hit), B (blob hit) |
| 운영 복잡도 | A+ | B+ | B |
| 확장성 (티커 5천개) | C | A | A+ |
| 신규 티커 즉시 처리 | F | A | A |
| 인스턴스 재시작 회복력 | A+ | A+ | A (Blob 백업으로 빠른 워밍) |
| 본 프로젝트 §8 적응형 캐싱과 정렬 | C | A | A+ |
| **종합 점수** | **B-** | **A-** | **A+** |

---

## 7. 단계별 도입 권장

본 프로젝트의 저비용 + 점진적 확장 원칙에 따라 다음 순서를 권장합니다.

### 단계 1: 인메모리만 (가장 단순)

```python
# Functions 인메모리 캐시만 사용, Blob 없이
# TTL: 30분 통일
# Hot ticker 사전 워밍 없음
```

이 단계는 **DAU 500까지** 충분합니다. 코드 30줄, Blob 비용 0원.

### 단계 2: Blob 백업 추가

인스턴스 재시작 시 콜드 스타트 영향이 거슬리기 시작하면 Blob 백업 추가. 코드 +30줄, 월 $1~3 추가.

### 단계 3: 핫 티커 사전 워밍 추가

Timer Trigger로 핫 티커 30개를 30분마다 미리 갱신. 사용자 첫 요청에서도 캐시 히트. 코드 +20줄.

### 단계 4: 적응형 TTL 도입

§8 적응형 캐싱의 시간대 군집 + 빈도 기반 TTL을 본 엔드포인트에도 적용.

각 단계는 이전 단계의 코드를 점진적으로 확장하므로 마이그레이션 부담 없음.

---

## 8. 모니터링과 관찰 가능성

### 8.1 응답 헤더로 캐시 출처 노출

응답에 `X-Cache-Source: memory | blob | origin` 헤더를 포함하여 디버깅과 통계 분석을 쉽게 합니다.

### 8.2 Application Insights 메트릭

다음 커스텀 메트릭을 추적합니다:

| 메트릭 | 의미 |
|---|---|
| `cache.memory.hit` | 인메모리 캐시 히트 횟수 |
| `cache.blob.hit` | Blob 캐시 히트 횟수 |
| `cache.miss` | 외부 API 호출 횟수 |
| `cache.refresh.scheduled` | Timer 갱신 성공 횟수 |
| `cache.refresh.failed` | Timer 갱신 실패 횟수 |
| `external_api.latency_ms` | 외부 API 응답 시간 |
| `external_api.errors` | 외부 API 오류 횟수 |

### 8.3 일일 보고

일 1회 자동 집계로 다음을 확인:

- 메모리 hit rate / Blob hit rate / origin call 비율
- 외부 API 호출 횟수 (Alpha Vantage 무료 한도 500/일 대비)
- 평균 응답 시간 (cache hit / miss 별로)
- 신규 티커 첫 요청 횟수

---

## 9. 다른 시스템 컴포넌트와의 관계

본 캐싱 아키텍처는 §8 적응형 캐싱(LLM 응답)과 별도이지만, 다음 패턴을 공유합니다:

| 구성 요소 | LLM 응답 (§8) | 티커 데이터 (본 문서) |
|---|---|---|
| 인메모리 캐시 | 9장 Semantic Cache | 본 문서 §2 |
| 영속 캐시 | CDN + Blob | Blob |
| 사전 워밍 | §8.2 시간대 군집 | §4.2 Hot ticker |
| TTL 정책 | 빈도 + 시간대 군집 | 핫/일반 + 마감시간 |
| 메트릭 | 13장 통계 대시보드 | 본 문서 §8.2 |

티커 데이터 캐싱은 LLM 캐싱보다 **단순**합니다. 의미적 동등성 판별이 필요 없고 (`NVDA`는 정확히 `NVDA`), 임베딩 비교가 불필요하기 때문입니다.

---

## 10. 결정 요약과 다음 단계

### 결정

- **권장 아키텍처**: 후보 C (Static Web Apps + Functions 인메모리 + Blob 백업)
- **시작 지점**: 단계 1 (인메모리만), 단순한 30줄 구현부터
- **확장 트리거**: 콜드 스타트 영향이 거슬릴 때 Blob 추가, 사용자 트래픽 패턴 확인 후 사전 워밍 추가
- **SWA 플랜**: Free로 시작 가능 (Managed Functions 활용), Standard 전환은 BYO Functions 필요할 때

### 다음 단계 후보

1. 단계 1 코드 스캐폴딩 작성 (`function_app.py` + `staticwebapp.config.json` + GitHub Actions 배포 워크플로)
2. Alpha Vantage / 한국투자증권 fetcher 통합 (14장 코드 재사용)
3. Application Insights 메트릭 대시보드 구성
4. 단계 2 (Blob 백업) 마이그레이션 계획
5. 핫 티커 리스트(`HOT_TICKERS`)를 동적으로 결정하는 로직 (최근 24시간 트래픽 기준)

---

**End of Document**
