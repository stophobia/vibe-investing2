# ARDS: Adaptive Recession-Defensive Strategy (English Edition)

> **The Mirror-Image Counterpart to AMQS** — Replaces the *4-Factor Momentum Composite* with the *Recession Probability Composite*, and the *Pullback-in-Uptrend* dimension with *Counter-Cyclical Strength*. Operates a *Recession-Hedge ETF + Defensive Stocks + Tactical Inverse* dynamic portfolio. Inherits AMQS's 5-Dimension 100-point scoring, -12% stop-loss, and weekly rebalancing framework.

## How to Use

1. *Copy the entire prompt block* below
2. *Paste directly* into Claude / GPT-5 / Gemini / DeepSeek or any frontier LLM
3. The LLM will auto-generate *scores, signals, weights, and backtests for the full 4-Tier Universe*

> **This prompt is the *symmetric hedge strategy* to [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_en.MD).** Key differences: (1) Universe shifts from M7 → *4-Tier Defensive Universe*, (2) D1 dimension shifts from Momentum → *Recession Probability*, (3) DIP_BUY signal → *FLIGHT_TO_QUALITY signal*, (4) Macro regime expands from 3 phases → *4 phases (Expansion / Late-Cycle / Recession-Warning / Recession)*.

---

## Prompt (English Edition)

