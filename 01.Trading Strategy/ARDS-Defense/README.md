# ARDS-Defense

### Adaptive Recession-Defensive Strategy for Defense & AI-Weaponization

> "전쟁과 분쟁의 시대, 방산은 더 이상 경기방어주가 아니라 구조적 성장주다.
> 그 구조적 성장 속에서도 경기 사이클은 반드시 찾아온다. 이 전략은 그 역설을 거래한다."

냉전이 지나고 팍스 아메리카나의 시대가 저물면서 다시 새로운 혼돈의 시기가 오고 있습니다. 러시아-우크라이나 전쟁은 유럽의 재무장을 촉발시켰으며, 일본 역시 1%로 묶여 있던 군비를 증강하고 있습니다. 이란과 이스라엘, 미국의 중동 전쟁은 미국이 1년간 생산할 무기 방어체계를 단시간 내에 소모시켰습니다.

방산(Defense)과 AI 무기화(AI-Weaponization) 섹터에 특화된 적응형 경기방어 투자 전략입니다. 거시 레짐을 판별해 Phase를 산출하고, 방산 특수 지표(Defense Sentiment)로 이를 조정한 뒤, 한국·미국 방산 종목을 3-Tier로 나눠 Phase별 자산 배분을 자동 산출합니다.

---

## Repository 구조

```
ARDS-Defense/
├── README.md                ← 본 문서 (전략 전문 + 다국어 프롬프트 + 멀티-LLM 분석)
├── llms.txt                 ← LLM 친화적 요약 인덱스
├── README_EN.md             ← English version
├── prompts/
│   ├── ARDS-Defense_KO.md    ← 한국어 실행 프롬프트 (v1.1)
│   ├── ARDS-Defense_EN.md    ← English execution prompt (v1.1)
│   └── ARDS-Defense_ZH.md    ← 中文执行提示词 (v1.1)
└── result/                  ← 각 LLM의 출력 결과 보관
    ├── claude_0524.md                       ← Claude 실행 결과
    ├── DeepSeek_0524.md                      ← DeepSeek 실행 결과
    ├── readme.md                             ← 교차 LLM 비교 분석 (Claude vs DeepSeek)
    ├── ARDS_Defense_Critique.md              ← 백테스트/실전 관점 냉정한 비판
    └── deepseek_markdown_20260524_371f74.md  ← DeepSeek 자기비판 피드백
```

`result/` 폴더에는 동일 프롬프트를 여러 LLM·여러 언어로 실행한 출력 결과를 보관합니다. 멀티-LLM 교차검증(cross-validation) 및 언어별 출력 비대칭(cross-lingual asymmetry) 분석에 활용합니다.

---

## STEP 1 — 투자 논리 (Investment Thesis)

### 1.1 왜 지금 방산 + AI인가

전쟁·분쟁의 구조화(Structuration of Warfare)와 국방비 슈퍼사이클(Defense Supercycle)이라는 두 개의 거대한 흐름이 중첩되고 있습니다. 글로벌 국방비 지출은 2026년 기준 2.6조 달러를 돌파했으며, 2030년까지 3.6조 달러로 확대될 전망입니다. 이 중 펜타곤의 AI 예산만 20억 달러 미만에서 134억 달러로 단일 연도에 급증했습니다.

단순한 국방비 증가가 아닌, **국방비 내 AI/소프트웨어 비중의 구조적 재편**이 핵심입니다. 2025년 VC-backed 방산 스타트업 투자는 미국·유럽 합산 약 77억 달러로 2024년의 2배 이상을 기록했으며, 팔란티어는 2026년 연간 매출 가이던스를 76.5억~76.6억 달러로 상향(2025년 33.2억 달러 대비 +71%)했습니다.

> 위 수치는 작성 시점 기준 추정치입니다. 실행 프롬프트는 매크로/펀더멘털 지표를 웹검색으로 실시간 재확보하도록 설계되어 있으니, 매 실행 시 최신 값으로 갱신됩니다.

### 1.2 경기방어 + 구조적 성장의 이중적 성격

| 성격 | 내용 |
|---|---|
| Recession-Defensive | 경기 침체기에도 국방 예산은 후행적으로 삭감되며, 지정학적 위기는 경기와 무관하게 발생 |
| Structural Growth | AI·자율무기·우주방어·사이버전으로의 패러다임 전환은 경기 사이클을 초월한 10년+ 투자 사이클 |
| Asymmetric Alpha | 전통 방산주 vs AI 방산주는 동일 섹터 내에서도 완전히 다른 리스크-리턴 프로파일 |

