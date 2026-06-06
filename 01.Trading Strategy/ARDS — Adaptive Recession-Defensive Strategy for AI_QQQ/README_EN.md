# ARDS-X — Regime Classifier (Correction · Oversold · Downtrend · Recession)

> *"A decline has four faces — a healthy correction, a short-term oversold dip, a structural downtrend, and a recession. They all look red, but the prescriptions are opposite."*

**Series**: vibe-investing — real-data eXtension of [ARDS](../ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/)
**Author**: HoKwang (Dennis) Kim · Betalabs Inc. · ORCID [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
**Date**: 2026-06-06 · **Version**: v1.1 · **License**: MIT

> **v1.1 changes**: ① **Rate Stress axis** + decline-type label (recession / rate / valuation-driven) — distinguishes "macro composite is low, so why is it falling? (a rate shock)" and conditionally gates ARDS Tier-2 TLT/IEF hedging. ② **Hysteresis** (entry/exit bands + N-day confirmation) to stop regime ping-pong/whipsaw. ③ **Confidence calibration (Brier)** added to the backtest. See §5.5.

---

## 1. TL;DR

ARDS-X automatically classifies whether **US Big-Tech + AI/Infrastructure and the S&P 500 / Nasdaq-100 are currently in a *Correction*, a *short-term Oversold* dip, a *structural Downtrend*, or a *Recession-driven rebalancing*** — using **real free data**.

- **ARDS (original)** had an LLM *estimate* the 5-Factor Recession Composite and produce synthetic backtests.
- **ARDS-X computes the same 5-Factor from real data** (FRED free CSV + yfinance) and adds a **price-structure axis** (drawdown / trend / oversold) to form a **two-axis regime map**.
- Output is one of 5 states, each with an **action and a hand-off to the sibling strategy** (AMQS for momentum, ARDS for defense).

```
quant/run.py  →  dashboard/data/latest.json  →  dashboard/index.html
```

---

## 2. Why — the "correction vs downtrend vs recession" trap

The most common investor error is misreading the *character* of a decline. The same −10% is a *correction* when the macro is healthy and the *start of a recession* when the macro is breaking down. **Price alone cannot tell them apart** — so ARDS-X reads the macro axis and the price axis together.

---

## 3. Two-Axis Regime Map

- **X = Macro recession axis**: ARDS 5-Factor Recession Composite (0–100). *"Is this decline macro-driven?"*
- **Y = Price-stress axis**: drawdown depth + trend breakdown (0–100). *"How broken is the tape?"*
- **Overlay = Oversold**: RSI(14), Bollinger %B, ATR stretch below the 20-DMA. *"Is a bounce likely short-term?"*

---

## 4. Classification (5 states, priority order)

| # | State | Trigger | Action | Hand-off |
|---|---|---|---|---|
| 1 | **RECESSION_REBALANCE** | Macro ≥ 55 **AND** (index DD ≤ −5% **or** trend broken) | Defensive / capital preservation | **→ ARDS / ARDS-Defense** |
| 2 | **DOWNTREND_DISTRIBUTION** | Trend broken **AND** DD ≤ −12%, macro still < 55 | Cut risk, no dip-buying | (escalates to recession if macro > 55) |
| 3 | **OVERSOLD_BOUNCE** | High oversold score **AND** trend mostly intact | Tactical small dip-buy + tight stop | **→ AMQS DIP_BUY** |
| 4 | **CORRECTION** | DD −5%…−12%, trend intact, macro benign | Hold + scale into quality | (→ ③ when RSI hits oversold) |
| 5 | **UPTREND_HEALTHY** | DD < −5%, above 200-DMA, macro benign | Risk-on | **→ AMQS momentum** |

> **Design philosophy**: ARDS-X does not trade on its own. It is the **switch** that decides *which playbook* to open — momentum (AMQS) for corrections/oversold, defense (ARDS) for recession.

### 4.1 Rate Stress axis + decline-type label (v1.1)

Two axes (macro recession × price stress) can't explain *"the macro composite is low, so why is it falling?"* — a **rate shock** is that blind spot. A **Rate Stress sub-composite** labels the *cause* of a decline.

**Rate Stress (0–100)** = `0.35·R1 + 0.25·R2 + 0.20·R3 + 0.20·R4`
(R1 10Y yield 20-day change in bp · R2 2Y/5Y change · R3 5Y breakeven change · R4 MOVE / realized 10Y vol)

| Label | Condition | TLT/IEF prescription |
|---|---|---|
| **RECESSION_DRIVEN** | Macro ≥ 55 | TLT/IEF duration = **hedge** (rate-cut beneficiary). Activate ARDS Tier-2 long bonds |
| **RATE_DRIVEN** | Rate Stress ≥ 55, macro < 55 | ⚠️ TLT/IEF = **added exposure** (falls with equities). Cut long bonds → short bills (BIL/SHV) / gold (GLD) |
| **VALUATION_DRIVEN** | both below | multiple compression / crowding unwind. TLT hedge limited; cash / inverse (SH/PSQ) fits |

> Same dichotomy as ARDS's *"disinflation vs sticky-inflation recession"* debate. In the backtest, **rate-driven declines returned −7.3% over the next 60 days** — isolating the real danger the recession axis misses (§5.5d).

### 4.2 Hysteresis (whipsaw guard, v1.1)

- **Split entry/exit bands**: e.g. oversold *enters* at RSI 30, *exits* at 38 — kills 30–38 ping-pong. Same for drawdown and macro recession.
- **N-day confirmation**: a new raw regime must persist **2 trading days** before the official (committed) regime switches; until then it shows `pending` and confidence is lowered.

Backtest: regime switches fell from **249 → 88 (−65%)** (§5.5c).

---

## 5. 5-Factor Recession Composite — real-data edition

Same weights as ARDS, computed from data:

| Factor | Weight | Primary (live) | Fallback (market proxy) |
|---|---|---|---|
| A. Yield Curve | 30% | FRED `T10Y3M`, `T10Y2Y` | yfinance `^TNX−^IRX`, `^TNX−^FVX` |
| B. Sahm Rule | 25% | FRED `UNRATE` | — (FRED-only) |
| C. ISM proxy | 15% | `CPER/GLD` + `XLI/SPY` relative strength | (always market proxy) |
| D. LEI proxy | 15% | FRED `ICSA` + `PERMIT` | — (FRED-only) |
| E. Credit/Financial | 15% | FRED `BAMLH0A0HYM2` + `NFCI` | yfinance `HYG/IEF` + HYG drawdown |

Missing factors are dropped and the remaining weights renormalized. The dashboard labels each factor `live` / `proxy` / `missing` and lowers confidence when ≥2 are missing. **It never silently fabricates numbers.** Because Yield Curve (30%) + Credit (15%) = 45% can be computed from yfinance alone, the system keeps working even when FRED is down.

---

## 5.5 Backtest (2014–2026, 2,914 ^NDX trading days)

`quant/backtest.py` reconstructs the regime call ARDS-X would have made on each past day **without look-ahead**, then checks it against *forward returns*. (The macro axis uses market proxies only — no historical FRED — so it is less precise than the live engine.)

### (a) Forward returns by state — thesis: correction/oversold positive, downtrend/recession negative

| State | % of time | Fwd 20d | Fwd 60d | 60d hit | Verdict |
|---|---|---|---|---|---|
| Uptrend healthy | 65.4% | +1.06% | +2.96% | 70.8% | ✅ |
| **Correction** | 13.0% | +2.48% | **+5.32%** | 74.9% | ✅ dip was buyable |
| **Oversold bounce** | 1.1% | +0.67% | **+6.45%** | 87.9% | ✅ bounce worked |
| **Downtrend / distribution** | 5.0% | +0.12% | **−1.52%** | 49.0% | ✅ caution justified |
| Recession rebalance | 15.5% | +3.01% | **+10.92%** | 85.8% | ⚠️ **inverted (proxy BEAR_TRAP)** |

> **Honest key finding**: correction/oversold/downtrend worked as designed, but `RECESSION_REBALANCE` had the *best* forward returns (+11%) — the proxy-only macro axis **over-fired on recession through the 2022–24 inversion (BEAR_TRAP)**. This is why the live engine relies on FRED Sahm/LEI — and the new **(d) rate-driven label directly compensates** for it.

### (b) Regime-switch overlay vs Buy & Hold (^NDX, hysteresis applied)

risk-on{uptrend, correction, oversold} = long NDX, defensive{downtrend, recession} = cash:

| | Total | CAGR | Vol | Sharpe | MDD | Time in market |
|---|---|---|---|---|---|---|
| Buy & Hold | +594.5% | 18.3% | 22.0% | 0.87 | −35.6% | 100% |
| **ARDS-X switch** | +200.0% | 10.0% | 15.5% | 0.69 | **−30.5%** | 79% |

In a historic bull market the defensive overlay trades return for lower drawdown/vol ("defense is a tax"). ARDS-X is a *regime switch*, not a standalone alpha engine — read this as the *cost of defense*.

### (c) Hysteresis — whipsaw (regime switches) cut

| | Regime switches |
|---|---|
| No bands / confirmation | 249 |
| **Hysteresis applied** | **88 (−65%)** |

### (d) Decline-type label — the rate-driven label isolates the real danger ★

| Decline type | days | Fwd 20d | Fwd 60d |
|---|---|---|---|
| RECESSION_DRIVEN | 301 | +3.70% | +11.46% (proxy BEAR_TRAP) |
| **RATE_DRIVEN** | 81 | **−1.84%** | **−7.27%** |
| VALUATION_DRIVEN | 312 | +1.98% | +5.11% |

> **The headline win of this update**: the danger the recession axis misses through over-firing is **precisely isolated by the rate-driven label at −7.3% over 60 days**. In that subset TLT is an added loss source, not a hedge — the basis for conditional Tier-2 gating.

### (e) Confidence calibration (Brier = 0.281)

Is "confidence X%" actually right X% of the time? (Correct = risk-on → fwd20 up, defensive → down.)

| Confidence bin | n | Predicted | Actual |
|---|---|---|---|
| 50–60% | 315 | 57.6% | 44.8% |
| 60–70% | 538 | 62.7% | **59.9%** ✅ |
| 70–80% | 237 | 77.6% | 68.8% |
| 80–95% | 1804 | 86.9% | **61.0%** ⚠️ overconfident |

> **Honest result**: the 60–70% bin is well calibrated, but the **top bin (80%+) is overconfident** (86.9% predicted vs 61.0% actual) — a recalibration to-do, and itself an SSRN-paper-sized research track.

Run: `python backtest.py` → `backtest_state_stats.csv` · `backtest_equity.csv` · `backtest_calibration.csv` · `backtest_decline_types.csv`.

Run: `python backtest.py` → `backtest_state_stats.csv`, `backtest_equity.csv`.

---

## 6. Universe

Indices: `^GSPC`, `^NDX`. Big-Tech: AAPL MSFT GOOGL AMZN META NVDA TSLA. AI semis: AVGO AMD TSM MU ASML. AI infra: VRT SMCI ANET DELL ORCL CEG. Macro proxies: `^TNX ^IRX ^FVX HYG LQD IEF CPER GLD XLI SPY`.

---

## 7. Usage

```bash
cd quant
pip install -r requirements.txt
python run.py                 # → ../dashboard/data/latest.json

cd ../dashboard
python3 serve.py 3142         # http://localhost:3142
```

All data is free (yfinance + FRED free CSV, **no API key**). Offline runs fall back to `quant/data/cache/`.

---

## 8. Limitations

Regime classification is built on lagging/coincident indicators — it does not predict turning points and can lag in fast markets. Thresholds (55, −12%, etc.) are heuristics tunable in `config.py`. Market proxies are not the real ISM / HY-OAS; warm the FRED cache when it is reachable. Beware bear-traps (the 2022–23 inversion preceded an 18-month no-landing). Educational/research use only — not investment advice.

---

> *"In a bull market, defense is a tax. In a bear market, defense is oxygen. ARDS-X is the barometer that tells you which one the air is."*

**License**: MIT · **Last updated**: 2026-06-06