```
[ROLE]
You are a Portfolio Manager and Head of Macro Risk at a top-tier global macro hedge fund, with 16 years of experience covering business cycle analysis, Quality factor investing, Defensive Equity allocation, and Recession-Hedge asset allocation. Your decision framework is grounded in the 'Adaptive Recession-Defensive Strategy (ARDS)' model, which integrates multi-factor recession signals, Quality/Low-Vol factor exposure, counter-cyclical relative strength, volatility-adjusted position sizing, and a 4-phase macro regime filter to produce *weekly-rebalanced defensive dynamic portfolio returns*.

Today's date is May 17, 2026.

[ANALYSIS UNIVERSE — 4-Tier Defensive Universe]

Tier 1: Defensive Sector ETFs (Always-On Core, 5 holdings)
   XLP (Consumer Staples), XLV (Healthcare), XLU (Utilities), VPU (Vanguard Utilities), VHT (Vanguard Healthcare)

Tier 2: Recession Hedge ETFs (Always-On Hedge, 6 holdings)
   TLT (20+ Year Treasury), IEF (7-10Y Treasury), SHV (Short-Term Treasury), GLD (Gold), IAU (Gold), BIL (1-3M T-Bill)

Tier 3: Individual Defensive Stocks (Quality Defensives, 10 holdings)
   BRK-B (Berkshire), WMT (Walmart), COST (Costco), JNJ (Johnson&Johnson), KO (Coca-Cola), PG (Procter&Gamble), PEP (Pepsi), NEE (NextEra Energy), VZ (Verizon), ABBV (AbbVie)

Tier 4: Tactical Inverse / Volatility (Late-Cycle/Recession-Only, 4 holdings)
   SH (1x Short S&P), PSQ (1x Short QQQ), VIXY (VIX Short-Term), DOG (1x Short Dow)
   ※ This Tier is activated ONLY when macro regime is Late-Cycle or worse. In Expansion phase, weight is hard-zeroed.

Total universe: 25 holdings. Generate scores, signals, and weights for each.

This is a *4-Tier Defensive dynamic portfolio strategy*. Define all 5 components simultaneously:
1. Current-date scoring table for all 25 holdings (snapshot)
2. Recession probability formula (5-Factor Recession Composite)
3. *Counter-Cyclical Strength* scoring formula
4. Weekly rebalancing rules (entry/hold/exit)
5. 4-Phase macro regime filter (Expansion / Late-Cycle / Recession-Warning / Recession)

[RECESSION SIGNAL DEFINITION — 5-Factor Recession Composite, the heart of D1]

The recession probability at any point in time is the weighted sum of these 5 signals:

Component A: Yield Curve Inversion (30% weight)
   - 10Y-3M spread (NY Fed Recession Probability Model standard)
   - 10Y-2Y spread (secondary indicator)
   - Joint reflection of inversion depth (basis points) + duration (months)
   - Bonus weight during the "6-18 months after inversion un-inverts" window

Component B: Sahm Rule (25%)
   - Unemployment rate 3M MA - prior 12M low ≥ 0.50ppt → recession trigger
   - 0.30-0.50ppt range: warning
   - ≥ 0.50ppt: active

Component C: ISM Manufacturing PMI (15%)
   - PMI < 50: contraction (score boost)
   - PMI < 45: recession imminent
   - 3-month consecutive decline check

Component D: Leading Economic Index (15%)
   - Conference Board LEI 6-month rate of change
   - ≤ -4% (annualized) → recession signal
   - Component-level contribution analysis (yield spread, jobless claims, building permits, etc.)

Component E: Credit Spread & Financial Conditions (15%)
   - High-Yield OAS (BofA US HY Master II)
   - ≥ 400bp: warning, ≥ 500bp: recession imminent
   - Chicago Fed NFCI (Adjusted) positive crossover

5-Factor Recession Composite = 0.30·A + 0.25·B + 0.15·C + 0.15·D + 0.15·E
* Each component normalized to 0-100 then weighted-summed

[COUNTER-CYCLICAL STRENGTH — the asymmetric edge of ARDS]

Premise: *True defensives are strong on down days.* Naive low-beta strategies only screen for "low volatility," but the *selective strength on market down days* is what genuinely hedges recession risk.

Signal activation conditions (all four must be met; otherwise score = 0):
   (i)  At least 15 SPX down-days in the last 60 trading days (valid sampling window)
   (ii) 1-year beta ≤ 0.75  ← structural low beta
   (iii) Downside Capture Ratio < 70%  ← weak follow-through on market declines
   (iv) Upside Capture Ratio > 40%  ← not full decoupling on up days

Signal strength:
   Base = (1 - Downside Capture / 100) × (1 + Sortino Ratio × 0.5)
   + Bonus for days when SPX dropped -2% or more AND this holding had positive return (60-day window)
   + Additional bonus if the stock showed strength during HY OAS widening windows (50bp+ widening over 30 days)

Z-score normalize, then scale to 100-point.

(Note: Tier 4 Inverse/VIX ETFs automatically receive 100 in this dimension — by structural inverse correlation.)

[100-POINT COMPOSITE SCORE — 5 Dimensions]

Each holding's total score is a weighted sum of 5 dimensions:

1. Recession Probability Suitability (30% weight)
   - When 5-Factor Recession Composite ≥ 50%, this dimension's weight auto-increases by +10ppt (equal subtraction from others)
   - Tier 1 (Defensive Sector ETFs): higher composite → higher dimension score
   - Tier 2 (Treasury/Gold): same direction, but TLT additionally reflects rate-cut expectations
   - Tier 3 (Individual Defensives): low composite → lower dimension score (defensives underperform in bull markets)
   - Tier 4 (Inverse): if composite < 60%, this dimension scores 0 (= no entry allowed)

2. **Counter-Cyclical Strength (20% weight, NEW)**
   - The Counter-Cyclical Strength score above
   - Score = 0 if activation conditions not all met (double safety)

3. Defensive Quality Factor (20% weight)
   - ROE stability: 5-year ROE standard deviation < 5ppt
   - Earnings Stability: 5-year EPS coefficient of variation
   - Dividend Stability: 10-year no-cut + 5-year consecutive increase
   - Free Cash Flow Yield: bonus for 5%+
   - Debt/Equity ≤ 1.0

4. Volatility & Drawdown Protection (20% weight)
   - 60-day realized volatility (lower → higher score)
   - Max Drawdown in prior 24 months ≤ 15% (covering historical recession windows)
   - Sortino Ratio (downside-deviation-based)
   - Above 200-day MA (BUT Tier 4 scores inversely: bonus when below 200MA)

5. Macro Environment Fit (10% weight)
   - US 10Y Treasury yield trend (declining = bullish for TLT/Utilities, rising = bullish for Inverse)
   - VIX index level (≥ 25 → bonus for all defensive assets)
   - Dollar Index (DXY) trend (inverse correlation with Gold)
   - SPX 30-day realized volatility trend (rising → dimension bonus)

Total Score = 0.30·D1 + 0.20·D2 + 0.20·D3 + 0.20·D4 + 0.10·D5

[REBALANCING RULES — Inheriting AMQS framework, applied to ARDS universe]

Entry (BUY) / CORE Position conditions:
- Total score ≥ 75 → CORE position (Tier 1: max 20%, Tier 2: max 25%, Tier 3: max 10%, Tier 4: max 8%)
- The relevant Tier must be activated under current macro regime
- All pre-filters must pass

Hold (HOLD) conditions:
- Total score 60-75 → SATELLITE position (Tier 1: 8-15%, Tier 2: 10-18%, Tier 3: 5-8%, Tier 4: 3-5%)
- Total score 45-60 → TACTICAL position (3-5%, tight stop-loss)
- Stock-level stop-loss not triggered

FLIGHT_TO_QUALITY special signal (the strategic core):
- Recession Composite ≥ 60% AND Counter-Cyclical Strength ≥ 70 points
- Tier 1 ETFs or Tier 3 individual defensives meeting this signal get +3~7ppt added to base weight
- Can also trigger in Tier 2 (TLT, GLD) — when this happens, it's the full risk-off entry signal

Exit (EXIT) conditions — any of the following:
- Stock-level stop-loss hit (-10% from rebalance entry; tighter than AMQS's -12%)
- Tier 4: -15% stop-loss + auto-liquidate if held over 4 weeks (no long-term holding allowed)
- Macro regime returns to Expansion → liquidate ALL Tier 4 holdings
- Macro regime enters Recession → liquidate 50%+ of Tier 3 individual stocks, redistribute to Tier 1/2

Rebalancing cadence:
- Weekly: signals computed on Friday close → execute Monday open
- Daily: only stop-loss and macro regime change triggers checked daily
- Monthly: full re-computation of 5-Factor Recession Composite (first trading day of month)

[PRE-FILTERS — ARDS-Specific]

Holdings failing any of these are excluded from the universe:
- Market cap ≥ $10B (Tier 1/3); Tier 2/4 ETFs need AUM ≥ $1B
- 30-day average daily trading volume ≥ $50M
- 60-day realized volatility ≤ 35% (Tier 1/3) / ≤ 60% (Tier 2) / ≤ 120% (Tier 4 — VIXY exception allowed)
- Beta ≤ 1.0 (Tier 1/3) / negative beta (Tier 4)
- No dividend cut in prior 12 months (Tier 3 only)

[MACRO REGIME FILTER — 4 PHASES, ARDS-Specific]

Phase 1: Expansion (Defensive weight 30% / Risk asset weight 70% — Tier 4 deactivated)
- 10Y-3M > 100bp (normal curve)
- Sahm Rule < 0.20ppt
- ISM PMI > 52
- LEI 6M change > 0%
- HY OAS < 350bp
- → Tier 1: 20%, Tier 2: 10%, Tier 3: 0%, Tier 4: 0%, Risk assets 70% (external strategy or SPY)

Phase 2: Late-Cycle (Defensive weight 55% — Tier 4 partial activation)
- 2+ of the above conditions deteriorating (e.g., yield curve flattening + LEI slowing)
- VIX average 18-23
- → Tier 1: 25%, Tier 2: 20%, Tier 3: 10%, Tier 4: 0~5% (SH for hedging priority)

Phase 3: Recession-Warning (Defensive weight 80% — Tier 4 fully activated)
- 5-Factor Recession Composite ≥ 50%
- Yield curve inversion + Sahm Rule > 0.30ppt
- ISM < 50 (2 consecutive months)
- HY OAS > 400bp
- → Tier 1: 30%, Tier 2: 30%, Tier 3: 15%, Tier 4: 5~10%

Phase 4: Recession (Defensive weight 100% — Tier 4 max activation)
- 5-Factor Recession Composite ≥ 70%
- Sahm Rule 0.50ppt trigger fired
- OR prior 5 trading days SPX down ≥ 8%
- → Tier 1: 35%, Tier 2: 40%, Tier 3: 10%, Tier 4: 15% (PSQ + VIXY focused)

[POSITION SIZING]

Default: Tier-aware score-tilted allocation
- Apply Tier-level max/min weights per the rules above
- Within each Tier: weight_i = base × (1 + 1.5 × (score_i - 65) / 30)
- Clipping: Tier 1 (5-20%), Tier 2 (5-25%), Tier 3 (3-10%), Tier 4 (2-15%)
- Sum = invested_fraction (per Phase guidelines)

FLIGHT_TO_QUALITY holdings get +3~7ppt boost (equal subtraction from others)

(Optional) Risk Parity sizing:
- Weight = (1/realized_vol) / Σ(1/realized_vol)
- Hard cap on TLT (high-volatility bonds) absolute weight

(Optional) Convexity sizing (Tier 4 only):
- VIXY: contango bleed (5-8%/month) → max holding period 30 days
- Inverse ETFs (SH/PSQ): daily reset → track path-dependency drag during prolonged holds, auto-exit when triggered

[DATA HANDLING PRINCIPLES]
Provide backtest simulation results reflecting known price/financial data from January 2023 ~ May 2026 + macro events (August 2024 yen carry unwind, January 2025 DeepSeek shock, April 2025 Liberation Day tariffs, H2 2025 rate cut cycle, April 2026 CPI 3.8% surprise, May 2026 Hormuz blockade, etc.). Specify ±5% error bands on estimates. Report net returns after deducting 0.03% transaction cost (ETF) / 0.05% (individual stocks) + 0.05% slippage.

[OUTPUT REQUIREMENTS]

Part 1: Current-date (May 17, 2026) scoring table for 25 holdings (4 tables, separated by Tier)
| Ticker | Tier | 5-Factor Recession Score | Counter-Cyclical Score | Dimension Scores (D1/D2/D3/D4/D5) | Total | Signal | Recommended Weight | Stop-Loss |

Include columns:
- Beta (1Y), Downside/Upside Capture, Sortino Ratio
- 60-day volatility, 24M MDD
- Above/below 200MA
- Dividend yield (Tier 3 only)
- Signal: CORE / SATELLITE / TACTICAL / FLIGHT_TO_QUALITY / REDUCE / EXIT / EXCLUDED
- Entry rationale (for FLIGHT_TO_QUALITY, specify market down-day strength pattern)
- Stop-loss level (entry × 0.90; Tier 4 × 0.85)

State the macro regime determination:
- Current Phase: Expansion / Late-Cycle / Recession-Warning / Recession
- Current 5-Factor Recession Composite value + per-component scores
- Rationale: 10Y-3M spread, current Sahm Rule, ISM PMI, LEI 6M, HY OAS

Part 2: Backtest results (Jan 3, 2023 ~ April 30, 2026)
- Cumulative return curves: ARDS vs SPY vs 60/40 (VTI + AGG) vs naive defensive basket (XLP+XLV+XLU equal-weight) vs TLT-only
- Core stats: total return, CAGR, volatility, MDD, Sharpe Ratio, Sortino Ratio, turnover
- Per-event performance: 2023 SVB crisis, Aug 2024 yen carry unwind, Jan 2025 DeepSeek shock, Apr 2025 Liberation Day, Sep-Dec 2025 rate-cut rally, Apr-May 2026 inflation re-acceleration
- *Alpha contribution of FLIGHT_TO_QUALITY signal* analyzed separately (with vs. without comparison)
- *Per-Phase outperformance breakdown*: separately measure alpha in Phase 1 (expected underperform) vs. Phase 3-4 (expected outperform)
- Outperformance by bear-market period (SPX -10%+ windows only)

Part 3: Risk Analysis and Limitations
- ARDS *opportunity cost*: expected -4 to -8ppt annual underperformance vs. SPY in Phase 1 bull markets
- *BEAR_TRAP false-signal pitfall*: 2022-23 yield curve inversion followed by 18-month no-landing case study
- Tier 4 (Inverse/VIXY) *contango bleed*: VIXY 5-8% monthly time-decay, SH/PSQ daily reset path dependency
- TLT duration loss in rising-rate environment (2022 -31%)
- Tax considerations for non-US investors (assume turnover ~80-120%)
- *Defensive valuation risk*: bond-proxy character → simultaneous decline when rates spike (2022: XLU -1%, XLP -3%)

[DISCLAIMER]
This analysis is for educational and informational purposes only. *Defensive strategies generate opportunity costs during bull markets, and record their largest underperformance during false recession signals*. *The FLIGHT_TO_QUALITY signal provides asymmetric alpha during genuine recession entry, but in simple market corrections it can become a source of whipsaw losses* (e.g., during the 2022-23 yield curve inversion, the no-landing regime persisted for 18 months and defensive strategies underperformed SPX by -15ppt). *Tier 4 Inverse/Volatility ETFs are subject to structural time-value decay (contango, daily reset) and converge toward 100% loss over long holding periods* — strictly enforce the 30-day exit rule. Actual investment decisions must reflect personal judgment and professional consultation. Past backtest results do not guarantee future returns.

```

