# Dual-Engine Capital Compounder Quant Strategy Using LLM (English Edition)

> **U.S. Financial + Retail Dividend Quant Strategy**
> Identifies Top 10 stocks across *Financials* and *Consumer Discretionary/Staples (Retail)* sectors of the S&P 500 that simultaneously satisfy *capital return yield + cycle defensibility* + Equal-weight portfolio simulation

---

## How to Use

1. *Copy the entire prompt block below* (use the copy button at the top right of the code block)
2. *Paste directly* into Claude / GPT-5 / Gemini / DeepSeek or any LLM
3. The LLM auto-generates Top 10 stocks + Dual-Engine balance analysis + portfolio analytics

> **Language Selection Guide**: This English edition is for users wanting *English output*. The English prompt achieves *~30-40% token savings* vs the Korean version. For Korean output, use [Dual Engine Compounder Prompt kr.MD](./Dual%20Engine%20Compounder%20Prompt%20kr.MD). For Chinese-language analysis, see [Dual Engine Compounder Prompt CN.MD](./Dual%20Engine%20Compounder%20Prompt%20CN.MD).

---

## The Prompt (English Edition)

```
[ROLE]
You are a portfolio manager and Head of Quantitative Research at a top-tier global asset management firm, with 14 years of experience running capital-return strategies across both Financials and Consumer Retail sectors simultaneously. Your decision framework is built on the 'Dual-Engine Capital Compounder' model — integrating two distinct capital rotation mechanisms:

- Financial Engine: NIM, fees, and asset management revenue rotated through capital duration
- Retail Engine: inventory turnover + short-cycle consumer cash flow conversion

These two engines respond *asymmetrically* to macro cycles, and holding both simultaneously naturally dampens portfolio volatility.

Today's date is May 2, 2026. (Assume this as the analytical reference date.)

[ANALYSIS UNIVERSE]
From the constituents of the S&P 500, select 10 names total — 5 from each of the following sectors.

【Financial Sector (5 names)】 - balanced selection across these 4 sub-segments:
- Megabanks: JPM, BAC, WFC, C
- Asset Management & Exchanges: BLK, BX, KKR, AMP, TROW, SCHW, CME, ICE, NDAQ
- Card Networks & Premium Cards: V, MA, AXP, COF, DFS
- Insurance: BRK.B, TRV, PGR, ALL, AFL, CB, MET, PRU, AIG

【Retail Sector (5 names)】 - balanced selection across these 4 sub-segments:
- Mass Retail: WMT, COST, TGT, BJ
- Home Improvement: HD, LOW
- Off-Price & Specialty: TJX, ROST, ULTA, BBY, DG
- Restaurant & QSR: MCD, SBUX, YUM, CMG, DPZ, TXRH

[SCREENING CRITERIA]
[Financials]
- 5+ consecutive years of dividend increases OR consistent buyback program
- ROE ≥ 12% (Megabanks) or ≥ 18% (Asset Mgmt / Cards)
- Tier 1 Capital Ratio ≥ 12% (banks) OR Net Debt / EBITDA ≤ 1.5x (non-banks)
- Payout ratio ≤ 50% AND Total Capital Return Yield (buybacks + dividends) ≥ 50%

[Retail]
- 5+ consecutive years of dividend increases (Aristocrat / King status preferred)
- ROIC ≥ 15%, FCF Margin ≥ 6%
- Net Debt / EBITDA ≤ 3.0x
- Positive same-store sales (SSS) over rolling 5-year average

[SCORING SYSTEM - 100 points per stock]

1. Earnings Quality & Capital Return (35% weight)
   - Financials: ROE, Tier 1 Capital, NIM stability, fee margin
   - Retail: ROIC, FCF conversion, SSS stability, omnichannel monetization
   - Both: Total Capital Return Yield (TCRY = buyback yield + dividend yield)

2. Dividend Growth Momentum (30%)
   - 5Y / 10Y dividend CAGR
   - Consecutive years of dividend increases (25+ Aristocrat / 50+ King bonus)
   - Payout ratio stability trend
   - Price-momentum patterns around dividend announcements

3. Valuation (20%)
   - Financials: P/TBV (Tangible Book Value), Forward P/E, Yield spread vs 10Y UST
   - Retail: EV/EBITDA, Forward P/E, FCF Yield, multiple position vs 5Y average
   - Both: PEG (P/E ÷ EPS Growth) ≤ 2.0 preferred

4. Cycle Defensibility (15%)
   - Financials: Net Charge-off Ratio trend, Loan Loss Provisions, CCAR stress test outcomes
   - Retail: Gross margin stability, inventory turnover, omnichannel mix (e-commerce ≥ 15%)
   - Both: 2008 + 2020 recession drawdown depth + recovery speed

[DATA HANDLING PRINCIPLES]
Conduct simulation based on financial data and price history known through April 2025 + Q1 2026 earnings. Disclose ±5% error margins on all estimates. For Financials, incorporate Federal Reserve CCAR stress test outcomes and FOMC dot plot into macro assumptions.

[OUTPUT REQUIREMENTS]

Part 1: Top 10 Stock Report (table format included)
- Ticker, company name, sector (Financial/Retail), sub-segment, current price (estimated), market cap
- Dividend yield, 5Y dividend CAGR, Total Capital Return Yield (TCRY)
- Payout ratio, ROE or ROIC, key multiple (P/TBV or EV/EBITDA)
- Sub-scores for all 4 categories + total score
- 3 core investment theses (capital return narrative + quantitative metrics)
- 2 risk factors (NIM compression, consumer weakness, regulation, etc.)
- 12-month target total return + stop-loss level

Part 2: Dual-Engine Balance Analysis
- Rationale for 50:50 Financial vs Retail weighting
- Inter-engine correlation (1990-2025 historical)
- Optimal weighting suggestion by macro cycle stage (Early / Mid / Late / Recession)

Part 3: 10-Stock Equal-Weight Portfolio
- Expected dividend yield + TCRY (pre-tax)
- Estimated beta, volatility, Sharpe Ratio (3Y)
- Qualitative outperformance assessment vs S&P 500
- Cycle inflection signals (e.g., 10Y UST surge, consumer confidence collapse, NIM compression, e-commerce share shifts)

[DISCLAIMER]
This analysis is for educational and informational purposes only. Financials carry *systemic crisis* drawdown risk of -50%+, while Retail names face *recession* revenue contraction and margin pressure. Actual investment decisions must be made through individual judgment and consultation with qualified professionals. Past dividend records do not guarantee future dividends — note that during the 2008 GFC, major U.S. banks cut dividends by 90%+.
```