---

## STEP 2 — Universe (투자 유니버스)

### 2.1 한국 (KOSPI/KOSDAQ) 상장 방산 기업

| Tier | 종목명 | 티커 | 핵심 사업 | AI/무인화 연계 |
|---|---|---|---|---|
| Core | 한화에어로스페이스 | 012450 | 항공엔진, 미사일, 자주포(K9), 우주발사체 | 한화 방산 3사 AI·무인화 통합 플랫폼 |
| Core | LIG넥스원 | 079550 | 유도미사일, 정밀타격, 감시정찰 | AI 기반 지휘통제체계 |
| Core | 한국항공우주(KAI) | 047810 | 전투기(KF-21), 훈련기, 위성 | 무인전투기(UCAV) 개발 |
| Core | 현대로템 | 064350 | 전차(K2), 장갑차, 철도 | 무인전차·자율주행 기술 |
| Core | 한화오션 | 042660 | 함정, 잠수함 | 무인수상정(USV) 기술 |
| Core | 한화시스템 | 272210 | C4I, 레이더, 위성통신 | AI·무인화 플랫폼 핵심 |
| Satellite | 풍산 | 103140 | 탄약, 포탄 | — |
| Satellite | STX엔진 | 077970 | 함정용 엔진, 발전기 | — |
| Satellite | 빅텍 | 065450 | 군용 전원공급체계 | — |
| Satellite | SNT중공업 | 003570 | 함정 엔진, 방산 차량 부품 | — |
| Satellite | 퍼스텍 | 010820 | 유도무기 체계, 항공기 개조 | — |
| Satellite | HJ중공업 | 097230 | 함정 건조 | — |

### 2.2 미국 (NYSE/NASDAQ) 상장 방산 기업

| Tier | 종목명 | 티커 | 핵심 사업 | AI/무인화 연계 |
|---|---|---|---|---|
| Core | Lockheed Martin | LMT | 전투기(F-35), 미사일, 위성 | AI 전장관리, 자율비행 |
| Core | RTX Corp | RTX | 미사일(Patriot), 레이더, 항공엔진 | AI 센서퓨전, 요격체계 |
| Core | Northrop Grumman | NOC | 스텔스 폭격기(B-21), 우주, 미사일 | 자율무인기 |
| Core | General Dynamics | GD | 전차, 잠수함, IT/C4I | 사이버 보안, AI 지휘통제 |
| Core | L3Harris | LHX | 전자전, 통신, 위성 | AI 신호정보(SIGINT) |
| Core | Boeing | BA | 전투기(F/A-18), 수송기, 위성 | 자율비행, MQ-25 무인급유기 |
| AI-Defense | Palantir | PLTR | AI 전장관리 플랫폼(AIP/Maven) | 국방 AI 순수 플레이 |
| AI-Defense | Kratos Defense | KTOS | 무인전투기(XQ-58) | 자율무인기 특화 |
| AI-Defense | AeroVironment | AVAV | 소형 무인기(Switchblade) | 자율공격 드론 |
| AI-Defense | BigBear.ai | BBAI | AI 의사결정 분석 | 국방 AI 데이터 분석 |
| Tactical | Huntington Ingalls | HII | 항공모함, 잠수함 | — |
| Tactical | Rocket Lab | RKLB | 우주발사체, 위성 | — |
| Tactical | Booz Allen Hamilton | BAH | 국방 컨설팅, 사이버 보안 | AI 컨설팅 |
| Pre-IPO | Anduril Industries | (비상장) | AI 자율무기, 무인전투기(Fury) | 국방 AI 스타트업 대장 (밸류 ~$61B) |

### 2.3 ETF Universe

| ETF 명 | 티커 | 국가 | 특징 | 운용사 |
|---|---|---|---|---|
| PLUS K방산 | 449450 | 한국 | K-방산 핵심 10종목 | 한화자산운용 |
| TIGER 미국방산TOP10 | 494840 | 미국 | 미국 방산 대형주 10종목 | 미래에셋자산운용 |
| iShares US Aerospace & Defense | ITA | 미국 | 미국 항공우주·방산 전반 | BlackRock |
| iShares Defense Industrials Active | IDEF | 글로벌 | 글로벌 방산 액티브 | BlackRock |

