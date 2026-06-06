# ARDS-X — Regime Classifier (Correction · Oversold · Downtrend · Recession)

> *"A decline has four faces — a healthy correction, a short-term oversold dip, a structural downtrend, and a recession. They all look red, but the prescriptions are opposite."*

**Series**: vibe-investing — real-data eXtension of [ARDS](../ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/)
**Author**: HoKwang (Dennis) Kim · Betalabs Inc. · ORCID [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
**Date**: 2026-06-06 · **License**: MIT

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
| Uptrend healthy | 66.7% | +1.05% | +3.02% | 71.0% | ✅ |
| **Correction** | 12.4% | +2.19% | **+5.24%** | 77.5% | ✅ dip was buyable |
| **Oversold bounce** | 1.5% | +1.60% | **+5.64%** | 76.7% | ✅ bounce worked |
| **Downtrend / distribution** | 5.3% | +0.01% | **−0.37%** | 44.5% | ✅ caution justified |
| Recession rebalance | 14.2% | +3.54% | **+11.22%** | 87.4% | ⚠️ **inverted** |

> **Honest key finding**: correction / oversold / downtrend classifications worked as designed. But **`RECESSION_REBALANCE` had the *best* forward returns (+11%)** — because the proxy-only macro axis **over-fired on recession throughout the 2022–24 yield-curve inversion (a BEAR_TRAP)**. This is precisely why the live engine relies on FRED's Sahm Rule / LEI (real data) and lowers confidence when they are missing: distinguishing a true recession from an inversion-only "no-landing" requires labor and leading indicators.

### (b) Regime-switch overlay vs Buy & Hold (^NDX)

risk-on{uptrend, correction, oversold} = long NDX, defensive{downtrend, recession} = cash:

| | Total | CAGR | Vol | Sharpe | MDD | Time in market |
|---|---|---|---|---|---|---|
| Buy & Hold | +594.5% | 18.3% | 22.0% | 0.87 | −35.6% | 100% |
| **ARDS-X switch** | +190.5% | 9.7% | 15.6% | 0.67 | **−25.6%** | 80% |

2014–2026 was a historic bull market, so the defensive overlay traded return for a shallower drawdown (−35.6% → −25.6%) — exactly the "defense is a tax in a bull market" philosophy. ARDS-X is a *regime switch*, not a standalone alpha engine; treat this as the *cost of defense*, not a strategy return.

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