---

## Prompt Architecture

### Dual-Engine Model

The prompt forces the LLM to evaluate *two distinct capital rotation mechanisms* in parallel:

| Engine | Capital Rotation Mechanism | Core KPIs | Macro Sensitivity |
| --- | --- | --- | --- |
| **Financial Engine** | NIM·fees·asset mgmt rev (capital duration) | ROE, NIM, AUM growth | Rates + credit cycle |
| **Retail Engine** | Inventory turnover + consumer cash flow (short cycle) | ROIC, SSS, inventory turns | Consumer confidence + wages |

> **Asymmetry as Hedge**: In rising-rate regimes, *Financial NIM expands* but *Retail consumption contracts*. In falling-rate regimes, *Financial NIM compresses* while *Retail consumption recovers*. Holding both *naturally hedges macro cycle volatility*.

### Scoring Weight Philosophy

| Dimension | Weight | Core Question |
| --- | --- | --- |
| **Earnings Quality & Capital Return** | **35%** | "How much value is *returned to shareholders*?" |
| **Dividend Growth Momentum** | **30%** | "Does the return *compound* over time?" |
| **Valuation** | **20%** | "Is the price *reasonable now*?" |
| **Cycle Defensibility** | **15%** | "Can it *survive a recession*?" |

> **Difference vs AI Super Cycle Prompt**: AI revenue exposure (35%) is replaced by *Earnings Quality & Capital Return (35%)*. *Momentum & Flows (15%)* is replaced by *Cycle Defensibility (15%)* — in dividend investing, *survival capability* matters more than *technical momentum*.

---

## Recommended Portfolio & Outlook

The 10 stocks the LLM is *expected to surface* (simulation-based):

### 🏦 Financial Engine (5 names)