---

## STEP 3 — 실행 프롬프트 (다국어)

아래 프롬프트(v1.1)를 그대로 복사해 웹검색 가능한 LLM에 붙여넣어 실행하세요. 빈칸 없이 즉시 실행 가능하며, 매크로 지표는 웹검색으로 실시간 확보하도록 설계되어 있습니다.

| 언어 | 파일 | 비고 |
|---|---|---|
| 한국어 | `prompts/ARDS-Defense_KO.md` | 기본(primary) |
| English | `prompts/ARDS-Defense_EN.md` | 글로벌 배포용 |
| 中文 | `prompts/ARDS-Defense_ZH.md` | 중화권 배포용 |

### v1.1 핵심 로직 (3개 언어 공통)

- STEP 0 — 5-Factor Recession Composite로 거시 Phase(1~4) 판별
- STEP 1 — Defense Sentiment Score(0~100)로 Phase 레벨 ±1 조정
- STEP 2 — 3-Tier Universe (Core Defense / AI-Defense / Tactical)
- STEP 3 + 3.5 — 5-Dimension Scoring → Tier 내 비중 자동 배분(Score 가중 + 40% 캡)
- STEP 4 — Phase별 자산 배분 Matrix
- STEP 5~7 — AI-Defense 특별 규칙, 실행 규칙, 반대 시나리오

---

## STEP 4 — 멀티-LLM 실행 결과 분석 (2026-05-24)

본 절은 동일한 v1.1 프롬프트를 **Claude**와 **DeepSeek** 두 모델에 실행한 결과를 비교·분석한다. 같은 규칙·같은 유니버스·같은 절차를 따랐음에도 거시 판정의 근거 수치, 종목 스코어링, 최종 비중, 규칙 일관성에서 의미 있는 차이가 발생했다. 이 분석은 본 리포지토리의 cross-LLM 검증 연구 목적과 직결된다.

원본 결과: [`result/claude_0524.md`](result/claude_0524.md), [`result/DeepSeek_0524.md`](result/DeepSeek_0524.md)
교차 분석·자기비판: [`result/readme.md`](result/readme.md), [`result/deepseek_markdown_20260524_371f74.md`](result/deepseek_markdown_20260524_371f74.md)

### 4.1 결과 요약

| 항목 | Claude | DeepSeek | 일치 여부 |
|---|---|---|---|
| 최종 Phase | Phase 1 (Expansion) | Phase 1 (Expansion) | 동일 |
| Recession Composite | 22.5% | 15.0% | 7.5%p 차 |
| Defense Sentiment | 92.5 | 97.25 | 근사 |
| 국가 비중 | 한국 50 / 미국 50 | 한국 50 / 미국 50 (사후 조정) | 동일(경로 상이) |
| Tier 1 최상위 | LIG넥스원 (75.1) | 한화에어로스페이스 (86.0) | 1위 다름 |
| PLTR 최종 비중 | 3.7% | 4.5% | 상이 |
| 포트폴리오 스타일 | 분산형 (종목당 4.6~5.3%) | 집중형 (상위 9~14%) | 철학 차이 |

두 모델은 결론(Phase 1, 한미 50:50, 방산 초강세)에는 수렴했으나, 거기에 도달하는 수치 근거와 종목별 비중은 상당히 달랐다. 같은 프롬프트라도 LLM마다 출력이 갈린다는 점을 정량적으로 보여주는 사례다.

### 4.2 DeepSeek의 실수와 원인 추론

DeepSeek 출력에는 실전 운용에서 용납될 수 없는 결함이 포함되어 있었다. 주목할 점은 이 결함들을 DeepSeek 본인도 자기비판 문서([`deepseek_markdown_20260524_371f74.md`](result/deepseek_markdown_20260524_371f74.md))에서 인정했다는 것이다.

**(1) 산술 오류 — 국가 비중 합계 142%**

DeepSeek은 STEP 3.5에서 한국을 "40% × 50% = 20%"로 배분한다고 적어놓고, 최종 합산에서 한국 61.5% + 미국 80.4% = 합계 **142%**라는 불가능한 숫자를 냈다. 이후 "규칙 위반 감지"라며 사후에 50:50으로 강제 조정했다.

