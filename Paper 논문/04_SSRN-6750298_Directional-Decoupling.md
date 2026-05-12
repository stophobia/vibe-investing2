---
ssrn_id: 6750298
title: "Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 – April 2026"
title_ko: "방향성 디커플링 — BNB-ETH 페어에서 변동성 비율 채널에 의한 베타 압축 (2022.05–2026.04)"
short_title: "Directional Decoupling"
authors:
  - family: Kim
    given: HoKwang
    given_ko: 호광
    alias: Dennis Kim
    affiliation: "Betalabs Inc."
    orcid: "0009-0002-0962-2175"
    corresponding: true
doi: "10.2139/ssrn.6750298"
url: "https://ssrn.com/abstract=6750298"
canonical_url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6750298"
ssrn_author_id: 11276088
posted_date: "2026-05-12"
language: "en"
pages: 28
type: "preprint"
publisher: "SSRN"
license: "CC-BY-4.0"
data_availability: "Public — daily price data from public exchanges"
funding: "This research received no external funding."
keywords:
  - "beta decomposition"
  - "volatility ratio"
  - "directional decoupling"
  - "BNB"
  - "Ethereum"
  - "cryptocurrency"
  - "DCC-GARCH"
  - "variance decomposition"
  - "rolling beta"
  - "correlation"
  - "Pearson correlation"
keywords_ko:
  - "베타 분해"
  - "변동성 비율"
  - "방향성 디커플링"
  - "BNB"
  - "이더리움"
  - "암호화폐"
  - "DCC-GARCH"
  - "분산 분해"
  - "롤링 베타"
  - "상관관계"
  - "피어슨 상관"
jel_codes: ["G12", "G14", "G15", "C58"]
acm_classification: []
mesh_terms: []
github_repo: "https://github.com/gameworkerkim/vibe-investing"
related_papers: ["10.2139/ssrn.6632838", "10.2139/ssrn.6688740"]
---

# Directional Decoupling

> **Subtitle**: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 – April 2026

