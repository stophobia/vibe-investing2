# Macro-Regime Quant Prompts for M7 & AI-Infrastructure Stocks

> 거시 변수(환율·금리·물가·소비심리·유가)와 M7 + AI 인프라 종목의 관계를 **정직하게** 분석하는 퀀트 프롬프트 + 파이썬 파이프라인.
> A quant prompt + Python pipeline that **honestly** analyzes the relationship between macro variables (FX, rates, inflation, sentiment, oil) and the Magnificent 7 + AI-infrastructure stocks.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)


## 주의: 아직 미완성입니다. 금융공학적 지식이 없다면 이 퀀트로 투자에 이용하지 마세요!

---

## TL;DR — 핵심 결론 / Key Finding

**KO:** 거시 변수는 빅테크·AI 인프라 주가를 거의 설명하지 못합니다 (주간 회귀 R² 1~3%). 거시 레짐(국면)은 *시장 전체 타이밍*과 *하락 방어*에는 유효하지만, 시장 베타(QQQ)를 제거하면 종목 고유 알파의 레짐 의존성은 거의 사라집니다 (유의 종목 3/17 → 1/17). **거시는 "언제 시장에 있을지"는 알려주지만 "어떤 종목을 고를지"는 알려주지 않습니다.** 이 프레임워크의 진짜 가치는 *틀린 확신을 통계로 막아주는 정직성*에 있습니다.

**EN:** Macro variables barely explain big-tech / AI-infra prices (weekly regression R² of 1–3%). Macro regimes are useful for *market timing* and *drawdown defense*, but once you strip out market beta (QQQ), the regime-dependence of stock-specific alpha nearly vanishes (significant names drop 3/17 → 1/17). **Macro tells you *when to be in the market*, not *which stock to pick*.** The real value of this framework is *honesty enforced by statistics* — it refuses to manufacture confident signals that the data doesn't support.

---

## 왜 이게 중요한가 / Why This Matters

대부분의 "거시 기반 매매" 콘텐츠는 상관관계를 과장합니다. "금리가 오르면 NVDA를 팔아라" 같은 단정은 백테스트와 유의성 검정을 통과하지 못합니다. 이 프로젝트는 LLM이 그런 과장을 하지 않도록 설계된 프롬프트와, 그 주장을 데이터로 *반증*하는 코드를 함께 제공합니다.

Most "macro-driven trading" content overstates correlations. Claims like "sell NVDA when rates rise" don't survive backtests and significance tests. This project provides prompts engineered to *prevent* an LLM from overstating, plus code that *falsifies* such claims with data.

---

## 분석 대상 / Universe

| Group | Tickers |
|-------|---------|
| **M7** | AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA |
| **AI Infra — Semiconductors** | AVGO, AMD, TSM, ASML, MU |
| **AI Infra — Power / Datacenter / Network** | VRT, ETN, SMCI, DLR, GEV |
| **Market factor (beta control)** | QQQ |
| **Macro** | DXY (dollar), UST10Y (10y yield), CPI YoY, Michigan Consumer Sentiment, WTI (oil / petrodollar) |

**Period:** 2020-01-01 → 2026-04-30 (daily).

---

## 세 가지 접근 / Three Approaches

| Prompt | 방법 / Method | 결과 / Result | 용도 / Use |
|--------|---------------|----------------|------------|
| **A** | Rule-based regime (rates × risk) + momentum | MDD 16/17 개선, Sharpe 5/17 승 | Drawdown defense / 하락 방어 |
| **B** | Macro regression fair-value | Weekly R² 1–3% | Weak. Supplementary only / 보조 지표 |
| **C** | Unsupervised regime (KMeans/HMM) + QQQ beta-neutral residual alpha | Regime-dependence 3/17 → 1/17 after removing market | Timing yes, stock-selection no / 타이밍 O, 종목선택 X |

---

## 프롬프트 (한국어) / Prompt (Korean)

전체 프롬프트 3종(A/B/C)은 [`QUANT_PROMPT_TEMPLATE.md`](./QUANT_PROMPT_TEMPLATE.md)에 있습니다. 아래는 메인인 PROMPT A 요약입니다.

```
당신은 정직한 퀀트 애널리스트다. 거시 변수로 시장 레짐(국면)을 분류하고,
각 종목의 레짐별 과거 성과와 모멘텀을 결합해 매수/매도 시그널을 낸다.
통계적으로 정당화될 때만 시그널을 내고, 아니면 그렇게 말한다.

[입력] 거시(DXY,UST10Y,CPI_YoY,ConsumerSentiment,WTI) + M7 + AI인프라, 2020~2026-04
[레짐] 금리추세(UST10Y 60d) × 위험선호(z(-DXY)+z(WTI)+z(Sentiment), 60d)
       => Goldilocks / Reflation / Deflation / Stagflation 4국면
[검증] 레짐별 연율수익(에지) + Kruskal-Wallis 유의성. 유의 종목 적으면 명시.
[시그널] 레짐에지 부호 + 50일 모멘텀 부호. 둘다+ BUY / 둘다- SELL / 엇갈림 HOLD.
[백테스트] 룩어헤드 방지. CAGR/Sharpe/MDD를 B&H와 비교.
          수익을 늘리는가 vs 낙폭을 줄이는가를 반드시 구분해 보고.
거시가 종목을 설명 못 하면 억지 시그널 금지. 정직하게 말하라.
```

