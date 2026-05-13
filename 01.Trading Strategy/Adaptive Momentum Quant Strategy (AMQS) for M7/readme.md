# AMQS-M7: Adaptive Momentum Quant Strategy for Magnificent 7

> [vibe-investing/AMQS](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)) 의 **M7 특화 확장판**. 원본 AMQS 의 *4-Factor Momentum Composite*, *거시 레짐 필터*, *-12% 손절*, *주간 리밸런싱* 을 그대로 계승하면서 **5번째 점수 차원으로 "단기 하락 매수 모멘텀 (Pullback-in-Uptrend)" 을 정식 편입**한 sub-strategy.

**Universe**: AAPL · MSFT · GOOGL · AMZN · META · NVDA · TSLA

---

## 원본 AMQS 와의 관계

| 측면 | AMQS (원본) | **AMQS-M7 (본 확장)** |
|---|---|---|
| Universe | NASDAQ-100 + AI Value Chain ~150종목 | **M7 7종목** |
| 선별 방식 | Top 10 모멘텀 점수 | **7종목 전체 score-tilted allocation** |
| 4-Factor Composite | 12-1 / 6-1 / 3-1 / Vol-adj | **동일** |
| 사전 필터 | mkt cap / 유동성 / vol / beta / gap-down | **동일** |
| 100점 채점 차원 | 4 dimensions (40/30/20/10) | **5 dimensions (35/15/25/15/10)** |
| 5번째 차원 | — | **단기 하락 매수 모멘텀 15% (NEW)** |
| 거시 레짐 필터 | Risk-On/Off/Defensive (QQQ 200MA · VIX) | **동일** |
| 손절 | -12% from entry | **동일** |
| 리밸런싱 주기 | 주간 (금→월) + 일간 손절 모니터링 | **동일** |

### 본 확장의 핵심: Pullback-in-Uptrend Dimension

원본 AMQS 가 "12-1 모멘텀 > 0" 만으로 추세 판정을 했다면, AMQS-M7 은 *추세 유지 종목의 단기 조정* 을 *별도 차원으로 정량화*. 활성 조건 4중 게이트:

1. Component A (12-1 momentum) > 0  ← 장기 추세 유지
2. Component B (6-1 momentum)  > 0  ← 중기 추세 유지
3. 현재가 > 50일 이동평균          ← 건전한 조정 (추세 붕괴 아님)
4. 5D ≤ -3% OR 20D ≤ -5%          ← 의미 있는 단기 하락

신호 강도 = (0.7·|ret_5d| + 0.3·|ret_20d|) × (1 + min(factor_A, 1.0)) + RSI-oversold 가산

> **이론적 근거**: M7 같은 *지속적 강세 종목군* 에서는 조정 = 매수 기회 패턴이 통계적으로 우세. 그러나 *DeepSeek 같은 추세 전환 이벤트* 직전에는 dip-buy 가 함정이 되므로, 4중 게이트로 falling knife 차단.

---

## 프로젝트 구조

```
AMQS_M7/
├── README.md
├── requirements.txt
├── src/
│   ├── strategy.py       # 4-Factor + 100점 채점 + 거시 레짐 + 사전 필터
│   ├── amqs_m7.py        # CLI 트래커 + 알림 + 손절 추적
│   ├── backtest.py       # 백테스트 (vs QQQ/SOXX/AI 반도체)
│   └── broker.py         # Phase 1 CLI / Phase 2 KIS API 자리표시
├── prompts/
│   ├── AMQS_M7_kr.MD     # 한국어 LLM 프롬프트 (원본과 동일 톤)
│   ├── AMQS_M7_EN.MD     # English (토큰 30-40% 절감)
│   └── AMQS_M7_zh.MD     # 中文
└── data/                  # 런타임 CSV 출력
```

---

## 설치

```bash
cd AMQS_M7
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 사용법

### Phase 1: CLI 알림 모드

**일회성 스냅샷**:
```bash
python -m src.amqs_m7 --mode track --csv data/amqs_m7_log.csv
```

출력 예시:
```
==================================================================================
  AMQS-M7  ·  Adaptive Momentum Quant Strategy (Magnificent 7)
  vibe-investing extension  ·  as of 2026-05-13 22:30:00
==================================================================================

  거시 레짐: [ON ] RISK-ON
  QQQ +200MA, VIX 18.2<25, 5D +1.4%
  QQQ > 200MA  ·  VIX 18.2  ·  QQQ 5D +1.4%

  100점 구성: 모멘텀 신호 35% · 단기 하락 매수 15% · 추세 품질 25% · 변동성 알파 15% · 거시 10%

  Ticker     Price     12-1     6-1    3-1      5D     20D    RSI    52W  Score    Wt  Signal
  ------------------------------------------------------------------------------------------
  NVDA     920.50   +62.4%  +18.5%  -2.1%   -8.2%   -4.1%     28   -9.1%   84.5  22.5%  [++] 단기 하락 매수
  MSFT     452.30   +28.5%  +12.1%  +5.4%   +1.2%   +3.4%     58   -0.5%   78.2  18.3%  [+ ] 위성 포지션
  ...

  >> 실행 알림 (Action Alerts)
  [++] [단기 하락 매수] NVDA -> 목표 22.5%
     5D -8.2% / 20D -4.1% 단기 하락, 12-1 +62% / 6-1 +19% 추세 유지, RSI 28 과매도
