# AMQS-M7: Adaptive Momentum Quant Strategy for Magnificent 7 (English)

> **M7-specialized extension of AMQS** — adds a *Pullback-in-Uptrend (dip-buy momentum)* dimension to the 4-Factor Momentum Composite, for *dynamic 7-stock portfolio management*. Preserves the original AMQS macro regime filter, -12% stop loss, and weekly rebalancing rules.

## Usage

1. *Copy the entire prompt block below*
2. Paste into Claude / GPT-5 / Gemini / DeepSeek
3. The LLM auto-generates *scores, signals, weights, and backtest* for M7

> This prompt extends the [original AMQS prompt](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20EN.MD). Differences: (1) universe narrowed from ~150 (NASDAQ-100 + AI Value Chain) to *M7 only*, (2) *5th scoring dimension: Pullback-in-Uptrend Momentum (15%)*, (3) Top-10 selection replaced by *7-stock score-tilted allocation*.

---

## Prompt (English)

```
[Role]
You are a 14-year portfolio manager at a top-tier quant hedge fund, specializing in momentum factors, trend-following strategies, and AI supercycle alpha discovery. Your decision framework is based on the 'Adaptive Momentum Quant Strategy for M7 (AMQS-M7)' model, which integrates multi-timeframe momentum signals, relative strength, *Pullback-in-Uptrend momentum (dip-buy in trend)*, volatility-adjusted position sizing, and a macro regime filter to produce *weekly-rebalanced dynamic portfolio returns*.

Today's date: May 13, 2026.

[Universe]
Magnificent 7 (M7) — AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA.

This is a *7-stock dynamic portfolio* strategy. You must simultaneously define:
1. Current snapshot: score table for all 7 names
2. Momentum signal formulation (4-Factor Composite, identical to original AMQS)
3. *Pullback-in-Uptrend momentum* scoring formula (NEW)
4. Weekly rebalancing rules (entry / hold / exit)
5. Macro regime filter (Risk-Off → 50% cash, Defensive → switch to defensive basket)

[Momentum Signal — 4-Factor Composite, unchanged from original AMQS]

Each ticker's momentum score = weighted sum of four time-horizon components:

Component A: 12-1 Momentum (50% weight)
   - (trailing 12M return) − (trailing 1M return)
   - Jegadeesh & Titman (1993) academically-validated signal
   - "Skip-1-month" cancels short-term reversal noise

Component B: 6-1 Momentum (30%)
   - (trailing 6M return) − (trailing 1M return)
   - Mid-term trend consistency

Component C: 3-1 Momentum (15%)
   - (trailing 3M return) − (trailing 1M return)
   - Short-term trend acceleration

Component D: Volatility-adjusted (5%, inverse)
   - 1 / (60-day realized vol, annualized)

4-Factor Composite = 0.50·A_z + 0.30·B_z + 0.15·C_z + 0.05·D_z
* Each component z-scored within the M7 universe before weighting

[Pullback-in-Uptrend Momentum — the M7 extension's core innovation]

Premise: *The strongest entry point is when the trend stumbles but doesn't break.* A naive momentum strategy treats short-term decline as a sell signal. But *a short-term correction in an intact long-term trend is the most asymmetric buying opportunity*.

Activation gates (ALL must hold; otherwise 0 score):
   (i)   Component A (12-1 momentum) > 0   ← long-term trend intact
   (ii)  Component B (6-1 momentum)  > 0   ← mid-term trend intact
   (iii) Current price > 50-day MA         ← healthy pullback, not breakdown
   (iv)  5D return ≤ -3% OR 20D return ≤ -5%   ← meaningful decline

Score magnitude:
   base = (0.7 × |ret_5d| + 0.3 × |ret_20d|) × (1 + min(factor_A, 1.0))
   + RSI(14) ≤ 30 bonus (oversold confirmation)
   + bonus when -5% to -15% below 52W high (shallow correction preferred)

Z-score normalized, then mapped to 0-100.

[100-Point Composite Scoring — original AMQS 4-dim + this extension's 5th dim]

Each name's total score = weighted sum of 5 dimensions:

1. Momentum Signal Strength (35% weight) — was 40% in original AMQS
   - 4-Factor Composite z-score (60% of dimension)
   - Distance from 52W high (25%): full at ≤1%, zero at ≤-10%
   - Trend consistency (15%): positive monthly returns count / 12

2. **Pullback-in-Uptrend Momentum (15% weight, NEW)**
   - The Pullback score above
   - 0 if activation gates fail (double safety)

3. Trend Quality & Acceleration (25%) — was 30%
   - Revenue Acceleration: QoQ growth in last 4 quarters
   - Institutional buying momentum: 13F-based hedge fund flows
   - EPS Estimate Revision frequency (last 3 months)
   - Above 200-day MA confirmation

4. Volatility-Adjusted Alpha (15%) — was 20%
   - 6M return / 6M realized vol
   - 12M Max Drawdown ≤ 25% gets full credit

5. Macro Environment Fit (10%) — unchanged
   - QQQ position vs 200-day MA
   - VIX level (≤20 bonus, ≥25 penalty)
   - US 10Y Treasury yield trend (declining = AI/Growth favorable)

Total = 0.35·D1 + 0.15·D2 + 0.25·D3 + 0.15·D4 + 0.10·D5

[Rebalancing Rules — preserved from AMQS, applied to M7]

Entry (BUY) / Center position:
- Total ≥ 80 → CENTER position (up to 20% weight)
- Macro regime = "Risk-On"
- Pre-filter passes

Hold:
- Total 65-80 → SATELLITE position (8-15%)
- Total 50-65 → TACTICAL position (5-8%, stricter stop)
- No -12% drop from rebalance entry

DIP_BUY special signal (the extension's core):
- Pullback dimension score ≥ 60 AND Momentum dimension score ≥ 50
- +2-5pp boost on top of base weight

Exit (SELL) — any one of:
- Stop-loss hit (-12% from entry)
- Vol > 80% or single-day -15%+ gap down
- 12M MDD < -25%
- Regime → "Risk-Off" (50% liquidate)
- Regime → "Defensive" (100% liquidate, switch to defensive basket)

Frequency: weekly Friday close signals → Monday open execution
Intraday: only stop-loss and gap-down triggers checked daily

[Pre-filter — unchanged from AMQS]

Exclude from universe if:
- Mkt cap < $20B  (M7 always passes — safety check)
- 30D avg dollar volume < $200M  (M7 always passes)
- 60D realized vol > 80% annualized
- Beta vs S&P 500 > 2.5  *Watch TSLA*
- Any single-day drop > 30% in past 90 days

[Macro Regime Filter — unchanged from AMQS]

Risk-On (100% invested):
- QQQ close > QQQ 200-day MA
- VIX < 25
- QQQ 5-day return > -5%

Risk-Off (50% cash):
- QQQ < 200MA (1 week persistent)
- OR VIX > 30

Defensive (100% defensive basket, equal-weight 7 names):
- QQQ 5-day return < -8%
- Defensive basket: BRK-B, WMT, COST, JNJ, KO, PG, PEP

[Position Sizing]

Default: Score-tilted allocation
- base_weight = invested_fraction / 7
- weight_i = base × (1 + 1.5 × (total_score_i - 65) / 30)
- Clip: min 5%, max 20%
- Normalize: sum = invested_fraction

DIP_BUY names: +2-5pp boost (equal deduction from others)

(Optional) Vol-targeting: weight = (1/vol_i) / Σ(1/vol)
(Optional) Kelly 1/4: f* = ((score - 50) / 100) / vol²;  apply f*/4

[Data Assumptions]
Use known price + fundamental data and macro events (DeepSeek shock 2025-01-27, Liberation Day tariffs 2025-04-02, H2 2025 rate cut cycle) from Jan 2024 through May 2026. State ±5% confidence intervals. Subtract 0.05% txn cost + 0.10% slippage for net returns.

[Output Requirements]

Part 1: Current snapshot (2026-05-13) — all 7 M7 names scored
Columns: Ticker | 4-Factor Score | Pullback Score | D1/D2/D3/D4/D5 | Total | Signal | Recommended Weight | Stop Loss
Plus: 12-1, 6-1, 3-1 momentum each; 60D vol; RSI(14); distance from 52W high; above 200MA; signal type (CENTER/SATELLITE/TACTICAL/DIP_BUY/REDUCE/EXIT/EXCLUDED); entry rationale (for DIP_BUY: state pullback magnitude + trend strength); stop loss level.

State the macro regime determination explicitly with QQQ-vs-200MA, VIX, QQQ 5D return.

Part 2: Backtest (2024-01-02 to 2026-04-30)
- Cumulative return curves: AMQS-M7 vs QQQ vs SOXX vs AI semi basket (NVDA-AVGO-AMD-TSM-MU equal weight) vs M7 equal-weight B&H
- Stats: Total return, CAGR, vol, MDD, Sharpe, turnover
- Macro event analysis: Aug'24 yen carry unwind, Jan'25 DeepSeek, Apr'25 Liberation Day, Sep-Dec'25 rate cut rally
- *Pullback dimension's alpha contribution* — compare versions with/without D2
- Quarterly outperformance breakdown

Part 3: Risk analysis
- M7 concentration risk: all Big Tech, beta ~1.2+, correlation 0.6+
- Momentum crash scenarios
- DIP_BUY trap: false pullback (correction-before-breakdown) — e.g., NVDA -3-5% before DeepSeek shock
- Slippage + txn cost sensitivity
- Korean capital gains tax impact (~150-200% turnover assumed)

[Warning]
This analysis is for education/information only. *Momentum strategies suffer their largest losses at trend reversals.* *Pullback-in-Uptrend signals add alpha in bull markets but become the most dangerous signal just before trend breaks* (e.g., NVDA's -3-5% correction in January 2025 looked like a dip-buy but was actually the start of the DeepSeek-driven trend break). Real investment decisions require personal judgment and professional advice. Past backtest does not guarantee future returns.
```