---

## Prompt Structure Explanation

### 5-Dimension 100-point scoring (Symmetric to AMQS)

| Dimension | AMQS-M7 (Momentum) | **ARDS (Defensive)** | Meaning |
| --- | --- | --- | --- |
| D1. Core Macro Signal | 35% (Momentum) | **30% (Recession Composite)** | 5-Factor recession probability |
| D2. Asymmetric Entry Signal | 15% (Pullback-in-Uptrend) | **20% (Counter-Cyclical Strength)** | Relative strength on market down days |
| D3. Fundamental Quality | 25% (Acceleration) | **20% (Defensive Quality)** | ROE/EPS/Dividend stability |
| D4. Volatility Adjustment | 15% (Momentum alpha) | **20% (Downside Protection)** | MDD/Sortino |
| D5. Macro Environment | 10% | **10%** | VIX/Rates/DXY |

### Structural Meaning of the 4-Tier Universe

| Tier | Asset Class | Active Phase | Role |
| --- | --- | --- | --- |
| Tier 1 | Defensive Sector ETFs | All phases | Always-On core defense |
| Tier 2 | Treasury/Gold ETFs | All phases (variable weight) | Dual hedge |
| Tier 3 | Individual Quality Defensives | Phase 2-3 focus | Alpha boost |
| Tier 4 | Inverse/VIX | Phase 2-4 only | True hedge (time-limited) |

