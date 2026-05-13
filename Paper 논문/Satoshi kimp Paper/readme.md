# The Bithumb–Binance BTC-numéraire Premium — Trilingual Edition

A Theoretical Framework with Calibrated Simulation Evidence on BNB Chain Tokens

**김호광 / Ho-Kwang Kim** — Betalabs Inc., former CEO of Cyworld Z
*2017년부터 Blockchain · Web3 사업과 개발을 수행한 실무 경험자*
ORCID: https://orcid.org/0009-0002-0962-2175
Repository: https://github.com/gameworkerkim/vibe-investing

## Three language editions

| Language | PDF | LaTeX source | Pages | Engine |
|----------|-----|--------------|-------|--------|
| Korean (한국어) | `ko/paper.pdf` | `ko/paper.tex` | 19 | XeLaTeX + xeCJK + Noto Serif CJK KR |
| English | `en/paper_en.pdf` | `en/paper_en.tex` | 21 | XeLaTeX + Latin Modern Roman |
| Chinese (中文) | `zh/paper_zh.pdf` | `zh/paper_zh.tex` | 18 | XeLaTeX + xeCJK + Noto Serif CJK SC |

All three editions share identical content: 11 figures (English-labeled,
in `figures/`), the same 15 data CSVs (in `data/`), the same equations,
and the same paper structure (Abstract, §1 Introduction, §2 Literature,
§3 Theory, §4 Hypotheses, §5 Data & Methodology, §6 Empirical Results
with subsections 6.1–6.5, §7 Discussion, §8 Limitations & Agenda,
§9 Conclusion, Appendix A, References).

## How to compile each edition

```bash
# Korean
cd ko && xelatex paper.tex && xelatex paper.tex

# English
cd en && xelatex paper_en.tex && xelatex paper_en.tex

# Chinese (requires Noto Serif/Sans CJK SC fonts)
cd zh && xelatex paper_zh.tex && xelatex paper_zh.tex
```

## Localisation notes

**Figures.** All three editions share English-labeled figures
(`figures/`). Chinese academic finance papers typically use English
labels for technical financial terms (BTC-numéraire, OLS, EGARCH, etc.),
following international convention; this also keeps figure reproducibility
identical across editions.

**Chinese edition standardised term mappings:**
- 김치 프리미엄 → 泡菜溢价 (kimchi premium)
- 사토시 김프 → 比特币本位溢价 / satoshi 溢价
- BTC-numéraire → BTC本位
- 빗썸 → Bithumb；바이낸스 → 币安 (Binance)
- 자본통제 → 资本管制
- 트래블룰 → Travel Rule
- 정규화 분산 비율 → 标准化方差比
- EGARCH 레버리지 → 杠杆项

## Standing caveats (apply to all three editions)

1. **Synthetic data caveat** — all CSVs calibrated to literature stylized
   facts (Appendix A). Empirical submission requires real exchange API data.

2. **Modeling assumption caveat** — non-Korean exchange spreads modeled
   as pure AR(1) microstructure noise (Appendix A core assumption).

3. **Policy-cost caveat** — KCS-detected 14.2 trillion KRW (2018–2025
   cumulative) and 2.04 trillion KRW (2024–2025 partial) treated as
   lower-bound indicators; not all detected illegal forex is
   kimchi-arbitrage-driven.