## Prompt (English)

Full A/B/C prompts are in [`QUANT_PROMPT_TEMPLATE.md`](./QUANT_PROMPT_TEMPLATE.md). Below is the main PROMPT A.

```
You are an honest quant analyst. Classify market regimes from macro variables,
then combine each stock's per-regime historical performance with momentum to
produce buy/sell signals. Only emit a signal when statistically justified;
otherwise say so explicitly.

[Inputs] Macro (DXY, UST10Y, CPI_YoY, ConsumerSentiment, WTI) + M7 + AI-infra, 2020 to 2026-04
[Regime] Rate trend (UST10Y 60d) x Risk appetite (z(-DXY)+z(WTI)+z(Sentiment), 60d)
         => 4 regimes: Goldilocks / Reflation / Deflation / Stagflation
[Validation] Per-regime annualized return ("edge") + Kruskal-Wallis significance.
             If few names are significant, state it plainly.
[Signal] Sign of regime-edge + sign of 50d momentum.
         Both + => BUY / both - => SELL/AVOID / mixed => HOLD.
[Backtest] No look-ahead (enter next day). Compare CAGR/Sharpe/MDD vs Buy&Hold.
           ALWAYS separate: does it raise returns, or does it cut drawdowns?
If macro fails to explain a stock, do NOT manufacture a signal. Be honest.
```

---

## 빠른 시작 / Quick Start

```bash
# 1. 의존성 설치 / Install deps
pip install yfinance pandas-datareader statsmodels scipy scikit-learn hmmlearn matplotlib pandas numpy

# 2. 합성 데이터로 파이프라인 실연 (인터넷 불필요)
#    Demo the full pipeline on synthetic data (no internet needed)
python 00_generate_data.py
python 01_quant_engine.py        # Prompt B: regression fair-value
python 03_regime_engine.py       # Prompt A: regime + momentum
python 05_unsup_regime_alpha.py  # Prompt C: unsupervised regime + beta-neutral alpha

# 3. 실데이터로 실행 (yfinance + FRED)
#    Run on real data
python quant_macro_signal_REALDATA.py
```

> **주의 / Note:** 레포의 수치·차트는 *방법론 검증용 합성 데이터* 결과입니다. 실제 투자 결론은 실데이터 스크립트로 직접 확인하세요. The numbers/charts in this repo are from *synthetic data for methodology validation*. Verify real conclusions with the real-data script.

---

## 파일 구성 / Repository Layout

```
.
├── QUANT_PROMPT_TEMPLATE.md        # 프롬프트 A/B/C 전문 + 발견 / Full prompts + findings
├── 00_generate_data.py             # 합성 데이터 생성 (QQQ 포함) / Synthetic data gen
├── 01_quant_engine.py              # Prompt B: 회귀 적정가 / Regression fair-value
├── 03_regime_engine.py             # Prompt A: 레짐+모멘텀 / Regime + momentum
├── 05_unsup_regime_alpha.py        # Prompt C: 비지도 레짐 + 베타중립 / Unsup + beta-neutral
├── 02/04/06_visualize*.py          # 대시보드 / Dashboards
├── quant_macro_signal_REALDATA.py  # 실데이터 (yfinance+FRED) / Real data
├── market_data_2020_2026.csv       # 백테스트 데이터셋 / Backtest dataset
└── out_*.csv                       # 분석 결과 / Analysis outputs
```

---

## 방법론 노트 / Methodology Notes

- **수익률로 분석, 가격으로 X.** 가격 레벨 상관은 추세 때문에 허위(spurious). Always use returns/changes, never price levels (spurious trend correlation).
- **일간이 아니라 주간/월간.** 거시 효과는 저빈도에서만 드러남. Macro effects only surface at weekly/monthly horizons.
- **유의성 검정 필수.** Pearson p-value, Kruskal-Wallis. p≥0.05면 "ns(유의하지 않음)". Significance testing is mandatory.
- **룩어헤드 방지.** 시그널 다음날 진입. Signals enter next day, no look-ahead.
- **베타 중립화.** QQQ 회귀 잔차로 시장 효과 제거 → 종목 고유 알파 분리. Strip market via QQQ regression residuals.

---

## 한계 / Limitations

- 합성 데이터 기반 시연이므로 실데이터에서 결과가 달라질 수 있음. Synthetic-data demo; real data may differ.
- 거래비용·세금·슬리피지 미반영. No transaction costs / taxes / slippage.
- 과거 레짐이 미래에 반복된다는 보장 없음. No guarantee historical regimes repeat.
- **투자 자문 아님.** 교육·연구용. Not investment advice; for education/research only.

---

## License

MIT. 자유롭게 사용·수정하되 자기 책임 하에. Use/modify freely at your own risk.
