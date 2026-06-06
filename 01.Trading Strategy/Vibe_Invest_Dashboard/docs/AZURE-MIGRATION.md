# Azure 이식 & 호환성 체크리스트

> 라이브 대시보드를 **Azure Static Web Apps(SWA) + Azure Functions + Blob** 기반으로 운영.
> 이 문서는 "현재 코드가 Azure에 맞는가"를 지속 점검하는 기준. (원본은 Cloudflare Pages/Workers 타깃)

## 0. 한 줄 결론
**프론트 + `shared/`는 그대로, 백엔드(API·크론·저장소)는 Cloudflare 전용이라 포팅 필요.**

---

## 1. 그대로 가는 것 (✅ Azure 호환)
| 경로 | 비고 |
|---|---|
| `frontend/` | 정적. SWA가 서빙. **`fetch('/api/*')` 상대경로** → SWA가 동일 오리진 Functions로 라우팅 → 무수정. esbuild 빌드 동일 |
| `shared/strategy/**`, `shared/symbols.ts`, `frontend/src/saju.ts` | 순수 TS, 프레임워크 비의존 |
| `shared/ingest.ts`, `shared/hash.ts` | `crypto.subtle` → Node 20 내장(`globalThis.crypto`)이라 Azure Functions(Node)에서 동작 |
| `shared/http.ts` 의 envelope/캐시 로직 | 단, `new Response()` 생성부는 Azure 응답형식으로 감싸야 함 |

> **원칙(앞으로)**: 신규 기능은 **frontend/(상대 /api/*) + shared/(순수 TS)** 에 두면 Azure 호환 유지.
> 플랫폼 의존(저장소·요청/응답)은 얇은 어댑터로 분리.

---

## 2. 포팅 필요 (❌ Cloudflare 전용)
| 현재 | Azure 대응 | 작업 |
|---|---|---|
| `functions/api/*.ts` (`PagesFunction`, `onRequestGet`, `ctx.env`) | **SWA 관리형 Azure Functions(HTTP, Node v4)** — `api/` 폴더 | 라우트 `/api/*` 동일. 핸들러는 `shared/` 로직 호출 + 응답 어댑터 |
| `cron-worker/**` (`scheduled`) | **Azure Functions Timer (별도 Function App)** | ⚠️ SWA 관리형 Functions는 **HTTP 전용·Timer 불가** → 크론은 반드시 별도 앱 |
| `ctx.env.SNAPSHOTS` (R2 `.get/.put`) | **Azure Blob** (`@azure/storage-blob` + `DefaultAzureCredential`) | AIInvestor `services/usage_logger.py` 패턴 재사용 |
| `ctx.env.DB` (D1 `prepare/bind/all/first/batch`) | **Blob JSON**(권장, 단순) 또는 Azure Table/Cosmos | §4 매핑 |
| `wrangler.toml` ×2, `package.json` wrangler 스크립트 | `staticwebapp.config.json` + `host.json` + SWA/Functions 설정 | |

---

## 3. API 엔드포인트 계약 (Azure Functions가 맞춰야 할 것)
모두 `GET`(쓰기 제외) + envelope `{ data, updated_at, disclaimer }`. 프론트는 이 형식을 기대.

| 경로 | 읽는 곳(현재 R2/D1) | Azure 소스 | 캐시 |
|---|---|---|---|
| `GET /api/dashboard` | R2 `signals/latest.json` | Blob 동일 | 60s |
| `GET /api/market` | R2 `market-latest.json` | Blob 동일 | 120s |
| `GET /api/movers` | D1 `movers` 최신 ts | Blob `movers-latest.json`(이미 크론이 생성) | 1800s |
| `GET /api/news?limit` | D1 `news_summary` + `market_summary` | Blob/Table | 300s |
| `GET /api/rankings` | D1 `rankings` | Blob/Table | 300s |
| `GET /api/search?q` | D1 `signals`(읽기) + `searches`(쓰기) | Blob/Table | no-store |
| `POST /api/track` | D1 `daily_users`/`all_users` 카운트 | Table(권장) | no-store |
| `POST /api/ingest/news` | HMAC 검증 → D1 저장 | `shared/ingest.ts` 재사용 + Blob 저장 | — |

> **HMAC ingest 계약**(`docs/PROMPT-azure-news.md` §ingest 계약)은 플랫폼 무관 — Azure Function에서도 동일하게 검증.
> `CF_INGEST_URL`(AIInvestor 측)을 **SWA의 `/api/ingest/news` URL**로 교체만 하면 됨.

---

## 4. D1 → Azure 저장소 매핑 (무료 우선)
가장 단순: **D1 폐기, 전부 Blob JSON**(AIInvestor 방식). 주기 데이터는 이미 R2 JSON.

| D1 테이블 | Azure |
|---|---|
| `market_snapshot`/`signals` 스냅샷 | Blob `signals/latest.json`, `market-latest.json` (이미 존재) |
| `movers` | Blob `movers-latest.json` (이미 크론이 생성) |
| `news_summary`, `market_summary` | Blob `news/latest.json` (ingest가 기록) |
| `rankings` | Blob `rankings/<date>.json` |
| `searches`(검색로그) | Blob append 또는 Azure Table |
| `daily_users`/`all_users`(DAU) | **Azure Table**(파티션=date, row=user_hash → COUNT) 권장 |
| `stats_cache` | Blob `stats.json` |

크론(`signals.ts`/`daily.ts`/`market.ts`)의 `persist*`만 Blob/Table 클라이언트로 교체. **계산 로직은 그대로.**

---

## 5. 크론 (별도 Timer Function App)
- `runMarketSnapshot` → 10분 Timer (`0 */10 * * * *`)
- `runDailySignals` + `runMoversSnapshot` → 미 장마감 후 1회 Timer (`0 30 21 * * 1-5`)
- 데이터 수집(`providers/yahoo.ts`, `fred.ts`)은 `fetch` 기반 → Node 그대로.
- AIInvestor(Python) 옆에 **별도 Node Function App**으로 두거나, 같은 리소스그룹.

---

## 6. 시크릿
| 키 | Azure 위치 |
|---|---|
| `INGEST_SECRET`(Azure 뉴스와 공유), `USER_HASH_SALT` | SWA/Function App **Application settings** 또는 Key Vault |
| (데이터 소스는 키리스: Yahoo/FRED) | — |

---

## 7. 지금 즉시 점검 결과 (2026-06)
- [x] 프론트 상대 `/api/*` → SWA 호환. 푸터 "Cloudflare Pages" → **"Microsoft Azure"** 수정함.
- [ ] `api/` (Azure Functions) 미존재 → **라이브 SWA의 `/api/*`는 현재 404 추정**(데이터 빈 화면). API 포팅 필요.
- [ ] `staticwebapp.config.json`(라우팅/`navigationFallback: /index.html`) 미존재.
- [ ] 크론 Timer Function App 미존재 → 스냅샷 미생성.
- [ ] Blob/Table 어댑터 미작성.

> 결론: **프론트는 떠도 데이터는 안 채워짐.** API(Azure Functions)+크론(Timer)+Blob을 올려야 완성.
> 다음 단계로 `api/` Azure Functions 스캐폴드 + Blob 어댑터를 원하면 만들어줄게.
