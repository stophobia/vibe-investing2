# 토스증권 Open API — Getting Started

> 작성일: 2026-06-19 | API 버전: v1.0.3 | 실전 구현 경험 기반

한 줄 요약: TOSS 증권 API는 깔끔하고 서버 백엔드 단에 FDS와 보안 장비가 비교적 잘 구축되어 있었다. 문서 역시 가독성이 좋았다. 붙이는데 큰 시간이 걸리지 않았다. 실제 트레이딩까지 구현과 백테스트, 모의 테스트까지 3~5일 이내 완료될 수준이다.

---

## 목차

1. [서비스 개요](#1-서비스-개요)
2. [API 핵심 특징](#2-api-핵심-특징)
3. [빠른 시작 (Quick Start)](#3-빠른-시작-quick-start)
4. [실전에서 실수하기 쉬운 함정들](#4-실전에서-실수하기-쉬운-함정들)
5. [TypeScript 예제](#5-typescript-예제)
6. [Python 예제](#6-python-예제)
7. [전체 엔드포인트 레퍼런스](#7-전체-엔드포인트-레퍼런스)

---

## 1. 서비스 개요

토스증권 Open API는 국내주식과 미국주식을 **단일 REST 인터페이스**로 다루는 통합 API입니다.

![TOSS x Vibe Invest 대시보드](../images/Toss_vibe_01.png)

| 항목 | 내용 |
|---|---|
| Base URL | `https://openapi.tossinvest.com` |
| 인증 방식 | OAuth 2.0 Client Credentials Grant |
| 지원 시장 | 국내주식, 미국주식 (선물옵션·채권 미지원) |
| 프로토콜 | REST only (WebSocket 미지원) |
| 개발자 문서 | https://developers.tossinvest.com/docs |
| API 키 발급 | 토스증권 PC 웹사이트 → 개발자 설정 |

---

## 2. API 핵심 특징

### 2.1 인증 — OAuth2 Client Credentials

토큰은 **24시간** 유효하며 **Refresh Token이 없습니다.**

```
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=tsck_live_xxxxx
&client_secret=tssk_live_xxxxx
```

응답:
```json
{
  "access_token": "eyJraWQi...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

이후 모든 요청 헤더에 포함:
```
Authorization: Bearer {access_token}
```

### 2.2 응답 구조 — `result` 키가 루트

**모든 엔드포인트의 최상위 키는 `result`입니다.**
`data`, `response`, `body` 같은 이름이 아닙니다.

```json
// 현재가 응답
{ "result": [ { "symbol": "005930", "lastPrice": "352500", "currency": "KRW" } ] }

// 캔들 응답
{ "result": { "candles": [ {...}, {...} ], "nextBefore": "2026-06-17T00:00:00.000+09:00" } }
```

### 2.3 가격은 모두 문자열(String)

API가 반환하는 모든 가격 값은 **문자열**입니다. 반드시 숫자로 변환해야 합니다.

```typescript
//  틀림
const price = data.lastPrice;          // "352500" — 문자열

//  올바름
const price = parseFloat(data.lastPrice);  // 352500 — 숫자
```

### 2.4 변동률(changeRate)은 API에 없다

현재가 엔드포인트는 `lastPrice`만 반환합니다. `changeRate`, `change` 필드가 없습니다.
변동률이 필요하면 **캔들 2일치**를 가져와 직접 계산해야 합니다.

```typescript
// 오늘 종가 vs 전일 종가 → 변동률 계산
const candles = await getCandles(symbol, 2);
const today = candles[0].closePrice;
const yesterday = candles[1].closePrice;
const changeRate = ((today - yesterday) / yesterday) * 100;
```

### 2.5 종목 코드 형식

| 시장 | 형식 | 예시 |
|---|---|---|
| 국내주식 | 6자리 숫자 | `005930` (삼성전자) |
| 국내 ETF | 6자리 숫자 | `069500` (KODEX 200) |
| 미국주식 | 티커 문자 | `AAPL`, `NVDA`, `TSLA` |
| 미국 ETF | 티커 문자 | `SPY`, `QQQ`, `TQQQ` |

---

## 3. 빠른 시작 (Quick Start)

### Step 1 — 토큰 발급

```bash
curl -X POST "https://openapi.tossinvest.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET"
```

### Step 2 — 현재가 조회

```bash
# 삼성전자 + AAPL 동시 조회 (쉼표 구분, 최대 200개)
curl "https://openapi.tossinvest.com/api/v1/prices?symbols=005930,AAPL" \
  -H "Authorization: Bearer {access_token}"
```

응답:
```json
{
  "result": [
    { "symbol": "005930", "timestamp": "2026-06-19T18:40:05.000+09:00", "lastPrice": "352500", "currency": "KRW" },
    { "symbol": "AAPL",   "timestamp": "2026-06-19T08:59:51.000+09:00", "lastPrice": "297.2001", "currency": "USD" }
  ]
}
```

### Step 3 — 캔들(일봉) 조회

```bash
curl "https://openapi.tossinvest.com/api/v1/candles?symbol=005930&interval=1d&count=5" \
  -H "Authorization: Bearer {access_token}"
```

응답:
```json
{
  "result": {
    "candles": [
      {
        "timestamp": "2026-06-19T00:00:00.000+09:00",
        "openPrice": "380000",
        "highPrice": "380000",
        "lowPrice": "346000",
        "closePrice": "353000",
        "volume": "75059244",
        "currency": "KRW"
      }
    ],
    "nextBefore": "2026-06-14T00:00:00.000+09:00"
  }
}
```

---

## 4. 실전에서 실수하기 쉬운 함정들

실제 `TOSS x Vibe Invest` 대시보드를 구현하며 겪은 실수들을 정리했습니다.

![실시간 미국주식 대시보드](../images/Toss_vibe_02.png)

---

### 함정 1 — 응답 루트 키를 잘못 가정

가장 흔한 실수. `data`, `prices`, `stocks` 등 일반적인 키 이름을 예상하다가 빈 데이터를 받게 됩니다.

```typescript
//  이렇게 하면 undefined
const items = response.data ?? response.prices ?? [];

//  실제 응답 키는 result
const items = response.result ?? [];
```

캔들은 한 단계 더 깊습니다:
```typescript
//  틀림
const candles = response.result ?? [];

//  올바름
const candles = response.result?.candles ?? [];
```

---

### 함정 2 — 가격 값을 숫자로 착각

```typescript
//  이렇게 하면 계산 결과가 문자열 연결됨
const change = item.lastPrice - item.prevClose;  // NaN 또는 "352500-363500"

//  parseFloat 필수
const price = parseFloat(item.lastPrice);
const prev  = parseFloat(candle.closePrice);
const change = price - prev;  // -11000
```

---

### 함정 3 — 변동률을 prices API에서 찾음

prices 엔드포인트에는 변동률 데이터가 없습니다.

```typescript
//  없는 필드를 참조하면 항상 0
const changeRate = item.changeRate ?? 0;  // 항상 0

//  캔들 2일치로 직접 계산
async function getChangeRate(symbol: string): Promise<number> {
  const res = await fetch(`/api/v1/candles?symbol=${symbol}&interval=1d&count=2`, ...);
  const candles = res.result.candles;
  if (candles.length < 2) return 0;
  const today = parseFloat(candles[0].closePrice);
  const yesterday = parseFloat(candles[1].closePrice);
  return ((today - yesterday) / yesterday) * 100;
}
```

---

### 함정 4 — 토큰 24시간 후 자동 만료

Refresh Token이 없으므로 만료 후에는 재발급 로직이 없으면 401 에러가 계속 발생합니다.

```typescript
//  만료 1시간 전 선제 재발급 패턴
let cachedToken: { access_token: string; issued_at: number; expires_in: number } | null = null;

async function getToken(): Promise<string> {
  const now = Date.now() / 1000;
  // 만료 3600초(1시간) 전에 갱신
  if (cachedToken && now < cachedToken.issued_at + cachedToken.expires_in - 3600) {
    return cachedToken.access_token;
  }
  const data = await issueNewToken();
  cachedToken = { ...data, issued_at: now };
  return cachedToken.access_token;
}
```

---

### 함정 5 — Upstash Redis REST URL 형식 오류

Upstash Redis를 쓸 때 redis-cli 연결 문자열을 REST URL로 혼동하면 즉시 에러가 납니다.

```bash
# redis-cli 연결 문자열 — REST 클라이언트에서 사용 불가
UPSTASH_REDIS_REST_URL=redis-cli --tls -u redis://default:TOKEN@host:6379

# Upstash REST URL — https:// 로 시작해야 함
UPSTASH_REDIS_REST_URL=https://pet-sturgeon-119990.upstash.io
```

Upstash 콘솔(console.upstash.com) → 데이터베이스 선택 → **REST API** 탭에서 올바른 URL을 확인하세요.

---

### 함정 6 — Next.js 15의 serverComponentsExternalPackages 위치 변경

Next.js 15부터 `experimental.serverComponentsExternalPackages`가 최상위로 이동했습니다.

```typescript
//  Next.js 14 이하 방식 — 경고 + 무시됨
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ["@neondatabase/serverless"],
  },
};

//  Next.js 15 방식
const nextConfig = {
  serverExternalPackages: ["@neondatabase/serverless"],
};
```

---

### 함정 7 — 캔들 interval은 `1d`와 `1m`만 지원

3분봉, 5분봉, 15분봉은 없습니다. 중간 주기가 필요하면 1분봉을 직접 리샘플링해야 합니다.

```typescript
//  지원 안 됨
interval=5m
interval=15m
interval=1h

//  지원되는 값
interval=1m   // 1분봉
interval=1d   // 일봉
```

---

### 함정 8 — 배치 조회 시 심볼 구분자

여러 종목을 한 번에 조회할 때 구분자는 쉼표(`,`)이며 공백 없이 붙여야 합니다.

```bash
# 공백 포함 시 파싱 오류 가능
?symbols=005930, 000660, AAPL

# 공백 없이
?symbols=005930,000660,AAPL
```

---

## 5. TypeScript 예제

### 전체 클라이언트 구현 (Next.js / Node.js)

```typescript
// lib/toss-client.ts

const BASE_URL = "https://openapi.tossinvest.com";

interface TokenCache {
  access_token: string;
  expires_in: number;
  issued_at: number;
}

let tokenCache: TokenCache | null = null;

// ── 토큰 발급 (자동 캐시 + 재발급) ──────────────────────────
async function getToken(): Promise<string> {
  const clientId = process.env.TOSS_CLIENT_ID!;
  const clientSecret = process.env.TOSS_CLIENT_SECRET!;

  const now = Date.now() / 1000;
  if (tokenCache && now < tokenCache.issued_at + tokenCache.expires_in - 3600) {
    return tokenCache.access_token;
  }

  const res = await fetch(`${BASE_URL}/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });

  if (!res.ok) throw new Error(`토큰 발급 실패: ${await res.text()}`);

  const data = await res.json();
  tokenCache = { ...data, issued_at: now };
  return tokenCache!.access_token;
}

async function get(path: string, params: Record<string, string> = {}) {
  const token = await getToken();
  const url = new URL(`${BASE_URL}${path}`);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error(`API 오류 (${res.status}): ${await res.text()}`);
  return res.json();
}

// ── 현재가 조회 (최대 200개 배치) ────────────────────────────
export interface StockPrice {
  symbol: string;
  price: number;       // parseFloat(lastPrice)
  currency: "KRW" | "USD";
  timestamp: string;
}

export async function getPrices(symbols: string[]): Promise<StockPrice[]> {
  if (symbols.length === 0) return [];

  // 200개씩 배치 처리
  const chunks: string[][] = [];
  for (let i = 0; i < symbols.length; i += 200) {
    chunks.push(symbols.slice(i, i + 200));
  }

  const results = await Promise.all(
    chunks.map((chunk) => get("/api/v1/prices", { symbols: chunk.join(",") }))
  );

  return results.flatMap((r) =>
    (r.result as Array<{ symbol: string; lastPrice: string; currency: string; timestamp: string }>)
      .map((item) => ({
        symbol: item.symbol,
        price: parseFloat(item.lastPrice),   //  문자열 → 숫자 변환 필수
        currency: item.currency as "KRW" | "USD",
        timestamp: item.timestamp,
      }))
  );
}

// ── 캔들(일봉) 조회 ───────────────────────────────────────────
export interface Candle {
  time: string;  // "2026-06-19"
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export async function getCandles(symbol: string, count = 60): Promise<Candle[]> {
  const data = await get("/api/v1/candles", {
    symbol,
    interval: "1d",
    count: String(Math.min(count, 200)),
  });

  //  result.candles — result[] 아님
  const items = data.result?.candles ?? [];
  return items.map((c: Record<string, string>) => ({
    time: c.timestamp.split("T")[0],
    open: parseFloat(c.openPrice),
    high: parseFloat(c.highPrice),
    low: parseFloat(c.lowPrice),
    close: parseFloat(c.closePrice),
    volume: parseInt(c.volume, 10),
  }));
}

// ── 변동률 계산 (API에 없으므로 캔들로 직접 계산) ─────────────
export async function getPriceWithChange(symbol: string) {
  const [prices, candles] = await Promise.all([
    getPrices([symbol]),
    getCandles(symbol, 2),
  ]);

  const price = prices[0]?.price ?? 0;
  const todayClose = candles[0]?.close ?? price;
  const prevClose = candles[1]?.close ?? todayClose;

  const change = price - prevClose;
  const changeRate = prevClose > 0 ? (change / prevClose) * 100 : 0;

  return { symbol, price, change, changeRate };
}

// ── 환율 조회 ─────────────────────────────────────────────────
export async function getExchangeRate(): Promise<number> {
  const data = await get("/api/v1/exchange-rate");
  const r = data.result ?? data;
  return parseFloat(r.rate ?? r.usdKrw ?? "1380");
}
```

### 사용 예시

```typescript
// 삼성전자, SK하이닉스, AAPL 현재가 일괄 조회
const prices = await getPrices(["005930", "000660", "AAPL"]);
console.log(prices);
// [
//   { symbol: "005930", price: 352500, currency: "KRW", timestamp: "..." },
//   { symbol: "000660", price: 2778000, currency: "KRW", timestamp: "..." },
//   { symbol: "AAPL",   price: 297.2,  currency: "USD", timestamp: "..." },
// ]

// 삼성전자 변동률 포함 조회
const { price, changeRate } = await getPriceWithChange("005930");
console.log(`삼성전자: ${price.toLocaleString()}원 (${changeRate:+.2f}%)`);
// 삼성전자: 352,500원 (-3.03%)

// 60일 캔들
const candles = await getCandles("NVDA", 60);
console.log(candles[0]);
// { time: "2026-06-19", open: 208, high: 215, low: 207, close: 210, volume: 45000000 }
```

---

## 6. Python 예제

```python
# toss_client.py
import time
import requests

BASE_URL = "https://openapi.tossinvest.com"

class TossClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None
        self._token_issued_at: float = 0
        self._token_expires_in: int = 86400

    # ── 토큰 발급 (자동 재발급) ─────────────────────────────────
    def get_token(self) -> str:
        now = time.time()
        # 만료 1시간 전 갱신
        if self._token and now < self._token_issued_at + self._token_expires_in - 3600:
            return self._token

        res = requests.post(
            f"{BASE_URL}/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        res.raise_for_status()
        data = res.json()

        self._token = data["access_token"]
        self._token_expires_in = data.get("expires_in", 86400)
        self._token_issued_at = now
        return self._token

    def _get(self, path: str, params: dict = {}) -> dict:
        headers = {"Authorization": f"Bearer {self.get_token()}"}
        res = requests.get(f"{BASE_URL}{path}", headers=headers, params=params)
        res.raise_for_status()
        return res.json()

    # ── 현재가 조회 ─────────────────────────────────────────────
    def get_prices(self, symbols: list[str]) -> list[dict]:
        """
        반환: [{"symbol": "005930", "price": 352500.0, "currency": "KRW"}, ...]
        주의: lastPrice는 문자열 → float 변환 필수
        """
        # 200개씩 배치
        results = []
        for i in range(0, len(symbols), 200):
            chunk = symbols[i:i + 200]
            data = self._get("/api/v1/prices", {"symbols": ",".join(chunk)})
            #  루트 키는 result
            for item in data.get("result", []):
                results.append({
                    "symbol": item["symbol"],
                    "price": float(item["lastPrice"]),   #  문자열 → float
                    "currency": item["currency"],
                    "timestamp": item["timestamp"],
                })
        return results

    # ── 캔들(일봉) 조회 ─────────────────────────────────────────
    def get_candles(self, symbol: str, count: int = 60) -> list[dict]:
        """
        반환: [{"time": "2026-06-19", "open": 380000, "close": 353000, ...}, ...]
        주의: result.candles — result[] 아님
        """
        data = self._get("/api/v1/candles", {
            "symbol": symbol,
            "interval": "1d",
            "count": str(min(count, 200)),
        })
        #  result.candles 경로
        candles = data.get("result", {}).get("candles", [])
        return [
            {
                "time": c["timestamp"][:10],
                "open":   float(c["openPrice"]),    #  모두 문자열
                "high":   float(c["highPrice"]),
                "low":    float(c["lowPrice"]),
                "close":  float(c["closePrice"]),
                "volume": int(c["volume"]),
            }
            for c in candles
        ]

    # ── 변동률 계산 ─────────────────────────────────────────────
    def get_change_rate(self, symbol: str) -> dict:
        """
        prices API에 변동률이 없으므로 캔들 2일치로 계산
        """
        prices = self.get_prices([symbol])
        candles = self.get_candles(symbol, count=2)

        current = prices[0]["price"] if prices else 0
        prev_close = float(candles[1]["close"]) if len(candles) >= 2 else current

        change = current - prev_close
        change_rate = (change / prev_close * 100) if prev_close else 0

        return {
            "symbol": symbol,
            "price": current,
            "change": change,
            "change_rate": change_rate,
        }

    # ── 환율 조회 ────────────────────────────────────────────────
    def get_exchange_rate(self) -> float:
        data = self._get("/api/v1/exchange-rate")
        r = data.get("result", data)
        return float(r.get("rate") or r.get("usdKrw") or 1380)


# ── 사용 예시 ───────────────────────────────────────────────────
if __name__ == "__main__":
    import os

    client = TossClient(
        client_id=os.environ["TOSS_CLIENT_ID"],
        client_secret=os.environ["TOSS_CLIENT_SECRET"],
    )

    # 현재가 일괄 조회
    prices = client.get_prices(["005930", "000660", "AAPL", "NVDA"])
    for p in prices:
        print(f"{p['symbol']}: {p['price']:,.2f} {p['currency']}")

    # 삼성전자 변동률
    result = client.get_change_rate("005930")
    print(f"\n삼성전자: {result['price']:,.0f}원  {result['change_rate']:+.2f}%")

    # 60일 캔들
    candles = client.get_candles("005930", count=60)
    print(f"\n최근 종가: {candles[0]['close']:,.0f}원 ({candles[0]['time']})")

    # 환율
    rate = client.get_exchange_rate()
    print(f"\nUSD/KRW: {rate:,.0f}원")
```

---

## 7. 전체 엔드포인트 레퍼런스

| # | 엔드포인트 | 메서드 | 설명 | 주요 파라미터 |
|---|---|---|---|---|
| 1 | `/oauth2/token` | POST | 액세스 토큰 발급 | `client_id`, `client_secret` |
| 2 | `/api/v1/accounts` | GET | 보유 계좌 목록 | — |
| 3 | `/api/v1/holdings` | GET | 보유 종목 조회 | — |
| 4 | `/api/v1/prices` | GET | **현재가** (최대 200개) | `symbols` (쉼표 구분) |
| 5 | `/api/v1/orderbook` | GET | 호가 조회 | `symbol` |
| 6 | `/api/v1/trades` | GET | 체결 내역 | `symbol` |
| 7 | `/api/v1/candles` | GET | **캔들** (1d / 1m만 지원) | `symbol`, `interval`, `count` |
| 8 | `/api/v1/stocks` | GET | 종목 기본정보 | `symbols` |
| 9 | `/api/v1/price-limits` | GET | 상·하한가 | `symbol` |
| 10 | `/api/v1/market-calendar/KR` | GET | 국내 시장 캘린더 | `date` |
| 11 | `/api/v1/market-calendar/US` | GET | 미국 시장 캘린더 | `date` |
| 12 | `/api/v1/exchange-rate` | GET | **환율** (USD/KRW) | — |
| 13 | `/api/v1/buying-power` | GET | 매수 가능 금액 | — |
| 14 | `/api/v1/sellable-quantity` | GET | 매도 가능 수량 | `symbol` |
| 15 | `/api/v1/commissions` | GET | 수수료 조회 | `symbol` |
| 16 | `/api/v1/orders` | POST | **주문 생성** | `symbol`, `side`, `orderType`, `quantity`, `price` |
| 17 | `/api/v1/orders/{id}/modify` | POST | 주문 정정 | `price`, `quantity` |
| 18 | `/api/v1/orders/{id}/cancel` | POST | 주문 취소 | — |
| 19 | `/api/v1/orders` | GET | 주문 목록 조회 | `status` (OPEN/CLOSED) |
| 20 | `/api/v1/orders/{id}` | GET | 개별 주문 조회 | — |

---

## 참고 자료

- 토스증권 개발자 센터: https://developers.tossinvest.com/docs
- OpenAPI 스펙 (JSON): https://openapi.tossinvest.com/openapi-docs/latest/openapi.json
- 실전 구현 예시 (이 레포): [toss-dashboard/](../../toss-dashboard/)
- 이 문서의 원본 분석: [Toss_OpenAPI_Guide.md](./Toss_OpenAPI_Guide.md)

---

> **면책고지:** 이 문서는 실전 구현 경험을 바탕으로 작성됐습니다. API 스펙은 변경될 수 있으므로 공식 문서를 병행 참조하세요.
> 투자 판단의 책임은 본인에게 있습니다.

