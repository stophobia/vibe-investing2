# Awesome Claude Quant Scripts

> **다양한 LLM(Claude · ChatGPT · Gemini · DeepSeek)을 교차검증하여 미국 주식·암호화폐 시장을 분석하는 퀀트 프롬프트 + 코드 모음**

 **한국어** (현재 문서) · [English](./Readme%20EN.md)

→ [상위 폴더 README](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/README.md)
→ [메인 레포 README](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)

---

## 이 컬렉션의 핵심 철학 — Multi-LLM Cross-Validation

이 폴더의 모든 전략은 단순한 "프롬프트 모음"이 아닙니다. 핵심은 **하나의 동일한 프롬프트를 서로 다른 LLM에 입력하고, 그 출력의 차이를 분석하는 교차검증(Cross-Validation) 방법론**입니다.

저의 LLM 프롬프트 전략의 기본 전제는 다음과 같습니다.

1. **단일 LLM은 신뢰의 단일 근거가 될 수 없다.** 동일한 프롬프트·동일한 데이터를 주어도, Claude · ChatGPT · Gemini · DeepSeek은 서로 다른 종목, 다른 비중, 심지어 정반대의 매수/매도 포지션을 제시합니다. 단일 모델만 쓰면 그 모델의 환각(hallucination)·점수 인플레이션·학습 데이터 편향을 그대로 떠안게 됩니다.

2. **모델 간 "합의(Consensus)"와 "분열(Divergence)" 자체가 신호다.** 여러 모델이 만장일치로 동의한 종목은 강한 시그널이고, 의견이 갈리는 종목은 사람이 직접 1차 출처로 검증해야 하는 영역입니다. *"하나의 LLM은 환각을 만들 수 있다. 세 LLM이 합의할 때 진실에 가까워진다 — 그러나 그들이 갈릴 때, 비로소 알파를 발견한다."*

3. **정량 의사결정은 사람이 최종 캡(cap)을 적용한다.** 위상 판정·매크로 진단 같은 정성적 영역에서는 모델이 잘 수렴하지만, "그래서 무엇을 얼마나 사야 하는가"라는 정량 비중 산출에서는 극단적으로 발산합니다. 따라서 다중 LLM 보팅(median)이나 사람의 보수적 캡 적용이 반드시 필요합니다.

4. **각 모델은 고유한 "캐릭터(투자 철학)"를 가진다.** Claude는 규율 기반·audit-ready·보수적, DeepSeek은 (중국 HFT 헤지펀드 출신답게) 공격적 알파 추구, ChatGPT는 빠른 outline·구조화, Gemini는 압축적·contrarian 픽에 강합니다. 이는 마치 multi-PM 헤지펀드의 투자위원회처럼 작동합니다.

이 방법론은 제가 CTI(사이버 위협 인텔리전스) 리포트를 한국어·영어·중국어·일본어 4개국어로 교차 발행하는 노하우와 동일한 패턴입니다.

앞으로 각 LLM의 특징을 이용하여 multi-PM 헤지펀드의 투자위원회처럼 투자의 리스크와 알파를 추구하는 LLM Quant Prompt를 완성하겠습니다.

---

## 수록 전략 (최신 업데이트순)

> 날짜는 각 전략의 최종 수정/작성일 기준입니다.