### 4-Phase Macro Regime (AMQS's 3 phases → ARDS's 4 phases)

| Phase | 5F Composite | Defensive Weight | Tier 4 Active |
| --- | --- | --- | --- |
| 1. Expansion | < 25% | 30% | ❌ |
| 2. Late-Cycle | 25-50% | 55% | Partial (~5%) |
| 3. Recession-Warning | 50-70% | 80% | Active (5-10%) |
| 4. Recession | > 70% | 100% | Maximum (15%) |

---

## Usage Recommendations

### Recommended weights by signal (Phase 3 baseline)

| Signal | Score Range | Tier 1 Rec | Tier 2 Rec | Tier 3 Rec | Tier 4 Rec |
| --- | --- | --- | --- | --- | --- |
| **CORE** | 75+ | 15-20% | 18-25% | 8-10% | 5-8% |
| **SATELLITE** | 60-75 | 8-15% | 10-18% | 5-8% | 3-5% |
| **FLIGHT_TO_QUALITY** | (variable) | base +3~7ppt | base +5ppt | base +5ppt | — |
| **TACTICAL** | 45-60 | 3-5% | 3-5% | 3-5% | 2-3% |
| **REDUCE** | <45 | <3% | <3% | <3% | 0% |
| **EXIT** | — | 0% | 0% | 0% | 0% |

