# 시간대별 리포트 생성 + 적응형 캐싱 정책

**문서 버전**: v1.0 (2026-05-06)
**관련 문서**:
- `ticker-data-caching-architecture-v1.0-ko.md` (옵션 C — 가벼운 ticker price 캐시)
- `paper_plan.md` §16 (사전 캐싱 데몬), §17.3 (usage logger + 대시보드)

---

## 0. TL;DR

| 결정 항목 | 값 |
|---|---|
| 일일 정기 리포트 슬롯 수 | **6개** (06/08/12/15:30/21/23 KST) |
| 슬롯당 자동 생성되는 리포트 수 | 페르소나 3 × 언어 4 = **12개** |
| 일일 총 자동 생성량 | 6 × 12 = **72 리포트 / 일** |
| 사용자 자주 묻는 종목 캐싱 대상 | **TOP_50 hot tickers** (페르소나별 commentary) |
| 슬롯간 캐시 hit 가능 사용자 비율 | **70–80%** (한국 retail 트래픽 패턴 기준) |
| 옵션 C 적용 후 평균 응답 시간 | 가중 평균 **~1.5초** (현재 캐시 적중 ~5–7초 대비) |
| 옵션 C 적용 후 LLM 호출 절감 | **약 88%** (사용자 요청 1,000건 → LLM 호출 120건 수준) |
| 추가 월 비용 | **~$10** (DeepSeek 72 ×30 = 2,160 호출 + Blob/Functions overhead) |

---

## 1. 시장 운영 시간 매핑 (KST 기준)

본 정책의 모든 시간은 KST 기준입니다.

| 시간대 (KST) | 한국 증시 | 미국 증시 | 활동 |
|---|---|---|---|
| 09:00–15:30 | **개장** | 휴장 (전일) | 한국 일 거래 |
| 15:30–22:30 | 마감 | 휴장 (개장 전) | 양 시장 모두 휴식 |
| 22:30–05:00 (翌日) | 마감 | **개장** (서머타임 시 23:30–06:00) | 미국 일 거래 |
| 05:00–09:00 (翌日) | 마감 | 마감 | 양 시장 모두 휴식 |

> **휴장 정의**:
> - 미국 시장: 토일 + 미국 공휴일 (Memorial Day, Independence Day, Thanksgiving 등)
> - 한국 시장: 토일 + 한국 공휴일 (설/추석/광복절 등)

---

## 2. 시간대별 리포트 스케줄 (6개 슬롯)

### 2.1 슬롯 정의

| # | 시간 (KST) | 슬롯 이름 | 콘텐츠 | 트리거 시점 |
|---|---|---|---|---|
| 1 | **06:00** | 🌅 미국 증시 마감 요약 | 전일 미국 시장 종합 — S&P/NASDAQ/NDX, Top 5 상승/하락, 주요 헤드라인 | 미국 마감(05:00) + 1시간 — yfinance EOD 데이터 안정화 후 |
| 2 | **08:00** | 🇰🇷 한국 증시 예측 | KOSPI/KOSDAQ 시작 전 미장 영향 + 환율 + 선물 + 주요 이슈 | 한국 개장(09:00) − 1시간 |
| 3 | **12:00** | 🇰🇷🇨🇳🇯🇵 한국 오전 + 아시아 요약 | KOSPI 오전 + 닛케이 + 항셍 + 환율 | 한국 점심 휴장 직전 |
| 4 | **15:30** | 🇰🇷 한국 증시 마감 요약 | KOSPI/KOSDAQ 종가, Top 5, 외국인/기관 수급 | 한국 마감 직후 |
| 5 | **21:00** | 🇺🇸 미국 증시 개장 전 포인트 | 프리마켓 + 어닝 일정 + 거시지표 + 주목 종목 | 미국 개장(22:30) − 1.5시간 |
| 6 | **23:00–24:00** | 🇺🇸 미국 증시 개장 후 시황 | 개장 30분 후 시장 톤 + 핫 종목 | 미국 개장(22:30) + 30분 |

### 2.2 슬롯당 생성되는 리포트

각 슬롯에서 다음을 한 번에 생성하여 Blob에 저장:

```
reports/<date>/<slot>/<persona>.<lang>.json
```

- 슬롯 6개 × 페르소나 3종(buffett/dalio/wood) × 언어 4종(ko/en/ja/zh) = **72 리포트/일**

### 2.3 LLM 호출 비용 (DeepSeek)

