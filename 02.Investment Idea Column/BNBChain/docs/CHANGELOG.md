# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-05-01

### Fixed (Critical)
- **Section 5.2 correlation values**: Replaced incorrect Pearson coefficients with correct values from `correlation_results.txt`:
  - BTC-ETH: 0.7831 → 0.6769 (p: 0.0125 → 0.0452, * unchanged)
  - BTC-BNB: 0.8518 → 0.6617 (p: 0.0036 → 0.0522, ** → n.s. marginal)
  - ETH-BNB: 0.8362 → 0.8518 (p: 0.0050 → 0.0036, ** unchanged)
- **Section 5.2 Observation**: Rewrote interpretation to reflect ETH-BNB (not BTC-BNB) as the strongest correlation, supporting the alt season hypothesis (H1)
- **Section 5.4 BTC dominance direction**: Corrected reversed direction error — 25.47% BNB outperformance occurs during BTC dominance *decline* phases, not *increase* phases. Added explicit Mann-Whitney U test results (U = 14.00, p = 0.0714)

### Changed
- **Figure renumbering to body-appearance order**: Figures now appear sequentially as 1, 2, 3, 4, 5, 6, 7 in the paper
  - Figure 1 (was Figure 3): Foundation Break-Even Region — Section 4.7
  - Figure 2 (unchanged): Forest Plot — Section 6.2.1
  - Figure 3 (was Figure 4): HYPE Counterfactual — Section 6.2.7
  - Figure 4 (was Figure 5): Decoupling Chart — Section 7.4
  - Figure 5 (was Figure 6): Decoupling Domains Diagram — Section 7.4
  - Figure 6 (was Figure 7): Three-Actor Impact — Section 7.6
  - Figure 7 (was Figure 1): Mathematical Causal Chain — Section 10.1
- Updated `docs/figures_guide.md` to reflect new numbering with file-to-figure mapping table
- Image files retain original names (e.g., `Diagram1_Causal_Chain.png` is now Figure 7) for development history traceability

## [1.0.0] - 2026-05-01

### Added
- Initial GitHub release with full reproducibility package
- 7 publication-grade figures (PNG + PDF) generated from Python source
- DOCX with embedded figures and academic captions
- 4 CSV data files with verified sources
- 4 analysis scripts + 7 figure generation scripts (all English)
- MIT (code) + CC BY 4.0 (data/paper) dual licensing
- CITATION.cff for academic citation support
- Comprehensive README with reproducibility instructions
- Data dictionary and figures insertion guide

### Notable Methodology
- Bootstrap 95% CI with N=10,000 iterations
- Hyperliquid HYPE counterfactual case included (Direct N=2 → N=3)
- Cohen's d normalized from -10.665 (artifact, N=2) to -1.519 (N=3 with HYPE)
- Three-actor differential impact analysis ($1.69B holder gain, $4.80B foundation loss, $104B BNB Chain market cap growth)
- Decoupling pattern observation with explicit causality non-establishment

## Pre-release Versions (Internal Development)

### [v0.5] - 2026-04-28
- Korean-language draft completed (~9,600 words)
- N=18 token sample without HYPE
- Bootstrap CI calculated for N=18 sample
- Cohen's d Megadrop vs Direct (N=2) = -10.665 (flagged as artifact)
- External academic evaluation requested

### [v0.4] - 2026-04-25
- Theorem 6 (Foundation Break-Even Impossibility) proof completed
- Theorem 7 (Nash Equilibrium) proof completed
- Section 4.10 scenario analysis added (α 2-15%, θ 30-60%, d 10-90%)

### [v0.3] - 2026-04-22
- Section 7 BNB Chain decoupling pattern observed
- Messari Q1-Q3 2025 data integration

### [v0.2] - 2026-04-18
- Theorems 1-5 (Foundation Cost Function) developed
- Megadrop, HODLer, Launchpool category definitions

### [v0.1] - 2026-04-15
- Initial concept: distribution mechanism asymmetry hypothesis
- Companion to SSRN 6632838 ("The 72-Hour Shock")

## Roadmap (Subsequent Versions)

### [v1.1] (planned)
- Expanded sample to N≥50 tokens
- Daily OHLCV data integration via CoinGecko/Binance APIs
- Real Granger causality testing (Section 7 limitation 6 resolution)

### [v2.0] (planned)
- Sample size N≥100
- Propensity Score Matching (PSM) for selection bias
- Heckman 2-step estimation
- Multi-exchange comparison (Bybit, OKX, Coinbase listings)
- LaTeX paper compilation for journal submission

## Citation Note

For academic citation, please use the metadata in [CITATION.cff](CITATION.cff)
or the BibTeX template in the [README.md](README.md).

When citing v1.0 specifically, please use:
> Kim, H. (2026). Distribution Asymmetry of Centralized Exchange Airdrops and the
> BNB Chain Ecosystem (v1.0) [Preliminary working paper and dataset]. GitHub.
> https://github.com/gameworkerkim/distribution-asymmetry-cex-airdrops
