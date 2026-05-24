# ARDS-Defense

### Adaptive Recession-Defensive Strategy for Defense & AI-Weaponization

> "In an age of war and conflict, defense is no longer merely a defensive sector but a structural growth sector.
> Yet even within structural growth, the business cycle always returns. This strategy trades that paradox."

As the Cold War recedes and the era of Pax Americana fades, a new period of disorder is emerging. The Russia-Ukraine war has triggered European rearmament, and Japan has begun expanding a defense budget long capped at 1% of GDP. The Iran-Israel-US conflict in the Middle East consumed in a short span the weapons and defense systems the US would produce in a full year.

ARDS-Defense is an adaptive recession-defensive investment strategy specialized for the Defense and AI-Weaponization sectors. It diagnoses the macro regime to determine a Phase, adjusts that Phase with a defense-specific indicator (Defense Sentiment), then splits Korean and US defense names into three tiers and automatically derives a Phase-based allocation.

---

## Repository Structure

```
ARDS-Defense/
├── README.md                ← Korean master document
├── README_EN.md             ← This document (English)
├── llms.txt                 ← LLM-friendly summary index
├── prompts/
│   ├── ARDS-Defense_KO.md    ← Korean execution prompt (v1.1)
│   ├── ARDS-Defense_EN.md    ← English execution prompt (v1.1)
│   └── ARDS-Defense_ZH.md    ← Chinese execution prompt (v1.1)
└── result/                  ← Per-LLM output archive
    ├── claude_0524.md                       ← Claude run
    ├── DeepSeek_0524.md                      ← DeepSeek run
    ├── readme.md                             ← Cross-LLM comparison (Claude vs DeepSeek)
    ├── ARDS_Defense_Critique.md              ← Hard critique from a live-trading view
    └── deepseek_markdown_20260524_371f74.md  ← DeepSeek self-critique feedback
```

The `result/` folder archives outputs from running the same prompt across multiple LLMs and languages, used for multi-LLM cross-validation and cross-lingual output asymmetry analysis.

---

## STEP 1 — Investment Thesis

### 1.1 Why Defense + AI Now

Two large forces overlap: the structuration of warfare and a defense supercycle. Global defense spending surpassed USD 2.6 trillion in 2026 and is projected to reach USD 3.6 trillion by 2030. Within this, the Pentagon's AI budget alone jumped in a single year from under USD 2 billion to USD 13.4 billion.

