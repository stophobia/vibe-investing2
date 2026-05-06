# 증권당 개발 스펙

**문서 버전**: v1.0 (2026-05-06)
**범위**: 시스템 아키텍처 / 비용 / 보안 / 운영 / 향후 로드맵 + 변경 히스토리

본 문서는 다음 문서들을 종합·요약하는 단일 진실원본입니다:
- [paper_plan.md](paper_plan.md) — 1차/2차 개발 단계 + 학술 데이터 수집 계획
- [postmortem.md](postmortem.md) — 응답 지연 진단 + 캐싱 도입 1·2부
- [ticker-data-caching-architecture-v1.0-ko.md](ticker-data-caching-architecture-v1.0-ko.md) — `/api/data/{ticker}` 옵션 C
- [report-generation-policy-v1.0-ko.md](report-generation-policy-v1.0-ko.md) — 시간대 슬롯 + 선호도/빈도 결합

---

## 0. 한 줄 요약

워렌 버핏 / 레이 달리오 / 캐시 우드 페르소나가 미국 시황과 종목을 4개 언어로 해설하는 텔레그램 챗봇. **3-tier 캐시 (메모리→Blob→yfinance)** + **선호도×빈도 가중 hot ticker 자동 갱신** + **Azure Static Web Apps + Functions Flex Consumption** 으로 응답시간 1.7초·월 비용 ~$105 (DAU 3,000 기준).

---

## 1. 개발 방식의 장점

### 1.1 인프라

| 차원 | 선택 | 장점 |
|---|---|---|
| 컴퓨트 | **Azure Functions Flex Consumption** | 사용량 기반 과금, 24h 가동 부담 없음, 자동 스케일아웃, Always Ready 1로 콜드 스타트 완화 가능 |
| 프런트 | **Azure Static Web Apps Free** | 글로벌 edge CDN 자동, $0/월, GitHub Actions 자동 배포, HTTPS 무료 |
| 저장소 | **Azure Blob Storage 단일 계층** | Cosmos DB 미사용 → RU 관리 부담 0, 컨테이너 7종으로 책임 분리 |
| LLM | **DeepSeek (OpenAI 호환)** | GPT-4 대비 1/35 비용, OpenAI SDK 그대로 사용 (drop-in), 한국어 품질 우수 |
| 가격 데이터 | **yfinance** | 무료, NASDAQ/S&P/한국주/암호화폐 모두 지원, rate limit 만 주의 |
| 관측 | **Application Insights + OpenTelemetry** | Functions 자동 통합, KQL 쿼리, 커스텀 메트릭 |
| 배포 | **GitHub Actions + Bicep** | Infrastructure as Code, 1 push = 1 배포, 환경 분리 (prod/dev) |

### 1.2 운영 원칙

- **저비용 우선**: Free SKU 우선 시도, 막힌 곳만 paid 검토
- **인프라 코드화**: Bicep + workflow secret sync — 손으로 클릭하는 작업 0
- **익명화 기본**: SHA-256 + 90일 salt rotation, 원시 식별자 절대 저장 안 함
- **점진적 도입**: 1차(로컬 SQLite) → 2차(Azure Blob) → 3차(학술 데이터) 단계별
- **문서 단일 진실원본**: 코드 변경 시 paper_plan / postmortem / spec 동시 업데이트

### 1.3 사용자 경험

- 평균 응답 1.7초 (가중 평균, 캐시 적중률 70%)
- 4개 언어 자동 감지 + 페르소나 응답
- 다국어 종목명 (`엔비디아`/`テスラ`/`苹果` → `NVDA`/`TSLA`/`AAPL`)
- 자연어 입력 (`아마존 주가`, `테슬라 어때`) 정상 처리
- 2단계 분석 (짧은 응답 → 깊이 있는 전문 분석 옵션)
- 섹터 추적 + 라이벌 비교 자동 권유

---

## 2. 전체 아키텍처

### 2.1 시스템 다이어그램

