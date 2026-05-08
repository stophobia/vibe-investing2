# Awesome Claude Quant Scripts

> Claude 기반 재현 가능한 퀀트 스크립트 라이브러리. 다국어 검증 + 1차 출처 강제 + 시점적 전략 + 학술 검증 결합.

→ [01.Trading Strategy README로 돌아가기](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Readme.MD)
→ [메인 README](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)

---

## 한 줄 요약

이 폴더의 모든 스크립트는 **단일 LLM의 답을 신뢰하지 않고**, *다국어 cross-validation + 1차 출처 강제 + 학술적 검증* 을 통해 **AI 시대의 재현 가능한 퀀트 프롬프트** 패턴을 라이브러리화한 결과물입니다.

> 메타 메시지: LLM은 엑셀이지, 정답을 알려주는 오라클이 아니다.

---

## 폴더 구성

3개의 하위 폴더로 구성되어 있습니다.

| # | 폴더 | 핵심 자산 | 형식 |
| --- | --- | --- | --- |
| Q1 | [Dividend growth prompt](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dividend%20growth%20prompt) | Cross-Lingual LLM Accuracy v5 + MSFT 사례 칼럼 v2 | 학술 (SSRN) + 칼럼 + 프롬프트 |
| Q2 | [Pharma growth prompt](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Pharma%20growth%20prompt) | 미국 제약 LONG 7 + SHORT 3 (FDA + ClinicalTrials.gov NCT) | 다국어 프롬프트 (KR/EN/CN) |
| Q3 | [AI Supercycle Investment Quant Strategy](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20Supercycle%20Investment%20Quant%20Strategy) | AI 인프라 사이클의 시점적 정량 전략 | 칼럼 + 전략 |

---

## 핵심 자산

### Q1. Dividend Growth Prompt — Cross-Lingual LLM 학술 검증 + MSFT 실증 사례

**가장 중요한 폴더.** 이 폴더 하나에 *학술 working paper + 실증 칼럼 + 재현 가능한 프롬프트* 가 **모두 함께** 위치합니다.

#### 주요 자산

**1. 학술 working paper (SSRN IN REVIEW)**

> *\"Less Volume, More Variety: Same LLM, Different Languages, Different Answers\"*

- 같은 LLM이 한국어 / 영어 / 중국어로 같은 질문을 받을 때 *서로 다른 답을 산출*하는 현상을 N=11 종목으로 검증
- Abstract ID 6705598 (5/4 created, 5/6부터 IN REVIEW, 5/8-11 publishing 예상)
- v5에서 *실시간 시장 검증 addendum* 추가 (이론 → 실측 시장 데이터로 cross-validation)

#### 핵심 발견 사항

- 같은 LLM (예: Claude Opus 4.5) 이 한국어 질문 → 11개 종목 중 8개 매수 추천, 영어 질문 → 11개 종목 중 5개 매수 추천, 중국어 질문 → 11개 종목 중 6개 매수 추천 등의 *언어 간 inconsistency*
- 다국어 답변 *합집합* 이 단일 언어 답변보다 *더 정확한 universe* 를 만든다는 결론
- Korean retail 투자자가 *영문 답변만* 신뢰하면 *놓치는 종목* 이 평균 27% 발생

**2. 실증 칼럼 — LLM 합의 vs 시장 현실 (MSFT 사례 v2)**

