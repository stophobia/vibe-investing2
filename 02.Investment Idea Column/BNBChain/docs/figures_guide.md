# Figures Insertion Guide

This document specifies the location, recommended caption, and academic value of each of the 7 figures in the paper. Figures are numbered in **body-appearance order** (Figure 1 appears first in the paper, Figure 7 last).

---

## Figure 1 — Foundation Break-Even Region

**File**: `figures/Chart5_BreakEvenRegion.png` (or `.pdf`)

**Insertion Location**: Section 4.7 — *Theorem 6 (Foundation Break-Even Impossibility)*, after the proof

**Recommended Caption**:
> **Figure 1.** Foundation break-even region in the (α, d) parameter space, holding θ = 0.40 fixed. The colored heatmap shows foundation cost C/FDV ranging from −40% (deep green, profit) to +60% (deep red, loss). The solid black curve marks the break-even contour (C = 0), defined by d* = −α/(1−α−θ). The Megadrop typical operating range (α = 5–8%, d ≈ 44%, dashed blue rectangle) falls deeply in the loss region, with the Megadrop average (orange circle: α = 7.3%, d = 44%, C = 30.5% FDV) located 58.3 percentage points below the break-even contour. HODLer (α = 2–3%) and Direct (α ≈ 0%) ranges are also annotated.

**Academic Value**: ★★★ — Mathematical model visualization. Aggregates Section 4.10 scenario analysis (Tables 4.1–4.3) into one figure.

---

## Figure 2 — Bootstrap 95% CI Forest Plot

**File**: `figures/Chart1_ForestPlot.png`

**Insertion Location**: Section 6.2.1 — *Bootstrap 95% Confidence Intervals*, immediately after Table 6.1

**Recommended Caption**:
> **Figure 2.** Forest plot of category-wise 1-year+ BTC-relative returns with bootstrap 95% confidence intervals (N = 10,000 iterations, sample N = 21 tokens). Distribution mechanism categories (Megadrop, HODLer, Launchpool) cluster in the loss region; Direct categories (with and without HYPE inclusion) cluster in the gain region. Filled circles denote arithmetic means; open diamonds denote geometric means. The dramatic shift in the Direct (Diversified, N=3) row — from arithmetic mean +81.5% to +384.3% — illustrates the impact of HYPE integration on Cohen's d normalization (from −10.67 to −1.52, see Section 6.2.3).

**Academic Value**: ★★★★★ — Visual evidence of HYPE integration's effect on Cohen's d normalization (key external evaluation recommendation).

---

## Figure 3 — HYPE Counterfactual Trajectory

**File**: `figures/Chart4_HYPE_Counterfactual.png`

**Insertion Location**: Section 6.2.7 — *Hyperliquid (HYPE) — True Non-CEX Direct Case Verification*, after the HYPE Price Trajectory table

**Recommended Caption**:
> **Figure 3.** Counterfactual evidence for the distribution mechanism effect on token prices. Hyperliquid HYPE (zero CEX distribution, zero VC allocation, DeFi infrastructure category) appreciated approximately 925–1,054% over 1+ years post-listing, while Megadrop tokens (α = 5–8% distribution) declined by an average of 76%. HODLer tokens (α = 2–3%) declined by an average of 20%. Direct memecoin tokens (WIF, PEPE) appreciated by an average of 81%. The qualitative direction of the distribution mechanism effect is supported, though HYPE alone (N = 1) cannot establish statistical generalization. Indexed to listing date (T-0 = 100).

**Academic Value**: ★★★★ — Counterfactual evidence reflecting external evaluation's *Memecoin bias mitigation* recommendation. 4 series comparison shows distribution mechanism *grade*.

---

## Figure 4 — BNB Chain Decoupling Pattern

**File**: `figures/Chart2_Decoupling.png`

**Insertion Location**: Section 7.4 — *Revised Model — Partial Self-Cannibalizing Loop + Decoupling*, after introducing the revised model

**Recommended Caption**:
> **Figure 4.** BNB Chain macro-activity (trading volume, DeFi TVL, BNB price, active wallets) versus Megadrop category market capitalization, indexed to Q1 2025 = 100. While BNB Chain macro indicators trend upward (+102% to +171% across Q1–Q3 2025), the Megadrop category market cap declines by approximately 75%. This pattern illustrates the time-series decoupling described in Section 7.3, but does not establish causality (see Limitation 6: full Granger causality testing requires daily data, deferred to subsequent versions). Sources: Messari "State of BNB" Q1–Q3 2025 reports, author estimates for Megadrop category.

**Academic Value**: ★★★★ — Most intuitive decoupling visualization. *4 ascending lines vs 1 descending line* contrast.

---

## Figure 5 — Decoupling Domains Diagram

**File**: `figures/Diagram2_DecouplingDomains.png`

**Insertion Location**: Section 7.4 — Immediately after Figure 4