```
                          ┌─────────────────────────────────┐
                          │  Azure Static Web Apps (Free)    │
사용자 ────HTTPS────▶     │   black-plant-...azurestaticapps │
                          │   /         소개 페이지           │
                          │   /ticker   종목 검색 UI         │
                          │   /dashboard 운영 대시보드        │
                          └────────┬──────────────┬──────────┘
                                   │              │
                                   │ /api/* (cors)│
                                   ▼              ▼
       ┌──────────────────────────────────────────────────┐
       │  Azure Functions Flex Consumption (Korea Central) │
       │   • telegram_webhook    봇 메시지 처리            │
       │   • daily_report        KST 06:30 일일 리포트     │
       │   • prewarm_snapshots   4시간 yfinance 252 ticker │
       │   • prewarm_commentaries 4시간 LLM 600 commentary │
       │   • refresh_hot_ticker_data 30분 (light price)    │
       │   • rotate_hot_tickers  매일 KST 02:00 hot 재계산 │
       │   • aggregate_dashboard 15분 24h/7d 집계          │
       │   • keepalive           5분 (콜드 스타트 완화)     │
       │   • /api/data/{ticker}  옵션 C 3-tier             │
       │   • /api/stats          공개 카운트 (CountUp)      │
       │   • /api/dashboard_stats key 게이트 통계           │
       │   • /api/dashboard_export?key=… CSV               │
       │   • /api/feedback (텔레그램 핸들러 내부)            │
       └────────┬──────────┬─────────┬────────┬────────────┘
                │          │         │        │
        ┌───────▼──┐ ┌─────▼──┐ ┌────▼────┐ ┌─▼──────┐
        │ DeepSeek │ │yfinance│ │Telegram │ │Blob St │
        │  Chat API│ │  HTTP  │ │  Bot API│ │ 7 ctnr │
        └──────────┘ └────────┘ └─────────┘ └────────┘

Blob 컨테이너 (7개):
  users/         사용자 프로필 (anon SHA-256, ETag concurrency, 5분 메모리 캐시)
  reports/       슬롯별 사전 생성 시황 리포트
  prewarm/       snapshots/ + commentary/ (4시간 단위 사전 생성)
  ticker-cache/  light price feed (30분/4시간 적응형 TTL)
  logs/          NDJSON 사용 통계 (60s/50건 버퍼 → append-blob)
  dashboard/     15분 단위 집계 JSON (24h.json, 7d.json)
  analysis/      배치 분석 결과 (예약, 미사용)
  deployment/    Functions zip 배포 (Azure 시스템)
```

### 2.2 데이터 흐름 — 사용자 메시지 1건

```
1. 사용자 → Telegram → Webhook
2. Function App: 인증 헤더 검증 (X-Telegram-Bot-Api-Secret-Token)
3. _profile() → BlobUserProfileRepo.get_or_create
   ├ 메모리 캐시 hit (5분 내)  → 즉시 반환
   └ Blob read (users/<anon[:2]>/<anon>.json)
4. 의도 분류 (`_classify_intent`)
   ├ 자연어 키워드 → intent_unrecognized
   └ ticker → continue
5. 다국어 ticker resolve (`ticker_lookup.resolve`)
   ├ 정확 매칭 → ticker
   ├ noise 단어 제거 후 매칭 ('아마존 주가' → '아마존' → AMZN)
   └ 단어 단위 scan → 첫 매칭
6. Tier 1: prewarm/commentary/<TICKER>.<persona>.<lang>.json
   ├ hit → strip_md() + Telegram 회신 → 끝 (~0.5s)
   └ miss
7. Tier 2: prewarm/snapshots/<TICKER>.json
   ├ hit → snapshot 재사용 + DeepSeek 호출
   └ miss → live yfinance + DeepSeek
8. 짧은 응답 + [✅ 예 / 아니요] 키보드
9. 섹터 추적 → 같은 섹터 3+ 회면 비교 권유
10. usage_logger.record (NDJSON 버퍼)
11. _profile.update — recent_tickers, sector_count
```

### 2.3 시간대별 자동 작업

| 시간 (KST) | Trigger | 작업 |
|---|---|---|
| 매 5분 | keepalive | 콜드 스타트 방지 + usage_logger flush |
| 매 15분 | aggregate_dashboard | logs/ → dashboard/24h.json + 7d.json |
| 매 30분 | refresh_hot_ticker_data | 14 hot ticker light price 갱신 |
| **매 4시간** | prewarm_snapshots | 252 ticker yfinance 갱신 |
| **매 4시간 + 30분** | prewarm_commentaries | 50 ticker × 3 페르소나 × 4 언어 = 600 LLM |
| **KST 02:00 매일** | rotate_hot_tickers | 선호도×빈도 결합 → top 50 갱신 |
| **KST 06:30 매일** | daily_report | 일일 리포트 12개 (3 페르소나 × 4 언어) |

---

## 3. 비용 구조

### 3.1 월 고정 비용 (DAU 3,000 기준)

| 항목 | 비용 | 비고 |
|---|---|---|
| Azure Functions Flex (always_ready=1) | $13 | 콜드 스타트 완화 |
| Functions per-execution | $0.50 | 15K req/일 × 30일 |
| Blob Storage (용량 + 트랜잭션) | $5 | 7 컨테이너 |
| Application Insights | $0 | Free 1GB ingestion |
| Static Web Apps Free | $0 | 100 GB/월 대역폭 |
| Key Vault | $0.30 | 5 secret |
| **Azure 합계** | **~$19** | |
| DeepSeek LLM 호출 | $86 | 4,500 webhook × 800 token + 600 commentary + 72 slot |
| **총합** | **~$105/월** | |