- 추정 원인 1 — **이중 계산(double counting):** 한화시스템이 Tier 1과 Tier 2에 동시 편입되는데, 국가 합산 시 두 Tier 비중을 모두 한국에 더하면서 중복 집계됐을 가능성. Claude는 한화시스템의 Tier 1·Tier 2 비중을 분리 표기해 혼동을 피했다.
- 추정 원인 2 — **배분 기준선 혼동:** "Tier 내 비중(%)"과 "최종 포트폴리오 비중(%)" 두 척도를 중간에 섞으면서, Tier 내 100% 기준 수치를 포트폴리오 100% 기준으로 잘못 합산. 80.4% 같은 값은 "미국 Tier 1 내 비중 합"에 가깝다.
- 추정 원인 3 — **순차 생성의 누적 오차:** LLM은 표를 토큰 단위로 순차 생성하므로, 앞 단계 수치를 뒤 단계에서 재계산하지 않고 새로 "그럴듯하게" 생성하는 경향이 있다. 중간 검증 단계가 프롬프트에 없으면 누적 오차가 그대로 출력된다.

**(2) 방법론 비일관 — LEI 해석**

5개 Factor 중 유일한 분기점은 Factor D(LEI -0.7%)였다. 프롬프트는 "< -2% 시 100%"만 명시하고 0~-2% 구간 처리를 정의하지 않았다.

- Claude: 0~-2% 구간을 "중간값 50%"로 처리 → Composite 22.5%
- DeepSeek: "-2% 미만이 아니므로 0%" 처리 → Composite 15.0%

문제는 DeepSeek이 동일 보고서 내 Factor A(Yield Curve)에서는 0~50bp 구간을 50%로 처리해놓고, Factor D에서는 0%를 적용했다는 점이다. **같은 보고서 안에서 구간 처리 논리가 일관되지 않았다.** 규칙의 공백(under-specification)을 모델이 매번 다르게 메우는 전형적 사례다.

**(3) 정밀함의 외관(illusion of precision)**

DeepSeek은 GPR 415, 미사일 조달 +188%, 美 국방예산 +42% YoY 등 정량 수치를 다수 인용해 더 정밀해 보이는 효과를 냈으나, 상당수가 검증이 어렵거나 맥락이 제한된 수치였다. "+42% YoY"는 의회 통과 전 제안치, "+188%"는 단일 카테고리 가능성, GPR 415는 2차 출처 인용으로 원출처와의 교차검증이 어렵다. 수치가 많다고 더 나은 분석이 아니다.

**(4) PLTR 비중 역전 — 규칙 적용 순서의 민감성**

점수가 더 낮은 PLTR(62.5)이 DeepSeek에서 오히려 더 높은 비중(4.5%)을 받았다. Tier 2를 4종목으로 좁히고 KTOS·AVAV에 Cap을 먼저 건 뒤 잔여 비중이 PLTR로 흘러갔기 때문이다. "Score 비례 배분" 규칙이 종목 수와 Cap 적용 순서에 민감하게 반응한다는 구조적 약점을 드러낸다.

### 4.3 DeepSeek의 강점 (인정할 부분)

오류가 있었다고 DeepSeek 출력 전체가 무가치한 것은 아니다.

- **반대 시나리오의 구체성:** LAWS(자율살상무기 금지 조약) 발효 시나리오, PLTR의 DIA 계약 분쟁 등 개별 리스크를 구체적으로 짚었다. Claude는 비슷한 주제를 다루되 구체성이 떨어졌다.
- **신생 기업 정보:** Anduril $61B 밸류·$20B 10년 계약, KTOS 파이프라인 등 Pre-IPO/신흥 기업 정보를 풍부하게 반영했다.
- **밸류에이션 현실성:** PLTR 선행 PER 97~110배, KTOS 67배 등 구체적 밸류 근거로 D4 점수를 할인했다.

### 4.4 추천 주식 리스트 (두 모델 교차검증 결과)

두 LLM이 공통으로 상위권에 올린 종목은 신뢰도가 높은 "수렴 영역"이다. 아래는 두 모델 결과를 종합한 통합 추천 리스트다.

**Tier 1 — Core Defense (핵심, 양 모델 공통 상위)**