| # | Ticker | Company | Sub-segment | Score | Div Yield | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **JPM** | JPMorgan Chase | Megabank | **88** | 2.05% | 6.5% |
| 2 | **BLK** | BlackRock | Asset Mgmt | **86** | 1.90% | 4.8% |
| 3 | **V** | Visa | Card Network | **90** | 0.65% | 4.7% |
| 4 | **AXP** | American Express | Premium Card | **85** | 1.05% | 5.1% |
| 5 | **CB** | Chubb | Insurance (P&C) | **82** | 1.25% | 4.0% |

### 🛒 Retail Engine (5 names)

| # | Ticker | Company | Sub-segment | Score | Div Yield | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | **HD** | Home Depot | Home Improvement | **87** | 2.17% | 6.2% |
| 7 | **WMT** | Walmart | Mass Retail | **84** | 0.87% | 2.9% |
| 8 | **TGT** | Target | Discount Retail | **80** | 2.89% | 6.5% |
| 9 | **TJX** | TJX Companies | Off-Price Retail | **86** | 1.15% | 4.7% |
| 10 | **MCD** | McDonald's | QSR | **83** | 2.28% | 5.4% |

> **TCRY (Total Capital Return Yield) = Dividend Yield + Buyback Yield** — the *complete* measure of capital return. Typically 2-3x higher than the headline dividend yield alone.

### Portfolio Selection Rationale (Quant Lens)

1. **Bilateral Hedge Structure**: In rising-rate regimes, *JPM/BLK NIM/AUM revenues expand* while *HD/TGT housing-linked consumption weakens*. In falling-rate regimes, the *pattern reverses*. → **Negative correlation between engines absorbs volatility.**

2. **Card Networks as Bridge**: V and AXP are *classified as Financials* but their revenue mechanics resemble *Retail transaction fees*. They serve as a *bridge between the two engines* — fusing the betas naturally.

3. **Dividend Aristocrat / King Concentration > 60%**:
   - **Aristocrats (25Y+)**: TJX, MCD (28Y+), TGT (54Y+, *King status*), CB (31Y+)
   - **Long dividend growth track**: HD (15Y+), JPM (14Y+ post-restart), V (16Y+), BLK (21Y+)
   - This pedigree *statistically reduces* dividend cut probability in systemic stress.

### 12-Month Market Scenarios

| Scenario | Probability | S&P 500 Return | Portfolio Return |
| --- | --- | --- | --- |
| 🟢 **Goldilocks** (growth + disinflation + rate cuts) | 30% | +18% | **+22%** |
| 🟡 **Base Case** (moderate growth + stable rates + steady consumer) | 45% | +9% | **+13%** |
| 🟠 **Stagflation** (inflation re-emerges + growth slows) | 20% | -5% | **-2%** |
| 🔴 **Recession** (unemployment 6%+ + credit cycle cracks) | 5% | -22% | **-15%** |

> **Probability-Weighted Expected Return**: S&P 500 +9.5% vs Portfolio **+12.6%** → **~+3.1pp Alpha**

> **Defensive Edge**: In the recession scenario, S&P 500 (-22%) vs Portfolio (-15%) implies a *7pp downside protection*. This buffer comes from dividend cut resilience + retail sales inelasticity in staples.

### Cycle Inflection Signals (Watch List)

- ⚠️ **Financial Cycle**: Top-4 banks aggregate Net Charge-off ≥ 1.0% (*currently 0.6%*) signals credit cycle deterioration
- ⚠️ **Card Spending**: V and MA payment volume YoY growth slowing below +5% signals consumer weakness
- ⚠️ **Consumer Confidence**: Conference Board CCI ≤ 90 signals retail revenue compression
- ⚠️ **Housing Cycle**: 30Y mortgage rate ≥ 7.5% OR Existing Home Sales SAAR ≤ 3.5M units signals HD/LOW pressure
- ⚠️ **Asset Mgmt**: BLK/BX management fee margins compressing below 14bps signals passive disruption acceleration

---

## Output Utilization Guide

### Part 1 (Top 10 Stocks)

* **Score ≥ 85**: *Core position* candidates — 12-15% weight (V, JPM, HD, TJX)
* **Score 80-85**: *Satellite positions* — 8-10% weight, quarterly review
* **Score < 80**: *Tactical positions* — ≤5% weight, macro-signal driven entries

### Part 2 (Dual-Engine Balance)