[칼럼 8번](https://github.com/gameworkerkim/vibe-investing/blob/main/02.Investment%20Idea%20Column/Readme.MD)

- 6개 LLM이 MSFT에 대해 *11/11 매수 합의*
- 시장은 다음 달 -7% 하락
- → *LLM 합의가 시장 정확도를 보장하지 않는다* 의 명확한 사례

**3. 재현 가능한 프롬프트**

배당 성장주 universe 자동 생성 프롬프트. 본인이 *fork 하여 본인 universe* 에 적용 가능. 특히 다국어 cross-validation 패턴이 명시되어 있어 *프롬프트만 교체하면* 다른 섹터에도 즉시 적용 가능합니다.

#### Q1의 차별점

| 일반 LLM 사용 | **이 폴더의 패턴** |
| --- | --- |
| 한 언어로 한 LLM에게 질문 | **3개 언어 × 다중 LLM cross-validation** |
| 답변을 그대로 신뢰 | **답변의 시장 검증 (MSFT 사례)** |
| 결과만 사용 | **결과 + 학술 working paper + 칼럼 함께 제공** |
| 일회성 | **재현 가능한 프롬프트 라이브러리화** |

### Q2. Pharma Growth Prompt — 다국어 프롬프트 (KR / EN / CN)

미국 제약 섹터 LONG 7 + SHORT 3 추천을 *FDA Orange Book + ClinicalTrials.gov NCT 1차 출처 강제* 패턴으로 생성하는 다국어 프롬프트.

#### 평가 기준 (3-axis)

| 축 | 비중 | 검증 출처 |
| --- | --- | --- |
| Pipeline (FDA approval phases) | 40% | FDA Orange Book + drugs.fda.gov |
| Revenue / IR | 35% | SEC EDGAR 10-K, 10-Q |
| Valuation | 25% | 일반 financial data API |

#### 다국어 동시 제공의 의미

3개 언어 (KR / EN / CN) 동시 제공이 *단순 번역*이 아닙니다. 이는 위 Q1의 Cross-Lingual LLM Accuracy 학술 결과의 **시스템 차원 implementation**:

- 같은 universe 질문에 *3개 언어로 동시 호출* → *답변 합집합* 이 본인 분석 universe
- 각 언어의 *지역 시장 narrative bias* 분리 (KR 사용자는 한국어 답변에서 강한 종목, EN 사용자는 글로벌 narrative 종목)
- 사용자 본인이 다국어를 *모두* 못 읽어도 *프롬프트 자체가 cross-validation 강제*

#### 사용 시나리오

```
1. 본인이 분석하고 싶은 섹터 결정 (현재: Pharma)
2. 3개 언어 프롬프트를 LLM (Claude / GPT / Gemini) 에 동시 호출
3. 답변 합집합으로 LONG 7 + SHORT 3 universe 형성
4. FDA Orange Book / ClinicalTrials.gov / SEC EDGAR 1차 출처 cross-check
5. 본인 분석으로 최종 의사결정
```

**섹터 교체만으로 다른 분야에 즉시 적용 가능합니다.** Pharma → Semiconductor, EV, Biotech 등으로 *프롬프트 키워드만 변경*.

### Q3. AI Supercycle Investment Quant Strategy — 시점적 정량 전략

[게재 일자: 2026년 5월 8일]

AI 인프라 사이클 (Nvidia, AMD, Broadcom, TSMC, ASML, Synopsys, Cadence, Arm 등) 의 *시점적 정량 전략*. AI 슈퍼사이클이 *영원하지 않다*는 것을 정량적으로 측정하기 위한 도구.

#### 핵심 thesis

AI 인프라 사이클은 다음 단계 중 어디에 있는가:
- 1단계 Adoption (수요 발견)
- 2단계 Capacity Build-out (현재)
- 3단계 Saturation (잠재 위험)
- 4단계 Replacement Cycle

각 단계에서 *유효한 전략과 위험* 이 다름. 이 폴더는 *현재 2단계에서 3단계로의 전환 시그널* 을 정량적으로 측정.

#### 칼럼 10번 (Storage Wars) 와의 연관

이 폴더의 시점적 전략은 칼럼 10번 [AI 인프라 스토리지 전쟁](https://github.com/gameworkerkim/vibe-investing/blob/main/02.Investment%20Idea%20Column/Storage%20War/Storage%20wars%20ai%20infrastructure%20column.md) 의 *6대 스토리지 기업 진단* 과 함께 읽으면 효과적입니다. AI 인프라 = GPU 일변도가 아닌 *스토리지까지 확장된 사이클* 인지가 핵심.

---

## 이 폴더가 다른 퀀트 자료와 다른 점

### 1. 학술 + 실증 + 프롬프트가 *같은 폴더에*

대부분의 GitHub 퀀트 레포는 *코드만* 있거나, *학술 논문은 별도*로 분리되어 있습니다. 이 폴더는:

- 학술 working paper (Cross-Lingual LLM v5)
- 실증 칼럼 (MSFT 사례 v2)
- 재현 가능한 프롬프트 (배당, Pharma KR/EN/CN, AI Supercycle)

위 3가지가 *Dividend growth prompt 한 폴더 안에* 통합되어 있습니다.

### 2. 다국어 cross-validation 강제

Pharma 프롬프트는 *KR / EN / CN 동시 제공*. 이는 한국 사용자가 *영문 답변만 보고* universe 형성 시 평균 27% 누락 (Q1 학술 결과) 을 *프롬프트 차원에서 차단*.

### 3. 1차 출처 인용 강제

Pharma 프롬프트는 LLM에게 *FDA Orange Book URL + ClinicalTrials.gov NCT 번호 + SEC EDGAR 10-K* 를 *반드시 인용하도록 강제*. 이는 *LLM hallucination 방지* 의 시스템 차원 implementation.

### 4. 메타 메시지 일관성

> *\"LLM은 엑셀이지, 정답을 알려주는 오라클이 아니다.\"*

이 메시지가 *Cross-Lingual LLM 학술 → MSFT 사례 칼럼 → Pharma 프롬프트 → AI Supercycle 전략* 4가지에 일관되게 반영되어 있습니다.

---

## 권장 사용 순서

처음 오신 분에게 권장하는 순서.

1. **학술적 정당성 이해부터** → Q1 Dividend growth prompt 폴더의 Cross-Lingual LLM v5 paper
2. **실증 사례로 검증** → 칼럼 8번 (LLM 합의 vs 시장 현실 MSFT v2)
3. **다국어 프롬프트 적용 연습** → Q2 Pharma growth prompt (섹터 교체로 본인 universe)
4. **시점적 전략 결합** → Q3 AI Supercycle Investment Quant Strategy + 칼럼 10번 (Storage Wars)

각 단계가 *이전 단계의 메타 메시지 implementation* 입니다.

---

## 알려진 한계

이 폴더의 모든 자산에 적용되는 공통 한계입니다.

- LLM 답변은 *시점에 따라 변동*. 같은 프롬프트도 *모델 업데이트 후* 다른 답변 산출
- 다국어 cross-validation 도 *LLM이 학습한 코퍼스의 언어별 bias* 를 완전히 제거하지 못함
- 1차 출처 인용 강제도 *LLM이 가짜 URL을 생성*하는 사례 발생 (사용자 검증 필수)
- Pharma 프롬프트는 *FDA / ClinicalTrials.gov 데이터* 가 *최신* 인지 사용자가 직접 확인 필요
- AI Supercycle 전략은 *현재 시점 (2026년 5월) 기준*. 향후 사이클 위치 변화 시 전략 재검토 필요
- 모든 백테스트는 *과거 데이터 기반*, 미래 보장 아님

---

## 라이선스

MIT License. 자유롭게 사용·수정·배포 가능합니다. 출처 표기 부탁드립니다.

학술 인용은 SSRN paper (Cross-Lingual LLM v5) 출처 명기 권장:

> *김호광 (Dennis Kim), \"Same LLM, Different Languages, Different Answers (v5)\", SSRN Working Paper, 2026.*
> *https://github.com/gameworkerkim/vibe-investing*

---

## Disclaimer

모든 프롬프트와 분석은 연구·교육 목적입니다. 자세한 내용은 [메인 README의 Disclaimer](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md#disclaimer) 참조.

> *Same LLM, different languages, different answers.*
> 같은 LLM, 다른 언어, 다른 답.