### 3.2 비용 절감 효과

| 비교 | 비용 | 절감 |
|---|---|---|
| Before (캐시 0) | $320/월 | — |
| **After (옵션 C + 슬롯)** | **$105/월** | **-67%** |

### 3.3 DAU 확장 시 비용

| DAU | LLM 호출/일 | Functions exec | LLM 비용/월 | 총 월 비용 |
|---|---|---|---|---|
| 500 | 1,500 | 2,500 | $30 | ~$50 |
| 3,000 | 4,500 | 15,000 | $86 | $105 |
| 10,000 | 15,000 | 50,000 | $290 | $335 |
| 50,000 | 75,000 | 250,000 | $1,450 | ~$1,600 |

LLM 비용이 가장 빠르게 증가 — 캐시 적중률 향상 + 슬롯 확장이 비용 곡선 평탄화 핵심.

### 3.4 자동 슬롯 ROI (시간대 6개 × 12 = 72/일)

```
슬롯 LLM 비용:    $1.13/월
슬롯 hit으로 절약된 LLM:  $42/월 (DAU 3,000)
ROI:              37×
```

---

## 4. 장애 복구

### 4.1 장애 시나리오 + 대응

| 장애 | 영향 | 자동 복구 | 수동 복구 |
|---|---|---|---|
| Functions 인스턴스 콜드 스타트 | 첫 요청 +1–3초 | keepalive Timer | Always Ready N 증가 |
| Functions 일시 장애 (502) | 사용자 webhook 실패 | Telegram이 자동 재전송 | GitHub Actions 워크플로 재실행 |
| Blob read 실패 | 캐시 miss → live LLM/yfinance | 자동 fallback (Tier 2 → Tier 3) | Storage 상태 확인 |
| DeepSeek API 일시 장애 | 응답 LLM 단계 fail | 사용자 친화적 error 메시지 | 환경변수로 OpenAI 등 대체 (코드 변경 0) |
| yfinance 차단/rate limit | 새 ticker 조회 실패 | 5분 메모리 캐시로 흡수 | Polygon.io / Alpha Vantage backup supplier 추가 |
| 전체 사용자 프로필 손실 | 페르소나 재선택 필요 | 사용자가 /start 재실행 시 복구 | Storage point-in-time restore (7일 보관) |
| 의도되지 않은 LLM 환각 | 잘못된 수치 응답 | 시스템 프롬프트가 데이터 블록 외 수치 금지 | 사용자 /feedback 으로 즉시 보고 |

### 4.2 백업 정책

| 데이터 | 백업 | 보존 |
|---|---|---|
| Bicep 인프라 코드 | Git | 영구 |
| 사용자 프로필 (`users/`) | Storage soft-delete | 7일 |
| 사용 통계 (`logs/`) | Lifecycle policy | 90일 자동 삭제 |
| 사전 캐시 (`prewarm/`) | 4시간 마다 자동 재생성 | TTL 시 자동 갱신 |
| 시크릿 (Key Vault) | Vault soft-delete + purge protection | 7일 + 90일 retention |

### 4.3 복구 시간 (RTO) / 복구 지점 (RPO)

| 시나리오 | RTO | RPO |
|---|---|---|
| Functions 코드 롤백 | 6분 (1회 deploy) | 0 (Git history) |
| 전체 RG 재구축 | 12–15분 (Bicep + secret sync) | 7일 (사용자 프로필 soft-delete) |
| 단일 사용자 프로필 복구 | 10초 (`/start` 재실행) | 사용자가 다시 입력 |

---

## 5. 보안

### 5.1 신원 + 인증

| 표면 | 인증 |
|---|---|
| Telegram Webhook | `X-Telegram-Bot-Api-Secret-Token` 헤더 검증, secret 32자 hex |
| `/api/data/{ticker}` (공개) | 인증 없음 — 가격 데이터 비민감 |
| `/api/stats` (공개) | 인증 없음 — 집계 수치만 |
| `/api/dashboard_stats?key=...` | DASHBOARD_ACCESS_KEY 평문 비교 (dashboard/ 전용) |
| `/api/dashboard_export?key=...` | 동일 |
| Static Web App `/dashboard` | 클라이언트 사이드 SHA-256(key) hash 비교 |
| Function App ↔ Blob | Managed Identity (`Storage Blob Data Contributor`) |
| Function App ↔ Key Vault | Managed Identity (`Key Vault Secrets User`) |
| GitHub Actions ↔ Azure | Service Principal (Resource Group scoped) |