| 업데이트 | 전략 | 분류 | LLM 교차검증 | 핵심 |
| --- | --- | --- | --- | --- |
| 2026-05-24 | [Midterm Signal](#1-midterm-signal--중간선거-조정장-매수-시그널) | 매크로·타이밍 | 웹검색 기반 | 중간선거 매수 격언을 백테스트로 팩트체크 |
| 2026-05-21 | [AI Super Cycle Weekly Rebalance](#2-ai-super-cycle-weekly-rebalance--ai-슈퍼사이클-주간-리밸런싱) | AI·고위험 트레이딩 | **3-LLM** | NVDA 동적 비중 조절 고위험 |
| 2026-05-18 | [ARDS — Adaptive Recession-Defensive Strategy](#최신-연구--ards--adaptive-recession-defensive-strategy) | 방어·학술 연구 | **4-LLM** | 경기 침체 방어 + 멀티에이전트 가설 |
| 2026-05-04 | [Pharma Sector Long/Short](#3-pharma-sector-longshort--제약-섹터-롱숏) | 섹터(제약·바이오) | **4-LLM** | 제약 메가캡 롱/숏, 양극화 종목 발굴 |
| 2026-05-02 | [AI Supercycle Investment](#4-ai-supercycle-investment--ai-슈퍼사이클-투자) | AI·테크 | 다국어 번들 | AI 가치사슬 4-Layer, 3개 언어 + CSV + 스크리너 |
| 2026-05-02 | [Dividend Growth Prompt](#5-dividend-growth-prompt--배당-성장) | 배당 | **3-LLM** | 배당 성장주 발굴 + "AI도 실수한다" 실증 |
| 2026-05-02 | [Dual-Engine Capital Compounder](#6-dual-engine-capital-compounder--금융리테일-복리) | 배당·자본환원 | 다국어 번들 | 금융+리테일 2-엔진, TCRY 신호 |
| 2026-04-27 | [AI Supply Chain Bayesian Analysis](#7-ai-supply-chain-bayesian-analysis--ai-공급망-베이지안-분석) | 연구·정량분석 | 재현성 프롬프트 | 베이지안 멀티팩터 단기 상승확률 |
| 2026-04-27 | [DAT Quant Strategy](#8-dat-quant-strategy--디지털-자산-기업-평균회귀) | 트레이딩(평균회귀) | Python+Kotlin | DAT 기업↔암호화폐 Z-Score 페어 |
| 2026-04-27 | [Long-Term Dividend Investing](#9-long-term-dividend-investing--장기-배당-투자) | 배당 | 코드 구현 | 장기 배당 종목 선별 코드 |
| 2025-04-26 | [Declining Stock Quant Script](#10-declining-stock-quant-script--하락주--인버스) | 숏·하락 | LLM 프롬프트 | 하락 예상 종목 + 인버스 포지션 |
| (미완성) | [REGIME](#11-regime--거시-레짐-정직한-퀀트) | 매크로·연구 | A/B/C 3접근 | "정직한 퀀트" — 거시는 종목을 설명 못 함 |
| - | [Sample](#sample--새-전략-템플릿) | 템플릿 | - | 새 전략 시작용 표준 구조 |

---

## 산업·전략 유형별 그룹

전략을 **무엇을 사느냐(산업)** 와 **어떻게 접근하느냐(유형)** 로 분류했습니다.

### AI · 반도체 · 테크
인공지능 슈퍼사이클의 핵심 수혜 종목군을 다룹니다.
- [AI Supercycle Investment](#4-ai-supercycle-investment--ai-슈퍼사이클-투자) — AI 가치사슬 4-Layer 분산
- [AI Super Cycle Weekly Rebalance](#2-ai-super-cycle-weekly-rebalance--ai-슈퍼사이클-주간-리밸런싱) — NVDA 동적 비중 (고위험)
- [AI Supply Chain Bayesian Analysis](#7-ai-supply-chain-bayesian-analysis--ai-공급망-베이지안-분석) — 공급망 단기 상승확률

### 배당 · 자본환원 · 인컴
배당 성장과 자사주 매입을 통한 복리 효과를 추구합니다.
- [Dividend Growth Prompt](#5-dividend-growth-prompt--배당-성장) — 6-섹터 배당 성장주
- [Dual-Engine Capital Compounder](#6-dual-engine-capital-compounder--금융리테일-복리) — 금융+리테일 자본환원
- [Long-Term Dividend Investing](#9-long-term-dividend-investing--장기-배당-투자) — 장기 보유 코드

### 섹터 특화 (헬스케어 등)
특정 산업의 고유 동학(파이프라인, 임상 데이터, LOE)을 반영합니다.
- [Pharma Sector Long/Short](#3-pharma-sector-longshort--제약-섹터-롱숏) — 제약·바이오 롱/숏

### 암호화폐 · 디지털 자산
비트코인·이더리움 보유 기업의 평균회귀를 활용합니다.
- [DAT Quant Strategy](#8-dat-quant-strategy--디지털-자산-기업-평균회귀) — DAT 기업 Z-Score 페어 ( 권장하지 않음)

### 숏 · 하락 방어
하락장·조정장에서의 방어와 숏 포지션을 다룹니다.
- [Declining Stock Quant Script](#10-declining-stock-quant-script--하락주--인버스) — 하락주 + 인버스
- [ARDS](#최신-연구--ards--adaptive-recession-defensive-strategy) — 경기 침체 방어 포트폴리오

### 매크로 · 레짐 · 타이밍
시장 전체의 국면 판단과 진입 타이밍을 다룹니다.
- [Midterm Signal](#1-midterm-signal--중간선거-조정장-매수-시그널) — 중간선거 매수 시그널
- [REGIME](#11-regime--거시-레짐-정직한-퀀트) — 거시 레짐 분석

---

## 최신 연구 — ARDS — Adaptive Recession-Defensive Strategy

**업데이트: 2026-05-18 · 4-LLM 교차검증의 결정판**

→ [ARDS 전체 문서 바로가기](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/readme.md)

ARDS는 *경기 침체 진입기에 비대칭 알파를 추구하는 동적 방어 포트폴리오 전략*입니다. 이 컬렉션의 모든 멀티-LLM 교차검증 방법론을 학술 수준으로 집약한 최신 연구물로, AMQS-M7(모멘텀 전략)의 대칭 헤지(Counter-Strategy)로 설계되었습니다.

**왜 이 연구가 중요한가:** ARDS는 단순한 방어 전략을 넘어, "*미래의 퀀트 시스템은 하나의 초지능 AI가 아니라, 서로 다른 투자 철학을 가진 AI들의 위원회(committee)일 가능성이 높다*"는 가설을 4-LLM 교차검증으로 실증합니다.

핵심 발견:

- **매크로 진단은 수렴, 실행은 발산.** 4개 모델 모두 동일하게 "Phase 3 경기침체 경고" 국면으로 진단했으나(표준편차 2.29%p), "무엇을 얼마나 사야 하는가"에서는 비중 합계가 85%(Claude)~225%(DeepSeek)로 **14배의 분산 격차**를 보였습니다.
- **만장일치 종목은 GLD(금) 단 1종.** 25개 종목 중 4개 모델이 모두 동의한 종목은 금 하나뿐. 이는 거시 체제 불안정성에 대한 "보험"으로서 금에 대한 일관된 인식을 보여줍니다.
- **모델별 캐릭터가 헤지펀드 투자위원회와 유사.** Claude(규율 기반 PM) · Gemini(Cash-is-King 리스크 책임자) · ChatGPT(Quant Overlay 전략가) · DeepSeek(공격적 알파 헌터)가 실제 multi-PM 헤지펀드(Millennium, Citadel 등)의 역할 분담과 놀랍도록 유사하게 작동했습니다.

이 연구는 본 컬렉션의 모든 개별 전략이 지향하는 방법론적 종착점입니다.

---

## 전략별 상세 설명

### 1. Midterm Signal — 중간선거 조정장 매수 시그널
**2026-05-24 · 매크로·타이밍**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Midterm%20signal)

"미국 중간선거 해에 조정장이 오면 매수하라"는 오랜 투자 격언(앙드레 코스톨라니의 페타 꼼플리 심리)을 **LLM 프롬프트로 점검하고, 직접 백테스트로 팩트체크**하는 도구입니다.

특징:

- 1938~2022년 22번의 중간선거를 직접 백테스트하여, 흔히 알려진 "1년 뒤 +36%" 주장이 저점 매수를 가정한 상한선이며 현실 기대치는 약 +19%임을 밝힘.
- 승률 95.5%는 사실이나, 1939년(공황·전쟁) 같은 구조적 위기에서는 깨진다는 점, 중간선거 효과 자체가 통계적으로 유의하지 않다는 점을 정직하게 명시.
- 6개 시그널 체크리스트로 현재 시장을 점수화 — 2026년 5월 현재 "매수 금지(2/6점)" 구간으로 판정. *과장 없이 반증 가능한 근거만 사용하도록 설계된 프롬프트.*

### 2. AI Super Cycle Weekly Rebalance — AI 슈퍼사이클 주간 리밸런싱
**2026-05-21 · AI·고위험 트레이딩 · 3-LLM 교차검증**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Ai%20super%20cycle%20weekly%20rebalance%20prompt)

> **고위험 경고**: 단일 종목(NVDA)에 25~44%를 싣는 초고집중 능동 매매 전략입니다. NVDA 단순 장기보유보다 수익이 낮을 가능성이 높으며(보수 시나리오 +38.5% vs NVDA +68.5%), 가치는 "더 버는 것"이 아니라 "하락장에서 덜 깨지는 것"에 있습니다.

GPU 수요 3년 재투자 사이클에 기반해 NVDA 비중을 위상에 따라 동적으로 조절하는 전략입니다.

특징:

- **동일 프롬프트를 Claude·ChatGPT·DeepSeek 3개 모델에 입력한 교차검증 리포트.** 위상 판정(정성)은 만장일치 ACCEL이었으나, NVDA 목표 비중은 35%~44%로 9%p 갈림.
- 발산 원인 3가지(STRESS 캡 해석 차이, ASP 보정 부호 차이, 미배치분 해석 차이)를 분석 — *정량 의사결정을 단일 LLM에 위임하면 안 된다는 강력한 근거.*
- 실무 권장: 3-LLM 중앙값(median) + 사람의 보수적 캡(35%) 적용.

### 3. Pharma Sector Long/Short — 제약 섹터 롱/숏
**2026-05-04 · 섹터(제약·바이오) · 4-LLM 교차검증**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Pharma%20sector%20prompt)

미국 제약 메가캡을 대상으로 12~24개월 호라이즌의 롱/숏 포트폴리오를 구성하는 프롬프트입니다.

특징:

- **4개 모델(ChatGPT·Claude·DeepSeek·Gemini)이 동일 프롬프트에 4개의 다른 포트폴리오를 산출.** BMY·AMGN·GILD·NVO·MRK 등 메가캡의 절반 이상에서 모델 간 포지션이 정반대로 갈림 — 단일 모델 의존이 "모델별 룰렛 게임"임을 입증.
- 모델별 특성 분석: Claude(한국어 audit-ready + 8-K 직접 인용 + contrarian), DeepSeek(영문 기관양식 + 풍부한 M&A 정보), ChatGPT(빠른 outline + stale data), Gemini(압축적 + MDGL 단독 발굴 + MRK 단독 숏).
- 웹검색 활용 여부가 데이터 정확도를 좌우(Claude·DeepSeek는 Q1 2026 실적 반영, ChatGPT·Gemini는 stale data)함을 실증.

### 4. AI Supercycle Investment — AI 슈퍼사이클 투자
**2026-05-02 · AI·테크 · 다국어 번들**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20Supercycle%20Investment%20Quant%20Strategy)

인공지능 슈퍼사이클에 올라타는 미국 주식 퀀트 전략입니다. **한국어·영어·중국어 3개 언어 LLM 프롬프트 + 추천 포트폴리오 CSV 3종 + Python 스크리너(yfinance 기반)** 로 구성된 완성형 번들입니다.

특징:

- AI 가치사슬을 4-Layer(Foundation 반도체 → Infra 하이퍼스케일러 → Enablers 전력·네트워킹 → Application)로 분산하여 10종목 추천.
- 점수 체계: AI 매출 노출도(35%) + 자본 효율·모멘텀(30%) + GARP 밸류에이션(20%) + 모멘텀·수급(15%).
- "줍는 도구가 금보다 중요하다(picks and shovels)"는 철학 — NVDA·TSM·AVGO 등 인프라 종목 중심.

### 5. Dividend Growth Prompt — 배당 성장
**2026-05-02 · 배당 · 3-LLM 교차검증**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dividend%20growth%20prompt)

S&P 500 + NASDAQ-100 배당 성장 종목을 발굴하는 프롬프트이자, **"인공지능도 실수할 수 있다"는 것을 보여주는 실증 사례**입니다.

특징:

- Claude·Gemini·DeepSeek 3사 결과를 실증 비교. 동일 프롬프트에도 3사 모두 동의한 종목은 MSFT·UNH 단 2종.
- 각 모델의 오류를 명시적으로 정정: Gemini의 섹터 오분류 3건(LOW·JPM·COP), DeepSeek의 섹터 위반(LIN)과 에너지 누락, Gemini의 점수 인플레이션(평균 90점), DeepSeek의 Sharpe 1.45 "too good to be true" 의심.
- Claude는 섹터 준수도 A등급·보수적 Sharpe(0.82)·무위험금리 명시로 가장 audit-ready한 출력을 보였으나 토큰 비용 4배의 트레이드오프 존재.

### 6. Dual-Engine Capital Compounder — 금융+리테일 복리
**2026-05-02 · 배당·자본환원 · 다국어 번들**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dual-Engine%20Capital%20Compounder%20Quant%20Strategy%20Using%20LLM)

미국 금융(카드·은행·자산운용)과 리테일(유통) 배당주를 동시에 발굴하는 2-엔진 퀀트 시스템입니다. 한국어·영어·중국어 3개 언어 프롬프트 + CSV + Python 스크리너 번들.

특징:

- **TCRY(Total Capital Return Yield) 핵심 신호** — 단순 배당수익률이 아니라 자사주 매입까지 합산한 "진정한 자본 환원의 복리 효과"를 측정.
- Financial Engine 5종(V·JPM·BLK·AXP·CB) + Retail Engine 5종(HD·TJX·WMT·MCD·TGT).
- 사이클 방어력 점수(15%)를 추가하여 침체 시나리오 대비 — 2008 GFC 배당 컷 사례(BAC -90%, C -97%)를 위험 고지에 반영.

### 7. AI Supply Chain Bayesian Analysis — AI 공급망 베이지안 분석
**2026-04-27 · 연구·정량분석 · 재현성 프롬프트**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20supply%20chain%20bayesian%20analysis)

AI 공급망 종목의 단기(5~20거래일) 상승 확률을 **베이지안 멀티팩터 프롬프트**로 분석하는 LLM 기반 퀀트 분석 도구입니다.

특징:

- 거시 환경(금리·VIX·AI Capex)을 사전 확률(Prior)로 설정한 뒤, 우도비(LR)로 사후 하락 확률을 업데이트하는 베이지안 사고 프레임.
- 5개 레이어(GPU/AI 가속기 → HBM/메모리 → 데이터센터 네트워킹 → 스토리지 → NPU/온디바이스) × 3대 팩터(기술적 30% + 펀더멘털·거시 30% + 수급·심리·매크로 40%).
- 출력의 구조적 일관성(종목 명시·가중치 고정·형식 강제·산식 명시)을 통해 *"같은 프롬프트로 동일 형식의 보고서를 재생성"* 가능한 재현성 강조. 점수는 절대값이 아닌 상대 순위로만 활용.

### 8. DAT Quant Strategy — 디지털 자산 기업 평균회귀
**2026-04-27 · 트레이딩(평균회귀) · Python+Kotlin**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/DAT%20quant%20strategy)

> **솔직한 조언**: 비트코인 노출을 원한다면, MSTR 같은 DAT 기업의 평균회귀를 노리기보다 **비트코인을 직접 구매하는 것이 낫습니다.** DAT 기업은 희석·부채·경영 결정 등 equity-specific 리스크를 추가로 떠안으며, Spot BTC ETF·GENIUS Act 등 regime change 시 과거 프리미엄 패턴이 무효화될 수 있습니다. 이 전략은 *이미 DAT 기업을 보유하기로 결정한 사람의 진입 타이밍 식별용*일 뿐입니다.

DAT(Digital Asset Treasury) 기업의 주가와 보유 암호화폐 가격 간 평균회귀를 활용한 Z-Score 페어 트레이딩 시그널 스크립트입니다.

특징:

- 7개 페어(MSTR·MARA·RIOT·GLXY·COIN·BMNR·SBET) 대상 90일 Rolling Z-Score (Z≤-2 매수, Z≥+2 매도, look-ahead bias 방지).
- **Python + Kotlin 동시 구현** — 365일 무중단 핀테크 백엔드(JVM) 환경을 위한 Kotlin 버전 제공.
- MSTR-BTC 페어 상관계수 r≈0.87. 단, 위 경고대로 평균회귀는 상관관계 지속을 전제하므로 구조적 프리미엄 압축 시 무효 가능.

### 9. Long-Term Dividend Investing — 장기 배당 투자
**2026-04-27 · 배당 · 코드 구현**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Long-Term%20Dividend%20Investing)

장기 배당 투자를 위한 종목 선별 스크립트입니다. 단순 배당수익률이 아니라 배당 성장성·지속 가능성·페이아웃 비율·재무 건전성을 종합 평가합니다.

특징:

- Dividend Growth Prompt(프롬프트 중심)의 **코드 구현 보완판** — 은퇴 자금 운용, 인컴 포트폴리오 구성, 배당 귀족주(Dividend Aristocrats) 후보 발굴에 활용.
- 장기 보유 관점에서 페이아웃 비율과 재무 건전성을 핵심 필터로 사용.

### 10. Declining Stock Quant Script — 하락주 + 인버스
**2025-04-26 v1.0 · 숏·하락 · LLM 프롬프트**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Declining%20Stock%20Quant%20Script%20Using%20LLM)

S&P 500·NASDAQ-100 구성 종목 중 향후 1~4주 내 하락 가능성이 높은 종목을 LLM이 선별하고, 대응하는 인버스(숏) 종목까지 제시하는 프롬프트입니다.

특징:

- 멀티팩터 모델: 기술적 분석(40%, 과매수·데드크로스·헤드앤숄더) + 펀더멘털(30%, 고PER·FCF 악화) + 수급/심리(30%, 내부자 매도·풋옵션 급증·부정 감성).
- 하락 종목별로 인버스 ETF를 매칭하되, **인버스 ETF의 변동성 부패(volatility decay)** — 일일 리밸런싱 구조로 1일 초과 보유 시 추적오차 누적 — 를 명시적으로 경고.

### 11. REGIME — 거시 레짐, "정직한 퀀트"
**(미완성) · 매크로·연구**
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/REGIME)

> **주의: 아직 미완성입니다. 금융공학적 지식이 없다면 이 퀀트로 투자에 이용하지 마세요.**

거시 변수(환율·금리·물가·소비심리·유가)와 M7 + AI 인프라 종목의 관계를 **정직하게** 분석하는 퀀트 프롬프트 + Python 파이프라인입니다.

특징:

- **핵심 결론: 거시는 종목을 거의 설명하지 못한다** (주간 회귀 R² 1~3%). 거시 레짐은 "언제 시장에 있을지(타이밍)"는 알려주지만 "어떤 종목을 고를지(종목 선택)"는 알려주지 않습니다. QQQ 베타를 제거하면 종목 고유 알파의 레짐 의존성이 거의 사라짐(유의 종목 3/17 → 1/17).
- A/B/C 3가지 접근(규칙 기반 레짐+모멘텀 / 회귀 적정가 / 비지도 레짐+베타중립 잔차).
- 이 프레임워크의 진짜 가치는 *"틀린 확신을 통계로 막아주는 정직성"* — LLM이 데이터가 뒷받침하지 않는 자신감 있는 시그널을 억지로 만들지 않도록 설계.

### Sample — 새 전략 템플릿
→ [폴더 바로가기](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Sample)

새 전략을 만들 때 사용할 표준 구조(README, 스크립트, 데이터, 백테스트, 한계) 템플릿 폴더입니다.

---

## 권장 사용 순서

1. 이 README에서 **Multi-LLM Cross-Validation 철학**을 먼저 이해
2. 본인 관심 영역(AI / 배당 / 섹터 / 매크로 등)에 맞는 그룹에서 전략 선택
3. 해당 전략의 폴더 README와 **한계·위험 고지** 섹션 정독
4. 프롬프트를 **최소 2개 이상의 LLM**에 입력하여 교차검증
5. 합의 종목(Consensus)과 분열 종목(Divergence)을 구분
6. 분열 종목은 SEC EDGAR·Morningstar 등 **1차 출처로 직접 검증**
7. 백테스트 데이터 재현 → 페이퍼 트레이딩 → (그 후에야) 실거래 고려

---

## Disclaimer

모든 스크립트와 프롬프트는 **연구·교육 목적의 가상 시뮬레이션**이며, 실제 투자 권유가 아닙니다.

- LLM이 생성한 분석·점수·확률은 추정치이며, 실제 통계 모델 결과가 아닙니다. 백테스트 결과는 슬리피지·수수료·세금이 미반영된 경우가 많습니다(illustrative only).
- LLM은 환각(hallucination), look-ahead bias, survivorship bias를 가질 수 있으므로 **반드시 독립 데이터 소스로 교차 검증**해야 합니다.
- 한국 거주자: 해외주식 양도소득세 22% + 외환거래법 신고 의무 + 종합과세 별도 확인 필요.
- DeepSeek 같은 중국 LLM 사용 시 지정학적 위험을 별도 검토하시기 바랍니다.
- 모든 투자 판단과 그 결과의 책임은 전문가 상담 후 투자자 본인에게 있습니다.

자세한 내용은 [메인 README의 Disclaimer](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md#disclaimer)를 참조하세요.

---

## 저자

**김호광 (Dennis Kim / HoKwang Kim)**

- Betalabs Inc. CEO · Independent Researcher
- Microsoft Azure MVP (Long-tenured) · Former CEO, CyworldZ
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · Email: <gameworker@gmail.com>

**관심 분야**: Cyber Threat Intelligence · AI-Assisted Solo Entrepreneurship · Quant Finance · Cross-Lingual LLM Behavior · Multi-Agent AI Systems

---

> *"하나의 LLM은 환각을 만들 수 있다. 세 LLM이 합의할 때 진실에 가까워진다 — 그러나 그들이 의견이 갈릴 때, 비로소 알파를 발견한다."*

**시리즈**: vibe-investing — Awesome Claude Quant Scripts · **라이선스**: MIT
