# ARDS: Adaptive Recession-Defensive Strategy (한국어판)

> **AMQS의 거울상(逆) 전략** — 4-Factor Momentum Composite 대신 *Recession Probability Composite*, Pullback-in-Uptrend 대신 *Counter-Cyclical Strength* 차원을 채택. *경기 침체 헤지 ETF + 경기 방어주 + Tactical Inverse 동적 포트폴리오 운용*. AMQS의 5-Dimension 100점 채점 구조·-12% 손절·주간 리밸런싱 골격은 그대로 계승.

## 사용 방법

1. 아래 프롬프트 블록을 *전체 복사*
2. Claude / GPT-5 / Gemini / DeepSeek 등 LLM 에 *그대로 붙여넣기*
3. LLM 이 *4-Tier Universe 전체의 점수·신호·비중·백테스트* 자동 생성

> **본 프롬프트는 [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD) 의 *대칭 헤지 전략* 입니다.** 차이점: (1) Universe 가 M7 → *4-Tier Defensive Universe*, (2) D1 차원이 모멘텀 → *Recession Probability*, (3) DIP_BUY 신호 → *FLIGHT_TO_QUALITY 신호*, (4) 거시 레짐이 3단계 → *4단계 (Expansion / Late-Cycle / Recession-Warning / Recession)*.

---

## 프롬프트 (한국어판)

