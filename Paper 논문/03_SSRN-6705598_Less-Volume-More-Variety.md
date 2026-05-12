---
ssrn_id: 6705598
title: "Less Volume, More Variety: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection"
title_ko: "Less Volume, More Variety — 제약 섹터 종목 선별에서 LLM 출력 길이와 컨트라리안 발굴의 역상관 관계"
short_title: "Less Volume, More Variety"
authors:
  - family: Kim
    given: HoKwang
    given_ko: 호광
    alias: Dennis Kim
    affiliation: "Betalabs Inc."
    orcid: "0009-0002-0962-2175"
    corresponding: true
doi: "10.2139/ssrn.6705598"
url: "https://ssrn.com/abstract=6705598"
canonical_url: "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6705598"
ssrn_author_id: 11276088
posted_date: "2026-05-11"
language: "en"
pages: 9
type: "preprint"
paper_format: "Letter (Finance Research Letters style)"
publisher: "SSRN"
license: "CC-BY-4.0"
data_availability: "Public — full prompt/response transcripts on GitHub"
funding: "This research received no external funding."
keywords:
  - "large language model"
  - "LLM"
  - "output length"
  - "contrarian discovery"
  - "stock selection"
  - "pharmaceutical sector"
  - "compression-forces-selection"
  - "Spearman correlation"
  - "ChatGPT"
  - "Claude"
  - "DeepSeek"
  - "Gemini"
  - "model ensemble"
  - "token budget"
keywords_ko:
  - "거대언어모델"
  - "LLM"
  - "출력 길이"
  - "컨트라리안 발굴"
  - "종목 선별"
  - "제약 섹터"
  - "압축이 선별을 강제한다"
  - "스피어만 상관"
  - "ChatGPT"
  - "Claude"
  - "DeepSeek"
  - "Gemini"
  - "모델 앙상블"
  - "토큰 예산"
jel_codes: ["G11", "G14", "G17", "C45", "O33"]
acm_classification: ["I.2.7 Natural Language Processing"]
mesh_terms: []
github_repo: "https://github.com/gameworkerkim/vibe-investing"
related_papers: []
target_journal: "Finance Research Letters"
---

# Less Volume, More Variety

> **Subtitle**: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection

