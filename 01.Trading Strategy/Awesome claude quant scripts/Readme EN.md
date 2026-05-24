# Awesome Claude Quant Scripts

> **A collection of quant prompts + code that analyzes US equity & crypto markets by cross-validating across multiple LLMs (Claude · ChatGPT · Gemini · DeepSeek)**

 [한국어](./Readme.MD) · **English** (current document)

→ [Parent folder README](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/README.md)
→ [Main repo README](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)

---

## Core Philosophy — Multi-LLM Cross-Validation

Every strategy in this folder is more than a "prompt collection." The core is a **cross-validation methodology: feeding one identical prompt to different LLMs and analyzing the divergence in their outputs.**

The foundational premises of my prompt strategy are:

1. **A single LLM cannot be the sole basis of trust.** Given the same prompt and same data, Claude · ChatGPT · Gemini · DeepSeek produce different tickers, different weights, and even diametrically opposed buy/sell positions. Relying on one model means inheriting that model's hallucinations, score inflation, and training-data bias.

2. **The "consensus" and "divergence" between models is itself a signal.** A ticker that several models unanimously agree on is a strong signal; a ticker they disagree on is exactly where a human must verify against primary sources. *"One LLM may hallucinate. Three LLMs converge on truth — but only when they disagree do you find the alpha."*

3. **Humans apply the final cap on quantitative decisions.** Models converge well on qualitative domains (regime classification, macro diagnosis), but diverge extremely on quantitative weight construction — "so what should I buy and how much?" Multi-LLM voting (median) or a human's conservative cap is therefore mandatory.

4. **Each model has a distinct "character" (investment philosophy).** Claude is discipline-based, audit-ready, and conservative; DeepSeek (born from a Chinese HFT hedge fund) pursues aggressive alpha; ChatGPT is fast at outlines and structuring; Gemini is compact and strong at contrarian picks. Together they operate like the investment committee of a multi-PM hedge fund.

This methodology mirrors the same pattern I use to publish CTI (Cyber Threat Intelligence) reports across four languages — Korean, English, Chinese, and Japanese.

---

## Strategies (most recently updated first)

> Dates reflect each strategy's last-modified / authored date.