```
[역할]
당신은 글로벌 톱티어 매크로 헤지펀드에서 16년간 경기 사이클 분석, Quality 팩터, Defensive Equity, Recession-Hedge 자산 배분을 담당해온 포트폴리오 매니저이자 매크로 리스크 책임자입니다. 당신의 의사결정 체계는 'Adaptive Recession-Defensive Strategy (ARDS)' 모델에 기반하며, 다중 경기 침체 시그널, Quality/Low-Vol 팩터, 카운터-사이클리컬 상대강도, 변동성 조정 포지션 사이징, 4단계 거시 레짐 필터를 통합해 *주간 리밸런싱 기준 방어형 동적 포트폴리오 수익률* 을 산출합니다.

현재 날짜는 2026년 5월 17일입니다.

[분석 요청 대상 — 4-Tier Defensive Universe]

Tier 1: 방어 섹터 ETF (Always-On Core, 5종목)
   XLP (Consumer Staples), XLV (Healthcare), XLU (Utilities), VPU (Vanguard Utilities), VHT (Vanguard Healthcare)

Tier 2: 경기 침체 헤지 ETF (Always-On Hedge, 6종목)
   TLT (20+ Year Treasury), IEF (7-10Y Treasury), SHV (Short-Term Treasury), GLD (Gold), IAU (Gold), BIL (1-3M T-Bill)

Tier 3: 개별 방어주 (Quality Defensives, 10종목)
   BRK-B (Berkshire), WMT (Walmart), COST (Costco), JNJ (Johnson&Johnson), KO (Coca-Cola), PG (Procter&Gamble), PEP (Pepsi), NEE (NextEra Energy), VZ (Verizon), ABBV (AbbVie)

Tier 4: Tactical Inverse / Volatility (Late-Cycle/Recession-Only, 4종목)
   SH (1x Short S&P), PSQ (1x Short QQQ), VIXY (VIX Short-Term), DOG (1x Short Dow)
   ※ 이 Tier 는 거시 레짐이 Late-Cycle 이상일 때만 활성화. Expansion 구간에서는 무조건 0% 비중.

총 universe: 25종목. 각 종목의 점수·신호·비중을 산출하십시오.

이 전략은 *4-Tier Defensive 동적 포트폴리오* 입니다. 다음 5개 항목을 동시에 정의해야 합니다:
1. 현재 시점 25종목 전체 점수표 (스냅샷)
2. 경기 침체 확률 산출 공식 (5-Factor Recession Composite)
3. *카운터-사이클리컬 상대강도 (Counter-Cyclical Strength)* 점수 산출 공식
4. 주간 리밸런싱 규칙 (진입/유지/청산 조건)
5. 4단계 거시 레짐 필터 (Expansion / Late-Cycle / Recession-Warning / Recession)

[경기 침체 시그널 정의 — 5-Factor Recession Composite, D1 차원의 핵심]

각 시점의 경기 침체 확률은 다음 5개 시그널의 가중합으로 계산:

Component A: 수익률 곡선 역전 (30% 가중치)
   - 10Y-3M 스프레드 (NY Fed Recession Probability Model)
   - 10Y-2Y 스프레드 (보조 지표)
   - 역전 깊이 (basis points) + 역전 지속 기간 (월) 동시 반영
   - "역전 해소 후 6-18개월" 구간은 경기 침체 확률 가산

Component B: Sahm Rule (25%)
   - 실업률 3개월 이동평균 - 직전 12개월 최저치 ≥ 0.50%p → 침체 트리거
   - 0.30%p ~ 0.50%p 구간: 경고
   - 0.50%p 이상: 활성

Component C: ISM Manufacturing PMI (15%)
   - PMI < 50: 수축 (점수 가산)
   - PMI < 45: 침체 임박
   - 3개월 연속 하락 여부

Component D: Leading Economic Index (15%)
   - Conference Board LEI 6개월 변화율
   - -4% 이하 (annualized) → 침체 시그널
   - 컴포넌트별 (yield spread, jobless claims, building permits 등) 기여도 분석

Component E: 신용 스프레드 & 금융 컨디션 (15%)
   - High-Yield OAS (BofA US HY Master II)
   - 400bp 이상: 경고, 500bp 이상: 침체 임박
   - Chicago Fed NFCI (Adjusted) 양수 전환 여부

5-Factor Recession Composite = 0.30·A + 0.25·B + 0.15·C + 0.15·D + 0.15·E
* 각 컴포넌트는 0-100 점으로 정규화 후 가중합

[카운터-사이클리컬 상대강도 (Counter-Cyclical Strength) — 본 ARDS 의 핵심]

전제: *진정한 방어주는 시장 하락일에 강하다.* 단순 저베타 전략은 "낮은 변동성" 만 보지만, *시장 하락일에만 선택적으로 강세를 보이는 종목* 이 진짜 침체 헤지에 효과적입니다.

신호 활성 조건 (모두 충족 시에만 점수 계산, 그렇지 않으면 0점):
   (i)  최근 60거래일 중 SPX 하락일 ≥ 15일 존재
   (ii) 베타 (1년) ≤ 0.75  ← 구조적 저베타
   (iii) Downside Capture Ratio < 70%  ← 시장 하락일 추격 약함
   (iv) Upside Capture Ratio > 40%  ← 시장 상승일 완전 디커플링은 아님

신호 강도 산출:
   기본 = (1 - Downside Capture / 100) × (1 + Sortino Ratio × 0.5)
   + SPX -2% 이상 하락일에 해당 종목 양수 수익률 빈도 가산점 (60일 윈도우)
   + High-Yield OAS 확대 구간 (직전 30일 OAS 50bp 이상 widening) 에 강세 보였으면 추가 가산

z-score 정규화 후 100점 만점으로 변환.

(주: Tier 4 Inverse/VIX 는 본 차원 평가 시 자동으로 100점 만점 — 본질이 역상관)

[100점 종합 채점 — 5-Dimension]

각 종목의 종합 점수는 5개 차원의 가중합:

1. 경기 침체 확률 적합성 (30% 가중치)
   - 위 5-Factor Recession Composite 가 50% 이상일 때 본 차원 가중치 자동 +10%p (다른 차원에서 균등 차감)
   - Tier 1 (방어 섹터 ETF): Composite 가 높을수록 본 차원 점수 상승
   - Tier 2 (Treasury/Gold): 동일하게 상승, 단 TLT 는 금리 인하 기대 추가 반영
   - Tier 3 (개별 방어주): Composite 가 낮으면 본 차원 점수 하향 (강세장에서 방어주는 underperform)
   - Tier 4 (Inverse): Composite 가 60% 미만이면 본 차원 점수 0점 (= 진입 금지)

2. **카운터-사이클리컬 상대강도 (20% 가중치, NEW)**
   - 위 Counter-Cyclical Strength 점수
   - 신호 활성 조건 미충족 시 0점 (이중 안전장치)

3. Defensive Quality 팩터 (20% 가중치)
   - ROE 안정성: 5년 ROE 표준편차 < 5%p
   - Earnings Stability: 5년 EPS 변동계수
   - Dividend Stability: 10년 무삭감 + 5년 연속 증액 여부
   - Free Cash Flow Yield: 5%+ 가산점
   - 부채비율 (D/E) ≤ 1.0

4. 변동성 & 드로우다운 보호 (20% 가중치)
   - 60일 실현 변동성 (낮을수록 점수)
   - Max Drawdown 직전 24개월 ≤ 15% (역사적 침체기 포함)
   - Sortino Ratio (downside-deviation 기반)
   - 200일 이동평균 위 여부 (단, Tier 4 는 반대로 200MA 아래일 때 가산)

5. 거시 환경 적합성 (10% 가중치)
   - 미 10년 국채금리 트렌드 (하락 = TLT/Utility 우호, 상승 = Inverse 우호)
   - VIX 지수 위치 (≥ 25 일 때 모든 방어 자산 가산)
   - 달러 인덱스 (DXY) 트렌드 (Gold 와 역상관)
   - 직전 30일 SPX 변동성 trend (확대 시 본 차원 가산)

총점 = 0.30·D1 + 0.20·D2 + 0.20·D3 + 0.20·D4 + 0.10·D5

[리밸런싱 규칙 — AMQS 골격 계승, ARDS Universe 적용]

진입 (BUY) / 비중 확대 (CORE) 조건:
- 총점 ≥ 75 → CORE 포지션 (Tier 1: 최대 20%, Tier 2: 최대 25%, Tier 3: 최대 10%, Tier 4: 최대 8%)
- 거시 레짐 필터에 해당 Tier 가 활성화되어 있을 것
- 사전 필터 모두 충족

유지 (HOLD) 조건:
- 총점 60~75 → SATELLITE 포지션 (Tier 1: 8-15%, Tier 2: 10-18%, Tier 3: 5-8%, Tier 4: 3-5%)
- 총점 45~60 → TACTICAL 포지션 (3-5%, 손절선 엄격)
- 종목별 손절선 미도달

FLIGHT_TO_QUALITY 특별 신호 (본 전략의 핵심):
- Recession Composite ≥ 60% AND Counter-Cyclical Strength ≥ 70 점
- Tier 1 ETF 또는 Tier 3 개별 방어주 중 해당 신호 발생 종목은 일반 비중에 +3~7%p 가산
- Tier 2 (TLT, GLD) 에서도 발생 가능 — 이 경우 본격 risk-off 진입 시그널

청산 (EXIT) 조건 - 다음 중 하나:
- 종목별 손절선 도달 (-10% from rebalance entry, AMQS 의 -12% 보다 타이트)
- Tier 4 의 경우 -15% 손절 + 4주 보유기간 초과 시 자동 청산 (장기 보유 금지)
- 거시 레짐이 Expansion 으로 회귀 시 Tier 4 전량 청산
- 거시 레짐이 Recession 으로 진입 시 Tier 3 개별주의 50% 이상 청산 후 Tier 1/2 로 재배분

리밸런싱 주기:
- 주간: 매주 금요일 종가 신호 → 월요일 시초가 매매
- 일간: 손절선 + 거시 레짐 변화 트리거만 일간 체크
- 월간: 5-Factor Recession Composite 전체 재산정 (월초 첫 거래일)

[사전 필터 — ARDS 특화]

다음 조건 미충족 시 해당 종목은 universe 에서 제외:
- 시가총액 ≥ $10B (Tier 1/3) — Tier 2/4 는 ETF AUM ≥ $1B
- 30일 평균 거래대금 ≥ $50M
- 60일 실현 변동성 ≤ 35% (Tier 1/3) / ≤ 60% (Tier 2) / ≤ 120% (Tier 4 — VIXY 예외 인정)
- 베타 ≤ 1.0 (Tier 1/3) / 음의 베타 (Tier 4)
- 배당 삭감 직전 12개월 내 없을 것 (Tier 3 한정)

[거시 레짐 필터 — 4단계, ARDS 특유]

Phase 1: Expansion (방어 비중 30% / 위험자산 비중 70% — Tier 4 비활성)
- 10Y-3M > 100bp (정상 곡선)
- Sahm Rule < 0.20%p
- ISM PMI > 52
- LEI 6개월 변화율 > 0%
- HY OAS < 350bp
- → Tier 1: 20%, Tier 2: 10%, Tier 3: 0%, Tier 4: 0%, 위험자산 70% (외부 전략 또는 SPY)

Phase 2: Late-Cycle (방어 비중 55% — Tier 4 부분 활성)
- 위 조건 중 2개 이상 악화 (예: yield curve 평탄화 + LEI 둔화)
- VIX 평균 18-23
- → Tier 1: 25%, Tier 2: 20%, Tier 3: 10%, Tier 4: 0~5% (헤지용 SH 우선)

Phase 3: Recession-Warning (방어 비중 80% — Tier 4 본격 활성)
- 5-Factor Recession Composite ≥ 50%
- yield curve 역전 + Sahm Rule 0.30%p 초과
- ISM < 50 (2개월 연속)
- HY OAS 400bp 초과
- → Tier 1: 30%, Tier 2: 30%, Tier 3: 15%, Tier 4: 5~10%

Phase 4: Recession (방어 비중 100% — Tier 4 최대 활성)
- 5-Factor Recession Composite ≥ 70%
- Sahm Rule 0.50%p 트리거 발동
- 또는 직전 5거래일 SPX -8% 이상 하락
- → Tier 1: 35%, Tier 2: 40%, Tier 3: 10%, Tier 4: 15% (PSQ + VIXY 중심)

[포지션 사이징]

기본: Tier-aware score-tilted allocation
- Tier 별 최대/최소 비중 위 규칙대로 적용
- 각 Tier 내에서는: weight_i = base × (1 + 1.5 × (총점_i - 65) / 30)
- 클리핑: Tier 1 (5-20%), Tier 2 (5-25%), Tier 3 (3-10%), Tier 4 (2-15%)
- 합계 = invested_fraction (Phase 별 가이드)

FLIGHT_TO_QUALITY 종목에 +3~7%p 가산 (다른 종목에서 균등 차감)

(선택적) Risk Parity 사이징:
- 가중치 = (1/실현변동성) / Σ(1/실현변동성)
- TLT 와 같은 고변동성 채권에 절대 비중 제한

(선택적) Convexity 사이징 (Tier 4 한정):
- VIXY 는 contango 손실 (월 5-8%) 감안하여 최대 보유기간 30일 제한
- Inverse ETF (SH/PSQ) 는 daily reset → 장기 보유 시 path dependency 손실 추적 후 자동 청산

[데이터 처리 원칙]
2023년 1월 ~ 2026년 5월 알려진 가격·재무 데이터 + 매크로 이벤트 (2024년 8월 엔 캐리 unwind, 2025년 1월 DeepSeek 쇼크, 2025년 4월 Liberation Day 관세, 2025년 하반기 금리 인하 사이클, 2026년 4월 CPI 3.8% 서프라이즈, 2026년 5월 호르무즈 봉쇄 등) 를 반영한 백테스트 시뮬레이션 결과를 제공하십시오. 추정치에는 ±5% 오차 범위를 명시하십시오. 거래비용 0.03% (ETF) / 0.05% (개별주) + 슬리피지 0.05% 를 차감한 net 수익률을 제시하십시오.

[출력 요구사항]

파트 1: 현재 시점 (2026.05.17) 25종목 점수표 (Tier 별로 분리된 표 4개)
| 티커 | Tier | 5-Factor Recession 점수 | Counter-Cyclical 점수 | 차원별 점수 (D1/D2/D3/D4/D5) | 총점 | 신호 | 권장 비중 | 손절선 |

다음 컬럼 포함:
- 베타 (1Y), Downside/Upside Capture, Sortino Ratio
- 60일 변동성, 24M MDD
- 200MA 위/아래 여부
- 배당수익률 (Tier 3 한정)
- 신호: CORE / SATELLITE / TACTICAL / FLIGHT_TO_QUALITY / REDUCE / EXIT / EXCLUDED
- 진입 근거 (FLIGHT_TO_QUALITY 의 경우 시장 하락일 강세 패턴 명시)
- 손절선 (entry × 0.90, Tier 4 는 × 0.85)

거시 레짐 결정 결과 명시:
- 현재 Phase: Expansion / Late-Cycle / Recession-Warning / Recession
- 5-Factor Recession Composite 현재 값 + 각 컴포넌트별 점수
- 근거: 10Y-3M 스프레드, Sahm Rule 현재값, ISM PMI, LEI 6M, HY OAS

파트 2: 백테스트 결과 (2023-01-03 ~ 2026-04-30)
- 누적 수익률 곡선: ARDS vs SPY vs 60/40 (VTI + AGG) vs 단순 방어 바스켓 (XLP+XLV+XLU 동가중) vs TLT 단독
- 핵심 통계: 총수익률, CAGR, 변동성, MDD, Sharpe Ratio, Sortino Ratio, 회전율
- 거시 이벤트별 성과: 23년 SVB 사태, 24년 8월 엔 캐리 unwind, 25년 1월 DeepSeek 쇼크, 25년 4월 Liberation Day, 25년 9-12월 금리 인하 랠리, 26년 4-5월 인플레 재가속
- *FLIGHT_TO_QUALITY 신호의 알파 기여도* 별도 분석 (이 신호 없는 버전 vs 있는 버전 비교)
- *Phase 별 outperformance breakdown*: Phase 1 (저조 예상) / Phase 3-4 (강세 예상) 의 alpha 분리 측정
- Bear-market period 별 outperformance (SPX -10% 이상 구간 한정)

파트 3: 리스크 분석 및 한계
- ARDS 의 *기회비용*: 강세장 (Phase 1) 에서 SPY 대비 연 4-8%p underperform 예상
- *가짜 침체 시그널 함정 (BEAR_TRAP)*: 2022-23 yield curve 역전 후 18개월 노 랜딩 사례
- Tier 4 (Inverse/VIXY) 의 *contango 손실*: VIXY 월 5-8% 시간 가치 잠식, SH/PSQ daily reset path dependency
- 금리 상승 국면 TLT 의 듀레이션 손실 (2022년 -31%)
- 한국 거주자 양도소득세 영향 (회전율 ~80-120% 가정)
- *방어주의 valuation 위험*: Bond proxy 성격 → 금리 급등 시 동반 하락 (2022년 XLU -1%, XLP -3%)

[경고 문구]
이 분석은 교육 및 정보 제공 목적이며, *방어형 전략은 강세장에서 기회비용을 발생시키고, 거짓 침체 시그널 (false recession signal) 에서 가장 큰 underperform 을 기록* 합니다. *FLIGHT_TO_QUALITY 신호는 진정한 침체 진입기에 비대칭 알파를 제공하지만, 단순 시장 조정 (correction) 에서는 휘프소 손실의 원인* 이 될 수 있습니다 (예: 2022-23 yield curve 역전 후 18개월 동안 노 랜딩이 지속되며 방어주 전략은 SPX 대비 -15%p underperform 했음). *Tier 4 Inverse/Volatility ETF 는 구조적 시간 가치 잠식 (contango, daily reset) 으로 장기 보유 시 100% 손실에 수렴* 하므로 반드시 30일 이내 청산 규칙을 준수해야 합니다. 실제 투자 결정은 개인의 판단과 전문가 상담을 거쳐 이루어져야 합니다. 과거 백테스트가 미래 수익을 보장하지 않습니다.

```

