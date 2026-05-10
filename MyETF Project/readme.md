# MyETF Builder

> **내가 만드는 미국 주식 ETF 플랫폼** — GICS 11 섹터에서 직접 종목을 골라 3-10개 종목 Personal ETF를 설계하고, AI 기반 펀더멘털·뉴스 요약과 변동성 기반 시나리오 시뮬레이션을 받는 솔로 투자자용 도구.

[![Status](https://img.shields.io/badge/status-concept-blue)]()
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20MySQL%20%2B%20Claude%20Haiku-green)]()
[![License](https://img.shields.io/badge/license-internal--prototype-lightgrey)]()
[![Compliance](https://img.shields.io/badge/compliance-not%20investment%20advice-red)]()

---

## 한 줄 정의

> "TipRanks급 애널리스트 컨센서스 + Finviz급 섹터 모멘텀 + 변동성 기반 손익 시뮬레이션을 한 화면에서 결합해, 3-10개 종목 ETF를 설계·저장·리밸런싱할 수 있는 솔로 투자자용 도구."

## 차별화 포인트

| 구분 | 기존 솔루션 | MyETF Builder |
|---|---|---|
| 스크리너 | Finviz / Yahoo: 종목 나열만 | 섹터 → 세부 산업 → 성향 3단 필터 |
| 애널리스트 데이터 | TipRanks: 단일 종목 forecast | 선택한 바스켓 전체의 가중 평균 forecast |
| 수익 시뮬레이션 | 백테스트 위주 / 과거형 | 변동성 기반 12개월 시나리오 (3구간 투자금) |
| 성향 분류 | 주관적 / 부재 | 변동성 · 베타 · 드로다운 기반 자동 라벨링 |
| 저장 / 리밸런싱 | 엑셀 수기 관리 | Google 로그인 + 분기/월별 자동 리밸런싱 알림 |
| 가격 | Bloomberg $24K/년 | 프리티어 인프라 → 무료 ~ $9/월 |

---

## 산출물 (Deliverables)

본 저장소는 5개 산출물로 구성된다. 모두 한국어 네이티브, Web3Paper 발행 연계.

| # | 파일 | 형식 | 분량 | 핵심 내용 |
|---|---|---|---|---|
| 01 | **MyETF Concept** | `01_MyETF_Concept.md` / `.docx` | 10 섹션 | Executive Summary · 페르소나 · 8단계 사용자 여정 · GICS 11 섹터 × 2026 모멘텀 · 데이터 소스 매핑 · 비즈니스 모델 (Free / Pro $9 / Trader $29 / B2B2C) · 자본시장법 비투자자문 포지셔닝 · 12개월 로드맵 · UI 와이어프레임 |
| 02 | **MyETF DevSpec** | `02_MyETF_DevSpec.docx` | 11 섹션 | 시스템 아키텍처 · Oracle Cloud Free Tier 운영 전략 · MySQL DDL 전체 · REST API 15 엔드포인트 · 퀀트 산식 · LLM 프롬프트 · Celery 8개 잡 · 비용 산정 · 12주 MVP 스프린트 |
| 03 | **Sample: Semiconductor** | `03_Sample_Semiconductor.docx` | AI Storage ETF | NVDA 30 / MU 25 / SNDK 20 / STX 15 / WDC 10 · aggressive · 가중 σ 51.2%, β 1.78 · $10K → $7,800 / $13,230 / $17,500 |
| 04 | **Sample: Financials** | `04_Sample_Financials.docx` | Big Finance + Digital Asset ETF | JPM / GS / BLK / BRK.B / COIN / MSTR · moderate · 75% 코어 + 25% 새틀라이트 바벨 전략 · $10K → $8,800 / $11,850 / $14,500 |
| 05 | **Code Bundle** | `myetf_code_assets.zip` | 8 파일 | MySQL 스키마 · 퀀트 모듈 · LLM 프롬프트 · Celery 잡 · FastAPI 라우터 · Nginx 설정 · requirements.txt · README |

---

## 코드 번들 구조

```
myetf_code_assets.zip
├── README.md                      # 코드 번들 자체 가이드
├── myetf_schema.sql               # MySQL DDL + GICS 11 섹터 시드 (3-10 종목 트리거 포함)
├── myetf_quant.py                 # 변동성 / 베타 / MDD / 리스크 분류 / 시나리오 시뮬레이션
├── myetf_llm_prompts.py           # Claude Haiku 4.5 뉴스 요약 / 펀더멘털 / 리포트 생성
├── myetf_celery_tasks.py          # EOD · 컨센서스 · 펀더멘털 · 뉴스 · 스냅샷 백그라운드 잡
├── myetf_main.py                  # FastAPI 라우터 (15 엔드포인트)
├── myetf_nginx.conf               # 운영 Nginx (TLS, rate limit, micro-cache)
└── myetf_requirements.txt         # Python 의존성 (Oracle Free Tier ARM 검증)
```

각 파일은 `02_MyETF_DevSpec.docx` 의 해당 섹션과 1:1 매핑된다.

---

## 기술 스택

```
Cloudflare (Free) ──▶ Nginx (TLS, rate-limit, cache) ──▶ uvicorn × 4
                                                          │
                                                          ▼
                                                       FastAPI
                                                          │
                       ┌──────────────────────────────────┼──────────────────────────────────┐
                       ▼                                  ▼                                  ▼
                  MySQL 8 (DDL)                Redis (cache/queue)                 Celery worker + beat
                                                                                          │
                                                                                          ▼
                                                                            yfinance / Finnhub / FMP
                                                                            Anthropic Claude Haiku 4.5
```

| 레이어 | 선택 |
|---|---|
| 인프라 | Oracle Cloud Free Tier — ARM Ampere A1 (4 OCPU / 24 GB / 200 GB) 단일 VM |
| OS / Web | Ubuntu 24 + Nginx + Let's Encrypt |
| API | Python 3.11 + FastAPI + uvicorn × 4 (systemd) |
| DB / Queue | MySQL 8 + Redis 7 + Celery |
| 데이터 | yfinance (EOD 1차) · Finnhub (컨센서스, 60/분 무료) · FMP (펀더멘털, 250/일 무료) |
| LLM | Claude Haiku 4.5 (요약 · 라벨링) · Sonnet 4.6 (심층 리포트) |
| Auth | Google OAuth 2.0 + JWT (access 15분 / refresh 30일) |
| Frontend | Next.js (정적 빌드 또는 SSR) — `myetf.app` |

---

## 빠른 시작 (로컬 개발)

```bash
# 1) 코드 번들 압축 해제
unzip myetf_code_assets.zip -d myetf && cd myetf

# 2) 가상환경
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r myetf_requirements.txt

# 3) MySQL 스키마
mysql -u root -p myetf < myetf_schema.sql

# 4) 환경변수 (.env)
cat > .env <<EOF
DATABASE_URL=mysql+asyncmy://myetf:secret@localhost/myetf
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-...
FINNHUB_API_KEY=...
GOOGLE_OAUTH_CLIENT_ID=...
JWT_SECRET=$(openssl rand -hex 32)
EOF

# 5) FastAPI
uvicorn myetf_main:app --reload --port 8000

# 6) Celery worker + beat (별도 터미널)
celery -A myetf_celery_tasks worker --loglevel=info
celery -A myetf_celery_tasks beat   --loglevel=info
```

API 문서: <http://localhost:8000/docs> (FastAPI 자동 OpenAPI)

---

## 운영 비용 (월간 추정)

| MAU | 인프라 | LLM (Haiku) | 외부 데이터 | 합계 |
|---:|---:|---:|---:|---:|
| 1 K | $0 (Oracle Free) | $7 | $0 | **$7** |
| 10 K | $0 | $150 | $30 (Tiingo) | **$167 ~ $300** |
| 100 K | $400 (paid VM) | $500 | $79 (Polygon) | **~$1,015** |

> Haiku prompt caching 50% 적용 시 LLM 비용 50% 절감 가능.

---

## 12개월 로드맵

| 분기 | 기간 | 마일스톤 | 성공 지표 |
|---|---|---|---|
| Q1 | M1-M3 | MVP — 섹터/종목 선택, 기본 시뮬레이션, Google 로그인 | 내부 테스터 50명, ETF 200개 생성 |
| Q2 | M4-M6 | 리밸런싱 알림, 뉴스 요약, Stripe 결제 | 유료 전환 30명, MAU 1,000명 |
| Q3 | M7-M9 | Web3Paper 연계, 백테스트, 공유 링크 | MAU 5,000명, ARR $5K |
| Q4 | M10-M12 | B2B2C API, 모바일 PWA, EN/ZH 다국어 | MAU 20,000명, ARR $30K |

---

## 컴플라이언스 / 면책

본 플랫폼은 한국 자본시장법상 **투자자문업 또는 로보어드바이저에 해당하지 않는 정보 제공 도구**로 설계됐다. 운영 시 반드시 다음을 준수해야 한다.

1. **종목을 추천하지 않는다** — 시스템은 데이터 표시만 수행하며, 종목 선택은 사용자 자유 의지.
2. **수익률을 보장하지 않는다** — 모든 시나리오는 *과거 변동성 + 컨센서스* 기반의 추정치이며, 미래 수익을 약속하지 않는다.
3. **주문 실행 기능이 없다** — 매매는 사용자가 별도 증권사에서 직접 실행한다.
4. **모든 응답에 면책 헤더** (`X-Disclaimer: Not investment advice; information only`) 가 자동 부착된다.

> ⚠️ **출시 전 권장**: 김앤장·세종·태평양 중 1곳에서 *시나리오 시뮬레이션이 자본시장법상 투자자문업에 해당하는지* 의견서 (200-500만원) 또는 금감원 비조치의견서 검토. 회색 지대일 경우 시나리오 표시를 *예측* 에서 *과거 변동폭 기반 분포 통계* 로 톤다운.

---

## 알려진 리스크 / 보강 예정

| 항목 | 심각도 | 대응 |
|---|---|---|
| yfinance 비공식 의존 | 🔴 | Polygon.io ($79/mo) 또는 Tiingo ($30/mo) 정식 라이센스 전환 |
| 자본시장법 회색지대 | 🔴 | 변호사 의견서 + 금감원 비조치의견서 |
| 변동성-only 리스크 모델 | 🟠 | 상관행렬 (cov matrix) 반영 + Monte Carlo 1000회 |
| 백테스트 부재 | 🟠 | v0.2 추가 (1주 작업) |
| Cold start UX 약함 | 🟠 | "투자 성향 3분 진단 → ETF 3개 자동 제안" 도입 |
| 모바일 우선 미설계 | 🟠 | PWA 우선 재설계 (Q4 → Q1 앞당김) |
| 단일 LLM 의존 | 🟡 | OpenRouter / Bedrock fallback 추가 |

---

## 연계 자산 (Dennis Kim / Betalabs)

본 프로젝트는 다음 기존 자산과 직접 연결된다.

- **virattt/ai-hedge-fund fork** — Multi-agent 분석 엔진을 ETF별 심층 리포트에 통합.
- **Multi-LLM Voting 프레임워크** — Claude vs GPT vs Gemini 의견 비교 뷰 = 핵심 차별화.
- **"같은 LLM, 다른 언어, 다른 답"** 논문 — Korean LLM bias 자동 측정 기능으로 학술 신뢰도 + 차별화.
- **Web3Paper (web3paper.net)** — KO/EN/ZH 멀티 언어 발행 채널, 마케팅 CAC 0.
- **STABLE1 / Web3 인프라** — v2 단계에서 ETF 토큰화 (ERC-20) 및 결제 통합.

---

## 메타

| 항목 | 값 |
|---|---|
| 프로젝트명 | MyETF Builder (가칭) |
| 버전 | v0.1 (Concept + DevSpec + Code Skeleton) |
| 작성일 | 2026-05-10 |
| 작성자 | Dennis Kim (김호광) / Cyworld CEO, Betalabs Inc. |
| 분류 | 내부 기획 — 외부 공개용 컨셉 (외부 공개 시 Web3Paper 라이선스 적용) |

---

© 2026  본 문서는 스터티 케이스이며, 투자는 전문적인 투자 전문가와 세금 전문가의 조언이 필요하며, 본 프로젝트는 투자자문이 아닙니다.