| 항목 | 일 | 월 |
|---|---|---|
| 자동 생성 리포트 | 72 | 2,160 |
| 평균 출력 토큰 (압축형) | 600 | — |
| 일 출력 토큰 | 43,200 | 1.3M |
| DeepSeek `deepseek-chat` 출력 단가 | $0.87/1M | — |
| **자동 생성 비용** | $0.04 | **~$1.13/월** |

매우 저렴함. 슬롯 추가/페르소나 추가에 부담 없음.

---

## 3. 섹터 정의 + 라이벌 매핑

### 3.1 섹터 정의 (8개)

[services/sector_tracker.py](services/sector_tracker.py)의 `SECTOR_RELATED` 매핑을 기반으로 섹터 8종 + 종목 + ETF 정리:

| 섹터 | ETF | 대표 종목 (Top 5) |
|---|---|---|
| Technology | XLK, SMH, SOXX, QQQ | NVDA, AAPL, MSFT, AVGO, AMD |
| Communication Services | XLC | GOOGL, META, NFLX, DIS, TMUS |
| Consumer Cyclical | XLY | AMZN, TSLA, HD, MCD, NKE |
| Consumer Defensive | XLP | WMT, COST, PG, KO, PEP |
| Financial Services | XLF | JPM, BAC, WFC, GS, V |
| Healthcare | XLV | JNJ, LLY, UNH, PFE, MRK |
| Energy | XLE, USO | XOM, CVX, COP, OXY, SLB |
| Crypto/Alt | (없음, 직접) | BTC-USD, ETH-USD, MSTR, COIN, MARA |

### 3.2 라이벌 비교 매트릭스

각 섹터에서 직접 경쟁하는 2–3 종목 페어:

| 페어 | 비교 포인트 |
|---|---|
| AAPL ↔ GOOGL | 광고 vs 하드웨어 + 서비스, 모바일 OS 양강 |
| MSFT ↔ GOOGL | 클라우드 + AI 인프라 (Azure vs GCP) |
| NVDA ↔ AMD ↔ INTC | AI 반도체 3강 |
| TSLA ↔ RIVN ↔ NIO | EV 글로벌 비교 |
| JPM ↔ GS ↔ BAC | 미국 빅뱅크 |
| LLY ↔ NVO | GLP-1 (비만/당뇨) |
| XOM ↔ CVX | 미국 메이저 에너지 |
| BTC ↔ ETH | 암호화폐 2강 |
| QQQ ↔ SPY ↔ VOO | 인덱스 ETF 가성비 |

라이벌 비교는 섹터 follow-up (`paper_plan §17.1`) 트리거 시 자동 제시되거나, 명시적 `/compare` 명령으로 호출.

---

## 4. 페르소나 × 시간 × 섹터 매트릭스

### 4.1 페르소나별 강점 시간대

각 페르소나가 가장 잘 맞는 슬롯 (사용자 가치 측면):

| 페르소나 | 슬롯 1 (06시 미장 마감) | 슬롯 2 (08시 한국 예측) | 슬롯 3 (12시 아시아) | 슬롯 4 (15:30 한국 마감) | 슬롯 5 (21시 미장 전) | 슬롯 6 (23시 미장 후) |
|---|---|---|---|---|---|---|
| 워렌 버핏 (가치) | ★★★★ (deep) | ★★★ | ★★ | ★★★ | ★★★★ (deep) | ★★ |
| 레이 달리오 (매크로) | ★★★ | ★★★★ (거시) | ★★★★ (거시) | ★★★ | ★★★★ (거시) | ★★★ |
| 캐시 우드 (혁신) | ★★★ | ★★ | ★★ | ★★ | ★★★★ (실적/모멘텀) | ★★★★ (intraday) |

별 4개 = 그 페르소나의 강점 영역 (내용 풍부 ~800 token), 별 2개 = 가벼운 코멘트 (~300 token).

### 4.2 가변 토큰 정책

```python
PERSONA_SLOT_TOKEN_BUDGET = {
    ("buffett", "06_us_close"): 800,
    ("buffett", "21_us_open"):  800,
    ("buffett", "08_kr_pred"):  500,
    # ...
    ("wood",    "23_us_after"): 800,  # intraday 최강
    ("wood",    "06_us_close"): 500,
}
```

자동 생성 시 슬롯 × 페르소나에 따라 max_tokens를 차등 — 강점 슬롯은 풍부, 비강점은 압축. 일일 총 LLM 비용 균형.

