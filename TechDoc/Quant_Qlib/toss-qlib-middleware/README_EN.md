# toss-qlib-middleware

> A Node.js/TypeScript middleware that bridges TOSS Securities Open API authentication (OAuth2) and market data retrieval into a [Microsoft Qlib](https://github.com/microsoft/qlib) pipeline. Redis is used for token caching and market data caching.
>
> 한국어 버전: [README.md](README.md)

For the overall design rationale, architecture, and Redis caching strategy, see the parent document:
[`../Qlib-getting-started-KR.md`](../Qlib-getting-started-KR.md) (Korean), section 7.4.

Deeper analysis of the TOSS Open API itself (full list of 20 endpoints, usage scenarios, design constraints) comes from this repo's [`Toss/`](../../../Toss) project:

- [`Toss/GUIDE.md`](../../../Toss/GUIDE.md) — setup/integration guide for a working TOSS Open API dashboard (Korean)
- [`Toss/src/toss.js`](../../../Toss/src/toss.js) — the actual auth/market-data client implementation (the basis for this middleware's endpoint paths and field parsing)
- [`Toss/docs/Toss_OpenAPI_Guide.md`](../../../Toss/docs/Toss_OpenAPI_Guide.md) — full 20-endpoint list, auth/token policy, usage scenarios, design constraints (Korean)

**This middleware's scope stops at authentication and market/instrument data retrieval. Order execution (trading) — creating, modifying, or cancelling orders — is intentionally not implemented.** See [`src/trading/README.md`](src/trading/README.md) for why and how to extend it.

---

## Why this exists

Qlib is a Python framework, but all Qlib actually needs is data in its expected CSV shape. This middleware fetches quotes from the TOSS Securities Open API, normalizes them into Qlib's CSV convention (`date,open,high,low,close,volume,symbol,factor`), and hands them off to `dump_bin.py`.

```
TOSS Open API  --OAuth2-->  [Node.js/TS middleware]  --CSV(csv_kr/*.csv)-->  scripts/dump_bin.py  -->  ~/.qlib/qlib_data/kr_data
                                   |
                                 Redis (token cache + market data cache)
```

## Authentication (confirmed spec)

| Item | Detail |
| :--- | :--- |
| Flow | OAuth2 Client Credentials Grant |
| Token issuance | `POST {TOSS_BASE_URL}/oauth2/token` — `grant_type`, `client_id`, `client_secret` sent as a **form-urlencoded body** (not Basic Auth) |
| Lifetime | 86,400 seconds (24h), **no refresh token** — you must re-issue with the client secret before expiry yourself |
| Call header | `Authorization: Bearer {access_token}` |
| Account/order APIs | require an additional `X-Tossinvest-Account` header (not called by this middleware) |

`scripts/setup.sh` generates `.env` interactively and can immediately test-issue a real token (see Quick Start below).

## Quick Start

```bash
cd TechDoc/Quant_Qlib/toss-qlib-middleware
npm install
npm run setup       # interactively creates .env, optionally test-issues a token
npm run typecheck
npm test             # passes without a Redis server (in-memory adapter validates the logic)
npm run dev            # http://localhost:4000, requires a real Redis instance
```

Without the setup script:

```bash
cp .env.example .env   # fill in TOSS_CLIENT_ID / TOSS_CLIENT_SECRET
chmod 600 .env
```

## Redis caching strategy

| Cached item | Key | TTL | Reason |
| :--- | :--- | :--- | :--- |
| Access token | `toss:access_token` | `86400 - safety margin (default 1h)` | No refresh token, so re-issue well before expiry |
| Token refresh lock | `toss:access_token:lock` | 10s (`SET NX`) | Prevents a thundering herd of simultaneous re-issue requests |
| Finalized past candles | `toss:candles:{symbol}:{interval}:{start}:{end}` | 1 day | Closed candles never change |
| Today's (unfinalized) candles | same key pattern | 30s (default) | Values keep updating intraday |
| Current price | `toss:price:{symbol}` | 5s (default) | Needs freshness; cached per symbol so batch requests reuse hits |

On a 401, the cache is invalidated and the request is retried once; on 429 (rate limit), it backs off based on the `Retry-After` header and retries.

## API and candle pagination

The TOSS candles endpoint returns at most 200 rows per request (`count`) and has no `start`/`end` filter. This middleware paginates backward from the most recent candle using a `before` cursor until it reaches the target start date, then returns the merged result sorted ascending (same strategy as `fetchCandles` in `Toss/src/toss.js`).

| Method | Path | Description |
| :--- | :--- | :--- |
| GET | `/health` | Health check |
| GET | `/api/candles/:symbol?start=&end=&interval=day` | Normalized candle JSON (Redis-cached, built-in `before` pagination) |
| GET | `/api/prices?symbols=005930,000660` | Batch current-price lookup (comma-separated, chunked at 200) |
| POST | `/api/export/qlib` `{symbols, start, end, outDir?}` | Fetches multiple symbols and writes `csv_kr/{symbol}.csv` |

To export CSV directly without running the server:

```bash
npm run export:qlib -- --symbols 005930,000660 --start 2020-01-01 --end 2026-07-01
```

Feed the generated CSV straight into the conversion command from section 7.2 of the Qlib guide:

```bash
python scripts/dump_bin.py dump_all \
    --csv_path ./csv_kr \
    --qlib_dir ~/.qlib/qlib_data/kr_data \
    --include_fields open,close,high,low,volume,factor \
    --date_field_name date --symbol_field_name symbol
```

## Why trading (order execution) is out of scope

Authentication and market data retrieval are common needs that are nearly identical for everyone, so building shared middleware for them makes sense. Order logic — order-state tracking, avoiding duplicate orders on retry, risk limits, fill confirmation — varies completely by each person's strategy and risk tolerance, so building it generically would be irresponsible. See [`src/trading/README.md`](src/trading/README.md) for how to extend it yourself.

## Project layout

```
src/
  config.ts              env var loading (lazily evaluated)
  types.ts                TOSS response / Qlib CSV types
  cache/
    redisPort.ts          Redis dependency abstraction
    ioredisAdapter.ts      production implementation (ioredis)
    memoryAdapter.ts        in-memory implementation for tests/local dev
  auth/tokenService.ts     OAuth2 token issuance + Redis cache + refresh lock
  market/
    tossClient.ts          authenticated HTTP client (401/429 handling)
    marketDataService.ts    candle fetch + before-cursor pagination + Redis cache
    priceService.ts        batch current-price fetch + per-symbol cache
    qlibExport.ts          writes Qlib's CSV convention
  trading/README.md         order-execution extension point (unimplemented)
  server.ts / index.ts / cli.ts
scripts/setup.sh            interactive .env generator + token test
test/                       node:test unit tests (no Redis required)
llms.txt                    summary index for AI agents / search
```

## Tests

```bash
npm test
```

Validates token caching/refresh locking, candle pagination and sorting, price caching, and the Qlib CSV format — all via the in-memory adapter, no Redis server required.

## Limitations and caveats

- **Not investment advice.** This is a market-data middleware; investment decisions and their consequences are the user's own responsibility.
- As of June 2026, TOSS Open API is in a pre-registration phase with no confirmed public launch date (see `Toss/docs/Toss_OpenAPI_Guide.md`). Endpoint paths and response schemas may change, which is why they're all environment variables here.
- The exact field names in candle responses (OHLC/volume) couldn't be cross-checked against the raw OpenAPI spec, so parsing defensively accepts several candidate keys. Once you have real responses, consider narrowing `RawTossCandle`/`RawTossPrice` in `src/types.ts`.
- Exact rate limit numbers are unconfirmed — only `Retry-After`-based backoff on 429 is implemented.

---

**Original Qlib guide**: [`../Qlib-getting-started-KR.md`](../Qlib-getting-started-KR.md) · **Reference TOSS Open API project**: [`Toss/`](../../../Toss) · MIT License