---

## 프롬프트 구조 설명

### 5-Dimension 100점 채점 (AMQS 와 대칭 구조)

| Dimension | AMQS-M7 (Momentum) | **ARDS (Defensive)** | 의미 |
| --- | --- | --- | --- |
| D1. 핵심 매크로 시그널 | 35% (모멘텀) | **30% (Recession Composite)** | 5-Factor 침체 확률 |
| D2. 비대칭 진입 시그널 | 15% (Pullback-in-Uptrend) | **20% (Counter-Cyclical Strength)** | 시장 하락일 상대강도 |
| D3. 펀더멘털 품질 | 25% (가속도) | **20% (Defensive Quality)** | ROE/EPS/배당 안정성 |
| D4. 변동성 조정 | 15% (모멘텀 알파) | **20% (Downside Protection)** | MDD/Sortino |
| D5. 거시 환경 | 10% | **10%** | VIX/금리/DXY |

### 4-Tier Universe 의 구조적 의미

| Tier | 자산군 | 활성 Phase | 역할 |
| --- | --- | --- | --- |
| Tier 1 | 방어 섹터 ETF | 전 구간 | Always-On 핵심 방어 |
| Tier 2 | 채권/금 ETF | 전 구간 (비중 변동) | 듀얼 헤지 |
| Tier 3 | 개별 Quality 방어주 | Phase 2-3 중심 | 알파 가산 |
| Tier 4 | Inverse/VIX | Phase 2-4 한정 | 본격 헤지 (시간 제한) |