### 5.2 시크릿 관리

```
Key Vault (kv-aiinvestor-prod)
├── telegram-bot-token            BotFather 발급
├── deepseek-api-key              DeepSeek dashboard
├── telegram-webhook-secret       openssl rand -hex 16
├── user-id-salt                  openssl rand -hex 24
└── dashboard-access-key          본인 임의 값 (사용자 결정)

GitHub Secrets
├── AZURE_CREDENTIALS             SP JSON
├── AZURE_DEPLOYER_CLIENT_ID      SP clientId
├── TELEGRAM_BOT_TOKEN            (KV로 sync)
├── DEEPSEEK_API_KEY              (KV로 sync)
├── TELEGRAM_WEBHOOK_SECRET       (KV로 sync)
├── USER_ID_SALT                  (KV로 sync)
├── DASHBOARD_ACCESS_KEY          (KV로 sync)
└── TELEGRAM_OWNER_CHAT_ID        plain App Setting (chat_id is not sensitive)
```

GitHub Actions가 매 deploy마다 secrets → Key Vault로 sync. Function App은 Managed Identity로 KV reference 해석.

### 5.3 익명화

```
사용자 텔레그램 ID (132928747)
        │
        ▼
SHA-256(user_id_salt + ":" + "tg:132928747")
        │
        ▼ 처음 16자
anon_user_id = "8dab0dcc0e1537fd"
        │
        ▼
저장: users/8d/8dab0dcc0e1537fd.json
로그: anon=8dab0dcc (8자만)
대시보드 CSV: anon=8dab0dcc (8자, k-anonymity)
```

salt는 90일 마다 rotation (예정) — rotation 후 같은 사용자가 다른 anon_user_id를 가짐. 장기 추적 차단.

### 5.4 Blob 접근

- 모든 컨테이너 `publicAccess: None` (Free Trial 제약 + 보안)
- 외부 노출 데이터(`dashboard/`, `ticker-cache/`)는 Function App 통해서만 (CORS + key 게이트)
- Static Web App은 동일 도메인 → Function App API 호출 시 CORS 허용

### 5.5 보안 헤더 (Static Web App)

- `Strict-Transport-Security: max-age=31536000` (HSTS 1년)
- `X-Frame-Options: DENY` (clickjacking 방지)
- `Content-Security-Policy` — script/style/connect-src 화이트리스트
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 5.6 LLM 안전 장치

