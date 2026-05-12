---
ssrn_id: 6632838
title: "The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance"
title_ko: "72시간의 쇼크? — 바이낸스 52개 토큰 언락 이벤트의 예비적 증거"
short_title: "72-Hour Shock"
authors:
  - family: Kim
    given: HoKwang
    given_ko: 호광
    alias: Dennis Kim
    affiliation: "Betalabs Inc."
    orcid: "0009-0002-0962-2175"
    corresponding: true
doi: "10.2139/ssrn.6632838"
url: "https://ssrn.com/abstract=6632838"
canonical_url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6632838"
ssrn_author_id: 11276088
posted_date: "2026-04-24"
language: "en"
pages: 21
type: "preprint"
publisher: "SSRN"
license: "CC-BY-4.0"
data_availability: "Public — GitHub repo (gameworkerkim/vibe-investing)"
funding: "This research received no external funding."
keywords:
  - "token unlock"
  - "cryptocurrency"
  - "event study"
  - "Binance"
  - "vesting schedule"
  - "market microstructure"
  - "abnormal returns"
  - "altcoin"
keywords_ko:
  - "토큰 언락"
  - "암호화폐"
  - "이벤트 스터디"
  - "바이낸스"
  - "베스팅 일정"
  - "시장 미시구조"
  - "초과수익률"
  - "알트코인"
jel_codes: ["G14", "G12", "G17"]
acm_classification: []
mesh_terms: []
github_repo: "https://github.com/gameworkerkim/vibe-investing"
related_papers: ["10.2139/ssrn.6688740", "10.2139/ssrn.6750298"]
---

# The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance

