# vibe investing

> **A repo for sharing opinions and resources on AI-powered Vibe Investing**

Covers a curated Awesome series for AI investing (Vibe Investing), 7 market-analysis columns, and 3 AI trading tools (Harness Quant v2 + Earnings Momentum Agent + Nasdaq-BTC Coupling Bot). Markets researched: US NASDAQ, S&P500, crypto, the European luxury sector, and crypto-equity correlation. AI is a tool, like Excel. LLMs are not all-knowing; the human insight that reads the model matters most. With the BTC-Nasdaq coupling signal currently strong, we can use AI as a tool to separate signal from noise.

Added on 2026-04-25: the LLM-powered Awesome Claude Quant Scripts now lets you build your own quant strategy.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with](https://img.shields.io/badge/Made%20with-Claude%20%2B%20Python-blue)](https://github.com/gameworkerkim/vibe-investing/blob/main)
[![Updates](https://img.shields.io/badge/Updates-Weekly-brightgreen)](https://github.com/gameworkerkim/vibe-investing/blob/main)
[![Awesome Lists](https://img.shields.io/badge/Awesome--Lists%20%C3%97%203-orange)](https://github.com/gameworkerkim/vibe-investing/blob/main)
[![Columns](https://img.shields.io/badge/Columns-7%20Published-purple)](https://github.com/gameworkerkim/vibe-investing/blob/main)
[![Tools](https://img.shields.io/badge/Tools-3%20Built-cyan)](https://github.com/gameworkerkim/vibe-investing/blob/main)
[![Datasets](https://img.shields.io/badge/Datasets-14%2B%20CSV-red)](https://github.com/gameworkerkim/vibe-investing/blob/main)

[한국어 README](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)

---

## Curation Map

The diagram below is the 8-strategy quant taxonomy organized by **Awesome Claude Quant Scripts**. The columns, tools, and datasets in this repo operate on top of this taxonomy — for example, the *Earnings Momentum Agent* is a Growth × Quality × Momentum multi-factor approach, the *Nasdaq-BTC Coupling Bot* is Statistical Arbitrage / Time-Series Momentum, and the *DAT mNAV column* is a variant of Value/Pair Trading.

[![Trading Strategy Taxonomy — Awesome Claude Quant Scripts](https://github.com/gameworkerkim/vibe-investing/raw/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/trading%20map.png)](/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/trading%20map.png)

> Four core factors (Value · Growth · Quality · Momentum) + four advanced strategies (Multi-Factor · Trend Following · Statistical Arbitrage · Machine Learning). For each strategy's primary academic/industry sources, Python code skeletons, and Claude prompt templates, see [Awesome Claude Quant Scripts](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD).

---

## Quick Links

### 📖 Awesome Curation Series

| # | Title | Coverage |
| --- | --- | --- |
| 1 | [**Awesome Vibe Invest — Stocks & Equities**](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest.MD) | Stocks (NASDAQ / S&P500) — evaluation of 30+ AI investing GitHub repos |
| 2 | [**Awesome Vibe Invest — Crypto & DeFi Edition**](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest%20crypto.MD) | Bitcoin / crypto — benchmark-centric LLM trading curation |
| 3 | [**Awesome Claude Quant Scripts**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD) 🆕 | 8 quant strategies — 30+ primary academic papers + Claude prompts + Python skeletons |

### 📰 Column Series

| # | Title | Topic |
| --- | --- | --- |
| 1 | [**Reading the model: lessons from LTCM**](https://github.com/gameworkerkim/vibe-investing/blob/main/Vibe%20Investing%20Risk%20Management.MD) | The 1998 LTCM collapse + the risks of 2026 AI vibe investing |
| 2 | [**Microsoft's Fintool acquisition — the day Excel becomes Bloomberg**](https://github.com/gameworkerkim/vibe-investing/blob/main/Microsoft%20fintool%20acquisition%20column.MD) | Synergy analysis of Microsoft's Fintool acquisition |
| 3 | [**Invisible hand, or planned fraud?**](https://github.com/gameworkerkim/vibe-investing/blob/main/Crypto%20perp%20manipulation%20column.MD) | A mathematical review of abnormal pump-and-dump patterns in crypto perpetual futures |
| 4 | [**Does the market open when it closes?**](https://github.com/gameworkerkim/vibe-investing/blob/main/AfterMarketClose/After_Market_Close_Column.md) | Why 91.2% of US-listed firms disclose bad news after market close — 34 empirical cases |
| 5 | [**The mNAV arbitrage strategy of DAT firms**](https://github.com/gameworkerkim/vibe-investing/blob/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage/Dat%20mnav%20arbitrage%20strategy.MD) | The crypto value-vs-market-cap gap in digital-asset treasury firms like MSTR and BMNR |
| 6 | [**When should you buy luxury?**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md) | LVMH · Hermès · Kering — a 3-tier luxury investing strategy for the China-slowdown era |
| 7 | [**How synchronized are crypto and Nasdaq?**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/Nasdaq%20crypto%20coupling%20strategy.MD) | 6-year BTC-QQQ correlation + 6-regime classification + intraday lag measurement |

### 🛠️ Tools Under Active Development

| # | Title | Description |
| --- | --- | --- |
| 1 | [**Harness Quant v2**](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quant%20v2%20readme%20.MD) | LLM-based NASDAQ/S&P500 analysis package (6 scenarios + backtest + MCP + multi-agent debate) |
| 2 | [**Earnings Momentum Agent**](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quantv2/Earnings%20momentum%20agent%20readme%20.MD) | Top 30 recommendation pipeline combining bottom rebound + revenue growth + earnings surprise + market sentiment (24-month backtest, hit rate 83.3%) |
| 3 | [**Nasdaq-BTC Coupling Bot**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) | Real-time BTC-QQQ 30-day rolling correlation tracking + 6-regime classification + trading signal generation (547 lines, 10 classes) |



---

## What is Vibe Investing?

If **Vibe Coding** is the paradigm of instructing an LLM in natural language to write code,
**Vibe Investing** is the **agentic pipeline** that goes from a natural-language instruction → the LLM calling tools → collecting and analyzing market data, news, and social signals → producing an investment decision.

Where traditional algorithmic trading is rigid, rule-based ("if RSI < 30 then buy"), vibe investing offers:

* **Strategy defined in natural language** ("find stocks in improving sectors that the market is praising")
* **The LLM actively calls tools** (price, fundamentals, news, social, insider trades, on-chain data)
* **Layered reasoning and consensus** (Bull/Bear/Risk/PM multi-agent debate)
* **Decisions structured as JSON** (a human-auditable reasoning trail)

This repo **maps the current landscape of vibe-investing tools and solutions**, publishes **columns that analyze market trends**, and shares **reference implementations I'm building myself**.

---

## What's in this repo?

### 1. Awesome Vibe Invest — Stocks & Equities

[**📖 Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest.MD)

A curation of 30+ AI tools for analyzing NASDAQ / S&P500, across 12 categories (multi-agent frameworks, RL trading, financial LLMs, backtest engines, MCP infrastructure, Korea-market resources, common pitfalls, and more).

**Key differentiators**:

* ⭐ Not a plain list, but **objective evaluation (strengths + weaknesses + best-fit users)**
* 📊 Five-axis scoring on activity, maturity, learning curve, Korea-market fit, and license
* 🇰🇷 **Separate section for Korea/Asia market resources** (pyKRX, Korea Investment & Securities OpenAPI, etc.)
* ⚠️ **12 common pitfalls** (backtest · LLM hallucination · operations · governance · cost)
* 🎯 **5 starting paths by user type**

### 2. Awesome Vibe Invest — Crypto & DeFi Edition

[**📖 Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest%20crypto.MD)

A curation of LLM trading for crypto including Bitcoin, centered on projects with **benchmark results** and **continuous updates**.

**The most important data — Alpha Arena Season 1 results**:

* 🥇 **DeepSeek V3.1**: +46% (real capital $10,000 → $14,764)
* 🥈 Qwen3 Max
* 🥉 Claude Sonnet 4.5
* 🥉 Grok 4
* ❌ Gemini 2.5 Pro
* ❌ **GPT-5**: -75%

→ The first live-trading benchmark to demonstrate that **model IQ is not trading IQ**.

**The 9 categories covered**:

```
1. Benchmark & evaluation infrastructure (Nof1 Alpha Arena, etc. — most important)
2. Academically validated LLM trading (CryptoTrade EMNLP 2024, FS-ReasoningAgent, etc.)
3. Production multi-agent bots (CloddsBot, qrak/LLM_trader, etc.)
4. Solana-native AI agents (ElizaOS 17.6k+ stars, Solana Agent Kit, GOAT, Rig)
5. Multichain / EVM agent toolkits
6. MEV / DEX-specific bots (Jito mev-bot, etc.)
7. Prediction-market (Polymarket / Kalshi) AI agents
8. Data infrastructure & on-chain analytics
9. Common pitfalls (crypto-specific) — 24/7 markets, slippage, MEV, CEX risk, etc.
```

### 3. Awesome Claude Quant Scripts — Quant Strategy + Claude Prompt Curation 🆕

[**📖 Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD)

> *"Code generated by Claude must always be verified by a human.*
> *If you cannot verify it yourself, cross-validate with another LLM to filter hallucinations."*

**A comprehensive reference binding 8 quant strategies across three layers: primary academic sources → Python code skeletons → Claude prompt templates.** If Vibe Investing curates *which tools to use*, this Awesome list curates *which strategy to run on which theoretical foundation*.

**3-layer structure**:

| Layer | Content |
| --- | --- |
| **Theory** | Primary papers and books on repeatedly validated factors/strategies from academia and industry |
| **Implementation** | The minimal Python code skeleton needed to run each strategy |
| **AI collaboration (Claude)** | Reusable Claude prompt templates that summon a strategy in one line |

**The 8 strategies covered**:

```
Core Factor Strategies
├── Value      — Graham, Fama-French, Greenblatt
├── Growth     — Fisher, Lynch, O'Neil (CAN SLIM)
├── Quality    — Novy-Marx, AQR (Quality Minus Junk)
└── Momentum   — Jegadeesh-Titman, Carhart, Moskowitz

Advanced Strategies
├── Multi-Factor          — Fama-French 5-factor, AQR multi-factor
├── Trend Following       — Turtle Traders, Clenow, AQR "Century of Evidence"
├── Statistical Arbitrage — Gatev-Goetzmann-Rouwenhorst, Vidyamurthy, Thorp
└── Machine Learning      — López de Prado, Gu-Kelly-Xiu, Stefan Jansen
```

**Key differentiators**:

* 📚 **30+ primary academic sources** — citing first-rate sources like *Journal of Finance*, *RFS*, *JFE*, not guesswork
* 🎯 **4 outputs per strategy** — overview, key metrics, masters table, Claude prompt, Python skeleton
* 🧰 **5 general-purpose prompts (T1–T5)** — Strategy Stress-Test · Paper→Code · Risk Overlay · Crypto port · Live Paper Trading transition
* ⚠️ **Look-ahead, survivorship, and overfitting checklists** specified for every strategy
* 🔍 **Claude hallucination filtering recommended** — cross-validate with another LLM when you cannot verify directly

**Why this curation matters**:

Most quant logic follows a fixed design pattern — *universe → factor calculation → ranking → rebalancing → performance evaluation*. Claude generates this boilerplate quickly, but there's no need to re-explain from scratch **which factor rests on which paper and what pitfalls apply** each time. This Awesome list performs that *context compression* — paste it into Claude once and it immediately produces academically coherent backtest code.

**Example — invoking a Value-factor backtest**:

```
You are a quant analyst. Write Python code for a Value-factor backtest to the spec below.

[UNIVERSE]    : KOSPI200
[FACTORS]     : PBR, PER, EV/EBITDA (equal-weighted Z-score composite)
[FILTERS]     : market cap >= 100B KRW, exclude loss-making firms, exclude financials/holding cos
[REBALANCING] : quarterly, equal-weighted buy of the top 20%
[PERIOD]      : 2015-01-01 ~ today
[BENCHMARK]   : KOSPI200 total return index
...
- Annotate each step with look-ahead bias prevention notes
```

The document contains ready-to-use prompts in this same format for all 8 strategies.

### 4. Column: Reading the model — lessons from LTCM

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/Vibe%20Investing%20Risk%20Management.MD)

> *"The model always points to truth. The finger always points to greed."*

A column analyzing how LTCM — a hedge fund run by two Nobel laureates — was liquidated within four months in 1998, and applying that to the 2026 AI vibe-investing environment.

**What it covers**:

* 🏛️ The rise and fall of LTCM (capital of $4.7B → leverage exploding to 130:1)
* 🔄 *Functional homogenization* — systemic risk when everyone uses the same model
* 📊 April 2026 market indicators (Shiller CAPE 38, Buffett indicator 230%, IT-sector CAPE 64.5)
* ⚠️ Three ways AI vibe investing resembles LTCM
* 🛡️ Five practical principles

### 5. Column: Microsoft's Fintool acquisition — the day Excel becomes Bloomberg

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/Microsoft%20fintool%20acquisition%20column.MD)

> *"The terminal of the next 30 years will not be a terminal. It will be a spreadsheet cell that answers back."*

An analysis of Microsoft's acquisition of Fintool, a 6-person startup that raised $7.24M. It examines Microsoft's entry strategy into the $37B financial-data-terminal market (Bloomberg, FactSet, S&P Capital IQ) across six synergies and five risks.

**What it covers**:

* What Fintool was (Y Combinator, Menlo Ventures, Cassius)
* What Microsoft already had (Copilot for Finance, Finance Agents, Agent Mode)
* Six synergy vectors (Distribution × Depth, Excel native, cross-app continuity, etc.)
* Five risks (acqui-hire failure patterns, EU regulation, LLM hallucination liability, etc.)
* Market-impact analysis (mindshare shifts at Bloomberg, FactSet, S&P Capital IQ)

### 6. Column: Invisible hand, or planned fraud?

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/Crypto%20perp%20manipulation%20column.MD)

> *"Benford's law cannot lie. On-chain data lasts forever."*

A column analyzing the recurring "spike → liquidation cascade → round-trip" pattern in crypto perpetual-futures markets through **mathematical and statistical argument** and **on-chain forensics**. It names no specific token, foundation, or exchange, drawing conclusions purely by statistical induction — securing both legal safety and argumentative strength.

**What it covers**:

* 🔢 **VTCLR pattern definition** — five conditions: Vertical, Thin, Coordinated, Liquidation, Round-trip
* 📐 **Three mathematical results**: Benford's-law deviation (χ² test), 4+ wallet coincidental simultaneity probability = 2×10⁻⁸, microstructure OHLC divergence
* 🔍 **Three public incidents** — Hyperliquid XPL (Aug 2025, $46M+ attacker profit), Fartcoin (Apr 2025, 4-wallet coordination), the Oct 2025 $20B liquidation
* 🧠 **Bayesian 3-hypothesis analysis** — H₁ (natural market) rejected, H₂ (single whale) partly supported, H₃ (coordinated strategy) dominant
* ⚖️ **Four legally safe conclusions** — statistical, structural, policy, and investor-facing

### 7. Column: Does the market open when it closes?

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/AfterMarketClose/After_Market_Close_Column.md)

> *"All disclosures are equally important. But investor attention is not equally distributed."*

A column analyzing, with real data, how market-moving disclosures by US-listed firms cluster overwhelmingly **after market close (AMC)**. It collects and analyzes **34 actual disclosure cases from NASDAQ-100 firms** between COVID (2020) and 2025, combined with academic literature.

**Key findings**:

* 🔍 **91.2% of market-moving disclosures are released at AMC** (34-case sample)
* 📉 Average next-day price change after AMC disclosure: **-6.45%** (BMO disclosures: +1.15%)
* 🎯 AMC + Severe combination (n=14) next-day average: **-10.79%**
* ⚖️ Framed as a *"natural consequence of market structure"* to secure legal safety

**What it covers**:

* 🏛️ Three legitimate reasons for AMC disclosures (information processing time, Reg FD, exchange convention)
* 📊 Citing Watkins et al. 2023 (*The Accounting Review*, analysis of 49,652 8-Ks)
* 🇺🇸 Meta 2022-02-02 -26.4%, Netflix 2022-04-19 -35.1%, Intel 2024-08-02 -26.1%, etc.
* 🛡️ Five defensive strategies for retail and institutional investors
* 🇰🇷 The time-zone problem for Korean investors and how to respond

**Companion data**: [`disclosure_timing_cases.csv`](https://github.com/gameworkerkim/vibe-investing/blob/main/AfterMarketClose/) — 34 actual disclosure cases + price-move data

### 8. Column: The mNAV arbitrage strategy of DAT firms

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage/Dat%20mnav%20arbitrage%20strategy.MD)

> *"Strategy (MSTR) is a strange object. It borrowed $8B to buy $61B of Bitcoin. Yet the market valued it at $152B. So the question is — what is the extra $91B being paid for?"*
>
> — Jim Chanos, December 2024 (on disclosing his MSTR short)

A validation of the **mNAV (Market-to-Net-Asset-Value) arbitrage strategy among DAT (Digital Asset Treasury) firms** that hold Bitcoin, Ethereum, and Solana as core balance-sheet assets. It reconstructs the status of **15 DAT firms** including Strategy (MSTR), BitMine (BMNR), and SharpLink (SBET), plus **Jim Chanos's actual pair trade**.

**Key findings**:

* 📈 MSTR 2020-2026 cumulative return **+2,950% vs BTC +940%** (excess return +193%)
* ⚡ MSTR mNAV range: **0.7x (2022 trough) ~ 3.89x (2024-11 peak) → 1.20x (2026-04)**
* ⚠️ **The BMNR sub-NAV trap**: even after falling below 1x mNAV, it dropped another -50%, underperforming direct ETH holding by -43%p
* 🎯 **MSTR's scarcity premium is structurally dissolving** with the launch of spot BTC ETFs

**What it covers**:

* 🏢 Details on 15 DAT firms (8 BTC + 6 ETH + 2 SOL, $84.1B total assets)
* 📊 Five trading strategies (Sub-NAV Long, Premium Peak Short, Pair Trade, Options, LLM alerts)
* 🚨 Five fatal risks (unlimited short loss, volatility decay, shareholder dilution, death spiral, index removal)
* 🇰🇷 Overseas-stock short selling and Foreign Exchange Transactions Act considerations for Korean investors

**Three companion datasets**:

* [`dat_companies_2026.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage) — status of 15 DAT firms
* [`dat_vs_benchmark_performance.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage) — semiannual returns 2020-H2 ~ 2026-H1 (MSTR · MARA · BMNR · SBET · BTC · ETH · IBIT · ETHA · S&P500 · QQQ)
* [`mnav_cycles_arbitrage_signals.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage) — 12 mNAV-cycle points + trade signals

### 9. Column: When should you buy luxury?

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md)

> *"A Birkin bag is forever. An LVMH share is not."*

An empirical analysis of the **historic 2024-2025 luxury-sector correction** triggered by China's economic slowdown and property crisis. Full-period 2020-2026 data on **13 major global luxury names** (11 companies + 2 ETFs) including LVMH · Hermès · Kering · Richemont · Ferrari, plus **225 backtests** and a **3-tier low/mid/high-risk portfolio**.

**Key findings**:

* 🥇 **2020-2026 cumulative compounding**: Ferrari +389%, Hermès +311%, Richemont +167%, LVMH +32%, **Kering -42%**
* 📉 **Single-year 2024 figures**: Kering -39.4%, Burberry -30%, LVMH -13%, Moncler -7.8%
* 🔬 **Three single-name (LVMH) strategy backtests**: DCA -10.87%, Buy-the-Dip -11.11%, China-shock contrarian -7.96%
* 🎯 **Lesson**: single-name concentration failed. A GLUX ETF DCA approach is estimated at roughly +30~40%

**What it covers**:

* 🏛️ A new 3-way classification of the luxury sector (Ultra-luxury / Commercial / Affordable)
* 💶 **Three ways to invest in dollar/euro-denominated assets** (local shares, ADRs, GLUX ETF)
* 📊 Deep dive on **Amundi S&P Global Luxury ETF (GLUX)** (ISIN LU1681048630, TER 0.25%)
* 🎨 **3-tier low/mid/high-risk portfolio**
  + 🟢 Low risk: GLUX 40% + Hermès 15% + Ferrari 10% + global ETF 25% + cash 10%
  + 🟡 Mid risk: GLUX 30% + LVMH 20% + Hermès 15% + Richemont 10% + Prada/Ferrari 10% + S&P 500 10% + cash 5%
  + 🔴 High risk: LVMH 25% + Kering 20% + Burberry 15% + Estée Lauder 10% + LVMH calls 10% + Hermès 10% + cash 10%
* 🇨🇳 **China demand-recovery scenario** — Morningstar 2026 base case

**Four companion datasets**:

* [`luxury_companies_etfs_2026.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Luxury%20investment%20strategy) — details on 13 investment targets
* [`luxury_performance_2020_2026.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Luxury%20investment%20strategy) — semiannual returns over 13 periods (LVMH · Hermès · Kering · Richemont · Ferrari · Moncler · GLUX · S&P500 · MSCI China)
* [`luxury_backtest_3strategies.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Luxury%20investment%20strategy) — detailed log of 225 backtests (DCA / Buy-the-Dip / China-shock contrarian)
* [`luxury_portfolio_by_risk.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Luxury%20investment%20strategy) — 19-asset allocations (low/mid/high risk)

### 10. Column: How synchronized are crypto and Nasdaq?

[**📰 Read the full column**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/Nasdaq%20crypto%20coupling%20strategy.MD)

> *"Does Bitcoin follow Nasdaq, or does Nasdaq follow Bitcoin?*
> *The answer — it depends on the moment. And knowing that 'moment' is everything."*

A column that breaks down the 2020-2026 BTC-QQQ 30-day rolling correlation into 26 quarters and analyzes **the correlation impact of 31 major macro and industry events**. It refines the generality that *"BTC moves with Nasdaq"* into **6 regimes**, empirically deriving a trading strategy for each. It delivers everything **end to end — including intraday lag measurement and Python code for a real-time signal-generation bot**.

**Key findings**:

* 📊 **2020-2026 BTC-QQQ 30-day rolling correlation averages +0.335** (the pre-2014 average was near zero)
* 📈 **2025 average correlation 0.52** — roughly **2x** the 2024 figure of 0.23 (LSEG data)
* 🔄 **Regime swing**: a **-0.68 → +0.72** swing **within two weeks** in February 2026
* 🚨 **-0.20 as of April 2026** — the lowest correlation in a decade (**a historic BTC-rebound signal**)
* ⏱️ **In the Medium regime (+0.30~+0.60), Nasdaq leads BTC by 15~60 minutes**
* ⚖️ **Asymmetric coupling**: BTC *ignores Nasdaq rallies but follows its declines*

**What it covers**:

* 📊 **Six years of BTC-Nasdaq relationship evolution** (2014-2019 uncorrelated → 2020-2021 coupling born → 2022 extreme → ETF reshuffle → 2025-2026 oscillation)
* 🎯 **Trading strategy by 6 regimes**
  + 🟢 **NEGATIVE** (<-0.50, 15% frequency): **90-day average +28.5%** → STRONG\_LONG\_BTC (position +15%)
  + 🟢 DECOUPLING (-0.10~-0.49, 15%): +15.2% → ACCUMULATE (+8%)
  + ⚪ LOW (-0.10~+0.30, 25%): NEUTRAL
  + 🟡 **MEDIUM** (+0.30~+0.60, **54%, most common**): +12.8% → **FOLLOW\_NASDAQ** (+10%, using the 15-60 min Nasdaq lag)
  + 🟠 STRONG (+0.60~+0.80, 15%): **-5.2% (negative)** → RISK\_OFF (-5%)
  + 🔴 EXTREME (+0.80~+1.0, 5%): **-12.5% (negative)** → CRISIS\_MODE (-20%)
* 🕐 **Four representative intraday session analyses**
  + 2025-04-02 Liberation Day: 0-min lag (perfect sync)
  + 2025-10-10 Flash Crash: decoupled (crypto alone)
  + 2026-02-17 AI Selloff: Nasdaq leads by 15 min
  + 2026-04-17 Max Divergence: fully decoupled
* 🤖 **Full architecture of a 547-line Python trading bot** — Binance + Alpaca WebSocket integration, Telegram/Slack alerts
* 🚨 **Six risk disclosures** — including the two-week regime-swing risk

**Four companion datasets + the trading bot**:

* [`btc_qqq_correlation_2020_2026.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — correlation across 26 quarters
* [`btc_nasdaq_event_log.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — impact log of 31 major macro/industry events
* [`intraday_coupling_samples.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — 4 sessions intraday (56 points)
* [`correlation_regimes_signals.csv`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — 6-regime classification + trade signals
* 🤖 [`nasdaq_btc_coupling_bot.py`](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — 547-line trading bot (see section 13 below)

### 11. Harness Quant v2 — Scenario-Matrix-Based AI Trading Platform

[**🛠️ Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quant%20v2%20readme%20.MD)

A package that analyzes NASDAQ/S&P500 names via **harness engineering** (an agentic loop where the LLM reasons while calling tools). It implements the know-how accumulated during the Awesome curation process as code.

**6-scenario matrix**:

| # | Horizon | Direction | Trigger |
| --- | --- | --- | --- |
| 01 | Short (1d~4w) | LONG | sector improving + stock well-regarded |
| 02 | Mid (1~3y) | LONG | structural growth (fundamentals + thesis) |
| 03 | Short | LONG/SHORT | sector trend departure (positive/negative divergence) |
| 04 | Mid | LONG/SHORT | structural alpha/underperformance vs sector baseline |
| 05 | Short | SHORT/AVOID | imminent-drop signal (R1~R6 confluence) |
| 06 | Mid | SHORT/AVOID | structural decline (D1~D7 confluence) |

**+ Add-on modules**: Bull vs Bear multi-agent debate, backtest engine, MCP server, orchestrator, GitHub Actions automation.

### 12. Earnings Momentum Agent — Earnings-Surprise-Specialized Top 30

[**🛠️ Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quantv2/Earnings%20momentum%20agent%20readme%20.MD)

> *"Earnings surprises lift the stock, but earnings shocks create the next morning's gap down."*

A **specialized pipeline** built as an extension of Harness Quant v2. On the first trading day of each month it scans roughly 700 NASDAQ + S&P500 names and produces a **Top 30 recommendation** combining *bottom rebound + revenue/earnings growth + earnings surprise + market sentiment*.

**7-stage pipeline**:

```
1. Universe Scanner      filter: market cap $5B+, daily turnover $50M+
2. Fundamental Filter    revenue YoY>=10%, QoQ>=0%, EPS surprise>=+5%, EPS YoY>=0%
3. Technical Filter      +15% rebound off 52-week low, RSI 40~70, MACD bullish/neutral
4. Sentiment Engine      extract 5 signals from X/news/Reddit with Haiku
5. Analyst Consensus     tally Strong Buy/Buy/Hold/Sell, compute price-target upside
6. Multi-Agent Judge     Bull/Bear/Risk/PM 4-agent debate with Opus
7. Top 30 Report         JSON + CSV + Nvidia-forecast-style HTML dashboard
```

**Outputs**:

* **Top 30 JSON** — per name: conviction score 1-10, rating (STRONG\_BUY~STRONG\_SELL), 12-month target, stop loss, Bull/Bear thesis, Risk scenario, PM verdict
* **CSV** — for Excel/Google Sheets viewing
* **HTML dashboard** — price-target distribution bar, Buy/Sell distribution bar, Bull vs Bear thesis cards
* **24-month backtest CSV** — 768 decisions, monthly rebalancing, 3 reasons per action + forward 30-/90-day returns

**24-month backtest summary (2024-04 ~ 2026-04)**:

| Metric | Value |
| --- | --- |
| Total decisions | 768 (BUY 108 / HOLD 582 / SELL 78) |
| Rebalances | 23 (monthly) |
| BUY-point forward 30-day average return | **+7.15%** |
| BUY-point forward 90-day average return | **+14.97%** |
| 30-day hit rate | **83.3%** |
| 90-day hit rate | **68.5%** |

**Key strengths** ✅:

* **Dual filter of bottom rebound + fundamentals** — not pure momentum, but selecting only names that "build a base and rebound on earnings." Capped within -30% of highs to exclude overheated names
* **Agentic reasoning** — not hardcoded rules; the LLM autonomously calls tools like `get_price_snapshot()`, `get_fundamentals()`, `get_sentiment()`, `get_analyst_view()` while reasoning
* **Bull vs Bear opposition** — mitigates single-model bias via four-agent (Bull/Bear/Risk/PM) debate. Each recommendation records a *counterargument* for post-hoc verification
* **Explainability** — three concrete reasons are recorded for every decision
* **Nvidia-forecast-style dashboard** — review everything on one screen
* **Fully open source** — MIT license

**Known risks and limits** ⚠️:

* **The 83.3% hit rate is an idealized scenario** — in live trading, slippage, commission, taxes, and pipeline latency lower actual returns
* **Possible ex-post bias** — Finnhub historical consensus may reflect restatements
* **Sentiment signals are bot/manipulation-prone** — less reliable for low-liquidity small caps
* **Market-regime dependence** — 2024-2026 was an AI rally; unverified in bear markets and sector-rotation phases
* **LLM cost** — roughly $200~400/month on Opus
* **Overfitting concern** — filter thresholds are based on historical data
* **Regulatory risk** — Korean residents must review the Foreign Exchange Transactions Act and FSS requirements

### 13. Nasdaq-BTC Coupling Bot — Real-Time Correlation-Tracking Signal Generator

[**🛠️ Read the full document**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/)

> *"The question was never whether crypto and stocks move together.*
> *The question is — when, how fast, and in which direction?*
> *Those who know the regime, know the trade."*

A Python bot that **implements the analysis from column 10 (Nasdaq-crypto coupling) above as a real-time trading-signal-generation system**. With Binance + Alpaca WebSocket integration, it forms an end-to-end pipeline: **real-time BTC·QQQ price collection**, **30-day rolling correlation calculation**, **automatic 6-regime classification**, and **Telegram/Slack alerts**.

**Core architecture** (547 lines, 10 classes, 18 functions):

```
┌──────────────────────────────────────────────────────┐
│              CouplingBot (Orchestrator)              │
└───────────────┬──────────────────┬───────────────────┘
                │                  │
     ┌──────────▼────────┐  ┌──────▼──────────┐
     │  DataCollector    │  │ NotifDispatcher │
     │  (WebSocket)      │  │ (Telegram/Slack)│
     └──────────┬────────┘  └─────────────────┘
                │
     ┌──────────▼────────────┐
     │  CorrelationAnalyzer  │
     │  - 30d rolling corr   │
     │  - Regime classifier  │
     │  - Cross-asset lag    │
     └──────────┬────────────┘
                │
     ┌──────────▼────────────┐
     │   SignalGenerator     │
     │  6 regimes → signals  │
     └──────────┬────────────┘
                │
                ▼
          TradingSignal (JSON)
```

**The 10 main classes**:

| Class | Role |
| --- | --- |
| `Regime` (Enum) | 6-regime classification (NEGATIVE ~ EXTREME) |
| `Signal` (Enum) | 7 signal types (STRONG\_LONG\_BTC ~ CRISIS\_MODE) |
| `MarketSnapshot` (dataclass) | current market state (price, return, correlation, market-open flag) |
| `TradingSignal` (dataclass) | the bot's full output spec (position size, stop, target, reasoning) |
| `CorrelationAnalyzer` | 30-day rolling correlation + regime classification + cross-correlation lag measurement |
| `SignalGenerator` | regime + intraday movement → trading signal generation |
| `DataCollector` | unified data collection from Binance (ccxt) + Alpaca + yfinance |
| `NotificationDispatcher` | Telegram / Slack / email push |
| `CouplingBot` | main orchestrator (infinite loop + regime-change alerts) |
| `Backtester` | historical-data validation framework |

**Parameters by regime** (built into SignalGenerator):

| Regime | Signal | Position | Stop Loss | Target | Confidence |
| --- | --- | --- | --- | --- | --- |
| 🟢 NEGATIVE | STRONG\_LONG\_BTC | **+15%** | -15% | **+25%** | 85% |
| 🟢 DECOUPLING | ACCUMULATE\_BTC | +8% | -10% | +15% | 65% |
| ⚪ LOW | NEUTRAL | 0% | — | — | 40% |
| 🟡 **MEDIUM** | **FOLLOW\_NASDAQ** | +10% | -8% | +12% | 70% |
| 🟠 STRONG | RISK\_OFF | **-5%** | -5% | +5% | 75% |
| 🔴 EXTREME | CRISIS\_MODE | **-20%** | -3% | +3% | 90% |

**Four execution modes**:

```
# Set environment variables
export BINANCE_API_KEY=xxx
export ALPACA_API_KEY=xxx
export TELEGRAM_BOT_TOKEN=xxx
export TELEGRAM_CHAT_ID=xxx

# One-shot check (see current state immediately)
python nasdaq_btc_coupling_bot.py --mode once

# Paper trading (signals only, no live trades)
python nasdaq_btc_coupling_bot.py --mode paper --interval 300

# Backtest (validate against historical data)
python nasdaq_btc_coupling_bot.py --mode backtest

# Live (caution: real signal generation)
python nasdaq_btc_coupling_bot.py --mode live --interval 60
```

**Example output** (based on the 2026-04-17 situation):

```
🟢🚀 Nasdaq-BTC Coupling Bot
── Time: 2026-04-17 14:30 UTC
── Signal: STRONG_LONG_BTC
── Regime: Negative (-0.50~-1.0)
── Correlation (30d): -0.200
── Confidence: 85%
── Risk: HIGH

📋 Recommended action: Correlation -0.20. Begin staged BTC accumulation
              (3 tranches, 5% capital each)

💰 Position size: +15.0%
🛑 Stop: -15.0%
🎯 Target: +25.0%

🧠 Rationale:
   1. BTC-NDX correlation < -0.5 (historic low)
   2. Past 4 instances of this regime: 90-day average +28% rebound
   3. 2021-Q3, 2023-Q3, 2024-Q3, 2025-Q4 all formed BTC bottoms

⚠️ This signal is for education/research. Investment decisions are your own responsibility
```

**Key strengths** ✅:

* **Regime-based auto-switching** — automatically responds to swings like the -0.68 → +0.72 in two weeks (2026-02)
* **Cross-correlation lag measurement** — extracts the 15~60 min Nasdaq-leads-BTC pattern in the Medium regime in real time
* **Reflects asymmetric coupling** — BTC ignores Nasdaq rallies but tracks declines; this asymmetry is baked into the SignalGenerator parameters
* **Off-hours correction** — automatically applies -30% confidence when the US market is closed
* **Includes a Backtester framework** — historical validation possible (real implementation extends with yfinance + ccxt)
* **Fully open source** — MIT license

**Known risks and limits** ⚠️:

* **Correlation is past statistics** — no guarantee of the future. A pattern valid in 2021 may not work in 2026
* **Regime-transition lag** — a 30-day window reacts slowly to sudden changes; a parallel 14-day window is advised in some scenarios
* **Flash-crash vulnerability** — a crypto-only crash like 2025-10-10 cannot be predicted by the coupling model
* **Liquidity assumptions** — slippage on large positions is far greater than in simulation
* **API-stability dependence** — the bot halts during Binance/Alpaca outages
* **Regulatory risk** — automated trading by Korean residents requires review under the Foreign Exchange Transactions Act and Capital Markets Act

**Future expansion roadmap** (v2 plan):

1. **Include ETH, SOL** — altcoins correlate +0.85~0.95 with BTC; signals can be extended
2. **MCP integration** — Claude Opus validates signals against news, SEC filings, and social
3. **Walk-forward backtest** — measure hit rate per regime
4. **Kelly Criterion** — auto-optimize position size
5. **Pre-emptive regime-transition detection** — early warning on sharp correlation changes
6. **Multi-timeframe** — simultaneous 1-min·5-min·1-hour·1-day monitoring
7. **Options integration** — automated BTC put/call option hedging

---

## Why is this repo needed?

The AI-trading field **spawns new repos by the month.**

* virattt/ai-hedge-fund has passed 55,800 stars
* ElizaOS, at 17,600+ stars, has become the standard for crypto AI agents
* Frameworks like TradingAgents, FinRobot, and AgenticTrading ship major updates monthly
* Frontier LLMs like Claude Opus 4.7, GPT-5.4, and Gemini 3.x keep evolving
* New standards like MCP shift the infrastructure landscape weekly
* **Nof1 Alpha Arena shakes our intuition with GPT-5 -75% and DeepSeek +46%**

The problem is — **it's hard to tell what's actually usable versus what just has a flashy README**. Star count is not quality, an academic-paper basis doesn't mean it works live, and backtest results are often cherry-picked.

**And apart from tool curation, strategies themselves need curation.** Every quant tool is ultimately a variant of *which factor you run on which theoretical foundation*. **Awesome Claude Quant Scripts** organizes that academic foundation (Graham, Fama-French, Jegadeesh-Titman, Novy-Marx, AQR, López de Prado…) into Claude-ready prompts, compressing the *tool selection → strategy design → code generation* cycle.

**AI is also not the only answer.** Traditional market-structure analysis — disclosure timing, DAT firms' mNAV arbitrage, luxury-sector polarization — is also a domain we can newly understand through AI-amplified analytical power.

This repo is a **public edition of personal curation** meant to organize that chaos. At the same time:

* It turns patterns learned during curation into **reference implementations** and publishes them
* It **analyzes macro market trends and industry shifts in columns**
* It publishes **empirical data and backtests** as CSV so readers can verify directly
* It releases all content under the **MIT license** for free use

---

## Where should I start?

### First-time visitors

Pick an Awesome list by your area of interest:

* **Stock investing tools**: the *"recommended starting path"* section of [Awesome Vibe Invest — Stocks](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest.MD)
* **Crypto trading tools**: the *"🎯 recommended starting path"* section of [Awesome Vibe Invest — Crypto](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest%20crypto.MD)
* **Quant strategy itself** 🆕: [Awesome Claude Quant Scripts](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD) — start from the 8-strategy taxonomy and primary sources. If you want to generate backtest code with Claude immediately, this is the entry point

### To gain market insight for the AI era

Read the columns (recommended order):

* 🛡️ **Insight on risk management**: [the LTCM column](https://github.com/gameworkerkim/vibe-investing/blob/main/Vibe%20Investing%20Risk%20Management.MD) — first
* 🏢 **Insight on industry change**: [the Microsoft Fintool acquisition column](https://github.com/gameworkerkim/vibe-investing/blob/main/Microsoft%20fintool%20acquisition%20column.MD)
* 🕵️ **Insight on the dark side of market structure**: [analysis of crypto-futures pump-dump patterns](https://github.com/gameworkerkim/vibe-investing/blob/main/Crypto%20perp%20manipulation%20column.MD)
* 🌙 **Structural asymmetry of disclosure timing**: [Does the market open when it closes?](https://github.com/gameworkerkim/vibe-investing/blob/main/AfterMarketClose/After_Market_Close_Column.md)
* 🏦 **Arbitrage in the crypto-equity intersection**: [the DAT mNAV arbitrage strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage/Dat%20mnav%20arbitrage%20strategy.MD)
* 👜 **Contrarian opportunity in a traditional sector**: [the luxury investing strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md)
* 🔗 **Empirical data on crypto-equity coupling**: [the Nasdaq-crypto coupling strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/Nasdaq%20crypto%20coupling%20strategy.MD)

### To jump straight into code

You have three choices:

* **Scenario-matrix approach**: the *"usage examples"* section of [Harness Quant v2](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quant%20v2%20readme%20.MD) — run whichever of the 6 scenarios interests you first
* **Earnings-momentum specialization**: the *"quick start"* section of [Earnings Momentum Agent](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quantv2/Earnings%20momentum%20agent%20readme%20.MD) — run the 7-stage pipeline at once via the orchestrator
* **Crypto-equity real-time signals**: [Nasdaq-BTC Coupling Bot](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling) — check the current regime instantly with `python nasdaq_btc_coupling_bot.py --mode once`

### To build a quant strategy with Claude yourself 🆕

From the 8 strategies in [**Awesome Claude Quant Scripts**](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD), pick the one that fits your style and copy that section's **Claude Prompt Template** into Claude.ai or the API. It generates backtest code that automatically incorporates primary academic sources + look-ahead-prevention notes.

* **Finding undervalued names**: Value (PER, PBR, EV/EBITDA composite)
* **Earnings growth + price balance**: Growth (PEG < 1.5 + revenue growth)
* **Bear-market-defensive quality names**: Quality (ROE + GP/Assets + low D/E)
* **Tracking trending names**: Momentum (12M-1M, J=K=6 variant)
* **Avoiding single-factor slumps**: Multi-Factor (Value × Momentum × Quality × Low Vol)
* **Multi-asset trend following**: Trend Following (Donchian breakout)
* **Market-neutral hedging**: Statistical Arbitrage (cointegration pair trading)
* **Using unstructured data**: ML-based (LightGBM or FinBERT sentiment alpha)

Plus **5 general-purpose prompts (T1~T5)** — Strategy Stress-Test, Paper→Code, Risk Overlay, Crypto port, Live Paper Trading transition — apply commonly across all of these strategies.

### To analyze the data yourself

14+ CSV datasets are published. Analyze immediately with Python pandas:

* **Disclosure timing**: `disclosure_timing_cases.csv` (34 actual disclosures + returns)
* **DAT firms**: `dat_companies_2026.csv`, `dat_vs_benchmark_performance.csv`, `mnav_cycles_arbitrage_signals.csv`
* **Luxury sector**: `luxury_companies_etfs_2026.csv`, `luxury_performance_2020_2026.csv`, `luxury_backtest_3strategies.csv` (225), `luxury_portfolio_by_risk.csv`
* **Nasdaq-crypto coupling**: `btc_qqq_correlation_2020_2026.csv` (26 quarters), `btc_nasdaq_event_log.csv` (31 events), `intraday_coupling_samples.csv` (56 points), `correlation_regimes_signals.csv` (6 regimes)
* **Earnings momentum**: `backtest_log_24months.csv` (768 decisions)

### If you plan to auto-trade with your own capital

**You must** read the following pitfall sections first:

* Stocks: [Awesome Vibe Invest — 12 common pitfalls](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest.MD)
* Crypto: [Awesome Vibe Invest Crypto — 8 common pitfalls](https://github.com/gameworkerkim/vibe-investing/blob/main/Awesome%20vibe%20invest%20crypto.MD)
* **Backtest pitfalls of the strategies themselves** 🆕: [Awesome Claude Quant Scripts — Disclaimer section](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD) — checklist for look-ahead, survivorship, overfitting, and LLM hallucination
* Futures-market structural risk: [the VTCLR definition and investor conclusions in the Invisible Hand column](https://github.com/gameworkerkim/vibe-investing/blob/main/Crypto%20perp%20manipulation%20column.MD)
* Limits of the earnings-momentum strategy: [the "known risks and limits" of the Earnings Momentum Agent](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quantv2/Earnings%20momentum%20agent%20readme%20.MD)
* **Short selling, inverse, and leverage risk**: [DAT mNAV arbitrage — 5 key risk disclosures](https://github.com/gameworkerkim/vibe-investing/blob/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage/Dat%20mnav%20arbitrage%20strategy.MD)
* **Sector-concentration risk**: [luxury investing strategy — high-risk portfolio warning](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md)
* **Correlation regime-swing risk**: [Nasdaq-crypto coupling — 6 risk disclosures](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/Nasdaq%20crypto%20coupling%20strategy.MD) — essential for handling swings like the -0.68→+0.72 in two weeks

Those who skip this step lose the most.

---

## Roadmap

### Done

* Awesome Vibe Invest v1 (stocks, 30+ repos)
* Awesome Vibe Invest — Crypto Edition (crypto + benchmark-centric)
* **Awesome Claude Quant Scripts** — 8 quant strategies + 30+ primary papers + Claude prompt templates 🆕
* Harness Quant v2 (6 scenarios + backtest + MCP + debate)
* LTCM column (risk management)
* Microsoft Fintool acquisition column
* Crypto-futures pump-dump mathematical-review column
* Earnings Momentum Agent — 24-month backtest, hit rate 83.3%
* Does the market open when it closes? — empirical analysis of 34 AMC disclosures
* DAT mNAV arbitrage — 15 DAT firms + Chanos pair-trade reconstruction
* Luxury investing strategy — LVMH/Hermès/Kering + 3-tier portfolio
* How synchronized are crypto and Nasdaq? — 2020-2026 BTC-QQQ correlation + 6-regime classification + intraday lag analysis
* Nasdaq-BTC Coupling Bot — 547-line Python signal generator (Binance + Alpaca + Telegram integration)

### In progress / planned

* **English edition of Awesome Claude Quant Scripts** 🆕 — expand international reach
* **Awesome Claude Quant Scripts v2** 🆕 — add domain sub-curations for KR equity, crypto-native, and FX
* **English translations** — the full Awesome series + columns
* **Korean-stock (KOSPI/KOSDAQ) scenarios** — pyKRX + Korea Investment & Securities OpenAPI integration
* **A column on Anthropic's finance-agent strategy**
* **A column on five changes coming to Korea's asset-management industry within a year**
* **On-chain asset integration** — DeFi/stablecoin/prediction-market signals
* **Awesome Vibe Invest — Korea Market Edition** (KOSPI/KOSDAQ-specialized)
* **Monthly insight report** — publishing backtest hit-rates of key signals
* **VTCLR pattern-detection open-source tool** — a Python package based on Benford's law + wallet clustering
* **Earnings Momentum Agent v2** — walk-forward validation + regime-aware filters + 2022 rate-hike-period backtest
* **DAT mNAV Watcher** — open-source real-time mNAV monitoring based on Claude + MCP
* **Luxury-sector regime detector** — China consumer sentiment + property indicators → luxury buy/sell signals
* **Coupling Bot v2** — ETH/SOL extension, Kelly Criterion position sizing, multi-timeframe (1-min·5-min·1-hour), walk-forward backtest
* **Coupling Bot Docker/AWS deployment guide** — configuring a 24-hour unattended environment

---

## Content Stats

```
Awesome curations: 3 (50+ tools evaluated + 8 strategies + 30+ primary papers)  ← 🆕 +1
Columns:           7 (70,000+ words total)
Tools built:       3 (Harness Quant v2 + Earnings Momentum Agent + Nasdaq-BTC Coupling Bot)
                   → 23 scenarios/pipelines/regime stages total
Backtest logs:     24 months × monthly rebalancing = 768 decisions
                   + 26 quarters of correlation tracking (coupling bot)
Public datasets:   14+ CSV (1,400+ data points total)
                  - 34 disclosure-timing cases
                  - 15 DAT firms + 12 semiannual return periods + 12 mNAV-cycle points
                  - 13 luxury names + 13 semiannual return periods + 225 backtests + 19 portfolio allocations
                  - Nasdaq-crypto coupling: 26 quarters + 31 events + 56 intraday points + 6 regimes
                  - Earnings Momentum 768 records
Open-source Python: Nasdaq-BTC Coupling Bot 547 lines (10 classes, 18 functions)
Prompt templates:  Awesome Claude Quant Scripts 13 (8 per-strategy + general T1~T5)  ← 🆕
Verified sources:  125+ academic papers, official docs, and industry reports  ← 🆕 (+30 quant papers)
Languages:         Korean (with English summaries)
```

---

## Contributing

All of the following are welcome:

* ⭐ **Starring** — the biggest encouragement
* 🐛 **Reporting good missing repos** — issue or PR
* 💬 **Rebutting an evaluation** — debate raises curation quality
* 🌍 **English translation** — international contribution
* 🇰🇷 **Suggesting Korea-market resources** — use cases for DART, ECOS, NICE, etc.
* 📊 **Sharing your own backtest results** — walk-forward results from Harness Quant or Earnings Momentum Agent
* 📰 **Proposing column topics** — market issues you'd like covered next
* 🔢 **Extending CSV data** — contributing additional cases to the disclosure-timing, DAT, and luxury datasets
* 📚 **Adding quant strategies** 🆕 — proposing new factors/papers/Claude prompts for Awesome Claude Quant Scripts

Let me know freely via an issue or PR. **Dissent is also welcome** — *"this evaluation is wrong"* is the most valuable feedback.

---

## Disclaimer

All content in this repo is for **research and educational purposes**.

* **No tool guarantees profit** — Alpha Arena's GPT-5 -75% is real data, and the Earnings Momentum Agent's 83.3% hit rate is an idealized backtest scenario
* All evaluations are subjective, based on public information at the time of writing
* Before deploying real capital, always conduct your own backtests, paper trading, and legal review
* **Code generated by LLMs, including Claude, may contain factual errors, structural bias, and security vulnerabilities.** If you cannot verify the prompts and code skeletons in Awesome Claude Quant Scripts yourself, cross-validate with another LLM to filter hallucinations 🆕
* The US SEC/CFTC, Korea's FSS, and the EU's MiCA may all apply regulation to AI-based automated trading — managing your own assets is OK, but managing others' funds requires a license
* Some strategies, such as MEV bots' sandwich attacks, are an ethical gray area and may be interpreted as market manipulation in some jurisdictions
* Market-structure columns (e.g., crypto-futures pump-dump, AMC disclosure timing, DAT mNAV arbitrage) are **statistical, academic commentary that names no specific party**; legal characterization of individual events is for the relevant investigative/regulatory authorities
* Earnings-surprise-based strategies are **market-regime dependent**. There is no guarantee that results validated in the 2024-2026 AI rally work identically in other regimes (e.g., bear markets, sector rotation)
* **Downside bets, short selling, inverse ETFs, and leveraged investing can be devastating for individuals.** Always consult the 5 risk disclosures in the DAT mNAV arbitrage column and the 3-tier risk warning in the luxury investing strategy. Strictly limit downside-bet strategies to within 5~10% of the portfolio
* Responsibility for investment outcomes and legal risk rests with the user

---

## About

**HoKwang Kim (Dennis Kim)**
Cyworld CEO · Developer · Web3 Investor
Active in Web3, blockchain, and AI trading.

* 📧 [gameworker@gmail.com](mailto:gameworker@gmail.com)
* 🔗 [GitHub @gameworkerkim](https://github.com/gameworkerkim)

This repo is built on insights gained as an AI-assisted entrepreneur.

---

## License

MIT License — free to use, modify, and distribute. Attribution is appreciated.

When citing or redistributing columns, please credit *"HoKwang Kim (Dennis Kim) / vibe-investing repo."*

---

***"Models always point to truth. Fingers always point to greed."***

***"Model intelligence is not trading intelligence."***  
— Alpha Arena Season 1 lesson

***"Benford's law cannot lie. On-chain data lasts forever."***

***"Earnings surprises lift the stock,  
earnings shocks create the next morning's gap down."***

***"The market closes, but information opens.  
The question is — who reads it first?"***  
— After Market Close column

***"Trade the premium, not the faith."***  
— DAT mNAV arbitrage column

***"A Birkin bag is forever. An LVMH share is not.  
Don't confuse the brand's immortality with your portfolio's fate."***  
— Luxury investing column

***"The question was never whether crypto and stocks move together.  
The question is — when, how fast, and in which direction?  
Those who know the regime, know the trade."***  
— Nasdaq-crypto coupling column

***"Theory without code is philosophy. Code without theory is gambling.  
Claude collapses the gap — but never replaces verification."***  
— Awesome Claude Quant Scripts

⭐ **If this repo helped you, please support it with a star.** ⭐  
Updated 1-2 times per week.