---

## 5. 자주 묻는 종목 — 빈도 기반 캐싱

### 5.1 트래픽 분포 가정 (한국 retail bias)

기존 학술 문서 §13 기반 + Korean retail 패턴:

| 구간 | 종목 수 | 트래픽 비중 |
|---|---|---|
| 핫 TOP_50 (NVDA, TSLA, AAPL, QQQ, ...) | 50 | **70%** |
| 핫 TOP_200 (TOP_50 + 모멘텀 ETF + 한국 인기) | 200 | 추가 15% |
| 롱테일 (252 priority pool 나머지) | 250 | 10% |
| 롱테일 외 (yfinance 가능한 모든 종목) | 수만 | 5% |

### 5.2 선호도 + 빈도 결합 hot ticker 결정 (구현됨)

[../services/hot_ticker_resolver.py](../services/hot_ticker_resolver.py) 가 두 신호를 결합:

**신호 1 — 정적 선호도** ([../data/korean_favorite_tickers.csv](../data/korean_favorite_tickers.csv))

editorial 한국인 retail 선호 14종 (rank 부여):

| Rank | Ticker | 종목 | 선호 이유 |
|---|---|---|---|
| 1 | TSLA | 테슬라 | 서학개미 최다 보유 |
| 2 | NVDA | 엔비디아 | AI 반도체 |
| 3 | GOOGL | 알파벳 | 검색·AI |
| 4 | PLTR | 팔란티어 | 빅데이터/군사 AI |
| 5 | AAPL | 애플 | 프리미엄 생태계 |
| 6 | QQQ | 인베스코 | 나스닥100 ETF |
| 7 | IONQ | 아이온큐 | 양자 컴퓨팅 |
| 8 | VOO | 뱅가드 | S&P500 ETF |
| 9 | TQQQ | 프로쉐어즈 | 나스닥100 3배 |
| 10 | MSFT | MS | 클라우드/AI |
| 11 | SOXL | Direxion | 반도체 3배 |
| 12 | TSLL | Direxion | 테슬라 2배 |
| 13 | MU | 마이크론 | HBM 메모리 |
| 14 | SLV | iShares | 은 ETF |

**신호 2 — 동적 빈도** (last 7d webhook count from `logs/yyyy/mm/dd/HH.ndjson`)

**결합 점수**:

```
preference_score(rank) = 14 − rank + 1     (rank 1 → 14, rank 14 → 1, 미수록 → 0)
frequency_score(count) = (count / max_count) × 14
score = 0.5 × preference_score + 0.5 × frequency_score
```

50 : 50 가중치로 두 신호가 동등하게 작용 — favorites 만 있어도 base 점수 보장, 트래픽이 많은 비-favorites도 진입 가능.

**갱신 주기 (구현됨)**:

- KST 02:00 매일 (UTC 17:00) — `rotate_hot_tickers` Timer Trigger ([../function_app.py](../function_app.py))
- logs 가 비어있으면 favorites 만으로 fallback (cold-start 대응)
- top-50 결과를 `services/ticker_data_cache.py` 의 `HOT_TICKERS` 로 in-memory 교체 (다음 30분 prewarm 사이클부터 적용)

**예시 결과** (가상 트래픽 NVDA=80건, AAPL=100건, AMZN=50건일 때):

| Rank | Ticker | Score | 출처 |
|---|---|---|---|
| 1 | NVDA | 12.10 | 선호(2) + 빈도 80 |
| 2 | AAPL | 12.00 | 선호(5) + 빈도 100 |
| 3 | TSLA | 7.00 | 선호(1) only |
| 4 | GOOGL | 6.00 | 선호(3) only |
| ... | | | |
| 9 | AMZN | 3.50 | 빈도 50 only (선호 미수록이지만 트래픽 진입) |

이로써 사용자 트래픽 변화에 자동 적응 — 어떤 ticker가 갑자기 hot 해지면 다음날부터 사전 캐싱 대상으로.

### 5.3 캐싱 계층 (옵션 C 기준 통합)