**SSRN Working Paper No. 6705598** · DOI: [10.2139/ssrn.6705598](https://doi.org/10.2139/ssrn.6705598) · Posted: 2026-05-11

[![SSRN](https://img.shields.io/badge/SSRN-6705598-1A5F7A)](https://ssrn.com/abstract=6705598)
[![DOI](https://img.shields.io/badge/DOI-10.2139%2Fssrn.6705598-blue)](https://doi.org/10.2139/ssrn.6705598)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--0962--2175-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0002-0962-2175)
[![Format](https://img.shields.io/badge/Format-Letter-orange)]()

---

## Author

**HoKwang Kim (Dennis Kim, 김호광)** — Betalabs Inc.
ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175) · Email: gameworker@gmail.com

---

## English

### Abstract

This Letter reports a counterintuitive empirical pattern in LLM-based stock analysis: under identical prompts, **shorter-output models produce proportionally more contrarian (uniquely-discovered) stock picks**. We submit a single LONG/SHORT pharmaceutical-sector prompt to four frontier LLMs (ChatGPT, Claude, DeepSeek, Gemini) and observe a strong negative rank correlation between *output length (KB)* and *contrarian discovery rate (CDR)*: Spearman ρ = −0.80 across all four models, and ρ = −1.00 after excluding ChatGPT as a stale-data outlier. The most compressed model (Gemini, 4.13 KB) generates **~14× more contrarian picks per kilobyte** than the most verbose (DeepSeek, 38.6 KB). We propose a *compression-forces-selection* mechanism: when token budget is constrained, models cannot afford to enumerate consensus picks and must allocate scarce capacity to differentiated signals. The Letter outlines a five-study research agenda for replication and extension.

### Significance (Why This Paper Matters)

This Letter contributes three things to the LLM-for-finance literature:

1. **Cautionary evidence against length-as-quality heuristics.** Practitioners routinely equate longer LLM outputs with richer or more thorough analysis. Our results suggest the opposite for *contrarian signal generation*: **token budget itself may function as a hyperparameter for inducing diversity-of-thought in LLM ensembles**. Practical implication — ensembling LLMs with diverse output-length characteristics reduces systematic blind spots more efficiently than ensembling LLMs of similar verbosity.
2. **A reproducible, low-cost evaluation protocol.** N=4 is small, but the protocol — single prompt, identical input, four frontier LLMs, transparent metric (CDR = unique picks / total picks) — can be replicated by any researcher with API access in under one hour. Full prompts and responses are public on GitHub.
3. **A testable mechanism for the diversity-volume tradeoff.** The *compression-forces-selection* hypothesis is falsifiable: it predicts that *within-model* token-budget manipulation (via `max_tokens` parameter) should produce the same inverse pattern. The Letter's Section 4 outlines this Study 2 of a five-study agenda.

### Five-Study Research Agenda (outlined in the Letter)

1. **Study 1** — Cross-model replication (n ≥ 12 frontier LLMs)
2. **Study 2** — Within-model `max_tokens` manipulation
3. **Study 3** — 2×2 factorial (web-search on/off × short/long output)
4. **Study 4** — T+12-month forward backtest of LLM-generated picks
5. **Study 5** — Cross-sector validation (financials, semiconductors, energy)

### Key Numbers

| Model | Output (KB) | CDR (%) | CDR / KB |
|---|---|---|---|
| Gemini | 4.13 | high | **~14× vs. DeepSeek** |
| Claude | (mid) | (mid) | (mid) |
| ChatGPT | (mid, stale-data outlier) | — | — |
| DeepSeek | 38.6 | low | baseline |

> Exact figures in the Letter; this table is illustrative.

### Methodology (One-Paragraph Summary)

A single prompt template asks each LLM to produce LONG / SHORT recommendations for the US pharmaceutical sector with explicit screening criteria. All four LLMs receive the *identical* prompt (controlling for temperature, system prompt, and date). Output length is measured in KB. *Contrarian discovery rate* (CDR) for model *m* is defined as $|S_m \setminus (\bigcup_{j \neq m} S_j)| / |S_m|$, where $S_m$ is the set of unique tickers in model *m*'s output. Rank correlation is computed via Spearman's ρ on (KB, CDR).

### Keywords

`large language model` · `output length` · `contrarian discovery` · `stock selection` · `pharmaceutical sector` · `compression-forces-selection` · `Spearman correlation` · `model ensemble`

### JEL Classification

- **G11** — Portfolio Choice; Investment Decisions
- **G14** — Information and Market Efficiency
- **G17** — Financial Forecasting and Simulation
- **C45** — Neural Networks and Related Topics
- **O33** — Technological Change: Choices and Consequences; Diffusion Processes

### ACM Classification

- **I.2.7** — Natural Language Processing

---

## 한국어 (Korean)

### 초록

본 Letter 는 LLM 기반 종목 분석에서 직관에 반하는 실증 패턴을 보고한다 — *동일 프롬프트 조건에서, **출력 분량이 짧은 모델일수록 컨트라리안(단독 발굴) 종목이 비례적으로 더 많이 나타난다.*** 4개 frontier LLM(ChatGPT, Claude, DeepSeek, Gemini) 에 동일한 LONG/SHORT 제약 섹터 프롬프트를 투입한 결과, 출력 길이(KB) 와 *컨트라리안 발굴률(Contrarian Discovery Rate, CDR)* 사이에 강한 음의 순위 상관이 관측됐다 — Spearman ρ = −0.80 (n=4 전체), ChatGPT 를 *stale-data 이상치* 로 제외 시 ρ = −1.00. 가장 압축적인 모델(Gemini, 4.13 KB) 은 가장 verbose 한 모델(DeepSeek, 38.6 KB) 대비 *KB 당 약 14배의 컨트라리안 발굴률* 을 보였다. 우리는 이를 *compression-forces-selection*(압축이 선별을 강제한다) 메커니즘으로 해석한다 — 토큰 예산이 제약될 때, 모델은 컨센서스 종목을 나열할 여유가 없어 차별화된 신호에 자원을 배분한다. 본 Letter 는 복제 및 확장을 위한 5단계 연구 어젠다를 제시한다.

### 연구의 의의

본 Letter 의 세 가지 기여:

1. **"분량 = 품질" 휴리스틱에 대한 경고적 증거.** 실무자들은 일상적으로 *LLM 출력이 길수록 더 풍부하거나 더 철저한 분석* 이라고 해석한다. 본 결과는 *컨트라리안 신호 생성* 영역에서는 그 반대임을 시사한다 — **토큰 예산 자체가 LLM 앙상블에서 사고 다양성을 유도하는 하이퍼파라미터로 기능할 수 있다.** 실무적 함의 — *출력 길이 특성이 다양한 LLM 들을 앙상블* 하는 것이 *유사한 분량의 LLM 들을 앙상블* 하는 것보다 체계적 사각지대를 더 효과적으로 줄인다.
2. **재현 가능하고 저비용인 평가 프로토콜.** 표본 크기(N=4) 는 작지만, 프로토콜 — 단일 프롬프트, 동일 입력, 4개 frontier LLM, 투명한 측정 지표(CDR = 단독 발굴 / 전체 발굴) — 은 API 접근권을 가진 누구나 1시간 내 복제 가능하다. 전체 프롬프트와 응답이 GitHub 에 공개되어 있다.
3. **검증 가능한 가설.** *compression-forces-selection* 가설은 반증 가능하다 — *동일 모델 내* `max_tokens` 조작 시 같은 역상관 패턴이 재현되어야 한다는 예측을 내놓는다. Letter 의 4절은 이를 *5단계 어젠다 중 Study 2* 로 명시한다.

### 5단계 연구 어젠다 (Letter 본문)

1. **Study 1** — 모델 간 복제 (n ≥ 12 frontier LLM)
2. **Study 2** — 동일 모델 내 `max_tokens` 조작
3. **Study 3** — 2×2 factorial (웹검색 on/off × 짧은/긴 출력)
4. **Study 4** — T+12 개월 forward 백테스트
5. **Study 5** — 섹터 횡단 검증 (금융, 반도체, 에너지)

### 방법론 (한 문단 요약)

단일 프롬프트 템플릿이 각 LLM 에게 미국 제약 섹터의 LONG/SHORT 추천을 명시적 스크리닝 기준과 함께 요구한다. 4개 LLM 모두 *동일* 프롬프트(temperature, system prompt, 날짜 통제) 를 받는다. 출력 길이는 KB 로 측정된다. 모델 *m* 의 *컨트라리안 발굴률(CDR)* 은 $|S_m \setminus (\bigcup_{j \neq m} S_j)| / |S_m|$ 로 정의되며, $S_m$ 은 모델 *m* 출력의 유니크 티커 집합이다. 순위 상관은 (KB, CDR) 에 대한 Spearman ρ 로 계산된다.

### 키워드

`거대언어모델` · `출력 길이` · `컨트라리안 발굴` · `종목 선별` · `제약 섹터` · `압축이 선별을 강제한다` · `스피어만 상관` · `모델 앙상블`

---

## Citation Formats

### BibTeX

```bibtex
@misc{kim2026_llm,
  author    = {Kim, HoKwang},
  title     = {Less Volume, More Variety: An Inverse Relationship Between {LLM} Output Length
               and Contrarian Discovery in Pharmaceutical Stock Selection},
  year      = {2026},
  month     = may,
  publisher = {SSRN},
  doi       = {10.2139/ssrn.6705598},
  url       = {https://ssrn.com/abstract=6705598},
  note      = {SSRN Working Paper No.~6705598}
}
```

### RIS

```
TY  - GEN
T1  - Less Volume, More Variety: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection
AU  - Kim, HoKwang
PY  - 2026
DA  - 2026/05/11
PB  - SSRN
DO  - 10.2139/ssrn.6705598
UR  - https://ssrn.com/abstract=6705598
KW  - large language model
KW  - output length
KW  - contrarian discovery
KW  - pharmaceutical sector
KW  - stock selection
N1  - SSRN Working Paper No. 6705598
ER  -
```

### APA (7th edition)

> Kim, H. (2026). *Less volume, more variety: An inverse relationship between LLM output length and contrarian discovery in pharmaceutical stock selection* (SSRN Working Paper No. 6705598). SSRN. <https://doi.org/10.2139/ssrn.6705598>

### MLA (9th edition)

> Kim, HoKwang. "Less Volume, More Variety: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection." *SSRN*, 11 May 2026, doi:10.2139/ssrn.6705598.

### Chicago (Author-Date)

> Kim, HoKwang. 2026. "Less Volume, More Variety: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection." SSRN Working Paper No. 6705598. <https://doi.org/10.2139/ssrn.6705598>.

### Korean (한국어 인용)

> 김호광 (2026). 「Less Volume, More Variety — 제약 섹터 종목 선별에서 LLM 출력 길이와 컨트라리안 발굴의 역상관 관계」. *SSRN Working Paper* No. 6705598. <https://doi.org/10.2139/ssrn.6705598>

---

## Machine-Readable Metadata (JSON-LD, schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "Less Volume, More Variety: An Inverse Relationship Between LLM Output Length and Contrarian Discovery in Pharmaceutical Stock Selection",
  "alternateName": "Less Volume, More Variety — 제약 섹터 종목 선별에서 LLM 출력 길이와 컨트라리안 발굴의 역상관 관계",
  "author": {
    "@type": "Person",
    "name": "HoKwang Kim",
    "alternateName": ["Dennis Kim", "김호광"],
    "affiliation": {"@type": "Organization", "name": "Betalabs Inc."},
    "identifier": "https://orcid.org/0009-0002-0962-2175"
  },
  "datePublished": "2026-05-11",
  "publisher": {"@type": "Organization", "name": "SSRN"},
  "url": "https://ssrn.com/abstract=6705598",
  "sameAs": "https://doi.org/10.2139/ssrn.6705598",
  "identifier": [
    {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.2139/ssrn.6705598"},
    {"@type": "PropertyValue", "propertyID": "SSRN", "value": "6705598"}
  ],
  "inLanguage": "en",
  "keywords": "large language model, LLM, output length, contrarian discovery, stock selection, pharmaceutical sector, compression-forces-selection, Spearman correlation, ChatGPT, Claude, DeepSeek, Gemini, model ensemble, token budget",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "abstract": "Under identical prompts to four frontier LLMs (ChatGPT, Claude, DeepSeek, Gemini), shorter-output models produce proportionally more contrarian stock picks. Spearman rank correlation between output length (KB) and contrarian discovery rate is −0.80 across four models and −1.00 excluding a stale-data outlier. Proposes the compression-forces-selection mechanism and outlines a five-study research agenda."
}
```

---

## Related Resources

- **Predecessor paper (unpublished)**: "Same LLM, Different Languages, Different Answers" — multilingual LLM consistency analysis on US dividend growth stocks (v5 working draft on GitHub).
- **GitHub repo**: <https://github.com/gameworkerkim/vibe-investing> — includes the prompts, full LLM responses, evaluation scripts.

---

## Reproducibility

- **Code & data**: <https://github.com/gameworkerkim/vibe-investing>
- **Replication time**: ~1 hour with API access to four frontier LLMs
- **License**: MIT (code), CC-BY-4.0 (paper text)
- **Target journal for full version**: *Finance Research Letters* (Letter format, ~2,200 words)