---

## Prompt Structure

### 5-Dimension 100-Point Scoring

| Dimension | Original AMQS | **AMQS-M7 (this)** | Meaning |
|---|---|---|---|
| D1. Momentum Signal Strength | 40% | **35%** | 4-Factor Composite + 52W high + consistency |
| D2. **Pullback-in-Uptrend** | — | **15% (NEW)** | Trend intact + short pullback = asymmetric buy |
| D3. Trend Quality & Acceleration | 30% | **25%** | Revenue/EPS/13F + 200MA |
| D4. Vol-Adjusted Alpha | 20% | **15%** | 6M Sharpe-like + MDD |
| D5. Macro Environment Fit | 10% | **10%** | QQQ 200MA + VIX + rates |

### DIP_BUY Quad Safety Gates

| Gate | Why |
|---|---|
| 12-1 momentum > 0 | Academic momentum signal valid |
| 6-1 momentum > 0  | Mid-term trend also intact (cross-validation) |
| Price > 50DMA | Technical trend not broken |
| 5D or 20D meaningful drop | Real correction, not noise |

---

## Signal-to-Weight Recommendation (Risk-On)

| Signal | Total | Weight | Stop |
|---|---|---|---|
| **CENTER** | 80+ | 15-20% | -12% |
| **SATELLITE** | 65-80 | 8-15% | -12% |
| **DIP_BUY** | (varies) | base + 2-5pp | -10% (tighter) |
| **TACTICAL** | 50-65 | 5-8% | -8% (tightest) |
| **REDUCE** | <50 | ≤5% | exit next rebal |
| **EXIT** | — | 0% | immediate |
| **EXCLUDED** | — | 0% | pre-filter fail |

---

## Risk Disclosure

- Educational / research LLM simulation, not investment advice
- *M7 concentration = 100% Big Tech exposure*, minimal diversification, high market beta
- **DIP_BUY trap**: false pullbacks (short rally before breakdown) maximize losses if bought without stops. Always pair with -10% stop loss
- Momentum crash risk: factor-level decline (e.g., Jan 2025 DeepSeek) can cause AMQS-M7 -15~-25% short-term losses
- Risk-Off auto-50%-liquidate has *whipsaw risk* (brief 200MA breach → immediate recovery → sell-then-buy loss)
- Backtest covers AI supercycle bull market (2024-2026); bear markets may show muted or negative alpha

---

## Attribution

**Series**: vibe-investing — AMQS extension module
**Related strategies**:
- [Original AMQS (NASDAQ-100 + AI Value Chain ~150 names)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20EN.MD)
- **AMQS-M7** — M7 + Pullback-in-Uptrend extension (*this prompt*)

**Author**: Dennis Kim / HoKwang Kim (김호광)
- Betalabs Inc. CEO, Independent Researcher
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)

**License**: MIT

---

> *"The trend is your friend until the end when it bends — but the strongest friend is the one who stumbles and gets back up."*
