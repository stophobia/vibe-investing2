# 영문 프롬프트 결과 비교 분석

> **S&P 500 + NASDAQ-100 배당 성장 종목 발굴 — Claude / DeepSeek / Gemini 영문 프롬프트 결과 실증 비교**
> **Comparison Results of 3 Types of LLM (Korean, English, Quant Prompt)**

## 한 줄 요약

영문 프롬프트로 실행하면 한국어 대비 **종목 구성이 크게 바뀌고**, **새로운 유형의 hallucination이 등장**하며, 한국 투자자 컨텍스트는 사라진다.

---

## 비교 대상 파일

| LLM | 파일 | 분량 | 라인 수 |
|---|---|---|---|
| **Claude Opus 4.7** | [claude_dividend_growth_portfolio_2026Q2.md](claude_dividend_growth_portfolio_2026Q2.md) | 32.4KB | 541 lines |
| **DeepSeek V3.1/V4** | [deepseek_markdown_20260502_2c64e1.md](deepseek_markdown_20260502_2c64e1.md) | 14.8KB | 245 lines |
| **Gemini 3 Flash** | [gemini_report.md](gemini_report.md) | 5.04KB | 78 lines |

> 한국어 결과 비교는 [상위 폴더 Readme.md](../../Readme.md) 참조. 본 문서는 **영문 결과만** 비교합니다.

---

## 평가 환경

| 항목 | 내용 |
|---|---|
| 프롬프트 | [Dividend_Growth_Prompt_EN.md](../../Dividend_Growth_Prompt_EN.md) (영문판, 토큰 31% 절감판) |
| 실행일 | 2026년 5월 2일 |
| Temperature | 기본값 (각 LLM default) |
| 평가 방식 | 단일 실행 (N=1) — 통계적 유의성 없음, 정성적 관찰만 |

> **출력 분량 차이**: 한국어 결과 대비 Claude는 32% 증가, DeepSeek는 44% 증가, Gemini는 14% 감소. 영문 출력이 일반적으로 토큰을 더 효율적으로 사용함을 보여줌 (단 Gemini 제외).

---

## Part 1 — Top 10 종목 비교

### 1.1 영문 결과 통합 매트릭스

