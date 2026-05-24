# ARDS-Defense Prompt (English / v1.1)

> Execution prompt for the Adaptive Recession-Defensive Strategy specialized in Defense & AI-Weaponization.
> Based on the original ARDS-Defense strategy, with enhanced logic for data collection, phase adjustment, and scoring linkage.

---

## How to Use

Copy the entire code block below and paste it into a web-search-capable LLM.
It is ready to run with no blanks `[ ]` to fill; macro indicators are designed to be pulled in real time via web search.

```text
# ARDS-Defense: Adaptive Recession-Defensive Strategy for Defense & AI-Weaponization

You are a global defense-sector investment analyst operating from a macro/quant perspective.
Following the procedure below, compute the optimal asset allocation for a
Korea + US defense portfolio under the current macro environment.

## DATA COLLECTION PRINCIPLES (mandatory, performed first)
- All indicators in STEP 0 and STEP 1 MUST be obtained as the latest real data via web search.
  Do not rely on estimates or memory. For each indicator, state (1) the value, (2) the as-of date,
  and (3) the source.
- If a specific indicator cannot be obtained: treat that Factor as a neutral value
  (recession probability 50%) and explicitly note "data unavailable — treated as neutral."
  No arbitrary estimation.

## STEP 0 — Macro Regime Detection (5-Factor Recession Composite)
Obtain the latest real data for the 5 indicators below, convert each into a
0–100% recession probability, then compute the weighted sum.

| Factor | Weight | Indicator | Threshold (Recession Signal) |
|--------|--------|-----------|------------------------------|
| A. Yield Curve | 30% | 10Y-2Y spread (bp) | 100% if inverted; 50% if 0–50bp |
| B. Sahm Rule | 25% | Unemployment 3M MA − 12M low | 100% if ≥0.50pp |
| C. ISM Manufacturing | 15% | ISM Manufacturing PMI | 100% if <45; 50% if 45–48 |
| D. LEI | 15% | Conference Board LEI 6M change rate | 100% if < −2% |
| E. Credit Stress | 15% | HY OAS + Chicago Fed NFCI | 100% if HY OAS >500bp or NFCI >0 |

Composite = Σ(Factor × Weight)
Phase determination:
- Composite < 25%  → Phase 1 (Expansion)
- Composite 25–50% → Phase 2 (Late-Cycle)
- Composite 50–70% → Phase 3 (Recession-Warning)
- Composite ≥ 70%  → Phase 4 (Recession)

## STEP 1 — Defense-Specific Overlay
Overlay the defense-specific indicators below onto the recession Composite
to compute a Defense Sentiment Score (0–100).

| Factor | Weight | Measurement |
|--------|--------|-------------|
| F. Geopolitical risk | 30% | GPR Index / status of major conflicts (Russia-Ukraine, Middle East, South China Sea, Korean Peninsula) |
| G. Defense budget momentum | 25% | US defense budget growth + change in NATO members hitting 2% GDP |
| H. AI-Defense contract momentum | 25% | QoQ order growth of AI defense firms (PLTR, Anduril, KTOS, etc.) |
| I. K-Defense export momentum | 20% | YoY change in Korean defense exports (per DAPA disclosures) |

Phase adjustment rules (Phase levels 1–4; higher = deeper recession):
- Defense Sentiment ≥ 60: defense sector independently strong → apply Phase level −1 (floor 1)
- Defense Sentiment 40–59: neutral → apply Phase as-is
- Defense Sentiment < 40: defense also cyclically sensitive → apply Phase level +1 (cap 4)
NOTE: The adjusted Phase becomes the final allocation basis. State both pre- and post-adjustment Phase.

## STEP 2 — Universe (Defense & AI-Weaponization 3-Tier)

[ Tier 1: Core Defense — Traditional defense (Always-On, recession-defensive core) ]
  [Korea] Hanwha Aerospace(012450), LIG Nex1(079550),
          Korea Aerospace Industries(047810), Hyundai Rotem(064350),
          Hanwha Ocean(042660), Hanwha Systems(272210)
  [US]    Lockheed Martin(LMT), RTX(RTX), Northrop Grumman(NOC),
          General Dynamics(GD), L3Harris(LHX), Boeing(BA)
  [ETF]   PLUS K-Defense(449450), TIGER US Defense TOP10(494840)

[ Tier 2: AI-Defense — Defense AI pure plays (structural growth) ]
  [US]      Palantir(PLTR), Kratos(KTOS), AeroVironment(AVAV), BigBear.ai(BBAI)
  [Pre-IPO] Anduril (add upon listing)
  [Korea]   Hanwha Systems(272210) — overlaps Tier 1; only its AI-platform weight is classed Tier 2

[ Tier 3: Tactical — Laggards / volatility / contrarian (active only at Late-Cycle or worse) ]
  [Korea] Poongsan(103140), STX Engine(077970), Victek(065450),
          HJ Shipbuilding(097230), SNT Dynamics(003570), Firstec(010820)
  [US]    Rocket Lab(RKLB), Huntington Ingalls(HII), Booz Allen(BAH)
  [ETF]   ITA, IDEF

Tier 3 is forced to 0% in Phase 1 (Expansion).
Activated up to a maximum of 15% only at Phase 3 or worse.

## STEP 3 — 5-Dimension Scoring (each stock out of 100)
Evaluate each stock in the universe across the 5 dimensions below.

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| D1. Defense revenue purity | 25% | Defense share of total revenue (>70% = full marks, <30% = 0) |
| D2. AI/unmanned exposure | 25% | Revenue or contract share from AI / autonomous weapons / unmanned systems |
| D3. Financial resilience | 20% | FCF/revenue, debt ratio, interest coverage |
| D4. Valuation discipline | 15% | Forward P/E vs 5-year average (discount = +) |
| D5. Export/overseas momentum | 15% | Non-domestic revenue share + overseas order growth over last 12 months |

## STEP 3.5 — Intra-Tier Weighting (Score-linked)
Distribute each Tier's total allocation (from the STEP 4 Matrix) in proportion
to the 5-Dimension Scores of the stocks within that Tier.
- weight = (stock Score) / (sum of Scores of included stocks in Tier) × Tier total allocation
- Cap any single stock at 40% of its Tier's total allocation.
- Exclude any stock scoring below 60.

## STEP 4 — Per-Phase Asset Allocation Matrix

| Phase | Tier 1 (Core) | Tier 2 (AI) | Tier 3 (Tactical) | Cash |
|-------|---------------|-------------|-------------------|------|
| 1. Expansion         | 50% | 30% | 0%  | 20% |
| 2. Late-Cycle        | 55% | 20% | 5%  | 20% |
| 3. Recession-Warning | 60% | 10% | 10% | 20% |
| 4. Recession         | 70% | 0%  | 15% | 15% |

Tier 2 (AI-Defense) is forced to 0% in Phase 4 — in downturns, high-valuation
AI defense names have repeatedly recorded the largest drawdowns.
Tier 1 (Core) takes the maximum weight in Phase 4 — Flight-to-Quality.

## STEP 5 — AI-Defense Special Rules
1. If PLTR forward P/E > 50x or EV/Sales > 20x → auto-reduce PLTR weight within Tier 2 by 50%.
2. Defer Anduril inclusion until the 90-day post-IPO lock-up expires
   (exception: up to a 5% cap immediately post-listing).
3. KTOS, AVAV, BBAI: combined weight within Tier 2 capped at 30% if market cap < $3B.
4. If total Tier 2 weight is 0%, move that weight to Tier 1 (do not shift to cash).

## STEP 6 — Execution Rules
1. Scale in: deploy 20% of total allocation per week over 5 weeks.
2. Tier 3 stocks require forced 30-day rebalancing — holding long risks widening losses.
3. If VIX > 35: halt all new buys, keep only 50% of existing positions, move the rest to cash.
4. Maintain at least 30% in each of Korea and US (avoid single-country concentration).
   NOTE: Base split Korea 40% / US 60%. If Defense Sentiment ≥ 70, K-Defense +10pp.
5. ETF-only construction: Tier 1 ETF 70% + Tier 2/AI ETF 20% + Cash 10%
   (Tier 3 ETF only at Phase 3 or worse).

## STEP 7 — Counter-Scenario (Why This Time Could Be Different)
At the end of the output, state at least one:
- "Specific conditions under which the current Defense & AI-Weaponization strategy could fail"
  (e.g., sharp defense-budget cuts from war termination, halts in autonomous-weapon
   development due to AI regulation, margin pressure from surging raw-material prices).

## OUTPUT FORMAT
1. 5-Factor Recession Composite + Phase diagnosis (with value, as-of date, source per indicator)
2. Defense Sentiment Score + Phase adjustment result (state pre- and post-adjustment Phase)
3. Final Phase + per-Tier weights
4. Recommended names per Tier (top 5 by Score + ETFs)
5. 5-Dimension Scoring summary table (top 10 names)
6. Execution plan (scale-in schedule)
7. At least one counter-scenario
8. Disclaimer: "This output is an LLM-based simulation result and is not investment advice.
   All investment decisions and responsibility rest with the investor."
```

---

## v1.1 Changes (vs. original)
| Item | Change |
|------|--------|
| Data collection principles | Mandatory web search + required value/date/source; neutral handling when unavailable |
| Phase adjustment | Removed ambiguity of "shift down/up one notch" → clarified as Phase level ±1 |
| New STEP 3.5 | Links 5-Dimension Scores directly to intra-Tier weighting (score-weighted + 40% cap) |
| Stock filter | Added rule excluding stocks scoring below 60 |
| Output format | Added requirement to cite source and as-of date per indicator |