- 시스템 프롬프트: "데이터 블록 외 수치 환각 금지"
- 매 응답 끝에 disclaimer 강제 (4개 언어)
- Buy/sell 명시적 권고 금지 — stance 표현으로 우회 ('I'd be inclined to wait')
- max_tokens 상한 (짧은 응답 550, deep 1500)

---

## 6. 개발 로드맵

### 6.1 우선순위 분류

- **🔴 Critical** — 사용자 차단 결함, 즉시 수정
- **🟠 High** — 사용자 가치 즉시 증가, 다음 sprint
- **🟡 Medium** — 운영 품질, 분기 단위
- **🟢 Low** — Nice to have, 시간 여유 시

### 6.2 로드맵 리스트

| 우선순위 | 항목 | 설명 |
|---|---|---|
| 🟠 High | **페르소나별 sub-dashboard** | `/dashboard/persona?key=...&p=buffett` — 각 페르소나의 인기 ticker, 응답 분포, 평균 시간. 본 문서 §7로 명세화 |
| 🟠 High | **개인화 통계 그룹화** | anon_user_id 기준으로 cohort 분류 (신규 / 활성 / 휴면), 각 그룹 내 ticker 분포 |
| 🟠 High | **프리미엄 모드 (dual persona)** | 같은 ticker를 두 페르소나가 각각 분석 + 결론 비교. §8 명세 |
| 🟠 High | **주 단위 캐싱 확장** | 빈도 누적 시 hot pool을 50 → 100 → 200 점진 확장. §9 명세 |
| 🟡 Medium | **시간대 슬롯 6개 본구현** | report-generation-policy §2 — 하루 6 슬롯 × 12 리포트 자동 생성 |
| 🟡 Medium | **`/recommend` `/compare` 명령** | 자연어 수용을 명시적 명령으로 |
| 🟡 Medium | **컨텍스트 유지** | "AMD는?" follow-up — 마지막 ticker 기억 |
| 🟡 Medium | **의미적 캐싱** | embedding ANN — paper_plan §13 학술 작업 |
| 🟡 Medium | **subscription email 인증** | Azure Communication Services 통합. paper_plan §17.2 |
| 🟢 Low | **30d MAU aggregator** | 현재 7d × 4 추정 → 정확한 30d unique 계산 |
| 🟢 Low | **Front Door CDN 활성화** | Pay-As-You-Go 구독으로 전환 시. 글로벌 사용자 확장 |
| 🟢 Low | **모바일 앱 (iOS/Android)** | React Native + Expo. 텔레그램 외 채널 |
| 🟢 Low | **응답 스트리밍** | DeepSeek streaming + Telegram editMessageText (체감 응답시간 -50%) |

### 6.3 다음 1주 권장 순서

1. 🟠 페르소나별 sub-dashboard (§7) — 코드 0.5일
2. 🟠 프리미엄 모드 dual persona (§8) — 코드 1일
3. 🟠 주 단위 캐싱 확장 (§9) — 코드 0.5일
4. 🟡 시간대 슬롯 6개 — 코드 1일

총 ~3일 분량.

---

## 7. 페르소나별 Sub-Dashboard 명세

### 7.1 URL

```
https://black-plant-….azurestaticapps.net/dashboard/persona?key=<KEY>&p=buffett
                                                              &p=dalio
                                                              &p=wood
```

### 7.2 표시 항목

| 위젯 | 데이터 |
|---|---|
| 페르소나 응답 갯수 (24h / 7d) | logs/ tier_counts |
| 페르소나가 가장 많이 다룬 ticker Top 20 | ticker × persona 매트릭스 |
| 페르소나별 평균 출력 토큰 | logs/ llm_out 평균 |
| 페르소나 deep analysis 사용 비율 | tier=deep / 전체 |
| 사용자 코호트 — 이 페르소나 선택자 (vs 기타) | profile.persona_key |
| 페르소나의 3개 카운터 페르소나 의견 사용 비율 | counter view 트리거 횟수 |

### 7.3 데이터 소스

```
dashboard_aggregator.py 확장:
  - 기존: 24h, 7d 집계
  - 추가: 24h_by_persona.json, 7d_by_persona.json
        스키마: { persona_key: { tier_counts, top_tickers, avg_tokens, ... } }
```

### 7.4 코드 변경 요약

- [services/dashboard_aggregator.py](../services/dashboard_aggregator.py) `_aggregate()` 가 persona 별 dict 추가 반환
- 신규 파일: `static_web/dashboard-persona.html` (탭 디자인 — buffett/dalio/wood)
- 신규 endpoint: `/api/dashboard_stats_persona?key=...&p=buffett`

### 7.5 그룹화 기준

- 신규 (created_at 7일 이내)
- 활성 (last 24h interaction 있음)
- 휴면 (30일 이상 비활성)
- 페르소나 선호도 (buffett/dalio/wood)
- 언어 (ko/en/ja/zh)
- 섹터 관심사 (sector_count 1위)

---

## 8. 프리미엄 모드 (Dual Persona) 명세

### 8.1 사용자 흐름

```
사용자 (프리미엄): NVDA
       │
       ▼
[ 짧은 응답 (현재 페르소나) ]
[ ✅ 두 페르소나 비교 ]  [ 일반 deep ]  [ 아니요 ]
       │
       ▼ "두 페르소나 비교" 클릭
[ 페르소나 선택 키보드 ]
[ 워렌 버핏 + 캐시 우드 ]
[ 워렌 버핏 + 레이 달리오 ]
[ 캐시 우드 + 레이 달리오 ]
       │
       ▼
[ 2 페르소나 동시 분석 ]
  📊 NVDA — 두 시각 비교
  
  🎩 워렌 버핏:
   - 본인의 stance + 핵심 근거
  
  🚀 캐시 우드:
   - 본인의 stance + 핵심 근거
  
  ⚖️ 결론 — 두 시각이 일치하는 부분 / 갈리는 부분
```

### 8.2 LLM 호출 패턴

- 짧은 응답: 단일 LLM 호출, max_tokens=550
- 일반 deep: 단일 LLM, max_tokens=1500 (기존)
- **dual persona**: 2 LLM 호출 + 1 결론 LLM = **3 호출**, 총 ~3500 token 소요

### 8.3 캐싱

```
prewarm/dual/<TICKER>.<persona1>+<persona2>.<lang>.json
```

- 한국 인기 14종에 대해서 페르소나 페어 3종 (buffett+wood, buffett+dalio, wood+dalio) × 4 언어 = **168 dual analysis 사전 생성**
- 4시간 갱신 (snapshot/commentary 와 같은 주기)
- LLM 비용: 168 × 3 호출 = 504/4시간 = 3,024/일
- DeepSeek 추가 비용: ~$5/월

### 8.4 가격 정책

- 무료: 단일 페르소나, 일 5회 deep
- 프리미엄: dual persona + 무제한 deep + 모든 언어 + email 알림
- 가격: ?? (구독 결제는 paper_plan §17.2 에서 정의)

### 8.5 코드 변경

- `services/persona_engine.py` 에 `generate_dual()` 메서드 추가
- 핸들러: 새 callback `dual:<p1>+<p2>:<ticker>`
- 사용자 프로필에 `is_premium: bool` 필드 추가
- prewarm_service.py 에 `refresh_dual_commentaries` 추가

---

## 9. 주 단위 캐싱 확장 명세

### 9.1 단계적 hot pool 확장

```
Week 1:  hot pool = 14 (한국 선호) + 8 (글로벌) = 22
         commentary: 22 × 3 페르소나 × 4 언어 = 264 blob
         LLM: 264 × 4시간 갱신 = 1,584/일

Week 2:  hot pool = 50 (선호도 + 빈도 결합 top 50)
         commentary: 50 × 12 = 600 blob (현재 상태)
         LLM: 3,600/일

Week 3+: hot pool = 100 (빈도 누적 7일치 상위 100)
         commentary: 100 × 12 = 1,200 blob
         LLM: 7,200/일

Week 4+: hot pool = 200 (트래픽 안정 시)
         commentary: 200 × 12 = 2,400 blob
         LLM: 14,400/일
```

### 9.2 트리거 조건

```python
def should_expand_hot_pool(current_size: int, recent_traffic: dict) -> int:
    """주 단위로 trigger. logs/ 7일치 unique ticker 수가 current_size의
    1.5배를 넘으면 다음 단계로 확장. 트래픽 줄면 그대로 유지 (축소 안 함)."""
    unique_7d = len(recent_traffic)
    thresholds = [22, 50, 100, 200]
    for t in thresholds:
        if t > current_size and unique_7d > current_size * 1.5:
            return t
    return current_size
```

### 9.3 비용 영향

| Week | hot size | LLM 호출/일 | LLM 비용/월 |
|---|---|---|---|
| 1 | 22 | 1,584 | $1.20 |
| 2 | 50 | 3,600 | $2.70 |
| 3 | 100 | 7,200 | $5.40 |
| 4 | 200 | 14,400 | $10.80 |

확장은 사용자 트래픽이 받쳐줄 때만 발생 — 비용 폭증 방지.

### 9.4 코드 변경

- `services/hot_ticker_resolver.py` 에 `should_expand_hot_pool()` 추가
- `function_app.py:rotate_hot_tickers` 매일 KST 02:00 호출 시 size 결정
- `data/hot_pool_size.txt` 또는 Blob에 현재 size 저장

---

## 10. 콜드 스타트 + LLM 로딩 극복 — 데이터·서비스 설계 특징

### 10.1 콜드 스타트의 본질

Azure Functions Flex Consumption은 사용자 요청이 없으면 인스턴스를 종료. 다음 요청 시:
- **Python 인터프리터 + 라이브러리 로딩**: 1–2초
- **OpenTelemetry init**: 0.3초
- **Bot/services 모듈 import**: 0.5초
- **`bot.initialize()` (getMe)**: 0.7초
- **첫 yfinance 또는 DeepSeek 호출 — DNS + TLS handshake**: 0.3초

총 콜드 비용: **2.8–3.8초**.

### 10.2 우리 시스템의 극복 전략

#### A. 인스턴스 보존 — keepalive

```
keepalive Timer (5분 마다) → 인스턴스 살아있음
  ↓
Always Ready=1 (option) → 항상 1개 깨어있음
  ↓
콜드 스타트 사실상 0
```

#### B. Bootstrap once, reuse forever

```python
_ptb_app = None  # 모듈 전역
async def _bootstrap():
    global _ptb_app
    if _ptb_app is not None:
        return
    # ... build once, reuse
    await _ptb_app.initialize()
```

이 패턴으로 매 요청마다 발생하던 750ms의 `getMe` 호출이 인스턴스 수명에 1회로 줄었다 (postmortem §1부 참조).

#### C. LLM 응답 사전 생성

문제: DeepSeek 본문 스트리밍 7초.
해결: **사용자가 묻기 전에 미리 만든다**.

```
Timer 4시간 → prewarm 50 ticker × 3 persona × 4 lang = 600 commentary
              → Blob 저장
사용자 요청 → Blob fetch (50ms) → 즉시 회신
```

캐시 적중 시 LLM 호출 0 — 응답 0.5초.

#### D. 점진적 캐싱 계층

```
Tier 1 — 메모리 (process dict)        ~5ms      stampede guard for hot
Tier 2 — Blob users/<anon>.json       ~50ms     인스턴스 재시작 후 빠른 워밍
Tier 3 — Blob prewarm/snapshots/      ~50ms     yfinance 절감 (1.5초)
Tier 4 — Blob prewarm/commentary/     ~50ms     LLM 절감 (7초)
Tier 5 — Blob reports/<slot>/         ~50ms     "오늘 시황" 슬롯 hit
Tier 6 — yfinance 라이브              ~500ms    fallback
Tier 7 — DeepSeek 라이브              ~7000ms   ultimate fallback
```

5단계 캐시로 평균 응답 1.7초 (가중 평균).

#### E. 사전 워밍 (predictive)

```
KST 02:00  rotate_hot_tickers      선호도 + 빈도 → 새 hot list
KST 06:00  daily_report             3 페르소나 × 4 언어 = 12 리포트
4시간 마다 prewarm_snapshots/commentaries
```

사용자가 NVDA를 묻기 전에, NVDA의 페르소나 코멘트가 4언어로 모두 Blob에 있다.

#### F. 빈도 기반 자동 적응

logs/ NDJSON → 7일 unique ticker → 새 ticker가 hot 진입 시 다음날부터 자동 사전 캐싱.

#### G. 비동기 일색

- `AsyncOpenAI` (DeepSeek 호출)
- `BlobServiceClient.aio` (Blob)
- `yfinance` 만 sync — `asyncio.to_thread` 로 격리
- python-telegram-bot v22 자체가 async

이벤트 루프 블록 없음 → 동시 사용자 ≥10 시도 응답시간 누적 안 됨.

#### H. 응답 메시지 분할

DeepSeek max_tokens=1500 응답이 Telegram 4096자 제한 초과 시 자동 split. 첫 부분 즉시 회신, 나머지 1초 후 발송.

### 10.3 콜드 스타트 비용 (실측)

| 사용자 시나리오 | 콜드 (keepalive 없음) | 워밍 (keepalive 있음) | Always Ready=1 |
|---|---|---|---|
| `/start` (LLM 없음) | 3–5초 | 0.8–1.2초 | 0.5–0.8초 |
| Hot ticker 짧은 응답 | 4–6초 | 1.5–2초 | **0.8–1.2초** |
| Cold ticker live LLM | 10–13초 | 7–9초 | 6–8초 |

keepalive + Always Ready 조합으로 콜드 스타트 사실상 무력화.

### 10.4 LLM 데이터 로딩 극복 요약

핵심 통찰: **느린 작업을 사용자 경로 밖으로 옮긴다**.

| 느린 작업 | 위치 | 해결 |
|---|---|---|
| Bot init (getMe) 750ms | 매 요청 | bootstrap once |
| yfinance .info + .history 1.5초 | 매 요청 | 5분 메모리 + 4시간 Blob |
| DeepSeek 본문 스트리밍 7초 | 매 deep 요청 | 4시간 사전 생성 commentary |
| 페르소나 문맥 1초 | LLM 호출에 묶임 | system prompt 캐싱 (DeepSeek 자동) |
| 슬롯 시황 분석 5초 | 매 시황 질의 | KST 06/08/12/15:30/21/23 사전 생성 |

평균: 약 5단계 사전 생성 + 7-tier 캐시로 **응답 시간 8초 → 1.7초** (-79%), **LLM 호출 70% 감소**.

---

## 11. 변경 히스토리 (역순)

가장 최근 commit이 위.

| Commit | 날짜 (KST) | 내용 |
|---|---|---|
| 979ccc2 | 2026-05-06 | feat(landing): 새 디자인 hero/persona/chat-demo + `/api/stats` live counters |
| b415193 | 2026-05-06 | feat(hot): 한국 retail favorites + 빈도 결합 hot rotation + docs/ 정리 |
| 8537b2b | 2026-05-06 | feat(lookup): 자연어 ticker resolution — '아마존 주가' 같은 입력 처리 |
| 23751e8 | 2026-05-06 | docs: report-generation-policy v1.0 (시간대 6 슬롯 + ROI) |
| 2837ea8 | 2026-05-06 | feat(swa): `/ticker` 페이지 (client-side fetch) |
| 4b685ae | 2026-05-06 | fix(swa): `/data/*` 302 redirect (cross-origin rewrite는 Standard 필요) |
| 3d07ba6 | 2026-05-06 | feat(ticker-cache): `/api/data/{ticker}` 옵션 C 3-tier hybrid |
| d4ec0f4 | 2026-05-06 | fix(feedback): self-forward skip + 새 thanks 메시지 |
| 893f7bd | 2026-05-06 | fix(llm): deep analysis 한국어 강제 — system+user 양쪽 명령 |
| a70e9e5 | 2026-05-06 | fix(blob): MatchConditions enum (모든 webhook crash 해결) |
| 7f90887 | 2026-05-06 | fix(swa): storage private 유지, dashboard JSON Function API 경유 |
| 8bc7276 | 2026-05-06 | feat(swa): landing + dashboard를 Static Web Apps Free로 이전 |
| 3773562 | 2026-05-06 | feat(dashboard): §17.3 NDJSON usage logger + 15분 aggregator + key-gated 페이지 |
| 9a589d2 | 2026-05-06 | feat(ux): §17.1 sector follow-up + §17.2 daily limit + subscribe stub |
| 9404892 | 2026-05-06 | feat(storage): profile_repo async 통합 + Blob backend wired |
| 970d488 | 2026-05-06 | feat(bot): deep analysis multi-perspective + 강한 disclaimer + §17 spec |
| a5da1a0 | 2026-05-06 | fix(bot): /whoami HTML parse_mode crash 수정 |
| a7f2da4 | 2026-05-06 | feat(bot): v2 alias CSV 통합 (931→2658) + 의도 분류기 + 2-step UX |
| ee9cec8 | 2026-05-06 | fix(infra): functionTimeout 1m30s → 10m for prewarm |
| 875463a | 2026-05-06 | docs: postmortem 2부 (prewarming) + README sync |
| b730a6b | 2026-05-06 | feat(bot): /feedback + /피드백 forwarding + aiohttp dep fix |
| 869c570 | 2026-05-06 | fix(infra): Front Door off — Free Trial 제약 |
| f208093 | 2026-05-06 | feat(prewarm): scheduled cache + Front Door CDN scaffold |
| 83190e4 | 2026-05-06 | docs: postmortem + §16 prewarming spec |
| cab2c67 | 2026-05-06 | perf(latency): bot.initialize once at bootstrap + tighter LLM caps |
| 0c0508f | 2026-05-06 | perf+obs: max_tokens=800 + concise prompt + App Insights instrumentation |
| 949daa9 | 2026-05-06 | perf(latency): max_tokens=500 cap + yfinance 5min snapshot cache |
| 10837ad | 2026-05-06 | fix(infra): 'deployment' 컨테이너 추가 (Functions Flex 필수) |
| 31ba917 | 2026-05-06 | fix(infra): classic CDN 제거 (retired) |
| 4023ae5 | 2026-05-06 | feat(aiinvestor): Azure Functions + Blob + CDN deploy scaffold |
| 43eeff5 | 2026-05-05 | feat(aiinvestor): Azure Functions + Bicep + CDN scaffold (2차-A/D 부분) |
| 223d063 | 2026-05-05 | 페르소나 업데이트 — 다국어 지원 + Azure Blob Storage |
| 37bb46c | 2026-05-05 | 개발 계획 업데이트 |
| e615ae3 | 2026-05-05 | paper_plan: Research Data Collection Plan (학술 논문) |

총 34개 commit. 시작은 학술 논문 계획서 (`e615ae3`), 가장 최근은 새 디자인 landing page (`979ccc2`).

### 11.1 사건 분류

| 분류 | 갯수 | 대표 commit |
|---|---|---|
| **인프라 셋업** | 8 | 4023ae5, 43eeff5, 869c570, 10837ad, 31ba917, 7f90887, 8bc7276, ee9cec8 |
| **신규 기능** | 12 | feat(prewarm), feat(dashboard), feat(swa), feat(ticker-cache), feat(hot), feat(lookup), feat(landing) |
| **버그 픽스** | 7 | fix(blob), fix(swa), fix(feedback), fix(infra), fix(llm), fix(bot) — 모두 prod에서 발견 |
| **문서** | 5 | postmortem 1부/2부, paper_plan, ticker-cache spec, report-policy |
| **성능 최적화** | 3 | perf(latency) cap+cache, bot.initialize once, max_tokens 압축 |

### 11.2 누계 통계

- 코드 라인: 약 3,500 (Python) + 약 2,000 (HTML/CSS/JS) + 약 1,200 (Bicep + YAML)
- 문서 라인: 약 5,000+ (paper_plan + postmortem + ticker-cache + report-policy + spec)
- pytest: 105건 통과 유지
- 배포 시도: 약 30회 (성공 ~22회, 실패 ~8회 — 인프라 측 주로)
- 외부 의존성: 6개 (DeepSeek, yfinance, Azure SDK 4종, Telegram)

---

**End of Document**

*다음 업데이트는 §6 로드맵의 🟠 항목 진행에 따라.*