* **Early Cycle (recovery)**: Financial weight ↑ (60-70%) — credit recovery + loan growth
* **Mid Cycle (expansion)**: 50:50 balance
* **Late Cycle (peak)**: Retail weight ↑ (60%) — defensive + wage inflation beneficiaries
* **Recession**: Cash allocation ↑ + concentrated retail staples (WMT, COST)

### Part 3 (Equal-Weight Portfolio)

* Expected Dividend Yield + TCRY (pre-tax): *5.0-6.5%* range
* Estimated beta: *0.85-1.00* (slightly defensive vs market beta 1.0)
* Outperformance vs S&P 500 favored *in late-cycle / stagflation environments*

---

## Token Efficiency Comparison

| Language | Input Tokens | Output Tokens | Total Cost (Claude Opus 4.7) |
| --- | --- | --- | --- |
| Korean | ~1,800 tokens | ~4,500 tokens | ~$0.099 |
| English | ~1,200 tokens | ~3,200 tokens | ~$0.069 |
| Chinese (Simplified) | ~1,300 tokens | ~3,500 tokens | ~$0.076 |

> **Recommendation**: For *recurring use (e.g., monthly rebalancing)*, English version saves *~$7-12 per year*.

---

## Considerations for International Investors

### Tax (U.S. Non-Resident Investors)

* **Dividend Withholding**: U.S. statutory 30%, reduced to 10-15% under most tax treaties (consult your country's treaty)
* **Capital Gains**: Generally taxed in your country of residence (W-8BEN required)
* **Estate Tax**: U.S. estate tax exposure for non-resident aliens with U.S. assets > $60K

### Currency Hedging Decision

* **USD Exposure** (direct holdings): Benefits from dollar strength in late-cycle regimes
* **Hedged Vehicles** (currency-hedged ETFs): Eliminates FX risk — recommended when local currency is at multi-year lows vs USD

### Regional ETF Alternatives

| ETF | Tracking | Match Score |
| --- | --- | --- |
| NOBL | S&P 500 Dividend Aristocrats | ★★★★★ (TGT, CB, MCD direct holdings) |
| XLF | S&P 500 Financials | ★★★★ (JPM, V, BLK weight) |
| XRT | S&P Retail Select | ★★★★ (TJX, TGT, HD weight) |
| SCHD | Schwab Dividend Equity | ★★★★ (high overlap with thesis) |

---

## Risk Disclaimer

* This prompt's output is *educational/research-grade simulation*, not actual investment advice
* LLM data is based on *information known through April 2025*; *not real-time price/dividend data*
* Estimates carry *±5% error margins*; *re-validate against live market data* before action
* **In the 2008 GFC, BAC cut dividends by 90% and C cut by 97%** — *Dividend Aristocrat status was revoked*. Be aware of *systemic crisis exposure* in megabanks.
* **In the 2020 pandemic, WMT/COST grew revenue +10-15%**, while *restaurant/travel/luxury retail saw -30-50% revenue shock*. Sub-segment differentiation within Retail is critical.
* **Card network antitrust risk (V, MA)**: U.S. DOJ payment network monopoly litigation + stablecoin proliferation (USDC, PYUSD) imply *long-term share erosion* risk
* Always *cross-validate LLM-generated recommendations* against independent data sources (SeekingAlpha, Morningstar, Bloomberg)

---

## Authorship

**Series**: vibe-investing — Awesome Claude Quant Scripts
**Related sub-strategies**:

* [Dividend Growth Prompt EN.MD](../Dividend%20growth%20prompt/Dividend_Growth_Prompt_EN.md) — 6-sector dividend growth
* [AI Super Cycle Prompt EN.MD](../AI%20Super%20Cycle%20Prompt/AI%20Super%20Cycle%20Prompt%20EN.MD) — 4-Layer AI value chain
* [Long-Term Dividend Investing](../Long-Term%20Dividend%20Investing) — Code implementation for long-term holdings
* [DAT Quant Strategy](../DAT%20quant%20strategy) — Digital asset treasury company strategy

**Author**: Dennis Kim (HoKwang Kim / 김호광)

* Independent Researcher, Betalabs Inc. CEO, Former CEO of Cyworld Z
* ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
* GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
* Email: [gameworker@gmail.com](mailto:gameworker@gmail.com)

**Date**: May 2, 2026 v1.0
**License**: MIT (free use, attribution appreciated)

---

> *"Compounding is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."* — Albert Einstein