| 계층 | 데이터 종류 | TTL | 위치 |
|---|---|---|---|
| L0 메모리 | ticker price (light) | 30분 (hot) / 4h (cold) | Functions process dict |
| L1 Blob | ticker price (light) | 동상 | `ticker-cache/<TICKER>.json` |
| L2 Blob | StockSnapshot (heavy) | 4시간 | `prewarm/snapshots/<TICKER>.json` |
| L3 Blob | LLM commentary (페르소나×언어) | 24시간 | `prewarm/commentary/<TICKER>.<persona>.<lang>.json` |
| **L4 Blob** | **시간대 슬롯 리포트** (시장 전반) | **8–12시간** | **`reports/<date>/<slot>/<persona>.<lang>.json`** |

L0–L3는 종목별, L4는 시장 슬롯별. **사용자가 "오늘 시황 어때?" 물으면 L4가 hit, "NVDA 어때?" 물으면 L3 hit.**

---

## 6. 휴장 시 노출 정책

### 6.1 휴장 판단

- **주말 (UTC 토요일~일요일)**: 양 시장 모두 휴장
- **한국 공휴일**: 한국 시장 휴장 (미국은 그 날에 따라)
- **미국 공휴일**: 미국 시장 휴장 (한국은 그 날에 따라)
- **양 시장 모두 휴장일**: 정기 슬롯 자동 발화 안 함

### 6.2 사용자 요청 시 노출

휴장 중 사용자가 "오늘 시황" 물었을 때:

| 사용자 시간 | 응답 |
|---|---|
| 한국 휴장, 미국 거래 중 | "한국 시장 휴장입니다. 미국 시장은 거래 중입니다 — 직전 슬롯 5/6 기준 마감 리포트 노출" |
| 미국 휴장, 한국 거래 중 | 반대 |
| **양 시장 모두 휴장** | "양 시장 모두 휴장입니다. 직전 슬롯의 마감 리포트만 표시합니다." |
| 주말 | "주말 휴장 — 직전 금요일 마감 기준" |

### 6.3 휴장일 LLM 비용 절감

휴장일에는 정기 슬롯 자동 발화 skip. 직전 슬롯 결과 그대로 노출. 일 평균 8.5%의 일이 휴장 (주말 + 공휴일) → 월 ~$0.10 추가 절감.

### 6.4 공휴일 데이터 소스

미국 공휴일: NYSE/Nasdaq calendar (yfinance가 자동 제공 — 종가 데이터 없으면 휴장)
한국 공휴일: KRX calendar (yfinance 005930.KS도 동일 패턴)

자동 판단 로직:

```python
def market_open_today(market: str, date: datetime) -> bool:
    # yfinance .history(period='5d') 의 가장 최근 거래일이 오늘인지 확인
    if market == "us":
        ticker = "^GSPC"
    elif market == "kr":
        ticker = "^KS11"
    history = yf.Ticker(ticker).history(period="5d")
    last_trading_day = history.index[-1].date()
    return last_trading_day == date.date()
```

---

## 7. 시나리오 분석

### 7.1 시나리오 가정

| 차원 | DAU 500 (MVP) | DAU 3,000 (성장) | DAU 10,000 (성숙) |
|---|---|---|---|
| 일 webhook 수 | 2,500 (DAU × 5건) | 15,000 | 50,000 |
| 평균 사용자당 ticker query | 3 | 4 | 5 |
| 평균 사용자당 deep analysis | 0.4 | 0.8 | 1.2 |
| Hot ticker 비중 | 70% | 75% | 78% |
| 시간대 리포트 조회 비중 | 20% (5건 중 1건) | 25% | 30% |

### 7.2 케이스별 처리 흐름 + 캐시 hit 위치

| Case | 사용자 요청 | 처리 흐름 | 캐시 hit | LLM 호출 |
|---|---|---|---|---|
| **A** | hot ticker 짧은 응답 (NVDA, TSLA 등) | L3 (commentary) hit | ✅ | 0 |
| **B** | hot ticker deep 분석 | L3 hit + max_tokens 1500 LLM 별도 호출 | 부분 | 1 |
| **C** | longtail ticker 짧은 응답 | L2 (snapshot) hit + LLM | snapshot only | 1 |
| **D** | longtail ticker deep | L2 hit + deep LLM | snapshot only | 1 |
| **E** | "오늘 시황" 자유 질의 | L4 (slot report) hit | ✅ | 0 |
| **F** | 자연어 ("추천", "비교") | intent classifier rejection | N/A | 0 |
| **G** | 미캐싱 ticker 첫 조회 | L0/L1/L2/L3 모두 miss → 라이브 fetch + LLM | miss | 1 |

### 7.3 케이스별 발생 빈도 (DAU 3,000 기준 일 15,000 webhook)

