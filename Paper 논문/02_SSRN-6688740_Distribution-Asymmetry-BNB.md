---
ssrn_id: 6688740
title: "Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain"
title_ko: "중앙화 거래소 에어드롭의 분배 비대칭과 BNB 체인 생태계: BNB 보유자의 이익, 재단의 재앙, 그리고 BNB 체인의 디커플링 패턴"
short_title: "Distribution Asymmetry (BNB Megadrop)"
authors:
  - family: Kim
    given: HoKwang
    given_ko: 호광
    alias: Dennis Kim
    affiliation: "Betalabs Inc."
    orcid: "0009-0002-0962-2175"
    corresponding: true
doi: "10.2139/ssrn.6688740"
url: "https://ssrn.com/abstract=6688740"
canonical_url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6688740"
ssrn_author_id: 11276088
posted_date: "2026-05-11"
language: "en"
pages: 55
type: "preprint"
publisher: "SSRN"
license: "CC-BY-4.0"
data_availability: "Public — on-chain data + Binance public Megadrop pages"
funding: "This research received no external funding."
keywords:
  - "airdrop"
  - "Megadrop"
  - "BNB Chain"
  - "centralized exchange"
  - "distribution asymmetry"
  - "tokenomics"
  - "foundation treasury"
  - "exchange-native token"
  - "Binance"
  - "ecosystem decoupling"
keywords_ko:
  - "에어드롭"
  - "메가드롭"
  - "BNB 체인"
  - "중앙화 거래소"
  - "분배 비대칭"
  - "토크노믹스"
  - "재단 자금"
  - "거래소 네이티브 토큰"
  - "바이낸스"
  - "생태계 디커플링"
jel_codes: ["G14", "G12", "G15", "D31", "L86"]
acm_classification: []
mesh_terms: []
github_repo: "https://github.com/gameworkerkim/vibe-investing"
related_papers: ["10.2139/ssrn.6632838", "10.2139/ssrn.6750298"]
---

# Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem

> **Subtitle**: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain

**SSRN Working Paper No. 6688740** · DOI: [10.2139/ssrn.6688740](https://doi.org/10.2139/ssrn.6688740) · Posted: 2026-05-11

[![SSRN](https://img.shields.io/badge/SSRN-6688740-1A5F7A)](https://ssrn.com/abstract=6688740)
[![DOI](https://img.shields.io/badge/DOI-10.2139%2Fssrn.6688740-blue)](https://doi.org/10.2139/ssrn.6688740)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--0962--2175-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0002-0962-2175)
[![Pages](https://img.shields.io/badge/Pages-55-informational)]()

---

## Author

**HoKwang Kim (Dennis Kim, 김호광)** — Betalabs Inc.
ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175) · Email: gameworker@gmail.com

---

## English

### Abstract

This paper examines the distribution-asymmetry structure of **centralized exchange (CEX) airdrop campaigns**, with a focus on Binance's *Megadrop* program and the broader BNB Chain ecosystem. Using a sample of Megadrop and HODLer-airdrop events from 2024 through Q1 2026, we decompose realized economic outcomes across three stakeholder cohorts: (i) BNB holders who lock BNB to qualify, (ii) project foundations that contribute tokens to the campaign, and (iii) general retail participants who buy post-listing. We document that **BNB holders systematically capture positive risk-adjusted returns** through subscription rebates, *vault APY*, and post-listing dump windows, while **project foundations realize negative outcomes** through valuation compression and immediate post-event sell pressure. We further document a *decoupling pattern* in which BNB Chain on-chain activity (DAU, gas usage, TVL) grew during the same window in which Megadrop-category token prices declined materially — evidence that platform-level token value can decouple from ecosystem usage when distribution mechanics privilege one stakeholder cohort. The paper formalizes this as a *three-cohort distribution model* with empirical calibration to public BNB Chain data.

### Significance (Why This Paper Matters)

Three contributions distinguish this paper from prior literature on airdrops:

1. **First systematic decomposition of CEX airdrop outcomes by stakeholder cohort.** Prior academic work on airdrops (Allen et al. 2023; Makarov & Schoar 2022) treats airdrops as a uniform marketing or distribution event. This paper shows that *the same airdrop generates structurally different P&L for BNB holders vs. foundations vs. retail* — and provides the framework to measure each.
2. **Quantification of the "foundation disaster" pattern.** For the median Megadrop project in our sample, the foundation's contributed tokens experience material price decline within 30 days post-listing, while BNB holders' realized yield (subscription + vault + sell) is positive in the same window. This is the strongest empirical evidence to date that the *issuer*-side economics of CEX airdrops are systematically disadvantageous to project foundations.
3. **Documentation of platform-ecosystem decoupling.** BNB Chain DAU and gas usage grew during the same window in which the average Megadrop token price declined ~X%. This finding has direct relevance for *exchange-native token valuation models* that conflate platform usage growth with token price appreciation — an assumption embedded in many Web3 venture capital theses.

The paper is also relevant to Korean regulatory deliberations. The *DAXA* and *KoFIU* frameworks currently treat all airdrop tokens uniformly under "투자유의" (investor caution) designation. This paper's three-cohort analysis suggests that distinct disclosure regimes for the three stakeholder types may be warranted.

### Methodology (One-Paragraph Summary)

We construct an event window around each Megadrop's *first trading day* on Binance Spot. For each event, we compute: (i) the BNB holder's *realized yield* from subscription rebate + vault APY + spot sell at first available liquidity; (ii) the foundation's *valuation realization* defined as $(\text{tokens distributed} \times P_{listing}) - (\text{tokens distributed} \times P_{T+30})$ where T denotes listing day; (iii) retail buyer P&L assuming purchase at $P_{listing}$ and exit at $P_{T+30}$. Decoupling is measured by quarterly correlation between BNB Chain DAU growth and Megadrop-token price index. Robustness includes excluding outliers, varying the holding window, and event-time normalization.

### Keywords

`airdrop` · `Megadrop` · `BNB Chain` · `centralized exchange` · `distribution asymmetry` · `tokenomics` · `foundation treasury` · `exchange-native token` · `Binance` · `ecosystem decoupling`

### JEL Classification

- **G14** — Information and Market Efficiency; Event Studies
- **G12** — Asset Pricing; Trading Volume; Bond Interest Rates
- **G15** — International Financial Markets
- **D31** — Personal Income, Wealth, and Their Distributions
- **L86** — Information and Internet Services; Computer Software

---

## 한국어 (Korean)

### 초록

본 논문은 **중앙화 거래소(CEX)** 의 에어드롭 캠페인이 가지는 *분배 비대칭 구조* 를 *바이낸스 메가드롭(Megadrop) 프로그램* 과 *BNB 체인 생태계* 를 중심으로 분석한다. 2024년부터 2026년 1분기까지의 메가드롭·HODLer 에어드롭 표본을 사용해, 실현된 경제적 성과를 세 이해관계자 집단으로 분해한다: (i) BNB 를 잠그고 자격을 얻는 *BNB 보유자*, (ii) 토큰을 캠페인에 제공하는 *프로젝트 재단*, (iii) 상장 후 매수하는 *일반 소매 참여자*. 분석 결과, **BNB 보유자는 구독 리베이트, *볼트 APY*, 상장 직후 매도 윈도우를 통해 체계적으로 양(+)의 위험조정 수익을 얻는** 반면, **프로젝트 재단은 평가가치 압축과 상장 직후 매도 압력으로 음(−)의 결과를 실현** 한다. 또한 *디커플링 패턴* 을 발견했다 — BNB 체인의 온체인 활동(DAU·가스 사용량·TVL) 이 성장하는 동일 구간에서 메가드롭 카테고리 토큰 가격은 상당 폭 하락했다. 이는 분배 메커니즘이 특정 이해관계자에게 유리하게 설계될 때 *플랫폼 토큰 가치* 가 *생태계 사용성* 과 *분리될 수 있다* 는 실증 증거이다. 본 논문은 이를 *3-코호트 분배 모형* 으로 형식화하고 BNB 체인 공개 데이터로 보정한다.

### 연구의 의의

기존 에어드롭 문헌과 구분되는 본 논문의 세 가지 기여:

1. **CEX 에어드롭 성과의 이해관계자별 분해 최초 시도.** 기존 학술 연구(Allen et al. 2023; Makarov & Schoar 2022 등) 는 에어드롭을 *균일한 마케팅·분배 이벤트* 로 다룬다. 본 논문은 *동일한 에어드롭이 BNB 보유자/재단/소매 참여자에게 구조적으로 다른 손익을 발생시킨다* 는 점을 보이고, 각 집단의 손익을 측정하는 프레임워크를 제시한다.
2. **"재단의 재앙(Foundation Disaster)" 패턴 정량화.** 표본 내 메가드롭 프로젝트 중앙값 기준, 재단이 제공한 토큰은 상장 후 30일 이내 상당한 가격 하락을 경험하는 반면, BNB 보유자의 실현 수익률(구독 + 볼트 + 매도) 은 동일 윈도우에서 양(+) 이다. 이는 *CEX 에어드롭의 발행자측 경제학이 프로젝트 재단에 체계적으로 불리하다* 는 가장 강력한 실증 증거다.
3. **플랫폼-생태계 디커플링 현상의 문서화.** BNB 체인 DAU·가스 사용량은 성장하는 같은 윈도우에서 평균 메가드롭 토큰 가격은 약 X% 하락했다. 이는 *플랫폼 사용량 성장 ≒ 토큰 가격 상승* 으로 가정하는 *거래소 네이티브 토큰 가치평가 모형* 에 직접적 시사점을 제공하며, Web3 벤처캐피탈 투자 논리의 핵심 가정을 재검토하게 한다.

본 논문은 한국 규제 환경에도 적용 가능하다. *DAXA* 와 *KoFIU* 의 *투자유의종목* 지정 체계는 현재 모든 에어드롭 토큰을 균일하게 다루지만, 본 논문의 *3-코호트 분석* 은 *세 이해관계자 유형에 대한 별도 공시 체계* 가 필요할 수 있음을 시사한다.

### 방법론 (한 문단 요약)

각 메가드롭의 *바이낸스 현물 첫 거래일* 을 중심으로 이벤트 윈도우를 구성한다. 각 이벤트에 대해 (i) BNB 보유자의 *실현 수익률* = 구독 리베이트 + 볼트 APY + 첫 유동성 시점 매도; (ii) 재단의 *평가가치 실현* = $(\text{분배 토큰} \times P_{상장}) - (\text{분배 토큰} \times P_{T+30})$, T 는 상장일; (iii) 소매 매수자 손익 = $P_{상장}$ 매수 후 $P_{T+30}$ 매도. 디커플링은 BNB 체인 DAU 성장률과 메가드롭 토큰 가격 인덱스의 분기별 상관계수로 측정한다. 견고성 검사로는 이상치 제외, 보유 윈도우 변경, 이벤트 시간 정규화를 포함한다.

### 키워드

`에어드롭` · `메가드롭` · `BNB 체인` · `중앙화 거래소` · `분배 비대칭` · `토크노믹스` · `재단 자금` · `거래소 네이티브 토큰` · `바이낸스` · `생태계 디커플링`

---

## Citation Formats

### BibTeX

```bibtex
@misc{kim2026_airdrop,
  author    = {Kim, HoKwang},
  title     = {Distribution Asymmetry of Centralized Exchange Airdrops and the {BNB} Chain Ecosystem:
               {BNB} Holder Gain, Foundation Disaster, and the Decoupling Pattern of {BNB} Chain},
  year      = {2026},
  month     = may,
  publisher = {SSRN},
  doi       = {10.2139/ssrn.6688740},
  url       = {https://ssrn.com/abstract=6688740},
  note      = {SSRN Working Paper No.~6688740}
}
```

### RIS

```
TY  - GEN
T1  - Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain
AU  - Kim, HoKwang
PY  - 2026
DA  - 2026/05/11
PB  - SSRN
DO  - 10.2139/ssrn.6688740
UR  - https://ssrn.com/abstract=6688740
KW  - airdrop
KW  - Megadrop
KW  - BNB Chain
KW  - centralized exchange
KW  - distribution asymmetry
N1  - SSRN Working Paper No. 6688740
ER  -
```

### APA (7th edition)

> Kim, H. (2026). *Distribution asymmetry of centralized exchange airdrops and the BNB Chain ecosystem: BNB holder gain, foundation disaster, and the decoupling pattern of BNB Chain* (SSRN Working Paper No. 6688740). SSRN. <https://doi.org/10.2139/ssrn.6688740>

### MLA (9th edition)

> Kim, HoKwang. "Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain." *SSRN*, 11 May 2026, doi:10.2139/ssrn.6688740.

### Chicago (Author-Date)

> Kim, HoKwang. 2026. "Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain." SSRN Working Paper No. 6688740. <https://doi.org/10.2139/ssrn.6688740>.

### Korean (한국어 인용)

> 김호광 (2026). 「중앙화 거래소 에어드롭의 분배 비대칭과 BNB 체인 생태계: BNB 보유자의 이익, 재단의 재앙, 그리고 BNB 체인의 디커플링 패턴」. *SSRN Working Paper* No. 6688740. <https://doi.org/10.2139/ssrn.6688740>

---

## Machine-Readable Metadata (JSON-LD, schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem: BNB Holder Gain, Foundation Disaster, and the Decoupling Pattern of BNB Chain",
  "alternateName": "중앙화 거래소 에어드롭의 분배 비대칭과 BNB 체인 생태계",
  "author": {
    "@type": "Person",
    "name": "HoKwang Kim",
    "alternateName": ["Dennis Kim", "김호광"],
    "affiliation": {"@type": "Organization", "name": "Betalabs Inc."},
    "identifier": "https://orcid.org/0009-0002-0962-2175"
  },
  "datePublished": "2026-05-11",
  "publisher": {"@type": "Organization", "name": "SSRN"},
  "url": "https://ssrn.com/abstract=6688740",
  "sameAs": "https://doi.org/10.2139/ssrn.6688740",
  "identifier": [
    {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.2139/ssrn.6688740"},
    {"@type": "PropertyValue", "propertyID": "SSRN", "value": "6688740"}
  ],
  "inLanguage": "en",
  "keywords": "airdrop, Megadrop, BNB Chain, centralized exchange, distribution asymmetry, tokenomics, foundation treasury, Binance, ecosystem decoupling",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "abstract": "Examines the distribution-asymmetry structure of CEX airdrop campaigns, focusing on Binance Megadrop and BNB Chain. Decomposes realized outcomes across three cohorts: BNB holders, foundations, and retail. Documents systematic BNB-holder gains, foundation losses, and ecosystem-level decoupling between BNB Chain on-chain activity and Megadrop token prices."
}
```

---

## Related Papers

- **Paper 1** — [The 72-Hour Shock (SSRN 6632838)](./01_SSRN-6632838_72-Hour-Shock.md) — companion event-study methodology
- **Paper 4** — [Directional Decoupling: BNB-ETH Beta (SSRN 6750298)](./04_SSRN-6750298_Directional-Decoupling.md) — formalizes a *different* decoupling concept (within-pair beta compression vs. ecosystem decoupling in this paper)

> **Terminology note**: "Decoupling" in this paper refers to *cross-domain decoupling* (BNB Chain on-chain activity vs. Megadrop token prices). Paper 4's "directional decoupling" refers to a *within-pair beta compression* phenomenon. The two concepts operate at different analytical levels.

---

## Reproducibility

- **Code & data**: <https://github.com/gameworkerkim/vibe-investing>
- **License**: MIT (code), CC-BY-4.0 (paper text), public domain (BNB Chain on-chain data)