### 4단계 거시 레짐 (AMQS 의 3단계 → ARDS 의 4단계)

| Phase | 5F Composite | 방어 비중 | Tier 4 활성 |
| --- | --- | --- | --- |
| 1. Expansion | < 25% | 30% | ❌ |
| 2. Late-Cycle | 25-50% | 55% | 부분 (~5%) |
| 3. Recession-Warning | 50-70% | 80% | 활성 (5-10%) |
| 4. Recession | > 70% | 100% | 최대 (15%) |

---

## 추천 활용 가이드

### 신호별 권장 비중 (Phase 3 기준)

| 신호 | 총점 범위 | Tier 1 권장 | Tier 2 권장 | Tier 3 권장 | Tier 4 권장 |
| --- | --- | --- | --- | --- | --- |
| **CORE** | 75+ | 15-20% | 18-25% | 8-10% | 5-8% |
| **SATELLITE** | 60-75 | 8-15% | 10-18% | 5-8% | 3-5% |
| **FLIGHT_TO_QUALITY** | (변동) | 일반 +3~7%p | 일반 +5%p | 일반 +5%p | — |
| **TACTICAL** | 45-60 | 3-5% | 3-5% | 3-5% | 2-3% |
| **REDUCE** | <45 | <3% | <3% | <3% | 0% |
| **EXIT** | — | 0% | 0% | 0% | 0% |

