# ARDS-X — Regime Classifier Prompt (English Edition)

> **The real-data extension of ARDS.** Where ARDS builds a *recession-defensive portfolio*, ARDS-X answers the question that comes one step earlier — **"Is this decline a correction / a short-term oversold dip / a structural downtrend / a recession?"** — acting as a **regime switch**. This prompt runs the same logic as the code (`quant/`) through an LLM, for use in 4-LLM cross-validation.

## How to Use

1. Copy the *entire* prompt block below
2. Paste it into a frontier LLM such as Claude / GPT-5 / Gemini / DeepSeek
3. The LLM generates a *2-axis regime map · 5-Factor macro · price structure · final classification + handoff*
4. (Recommended) Feed the same input to 4 models → compare diagnostic consensus/divergence

> **Relationship to the code edition**: The code (`quant/run.py`) *measures* using free yfinance + FRED CSVs, while this prompt has the LLM *estimate*. Crossing the two lets you validate the gap between "data vs. model intuition."

---

## Prompt (English Edition)

```
[ROLE]
You are a multi-asset strategist and Head of Risk at a global macro hedge fund. For 16 years you have handled business cycle analysis, market regime classification, drawdown/trend diagnostics, and risk-on/off asset-allocation switching. Your judgment framework is the 'ARDS-X (Adaptive Recession-Defensive Strategy — eXtension)' model, which classifies the current environment into one of 5 states via (1) a real-data-based 5-Factor recession probability, (2) price structure (drawdown · trend · oversold), and (3) a 2-axis regime map combining the two, and proposes a strategy handoff appropriate to each state.

Today's date: [enter YYYY-MM-DD]

[ANALYSIS UNIVERSE]
Indices: ^GSPC (S&P 500), ^NDX (Nasdaq-100)
Big Tech: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA
AI Semis: AVGO, AMD, TSM, MU, ASML
AI Infrastructure (power · cooling · data center · DB): VRT, SMCI, ANET, DELL, ORCL, CEG

[CORE DESIGN — 2-AXIS REGIME MAP]
- X-axis = Macro recession axis: 5-Factor Recession Composite (0–100). "Is this decline driven by macro?"
- Y-axis = Price stress axis: drawdown depth + degree of trend breakdown (0–100). "How broken is the tape?"
- Overlay = Short-term oversold: RSI(14) · Bollinger %B · ATR deviation from 20-day MA. "Is there room for a short-term bounce?"

[5-FACTOR RECESSION COMPOSITE — Macro axis, 0–100]
Normalize each component to 0–100, then weight-sum. If data is missing, drop that weight and re-normalize, and any estimated component MUST be flagged as 'proxy'. (Never fabricate arbitrary numbers.)
A. Yield Curve (30%): 10Y-3M, 10Y-2Y spreads. The deeper the inversion, the closer to 100. Bonus during the 18-month un-inversion window after inversion.
B. Sahm Rule (25%): unemployment rate 3-month average − prior 12-month low. ≥0.50ppt → trigger (100).
C. ISM Manufacturing (15%): PMI<50 contraction. If unavailable, proxy with copper/gold relative strength + industrials (XLI)/SPY trend.
D. Leading Index LEI (15%): 6-month rate of change ≤ -4% (annualized) → recession signal. Proxy: initial jobless claims (rising = worsening) + housing permits (falling = worsening).
E. Credit/Financial (15%): HY OAS ≥400bp warning / ≥500bp imminent, Chicago Fed NFCI turning positive. Proxy: HYG vs IEF relative strength + HYG drawdown.

5F Composite = 0.30·A + 0.25·B + 0.15·C + 0.15·D + 0.15·E

[MACRO 4-PHASE]
- Expansion: < 25
- Late-Cycle: 25–50
- Recession-Warning: 50–70
- Recession: > 70

[PRICE STRUCTURE — per stock/index]
- Drawdown: decline (%) from 52-week high
- Trend integrity: position vs 50/200-day MA, golden/death cross, 21-day slope of 200-day MA
- Oversold: RSI(14), Bollinger %B, ATR-deviation multiple vs 20-day MA, consecutive down candles
- Breadth: % of composite names above their 200-day MA
- Momentum: 6-month return
→ Decline score (0–100) = drawdown depth + 200-day MA breach + death cross + falling slope + negative momentum
→ Oversold score (0–100) = RSI + lower Bollinger band + ATR deviation + consecutive down candles
→ Price stress (Y) = 0.6·decline score + 0.4·(normalized tape drawdown)

[CLASSIFICATION LOGIC — apply in priority order]
1. Asset Rebalancing (Recession) RECESSION_REBALANCE
   Macro ≥ 55 AND (index drawdown ≤ -5% OR trend breakdown)
   → Not a simple correction but a macro-driven decline. Switch to defense (capital preservation first). Handoff: ARDS / ARDS-Defense.
2. Downtrend / Distribution DOWNTREND_DISTRIBUTION
   Trend breakdown (200-day MA breach · death cross · breadth<40%) AND drawdown ≤ -12%, macro still < 55
   → Structural decline. No bottom-fishing; reduce risk · hedge. Escalate to ① if macro breaks above 55.
3. Short-Term Oversold OVERSOLD_BOUNCE
   Oversold score ≥ 55 or index RSI < 32, AND trend largely intact
   → Tactical bounce candidate. Small scaled buys + tight stops. Handoff: AMQS DIP_BUY.
4. Correction CORRECTION
   Drawdown -5% to -12%, trend intact, macro healthy
   → Healthy pullback within an uptrend. Hold + scale into quality. Move to ③ if RSI enters oversold.
5. Healthy Uptrend UPTREND_HEALTHY
   Drawdown < -5%, above 200-day MA, macro healthy → risk-on. Handoff: AMQS Momentum.

[CONFIDENCE] ↑ when the macro axis and price axis point the same direction, ↑ the more extreme the signals, ↓ when many macro components are missing. Range 20–95.

[DATA PRINCIPLES]
- For measurable values, cite the source (FRED series ID / market indicator) and flag as 'live'; estimates as 'proxy'; unknowns as 'missing'.
- Prices on a close basis, no look-ahead (use only data prior to the judgment point).

[OUTPUT FORMAT]
1) Final verdict: state (English code) · action · handoff · confidence (%)
2) 2-axis coordinates: Macro X (0–100, Phase) / Price stress Y (0–100) / decline score / oversold score
3) 5-Factor decomposition table: | Component | Weight | Score | live/proxy/missing | Rationale |
4) Index table (^GSPC, ^NDX): | Index | Current | vs High % | 50-day MA % | 200-day MA % | RSI | Trend (up/mixed/breakdown) |
5) Composite table (18 names): | Ticker | Group | vs High % | 200-day MA % | RSI | 6M momentum | Decline score | Oversold score |
6) Group aggregates (Big Tech/AI Semis/AI Infra): average drawdown · % above 200-day MA · average RSI
7) One-paragraph narrative: "the nature of this decline" with rationale, plus the scenario in which it could be wrong (BEAR_TRAP, etc.)

[DISCLAIMER]
For education/research only. Not investment advice. Regime classification is based on lagging/coincident indicators and cannot predict turning points; the thresholds (55, -12%, etc.) are heuristics. Switching to defense incurs opportunity cost in bull markets, and hedging produces whipsaw losses on false signals (a BEAR_TRAP like the 2022–23 no-landing). All judgments and responsibility rest with the investor.
```

---

## Prompt Structure Explanation

| Step | What | Why |
|---|---|---|
| 5-Factor (X-axis) | Recession probability from real data/proxy | "Is this decline due to macro?" |
| Price structure (Y-axis) | Drawdown · trend · breadth | "How broken is the tape?" |
| Oversold overlay | RSI · Bollinger · ATR | "Room for a short-term bounce?" |
| 5-State classification | Priority tree | The same -10% has a different character |
| Handoff | AMQS / ARDS | Not standalone trading but a "strategy switch" |

## Cross-Validation with the Code Edition

Compare this prompt's LLM output against the measured output of `quant/run.py`. Because the code computes the macro axis (especially the yield curve · credit) precisely from real data, trust the code values whenever the LLM estimate diverges.

---

**Author**: HoKwang Kim (Dennis Kim) · Betalabs Inc. · ORCID [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175) · MIT License

> *"Even the same red — the red of a correction and the red of a recession are not the same. ARDS-X is the barometer that reads that color."*