| Case | 빈도 % | 일 건수 | LLM 호출 | LLM 토큰 (입력+출력) |
|---|---|---|---|---|
| A (hot 짧은) | 50% | 7,500 | 0 | 0 |
| B (hot deep) | 8% | 1,200 | 1,200 | 1,200 × 1,500 = 1.8M |
| C (longtail 짧은) | 12% | 1,800 | 1,800 | 1,800 × 600 = 1.08M |
| D (longtail deep) | 5% | 750 | 750 | 750 × 1,500 = 1.13M |
| E (시황) | 15% | 2,250 | 0 (L4 hit) | 0 |
| F (intent reject) | 5% | 750 | 0 | 0 |
| G (cold ticker 미스) | 5% | 750 | 750 | 750 × 600 = 0.45M |
| **합계** | 100% | 15,000 | **4,500** | **4.46M 출력 토큰** |

LLM 호출 4,500건 / 사용자 요청 15,000건 = **30% 만 LLM이 작동, 70% 캐시 hit**.

---

## 8. 옵션 C 정량 효과

### 8.1 응답 시간 비교 (DAU 3,000 기준 가중 평균)

| Case | 빈도 | Before (모든 요청 라이브) | After (옵션 C) |
|---|---|---|---|
| A (hot 짧은) | 50% | 8s | **0.5s** (메모리 hit) |
| B (hot deep) | 8% | 8s | **5s** (snapshot hit + deep LLM) |
| C (longtail 짧은) | 12% | 8s | **3.5s** (snapshot hit + LLM) |
| D (longtail deep) | 5% | 8s | **5s** |
| E (시황) | 15% | 12s (대화형 시황 LLM) | **0.5s** (slot 캐시 hit) |
| F (intent reject) | 5% | <1s | <1s |
| G (cold) | 5% | 8s | 6s (yfinance + LLM, no cache) |
| **가중 평균** | — | **~8.0s** | **~1.7s** |

가중 평균 응답 시간이 **8s → 1.7s 로 79% 감소**.

### 8.2 LLM 호출 횟수 비교

| 시나리오 | Before (캐시 없음) | After (옵션 C) | 절감률 |
|---|---|---|---|
| DAU 500 일 2,500건 | 2,500 | 750 | 70% |
| DAU 3,000 일 15,000건 | 15,000 | 4,500 + 72(자동슬롯) | **70%** |
| DAU 10,000 일 50,000건 | 50,000 | 15,000 + 72 | **70%** |

자동 슬롯(72)은 사용자 수 무관하게 일정 — DAU 늘수록 ROI 더 큼.

### 8.3 월 비용 비교 (DAU 3,000 기준)

| 항목 | Before | After (옵션 C) |
|---|---|---|
| DeepSeek `deepseek-chat` LLM | 15,000/일 × 30 × 평균 800 token × $0.87/1M | $313/월 |
| 옵션 C 적용 후 LLM (4,500 + 72 slot) | — | **$95/월** |
| Functions 실행 | $5 | $5 |
| Blob storage + 트랜잭션 | $0 | $5 |
| Static Web Apps Free | $0 | $0 |
| **총합** | **~$320/월** | **~$105/월** |

**월 $215 절감 = 67% 감소.**

DAU 10,000 으로 확장 시:
- Before: $1,050/월 LLM
- After: $315/월 LLM + $20 Functions/Blob = $335/월
- **월 $715 절감 (68% 감소)**

### 8.4 사용자 체감 측면 효과

| 차원 | 영향 |
|---|---|
| 첫 인상 (Hot ticker 첫 조회 0.5s) | "즉시 응답" — 모바일 UX 경계 (1s) 충족 |
| 시황 질의 0.5s | 챗봇 답변이 검색엔진 수준 즉시성 |
| Deep 분석 5s | "잠깐 기다리는" 가치 있는 정보 — 불만 임계점 (10s) 이하 |
| Daily limit 5회 (§17.2) | 캐시로 5회 충분 가능 — 구독 전환률 ↑ |

### 8.5 시간대 슬롯 리포트 ROI

|  | 일 | 월 |
|---|---|---|
| 슬롯 자동 생성 LLM 호출 | 72 | 2,160 |
| 슬롯 LLM 비용 | $0.04 | **$1.13** |
| 슬롯 hit 사용자 요청 (case E) | 2,250 (DAU 3,000) | 67,500 |
| 슬롯 hit 으로 절약된 LLM 호출 | 2,250 | 67,500 |
| 절약된 LLM 비용 | $1.41 | **$42.30** |
| **슬롯 시스템 ROI** | **35×** | **37×** |