The core point is not a simple rise in defense spending but a **structural reallocation toward AI and software within defense budgets**. In 2025, VC-backed defense startup investment across the US and Europe reached roughly USD 7.7 billion, more than double 2024, and Palantir raised its 2026 full-year revenue guidance to USD 7.65-7.66 billion (+71% over 2025's USD 3.32 billion).

> These figures are estimates as of writing. The execution prompt is designed to re-acquire macro and fundamental indicators via live web search, so values refresh on each run.

### 1.2 The Dual Nature: Recession-Defensive + Structural Growth

| Nature | Description |
|---|---|
| Recession-Defensive | Defense budgets are cut only with a lag in downturns, and geopolitical crises occur independently of the cycle |
| Structural Growth | The shift toward AI, autonomous weapons, space defense, and cyber warfare is a 10-year-plus investment cycle that transcends the business cycle |
| Asymmetric Alpha | Traditional defense vs AI-defense names have completely different risk-return profiles even within the same sector |

---

## STEP 2 — Universe

### 2.1 Korean (KOSPI/KOSDAQ) Defense Companies

| Tier | Name | Ticker | Core Business | AI / Unmanned Link |
|---|---|---|---|---|
| Core | Hanwha Aerospace | 012450 | Aero engines, missiles, K9 SPH, space launch | Hanwha 3-affiliate AI/unmanned platform |
| Core | LIG Nex1 | 079550 | Guided missiles, precision strike, ISR | AI-based C2 |
| Core | Korea Aerospace (KAI) | 047810 | Fighters (KF-21), trainers, satellites | UCAV development |
| Core | Hyundai Rotem | 064350 | Tanks (K2), armored vehicles, rail | Unmanned tank / autonomy |
| Core | Hanwha Ocean | 042660 | Warships, submarines | USV technology |
| Core | Hanwha Systems | 272210 | C4I, radar, satcom | Core AI/unmanned platform |
| Satellite | Poongsan | 103140 | Ammunition, shells | — |
| Satellite | STX Engine | 077970 | Naval engines, generators | — |
| Satellite | Victek | 065450 | Military power systems | — |
| Satellite | SNT Dynamics | 003570 | Naval engines, defense vehicle parts | — |
| Satellite | Firstec | 010820 | Guided weapon systems, aircraft mods | — |
| Satellite | HJ Heavy Industries | 097230 | Shipbuilding | — |

### 2.2 US (NYSE/NASDAQ) Defense Companies

| Tier | Name | Ticker | Core Business | AI / Unmanned Link |
|---|---|---|---|---|
| Core | Lockheed Martin | LMT | Fighters (F-35), missiles, satellites | AI battle management, autonomy |
| Core | RTX Corp | RTX | Missiles (Patriot), radar, aero engines | AI sensor fusion, interception |
| Core | Northrop Grumman | NOC | Stealth bomber (B-21), space, missiles | Autonomous UAVs |
| Core | General Dynamics | GD | Tanks, submarines, IT/C4I | Cyber, AI command and control |
| Core | L3Harris | LHX | EW, comms, satellites | AI SIGINT |
| Core | Boeing | BA | Fighters (F/A-18), transports, satellites | Autonomy, MQ-25 unmanned tanker |
| AI-Defense | Palantir | PLTR | AI battle management (AIP/Maven) | Pure-play defense AI |
| AI-Defense | Kratos Defense | KTOS | Unmanned combat aircraft (XQ-58) | Autonomous UAV specialist |
| AI-Defense | AeroVironment | AVAV | Small UAVs (Switchblade) | Autonomous attack drones |
| AI-Defense | BigBear.ai | BBAI | AI decision analytics | Defense AI data analysis |
| Tactical | Huntington Ingalls | HII | Carriers, submarines | — |
| Tactical | Rocket Lab | RKLB | Launch vehicles, satellites | — |
| Tactical | Booz Allen Hamilton | BAH | Defense consulting, cyber | AI consulting |
| Pre-IPO | Anduril Industries | (private) | AI autonomous weapons, Fury UCAV | Leading defense AI startup (~USD 61B valuation) |

### 2.3 ETF Universe

| ETF | Ticker | Region | Profile | Manager |
|---|---|---|---|---|
| PLUS K-Defense | 449450 | Korea | Top 10 K-defense names | Hanwha AM |
| TIGER US Defense TOP10 | 494840 | US | Top 10 US defense large caps | Mirae Asset |
| iShares US Aerospace & Defense | ITA | US | Broad US aerospace and defense | BlackRock |
| iShares Defense Industrials Active | IDEF | Global | Global defense active | BlackRock |

---

## STEP 3 — Execution Prompts (Multilingual)

Copy the v1.1 prompt and paste it into a web-search-capable LLM. It runs immediately with no blanks, and macro indicators are designed to be acquired live via web search.

| Language | File | Note |
|---|---|---|
| Korean | `prompts/ARDS-Defense_KO.md` | Primary |
| English | `prompts/ARDS-Defense_EN.md` | Global distribution |
| Chinese | `prompts/ARDS-Defense_ZH.md` | Greater China distribution |

### v1.1 Core Logic (shared across languages)

- STEP 0 — Determine macro Phase (1-4) via a 5-Factor Recession Composite
- STEP 1 — Adjust Phase level by +/-1 using a Defense Sentiment Score (0-100)
- STEP 2 — 3-Tier Universe (Core Defense / AI-Defense / Tactical)
- STEP 3 + 3.5 — 5-Dimension Scoring then auto-allocate within tiers (score-weighted, 40% cap)
- STEP 4 — Phase-based allocation matrix
- STEP 5-7 — AI-Defense special rules, execution rules, counter-scenarios

---

## STEP 4 — Multi-LLM Run Analysis (2026-05-24)

This section compares running the identical v1.1 prompt on **Claude** and **DeepSeek**. Despite identical rules, universe, and procedure, meaningful differences arose in the data backing the macro call, in security scoring, in final weights, and in rule consistency. This analysis is central to the repository's cross-LLM validation research.

Raw outputs: [`result/claude_0524.md`](result/claude_0524.md), [`result/DeepSeek_0524.md`](result/DeepSeek_0524.md)
Cross-analysis and self-critique: [`result/readme.md`](result/readme.md), [`result/deepseek_markdown_20260524_371f74.md`](result/deepseek_markdown_20260524_371f74.md)

### 4.1 Result Summary

| Item | Claude | DeepSeek | Match |
|---|---|---|---|
| Final Phase | Phase 1 (Expansion) | Phase 1 (Expansion) | Same |
| Recession Composite | 22.5% | 15.0% | 7.5pp gap |
| Defense Sentiment | 92.5 | 97.25 | Close |
| Country split | Korea 50 / US 50 | Korea 50 / US 50 (post-hoc fix) | Same (different path) |
| Tier 1 top | LIG Nex1 (75.1) | Hanwha Aerospace (86.0) | Different #1 |
| PLTR final weight | 3.7% | 4.5% | Different |
| Portfolio style | Diversified (4.6-5.3% each) | Concentrated (top 9-14%) | Philosophy gap |

Both models converged on the conclusion (Phase 1, Korea-US 50:50, defense super-strength), but the numeric basis and per-name weights diverged considerably. This quantitatively demonstrates that the same prompt produces different outputs across LLMs.

### 4.2 DeepSeek's Mistakes and Inferred Causes

DeepSeek's output contained flaws unacceptable in live operation. Notably, DeepSeek itself acknowledged these in its self-critique ([`deepseek_markdown_20260524_371f74.md`](result/deepseek_markdown_20260524_371f74.md)).

**(1) Arithmetic error: country weights summing to 142%**

DeepSeek wrote that Korea was allocated "40% x 50% = 20%" in STEP 3.5, yet its final tally showed Korea 61.5% + US 80.4% = **142%**, an impossible total. It then flagged a "rule violation" and post-hoc forced the split back to 50:50.

- Likely cause 1 — **Double counting:** Hanwha Systems sits in both Tier 1 and Tier 2; when summing by country, both tier weights were likely added to Korea, double-counting. Claude avoided this by tabulating Hanwha Systems' Tier 1 and Tier 2 weights separately.
- Likely cause 2 — **Baseline confusion:** Mixing "within-tier weight (%)" and "final portfolio weight (%)" mid-calculation, summing within-tier (100% base) figures as if they were portfolio (100% base) figures. A value like 80.4% is close to "sum of US within-tier-1 weights."
- Likely cause 3 — **Cumulative error from sequential generation:** LLMs generate tables token by token and tend to regenerate plausible numbers downstream rather than recompute upstream values. Without an intermediate verification step in the prompt, accumulated error passes straight through.

**(2) Methodological inconsistency: LEI interpretation**

The only divergence point among the five factors was Factor D (LEI -0.7%). The prompt specifies only "< -2% means 100%" and leaves the 0 to -2% band undefined.

- Claude: treats the 0 to -2% band as "midpoint 50%" → Composite 22.5%
- DeepSeek: treats it as "not below -2%, so 0%" → Composite 15.0%

The problem is that within the same report DeepSeek applied 50% to Factor A's 0-50bp band but 0% to Factor D. **The band-handling logic was inconsistent within one report.** This is a textbook case of a model filling an under-specified rule differently each time.

**(3) Illusion of precision**

DeepSeek cited many quantitative figures (GPR 415, missile procurement +188%, US defense budget +42% YoY) for a more precise look, but many are hard to verify or context-limited. "+42% YoY" is a pre-Congress proposal, "+188%" may be a single category, and GPR 415 is a secondary-source citation hard to cross-check against the original. More numbers do not equal better analysis.

**(4) PLTR weight inversion: sensitivity to rule-application order**

The lower-scoring PLTR (62.5) received a higher weight (4.5%) in DeepSeek. By narrowing Tier 2 to four names and capping KTOS and AVAV first, residual weight flowed to PLTR. This exposes a structural weakness: the "score-proportional allocation" rule is sensitive to the number of names and the cap-application order.

### 4.3 DeepSeek's Strengths (credit where due)

The presence of errors does not render DeepSeek's output worthless.

- **More concrete counter-scenarios:** It specifically flagged a LAWS (lethal autonomous weapons ban treaty) scenario and PLTR's DIA contract dispute. Claude touched similar themes but with less specificity.
- **Richer emerging-company info:** It incorporated Anduril's USD 61B valuation and USD 20B 10-year contract, and KTOS pipeline detail.
- **More realistic valuation:** It discounted D4 with concrete figures such as PLTR forward PE 97-110x and KTOS 67x.

### 4.4 Recommended Stock List (cross-validated by both models)

Names both LLMs placed in the top tier form a high-confidence "convergence zone." Below is a consolidated list synthesizing both outputs.

**Tier 1 — Core Defense (both models top-ranked)**

| Name | Ticker | Region | Claude Score | DeepSeek Score | Shared View |
|---|---|---|---|---|---|
| Hanwha Aerospace | 012450 | KR | 75.0 | 86.0 | Korea #1-2 in both, strongest export momentum |
| LIG Nex1 | 079550 | KR | 75.1 | 83.8 | Top-ranked in both, guided weapons |
| Lockheed Martin | LMT | US | 72.2 | 83.5 | US #1 in both, flight-to-quality anchor |
| Northrop Grumman | NOC | US | 71.5 | 80.0 | Nuclear, space, stealth |
| RTX | RTX | US | 66.2 | 79.0 | Missiles, air defense |
| Hyundai Rotem | 064350 | KR | 69.0 | 77.5 | K2 tank export margin |
| Korea Aerospace | 047810 | KR | 65.5 | 78.0 | KF-21 entering mass production |

**Tier 2 — AI-Defense (structural growth, high volatility)**

| Name | Ticker | Region | Shared View | Caution |
|---|---|---|---|---|
| Hanwha Systems | 272210 | KR | Top Tier 2 in both, K-AI defense | Double-listed with Tier 1 |
| AeroVironment | AVAV | US | UAVs, loitering munitions | Market-cap volatility |
| Kratos | KTOS | US | Unmanned combat / target drones | Turning profitable |
| Palantir | PLTR | US | Pure-play defense AI | Forward PE 80-110x; STEP 5 rule cuts weight 50% |

**Both models excluded:** BigBear.ai (BBAI), scoring below 60 in both. Boeing (BA) split the verdict: Claude excluded (44.2) vs DeepSeek borderline (61.5), so include only in small size with caution.

This list synthesizes qualitative LLM assessments; verify each name's actual financials and valuation immediately before execution. This is not investment advice.

### 4.5 Key Differences

| Dimension | Claude | DeepSeek |
|---|---|---|
| Arithmetic accuracy | No errors | 142% summation error |
| Rule consistency | LEI 50% applied consistently | LEI 0% (inconsistent with Factor A) |
| Data posture | Conservative, verifiable | Quant-rich but hard to verify |
| Portfolio | Broad diversification | High-conviction concentration |
| Counter-scenarios | Standard | More concrete, richer |
| Emerging-company info | Limited | Rich (Anduril, etc.) |
| Reasoning integrity | Stronger | Visible post-hoc patching |

### 4.6 LLM Error Modes and the Need for Multi-LLM Correction

This case quantitatively shows why a single LLM output should not be trusted as-is.

**Structural error modes of LLM output**

1. **Arithmetic/aggregation errors:** Sequential token generation produces cumulative and double-counting errors in multi-step math (the 142% case).
2. **Arbitrary filling of rule gaps:** Models fill undefined boundary bands differently (LEI 50% vs 0%).
3. **Illusion of precision:** Many unverified figures create a false sense of reliability.
4. **Order sensitivity:** The same rule yields different results depending on application order (PLTR inversion).
5. **Non-determinism:** Re-running the same prompt at the same time can yield different results.
6. **Sycophancy bias:** LLMs tend to overrate the input strategy. As the external critique ([`ARDS_Defense_Critique.md`](result/ARDS_Defense_Critique.md)) notes, live risks such as slippage, latency, and overfitting are easily missed in a static review.

**Mitigation: Multi-LLM Cross-Validation**

One model's weakness can be offset by another. The key is separating a "convergence zone" from a "divergence zone."

- **Convergence zone (high confidence):** Conclusions both models agree on (Phase 1, Korea-US 50:50, Hanwha Aerospace / LIG Nex1 / LMT at the top, BBAI excluded) are adopted as robust signals.
- **Divergence zone (re-review):** Items the models split on (Composite value, individual weights, Boeing inclusion) require human re-verification.
- **Add a verification layer:** A self-critique / cross-critique loop where one model critiques another's output. The repository's `deepseek_markdown_...md` is a live example, where DeepSeek caught its own errors.
- **Deterministic post-processing:** Force arithmetic sums, the 100% weight check, and cap application to be verified by code, not the LLM.

**Recommended workflow**

```
[Run prompt on 2+ LLMs]
        |
[Auto-diff convergence vs divergence zones]
        |
[Divergence zone -> human or third-LLM re-verification]
        |
[Arithmetic / weight-sum / caps -> deterministic code check]
        |
[Black-swan stress test + reprice with conservative costs (2-3x)]
        |
[Small-size forward test, then live execution]
```

### 4.7 Prompt Improvement Proposals (v1.2 candidate)

1. **Unify between-threshold handling:** Specify "boundary band = 50%" consistently across all factors (filling the gaps in Factors B, D, E).
2. **Add a country-weight verification step:** After STEP 3.5, force a check that country weights sum to <= 100% and total 100%, and codify the country attribution of double-listed names (Hanwha Systems).
3. **Quantitative scoring rubric:** Give concrete criteria such as "FCF/revenue > 10% = full marks" for D3 to reduce subjective dispersion.
4. **Codify cap-application order:** "Apply caps in descending within-tier score order, then redistribute excess to the next name."

---

## STEP 5 — Risk Management

| Risk | Description |
|---|---|
| Geopolitical paradox | A ceasefire or de-escalation can crash defense names up to 30% |
| AI-defense valuation risk | PLTR, Anduril, BBAI trade on contract pipelines, extremely exposed to multiple compression when rates rise |
| K-defense export concentration | Heavy reliance on Poland, UAE, Saudi Arabia means revenue air-pockets on geopolitical shifts |
| Materials / supply-chain risk | High China dependence for rare earths, semiconductors, special alloys can disrupt production amid US-China friction |
| Opportunity cost of the Phase 4 rule | The AI-Defense 0% rule can cap upside if these names rebound during a downturn |
| Live-execution gap | Slippage, latency, and overfitting can make realized MDD several times larger than backtest (see external critique) |

---

## References

- ARDS original strategy: ARDS: Adaptive Recession-Defensive Strategy
- Multi-LLM comparison: `result/readme.md` (Claude vs DeepSeek cross-analysis)
- Self-critique feedback: `result/deepseek_markdown_20260524_371f74.md`
- Live-trading critique: `result/ARDS_Defense_Critique.md`

---

## Disclaimer

This material is an LLM-based simulation result for educational and research purposes only and is not a solicitation to buy or sell any security. All investment decisions and responsibility rest with the investor.

The defense sector reacts extremely sensitively to geopolitical events, so building an entire portfolio on this strategy alone is not recommended. Parallel operation with the original ARDS (defensive ETFs, bonds, gold) is strongly advised.

Even with the same prompt at the same moment, LLM outputs are non-deterministic and may differ on re-run. Do not rely on a single LLM output; always apply multi-LLM cross-validation and deterministic post-processing.
