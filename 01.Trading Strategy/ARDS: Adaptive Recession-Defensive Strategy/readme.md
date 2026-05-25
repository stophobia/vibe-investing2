# ARDS — Adaptive Recession-Defensive Strategy

> *"미래의 퀀트 시스템은 하나의 초지능 AI 가 아니라, 서로 다른 투자 철학을 가진 AI 들의 committee 일 가능성이 높다. 본 연구는 그 가설을 4-LLM 교차검증으로 실증한 초기 사례다."*

주의: 이 전략은 매우 위험한 전략이며, 투자자의 경험과 인사이트가 있어야 합니다.

**시리즈**: vibe-investing — AMQS 의 대칭 헤지 (Counter-Strategy)
**저자**: 김호광 (Dennis Kim / HoKwang Kim) · Betalabs Inc. · ORCID [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
**작성일**: 2026-05-18
**라이선스**: MIT

---

## 1. 한눈에 보기 (TL;DR)

ARDS 는 *경기 침체 진입기에 비대칭 알파를 추구하는 동적 방어 포트폴리오 전략* 입니다. AMQS-M7 (Adaptive Momentum Quant Strategy for M7) 의 **반대, 리버스** 으로 설계되었으며, 다음 세 가지를 동시에 검증합니다.

1. **전략 자체 (Strategy)** — 5-Dimension 100점 채점 × 4-Tier Universe × 4-Phase 거시 레짐
2. **4-LLM 교차검증 (Cross-Validation)** — 동일 프롬프트를 Claude / Gemini / ChatGPT / DeepSeek 에 입력 후 비교 분석
3. **연구 가설 (Hypothesis)** — *"LLM 들은 동일 프롬프트에도 서로 다른 투자 철학을 형성하며, 이들의 ensemble 은 multi-manager hedge fund 의 의사결정 구조와 유사하게 작동한다"*

### 실험 결과 핵심 (2026-05-17 스냅샷)

| 차원 | 결과 |
|---|---|
| **매크로 진단 합의** | 4 모델 모두 Phase 3 Recession-Warning (Composite 표준편차 2.29%p) |
| **실행 단계 분산** | 비중 합계 85% (Claude) ~ 225% (DeepSeek) — *2.6배 격차* |
| **만장일치 FTQ** | **GLD 단 1종목 (25 중 1)** |
| **시그널 분열** | 25 종목 중 10종목 (40%) 에서 2-of-4 분열 |
| **합의 비중 (Weight) 상관** | Claude ↔ DeepSeek r=0.750, ChatGPT ↔ DeepSeek r=0.782 |

> **핵심 발견**: *진단 일치 ≠ 처방 일치*. LLM 들은 "지금이 침체 경고 구간인가?" 에는 정보 비대칭 없이 합의했으나, "그래서 무엇을 얼마나 사야 하는가?" 에서는 *서로 다른 투자 철학을 자연스럽게 형성*했습니다.

---

## 2. ARDS 전략 개요

### 2.1 설계 철학

ARDS 는 AMQS-M7 의 **다섯 가지 핵심 가설을 정확히 뒤집은 대칭 전략** 입니다.

| 차원 | AMQS-M7 (Momentum) | **ARDS (Defensive)** |
|---|---|---|
| D1 핵심 시그널 | 4-Factor Momentum Composite (35%) | **5-Factor Recession Composite (30%)** |
| D2 비대칭 진입 | Pullback-in-Uptrend (15%) | **Counter-Cyclical Strength (20%)** |
| D3 펀더멘털 | 가속도 (25%) | **Defensive Quality (20%)** |
| D4 변동성 | 모멘텀 알파 (15%) | **Downside Protection (20%)** |
| D5 거시 환경 | 10% | 10% |
| 특수 시그널 | DIP_BUY | **FLIGHT_TO_QUALITY** |
| 거시 레짐 | 3단계 | **4단계 (Expansion / Late-Cycle / Recession-Warning / Recession)** |
| Universe | M7 7종목 | **4-Tier 25종목** |

### 2.2 4-Tier Universe

```
┌─ Tier 1 (방어 섹터 ETF / Always-On Core)
│   XLP · XLV · XLU · VPU · VHT
│
├─ Tier 2 (경기 침체 헤지 ETF / Always-On Hedge)
│   TLT · IEF · SHV · GLD · IAU · BIL
│
├─ Tier 3 (개별 방어주 / Quality Defensives)
│   BRK-B · WMT · COST · JNJ · KO · PG · PEP · NEE · VZ · ABBV
│
└─ Tier 4 (Tactical Inverse / Volatility, Late-Cycle-Only)
    SH · PSQ · VIXY · DOG
```

Tier 4 는 Expansion Phase 에서는 **강제 0% 비중** — 진입 자체가 금지됩니다. Late-Cycle 이상에서만 부분 활성화되며, VIXY 는 콘탱고 구조로 인해 **30일 강제 청산 룰** 이 적용됩니다.

### 2.3 4-Phase 거시 레짐

| Phase | 5-Factor Composite | 방어 비중 | Tier 4 활성 |
|---|---|---|---|
| 1. Expansion | < 25% | 30% | 금지 |
| 2. Late-Cycle | 25–50% | 55% | 부분 (~5%) |
| 3. Recession-Warning | 50–70% | 80% | 활성 (5–10%) |
| 4. Recession | > 70% | 100% | 최대 (15%) |

**2026-05-17 현재**: 4 모델 모두 Phase 3 Recession-Warning 으로 진단 (Composite 61.14% ± 2.29%p).

### 2.4 5-Factor Recession Composite

|성분|가중치|핵심 지표|
|---|---|---|
| A | 30% | Yield Curve Inversion (10Y-3M, 10Y-2Y) — NY Fed 모델 표준 |
| B | 25% | Sahm Rule (실업률 3M MA - 12M 최저치) |
| C | 15% | ISM Manufacturing PMI |
| D | 15% | Conference Board LEI 6M 변화율 |
| E | 15% | HY OAS + Chicago Fed NFCI |

**상세 프롬프트**: [한국어](./prompts/ARDS_kr.MD) · [English](./prompts/ARDS_en.MD) · [中文](./prompts/ARDS_cn.MD)

---

## 3. 본 연구의 가장 중요한 발견

### 3.1 매크로 진단의 LLM 간 수렴

```
4-Model Recession Composite (2026-05-17 스냅샷)

  Gemini   ████████████████ 63.30%
  Claude   ████████████████ 62.25%
  DeepSeek ████████████████ 61.00%
  ChatGPT  ███████████████  58.00%
                            ───────
  Mean     ████████████████ 61.14%  (σ=2.29%p, CV=3.7%)
```

이는 *금융공학적으로 매우 의미 있는 결과* 입니다. 4개의 독립적으로 훈련된 frontier LLM 이 동일 매크로 지표 (역수익률 곡선, Sahm Rule, ISM, LEI, HY OAS) 를 입력받았을 때, **표준편차 2.29%p 내로 합의**한다는 것은:

> *Top-down macro classification 영역에서 LLM 간 정보 비대칭은 사실상 사라졌다.*

### 3.2 실행 단계의 폭발적 분산

반면, 동일한 진단을 받고도 *어떤 자산을 얼마나 사야 하는가* 는 완전히 갈렸습니다.

| 항목 | 변동계수 (CV) | 해석 |
|---|---|---|
| Macro Composite | **3.7%** | 거의 완벽한 합의 |
| Total Score | 8% | 종목 평가 유사 |
| Recommended Weight | **52%** | **극단적 분산** |

| 모델 | 비중 합계 | Phase 3 사양 (80%) 대비 |
|---|---|---|
| Claude | 85.0% | **(사양 준수)** |
| Gemini | 101.0% | *(약간 초과)* |
| ChatGPT | 149.4% | *(1.87배 초과)* |
| DeepSeek | 224.6% | *(2.81배 초과)* |

### 3.3 유일한 만장일치 — GLD

25 종목 중 *4 모델 모두 FLIGHT_TO_QUALITY 부여한 종목은 GLD 단 1종목* (4%). 이는 단순 "금이 좋다" 수준이 아닙니다. 4 모델 모두

- 인플레이션 재가속 (4월 CPI 3.8%)
- 호르무즈 봉쇄 → 지정학 리스크
- 달러 신뢰 약화 (DXY 약세 추세)
- 실질금리 구조 변화
- Recession-Warning regime 진입

이라는 다층적 위험 구조 속에서, **금을 "거시 체제 불안정성에 대한 보험"** 으로 일관되게 인식했다는 의미입니다.

---

## 4. 모델별 Character Profile

본 실험에서 가장 흥미로운 발견은, **동일 프롬프트를 받은 4개 LLM 이 서로 완전히 다른 "포트폴리오 매니저 페르소나"를 자연스럽게 형성**했다는 점입니다.

### 4.1 Claude — "Spec Adherent (규율 기반 리스크 관리자)"

| 지표 | 값 |
|---|---|
| 비중 합계 | **85.0%** ← Phase 3 사양 80%에 가장 근접 |
| Tier 비중 | T1: 30 / T2: 30 / T3: 15 / T4: 10 (사양 정확히 일치) |
| 평균 Beta | 0.58 (가장 엄격한 저베타) |
| FTQ 시그널 수 | 12 (가장 광범위 분산) |

**평가**: 가장 institutional PM 에 가까운 출력. 규칙 기반 시스템 구현 능력 최고. *알파 추구 성향이 약함*이 트레이드오프.

### 4.2 Gemini — "Cash is King (Macro Risk Officer)"

| 지표 | 값 |
|---|---|
| FTQ 시그널 분포 | **SHV, BIL, GLD, IAU** ← 단기채/금만 |
| 평균 Beta | 0.77 (가장 완화) |
| TLT 평가 | TACTICAL (듀레이션 위험 최강 경계) |

**평가**: "지금은 공격보다 생존이 우선". 기관 treasury desk · 보험사 ALM 성향과 유사. *Tail-risk 회피 능력 우수*. 강세장 기회비용이 큰 것이 단점.

### 4.3 ChatGPT — "ETF-Only Doctrine (Quant Overlay Strategist)"

| 지표 | 값 |
|---|---|
| CORE 시그널 사용 | **유일하게 활용** (XLU, VPU, XLV, VHT) |
| FTQ 분포 | ETF 6종목만 — **개별주 0종목** |
| 회전율 제시 | 96% (유일) |
| 기회비용 정량화 | Phase 1 -0.7%/yr (유일) |

**평가**: 전략 설명 능력과 구조화 능력 최고. *기회비용까지 정량화*한 유일 모델. *지나친 ETF 선호* 가 한계.

### 4.4 DeepSeek — "Aggressive Alpha Hunter (Hedge Fund PM)"

| 지표 | 값 |
|---|---|
| 비중 합계 | **224.6%** ← 사실상 leverage portfolio |
| FTQ 분포 | Equity 방어주 중심 (XLP, XLV, XLU, VPU, GLD, KO) |
| Phase 3 outperformance | **+6.2%p/yr** (가장 공격적 알파) |

> **DeepSeek 의 출신 맥락**: DeepSeek 는 중국 양적 헤지펀드 **High-Flyer (幻方量化, Liang Wenfeng 설립)** 의 AI 연구 부서에서 출범한 LLM 입니다. 이 헤지펀드 DNA 가 모델의 의사결정 character 에 그대로 반영된 것으로 보입니다 — 즉, *상대 강도 기반 알파 추구* 와 *공격적 ranking* 이라는 quant hedge fund 특유의 사고방식이 출력에 그대로 드러납니다. 다른 3개 모델이 일반 목적 (general-purpose) LLM 인 반면, DeepSeek 의 *상대적으로 공격적인 비중 배분과 ranking 중심 사고* 는 이 출신 배경으로 부분 설명 가능합니다.

**평가**: Alpha 아이디어 발굴 능력 1위. 다만 *절대 비중은 직접 사용 불가* — 상대 ranking 으로만 활용해야 합니다.

---

## 5. ChatGPT 최종 Synthesis Report (요약)

> 본 섹션은 ChatGPT 가 4-LLM 출력을 메타 분석한 최종 결론 보고서의 핵심 내용입니다. ChatGPT 의 *Quant Overlay Strategist* character 가 가장 잘 드러나는 출력이므로, 본 연구의 결론부에 그대로 통합합니다.

### 5.1 가장 중요한 한 문장

> **지금은 침체 경고 구간이며, 가장 확실한 공통 투자 아이디어는 GLD(금) 이다.**

### 5.2 4-Model 합의 영역

**거시 환경 합의:**
- Phase 3 Recession-Warning
- 방어 자산 비중 확대 필요
- Tier 4 부분 활성화
- 강세장 대비 기회비용 존재
- BEAR_TRAP 가능성 경계
- TLT 듀레이션 위험
- VIXY 콘탱고 손실 인식

**만장일치 종목:**
- FLIGHT_TO_QUALITY: **GLD**
- SATELLITE: ABBV · BRK-B · COST · NEE · VZ

**3-of-4 합의:**
- FLIGHT_TO_QUALITY: XLP · IAU
- SATELLITE: XLU · XLV · TLT · IEF · SHV · VPU · KO · WMT · JNJ
- TACTICAL: VIXY (30일 제한)

### 5.3 최대 분열 영역

| 영역 | 핵심 논쟁 |
|---|---|
| 현금성 자산 (BIL / SHV) | "현금=최고 방어" (Gemini) vs "현금=죽은 자산" (DeepSeek) |
| TLT (장기채) | 금리 인하 수혜 (Claude/ChatGPT) vs 인플레 재가속 위험 (Gemini) |
| Equity Defensives | 사야 한다 (Claude/DeepSeek) vs 회피 (Gemini) |

이 분열은 *실제 글로벌 헤지펀드 투자위원회에서 벌어지는 논쟁과 매우 유사* 합니다:

- 보험사 · 연기금 · treasury → Gemini 와 같은 입장
- 헤지펀드 · 글로벌 macro PM → DeepSeek 와 같은 입장

> *즉, LLM 들은 단순히 다른 답을 낸 것이 아니라, 다른 종류의 institutional player 의 사고방식을 자연스럽게 재현했다.*

### 5.4 핵심 논쟁 — "이번 침체의 성격"

TLT 에 대한 4-Model 분열은 본질적으로 다음 질문에 대한 해석 차이입니다:

> *"이번 침체는 disinflation recession 인가, 아니면 sticky inflation recession 인가?"*

- **disinflation recession 가정** → 금리 인하 → TLT 매수 (Claude, ChatGPT)
- **sticky inflation recession 가정** → 금리 고착 → TLT 회피 (Gemini, DeepSeek)

본 연구 시점 (2026-05) 의 4월 CPI 3.8% 서프라이즈 + 호르무즈 봉쇄 장기화는 후자에 더 가까운 환경이므로, *Gemini/DeepSeek 의 TLT 회피 입장이 단기적으로 더 적합* 할 가능성이 있습니다.

### 5.5 Ensemble Phase 3 권장 포트폴리오 (총 80%)

```
Tier 1 (30%): 방어 섹터 ETF
  XLP 10% · XLV 8% · XLU 6% · VPU 3% · VHT 3%

Tier 2 (30%): 침체 헤지
  GLD 12% · IAU 6% · TLT 6% · IEF 3% · SHV 3%

Tier 3 (15%): 개별 Quality 방어주
  BRK-B 3% · ABBV 3% · COST 3% · NEE 3% · VZ 3%

Tier 4 (5%): Tactical Hedge (30일 제한)
  SH 2% · PSQ 2% · VIXY 1%

현금 (20%): 리스크 버퍼
```

### 5.6 실무 운용 6대 규칙

1. **Claude 비중 구조를 기준 포트폴리오**로 사용
2. **ChatGPT 의 백테스트 및 기회비용 분석**을 overlay 로 활용
3. **Gemini 의 현금 방어 논리**를 risk-off 시 참고
4. **DeepSeek 의 종목 우선순위**를 보조 ranking 신호로 활용
5. 모든 비중은 **총 80% 로 정규화** 필수
6. **최소 2개 이상 LLM 이 동의한 종목**만 채택

> **ChatGPT 의 전체 최종 결론 보고서**: [ARDS_4_LLM_Master_Final_Conclusion.md](./reports/ARDS_4_LLM_Master_Final_Conclusion.md)

---

## 6. Working Paper 가설 — Multi-Agent Portfolio System

본 연구의 가장 중요한 학술적 함의는 다음 가설로 정리됩니다:

### 6.1 Core Hypothesis

> **H1 — Philosophical Divergence Hypothesis**
> 동일 프롬프트와 동일 정보를 받아도, 서로 다른 frontier LLM 들은 *학습 데이터 · 아키텍처 · post-training reward signal 의 누적적 결과* 로 인해 서로 다른 *투자 철학적 character* 를 자연스럽게 형성한다.

> **H2 — Macro-Execution Decoupling Hypothesis**
> LLM 들은 *top-down macro classification* 에서는 높은 합의를 보이지만, *bottom-up portfolio construction* 에서는 극단적 분산을 보인다. 이 두 단계는 사실상 서로 다른 추론 메커니즘에 기반한다.

> **H3 — Multi-Agent Ensemble Hypothesis**
> 서로 다른 character 의 LLM 들을 ensemble 한 의사결정은 *단일 LLM 의 출력보다 multi-PM hedge fund 의 투자위원회 의사결정 구조에 더 가깝게 작동* 한다.

### 6.2 본 연구의 실증적 근거

| 가설 | 본 연구의 정량 증거 |
|---|---|
| H1 | 4 모델의 character profile 이 명확히 구분됨 (Claude=Spec Adherent, Gemini=Cash-is-King, ChatGPT=ETF Doctrine, DeepSeek=Alpha Hunter) |
| H2 | Macro Composite CV=3.7% vs Weight CV=52% — **14배 분산 격차** |
| H3 | 40% 종목에서 4-Model 분열 → 단일 LLM 신뢰 불가능, ensemble 필수 |

### 6.3 미래 퀀트 시스템의 함의

본 연구의 결과는 *"퀀트 투자의 미래는 단일 초지능 AI 가 아니다"* 라는 명제를 시사합니다:

![Single Super-AI vs Multi-Agent Committee — 본 연구가 시사하는 차세대 퀀트 의사결정 구조](./ards_multi_agent_committee.svg)

**전통적 가정**: 더 큰 단일 모델 → 더 나은 의사결정
**본 연구가 시사하는 대안**: *서로 다른 투자 철학을 가진 multi-agent committee* → 단일 모델보다 robust 한 의사결정

### 6.4 실제 hedge fund 구조와의 유사성

본 실험에서 관찰된 4-LLM ensemble 의 작동 방식은 **실제 multi-PM hedge fund (예: Millennium, Citadel, Point72) 의 투자위원회 구조와 놀랍게 유사** 합니다:

| 실제 Hedge Fund 역할 | 본 실험의 LLM 대응 |
|---|---|
| Chief Risk Officer | Gemini (Tail-risk 보수) |
| Multi-Strategy PM | Claude (규율 기반 분산) |
| Quant Research Head | ChatGPT (체계화 · 백테스트) |
| Aggressive Sector PM | DeepSeek (Alpha 추구) |
| Investment Committee | Ensemble Voting |

특히 DeepSeek 가 *실제 중국 헤지펀드 (High-Flyer, 幻方量化) 의 quant DNA 를 그대로 계승한 LLM* 이라는 사실은, **LLM 의 base distribution 자체가 institutional player 의 사고 패턴을 내재화하고 있음**을 시사합니다.

### 6.5 향후 연구 방향

본 연구가 working paper 로 발전한다면 다음 후속 연구가 가능합니다:

1. **Persona stability testing** — 시간/시나리오/언어를 바꿔도 동일 LLM 의 character 가 유지되는가? (저자의 "Same LLM, Different Languages" 시리즈 v6 으로 확장 가능)
2. **Out-of-sample validation** — 본 ensemble 권장 포트폴리오를 6/12/24개월 실제 시장에서 검증
3. **Optimal voting weight estimation** — 4 모델의 voting weight 를 어떻게 최적화할 것인가? (Black-Litterman 응용 가능)
4. **Adversarial robustness** — 동일 프롬프트에 미세 변화 (noise) 를 주었을 때 character 가 무너지는가?
5. **Multi-strategy expansion** — ARDS 외 다른 전략 (Momentum, Mean-Reversion, Macro) 에서도 동일 character 가 일관되게 나타나는가?

이 다섯 가지 후속 질문이 모두 검증되면, 본 연구는 **"AI 기반 멀티-매니저 포트폴리오 시스템 (AI-MMP)" 의 이론적 기초**가 될 수 있습니다.

---

## 7. 핵심 통계 요약

### 7.1 4-Model 합의도 매트릭스

| 항목 | 합의 수준 | 정량 지표 |
|---|---|---|
| Macro Regime Phase | 100% 합의 | 4/4 모두 Phase 3 |
| 5-Factor Composite 절댓값 | 강한 합의 | σ=2.29%p, CV=3.7% |
| Total Score per ticker | 중간 합의 | 평균 CV=0.08 |
| Recommended Weight | 약한 합의 | 평균 CV=0.52 |
| Signal (시그널 등급) | 24% 만장일치 | 6/25 종목 (4/4 동의) |
| FTQ 시그널 | 만장일치 1종목 | GLD 만 |

### 7.2 모델 간 상관관계

**Total Score Correlation:**
```
              Claude   Gemini   ChatGPT   DeepSeek
   Claude     1.000   -0.199    0.286     0.616
   Gemini    -0.199    1.000    0.318    -0.372
   ChatGPT    0.286    0.318    1.000    -0.047
   DeepSeek   0.616   -0.372   -0.047     1.000
```

**Weight Correlation:**
```
              Claude   Gemini   ChatGPT   DeepSeek
   Claude     1.000    0.198    0.605     0.750
   Gemini     0.198    1.000    0.403     0.358
   ChatGPT    0.605    0.403    1.000     0.782
   DeepSeek   0.750    0.358    0.782     1.000
```

> **관찰**: Gemini 는 다른 3 모델과 모두 약한 또는 음의 상관 → 가장 *outlier persona* 형성.

---

## 8. Repository Structure

```
vibe-investing/01.Trading Strategy/ARDS — Adaptive Recession-Defensive Strategy/
│
├── README.md                                  ← 본 문서
├── ards_multi_agent_committee.svg             ← 6.3 챕터 다이어그램
│
├── prompts/                                   ← ARDS 프롬프트 (3개 언어)
│   ├── ARDS_kr.MD                            ← 한국어판
│   ├── ARDS_en.MD                            ← English
│   └── ARDS_cn.MD                            ← 中文
│
├── outputs/                                   ← 4-LLM 출력 원본 CSV
│   ├── claude_0518.csv
│   ├── gemini_0518.csv
│   ├── chatgpt_0518.csv
│   └── deepseek_csv_20260517_84dd88.csv
│
├── analysis/                                  ← 메타 분석 결과
│   ├── ARDS_LLM_Comparison_20260518.MD       ← 4-LLM 비교 분석 (Claude 작성)
│   ├── ARDS_signal_agreement.csv             ← 시그널 합의도
│   ├── ARDS_total_score_pivot.csv            ← 점수 피벗
│   └── ARDS_weight_pivot.csv                 ← 비중 피벗
│
└── reports/                                   ← 최종 결론 보고서
    └── ARDS_4_LLM_Master_Final_Conclusion.md ← ChatGPT 최종 Synthesis
```

---

## 9. 연관 시리즈

본 연구는 *vibe-investing* 시리즈의 일부이며, 다음 전략들과 연결됩니다:

| 전략 | 역할 | 링크 |
|---|---|---|
| AMQS 원본 | Momentum (NASDAQ-100 + AI Value Chain) | [Link](../Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD) |
| AMQS-M7 | Momentum (M7 + Pullback-in-Uptrend) | [Link](../Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD) |
| **ARDS** | **Defensive (4-Tier + Counter-Cyclical)** | **본 repo** |

**Portfolio pairing 권장**: AMQS-M7 + ARDS 를 50:50 으로 병행 운용 시, 시장 베타 ~0.5 + 침체 진입 시 비대칭 알파 동시 확보 가능.

---

## 10. 인용 (Citation)

본 연구를 학술적으로 인용하는 경우:

```bibtex
@misc{kim2026ards,
  author       = {Kim, HoKwang (Dennis)},
  title        = {ARDS: Adaptive Recession-Defensive Strategy and the
                  Multi-Agent Portfolio System Hypothesis — A 4-LLM
                  Cross-Validation Study},
  year         = {2026},
  month        = {May},
  publisher    = {GitHub},
  journal      = {vibe-investing series},
  howpublished = {\url{https://github.com/gameworkerkim/vibe-investing}},
  note         = {ORCID: 0009-0002-0962-2175}
}
```

---

## 11. 면책 조항

본 자료는 *교육 및 연구 목적의 LLM 시뮬레이션 결과* 이며, 특정 종목의 매수·매도를 권유하는 것이 아닙니다. 본 연구에 포함된 모든 백테스트 결과는 LLM 이 생성한 시뮬레이션 데이터이므로, **실제 시장 데이터와 일치하지 않을 수 있습니다**. 신호 부분 (Signal/Tier/Phase) 만 참고하고, 백테스트 수익률 절댓값은 *환상적 데이터 (synthetic)* 로 다뤄야 합니다.

특히:
- *방어형 전략은 강세장에서 큰 기회비용을 발생* 시킵니다
- *Tier 4 (Inverse/VIXY) 는 장기 보유 시 100% 손실에 수렴* 하므로 30일 청산 규칙을 반드시 준수해야 합니다
- *4-LLM ensemble 도 ground truth 가 아니며*, 사람의 최종 검토가 필요합니다

모든 투자 판단과 그에 따른 책임은 투자자 본인에게 있습니다.

---

## 12. 저자 정보

**김호광 (Dennis Kim / HoKwang Kim)**
- Betalabs Inc. CEO · Independent Researcher
- Microsoft Azure MVP (Long-tenured)
- Former CEO, Cyworld Z
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- Email: gameworker@gmail.com

**관심 분야**: Cyber Threat Intelligence · AI-Assisted Solo Entrepreneurship · Quant Finance · Cross-Lingual LLM Behavior · Multi-Agent AI Systems

---

> *"In a bull market, defense is a tax. In a bear market, defense is oxygen. But the real insight from this experiment is that there is no single AI that breathes for you — there are only four AIs with four different lungs, and you breathe best when they breathe together."*

---

**라이선스**: MIT
**최종 수정**: 2026-05-18
