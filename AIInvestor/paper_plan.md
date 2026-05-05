# AI Investor — 아키텍처 및 개발 계획

**서비스 코드명**: AI Investor (jeunggwon chatbot)
**소유자**: 김호광 (Dennis Kim)
**문서 버전**: 2.0 — 2026-05-05
**문서 범위**: 현재 구현된 텔레그램 MVP의 기술 검토 + Azure 서버리스/CDN 기반 v1 설계 + 사용자 플로우 정의 + 향후 확장 로드맵
**연구 동반 문서**: 본 문서 §13 *Empirical Validation of Semantic Edge Caching for Repetitive LLM Queries* (IEEE Trans. Cloud Computing 투고 예정)

---

## 0. Executive Summary

AI Investor는 **유명 투자자 페르소나로 미국 시황(NASDAQ / S&P 500)을 해설하는 텔레그램 챗봇**입니다. 현재 구현은 단일 프로세스 폴링 방식의 Python MVP이며, 1차 운영 목표는 **Azure 서버리스(Functions Flex Consumption) + Azure CDN** 기반의 저비용 상시 가동 형태로 이전하는 것입니다. 사용자는 봇에 입장 → 서비스 설명 → 페르소나 선택 → 오늘의 시황 리포트 수신 → 자유 질의의 5단계 플로우로 진행하며, 모든 LLM 호출은 DeepSeek (`deepseek-chat` / `deepseek-reasoner`)에 위임합니다.

본 문서는 다음 다섯 가지를 한 곳에 통합합니다.

1. **MVP 아키텍처 도식 + 모듈 책임 (§1–4)**
2. **현재 소스 코드의 기술 검토 결과 — 발견된 이슈 및 우선순위 (§5)**
3. **사용자 플로우 5단계 정의 (§6)**
4. **Azure 서버리스 + CDN 마이그레이션 설계 (§7–11)**
5. **연구 데이터 수집 계획 (§13, 학술 논문용)**

---

## Table of Contents