| Updated | Strategy | Category | LLM Cross-Validation | Key Idea |
| --- | --- | --- | --- | --- |
| 2026-05-24 | [Midterm Signal](#1-midterm-signal) | Macro · Timing | Web-search based | Fact-checking the midterm-year dip-buying adage with backtests |
| 2026-05-21 | [AI Super Cycle Weekly Rebalance](#2-ai-super-cycle-weekly-rebalance) | AI · High-risk trading | **3-LLM** | Dynamic NVDA weight high risk |
| 2026-05-18 | [ARDS — Adaptive Recession-Defensive Strategy](#latest-research--ards--adaptive-recession-defensive-strategy) | Defensive · Academic | **4-LLM** | Recession defense + multi-agent hypothesis |
| 2026-05-04 | [Pharma Sector Long/Short](#3-pharma-sector-longshort) | Sector (Pharma/Bio) | **4-LLM** | Pharma mega-cap long/short, polarized-ticker discovery |
| 2026-05-02 | [AI Supercycle Investment](#4-ai-supercycle-investment) | AI · Tech | Multilingual bundle | 4-Layer AI value chain, 3 languages + CSV + screener |
| 2026-05-02 | [Dividend Growth Prompt](#5-dividend-growth-prompt) | Dividend | **3-LLM** | Dividend-growth discovery + "AI makes mistakes too" |
| 2026-05-02 | [Dual-Engine Capital Compounder](#6-dual-engine-capital-compounder) | Dividend · Capital return | Multilingual bundle | Financial + Retail 2-engine, TCRY signal |
| 2026-04-27 | [AI Supply Chain Bayesian Analysis](#7-ai-supply-chain-bayesian-analysis) | Research · Quant | Reproducibility prompt | Bayesian multi-factor short-term upside probability |
| 2026-04-27 | [DAT Quant Strategy](#8-dat-quant-strategy) | Trading (mean-reversion) | Python+Kotlin | DAT-firm ↔ crypto Z-Score pairs |
| 2026-04-27 | [Long-Term Dividend Investing](#9-long-term-dividend-investing) | Dividend | Code implementation | Long-hold dividend screener code |
| 2025-04-26 | [Declining Stock Quant Script](#10-declining-stock-quant-script) | Short · Bearish | LLM prompt | Decline-candidates + inverse positions |
| (WIP) | [REGIME](#11-regime--the-honest-quant) | Macro · Research | A/B/C approaches | "Honest quant" — macro can't explain stock picks |
| - | [Sample](#sample--new-strategy-template) | Template | - | Standard structure for new strategies |

---

## Groups by Industry & Strategy Type

Strategies grouped by **what you buy (industry)** and **how you approach it (type)**.

### AI · Semiconductors · Tech
Covers the core beneficiaries of the AI super cycle.
- [AI Supercycle Investment](#4-ai-supercycle-investment) — 4-Layer AI value chain diversification
- [AI Super Cycle Weekly Rebalance](#2-ai-super-cycle-weekly-rebalance) — dynamic NVDA weight (high risk)
- [AI Supply Chain Bayesian Analysis](#7-ai-supply-chain-bayesian-analysis) — supply-chain short-term upside probability

### Dividend · Capital Return · Income
Pursues compounding through dividend growth and buybacks.
- [Dividend Growth Prompt](#5-dividend-growth-prompt) — 6-sector dividend growth
- [Dual-Engine Capital Compounder](#6-dual-engine-capital-compounder) — Financial + Retail capital return
- [Long-Term Dividend Investing](#9-long-term-dividend-investing) — long-hold code

### Sector-Specific (Healthcare etc.)
Reflects industry-specific dynamics (pipeline, clinical data, LOE).
- [Pharma Sector Long/Short](#3-pharma-sector-longshort) — pharma/bio long/short

### Crypto · Digital Assets
Exploits mean-reversion in BTC/ETH-holding companies.
- [DAT Quant Strategy](#8-dat-quant-strategy) — DAT-firm Z-Score pairs ( not recommended)

### Short · Drawdown Defense
Handles defense and short positions in bear/correction markets.
- [Declining Stock Quant Script](#10-declining-stock-quant-script) — decline candidates + inverse
- [ARDS](#latest-research--ards--adaptive-recession-defensive-strategy) — recession-defensive portfolio

### Macro · Regime · Timing
Handles whole-market regime judgment and entry timing.
- [Midterm Signal](#1-midterm-signal) — midterm-election buy signal
- [REGIME](#11-regime--the-honest-quant) — macro regime analysis

---

## Latest Research — ARDS — Adaptive Recession-Defensive Strategy

**Updated: 2026-05-18 · The definitive 4-LLM cross-validation study**

→ [Go to full ARDS document](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/readme.md)

ARDS is a *dynamic defensive portfolio strategy pursuing asymmetric alpha at the onset of a recession.* It is the latest research that distills this collection's entire multi-LLM cross-validation methodology to an academic level, designed as the symmetric hedge (counter-strategy) to AMQS-M7 (a momentum strategy).

**Why this research matters:** ARDS goes beyond a simple defensive strategy to empirically test, via 4-LLM cross-validation, the hypothesis that *"the future quant system is likely not a single super-intelligent AI, but a committee of AIs with different investment philosophies."*

Key findings:

- **Macro diagnosis converges, execution diverges.** All four models diagnosed the identical "Phase 3 Recession-Warning" regime (std dev 2.29%p), but on "what to buy and how much," total weights ranged from 85% (Claude) to 225% (DeepSeek) — a **14x divergence gap.**
- **Only one unanimous ticker: GLD (gold).** Of 25 tickers, the only one all four models agreed on was gold — reflecting a consistent recognition of gold as "insurance against macro-regime instability."
- **Per-model character resembles a hedge fund investment committee.** Claude (discipline-based PM) · Gemini (Cash-is-King risk officer) · ChatGPT (Quant Overlay strategist) · DeepSeek (aggressive alpha hunter) operated strikingly like the role division of a real multi-PM hedge fund (Millennium, Citadel, etc.).

This research is the methodological endpoint that every individual strategy in this collection aims toward.

---

## Detailed Strategy Descriptions

### 1. Midterm Signal
**2026-05-24 · Macro · Timing**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Midterm%20signal)

A tool that uses an LLM prompt to check, and a self-run backtest to fact-check, the old investing adage "buy the dip in a US midterm-election year" (Kostolany's *fait accompli* psychology).

Highlights:

- Backtested 22 midterm elections from 1938–2022, revealing that the commonly cited "+36% one year later" claim assumes buying the exact bottom; the realistic expectation is about +19%.
- The 95.5% win rate is real, but honestly notes it breaks during structural crises like 1939 (depression/war), and that the midterm effect is itself statistically insignificant.
- Scores the current market against a 6-signal checklist — as of May 2026, it judges a "do not buy (2/6)" zone. *A prompt engineered to use only falsifiable evidence, no exaggeration.*

### 2. AI Super Cycle Weekly Rebalance
**2026-05-21 · AI · High-risk trading · 3-LLM cross-validation**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Ai%20super%20cycle%20weekly%20rebalance%20prompt)

> **High-risk warning**: An ultra-concentrated active strategy placing 25–44% in a single ticker (NVDA). It is likely to earn less than simply holding NVDA long-term (conservative scenario +38.5% vs NVDA +68.5%); its value is "breaking less in a downturn," not "earning more."

A strategy that dynamically adjusts NVDA's weight by phase, based on the 3-year GPU-demand reinvestment cycle.

Highlights:

- **A cross-validation report feeding one identical prompt to Claude, ChatGPT, and DeepSeek.** The phase call (qualitative) was a unanimous ACCEL, but NVDA target weights diverged by 9%p (35%–44%).
- Analyzes three divergence causes (STRESS-cap interpretation, ASP-adjustment sign, unallocated-balance interpretation) — *strong evidence that quantitative decisions must not be delegated to a single LLM.*
- Practical recommendation: 3-LLM median + a human's conservative cap (35%).

### 3. Pharma Sector Long/Short
**2026-05-04 · Sector (Pharma/Bio) · 4-LLM cross-validation**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Pharma%20sector%20prompt)

A prompt that constructs a 12–24 month horizon long/short portfolio across US pharma mega-caps.

Highlights:

- **Four models (ChatGPT·Claude·DeepSeek·Gemini) produced four different portfolios from one prompt.** On more than half of the mega-caps (BMY·AMGN·GILD·NVO·MRK), positions flipped entirely between models — proving single-model reliance is a "per-model roulette game."
- Per-model character analysis: Claude (Korean audit-ready + direct 8-K citations + contrarian), DeepSeek (English institutional format + rich M&A info), ChatGPT (fast outline + stale data), Gemini (compact + sole MDGL discovery + sole MRK short).
- Demonstrates that web-search usage determines data accuracy (Claude·DeepSeek reflected Q1 2026 earnings; ChatGPT·Gemini used stale data).

### 4. AI Supercycle Investment
**2026-05-02 · AI · Tech · Multilingual bundle**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20Supercycle%20Investment%20Quant%20Strategy)

A US-equity quant strategy for riding the AI super cycle. A complete bundle of **3-language (Korean/English/Chinese) LLM prompts + 3 recommended-portfolio CSVs + a Python screener (yfinance-based).**

Highlights:

- Diversifies the AI value chain into 4 layers (Foundation semis → Infra hyperscalers → Enablers power/networking → Application) to recommend 10 tickers.
- Scoring: AI revenue exposure (35%) + capital efficiency & momentum (30%) + GARP valuation (20%) + momentum & flows (15%).
- A "picks and shovels matter more than the gold" philosophy — centered on infrastructure names like NVDA·TSM·AVGO.

### 5. Dividend Growth Prompt
**2026-05-02 · Dividend · 3-LLM cross-validation**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dividend%20growth%20prompt)

A prompt to discover S&P 500 + NASDAQ-100 dividend-growth names — and an **empirical case showing that "AI makes mistakes too."**

Highlights:

- Empirically compares Claude·Gemini·DeepSeek outputs. From the same prompt, only 2 tickers (MSFT·UNH) were agreed on by all three.
- Explicitly corrects each model's errors: Gemini's 3 sector misclassifications (LOW·JPM·COP), DeepSeek's sector violation (LIN) and energy omission, Gemini's score inflation (avg 90), DeepSeek's "too good to be true" Sharpe of 1.45.
- Claude showed the most audit-ready output (Grade-A sector compliance, conservative Sharpe 0.82, explicit risk-free rate) but with a 4x token-cost trade-off.

### 6. Dual-Engine Capital Compounder
**2026-05-02 · Dividend · Capital return · Multilingual bundle**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dual-Engine%20Capital%20Compounder%20Quant%20Strategy%20Using%20LLM)

A 2-engine quant system that simultaneously discovers US Financial (cards·banks·asset mgmt) and Retail dividend stocks. A bundle of 3-language prompts + CSV + Python screener.

Highlights:

- **TCRY (Total Capital Return Yield) as the core signal** — measures the "true compounding of capital return" by adding buybacks, not just dividend yield.
- Financial Engine 5 (V·JPM·BLK·AXP·CB) + Retail Engine 5 (HD·TJX·WMT·MCD·TGT).
- Adds a cycle-defense score (15%) for recession scenarios — reflecting 2008 GFC dividend cuts (BAC -90%, C -97%) in the risk disclosures.

### 7. AI Supply Chain Bayesian Analysis
**2026-04-27 · Research · Quant · Reproducibility prompt**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20supply%20chain%20bayesian%20analysis)

An LLM-based quant tool that analyzes the short-term (5–20 trading days) upside probability of AI supply-chain stocks via a **Bayesian multi-factor prompt.**

Highlights:

- A Bayesian thinking frame: set macro context (rates·VIX·AI Capex) as the prior, then update the posterior downside probability via a likelihood ratio (LR).
- 5 layers (GPU/AI accelerators → HBM/memory → datacenter networking → storage → NPU/on-device) × 3 factors (technical 30% + fundamental/macro 30% + flows/sentiment/macro 40%).
- Emphasizes reproducibility — structural consistency (named tickers, fixed weights, enforced format, explicit formula) lets you *"regenerate a same-format report from the same prompt."* Scores are used only as relative rankings, never absolute values.

### 8. DAT Quant Strategy
**2026-04-27 · Trading (mean-reversion) · Python+Kotlin**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/DAT%20quant%20strategy)

> **Honest advice**: If you want Bitcoin exposure, **buying Bitcoin directly is better** than playing mean-reversion on DAT firms like MSTR. DAT firms add equity-specific risk (dilution, debt, management decisions), and a regime change (Spot BTC ETF, GENIUS Act) can void the historical premium pattern. This strategy is *only for identifying entry timing for someone who has already decided to hold a DAT firm.*

A Z-Score pair-trading signal script exploiting mean-reversion between a DAT (Digital Asset Treasury) firm's stock price and its held crypto price.

Highlights:

- 90-day Rolling Z-Score across 7 pairs (MSTR·MARA·RIOT·GLXY·COIN·BMNR·SBET) (Z≤-2 buy, Z≥+2 sell, look-ahead-bias prevented).
- **Dual Python + Kotlin implementation** — a Kotlin version for 365-day uptime fintech backends (JVM).
- MSTR-BTC pair correlation r≈0.87. But as warned above, mean-reversion assumes correlation persistence and may be void under structural premium compression.

### 9. Long-Term Dividend Investing
**2026-04-27 · Dividend · Code implementation**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Long-Term%20Dividend%20Investing)

A stock-selection script for long-term dividend investing. It evaluates dividend growth, sustainability, payout ratio, and financial health — not just dividend yield.

Highlights:

- A **code-implementation companion** to the (prompt-centric) Dividend Growth Prompt — for retirement funding, income portfolios, and Dividend Aristocrats candidate discovery.
- Uses payout ratio and financial health as core filters from a long-hold perspective.

### 10. Declining Stock Quant Script
**2025-04-26 v1.0 · Short · Bearish · LLM prompt**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Declining%20Stock%20Quant%20Script%20Using%20LLM)

A prompt where an LLM selects S&P 500 / NASDAQ-100 constituents likely to decline within 1–4 weeks, and also suggests the corresponding inverse (short) positions.

Highlights:

- Multi-factor model: technical (40%, overbought·death cross·head-and-shoulders) + fundamental (30%, high P/E·deteriorating FCF) + flows/sentiment (30%, insider selling·put-option surge·negative sentiment).
- Matches an inverse ETF to each decline candidate, while explicitly warning about **inverse-ETF volatility decay** — tracking-error accumulation from holding daily-rebalanced products beyond one day.

### 11. REGIME — The "Honest Quant"
**(WIP) · Macro · Research**
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/REGIME)

> **Note: still incomplete. Do not use this for investing without financial-engineering knowledge.**

A quant prompt + Python pipeline that **honestly** analyzes the relationship between macro variables (FX·rates·inflation·sentiment·oil) and the M7 + AI-infrastructure stocks.

Highlights:

- **Key finding: macro barely explains stocks** (weekly regression R² of 1–3%). Macro regimes tell you "when to be in the market (timing)" but not "which stock to pick (selection)." Stripping QQQ beta nearly eliminates regime-dependence of stock-specific alpha (significant names 3/17 → 1/17).
- Three approaches A/B/C (rule-based regime+momentum / regression fair-value / unsupervised regime+beta-neutral residual).
- The real value of this framework is *"honesty enforced by statistics"* — engineered so the LLM refuses to manufacture confident signals the data doesn't support.

### Sample — New Strategy Template
→ [Go to folder](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Sample)

A template folder with the standard structure (README, scripts, data, backtest, limitations) for starting a new strategy.

---

## Recommended Usage Order

1. First understand the **Multi-LLM Cross-Validation philosophy** in this README
2. Pick a strategy from the group matching your interest (AI / Dividend / Sector / Macro, etc.)
3. Read that strategy's folder README and its **Limitations & Risk disclosure** sections carefully
4. Feed the prompt to **at least two different LLMs** and cross-validate
5. Separate consensus tickers from divergence tickers
6. For divergence tickers, **verify directly against primary sources** (SEC EDGAR, Morningstar, etc.)
7. Reproduce backtest data → paper-trade → (only then) consider live trading

---

## Disclaimer

All scripts and prompts are **hypothetical simulations for research/education**, not investment advice.

- LLM-generated analyses, scores, and probabilities are estimates, not actual statistical-model outputs. Backtest results often exclude slippage, fees, and taxes (illustrative only).
- LLMs can exhibit hallucination, look-ahead bias, and survivorship bias, so you **must cross-validate against independent data sources.**
- Korea residents: foreign-stock capital gains tax 22% + foreign-exchange reporting obligations + separate comprehensive taxation review required.
- When using Chinese LLMs like DeepSeek, separately review geopolitical risk.
- All investment decisions and their consequences rest with you, after consulting a qualified professional.

See the [main README Disclaimer](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md#disclaimer) for details.

---

## Author

**Dennis Kim (HoKwang Kim / 김호광)**

- CEO, Betalabs Inc. · Independent Researcher
- Microsoft Azure MVP (Long-tenured) · Former CEO, Cyworld Z
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · Email: <gameworker@gmail.com>

**Interests**: Cyber Threat Intelligence · AI-Assisted Solo Entrepreneurship · Quant Finance · Cross-Lingual LLM Behavior · Multi-Agent AI Systems

---

> *"One LLM may hallucinate. Three LLMs converge on truth — but only when they disagree do you find the alpha."*

**Series**: vibe-investing — Awesome Claude Quant Scripts · **License**: MIT