| 티커 | 회사명 | Claude(EN) | DeepSeek(EN) | Gemini(EN) | 추천 LLM 수 | 평균 점수 |
|---|---|---|---|---|---|---|
| **MSFT** | Microsoft | 87 (#1) | 88 (#6) | 89 (#3) | **3사 일치** | **88.0** |
| **V** | Visa | 86 (#2) | 92 (#4) | 91 (#2) | **3사 일치** | **89.7** |
| **UNH** | UnitedHealth | - | 89 (#3) | 92 (#1) | 2사 (D+G) | 90.5 |
| **AVGO** | Broadcom | 81 (#3) | - | 85 (#6) | 2사 (C+G) | 83.0 |
| **BLK** | BlackRock | 76 (#8) | 84 (#5) | - | 2사 (C+D) | 80.0 |
| **CTAS** | Cintas | 80 (#4) | 85 (#9) | - | 2사 (C+D) | 82.5 |
| **COST** | Costco | - | 86 (#1) | 83 (#7) | 2사 (D+G) | 84.5 |
| **SYK** | Stryker | - | 85 (#2) | 81 (#9) | 2사 (D+G) | 83.0 |
| ABBV | AbbVie | 79 (#5) | - | - | 1사 (Claude only) | 79.0 |
| LMT | Lockheed Martin | 78 (#6) | - | - | 1사 (Claude only) | 78.0 |
| NEE | NextEra Energy | 77 (#7) | - | - | 1사 (Claude only) | 77.0 |
| ABT | Abbott Labs | 75 (#9) | - | - | 1사 (Claude only) | 75.0 |
| HSY | Hershey | 74 (#10) | - | - | 1사 (Claude only) | 74.0 |
| ASML | ASML Holding ⚠️ | - | 87 (#7) | - | 1사 (DeepSeek only) | 87.0 |
| LNG | Cheniere Energy | - | 83 (#8) | - | 1사 (DeepSeek only) | 83.0 |
| EFX | Equifax | - | 87 (#10) | - | 1사 (DeepSeek only) | 87.0 |
| EOG | EOG Resources | - | - | 87 (#4) | 1사 (Gemini only) | 87.0 |
| PH | Parker-Hannifin | - | - | 87 (#5) | 1사 (Gemini only) | 87.0 |
| BX | Blackstone ⚠️ | - | - | 82 (#8) | 1사 (Gemini only) | 82.0 |
| PEP | PepsiCo | - | - | 78 (#10) | 1사 (Gemini only) | 78.0 |

### 1.2 일치도 요약

* **3사 합의 (Strong Consensus)**: **MSFT, V** 2종 — 한국어 결과(MSFT, UNH)와 **다른 합의**
* **2사 합의**: 6종 (UNH, AVGO, BLK, CTAS, COST, SYK)
* **1사 단독 추천**: 12종

> **한국어 vs 영문 합의의 차이**: 한국어에서는 MSFT+UNH, 영문에서는 MSFT+V. **Visa가 영문에서 강한 합의**를 받는 것은 영문권 학습 데이터에 Visa의 dividend growth 내러티브가 더 풍부하기 때문으로 추정.

### 1.3 영문 결과의 새로운 문제 — Hallucination & 분류 오류

#### ⚠️ DeepSeek의 ASML 추천 — *국적 모호성 문제*

DeepSeek 영문판은 **ASML Holding**을 Top 7으로 추천했습니다.

* **기술적 사실**: ASML은 NASDAQ-100에 ADR로 편입되어 있음 — *형식적으로는 프롬프트 조건 충족*
* **문제**: 본사가 네덜란드 (Veldhoven, Netherlands)이며 회계기준은 IFRS, 배당은 유로화 기준
* **사용자 의도와의 괴리**: 프롬프트는 "S&P 500 + NASDAQ-100 constituents"라 명시했으나 **사용자는 미국 배당주를 기대**. ASML은 미국 dividend growth 카테고리의 정상 후보가 아님
* **세제 문제**: 한국 거주자가 ASML ADR을 보유하면 네덜란드 원천징수세 15% + 미국 ADR 수수료 + 한국 종합과세 — *복잡한 세제 구조*

> **이 오류는 한국어 DeepSeek 결과에는 없었음** — 한국어 프롬프트로는 LIN(Linde, 영국 본사)을 추천했으나 영문 프롬프트로는 ASML로 옮겨감. **두 결과 모두 *유럽계 대형주를 미국 배당주로 처리*하는 패턴**을 보임.

#### ⚠️ DeepSeek의 SCHD Top Holdings Hallucination

DeepSeek 영문판이 보고한 SCHD Top 5:
> "Amgen, Cisco, Chevron, **BlackRock**, PepsiCo"

* **사실 확인 필요**: BlackRock(BLK)은 SCHD에 **일반적으로 포함되지 않음** — SCHD는 Dow Jones US Dividend 100 인덱스를 추적하며 BlackRock은 통상 비중 외
* **대조**: Claude 영문판이 보고한 SCHD Top 5는 "Texas Instruments, Lockheed Martin, AbbVie, Verizon, Cisco" — *훨씬 정확*
* **결론**: DeepSeek가 "SCHD에 BLK가 자주 보이는 자산운용 관련 종목"이라는 *얕은 연상*으로 hallucination을 만들어낸 것으로 보임

#### ⚠️ DeepSeek SCHD AUM 불일치

* 한국어 결과: AUM **$64B+**
* 영문 결과: AUM **$52B**
* **약 23% 차이** — 동일 ETF에 대한 데이터 일관성 부족

#### ⚠️ Gemini의 Blackstone (BX) 추천 — *카테고리 부적합*

Gemini 영문판은 **Blackstone**을 Top 8으로 추천하며 "5Y CAGR 11.5%"로 표기했습니다.

* **문제**: Blackstone의 배당은 **변동 배당 (variable distribution)** 모델 — 분기마다 운용 수익에 따라 배당이 달라짐
* **dividend growth 카테고리 부적합**: 프롬프트가 요구한 "5+ consecutive years of dividend increases"는 BX 같은 변동 배당 자산운용사에는 부적합
* **사례**: BX의 분기 배당은 2022년 $1.27 → 2023년 $0.91 → 2024년 $0.82 등 **감소 사례 다수** — "consecutive increases" 조건 명백히 위반

#### Gemini AVGO Yield 불일치

Gemini 영문판은 AVGO Yield를 1.44%로 표기했으나, Claude(0.58%)와 DeepSeek(영문 미표기)와 **2.5배 차이**. AVGO의 2024년 분할(10:1) 후 정상 수치는 약 0.6-1.4% 사이지만 1.44%는 분할 전 데이터 사용 가능성 시사.

---

## Part 2 — ETF 비교

### 2.1 영문 결과 ETF 매트릭스

| ETF | Claude(EN) | DeepSeek(EN) | Gemini(EN) | 추천 LLM 수 |
|---|---|---|---|---|
| **SCHD** | ★ | ★ | ★ | **3사 일치** |
| **VYM** | ★ | ★ | ★ | **3사 일치** |
| **JEPI** | ★ | ★ | ★ | **3사 일치** |

> **흥미로운 발견**: 영문 결과는 **3사 모두 SCHD + VYM + JEPI 동일 조합 추천**. 한국어 결과에서는 DeepSeek가 DGRO를 추천하고 Gemini가 VYM/DGRO를 함께 추천하는 등 분산이 있었으나, **영문에서는 완전 일치**.

이는 영문 dividend ETF 영역의 *consensus narrative*가 매우 강력하게 학습되어 있음을 시사. 영문 reach가 더 좁은 후보군에 집중됨.

### 2.2 SCHD 핵심 지표 비교

| 지표 | Claude(EN) | DeepSeek(EN) | Gemini(EN) |
|---|---|---|---|
| 운용보수 | 0.06% | 0.06% | 0.06% |
| AUM | **$85B** | **$52B** | **$68B** |
| 30일 SEC Yield | 3.30% | 3.6% | 3.42% |

> **AUM 추정치 편차가 매우 큼** ($52B ~ $85B, 차이 $33B). 동일 시점 동일 ETF에 대한 LLM 간 데이터 신뢰성 차이.

### 2.3 JEPI 처리의 차이

* **Claude (EN)**: SEC yield 0.65% / 분배율 8.0% **분리 명시**, "사용자가 명시한 2.5% 조건 미충족" *명확히 cavet*
* **DeepSeek (EN)**: SEC yield 7.2% — *옵션 프리미엄을 SEC yield에 포함하는 오류*
* **Gemini (EN)**: SEC yield 7.15% — *DeepSeek와 동일 오류*

> **Claude만이 JEPI의 SEC yield ≠ 분배율 차이를 정확히 인식**. DeepSeek/Gemini는 두 개념을 혼동. 이것은 **JEPI를 "SEC yield 2.5% 조건"에 부적합으로 식별하지 못하는 정량 오류**.

---

## Part 3 — 동일가중 포트폴리오 비교

### 3.1 핵심 지표

| 지표 | Claude(EN) | DeepSeek(EN) | Gemini(EN) |
|---|---|---|---|
| 세전 배당수익률 | **1.95%** | **1.01%** | **1.54%** |
| Sharpe Ratio | **0.78** | **0.92** | **1.14** |
| Max Drawdown | -16.4% | -18.4% | -17.2% |
| 12개월 기대수익률 | +9.2% | 12-14% | 13.0% |
| 무위험금리 가정 | **4.4%** (10Y UST) | 4.5% | 미명시 |

### 3.2 한국어 vs 영문 — Sharpe Ratio 변화 비교

| LLM | 한국어 Sharpe | 영문 Sharpe | 변화 |
|---|---|---|---|
| Claude | 0.82 | **0.78** | -0.04 (보수적으로 변경) |
| DeepSeek | 1.45 ⚠️ | **0.92** | **-0.53 (대폭 정상화)** |
| Gemini | 1.25 | **1.14** | -0.11 (소폭 정상화) |

> **DeepSeek의 가장 큰 변화**: 한국어 Sharpe 1.45 → 영문 Sharpe 0.92로 *0.53 정상화*. 이는 영문 학습 데이터에 *학술적 Sharpe Ratio 합리성 기준*이 더 강하게 학습되어 있음을 시사.

### 3.3 배당수익률 차이

* **Claude (EN) 1.95%**: 한국어 결과(2.10%)보다 약간 낮음 — *매크로 환경(Iran 사태, oil $107)을 반영해 더 보수적 종목 (NEE 3.40%, ABBV 3.29%, HSY 3.20%)*
* **DeepSeek (EN) 1.01%**: 한국어(2.08%)의 절반 수준 — *영문에서는 high-growth low-yield 종목 (COST 0.56%, V 0.81%, MSFT 0.81%, ASML 0.81%)에 편중*
* **Gemini (EN) 1.54%**: 한국어(2.05%)보다 낮음 — 유사한 패턴

> **공통 패턴**: 영문 결과에서는 **현재 yield는 낮지만 dividend CAGR이 높은 종목**에 더 편중. 한국어 결과는 **현재 yield + 안정성** 균형. 영문권 학습 데이터의 *"Growth-of-Dividend"* 내러티브가 더 강하게 작동.

---

## 영문 결과 3사 LLM의 *관찰된* 특성

### Claude Opus 4.7 (영문)

**강점:**
* **매크로 컨텍스트 명시적**: "10Y UST 4.4%, Fed funds 3.50-3.75%, oil $107 Iran 사태" 등 **현재 거시 환경을 첫 페이지에 명시**
* **방법론 투명성**: Sharpe 0.78 (학술 합리적), 무위험금리 4.4% 명시, 시나리오 4가지 + 확률 가중평균
* **JEPI 정확 처리**: SEC yield와 분배율 차이를 명확히 구분
* **위험 고지 깊이**: 종목별 risk factor 2개 + stop-loss + 12M target 모두 충실
* **포트폴리오 규모 가이드**: 코어 SCHD 40-60%, 위성 VYM 20-30%, JEPI 10-20% 명시

**약점:**
* 출력 분량 가장 큼 (32KB) — 토큰 비용 최고
* 한국 거주자 컨텍스트 약화 (한국어판 대비 *외환거래법 / 종합과세* 같은 맥락 자연 감소)

### DeepSeek V3.1/V4 (영문)

**강점:**
* **매트릭스 형식 명확**: 표 정리 우수
* **Sharpe 0.92로 정상화**: 한국어 1.45 → 영문 0.92로 *학술적 합리성 회복*
* **AUM ASML 같은 외국 종목 발굴**: 정통 미국 종목 외 추가 후보 제공

**약점:**
* **ASML 추천 — 사용자 의도 위반**: NASDAQ-100 ADR이지만 미국 배당주 카테고리 부적합
* **SCHD Top 5에 BlackRock 포함 — Hallucination**: 실제 SCHD 보유 아님
* **JEPI SEC yield 7.2% — 옵션 프리미엄과 혼동**
* **AUM 데이터 한국어/영문 불일치**: SCHD AUM $64B+ vs $52B
* **VYM Top 5에 JPMorgan, Bank of America** — JPM과 BAC 동시 보유는 의문 (실제로는 JPM 단독)
* **위험 고지 분량 부족**: Claude 대비 약함

### Gemini 3 Flash (영문)

**강점:**
* **출력 가장 간결**: 5KB / 78 lines, 토큰 비용 최저
* **점수 인플레이션 부분 완화**: 한국어 평균 90 → 영문 평균 85 (소폭 정상화)
* **EOG, PH 같은 차별화 종목 발굴**: 다른 LLM이 놓친 에너지·산업재 dividend grower

**약점:**
* **Blackstone (BX) 추천 — 카테고리 위반**: 변동 배당 모델로 dividend growth 부적합
* **AVGO Yield 1.44% — 분할 전 데이터 가능성**: 다른 LLM 0.58-0.81%와 큰 차이
* **JEPI SEC yield 7.15% — DeepSeek와 동일 오류**
* **방법론 투명성 가장 부족**: 무위험금리 미명시, 시나리오 분석 없음
* **종목별 분석 누락**: Top 10 모두에 대한 상세 thesis 없음

---

## 핵심 상이점 정리

### 1. *섹터 분산 정확도*

```
Claude    ★★★★★  6대 섹터 모두 정확 분산
Gemini    ★★★    BX(변동배당 부적합), AVGO yield 의심
DeepSeek  ★★     ASML(국적 모호), SCHD holdings hallucination
```

### 2. *데이터 정확도*

```
Claude    ★★★★   매크로 명시 + JEPI 정확 처리
Gemini    ★★     AVGO yield 의심, JEPI 혼동
DeepSeek  ★      SCHD holdings hallucination, AUM 불일치, JEPI 혼동
```

### 3. *Sharpe Ratio 신뢰성*

```
Claude   0.78  ★★★★  학술 합리적, 무위험금리 명시
DeepSeek 0.92  ★★★   한국어 1.45에서 정상화 (영문 학습 효과)
Gemini   1.14  ★★    경계 영역, 무위험금리 미명시
```

### 4. *Hallucination 빈도*

```
Claude    낮음   매크로 데이터 정확, 종목 분류 정확
Gemini    중간   BX dividend growth 분류 오류, AVGO yield 의심
DeepSeek  높음   SCHD holdings 환상, ASML 카테고리 모호, AUM 불일치
```

---

## 영문 vs 한국어 — 어느 것이 더 정확한가?

### 영문 프롬프트의 강점

1. **학술적 정량 메트릭 더 정확** (Sharpe Ratio 정상화 — 특히 DeepSeek)
2. **매크로 컨텍스트 명시 강화** (Claude의 10Y UST/oil price 표기)
3. **ETF 영역 consensus 강화** (3사 모두 SCHD+VYM+JEPI 동일 추천)
4. **방법론 투명성 일반적으로 향상**

### 영문 프롬프트의 약점

1. **외국계 종목을 미국 카테고리로 처리하는 오류 증가** (DeepSeek ASML)
2. **종목별 hallucination 위험 증가** (DeepSeek SCHD holdings)
3. **한국 투자자 컨텍스트 자동 소실** (외환거래법, 종합과세 가이드 사라짐)
4. **dividend yield 편중 (low yield + high growth)** — 사용자가 인컴 지향이면 부적합

### 한국어 프롬프트의 강점

1. **한국 투자자 컨텍스트 자연 통합** (외환거래법, 세제, 환율 가이드)
2. **현재 yield + 안정성 균형** (Claude 한국어 2.10% vs 영문 1.95%)
3. **사용자 메모리 통합** (Claude의 "Dennis님의 STABLE1" 같은 개인화)

### 한국어 프롬프트의 약점

1. **Sharpe Ratio 등 정량 지표 비현실적** (DeepSeek 한국어 1.45)
2. **섹터 오분류 빈도 높음** (Gemini 한국어 LOW/JPM/COP 3건)
3. **LLM 간 합의도 더 낮음**

---

## 사용자에게 주는 권고

### Cross-Lingual Validation 워크플로 (권장)

```
1단계: 영문 프롬프트로 1차 분석
   → 정량 메트릭 + 매크로 컨텍스트 추출
   → 학술적 합리성 확보

2단계: 한국어 프롬프트로 2차 분석
   → 한국 투자자 컨텍스트 (세제, 환율, 거주자 가이드)
   → 사용자별 맞춤 종목 후보

3단계: 두 결과의 *합의 종목* 추출
   → MSFT, V (3사 영문 + 일부 한국어 합의)
   → UNH (한국어 3사 + 영문 2사 합의)
   → BLK (4건 모두 추천 — 가장 강한 신호)

4단계: 단독 추천 종목 *교차 검증*
   → 영문에서 ASML 같은 ADR 등장 시 → 사용자 의도 재확인
   → 한국어에서 LIN, JPM(은행) 등 섹터 오분류 종목 → 독립 검증
```

### 영문 프롬프트가 더 적합한 경우

* **학술 논문 / 백서 작성**: Sharpe Ratio, Maximum Drawdown 등 정량 지표 정확도가 중요할 때
* **글로벌 자산 운용**: 미국 거주자 / 다국적 포트폴리오 운용 시
* **AI 보조 백테스트**: 매크로 변수 명시가 필요할 때

### 한국어 프롬프트가 더 적합한 경우

* **한국 거주자 실전 투자**: 외환거래법 / 양도소득세 22% / 종합과세 가이드 필요 시
* **국내 환율 헤지 전략**: USD/KRW 노출 분석 필요 시
* **사용자 컨텍스트 기반 맞춤형**: 본인 사업/직업 관련 섹터 뽑을 때

---

## 한계와 주의사항

### 본 비교 분석의 한계

1. **단일 실행 (N=1)** — 동일 LLM도 재실행 시 다른 결과 가능
2. **시점 한정** — 2026년 5월 2일 실행
3. **모델 버전** — 각 LLM의 정확한 버전 명시 어려움
4. **저자 단일 평가** — 객관적 벤치마크 아님

### 영문 결과 검증 시 주의

* 영문 결과의 종목 ticker는 반드시 **SEC EDGAR + 종목 거래소 본사 위치**를 직접 확인
* DeepSeek가 추천한 ASML은 **NASDAQ ADR이지만 본사 네덜란드** — 한국 투자자 세제 관점에서 검토 필요
* Gemini가 추천한 BX는 **변동 배당** — 5Y CAGR이 높아도 "consecutive increases" 조건 위반 가능
* DeepSeek의 ETF holdings 보고는 **Schwab/Vanguard 공식 fact sheet로 교차 검증** 필수

### Disclaimer

* 본 비교 분석은 **교육·연구 목적** — 실제 투자 권유 아님
* 본 비교는 **단일 실행 (N=1)** 결과로 통계적 유의성 없음
* 모든 투자 결정은 독립 데이터 소스 + 전문가 상담 후 본인 책임
* **과거 배당 기록이 미래 배당을 보장하지 않습니다**

---

## 작성 정보

**시리즈**: vibe-investing — Awesome Claude Quant Scripts → Dividend Growth Prompt
**연관 문서**:
* [상위 폴더 Readme.md](../../Readme.md) — 한국어 결과 비교
* [영문 프롬프트](../../Dividend_Growth_Prompt_EN.md)
* [한국어 프롬프트](../../Dividend%20Growth%20Prompt%20kr.MD)

**저자**: 김호광 (Dennis Kim)
**작성일**: 2026년 5월 3일 v1.0
**라이선스**: MIT

---

> *"The same prompt in two languages produces three different portfolios. Which one is true? Perhaps neither — only the disagreement is true."*
> *"같은 프롬프트가 두 언어에서 세 개의 다른 포트폴리오를 만든다. 어느 것이 진실인가? 어쩌면 어느 것도 아닐지 모른다 — 오직 그들의 불일치만이 진실이다."*