**SSRN Working Paper No. 6750298** · DOI: [10.2139/ssrn.6750298](https://doi.org/10.2139/ssrn.6750298) · Posted: 2026-05-12

[![SSRN](https://img.shields.io/badge/SSRN-6750298-1A5F7A)](https://ssrn.com/abstract=6750298)
[![DOI](https://img.shields.io/badge/DOI-10.2139%2Fssrn.6750298-blue)](https://doi.org/10.2139/ssrn.6750298)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--0962--2175-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0002-0962-2175)
[![Pages](https://img.shields.io/badge/Pages-28-informational)]()

---

## Author

**HoKwang Kim (Dennis Kim, 김호광)** — Betalabs Inc.
ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175) · Email: gameworker@gmail.com

---

## English

### Abstract

This paper documents a striking instance of *channel-specific beta change* in cryptocurrency markets that we term **directional decoupling** (equivalently, *volatility-ratio-driven beta compression*): a beta decline accompanied by an *unchanged* Pearson correlation, with all of the beta movement attributable to volatility-ratio compression rather than to weakened co-movement. Using daily price data on **BNB and ETH from May 2022 to April 2026**, BNB's static beta to ETH falls by **16.9%** (from 0.643 to 0.534) while the Pearson correlation remains essentially unchanged (**0.731 → 0.731**). A formal variance decomposition reveals that **100% of the beta change is attributable to the volatility-ratio channel**, with no contribution from correlation. The pattern is robust to DCC-GARCH dynamic-conditional-beta specifications (which yield a smaller but directionally consistent beta decline of −5.84%). We argue that the popular media label "decoupling" is, on this evidence, technically imprecise: BNB and ETH continued to move directionally in lock-step throughout the sample; what changed was their relative amplitude, not their direction.

### Significance (Why This Paper Matters)

Three contributions distinguish this paper:

1. **Formal decomposition of beta into the correlation channel vs. volatility-ratio channel.** Static OLS beta can be written as $\beta = \rho \cdot \sigma_X / \sigma_Y$. Most existing literature interprets a beta decline as evidence of weakening co-movement. This paper provides a *variance-decomposition framework* to rigorously distinguish *correlation-driven* from *volatility-ratio-driven* beta changes, showing they have very different economic interpretations.
2. **A new terminology — "directional decoupling" — that disambiguates a widely-used but imprecise market term.** Market commentary frequently describes any beta decline as "decoupling." This paper shows that for BNB-ETH, the more accurate description is "amplitude compression with preserved directional co-movement." The term *directional decoupling* (or, more precisely, *volatility-ratio-driven beta compression*) captures this distinction.
3. **A robustness-first methodology applicable to other exchange-native vs. base-layer token pairs.** The framework extends naturally to FTT-ETH (historical), OKB-ETH, KCS-ETH, and similar pairings. Section 5 of the paper outlines this extension.

### Methodology (One-Paragraph Summary)

Using daily log returns $r_{BNB,t}$ and $r_{ETH,t}$ over the period 2022-05 to 2026-04, we partition the sample at a chosen date (early 2024) and estimate static OLS beta separately in the pre and post sub-samples: $r_{BNB,t} = \alpha + \beta \cdot r_{ETH,t} + \epsilon_t$. Using the decomposition $\beta = \rho \cdot \sigma_{BNB}/\sigma_{ETH}$, we attribute $\Delta\beta = \beta_{post} - \beta_{pre}$ to a *correlation channel* and a *volatility-ratio channel* via a first-order log-linearization. Robustness includes DCC-GARCH dynamic conditional beta, rolling-window estimation (252-day window), and partition-date sensitivity (testing alternate breakpoints). All channels and robustness specifications agree on the qualitative pattern.

### Key Numbers

| Metric | Pre-period | Post-period | Δ | Channel attribution |
|---|---|---|---|---|
| Static OLS beta $\beta$ | 0.643 | 0.534 | **−16.9%** | — |
| Pearson correlation $\rho$ | 0.731 | 0.731 | ≈ 0% | Correlation channel: **0%** |
| Vol-ratio $\sigma_{BNB}/\sigma_{ETH}$ | (high) | (low) | (declined) | Vol-ratio channel: **100%** |
| DCC dynamic beta $\bar\beta_t$ | 0.575 | 0.541 | −5.84% | Direction-consistent |

### Keywords

`beta decomposition` · `volatility ratio` · `directional decoupling` · `BNB` · `Ethereum` · `DCC-GARCH` · `variance decomposition` · `rolling beta` · `correlation` · `cryptocurrency`

### JEL Classification

- **G12** — Asset Pricing; Trading Volume; Bond Interest Rates
- **G14** — Information and Market Efficiency
- **G15** — International Financial Markets
- **C58** — Financial Econometrics

---

## 한국어 (Korean)

### 초록

본 논문은 암호화폐 시장에서 *채널 특이적 베타 변화* 의 두드러진 사례를 문서화한다 — 우리는 이를 **방향성 디커플링(directional decoupling)** (또는 등가적으로, *변동성 비율 채널에 의한 베타 압축*) 으로 명명한다 — *피어슨 상관계수가 변하지 않은 채로* 베타가 하락하며, 베타 변화의 *전량이 변동성 비율 압축에 귀속되고 동조성 약화는 기여하지 않는* 패턴이다. **2022년 5월 ~ 2026년 4월** 의 BNB·ETH 일별 가격 자료를 사용해, BNB 의 ETH 에 대한 정적 OLS 베타가 **0.643 → 0.534 로 16.9% 하락** 한 반면, 피어슨 상관은 **0.731 → 0.731 로 사실상 변화 없음** 을 확인했다. 공식적인 *분산 분해* 결과, **베타 변화의 100% 가 변동성 비율 채널에 귀속되며, 상관관계 채널의 기여는 0%** 다. 패턴은 DCC-GARCH 동적 조건부 베타 명세 (−5.84% 의 더 작지만 방향 일치하는 베타 하락) 하에서도 유지된다. 본 논문은 시장에서 통용되는 "디커플링" 이라는 명명이 본 증거에 비추어 *기술적으로 부정확함* 을 주장한다 — BNB 와 ETH 는 표본 기간 내내 *방향성 측면에서는 동조* 했고, 변한 것은 *방향이 아닌 진폭의 상대적 크기* 이다.

### 연구의 의의

본 논문의 세 가지 기여:

1. **베타를 *상관관계 채널* 과 *변동성 비율 채널* 로 형식적으로 분해.** 정적 OLS 베타는 $\beta = \rho \cdot \sigma_X / \sigma_Y$ 로 표현된다. 기존 문헌 대부분은 베타 하락을 *동조성 약화* 의 증거로 해석한다. 본 논문은 *분산 분해 프레임워크* 를 통해 *상관관계 주도* 베타 변화와 *변동성 비율 주도* 베타 변화를 엄밀히 구분하며, 두 패턴이 *경제적 의미가 매우 다름* 을 보인다.
2. **"방향성 디커플링" 이라는 새로운 용어로, 시장에서 광범위하게 쓰이는 부정확한 표현을 명확히 한다.** 시장 평론은 *모든 베타 하락* 을 "디커플링" 으로 묘사한다. 본 논문은 BNB-ETH 의 경우 더 정확한 묘사가 *"방향성 동조 유지 + 진폭 압축"* 임을 보인다. *directional decoupling*(또는 더 엄밀하게는 *volatility-ratio-driven beta compression*) 이라는 용어가 이 차이를 포착한다.
3. **다른 *거래소 네이티브 토큰 vs. 베이스 레이어 토큰* 페어에 자연스럽게 확장 가능한 robustness-first 방법론.** 프레임워크는 FTT-ETH(과거), OKB-ETH, KCS-ETH 등의 페어로 자연 확장된다. 논문 5절이 이 확장 방안을 제시한다.

### 방법론 (한 문단 요약)

2022-05 ~ 2026-04 기간의 BNB·ETH 일별 로그수익률 $r_{BNB,t}$, $r_{ETH,t}$ 를 사용해 표본을 분기 시점(2024년 초) 에서 분할하고, 정적 OLS 베타를 사전·사후 부표본 각각에서 추정한다: $r_{BNB,t} = \alpha + \beta \cdot r_{ETH,t} + \epsilon_t$. 분해식 $\beta = \rho \cdot \sigma_{BNB}/\sigma_{ETH}$ 를 이용해 $\Delta\beta = \beta_{post} - \beta_{pre}$ 를 *상관관계 채널* 과 *변동성 비율 채널* 로 1차 로그선형화 통해 귀속시킨다. 견고성 검사는 DCC-GARCH 동적 조건부 베타, 롤링 윈도우 추정(252일), 분기 시점 민감도 분석(대안 분기점 검증) 을 포함한다. 모든 채널과 견고성 명세는 *질적 패턴* 에서 일치한다.

### 주요 수치

| 지표 | 사전기간 | 사후기간 | Δ | 채널 귀속 |
|---|---|---|---|---|
| 정적 OLS 베타 $\beta$ | 0.643 | 0.534 | **−16.9%** | — |
| 피어슨 상관 $\rho$ | 0.731 | 0.731 | ≈ 0% | 상관관계 채널: **0%** |
| 변동성 비율 $\sigma_{BNB}/\sigma_{ETH}$ | (높음) | (낮음) | (하락) | 변동성 비율 채널: **100%** |
| DCC 동적 베타 $\bar\beta_t$ | 0.575 | 0.541 | −5.84% | 방향 일치 |

### 키워드

`베타 분해` · `변동성 비율` · `방향성 디커플링` · `BNB` · `이더리움` · `DCC-GARCH` · `분산 분해` · `롤링 베타` · `상관관계` · `암호화폐`

---

## Citation Formats

### BibTeX

```bibtex
@misc{kim2026_decoupling,
  author    = {Kim, HoKwang},
  title     = {Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the
               {BNB}-{ETH} Pair, May 2022 -- April 2026},
  year      = {2026},
  month     = may,
  publisher = {SSRN},
  doi       = {10.2139/ssrn.6750298},
  url       = {https://ssrn.com/abstract=6750298},
  note      = {SSRN Working Paper No.~6750298}
}
```

### RIS

```
TY  - GEN
T1  - Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 - April 2026
AU  - Kim, HoKwang
PY  - 2026
DA  - 2026/05/12
PB  - SSRN
DO  - 10.2139/ssrn.6750298
UR  - https://ssrn.com/abstract=6750298
KW  - beta decomposition
KW  - volatility ratio
KW  - directional decoupling
KW  - BNB
KW  - Ethereum
KW  - DCC-GARCH
N1  - SSRN Working Paper No. 6750298
ER  -
```

### APA (7th edition)

> Kim, H. (2026). *Directional decoupling: Volatility-ratio-driven beta compression in the BNB-ETH pair, May 2022 – April 2026* (SSRN Working Paper No. 6750298). SSRN. <https://doi.org/10.2139/ssrn.6750298>

### MLA (9th edition)

> Kim, HoKwang. "Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 – April 2026." *SSRN*, 12 May 2026, doi:10.2139/ssrn.6750298.

### Chicago (Author-Date)

> Kim, HoKwang. 2026. "Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 – April 2026." SSRN Working Paper No. 6750298. <https://doi.org/10.2139/ssrn.6750298>.

### Korean (한국어 인용)

> 김호광 (2026). 「방향성 디커플링 — BNB-ETH 페어에서 변동성 비율 채널에 의한 베타 압축 (2022.05–2026.04)」. *SSRN Working Paper* No. 6750298. <https://doi.org/10.2139/ssrn.6750298>

---

## Machine-Readable Metadata (JSON-LD, schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "Directional Decoupling: Volatility-Ratio-Driven Beta Compression in the BNB-ETH Pair, May 2022 – April 2026",
  "alternateName": "방향성 디커플링 — BNB-ETH 페어에서 변동성 비율 채널에 의한 베타 압축",
  "author": {
    "@type": "Person",
    "name": "HoKwang Kim",
    "alternateName": ["Dennis Kim", "김호광"],
    "affiliation": {"@type": "Organization", "name": "Betalabs Inc."},
    "identifier": "https://orcid.org/0009-0002-0962-2175"
  },
  "datePublished": "2026-05-12",
  "publisher": {"@type": "Organization", "name": "SSRN"},
  "url": "https://ssrn.com/abstract=6750298",
  "sameAs": "https://doi.org/10.2139/ssrn.6750298",
  "identifier": [
    {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.2139/ssrn.6750298"},
    {"@type": "PropertyValue", "propertyID": "SSRN", "value": "6750298"}
  ],
  "inLanguage": "en",
  "keywords": "beta decomposition, volatility ratio, directional decoupling, BNB, Ethereum, DCC-GARCH, variance decomposition, rolling beta, correlation, cryptocurrency",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "abstract": "Documents an instance of channel-specific beta change in BNB-ETH, May 2022 to April 2026. Static beta falls 16.9% while Pearson correlation is unchanged at 0.731. Variance decomposition attributes 100% of the beta change to the volatility-ratio channel. DCC-GARCH confirms direction. The paper formalizes 'directional decoupling' as a distinct empirical phenomenon from co-movement weakening."
}
```

---

## Related Papers

- **Paper 2** — [Distribution Asymmetry of CEX Airdrops (SSRN 6688740)](./02_SSRN-6688740_Distribution-Asymmetry-BNB.md) — companion paper on BNB Chain ecosystem.

> **Terminology disambiguation**: Paper 2's "decoupling" refers to *cross-domain* decoupling (BNB Chain macro-activity vs. Megadrop token prices). This paper's "directional decoupling" refers to a *within-pair beta compression* phenomenon. The two concepts operate at distinct analytical levels.

- **Paper 1** — [The 72-Hour Shock (SSRN 6632838)](./01_SSRN-6632838_72-Hour-Shock.md) — methodologically related (cryptocurrency event-window analysis).

---

## Reproducibility

- **Code & data**: <https://github.com/gameworkerkim/vibe-investing>
- **Data source**: daily BNB and ETH prices from public exchanges (Binance, CoinGecko, CryptoCompare cross-validation)
- **License**: MIT (code), CC-BY-4.0 (paper text), public domain (price data)