**Recommended Caption**:
> **Figure 5.** Revised model illustrating partial self-cannibalizing loop within the Megadrop category alongside opposite-direction trends in BNB Chain macro-activity. The Megadrop impact domain (left, red) follows a five-step degradation: enhanced holder benefits → 5%+ distribution → selling pressure → 44% average loss → category market cap collapse. The BNB Chain macro domain (right, green) is driven by separate dynamics — Binance Alpha trading volume, PancakeSwap V4, Aster Perp DEX — yielding +63.7% growth and BNB price ATH at $1,369 (Q4 2025). The two domains exhibit time-series patterns in opposite directions; causal independence requires Granger testing in subsequent versions (see Limitation 6).

**Academic Value**: ★★★★ — Conceptual diagram complementing Figure 4 (empirical chart). *Model + Data* dual structure.

---

## Figure 6 — Three-Actor Differential Impact

**File**: `figures/Chart3_ThreeActor.png`

**Insertion Location**: Section 7.6 — *Three-Actor Quantitative Comparison* (or Section 10.3)

**Recommended Caption**:
> **Figure 6.** Three-actor differential impact of centralized exchange airdrops (2024–2025). **Panel A**: Base scenario absolute monetary values — BNB holders gain $1.69B, issuing foundations lose $4.80B, BNB Chain market cap grows $104B. The foundation loss is 2.84× the holder gain (asymmetry visible at absolute scale) but only 4.6% of BNB Chain market cap growth (decoupling pattern). **Panel B**: Sensitivity across five scenarios varying realization rate (40%–85%), average FDV ($200M–$600M), and listing count (40–100). The Foundation/Holder ratio remains ≥1.5× across all scenarios, confirming robustness of the asymmetry conclusion.

**Academic Value**: ★★★★ — Dual-panel structure delivers *base + sensitivity* simultaneously. Scale difference shows decoupling visually.

---

## Figure 7 — Mathematical Causal Chain

**File**: `figures/Diagram1_Causal_Chain.png`

**Insertion Location**: Section 10.1 — *Mathematical Causal Chain of This Study — Visual Synthesis*

**Recommended Caption**:
> **Figure 7.** Mathematical Causal Chain of Distribution Asymmetry. The seven theorems in Section 4 integrate into a unified derivation: distribution ratio α serves as input (Theorems 1–2), produces the foundation cost function (Theorems 3–5), proves break-even impossibility (Theorem 6), establishes the immediate sell-off Nash equilibrium (Theorem 7), and is verified via three robustness analyses (Sections 4.10, 4.11, 4.8.1) before reaching the three-actor asymmetry output. R = 4.18 for Megadrop, R = 12.66 for HODLer, value destruction D = 23.1% FDV.

**Academic Value**: ★★★★★ — Visual synthesis at the conclusion of the paper, ideal as a closing summary visual. Allows reviewers to grasp the seven-theorem integration in 5 seconds.

---

## File Naming Convention

The Python source files in `scripts/` retain their original names (referencing the *generation order* during paper development) for traceability with the analysis history:

| Figure (final) | Image file | Generation script |
|----------------|------------|-------------------|
| Figure 1 | `Chart5_BreakEvenRegion.{png,pdf}` | `generate_figure3_breakeven_region.py` |
| Figure 2 | `Chart1_ForestPlot.{png,pdf}` | `generate_figure2_forest_plot.py` |
| Figure 3 | `Chart4_HYPE_Counterfactual.{png,pdf}` | `generate_figure4_hype_counterfactual.py` |
| Figure 4 | `Chart2_Decoupling.{png,pdf}` | `generate_figure5_decoupling.py` |
| Figure 5 | `Diagram2_DecouplingDomains.{png,pdf}` | `generate_figure6_decoupling_domains.py` |
| Figure 6 | `Chart3_ThreeActor.{png,pdf}` | `generate_figure7_three_actor.py` |
| Figure 7 | `Diagram1_Causal_Chain.{png,pdf}` | `generate_figure1_causal_chain.py` |

The mismatch between figure number and file name (e.g., Figure 1 = `Chart5_*`) reflects the *historical development sequence*, where figures were created in priority order (Diagram 1 = causal chain was the first conceptual deliverable). The body-appearance order (Figure 1 → 7) was finalized in v1.2.

---

## Insertion Priority Summary

### Required for SSRN submission
1. **Figure 7** (Causal Chain) — Section 10.1 visual synthesis at paper conclusion
2. **Figure 5** (Decoupling Domains) — Section 7.4 conceptual diagram
3. **Figure 2** (Forest Plot) — Section 6.2.1 bootstrap CI

### Strongly recommended (academic value enhancement)
4. **Figure 4** (Decoupling Chart) — Section 7.4 empirical pattern
5. **Figure 6** (Three-Actor) — Section 7.6 quantitative impact
6. **Figure 3** (HYPE Counterfactual) — Section 6.2.7 alternative case

### Recommended (mathematical model strengthening)
7. **Figure 1** (Break-Even Region) — Section 4.7 parameter space heatmap

---

## File Format

Each figure is provided in *PNG (200 DPI) + PDF* format.

- **PNG**: For Microsoft Word insertion (recommended for DOCX editing)
- **PDF**: For LaTeX conversion or academic journal submission (preserves vector graphics)

---

## Reproducibility

All figures can be regenerated by running the scripts in `scripts/` directory:

```bash
cd scripts/
for f in generate_figure*.py; do python "$f"; done
```

Output files are saved to `../figures/`.