**SSRN Working Paper No. 6632838** · DOI: [10.2139/ssrn.6632838](https://doi.org/10.2139/ssrn.6632838) · Posted: 2026-04-24

[![SSRN](https://img.shields.io/badge/SSRN-6632838-1A5F7A)](https://ssrn.com/abstract=6632838)
[![DOI](https://img.shields.io/badge/DOI-10.2139%2Fssrn.6632838-blue)](https://doi.org/10.2139/ssrn.6632838)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--0962--2175-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0002-0962-2175)

---

## Author

**HoKwang Kim (Dennis Kim, 김호광)** — Betalabs Inc.
ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175) · Email: gameworker@gmail.com

---

## English

### Abstract

This paper documents a preliminary empirical pattern surrounding token unlock events on Binance, the largest centralized cryptocurrency exchange by spot volume. Using a sample of **52 token unlock events** scheduled between 2024 and early 2026, we conduct a short-window event study around each unlock date and report systematic negative abnormal returns concentrated in the **72-hour window** following the unlock. The pattern survives adjustments for market beta to BTC/ETH, controls for token-specific volatility, and a battery of robustness checks including event-window length variation, exclusion of low-liquidity tokens, and outlier trimming. Results are framed as preliminary evidence consistent with informed-trader anticipation and asymmetric inventory adjustment by market makers, and are not represented as causal claims. The paper is offered as an open replication artifact for academic and practitioner audiences.

### Significance (Why This Paper Matters)

The cryptocurrency literature on token unlocks has, until recently, been dominated by industry research reports without standardized event-study methodology. This paper contributes three things:

1. **A reproducible event-study template** applied uniformly to 52 events, with all 10 underlying CSVs and 8 Python scripts published on GitHub. Future researchers can extend the sample or test alternative window specifications without rebuilding the data infrastructure.
2. **A measurable 72-hour window** that aligns with practitioner intuition but had not been formally documented. The asymmetry between the 0–72h and 72–168h post-unlock windows is statistically significant and economically meaningful (mean abnormal return ≈ −X% in 0–72h vs. ≈ 0% afterward; exact figures in Table 2 of the paper).
3. **Regulatory relevance for Korean markets.** The DAXA (Digital Asset Exchange Joint Council) framework currently requires investor caution designation for newly listed tokens but does not directly address unlock events. This paper provides the empirical basis for arguing that unlock-window disclosure should be elevated to the same tier as listing-event disclosure.

### Methodology (One-Paragraph Summary)

For each event *i* with unlock date $t_i$, abnormal return is defined as $AR_{i,t} = r_{i,t} - \hat{r}_{i,t}$, where $\hat{r}_{i,t}$ is fitted from a market model estimated on a [−180, −30] pre-event window with BTC and ETH as factors. Cumulative abnormal return (CAR) is computed over windows [0, +24h], [0, +72h], and [0, +168h]. Robustness includes excluding stablecoin pairs, restricting to top-100 market-cap tokens, and bootstrap resampling.

### Keywords

`token unlock` · `vesting schedule` · `event study` · `abnormal returns` · `Binance` · `cryptocurrency market microstructure` · `altcoin`

### JEL Classification

- **G14** — Information and Market Efficiency; Event Studies; Insider Trading
- **G12** — Asset Pricing; Trading Volume; Bond Interest Rates
- **G17** — Financial Forecasting and Simulation

---

## 한국어 (Korean)

### 초록

본 논문은 현물 거래량 기준 세계 최대 중앙화 암호화폐 거래소인 **바이낸스(Binance)** 에서 발생한 **토큰 언락(token unlock) 이벤트 52건**에 대한 단기 이벤트 스터디 결과를 보고한다. 표본은 2024년부터 2026년 초까지 예정된 언락 일정에 기반하며, 각 언락 시점 전후의 단기 윈도우 분석에서 **언락 후 72시간 이내** 구간에 체계적인 음(−)의 초과수익률(abnormal return) 이 집중되는 패턴을 발견한다. BTC/ETH 시장 베타 조정, 토큰별 변동성 통제, 이벤트 윈도우 길이 변경, 저유동성 토큰 제외, 이상치 제거 등 다양한 견고성 검사 하에서도 패턴은 유지된다. 결과는 *정보거래자(informed trader) 의 사전 포지셔닝* 과 *마켓메이커의 비대칭 재고 조정* 가설에 부합하는 *예비적 실증 증거* 로 제시되며, *인과적 주장(causal claim)* 으로 확장되지는 않는다.

### 연구의 의의

암호화폐 토큰 언락에 관한 기존 문헌은 표준화된 이벤트 스터디 방법론 없이 업계 리포트 위주로 진행되어 왔다. 본 논문의 세 가지 기여:

1. **재현 가능한 이벤트 스터디 템플릿** — 52건의 이벤트에 동일하게 적용했으며, 10개의 CSV 데이터와 8개의 Python 스크립트를 GitHub에 모두 공개했다. 후속 연구자가 표본 확장이나 윈도우 변경을 시도하기 위해 처음부터 인프라를 재구축할 필요가 없다.
2. **측정 가능한 72시간 윈도우** — 실무자 직관과 일치하지만 학술적으로는 명시되지 않았던 윈도우. 언락 후 0–72시간 vs 72–168시간 구간의 초과수익률 비대칭이 통계적으로 유의하고 경제적으로도 의미 있는 크기다(논문 Table 2 참조).
3. **한국 시장 규제적 함의** — *DAXA(디지털자산거래소공동협의체)* 의 *투자유의종목 지정* 체계는 신규 상장 토큰에 대해서는 운영되지만, *언락 이벤트* 자체에 대한 별도 공시 의무는 부재하다. 본 논문은 언락 윈도우 공시를 *상장 이벤트 공시와 동등한 수준* 으로 격상하자는 정책 제안의 실증적 근거가 된다.

### 방법론 (한 문단 요약)

각 이벤트 *i* 의 언락일을 $t_i$ 라 할 때, 초과수익률은 $AR_{i,t} = r_{i,t} - \hat{r}_{i,t}$ 로 정의하고, $\hat{r}_{i,t}$ 는 [−180, −30] 사전 윈도우에서 BTC·ETH 를 팩터로 한 시장모형으로 추정한다. 누적 초과수익률(CAR) 은 [0, +24h], [0, +72h], [0, +168h] 윈도우에서 계산된다. 견고성 검사로는 스테이블코인 페어 제외, 시총 상위 100 종목 한정, 부트스트랩 재표집을 사용했다.

### 키워드

`토큰 언락` · `베스팅 일정` · `이벤트 스터디` · `초과수익률` · `바이낸스` · `암호화폐 시장 미시구조` · `알트코인`

---

## Citation Formats

### BibTeX

```bibtex
@misc{kim2026_72hr,
  author    = {Kim, HoKwang},
  title     = {The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance},
  year      = {2026},
  month     = apr,
  publisher = {SSRN},
  doi       = {10.2139/ssrn.6632838},
  url       = {https://ssrn.com/abstract=6632838},
  note      = {SSRN Working Paper No.~6632838}
}
```

### RIS

```
TY  - GEN
T1  - The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance
AU  - Kim, HoKwang
PY  - 2026
DA  - 2026/04/24
PB  - SSRN
DO  - 10.2139/ssrn.6632838
UR  - https://ssrn.com/abstract=6632838
KW  - token unlock
KW  - event study
KW  - Binance
KW  - cryptocurrency
N1  - SSRN Working Paper No. 6632838
ER  -
```

### APA (7th edition)

> Kim, H. (2026). *The 72-hour shock? Preliminary evidence from 52 token unlock events on Binance* (SSRN Working Paper No. 6632838). SSRN. <https://doi.org/10.2139/ssrn.6632838>

### MLA (9th edition)

> Kim, HoKwang. "The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance." *SSRN*, 24 Apr. 2026, doi:10.2139/ssrn.6632838.

### Chicago (Author-Date)

> Kim, HoKwang. 2026. "The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance." SSRN Working Paper No. 6632838. <https://doi.org/10.2139/ssrn.6632838>.

### Korean (한국어 인용)

> 김호광 (2026). 「72시간의 쇼크? 바이낸스 52개 토큰 언락 이벤트의 예비적 증거」. *SSRN Working Paper* No. 6632838. <https://doi.org/10.2139/ssrn.6632838>

---

## Machine-Readable Metadata (JSON-LD, schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "The 72-Hour Shock? Preliminary Evidence from 52 Token Unlock Events on Binance",
  "alternateName": "72시간의 쇼크? 바이낸스 52개 토큰 언락 이벤트의 예비적 증거",
  "author": {
    "@type": "Person",
    "name": "HoKwang Kim",
    "alternateName": ["Dennis Kim", "김호광"],
    "affiliation": {"@type": "Organization", "name": "Betalabs Inc."},
    "identifier": "https://orcid.org/0009-0002-0962-2175"
  },
  "datePublished": "2026-04-24",
  "publisher": {"@type": "Organization", "name": "SSRN"},
  "url": "https://ssrn.com/abstract=6632838",
  "sameAs": "https://doi.org/10.2139/ssrn.6632838",
  "identifier": [
    {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.2139/ssrn.6632838"},
    {"@type": "PropertyValue", "propertyID": "SSRN", "value": "6632838"}
  ],
  "inLanguage": "en",
  "keywords": "token unlock, cryptocurrency, event study, Binance, vesting schedule, market microstructure, abnormal returns, altcoin",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "abstract": "This paper documents a preliminary empirical pattern surrounding token unlock events on Binance using 52 events from 2024 to early 2026. Short-window event studies reveal systematic negative abnormal returns concentrated in the 72-hour window following unlock, surviving market-beta adjustments and robustness checks."
}
```

---

## Related Papers

- **Paper 2** — [Distribution Asymmetry of Centralized Exchange Airdrops (SSRN 6688740)](./02_SSRN-6688740_Distribution-Asymmetry-BNB.md)
- **Paper 4** — [Directional Decoupling: BNB-ETH Beta Compression (SSRN 6750298)](./04_SSRN-6750298_Directional-Decoupling.md)

Both papers extend the cryptocurrency market microstructure agenda initiated by this work.

---

## Reproducibility

- **Code**: <https://github.com/gameworkerkim/vibe-investing>
- **Data**: 10 CSV files included in repository under `data/`
- **Scripts**: 8 Python files under `src/` (requirements.txt provided)
- **License**: MIT for code; CC-BY-4.0 for paper text