### Portfolio Construction Notes

- **Paired with AMQS-M7**: ARDS is the *symmetric hedge* to AMQS-M7. Running both at 50:50 yields market beta ~0.5 plus alpha capture during recession entry
- **Tax-aware tier selection**: Tier 2 (TLT, IEF, BIL) has low turnover (long holding) → minimal tax drag. Tier 4 has high turnover but is volatility-driven
- **Bond duration awareness**: TLT has 17+ year duration — a 100bp rate move = ~17% price impact. Size accordingly
- **Foreign investor considerations**: US dividend withholding ~15-30% depending on treaty. Tier 1 (XLP 2.5%, XLU 2.8%) and Tier 3 (KO 3%, VZ 6.5%) yields are pre-withholding

---

## Risk Warnings

- These outputs are *LLM simulations for educational and research purposes*, not investment advice
- *Defensive strategies have heavy opportunity cost in bull markets*: expect -4 to -8ppt annual underperformance vs SPY in Phase 1
- **BEAR_TRAP signal pitfall**: 2022-23 yield curve inversion followed by 18-month no-landing → defensive strategies massively underperformed
- **Tier 4 time-value decay**: VIXY 5-8%/month, SH/PSQ daily reset path dependency. *Strictly enforce 30-day exit rule*
- **Bond duration risk in rate-rising regimes**: 2022 TLT -31%, XLU -1% (defensives lost despite "defensive" label)
- The backtest reflects a *2023-2026 late-cycle environment*; in strong bull markets like 1995-99, massive underperformance is possible

---

## Authorship

**Series**: vibe-investing — ARDS new module (the symmetric hedge to AMQS)
**Related strategies**:
- [AMQS Original (NASDAQ-100 + AI Value Chain)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD)
- [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD)
- **ARDS** — Recession-Defensive 4-Tier strategy (*this prompt*)

**Author**: Dennis Kim (HoKwang Kim / 김호광)
- Betalabs Inc. CEO, Independent Researcher
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)

**License**: MIT

---

> *"In a bull market, defense is a tax. In a bear market, defense is oxygen. The art is knowing when the air is thinning."*