| 종목 | 티커 | 국가 | Claude Score | DeepSeek Score | 공통 평가 |
|---|---|---|---|---|---|
| 한화에어로스페이스 | 012450 | 한국 | 75.0 | 86.0 | 양 모델 한국 1~2위, 수출 모멘텀 최강 |
| LIG넥스원 | 079550 | 한국 | 75.1 | 83.8 | 양 모델 최상위권, 유도무기 |
| Lockheed Martin | LMT | 미국 | 72.2 | 83.5 | 양 모델 미국 1위, Flight-to-Quality 앵커 |
| Northrop Grumman | NOC | 미국 | 71.5 | 80.0 | 핵·우주·스텔스 |
| RTX | RTX | 미국 | 66.2 | 79.0 | 미사일·방공 |
| 현대로템 | 064350 | 한국 | 69.0 | 77.5 | K2 전차 수출 마진 |
| 한국항공우주 | 047810 | 한국 | 65.5 | 78.0 | KF-21 양산 진입 |

**Tier 2 — AI-Defense (구조적 성장, 고변동성)**

| 종목 | 티커 | 국가 | 공통 평가 | 주의 |
|---|---|---|---|---|
| 한화시스템 | 272210 | 한국 | 양 모델 Tier 2 상위, K-AI 방산 | Tier 1과 중복 편입 |
| AeroVironment | AVAV | 미국 | 무인기·로이터링 탄약 | 시총 변동성 |
| Kratos | KTOS | 미국 | 무인전투기·표적기 | 흑자 전환 진행형 |
| Palantir | PLTR | 미국 | AI 방산 순수 플레이 | 선행 PER 80~110배, STEP 5 규칙상 비중 50% 축소 |

**공통 제외:** BigBear.ai(BBAI) — 양 모델 모두 Score 60점 미만으로 편입 제외. Boeing(BA)은 Claude 제외(44.2) vs DeepSeek 경계(61.5)로 판단 갈림 → 편입 시 소량·주의.

위 리스트는 두 LLM의 정성 평가를 종합한 것이며, 개별 종목의 실제 재무·밸류는 집행 직전 직접 확인해야 한다. 이는 투자 권유가 아니다.

### 4.5 핵심 차이점 정리

| 차원 | Claude | DeepSeek |
|---|---|---|
| 산술 정확성 | 오류 없음 | 142% 합산 오류 |
| 규칙 일관성 | LEI 50% 일관 적용 | LEI 0% (Factor A와 불일치) |
| 데이터 성향 | 보수적·검증가능 | 정량 풍부하나 검증 곤란 |
| 포트폴리오 | 광범위 분산 | 고확신 집중 |
| 반대 시나리오 | 표준적 | 더 구체적·풍부 |
| 신생 기업 정보 | 제한적 | 풍부(Anduril 등) |
| 추론 무결성 | 우위 | 사후 패치 흔적 |

### 4.6 LLM 오류 가능성과 대응 — 다중 LLM 보정의 필요성

이 사례는 단일 LLM 출력을 그대로 신뢰해서는 안 되는 이유를 정량적으로 보여준다.

**LLM 출력의 구조적 오류 유형**

1. **산술/집계 오류:** 순차 토큰 생성 특성상 다단계 계산에서 누적 오차·이중 계산 발생 (DeepSeek 142% 사례).
2. **규칙 공백의 자의적 해석:** 프롬프트가 정의하지 않은 경계 구간을 모델마다 다르게 메움 (LEI 50% vs 0%).
3. **정밀함의 외관:** 검증 안 된 수치를 다수 인용해 신뢰도가 높아 보이는 착시.
4. **적용 순서 민감성:** 동일 규칙이라도 처리 순서에 따라 결과가 바뀜 (PLTR 비중 역전).
5. **비결정성(non-determinism):** 동일 프롬프트·동일 시점이라도 재실행 시 다른 결과.
6. **무조건적 호평 편향:** LLM은 입력 전략을 과대평가하는 경향. 외부 비판([`ARDS_Defense_Critique.md`](result/ARDS_Defense_Critique.md))이 지적하듯, 슬리피지·체결지연·과적합 같은 실전 리스크는 정적 리뷰에서 누락되기 쉽다.

**대응 방식 — 다중 LLM 교차검증(Multi-LLM Cross-Validation)**

단일 모델의 약점은 다른 모델로 상쇄할 수 있다. 핵심은 "수렴 영역"과 "분산 영역"을 구분하는 것이다.