슬롯 자동 생성에 $1 쓰면 사용자 응답 시 $37 절약.

---

## 9. 구현 로드맵 (3단계)

### 9.1 단계 1 — 시간대 슬롯 6개 (1주)

- [ ] `services/slot_report_service.py` 신설 — 6개 슬롯 정의 + 페르소나×언어 매트릭스
- [ ] `function_app.py` 에 6개 timer trigger (KST 06/08/12/15:30/21/23)
- [ ] `reports/<date>/<slot>/...` Blob 적재
- [ ] 핸들러에서 자유 질의 ("오늘 시황", "today's market") → 가장 가까운 슬롯 fetch
- [ ] 휴장 판단 (yfinance ^GSPC / ^KS11 마지막 거래일)

### 9.2 단계 2 — 빈도 기반 동적 hot ticker (3일)

- [ ] `function_app.py` 에 추가 timer (`0 0 17 * * *` UTC = KST 02:00)
- [ ] logs/ 의 ticker count 집계 → 상위 50 추출
- [ ] `data/priority_tickers.csv` 자동 갱신 + commit (선택) 또는 in-memory
- [ ] `prewarm_commentaries` Timer 가 다음 발화 시 새 hot 사용

### 9.3 단계 3 — 페르소나×시간×섹터 가변 토큰 (3일)

- [ ] `services/slot_report_service.py` 의 `PERSONA_SLOT_TOKEN_BUDGET` 매트릭스
- [ ] 슬롯×페르소나×섹터 라이벌 비교 자동 포함
- [ ] [services/sector_tracker.py](services/sector_tracker.py) `SECTOR_RELATED` 의 라이벌 페어 활용

전 단계 누계 약 2주 작업.

---

## 10. 모니터링 메트릭

App Insights 커스텀 메트릭 추가:

| 메트릭 | 의미 |
|---|---|
| `slot.report.generated` | 슬롯별 정상 생성 카운트 |
| `slot.report.failed` | 슬롯별 LLM/yfinance 실패 |
| `cache.l4.hit_rate` | 시간대 슬롯 캐시 적중률 (목표 70%+) |
| `hot_ticker.update.count` | 동적 hot 갱신 시 추가/제거된 ticker 수 |
| `market.closed.skipped` | 휴장으로 skip한 슬롯 수 |

대시보드 (`paper_plan §17.3`) 에 추가하여 일/주 단위 추세 확인.

---

## 11. 리스크 + 완화

| 리스크 | 영향 | 완화 |
|---|---|---|
| 슬롯 LLM 호출 실패 | 그 슬롯의 사용자 요청이 라이브 LLM 호출로 폴백 → 응답시간 ↑ | 직전 슬롯 데이터 표시 (최대 6시간 stale) |
| 동적 hot 갱신이 잘못된 ticker 선택 | 캐싱 효과 감소 | 7일 이동 평균으로 안정화 (단일 일자 spike 방지) |
| 휴장 판단 오류 (특수 공휴일) | 잘못된 슬롯 발화 또는 skip | yfinance 마지막 거래일 기반 1차 판단 + 수동 override 가능한 `data/market_holidays.csv` |
| 슬롯 시간대 사용자 분포 편향 | 일부 슬롯 hit rate 낮음 | 4주 데이터 누적 후 슬롯 시간 재조정 |
| 사용자 언어가 `ko/en/ja/zh` 외 (예: vi, fr) | 슬롯 캐시 miss 100% | en으로 fallback (i18n 동작과 일관) |

---

## 12. 결론

본 정책 도입 시:

- **응답 시간**: 8s → 1.7s (가중 평균, 79% 감소)
- **LLM 호출**: 70% 감소
- **월 비용**: $320 → $105 (DAU 3,000 기준, 67% 감소)
- **자동 슬롯 ROI**: **37×** (월 $1.13 투자로 $42 절약)
- **사용자 체감**: 즉시 응답 (모바일 UX 경계 1s 통과)

위 모든 효과는 옵션 C (Static Web Apps + Functions 인메모리 + Blob 백업) 위에 본 시간대 슬롯 정책을 추가했을 때의 누적 효과입니다.

---

**End of Document**

*수정·시나리오 추가 요청은 GitHub Issue로 부탁드립니다.*