1. [현재 시스템 (MVP) 개요](#1-현재-시스템-mvp-개요)
2. [모듈 구조 및 책임](#2-모듈-구조-및-책임)
3. [데이터 흐름 — 단일 메시지 처리](#3-데이터-흐름--단일-메시지-처리)
4. [현재 의존성 및 환경](#4-현재-의존성-및-환경)
5. [기술 검토 / 코드 리뷰](#5-기술-검토--코드-리뷰)
6. [사용자 플로우](#6-사용자-플로우)
7. [Azure 서버리스 + CDN 목표 아키텍처](#7-azure-서버리스--cdn-목표-아키텍처)
8. [Azure 리소스 목록 및 비용 가이드](#8-azure-리소스-목록-및-비용-가이드)
9. [배포 파이프라인](#9-배포-파이프라인)
10. [관측성·로깅·시크릿](#10-관측성로깅시크릿)
11. [개발 로드맵](#11-개발-로드맵)
12. [리스크 및 미해결 항목](#12-리스크-및-미해결-항목)
13. [연구 데이터 수집 계획 (학술 동반 자료)](#13-연구-데이터-수집-계획-학술-동반-자료)

---

## 1. 현재 시스템 (MVP) 개요

### 1.1 한 줄 정의

> Telegram 메시지를 받아 yfinance 펀더멘털 스냅샷을 조회하고, DeepSeek LLM에 페르소나 시스템 프롬프트와 함께 던져 한국어/영어 시황 해설을 회신하는 단일 프로세스 봇.

### 1.2 시스템 구성도 (현재)

```
┌──────────────┐         ┌────────────────────────────┐
│   Telegram    │ HTTPS  │   AI Investor (local)       │
│   사용자       ├───────▶│   python-telegram-bot v22   │
└──────────────┘ getUpd. │   (long polling)            │
                          │                              │
                          │   ┌──────────────────────┐  │
                          │   │ services.stock_svc   │──┼──▶ Yahoo Finance (yfinance)
                          │   ├──────────────────────┤  │
                          │   │ services.persona_eng │──┼──▶ DeepSeek API
                          │   └──────────────────────┘  │
                          │                              │
                          └────────────────────────────┘
```

- **상태 저장소**: 없음 (페르소나 선택은 `chat_data` 인메모리 — 재시작 시 소실)
- **인증/시크릿**: `.env` 파일 (`TELEGRAM_BOT_TOKEN`, `DEEPSEEK_API_KEY`)
- **운영 형태**: 로컬 개발 머신 또는 단일 호스트에서 `python main.py` (긴 폴링)

### 1.3 현재 제공 기능

| 명령 | 동작 |
|---|---|
| `/start` | 환영 메시지 + 현재 페르소나 표시 |
| `/help` | 명령 목록 |
| `/personas` | 사용 가능한 페르소나 목록 |
| `/persona <key>` | 페르소나 전환 (`buffett` / `dalio` / `wood`) |
| 일반 텍스트 | 티커로 간주 → yfinance 조회 → 페르소나 해설 응답 |

### 1.4 의도적으로 *아직* 제공하지 않는 것

- 시황 일일 리포트 자동 생성/전송 (목표 플로우의 핵심, §6 참조)
- 멀티턴 대화 / 후속 질문 처리
- 페르소나 선택 UI (현재는 `/persona <key>` 명령 입력 필요)
- 사용자 개인 포트폴리오 연동
- 결제·구독

---

## 2. 모듈 구조 및 책임

### 2.1 디렉토리

```
AIInvestor/
├── main.py                       엔트리 포인트, DI 와이어링
├── config.py                     .env 로딩 + 로깅 설정
├── bot/
│   ├── __init__.py
│   └── telegram_handler.py       명령/메시지 라우팅, 페르소나 상태
├── services/
│   ├── __init__.py
│   ├── persona_engine.py         페르소나 정의 + DeepSeek 호출
│   └── stock_service.py          yfinance 스냅샷 + 1년치 기간변동률
├── requirements.txt
├── .env / .env.example
└── README.md (이 문서가 향후 통합되는 대상)
```

### 2.2 클래스 책임

| 클래스 / 함수 | 위치 | 역할 |
|---|---|---|
| `Config` | [config.py](config.py) | 환경변수 검증, `Config.load()` 가 부재 시 즉시 실패 |
| `Persona` | [services/persona_engine.py](services/persona_engine.py) | 키·이름·시스템 프롬프트의 불변 데이터 |
| `PERSONAS` (dict) | 동 파일 | 새 페르소나 추가는 dict 한 줄이면 자동으로 `/personas`/`/persona` 노출 |
| `PersonaEngine` | 동 파일 | OpenAI SDK로 DeepSeek 호출, 시스템 프롬프트 + 펀더멘털 블록 → 응답 |
| `StockSnapshot` | [services/stock_service.py](services/stock_service.py) | 21개 펀더멘털·가격 필드를 담는 dataclass |
| `StockService.get_snapshot` | 동 파일 | yfinance `info` + 1년치 종가에서 1M/6M/1Y 변동률 계산 |
| `BotDependencies` | [bot/telegram_handler.py](bot/telegram_handler.py) | 핸들러가 공유하는 의존성 묶음 |
| `build_application` | 동 파일 | python-telegram-bot Application 조립 |

### 2.3 페르소나 시스템 프롬프트의 안전 장치 (현행)

세 페르소나(Buffett / Dalio / Wood) 모두 다음 4가지를 시스템 프롬프트에서 강제:

1. **수치 환각 금지** — 제공된 데이터 블록 외의 수치 인용 불가
2. **명시적 매수/매도 권고 금지** — 'I'd be inclined to wait' 같은 stance 표현으로 우회
3. **마무리 면책** — `This is not financial advice.` 한 줄 강제
4. **role-play 톤** — 페르소나별 화법 규정

---

## 3. 데이터 흐름 — 단일 메시지 처리

```
User → Telegram → getUpdates → _on_message
   1. text = "AAPL"
   2. StockService.get_snapshot("AAPL")
      └─ yfinance.Ticker("AAPL").info       (HTTP)
      └─ yfinance.Ticker("AAPL").history()  (HTTP, 1y daily)
      └─ 1M/6M/1Y % change 계산
      → StockSnapshot
   3. PersonaEngine.generate(persona, snapshot)
      └─ OpenAI(base_url=https://api.deepseek.com).chat.completions.create()
      → str (LLM reply)
   4. update.message.reply_text(f"[{persona.display_name} on {ticker}]\n\n{reply}")
```

평균 지연 (현재):
- yfinance 2회 라운드트립: 0.5–1.5s
- DeepSeek `deepseek-chat`: 2–5s (출력 토큰 ~600)
- 합계 p50 ≈ **3–6초** (인터랙티브 봇 기준 허용 가능, 캐싱 도입 시 0.2–0.5s 목표)

---

## 4. 현재 의존성 및 환경

### 4.1 requirements.txt

```
python-telegram-bot>=20.7
openai>=1.40.0           # DeepSeek가 OpenAI-compatible이라 동일 SDK 사용
yfinance>=0.2.40
pandas>=2.0
python-dotenv>=1.0.0
```

### 4.2 환경 변수 ([.env.example](.env.example))

| 키 | 설명 | 필수 |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | @BotFather에서 발급 | 예 |
| `DEEPSEEK_API_KEY` | platform.deepseek.com/api_keys | 예 |
| `DEEPSEEK_BASE_URL` | 기본 `https://api.deepseek.com` | 아니오 |
| `DEEPSEEK_MODEL` | `deepseek-chat`(V3) 또는 `deepseek-reasoner`(R1) | 아니오 |
| `DEFAULT_PERSONA` | `buffett` / `dalio` / `wood` | 아니오 |
| `LOG_LEVEL` | `DEBUG`/`INFO`/`WARNING`/`ERROR` | 아니오 |

### 4.3 Python 호환성

코드 내부에 `from __future__ import annotations` 가 있어 Python 3.9에서도 PEP 604 union 어노테이션이 실행되지만, **타입 검사기(mypy 등) 사용 시에는 3.10+** 권장.

---

## 5. 기술 검토 / 코드 리뷰

현재 소스를 라인 단위로 점검한 결과를 우선순위별로 정리합니다.

### 5.1 즉시 수정 권고 (Severity: High)

| # | 위치 | 문제 | 권고 |
|---|---|---|---|
| H1 | [bot/telegram_handler.py:19](bot/telegram_handler.py#L19) | `DEFAULT_PERSONA_KEY` 를 import 하지만 사용처가 없음 | 죽은 import 제거 (linter가 잡아주지 못하는 이유는 tree에 등장하기 때문) |
| H2 | [main.py:40](main.py#L40) | `app.run_polling(allowed_updates=None)` — `None` 은 모든 업데이트 타입 허용. v1 운영 단계에서는 `["message"]` 등으로 좁혀서 텔레그램 측 부하/대역폭 절감 |
| H3 | [bot/telegram_handler.py:111](bot/telegram_handler.py#L111) | `_on_message` 가 입력을 항상 티커로 해석. "Tesla" / "엔비디아" 같은 회사명·한글·자유 질의 처리 분기 부재. §6 사용자 플로우의 "오늘의 리포트" / "추가 질문" 단계가 막힘 | 분류기 도입: (1) 정규식으로 티커 후보, (2) 그 외는 LLM 의도 분류 또는 룰 기반 키워드 매칭 |
| H4 | [services/stock_service.py:127](services/stock_service.py#L127) (`_safe_info`) | yfinance가 자주 던지는 `JSONDecodeError`/`HTTPError` 를 일반 `Exception` 으로 swallowing → 디버깅 어려움 | 구체적 예외 타입을 잡고 메트릭 카운터를 분리 (yfinance_failure_total) |
| H5 | [services/persona_engine.py:107](services/persona_engine.py#L107) | OpenAI 클라이언트가 동기 블로킹 호출. python-telegram-bot v22는 asyncio 기반이므로 LLM 호출 동안 이벤트 루프 블록됨. 동시 사용자 ≥ 2 시 응답 지연이 누적 | `AsyncOpenAI` 로 교체 + `await` 또는 최소한 `asyncio.to_thread(...)` 로 격리 |

### 5.2 중간 우선순위 (Severity: Medium)

| # | 위치 | 문제 | 권고 |
|---|---|---|---|
| M1 | [bot/telegram_handler.py:107](bot/telegram_handler.py#L107) | `chat_data` 에 페르소나 저장 — 프로세스 재시작 시 소실. 서버리스 환경에서는 매 요청 콜드 가능 | 영구 저장소(Cosmos DB / Table Storage)로 이전 |
| M2 | [services/stock_service.py:79](services/stock_service.py#L79) (`_normalize`) | `query.strip().upper().split()[0]` — 한글 회사명 입력 시 그대로 대문자화되어 yfinance가 못 찾음 | 회사명 → 티커 매핑 테이블 (S&P 500 + NASDAQ 100 ~600개 정도면 충분) |
| M3 | [services/persona_engine.py:107](services/persona_engine.py#L107) | LLM 응답에 timeout/retry 부재. DeepSeek 측 일시 장애 시 사용자가 30s 이상 대기 | `timeout=20`, 재시도 1회, 실패 시 fallback 메시지 |
| M4 | [services/stock_service.py:103](services/stock_service.py#L103) (`history`) | 모든 메시지마다 1년치 일봉을 다시 받음 (수십 KB × 호출 수) | 동일 티커 5분 캐싱 (인메모리 → 추후 Azure Cache for Redis) |
| M5 | [bot/telegram_handler.py:147](bot/telegram_handler.py#L147) | `_on_error` 가 모든 예외를 로깅만 — 사용자에게는 응답이 안 감 | 사용자에게 일반화된 사과 메시지 회신 추가 |

### 5.3 낮은 우선순위 (Severity: Low / Nice-to-have)

| # | 항목 | 권고 |
|---|---|---|
| L1 | 페르소나 시스템 프롬프트가 영어로만 작성 | 한국어 사용자를 위해 시스템 프롬프트 끝에 "Respond in the language of the user's most recent message" 추가 |
| L2 | 페르소나 3종만 존재 | 추가 후보: Charlie Munger, Peter Lynch, Howard Marks, 한국 가치투자자 등 |
| L3 | 단위 테스트 부재 | 최소한 `StockSnapshot.to_prompt_block()` 과 `_normalize` 의 pytest 추가 |
| L4 | `requirements.txt` 미고정 | `pip-compile` 로 `requirements.lock` 생성 — 재현성 확보 |

### 5.4 보안 / 컴플라이언스 점검

| 항목 | 상태 |
|---|---|
| `.env` 가 `.gitignore` 에 포함 | ✅ 루트 + AIInvestor 양쪽 |
| 키가 git 히스토리에 노출된 적 있는지 | ✅ 0건 |
| `.env` 파일 권한 | ✅ `0600` |
| 시크릿이 로그에 출력되는지 | ⚠ [main.py:34](main.py#L34) 가 `base_url` 만 로깅, 토큰은 노출되지 않음 — OK. 다만 `python-telegram-bot` 라이브러리가 디버그 레벨에서 토큰을 URL로 찍는 케이스 있음 → 로그 레벨을 INFO로 유지 |
| 페르소나 프롬프트 인젝션 | ⚠ 사용자 입력이 LLM `user` 메시지에 그대로 들어가지만, 시스템 프롬프트가 강하게 잠겨 있어 영향 제한적. 그래도 `</system>` 류 토큰은 sanitize 권장 |

### 5.5 종합 의견

현재 코드는 **MVP로서는 깔끔하고 모듈 분리도 합리적**이지만, 운영 단계로 진입하려면 위의 H1–H5 다섯 가지를 먼저 해결해야 합니다. 특히 **H5 (블로킹 LLM 호출)** 은 동시 사용자가 두 자릿수만 되어도 체감 응답이 무너지는 구조입니다.

---

## 6. 사용자 플로우

### 6.1 6단계 골든 패스 (1차 작업 범위)

```
[1] 인사            → /start 또는 봇 추가
                       "안녕하세요, AI Investor 입니다."
                       "당신만의 투자 멘토 페르소나로 매일의 미국 시황을 해설해 드립니다."

[2] 소개            → 자기소개 + 면책 + 데이터 출처 (1회 노출)
                       "yfinance · DeepSeek 기반 / 투자 자문 아님"
                       [버튼] "페르소나 고르고 시작하기"

[3] 페르소나 선택   → 인라인 키보드
                       [Warren Buffett] [Ray Dalio] [Cathie Wood]
                       선택 → 사용자 프로필에 영속 저장 (Cosmos / SQLite)
                       (재선택은 /persona 또는 메뉴 버튼)

[4] 오늘의 리포트   → "오늘의 리포트가 준비되어 있습니다. 받아보시겠어요?"
                       [예, 보기] [건너뛰기]
                       "예" 선택 시 → INTEGRATED_MARKET_PROMPT 실행
                         • S&P 500 / NASDAQ 종합 / NDX 일일 변동
                         • 상승 Top 5 / 하락 Top 5 (NASDAQ-100 기준)
                         • 거시 이슈 1–2개
                         • 페르소나 시각의 한 줄 시황 해설

[5] 관심사 획득     → "주로 어떤 분야/종목에 투자하시나요?"
                       (자유 입력 또는 인라인 키보드 멀티 선택)
                       예: "AI 반도체", "배당주", "BTC 관련주", "ETF",
                            "TSLA · NVDA · AAPL"
                       파싱 후 사용자 프로필에 태그 + 티커 리스트로 저장

[6] 기억 기반 소통  → 이후 모든 대화에서 다음을 자동 적용:
                       • 매일 첫 인사 시 사용자 관심사 우선 언급
                         "오늘 NVDA가 +3.2% 올랐어요. AI 반도체 섹터가 …"
                       • 사용자가 "오늘 어때?" 같은 모호한 질의 시
                         관심 종목·태그 기준으로 응답 구성
                       • 페르소나 교체 명령 시 인사 + 관심사는 그대로 유지
                         "✓ Ray Dalio 로 페르소나가 변경됐습니다.
                          (관심 분야: AI 반도체, ETF — 그대로 유지)"
```

식별 키:
- **Telegram 사용자**: `update.effective_user.id` (Telegram 정수 id)
- **모바일/웹 (Phase 4)**: 클라이언트가 발급한 UUIDv4
- 두 식별자 모두 §13.4 의 SHA-256 salt rotation 으로 익명화하여 저장 (§5.4 참고)

### 6.2 단계 매핑 — 구현 위치

| 단계 | 현재 구현 | 1차 작업 변경/신규 |
|---|---|---|
| [1] 인사 | `_cmd_start` ([bot/telegram_handler.py:60](bot/telegram_handler.py#L60)) | 메시지 한국어화 + 인라인 키보드로 다음 단계 유도 |
| [2] 소개 | 없음 | 신규 — 자기소개 + 면책 + `/policy` 명령 (1회만 자동 노출, `users.intro_seen` 플래그로 트래킹) |
| [3] 페르소나 | `_cmd_persona` (텍스트 명령만) | `InlineKeyboardMarkup` + `CallbackQueryHandler` + 영속 저장 |
| [4] 리포트 | 없음 | 신규 — `services/market_report.py` 추가 |
| [5] 관심사 획득 | 없음 | 신규 — 자유 텍스트 파싱 + 키워드 정규화 + 티커 매칭 |
| [6] 기억 기반 소통 | `chat_data` 인메모리 (M1 — 재시작 시 소실) | 신규 — `services/user_profile.py` + 영속 저장소 |

### 6.3 영속 저장소 — `users` 컨테이너 / 테이블

1차 작업에서는 단순화를 위해 **로컬 SQLite** (`./data/aiinvestor.db`) 로 구현하고, 2차 작업의 Azure 이전 시 **동일 스키마를 Cosmos DB 컨테이너**로 이주합니다.

```sql
-- users
CREATE TABLE users (
  user_key            TEXT PRIMARY KEY,    -- 'tg:<telegram_id>' 또는 'uuid:<v4>'
  anon_user_id        TEXT NOT NULL,       -- §13.4 SHA-256(salt + user_key)[:16]
  persona_key         TEXT NOT NULL DEFAULT 'buffett',
  intro_seen          INTEGER NOT NULL DEFAULT 0,
  research_consent    INTEGER NOT NULL DEFAULT 0,
  interest_tags       TEXT,                -- JSON array, e.g. ["AI 반도체","ETF"]
  watchlist_tickers   TEXT,                -- JSON array, e.g. ["NVDA","TSLA"]
  language            TEXT NOT NULL DEFAULT 'ko',
  created_at          TEXT NOT NULL,
  updated_at          TEXT NOT NULL
);
```

Cosmos DB 매핑 (2차 작업):

| SQLite | Cosmos DB |
|---|---|
| 테이블 `users` | 컨테이너 `users`, partition key `/anon_user_id` |
| `interest_tags`, `watchlist_tickers` JSON 문자열 | 네이티브 배열 필드 |
| `created_at` / `updated_at` ISO8601 | 동일 |

### 6.4 신규 모듈 — `services/user_profile.py` 설계 (1차 작업)

```python
@dataclass
class UserProfile:
    user_key: str
    anon_user_id: str
    persona_key: str
    intro_seen: bool
    research_consent: bool
    interest_tags: list[str]
    watchlist_tickers: list[str]
    language: str
    created_at: datetime
    updated_at: datetime

class UserProfileRepo:
    def get_or_create(self, user_key: str) -> UserProfile: ...
    def set_persona(self, user_key: str, persona_key: str) -> None: ...
    def mark_intro_seen(self, user_key: str) -> None: ...
    def add_interests(self, user_key: str, tags: list[str], tickers: list[str]) -> None: ...
    def update_consent(self, user_key: str, consent: bool) -> None: ...
```

구현은 **SQLite (1차) → Cosmos DB (2차)** 모두 동일 인터페이스(`UserProfileRepo`) 를 노출하도록 abstract base + 두 구현체로 분리. `config.py` 에 `STORAGE_BACKEND=sqlite|cosmos` 환경 변수로 스위치.

### 6.5 신규 모듈 — `services/market_report.py` 설계 (1차 작업)

```python
@dataclass
class MarketReport:
    date: str                      # "2026-05-05"
    sp500_close: float
    sp500_change_pct: float
    nasdaq_close: float
    nasdaq_change_pct: float
    ndx_close: float
    ndx_change_pct: float
    top_gainers: list[TickerMove]   # 5
    top_losers: list[TickerMove]    # 5
    macro_headlines: list[str]      # 1–2
    persona_commentary: str         # LLM 생성 (페르소나 + 사용자 관심사 반영)

class MarketReportService:
    def build(self, persona: Persona, profile: UserProfile) -> MarketReport: ...
```

데이터 소스:
- 인덱스 종가 — yfinance `^GSPC`, `^IXIC`, `^NDX`
- 종목 등락 — NASDAQ-100 100개 일괄 다운로드 ([QQQUpDownSignal/qqq_up_down_signal.py](../QQQUpDownSignal/qqq_up_down_signal.py) 재사용)
- 거시 헤드라인 — 1차에서는 LLM에 위탁, 2차에서 NewsAPI/RSS 도입

1차 작업에서의 캐싱: 단일 프로세스 인메모리 `dict[date, MarketReport]` (TTL 24h).
2차 작업에서의 캐싱: §7.4 의 **Timer Trigger 사전 생성 + Blob/CDN** 으로 승격.

### 6.6 인라인 키보드 예시

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def persona_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Warren Buffett (장기 가치)", callback_data="persona:buffett")],
        [InlineKeyboardButton("Ray Dalio (매크로/올웨더)",   callback_data="persona:dalio")],
        [InlineKeyboardButton("Cathie Wood (혁신 성장)",     callback_data="persona:wood")],
    ])

def report_offer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("예, 보기",   callback_data="report:show"),
         InlineKeyboardButton("건너뛰기",   callback_data="report:skip")],
    ])

INTEREST_PRESETS = ["AI 반도체", "빅테크", "배당주", "ETF",
                     "BTC 관련주", "원자재/에너지", "헬스케어", "직접 입력"]
```

콜백은 `CallbackQueryHandler` 가 처리하며, 영속 저장소(`UserProfileRepo`) 에 즉시 반영. 페르소나 교체 시 `interest_tags` / `watchlist_tickers` 는 그대로 유지하고 인사말만 갱신.

---

## 7. Azure 서버리스 + CDN 목표 아키텍처

### 7.1 v1 시스템 구성도

```
                    ┌──────────────────────────────────────────────┐
                    │  Azure                                       │
                    │                                              │
   Telegram         │  ┌──────────────┐    ┌──────────────────┐   │
   Bot Webhook  ───▶│ ─│ App Gateway  │───▶│ Azure Functions  │   │
   (HTTPS)          │  │ + WAF        │    │ (Flex Consumption)│  │
                    │  └──────────────┘    │  - bot_webhook    │  │
                    │                       │  - daily_report   │  │
                    │                       │  - timer_warmup   │  │
                    │                       └────────┬─────────┘   │
                    │                                │              │
                    │           ┌────────────────────┼────────┐    │
                    │           ▼                    ▼        ▼    │
                    │  ┌──────────────┐  ┌──────────────┐  ┌────┐ │
                    │  │ Cosmos DB    │  │ Blob Storage │  │ KV │ │
                    │  │ (users,      │  │ (daily       │  │    │ │
                    │  │  reports)    │  │  reports)    │  │    │ │
                    │  └──────────────┘  └──────┬───────┘  └────┘ │
                    │                           │                  │
                    │                           ▼                  │
                    │                    ┌─────────────┐           │
                    │                    │ Azure CDN   │           │
                    │                    │ (Standard)  │           │
                    │                    └──────┬──────┘           │
                    └───────────────────────────┼──────────────────┘
                                                │
                                  외부 cache 레이어 (TTL 1h)
                                                │
                                                ▼
                                     모바일 앱 / 웹 (장래)
```

### 7.2 컴포넌트 매핑

| 책임 | Azure 서비스 | 비고 |
|---|---|---|
| HTTPS 엔드포인트 (Telegram Webhook 수신) | Azure Functions HTTP Trigger | `setWebhook` 으로 텔레그램이 호출 |
| 봇 비즈니스 로직 | Azure Functions (Python 3.11 isolated worker) | 현재 코드의 `bot/`, `services/` 그대로 이전 |
| 일일 리포트 사전 생성 | Azure Functions Timer Trigger (`0 30 6 * * *` KST = 21:30 UTC, 미국 시장 마감 30분 후) | 결과를 Blob에 JSON 업로드 |
| 사전 생성된 리포트 서빙 | Azure Blob → Azure CDN (Standard Microsoft tier) | TTL 1시간, 동일 KST 일자 동안 재사용 |
| 사용자 상태 (페르소나, 동의 기록) | Azure Cosmos DB (Serverless) | 컨테이너 `users`, 파티션 `/anon_user_id` |
| 시크릿 관리 | Azure Key Vault | Functions가 Managed Identity로 참조 |
| 관측 | Application Insights | 자동 통합, 비용 최저 티어 |

### 7.3 Telegram Webhook 모드로 전환

현재 `app.run_polling()` ([main.py:40](main.py#L40)) 은 Functions에서 동작 불가. 전환 작업:

```python
# function_app.py (Azure Functions Python v2 model)
import azure.functions as func
from telegram import Update
from telegram.ext import Application

app_func = func.FunctionApp()
ptb_app: Application = build_application(token, deps)

@app_func.route(route="telegram/webhook", auth_level=func.AuthLevel.ANONYMOUS)
async def telegram_webhook(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    update = Update.de_json(body, ptb_app.bot)
    await ptb_app.process_update(update)
    return func.HttpResponse(status_code=200)
```

배포 후 1회 실행:

```bash
curl -F "url=https://<func-app>.azurewebsites.net/api/telegram/webhook" \
     -F "secret_token=<random32hex>" \
     "https://api.telegram.org/bot<TOKEN>/setWebhook"
```

`secret_token` 은 Telegram이 매 호출 헤더 `X-Telegram-Bot-Api-Secret-Token` 에 실어 보내며, Functions에서 검증 → 외부 위조 호출 차단.

### 7.4 일일 리포트 사전 생성 + CDN 캐시

```
KST 06:30 (UTC 21:30 — 미장 마감 직후)
┌──────────────────────────────┐
│ Timer Trigger Function        │
│  1. yfinance 인덱스/NDX-100   │
│  2. DeepSeek로 페르소나별 3개 │
│     리포트 생성               │
│  3. Blob 업로드:              │
│     reports/2026-05-05/       │
│       buffett.json            │
│       dalio.json              │
│       wood.json               │
│  4. CDN purge (해당 path)     │
└──────────────────────────────┘

사용자가 [예, 보기] 누르면:
  Functions가 Blob URL이 아닌 CDN URL을 사용자 메시지로 회신/렌더
  → 동일 일자 같은 페르소나 N명 사용자 → CDN edge에서 응답 (Functions 재실행 X)
```

**캐시 효과 정량 추정 (DAU 1,000, 페르소나 3, 일 1회 리포트 조회 가정):**
- 캐시 없음 시: 1,000회 LLM 호출 × $0.001 ≈ $1/일
- CDN 적중 시: **3회** 사전 생성 × $0.001 ≈ $0.003/일 (99.7% 절감)

이 캐싱 효과 자체가 §13 학술 동반 자료의 검증 대상.

### 7.5 Functions 콜드 스타트 대응

Flex Consumption은 콜드 스타트 1–3초. 봇 응답에 치명적이므로:

1. **Always Ready instances = 1** 설정 (월 추가 비용 ~$13)
2. 또는 5분마다 셀프-핑하는 Timer Trigger
3. 일일 리포트는 콜드 스타트 영향 없음 (timer 자체가 콜드)

### 7.6 환경 분리

| 환경 | Function App | Bot Token | DeepSeek Key |
|---|---|---|---|
| dev | `aiinvestor-dev` | `@AI_vibe_investor_dev_bot` (별도 발급) | 동일 키 (저비용) |
| prod | `aiinvestor-prod` | `@AI_vibe_investor_bot` (현재 실서비스) | 별도 키 |

GitHub Actions가 `main` 브랜치는 prod로, `dev` 브랜치는 dev로 배포.

---

## 8. Azure 리소스 목록 및 비용 가이드

### 8.1 리소스 목록 (1 RG 권장)

```
rg-aiinvestor-prod
├── func-aiinvestor-prod              Function App (Flex Consumption, Linux)
├── plan-aiinvestor-prod              App Service Plan (Flex)
├── st-aiinvestor-prod                Storage Account (Functions runtime + reports blob)
├── cdn-aiinvestor-prod               CDN Profile + endpoint
├── cosmos-aiinvestor-prod            Cosmos DB (Serverless, NoSQL API)
├── kv-aiinvestor-prod                Key Vault
└── appi-aiinvestor-prod              Application Insights
```

### 8.2 월간 비용 추정 (DAU 100 기준)

| 항목 | 사용량 추정 | 월 비용 |
|---|---|---|
| Functions Flex (always-ready 1) | ~$13 |
| Functions per-execution | 100 DAU × 5건/일 × 30일 = 15,000 호출 | ~$0.50 |
| Cosmos DB Serverless | 100 사용자 × 5 RU/req × 15K req | ~$1 |
| Blob Storage | 90일 × 3 페르소나 × 50KB JSON ≈ 13.5 MB | ~$0.01 |
| Azure CDN Standard Microsoft | 5 GB egress | ~$0.40 |
| Application Insights | 1 GB ingestion | $0 (free tier) |
| Key Vault | 키 5개, 호출 1만회 | ~$0.30 |
| **합계** | | **~$15/월** |
| DeepSeek API | 사전 생성 일 3회 + 사용자 질의 100×5×30 | ~$2/월 |
| **총합** | | **~$17/월** |

DAU 1,000 까지 확장 시 LLM 비용이 가장 빠르게 늘어나므로 §13의 의미적 캐싱이 비용 곡선 평탄화의 핵심.

---

## 9. 배포 파이프라인

### 9.1 GitHub Actions 워크플로 (개요)

```yaml
# .github/workflows/deploy.yml (요약)
name: deploy-aiinvestor
on:
  push:
    branches: [main, dev]
    paths: ['AIInvestor/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r AIInvestor/requirements.txt -t AIInvestor/.python_packages/lib/site-packages
      - uses: azure/login@v2
        with: { creds: ${{ secrets.AZURE_CREDENTIALS }} }
      - uses: azure/functions-action@v1
        with:
          app-name: ${{ github.ref_name == 'main' && 'func-aiinvestor-prod' || 'func-aiinvestor-dev' }}
          package: AIInvestor
          scm-do-build-during-deployment: true
```

### 9.2 인프라 코드 (Bicep 권장)

`infra/main.bicep` 에서 §8.1 리소스를 모두 선언. `azd up` 한 번으로 RG 전체 프로비저닝.

### 9.3 시크릿 흐름

```
.env (로컬 개발)
└── git에 절대 커밋 X (.gitignore)

Azure Key Vault
├── telegram-bot-token
├── deepseek-api-key
└── telegram-webhook-secret

Function App
├── Managed Identity 활성화
├── Key Vault에 RBAC: Key Vault Secrets User
└── App Settings에 Key Vault reference
    예: TELEGRAM_BOT_TOKEN=@Microsoft.KeyVault(SecretUri=https://kv-aiinvestor-prod.vault.azure.net/secrets/telegram-bot-token/)
```

---

## 10. 관측성·로깅·시크릿

### 10.1 로깅 정책

| 레벨 | 용도 | PII 포함 |
|---|---|---|
| ERROR | 예외, 외부 API 실패 | ❌ |
| WARNING | 재시도 발생, fallback 응답 | ❌ |
| INFO | 요청 1줄 (anon_user_id, channel, command, latency_ms, cache_hit) | ❌ |
| DEBUG | 페이로드 (개발 환경에서만) | ⚠ 최소화 |

### 10.2 핵심 메트릭 (Application Insights)

- `request.latency_ms` (p50/p95/p99)
- `llm.deepseek.tokens_in`, `llm.deepseek.tokens_out`, `llm.deepseek.cost_usd`
- `cache.hit_rate` (CDN + 의미적 캐시 분리)
- `yfinance.failure_total`
- `persona.distribution` (어느 페르소나가 자주 쓰이는지)
- `flow.dropoff` (사용자 플로우 5단계 중 어디서 이탈)

### 10.3 알람

- Functions error rate > 5% 5분간 → Slack
- DeepSeek 호출 실패 > 10건/5분 → Slack
- Cosmos DB RU 사용량 > 80% → Slack

---

## 11. 개발 로드맵

본 로드맵은 **1차 / 2차 / 후속(3·4차)** 의 3-tier 우선순위로 정리합니다. **1차 = 기능 완결 (로컬)**, **2차 = 클라우드 이전 (Azure 서버리스 + CDN)**, 후속 = 학술 데이터 수집 / 멀티 채널.

---

### 🥇 1차 작업 — 6단계 사용자 플로우 + 영속 메모리 (로컬에서 완성)

**목표**: 사용자가 봇과 처음 대화하기 시작해서 페르소나 교체까지 모든 인터랙션이 정상 동작하고, 사용자 관심사가 영구 기억되는 단일 프로세스 봇.
**환경**: 로컬 또는 단일 호스트, SQLite 기반 영속화. Azure 미사용.
**완료 기준**:
- §6.1 의 [1]–[6] 단계가 모두 텔레그램에서 동작
- 봇 재시작해도 페르소나·관심사가 유지됨
- 페르소나 교체 시 관심사 컨텍스트는 보존

#### 1차-A: 기술 부채 해소 (운영 적합성)

- [ ] **H5 — 비동기 LLM 전환**: `OpenAI` → `AsyncOpenAI`, `generate()` 를 `async def` 로 변경 후 `_on_message` 에서 `await` ([services/persona_engine.py:87](services/persona_engine.py#L87))
- [ ] **H3 — 의도 분류 분기**: `_on_message` 가 입력을 (a) 티커 후보 정규식 → yfinance, (b) 한글 회사명 → 매핑 테이블, (c) 그 외 자유 질의 → LLM Q&A 모드로 분기 ([bot/telegram_handler.py:111](bot/telegram_handler.py#L111))
- [ ] **H2 — `allowed_updates`** 좁히기: `["message", "callback_query"]` ([main.py:40](main.py#L40))
- [ ] **H1 — dead import 제거**: `DEFAULT_PERSONA_KEY` ([bot/telegram_handler.py:19](bot/telegram_handler.py#L19))
- [ ] **H4 — yfinance 예외 세분화**: 카운터 분리 ([services/stock_service.py:127](services/stock_service.py#L127))
- [ ] **M5 — `_on_error` 사용자 회신** ([bot/telegram_handler.py:147](bot/telegram_handler.py#L147))

#### 1차-B: 영속 저장소 — `UserProfileRepo` (SQLite)

- [ ] `services/user_profile.py` — `UserProfile` 데이터클래스 + `UserProfileRepo` 추상 인터페이스 (§6.4)
- [ ] `services/user_profile_sqlite.py` — SQLite 구현체 (`./data/aiinvestor.db`), 첫 실행 시 테이블 자동 생성 + `anon_user_id` 인덱스
- [ ] `anon_user_id` 생성 — SHA-256 with local salt (`.env` 의 `USER_ID_SALT`)
- [ ] DI 와이어링 — `BotDependencies` 에 `profile_repo: UserProfileRepo` 추가 ([bot/telegram_handler.py:32](bot/telegram_handler.py#L32))

#### 1차-C: 6단계 플로우 구현

- [ ] **[1] 인사** — `_cmd_start` 한국어화 + 다음 단계 인라인 키보드
- [ ] **[2] 소개** — `intro_seen=0` 사용자에게만 1회, 면책 + 데이터 출처 + `/policy` 명령
- [ ] **[3] 페르소나 선택** — `InlineKeyboardMarkup` + `CallbackQueryHandler("persona:*")` → `profile_repo.set_persona()`
- [ ] **[4] 오늘의 리포트** — `services/market_report.py` 신설 (§6.5), `[예/건너뛰기]` 버튼, 응답 끝에 [5]로 자연 전이
- [ ] **[5] 관심사 획득** — 자유 텍스트 입력 + 프리셋 버튼(`INTEREST_PRESETS`), 파싱 → `interest_tags` / `watchlist_tickers` 분리 저장
- [ ] **[6] 기억 기반 소통** — 모든 LLM 호출 시 user prompt 에 사용자 관심사 컨텍스트 주입; 모호 질의("오늘 어때?") 는 `watchlist_tickers` 우선 응답

#### 1차-D: 페르소나 교체 컨텍스트 보존

- [ ] `/persona <key>` 또는 인라인 키보드 재선택 시 `persona_key` 만 갱신, `interest_tags` / `watchlist_tickers` 보존
- [ ] 교체 직후 인사말 — "✓ {새 페르소나} 로 변경됐습니다. 관심 분야: {tags} — 그대로 유지"

#### 1차-E: 검증

- [ ] **L3 — pytest 추가**: `UserProfileRepo` (in-memory SQLite로 격리), `MarketReportService.build()` (mock yfinance), `intent_classifier`
- [ ] **L4 — `requirements.lock`** 생성 (`pip-compile`)
- [ ] **종단 시나리오**: 봇 재시작 후 동일 텔레그램 사용자가 (a) 페르소나 유지, (b) 관심사 회상, (c) 페르소나 교체 후에도 관심사 유지 — 수동 통과

---

### 🥈 2차 작업 — Azure Functions Flex Consumption + CDN 이전

**목표**: 1차 결과물을 **그대로** Azure 서버리스로 이전하고, 일일 리포트를 CDN 사전 캐싱하여 LLM 호출량 99%+ 절감.
**환경**: Azure (`rg-aiinvestor-prod`, §8.1). Telegram **Webhook 모드**.
**전제**: 1차 작업 완전 완료 — 코드 모듈은 그대로 두고 *runtime layer 만* 교체.
**완료 기준**:
- prod 환경에서 Functions 기반 봇이 24/7 응답 (always-ready 1)
- 일일 리포트가 KST 06:30 자동 생성되어 CDN edge에서 서빙
- 사용자 프로필이 Cosmos DB로 이전 완료, SQLite 백엔드는 dev 전용으로 잔존
- GitHub Actions가 main → prod, dev → dev 자동 배포

#### 2차-A: Functions 프로젝트 화

- [ ] `function_app.py` — Python v2 모델, `bot_webhook` (HTTP) + `daily_report` (Timer) + `keepalive` (Timer)
- [ ] Webhook 모드 — `app.run_polling()` 제거, `ptb_app.process_update(update)` 직접 호출 (§7.3)
- [ ] `setWebhook` 자동화 — 배포 직후 GitHub Actions가 `secret_token` 까지 함께 등록
- [ ] Webhook secret 검증 — `X-Telegram-Bot-Api-Secret-Token` 헤더 매칭 실패 시 401

#### 2차-B: 영속 저장소 SQLite → Cosmos DB

- [ ] `services/user_profile_cosmos.py` — Cosmos SDK 구현체 (1차의 `UserProfileRepo` 인터페이스 그대로)
- [ ] `STORAGE_BACKEND=cosmos` 환경변수로 자동 선택
- [ ] 일회성 마이그레이션 스크립트 — dev 단계 SQLite 데이터 → Cosmos
- [ ] **M1 해결 검증** — 콜드 스타트 후에도 페르소나/관심사 정확 회상 (통합 테스트)

#### 2차-C: Timer Trigger + Blob + CDN

- [ ] **Timer**: `0 30 6 * * *` (KST 06:30 = UTC 21:30, US 마감 30분 후)
- [ ] 페르소나 3종 × 일자별로 LLM 호출 → JSON → Blob `reports/<date>/<persona>.json`
- [ ] **Azure CDN Standard Microsoft** profile + endpoint, origin = Blob 컨테이너
- [ ] CDN purge — Timer 끝에서 신규 path 우선 캐싱
- [ ] [예, 보기] 클릭 시 Functions가 **CDN URL 의 JSON 을 fetch** → 페르소나 답변 렌더링 → Telegram 회신
- [ ] `cdn.hit_rate` App Insights 커스텀 메트릭

#### 2차-D: 인프라 코드 + 시크릿

- [ ] `infra/main.bicep` — §8.1 의 7개 리소스 모두 선언
- [ ] **Key Vault** 시크릿 — `telegram-bot-token`, `deepseek-api-key`, `telegram-webhook-secret`, `user-id-salt`
- [ ] Function App **Managed Identity** + KV RBAC (`Key Vault Secrets User`)
- [ ] App Settings 가 Key Vault reference 로 시크릿 주입 (`@Microsoft.KeyVault(...)`)
- [ ] **GitHub Actions** `.github/workflows/deploy.yml` (§9.1), main→prod / dev→dev
- [ ] dev/prod 환경 분리 — 별도 봇 토큰(`@AI_vibe_investor_dev_bot`), 별도 DeepSeek 키

#### 2차-E: 관측성

- [ ] App Insights 자동 통합 + 커스텀 메트릭: `request.latency_ms`, `llm.deepseek.tokens_*`, `cdn.hit_rate`, `flow.dropoff[1..6]`, `persona.distribution`
- [ ] Azure Monitor 알람: error rate > 5% / DeepSeek 실패 > 10건/5분 / Cosmos RU > 80% (§10.3)
- [ ] 비용 알람 — 월 예산 $30 임계 시 메일

#### 2차-F: 콜드 스타트 + 부하 검증

- [ ] **Always Ready instances = 1**
- [ ] `keepalive` Timer (5분)
- [ ] k6 또는 locust 부하 테스트 — 동시 50 사용자, p95 < 4초

---

### 🥉 후속 작업 (3·4차) — 학술 데이터 수집 / 모바일·멀티턴

> 1·2차 검수 후 별도 계획서로 분기. 본 항목은 §13 학술 동반 자료와 직접 연결됨.

**3차 — 의미적 캐싱 + 학술 데이터 수집**
- 4 컨테이너 (`research_query_embeddings`, `research_cache_events`, `research_latency`, `research_popularity_daily`) — §13.3
- Azure OpenAI `text-embedding-3-small` + DiskANN 벡터 인덱스
- 2-tier consent UI (operational / research-extended) — §13.5
- SHA-256 salt rotation 자동화 (Key Vault, 90일) — §13.4

**4차 — 모바일 + 멀티턴**
- React Native + Expo (iOS/Android) — 동일 백엔드 호출
- 멀티턴 컨텍스트 영속화 (`chat_history` 컨테이너, TTL 30일)
- 채널 비교 분석 (§13.7)

---

### 11.1 1차/2차 일정 가이드 (1인 풀타임 기준)

| 단계 | 예상 소요 | 비고 |
|---|---|---|
| 1차-A 기술 부채 | 2–3일 | H5 비동기 전환이 가장 큼 |
| 1차-B 영속 저장소 | 1–2일 | SQLite 단순 |
| 1차-C 6단계 플로우 | 3–5일 | InlineKeyboard + market_report 신규 |
| 1차-D 페르소나 보존 | 0.5일 | C와 함께 |
| 1차-E 검증 | 1–2일 | pytest + 수동 시나리오 |
| **1차 합계** | **약 8–13일** | |
| 2차-A Functions 화 | 2일 | |
| 2차-B Cosmos 이전 | 1–2일 | |
| 2차-C Timer + CDN | 2–3일 | |
| 2차-D 인프라 코드 | 2일 | Bicep 익숙도에 따라 변동 |
| 2차-E 관측성 | 1일 | |
| 2차-F 부하 검증 | 1일 | |
| **2차 합계** | **약 9–11일** | |

---

## 12. 리스크 및 미해결 항목

| 리스크 | 영향 | 완화 |
|---|---|---|
| yfinance가 비공식 API라 갑자기 차단/스로틀 | 데이터 공급 중단 | Polygon.io / Alpha Vantage / Finnhub 백업 supplier 준비 |
| DeepSeek API 가격 변동 / 서비스 정책 변경 | 비용 또는 가용성 | 환경 변수로 base_url + model 분리되어 있어 OpenAI / Anthropic 으로 즉시 스위치 가능 |
| 텔레그램 정책 변경 — 봇 metering | 운영 중단 | 모바일 앱 채널을 Phase 4에서 미리 구축 |
| LLM 환각으로 잘못된 수치 응답 | 사용자 손실 가능 | 시스템 프롬프트 + 데이터 블록 외 수치 사용 금지 + 면책 1줄 강제 (현행) |
| 한국 자본시장법 — 유사투자자문업 등록 의무 | 법적 리스크 | (1) "자문 아님" 면책 강조 (2) 매수/매도 추천 표현 금지 (이미 시스템 프롬프트에서 차단) (3) 변호사 검토 후 약관 작성 |
| Cosmos DB 비용 급증 (벡터 인덱스) | 월 비용 급등 | 90일 TTL + serverless tier로 상한 |

---

## 13. 연구 데이터 수집 계획 (학술 동반 자료)

> 이하 §13 은 IEEE Trans. Cloud Computing 투고 예정 논문 *"Semantic Edge Caching for Repetitive LLM Queries"* 의 동반 자료입니다. 본 챗봇 서비스 자체가 데이터 수집 플랫폼 역할을 합니다.

### 13.1 Abstract

This section specifies the data collection methodology for empirically validating the hypotheses presented in *"Semantic Edge Caching for Repetitive LLM Queries"*. Where the original paper relies primarily on simulation, this companion plan describes how the deployed AI Investor chatbot serves as a real-world data collection platform across two channels (Telegram and mobile native apps) under the low-cost serverless architecture defined in §7. The plan covers: (1) mapping of the paper's five core hypotheses to measurable signals, (2) anonymization and consent protocols satisfying Korean PIPA and GDPR, (3) Azure Cosmos DB schema with automatic TTL policies, (4) channel-stratified statistical analysis methods, and (5) ethics review preparation including IRB exemption justification.

**Keywords**: Semantic Caching, LLM Inference, CDN-inspired Architecture, Empirical Validation, Anonymized Telemetry, Multi-channel Data Collection

### 13.2 Hypothesis Mapping

| Paper Section | Claim | Measurement |
|---|---|---|
| §3 Query Repetition | Human queries follow repetitive statistical patterns | Repetition rate per command/ticker/hour |
| §4 Statistical Model | Query popularity follows Zipf distribution | Daily aggregation + MLE on Zipf exponent |
| §6 Semantic Cache Pipeline | Embedding ANN identifies semantically equivalent queries above threshold | Cosine similarity distribution + user feedback correlation |
| §7 Predictive Cache Warming | Trending signals enable proactive cache population | Pre-warming 30min before market open + A/B comparison |
| §11–14 Hit Rate / GPU / Cost / Energy | 60–90% hit rates → proportional savings | Direct measurement from `research_cache_events` + DeepSeek billing |

**Plan-introduced auxiliaries**:
- **H6 (Channel-clustered queries)**: Telegram vs. mobile distinguishable via KS test on length, command, time-of-day distributions.
- **H7 (Time-clustered queries)**: Same KST hour queries form semantic clusters in embedding space — silhouette score on K-means.

### 13.3 Cosmos DB 컨테이너 (4종)

`research_query_embeddings` (TTL 90d), `research_cache_events` (TTL 90d), `research_latency` (TTL 90d), `research_popularity_daily` (TTL 365d). 모든 컨테이너 partition key = `/date`, embedding 컨테이너만 DiskANN 벡터 인덱스.

스키마 상세는 (이전 v1.0 문서의 §4) 와 동일하며, 변경점은 다음 두 가지:
- 채널 enum에 `mobile_ios`, `mobile_android` 추가됨 (Phase 4)
- `model_used` 필드에 `cache | deepseek-v4-flash | deepseek-v4-pro` 외에 `cdn_warm` 추가 — §7.4 사전 생성 캐시 적중 케이스 구분용

### 13.4 익명화

```
anon_user_id = sha256(salt + ":" + raw_user_id)[0:16]
```

salt는 Azure Key Vault에 보관되어 로그에 절대 노출되지 않으며 90일 주기로 자동 rotation. PII 패턴(주민번호 / 카드번호 / 이메일) 정규식 redaction은 raw query text 저장 직전에 적용.

### 13.5 2-tier Consent

| Tier | 기본값 | 수집 |
|---|---|---|
| Operational | opt-out 만 가능 | anon_user_id, channel, command, embedding, cache event, latency, KST hour |
| Research-extended | opt-in | 위 + raw query text |

`/research_revoke` 명령으로 언제든 raw text 기록 일괄 삭제 가능 (anon_user_id 매칭).

### 13.6 첫 응답 시 1회 안내 (§6.4 / Phase 1과 결합)

```
"AI Investor를 사용해 주셔서 감사합니다.

• AI 응답에 오류가 있을 수 있습니다.
• 익명화된 사용 데이터가 서비스 개선과 학술 연구에 활용됩니다.
• 개인 정보는 식별 불가능한 형태로만 보관되며 90일 후 자동 삭제됩니다.
• 본 서비스는 투자 자문이 아닙니다.

[연구 데이터 수집에 추가 동의 — 가장 도움됩니다]
[운영 데이터만 — 기본]
[전체 정책 보기]"
```

### 13.7 채널 비교 분석 (H6)

| 차원 | 통계 검정 |
|---|---|
| 길이 분포 | Two-sample Kolmogorov–Smirnov |
| 시간대 분포 | Chi-square (24-bin histogram) |
| 캐시 적중률 | Two-proportion z-test |
| 지연시간 | Mann–Whitney U (heavy-tailed) |
| 페르소나 선호 | Chi-square independence |
| 후속 질의율 (60s 내) | Two-proportion z-test |

다중 검정 보정: Bonferroni (n=6).

### 13.8 통계 분석

- **Cache hit rate**: 7일 rolling, 95% Wilson score CI
- **Zipf fit**: MLE로 exponent s 추정, KS goodness-of-fit
- **Time clustering (H7)**: PCA 1536→50 + K-means K=24 + silhouette + UMAP 시각화
- **Pre-warming A/B**: day-level alternation, bootstrap CI
- **Cost / Energy**: DeepSeek billing 그대로, 에너지는 발표된 per-token 추정치

### 13.9 IRB / 컴플라이언스

| 관할 | 규정 | 적용 |
|---|---|---|
| 한국 | 개인정보보호법 (PIPA) | 1차 적용 |
| 한국 | 생명윤리법 (IRB) | 면제 신청 — 관찰적 telemetry, 익명화, 무중재 |
| EU | GDPR | EU 모바일 사용자 대비, 잊혀질 권리 §13.4 |
| US | Common Rule | 비적용, 단 substantive 요구사항 준수 |

**Exemption arguments**: (1) 무중재 관찰, (2) 식별 불가능한 정보, (3) Azure 표준 보호, (4) 최소 위험.

### 13.10 데이터 공개 계획

- 일일 집계 통계 (시간대별 hit rate, Zipf 파라미터) — IEEE Dataport CSV 부록
- De-identified 이벤트 데이터 — 별도 publication-specific salt로 재해시 후 controlled access
- Raw query text — **공개하지 않음**

### 13.11 Threats to Validity (Wohlin et al.)

- **Internal**: pre-warming은 user-level RCT가 아닌 day-level alternation
- **External**: 금융 도메인·한국어·텔레그램+모바일 mix 조건부 결과
- **Construct**: 캐시 임계값 0.93은 경험치 — 0.90/0.93/0.95 sensitivity 보고
- **Conclusion**: 다중 검정 — Bonferroni 또는 Benjamini–Hochberg

### 13.12 학술 일정

| 마일스톤 | 트리거 | 활동 |
|---|---|---|
| M1 텔레메트리 가동 | Phase 2 완료 | Cosmos 4 컨테이너 + 익명화 production |
| M2 텔레그램 30일 데이터 | M1 + 30일 | 사전 분석 |
| M3 모바일 출시 | Phase 4 완료 | 양 채널 동시 수집 |
| M4 충분한 모바일 표본 | M3 + 60일 | 채널 비교 가능 |
| M5 통계 분석 완료 | M4 + 30일 | §11–14 + H6/H7 |
| M6 논문 재투고 | M5 + 14일 | IEEE TCC 제출 |

M1 → M6 약 4개월, IRB 지연 시 +2–3개월.

---

**End of Document**

*수정·제안·재현 요청은 GitHub Issue로 부탁드립니다.*