### 한국 거주자 추가 고려

- **양도소득세 22%**: 미국 주식 매매차익 22% (250만원 공제 후). ARDS 의 *회전율 ~80-120%* 환경에서 *연 2-3% 세금 잠식* (AMQS-M7 보다 낮음)
- **배당소득세**: Tier 1 (XLP 2.5%, XLU 2.8%) + Tier 3 (KO 3%, VZ 6.5%) 배당 → 미국 원천징수 15% + 한국 종합과세 가능 (연 2천만원 초과 시)
- **환전 스프레드**: 0.5-1% 왕복. *Tier 2 채권 ETF 는 장기 보유* (회전율 낮음) → 환전 누적 비용 적음
- **자산 분산**: ARDS 는 *AMQS-M7 의 반대 포지션* — 두 전략 50:50 병행 시 시장 베타 ~0.5 + 침체 진입 시 알파 동시 확보

---

## 위험 고지

- 본 프롬프트의 결과는 *교육·연구 목적의 LLM 시뮬레이션* 이며, 실제 투자 권유가 아닙니다
- *방어형 전략은 강세장에서 기회비용이 큼*: Phase 1 구간에서 SPY 대비 연 4-8%p underperform 가능
- **BEAR_TRAP 시그널의 함정**: 2022-23 yield curve 역전 후 18개월 노 랜딩 → 방어주 전략 대규모 underperform 사례
- **Tier 4 의 시간 가치 잠식**: VIXY 월 5-8%, SH/PSQ daily reset path dependency. *반드시 30일 이내 청산* 규칙 준수
- **금리 상승기 채권 듀레이션 위험**: 2022년 TLT -31%, XLU -1% (방어주임에도 손실)
- 백테스트는 *2023-2026 후기-사이클 환경* 의 결과이며, 1995-99 와 같은 강세 강세장에서는 대규모 underperform 가능

---

## 작성 정보

**시리즈**: vibe-investing — ARDS 신규 모듈 (AMQS 의 대칭 헤지 전략)
**연관 strategy**:
- [AMQS 원본 (NASDAQ-100 + AI Value Chain)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD)
- [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD)
- **ARDS** — Recession-Defensive 4-Tier 전략 (*본 프롬프트*)

**저자**: 김호광 (Dennis Kim / HoKwang Kim)
- Betalabs Inc. CEO, Independent Researcher
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)

**라이선스**: MIT

---

> *"In a bull market, defense is a tax. In a bear market, defense is oxygen. The art is knowing when the air is thinning."*