- **수렴 영역(고신뢰):** 두 모델이 일치하는 결론(Phase 1, 한미 50:50, 한화에어로·LIG넥스원·LMT 최상위, BBAI 제외)은 강건한 신호로 채택.
- **분산 영역(재검토):** 모델 간 갈리는 항목(Composite 수치, 개별 비중, Boeing 편입)은 사람이 직접 재검증.
- **검증 레이어 추가:** 한 모델의 출력을 다른 모델에게 비판시키는 self-critique / cross-critique 루프. 본 리포지토리의 `deepseek_markdown_...md`가 그 실례로, DeepSeek이 자기 오류를 스스로 적발했다.
- **결정론적 후처리:** 산술 합산·비중 합 100% 검증·Cap 적용은 LLM이 아닌 코드로 강제 검증.

**권고 워크플로우**

```
[프롬프트 실행: 2개 이상 LLM]
        ↓
[수렴/분산 영역 자동 대조]
        ↓
[분산 영역 → 사람 또는 제3 LLM 재검증]
        ↓
[산술·비중합·Cap → 코드로 결정론적 검증]
        ↓
[블랙스완 스트레스 테스트 + 보수적 비용(2~3배) 재산출]
        ↓
[소액 포워드 테스트 후 실집행]
```

### 4.7 프롬프트 개선 제안 (v1.2 후보)

이 비교에서 드러난 분산을 줄이려면 프롬프트에 다음을 추가해야 한다.

1. **구간 사이(between-threshold) 처리 규칙 통일:** 모든 Factor에 "경계 구간 = 50%"를 일관 적용하도록 명시 (Factor B·D·E의 누락 보완).
2. **국가 비중 중간 검증 단계:** STEP 3.5 이후 "국가별 비중 합계 ≤ 100% 및 총합 = 100%" 강제 체크. 중복 편입 종목(한화시스템)의 국가 귀속 규칙 명문화.
3. **Score 정량 루브릭:** D3 재무 등에 "FCF/매출 > 10% = 만점" 같은 구체 기준 제시로 주관 분산 축소.
4. **Cap 적용 순서 명문화:** "Tier 내 Score 상위 순으로 Cap 적용 후 초과분을 차순위로 재배분."

---

## STEP 5 — 리스크 관리

| 리스크 | 내용 |
|---|---|
| 지정학 리스크 역설 | 전쟁 종결/긴장 완화 시 방산주는 최대 30% 급락 가능 |
| AI 방산 밸류에이션 리스크 | PLTR·Anduril·BBAI 등은 계약 파이프라인으로 거래 → 금리 상승기 멀티플 압축에 극도로 취약 |
| K-방산 수출 집중 리스크 | 폴란드·UAE·사우디 등 특정 국가 의존도가 높아 지정학 급변 시 매출 공백 가능 |
| 원자재·공급망 리스크 | 희토류·반도체·특수합금의 중국 의존도가 높아 미중 갈등 심화 시 생산 차질 |
| Phase 4 규칙의 기회비용 | AI-Defense 0% 규칙이 침체기 반등 시 수익을 제한할 수 있음 |
| 실전 괴리 리스크 | 슬리피지·체결지연·과적합으로 백테스트 대비 실전 MDD가 수배 커질 수 있음 (외부 비판 참조) |

---

## 참고자료

- ARDS 원본 전략: ARDS: Adaptive Recession-Defensive Strategy
- 멀티-LLM 비교: `result/readme.md` (Claude vs DeepSeek 교차 분석)
- 자기비판 피드백: `result/deepseek_markdown_20260524_371f74.md`
- 실전 관점 비판: `result/ARDS_Defense_Critique.md`

---

## 면책 조항 (Disclaimer)

본 자료는 교육 및 연구 목적의 LLM 시뮬레이션 결과이며, 특정 종목의 매수·매도를 권유하는 것이 아닙니다. 모든 투자 판단과 그에 따른 책임은 투자자 본인에게 있습니다.

방산 섹터는 지정학적 사건에 극도로 민감하게 반응하므로, 본 전략만으로 포트폴리오 전체를 구성하는 것은 권장하지 않습니다. ARDS 원본(경기방어 ETF·채권·금)과의 병행 운용을 강력히 권고합니다.

동일한 프롬프트, 동일한 시점이라도 LLM 출력은 비결정적(non-deterministic) 특성을 가지므로 재실행 시 다른 결과가 나올 수 있습니다. 단일 LLM 출력에 의존하지 말고 반드시 다중 LLM 교차검증과 결정론적 후처리를 거치십시오.

> This material is an LLM-based simulation result for educational and research purposes only, and is not a solicitation to buy or sell any security. All investment decisions and responsibility rest with the investor.
