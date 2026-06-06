# Vibe Investing Dashboard

> 프로젝트 루트. 작업 시 이 파일을 먼저 읽고 규칙을 지킬 것.
> 전체 기획·화면 가이드: [`VIBE-INVESTING-DEV-GUIDE.md`](./VIBE-INVESTING-DEV-GUIDE.md)
> 전략 분석(룰 포팅 근거): [`docs/STRATEGY-ANALYSIS.md`](./docs/STRATEGY-ANALYSIS.md)

## 목표
기존 퀀트 전략의 룰 기반 시그널을 단일 웹 대시보드로 통합한다.
**"LLM은 엑셀이지 오라클이 아니다"** — 모든 시그널은 룰 기반, LLM(DeepSeek)은 뉴스 요약 전용.

> 🚩 **1차 출시 = ARDS + AMQS 2개만**. MU_Hynix 는 1차 제외(Phase 2 보류) —
> SK하이닉스 KRX 소스 미해결 + statsmodels(ADF) 포팅 난점. 사유·재개 점검은 `docs/STRATEGY-ANALYSIS.md`.

## 스택 (아키텍처 결정 2026-06-06)
> 가이드 원문은 단일 Workers(+static assets)였으나, **웹=Cloudflare Pages** 방침으로 변경.
> Pages 는 Cron Trigger 를 지원하지 않으므로 **크론만 별도 Worker** 로 분리한다.
- **Cloudflare Pages**: 정적 프론트 + **Pages Functions**(`functions/api/*` = HTTP API, 프론트와 동일 오리진)
- **Cron Worker**(`cron-worker/`): 스케줄 작업 전용(10분 + 일1회). Pages 가 못 하는 부분만.
- **D1**(SQLite) + **R2**(스냅샷): Pages·Cron Worker 양쪽에 동일 리소스 바인딩 → 데이터 공유
- **뉴스 요약**: AIInvestor(Python Azure Functions) 앱에 통합 → `/api/ingest/news` 로 전송(`docs/PROMPT-azure-news.md`)
- **프론트**: vanilla TS + 단일 번들 (빌드: esbuild), 차트는 경량 SVG 직접 렌더

## 절대 규칙
1. **오직 무료 티어만 사용**: 유료 기능·유료 한도 초과 금지(DeepSeek 제외, 비용 가드 필수).
   KV 쓰기 금지, D1 쓰기 최소화, CPU 작업 최소화.
2. **CDN 캐시 적극 사용 / origin 연산 최소화**: 주기 갱신 데이터는 크론이 R2/D1 에 **미리 계산·저장**하고,
   읽기 API 는 연산 없이 반환 + `Cache-Control: public, s-maxage=…`(`shared/http.ts` jsonResponse)로 엣지 캐시.
   사용자 요청당 origin 연산을 0 에 가깝게. (CDN/Cache API 도 무료 한도 큼 → 적극 활용)
3. **API 키는 secret/env만**, 코드/레포에 하드코딩·커밋 금지
3. **LLM(DeepSeek)은 뉴스 요약 전용**. 투자 조언 생성 금지
4. **모든 시그널은 기존 전략 룰 로직 포팅**. 임의 로직 발명 금지, 불명확하면 질문할 것
5. **포팅 후 기존 Python 결과와 1주일 병행 검증 필수**
6. **한국어 UI 기본 + 영어 토글**. 등락색은 한국식(적=상승, 청=하락), 토큰 교체로 미국식 전환 가능
7. 모든 화면은 stale 상태를 명시. 빈 화면 절대 금지 (직전 데이터 + stale 배너)

## 디렉터리
```
functions/api/   Pages Functions = HTTP API (가이드 §4). ingest 완료, 나머지 스텁
shared/          프레임워크 비의존 공용 로직 (ingest.ts, http.ts, 추후 시그널 엔진) — Functions·Cron 공용
cron-worker/     스케줄 전용 Worker (src/index.ts + wrangler.toml)
frontend/        정적 프론트 (src=TS, public=정적, dist=빌드출력→Pages가 서빙)
migrations/      D1 SQL 마이그레이션
docs/            전략 분석·프롬프트 등 문서
azure-news/      (미사용) 뉴스는 AIInvestor 에 통합 — 결정 기록용
wrangler.toml          → Pages 설정
cron-worker/wrangler.toml → Cron Worker 설정
```

## 참조 전략 코드 (이 레포 내 부모 폴더 = 가이드의 `ref/`)
원본 전략은 별도 레포가 아니라 **이 레포의 상위 `01.Trading Strategy/` 폴더**에 있다.
포팅 시 아래 canonical 버전을 기준으로 한다 (상세: `docs/STRATEGY-ANALYSIS.md`).

| 전략 | 1차 | Canonical 폴더 (상위 경로) | 언어 |
|---|---|---|---|
| ARDS | ✅ | `../ARDS — Adaptive Recession-Defensive Strategy for AI_QQQ/` | Python (yfinance + FRED) |
| AMQS | ✅ | `../Adaptive Momentum Quant Strategy (AMQS) for AI Infra/` | Python (yfinance) |
| MU_Hynix | ⏸ P2 | `../Awesome claude quant scripts/MU_Hynix/` | Python (yfinance + statsmodels) |

## 시그널 어휘 (대시보드 통일 enum)
`BUY | SELL | HOLD | SHORT_TERM_RISK | SURGE`
각 전략 native 출력 → 이 enum 매핑은 `docs/STRATEGY-ANALYSIS.md` 참조.

## 개발 단계 (가이드 §6.3)
1. [x] 전략 분석 → `docs/STRATEGY-ANALYSIS.md`
2. [x] `wrangler.toml` + `migrations/0001_init.sql`
3. [x] Pages Functions `/api/ingest/news` (HMAC 검증) + 단위테스트 — `shared/ingest.ts`
4. [x] Pages + Pages Functions + Cron Worker 아키텍처 재구성
5. [ ] 시그널 TS 포팅(ARDS·AMQS, MU_Hynix 제외) + 단위 테스트 (Python 결과 대조 fixture) — `shared/`
6. [ ] Cron Worker: 10분 파이프라인 + 일1회 시그널 산출 (장외시간 스킵)
7. [ ] 나머지 API(Pages Functions): dashboard·search·rankings·movers·news·track
8. [ ] 프론트: PART B 화면 가이드 구현 (전략 카드 2장)
9. [ ] 뉴스 함수: AIInvestor 통합(`docs/PROMPT-azure-news.md`) → ingest 연결 테스트
10. [ ] 배포(Pages + Cron Worker) + Python 병행 검증

## 로컬 개발/검증
Cloudflare/Azure 계정·API 키 미보유. 로컬 모드 + mock 으로 검증. 코드는 키 없이도 빌드·테스트 가능하게.
```bash
npm install
npm run build:frontend                 # frontend/dist 생성 (Pages 출력)
npm run dev                            # wrangler pages dev (프론트 + Pages Functions)
npm run dev:cron                       # 크론 핸들러 테스트
npm run db:migrate:local               # 로컬 D1 마이그레이션
npm test                               # vitest (shared 로직 단위테스트)
npm run typecheck                      # tsc --noEmit
```
배포: `npm run deploy:pages` + `npm run deploy:cron` (D1/R2 생성·시크릿 주입 후).