```

**워치 모드 (주기 폴링)**:
```bash
python -m src.amqs_m7 --mode track --watch --interval 30
```

**강제 리밸런싱** (기본은 월요일에만 리밸런싱):
```bash
python -m src.amqs_m7 --mode track --force-rebalance
```

### 백테스트

```bash
python -m src.amqs_m7 --mode backtest --start 2024-01-02 --end 2026-04-30
# 또는
python -m src.backtest --start 2024-01-02 --end 2026-04-30
```

출력:
- `data/backtest_equity.csv` - 일별 equity curves (AMQS-M7 vs QQQ vs SOXX vs AI 반도체 바스켓)
- `data/backtest_positions.csv` - 주별 목표 비중 + 거시 레짐
- `data/backtest_trades.csv` - 진입/청산/손절 로그
- `data/backtest_regimes.csv` - 레짐 전환 이력
- 콘솔에 CAGR / Vol / Sharpe / MDD / 회전율 비교표

### LLM 프롬프트 사용

세 가지 언어 중 선택. 토큰 효율을 원하면 영문판 권장 (한국어 대비 ~30% 절감):

```
$ cat prompts/AMQS_M7_kr.MD | pbcopy   # Mac
$ cat prompts/AMQS_M7_kr.MD | xclip    # Linux
```

복사 후 Claude / GPT 등에 붙여넣기. 현재 시세를 직접 입력하거나 LLM 의 검색 기능 활용.

---

## Phase 2 로드맵: 증권사 API 통합

`src/broker.py` 의 `KISBroker` (한국투자증권 Open API) 자리표시 구조:

```bash
export KIS_APP_KEY=...
export KIS_APP_SECRET=...
export KIS_ACCOUNT_NO=...
python -m src.amqs_m7 --mode track --broker kis --live
```

구현해야 할 4가지:
1. `_ensure_token()` — `POST /oauth2/tokenP` 토큰 발급/캐싱
2. `get_positions()` — `GET /uapi/overseas-stock/v1/trading/inquire-balance` 잔고 조회
3. `rebalance()` — 잔고 → 차이 계산 → `POST .../order` 주문 체인
4. 시장 시간 가드 (한국시간 23:30 ~ 06:00) + 환율 처리 (KRW ↔ USD)

다른 증권사 (키움, 미래에셋) 확장도 동일 패턴: `Broker` 추상 클래스 상속, `build_broker()` 분기 추가.

---

## Python 스크립트 vs LLM 프롬프트의 역할 분담

| 항목 | Python 스크립트 | LLM 프롬프트 |
|---|---|---|
| 4-Factor 모멘텀 | Yes (자동) | Yes |
| 단기 하락 매수 (NEW) | Yes (자동) | Yes |
| 52주 신고가 거리 | Yes (자동) | Yes |
| 200DMA, 50DMA | Yes (자동) | Yes |
| RSI, MDD | Yes (자동) | Yes |
| 거시 레짐 (QQQ/VIX) | Yes (자동) | Yes |
| Revenue Acceleration | No (yfinance 한계) | Yes (LLM 지식) |
| 13F 헤지펀드 매수 | No | Yes (LLM 지식) |
| EPS Estimate Revision | No | Yes (LLM 지식) |
| 매크로 이벤트 내러티브 | No | Yes |

**역할 분담**: Python 스크립트는 *기술적 신호 자동 추적 + 알림*, LLM 프롬프트는 *분기별 펀더멘털 분석 + 전략 검토*. 양쪽 결과를 교차 검증하는 것이 권장 워크플로우.

---

## 주의사항 / 한계

- 본 시스템은 **연구·시뮬레이션 도구**. 실거래 손익 보장 아님.
- M7 7종목은 모두 동일 섹터(Big Tech) 노출 → 시장 베타 매우 높음, 상관관계 0.6+
- yfinance 무료 데이터 사용. Phase 2 에서 KIS 시세 API 로 교체 권장.
- 거래비용 5bps + 슬리피지 10bps 는 원본 AMQS 기본값; 한국 개인 투자자는 *20-30bps + 환전 50-100bps* 차감 후 재계산 필요
- 양도소득세 22% + 회전율 ~150-200% 환경에서 *연 3-5% 추가 잠식*

---

## 라이선스

MIT. 출처 표기 권장: "Built on AMQS by Dennis Kim, vibe-investing repository."
