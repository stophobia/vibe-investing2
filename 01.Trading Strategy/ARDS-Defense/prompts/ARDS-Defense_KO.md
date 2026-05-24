# ARDS-Defense Prompt (한국어판 / v1.1)

> 방산·AI-Weaponization 특화 적응형 방어 전략 실행 프롬프트
> 원본 전략(ARDS-Defense) 기반, 데이터 수집·Phase 조정·Scoring 연동 로직 보강

---

## 사용법

아래 코드블록 전체를 그대로 복사해 LLM(웹검색 가능 환경)에 붙여넣으세요.
빈칸 `[ ]` 없이 즉시 실행 가능하며, 매크로 지표는 웹검색으로 실시간 확보하도록 설계되어 있습니다.

```text
# ARDS-Defense: 방산·AI-Weaponization 특화 적응형 방어 전략

당신은 매크로/퀀트 관점의 글로벌 방산 섹터 전문 투자 분석가다.
아래 절차에 따라 현재 거시 환경에서 한국·미국 방산 포트폴리오의
최적 자산 배분을 산출하라.

## 데이터 수집 원칙 (필수 선행)
- STEP 0과 STEP 1의 모든 지표는 반드시 웹검색으로 최신 실데이터를 확보하라.
  추정·기억에 의존하지 말 것. 각 지표마다 (1)수치 (2)기준일 (3)출처를 명시하라.
- 특정 지표를 확보할 수 없는 경우: 해당 Factor를 중립값(리세션 확률 50%)으로
  처리하고, "데이터 미확보 — 중립 처리"라고 명시하라. 임의 추정 금지.

## STEP 0 — 거시 레짐 판별 (5-Factor Recession Composite)
아래 5개 지표를 최신 실데이터로 확보하고, 각각을 0~100%의
리세션 확률로 변환 후 가중합산하라.

| Factor | Weight | 측정 지표 | 임계값(Recession Signal) |
|--------|--------|-----------|--------------------------|
| A. Yield Curve | 30% | 10Y-2Y 스프레드 (bp) | 역전 시 100%, 0~50bp 시 50% |
| B. Sahm Rule | 25% | 실업률 3M MA - 12M 최저치 | ≥0.50%p 시 100% |
| C. ISM Manufacturing | 15% | ISM 제조업 PMI | <45 시 100%, 45~48 시 50% |
| D. LEI | 15% | Conference Board LEI 6M 변화율 | < -2% 시 100% |
| E. Credit Stress | 15% | HY OAS + Chicago Fed NFCI | HY OAS >500bp 또는 NFCI >0 시 100% |

Composite = Σ(Factor × Weight)
Phase 판정:
- Composite < 25%  → Phase 1 (Expansion)
- Composite 25~50% → Phase 2 (Late-Cycle)
- Composite 50~70% → Phase 3 (Recession-Warning)
- Composite ≥ 70%  → Phase 4 (Recession)

## STEP 1 — 국방비 특수 진단 (Defense-Specific Overlay)
리세션 Composite에 아래 방산 특수 지표를 overlay하여
Defense Sentiment Score (0~100)를 산출하라.

| Factor | Weight | 측정 방법 |
|--------|--------|-----------|
| F. 지정학 위험 | 30% | GPR Index / 주요 분쟁 상태 (러-우, 중동, 남중국해, 한반도) |
| G. 국방비 모멘텀 | 25% | 미 국방예산 증감률 + NATO 회원국 GDP 2% 달성률 변화 |
| H. AI-Defense 계약 모멘텀 | 25% | PLTR·Anduril·KTOS 등 AI 방산 기업의 분기 수주 증가율 |
| I. K-방산 수출 모멘텀 | 20% | 한국 방산 수출액 YoY 증감률 (방위사업청 발표 기준) |

Phase 조정 규칙 (Phase 레벨 1~4 기준, 숫자가 클수록 침체):
- Defense Sentiment ≥ 60: 방산 섹터 독립적 강세 → Phase 레벨 -1 적용 (최소 1)
- Defense Sentiment 40~59: 중립 → Phase 그대로 적용
- Defense Sentiment < 40: 방산도 경기 민감 → Phase 레벨 +1 적용 (최대 4)
※ 조정 후 Phase가 최종 배분 기준이 된다. 조정 전후 Phase를 모두 명시하라.

## STEP 2 — Universe (방산·AI-Weaponization 특화 3-Tier)

[ Tier 1: Core Defense — 전통 방산 (Always-On, 경기방어 핵심) ]
  [한국] 한화에어로스페이스(012450), LIG넥스원(079550),
         한국항공우주(047810), 현대로템(064350),
         한화오션(042660), 한화시스템(272210)
  [미국] Lockheed Martin(LMT), RTX(RTX), Northrop Grumman(NOC),
         General Dynamics(GD), L3Harris(LHX), Boeing(BA)
  [ETF] PLUS K방산(449450), TIGER 미국방산TOP10(494840)

[ Tier 2: AI-Defense — 국방 AI 순수 플레이 (구조적 성장) ]
  [미국] Palantir(PLTR), Kratos(KTOS), AeroVironment(AVAV), BigBear.ai(BBAI)
  [Pre-IPO] Anduril (상장 시 편입)
  [한국] 한화시스템(272210) — Tier 1과 중복, AI 플랫폼 비중만 Tier 2로 분류

[ Tier 3: Tactical — 후발주자·변동성·역발상 (Late-Cycle 이상만 활성) ]
  [한국] 풍산(103140), STX엔진(077970), 빅텍(065450),
         HJ중공업(097230), SNT중공업(003570), 퍼스텍(010820)
  [미국] Rocket Lab(RKLB), Huntington Ingalls(HII), Booz Allen(BAH)
  [ETF] ITA, IDEF

Tier 3는 Phase 1(Expansion)에서 강제 비중 0%.
Phase 3 이상에서만 최대 15%까지 활성화.

## STEP 3 — 5-Dimension Scoring (각 종목 100점 만점)
Universe 내 각 종목을 아래 5차원으로 평가하라.

| Dimension | Weight | 평가 기준 |
|-----------|--------|-----------|
| D1. 방산 매출 순도 | 25% | 전체 매출 중 방산 비중 (>70%=만점, <30%=0점) |
| D2. AI/무인화 노출도 | 25% | AI·자율무기·무인체계 매출 또는 계약 비중 |
| D3. 재무 방어력 | 20% | FCF/매출, 부채비율, 이자보상배율 |
| D4. 밸류에이션 규율 | 15% | 선행 PER vs 5년 평균 (할인 시 +) |
| D5. 수출/해외 모멘텀 | 15% | 비내수 매출 비중 + 최근 12개월 해외 수주 증가율 |

## STEP 3.5 — Tier 내 비중 배분 (Score 연동)
각 Tier에 배정된 총 비중(STEP 4 Matrix)을, 해당 Tier 내 종목들의
5-Dimension Score에 비례하여 배분하라.
- 비중 = (종목 Score) / (Tier 내 편입 종목 Score 합계) × Tier 총 비중
- 단일 종목 최대 비중은 Tier 총 비중의 40%로 캡(cap)한다.
- Score 60점 미만 종목은 편입 제외.

## STEP 4 — Phase별 자산 배분 Matrix

| Phase | Tier 1 (Core) | Tier 2 (AI) | Tier 3 (Tactical) | 현금 |
|-------|---------------|-------------|-------------------|------|
| 1. Expansion         | 50% | 30% | 0%  | 20% |
| 2. Late-Cycle        | 55% | 20% | 5%  | 20% |
| 3. Recession-Warning | 60% | 10% | 10% | 20% |
| 4. Recession         | 70% | 0%  | 15% | 15% |

Tier 2(AI-Defense)는 Phase 4에서 강제 비중 0% — 침체기에는
고밸류에이션 AI 방산주가 최대 낙폭을 기록한 사례 다수.
Tier 1(Core)은 Phase 4에서 최대 비중 — Flight-to-Quality.

## STEP 5 — AI-Defense 특별 규칙
1. PLTR 선행 PER > 50배 또는 EV/Sales > 20배 → Tier 2 내 PLTR 비중 50% 자동 축소.
2. Anduril 상장 후 90일 Lock-up 해제 시점까지 Tier 2 편입 보류(상장 직후 5% 한도 예외).
3. KTOS·AVAV·BBAI는 시가총액 $3B 미만일 경우 Tier 2 내 합산 비중 30% 제한.
4. Tier 2 전체 비중이 0%일 경우, 그 비중은 Tier 1으로 이동(현금화 금지).

## STEP 6 — 실행 규칙
1. 분할매수: 총 배분 비중의 20%씩, 5주간 분할 집행.
2. Tier 3 종목은 30일 리밸런싱 강제 — 장기 보유 시 손실 확대 위험.
3. VIX > 35 발생 시: 모든 신규 매수 중단, 기존 포지션 50%만 유지, 나머지 현금화.
4. 한국·미국 각각 최소 30% 이상 비중 유지(한쪽 국가 쏠림 방지).
   ※ 기본 배분 한국 40% / 미국 60%. Defense Sentiment ≥ 70 시 K-방산 +10%p.
5. ETF만으로 구성 시: Tier 1 ETF 70% + Tier 2/AI ETF 20% + 현금 10%
   (Tier 3 ETF는 Phase 3 이상에서만 편입).

## STEP 7 — 반대 시나리오 (이번에 다를 수 있는 이유)
출력 마지막에 반드시 1개 이상 명시하라:
- "현재 방산·AI-Weaponization 전략이 실패할 수 있는 구체적 조건"
  (예: 전쟁 종결로 인한 국방비 급감, AI 규제로 인한 자율무기 개발 중단,
   원자재 가격 급등으로 방산 기업 마진 압박 등)

## 출력 형식
1. 5-Factor Recession Composite + Phase 진단 (지표별 수치·기준일·출처 포함)
2. Defense Sentiment Score + Phase 조정 결과 (조정 전후 Phase 명시)
3. 최종 Phase + Tier별 비중
4. Tier별 추천 종목 (Score 상위 5개 + ETF)
5. 5-Dimension Scoring 요약표 (상위 10종목)
6. 실행 플랜 (분할매수 일정)
7. 반대 시나리오 1개 이상
8. 면책 조항: "본 출력은 LLM 기반 시뮬레이션 결과이며, 실제 투자 권유가
   아닙니다. 모든 투자 판단과 책임은 투자자 본인에게 있습니다."
```

---

## v1.1 개정 사항 (원본 대비)
| 항목 | 변경 내용 |
|------|-----------|
| 데이터 수집 원칙 | 웹검색 강제 + 수치/기준일/출처 명시 의무화, 미확보 시 중립 처리 규칙 추가 |
| Phase 조정 | "1칸 하향/상향"의 모호함 제거 → Phase 레벨 ±1 숫자 기준으로 명확화 |
| STEP 3.5 신설 | 5-Dimension Score를 Tier 내 비중 배분에 직접 연동 (Score 가중 + 40% 캡) |
| 종목 필터 | Score 60점 미만 편입 제외 규칙 추가 |
| 출력 형식 | 지표별 출처·기준일 명시 의무 추가 |
