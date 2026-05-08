# Dual-Engine Capital Compounder Quant Strategy Using LLM (한국어판)

> **미국 금융 + 리테일 배당주 동시 발굴 LLM 프롬프트**
> S&P 500 의 *Financials* 와 *Consumer Discretionary/Staples* 섹터에서 *자본 환원율(배당 + 자사주) + 사이클 방어력* 을 동시에 충족하는 Top 10 종목 발굴 + 동일가중 포트폴리오 시뮬레이션

---

## 사용 방법

1. 아래 프롬프트 블록을 *전체 복사* (코드 블록 우상단의 복사 버튼 클릭)
2. Claude / GPT-5 / Gemini / DeepSeek 등 LLM 에 *그대로 붙여넣기*
3. LLM 이 Top 10 종목 + 섹터 분산 분석 + 포트폴리오 시뮬레이션을 자동 생성

> **언어 선택 가이드**: 본 한국어판은 *한국어 결과* 를 받기 원하는 사용자용입니다. *토큰 소모량을 줄이고 싶다면* [영문판 (Dual Engine Compounder Prompt EN.MD)](./Dual%20Engine%20Compounder%20Prompt%20EN.MD) 사용을 권장합니다 — *영문 프롬프트가 한국어 대비 약 30-40% 토큰 절감* 효과가 있습니다. 중화권 시장 분석을 함께 보려면 [중문판 (Dual Engine Compounder Prompt CN.MD)](./Dual%20Engine%20Compounder%20Prompt%20CN.MD) 도 참고하세요.

---

## 프롬프트 (한국어판)

```
[역할]
당신은 글로벌 톱티어 자산운용사에서 14년간 금융주와 소비자(리테일) 섹터의 자본 환원 전략을 동시에 운영해온 포트폴리오 매니저이자 퀀트 리서치 책임자입니다. 당신의 의사결정 체계는 'Dual-Engine Capital Compounder' 모델에 기반하며, 두 가지 자본 회전 메커니즘을 통합 평가합니다:

- 금융주 엔진: 자본 듀레이션을 활용한 NIM·수수료·운용보수 회전
- 리테일 엔진: 재고 회전 + 소비자 현금흐름의 단주기 환원

이 두 엔진은 거시 사이클에 *비대칭적 반응* 을 보이며, 동시 보유 시 변동성이 자연스럽게 상쇄됩니다.

현재 날짜는 2026년 5월 2일입니다. (편의상 오늘 날짜 기준으로 가정)

[분석 요청 대상]
S&P 500 구성 종목 중, 다음 두 섹터에서 각 5개씩 총 10개 종목을 선별하십시오.

【Financial 섹터 (5종목)】 - 다음 4개 sub-segment 에서 균형 선택
- Megabank (메가뱅크): JPM, BAC, WFC, C
- Asset Management & Exchanges (자산운용·거래소): BLK, BX, KKR, AMP, TROW, SCHW, CME, ICE, NDAQ
- Card Networks & Premium Cards (카드 네트워크·프리미엄): V, MA, AXP, COF, DFS
- Insurance (보험): BRK.B, TRV, PGR, ALL, AFL, CB, MET, PRU, AIG

【Retail 섹터 (5종목)】 - 다음 4개 sub-segment 에서 균형 선택
- Mass Retail (대형 할인): WMT, COST, TGT, BJ
- Home Improvement (홈 개량): HD, LOW
- Off-Price & Specialty (오프프라이스·스페셜티): TJX, ROST, ULTA, BBY, DG
- Restaurant & QSR (외식·QSR): MCD, SBUX, YUM, CMG, DPZ, TXRH

[스크리닝 조건]
[금융주]
- 5년 연속 배당 인상 또는 자사주 매입 일관성
- ROE ≥ 12% (메가뱅크) 또는 ≥ 18% (자산운용·카드)
- Tier 1 자본비율 ≥ 12% (은행) 또는 부채비율 ≤ 1.5x (비은행)
- 배당성향 ≤ 50% + 자사주 매입 + 배당 합산 환원율 ≥ 50%

[리테일주]
- 5년 연속 배당 인상 (Aristocrat 또는 King 기록 우대)
- ROIC ≥ 15%, FCF Margin ≥ 6%
- Net Debt / EBITDA ≤ 3.0x
- 5년 평균 동일점포매출 (SSS) 양수 유지

[점수 체계 - 종목별 총 100점]

1. 수익 품질 & 자본 환원율 (35% 가중치)
   - 금융: ROE, Tier 1 Capital, NIM 안정성, 운용보수 마진
   - 리테일: ROIC, FCF Conversion, Same-Store Sales 안정성, 옴니채널 수익화
   - 공통: 자사주 매입 + 배당 합산 Total Capital Return Yield (TCRY)

2. 배당 성장 모멘텀 (30%)
   - 5년·10년 연평균 배당 증가율
   - 배당 인상 연속 기록 (25년+ Aristocrat / 50년+ King 가산점)
   - Payout Ratio 안정화 추세 (점진적 상승은 음의 점수, 안정성 양의 점수)
   - 분기 배당 발표일 전후의 가격 모멘텀 패턴

3. 밸류에이션 (20%)
   - 금융: P/TBV (장부가 대비), Forward P/E, Dividend Yield vs 10Y UST 스프레드
   - 리테일: EV/EBITDA, Forward P/E, FCF Yield, 5년 평균 대비 멀티플 위치
   - 공통: PEG (P/E ÷ EPS Growth) ≤ 2.0 우대

4. 사이클 방어력 (15%)
   - 금융: Net Charge-off Ratio 추이, 대출 손실 충당금, 자본 적정성 스트레스 테스트 결과
   - 리테일: Gross Margin 안정성, 재고 회전율, 옴니채널 비중 (e-commerce ≥ 15%)
   - 공통: 2008·2020 경기 침체기 drawdown 폭 + 회복 속도

[데이터 처리 원칙]
2025년 4월까지의 알려진 재무 데이터와 가격 이력 + 2026년 1분기 어닝을 기반으로 합리적 시뮬레이션을 수행하십시오. 추정치에는 ±5% 오차 범위를 명시하십시오. 금융주의 경우 *연방준비제도의 CCAR 스트레스 테스트 결과* 와 *FOMC 의 점도표* 를 거시 환경 가정에 반영하십시오.

[출력 요구사항]

파트 1: 상위 10개 종목 리포트 (표 형식 포함)
- 티커, 회사명, 섹터(Financial/Retail), Sub-segment, 현재가(추정), 시가총액
- 배당수익률, 5년 배당 CAGR, Total Capital Return Yield (TCRY)
- 배당성향, ROE 또는 ROIC, 핵심 멀티플 (P/TBV 또는 EV/EBITDA)
- 4개 항목별 점수 및 총점
- 핵심 투자 근거 3가지 (자본 환원 내러티브 + 정량 지표)
- 리스크 요인 2가지 (NIM 압박, 소비자 약세, 규제 등)
- 12개월 목표 총수익률 및 손절 기준

파트 2: Dual-Engine 균형 분석
- Financial vs Retail 50:50 비중의 합리성
- 두 엔진 간 상관관계 (1990-2025 historical correlation)
- 사이클 단계별(Early Cycle / Mid / Late / Recession) 최적 비중 제안

파트 3: 10개 종목 동일가중 포트폴리오
- 예상 배당수익률 + TCRY (세전)
- 추정 베타, 변동성, Sharpe Ratio (3Y)
- S&P 500 대비 초과 성과 가능성에 대한 정성적 평가
- 사이클 전환점 시그널 (예: 미 10Y 금리 급등, 소비자 신뢰지수 급락, NIM 압박, e-commerce 점유율 변동)

[경고 문구]
이 분석은 교육 및 정보 제공 목적이며, 금융주는 *시스템 위기* 시 -50% 이상 drawdown 가능성을, 리테일주는 *경기침체* 시 매출 축소와 마진 압박 위험을 동시에 가집니다. 실제 투자 결정은 개인의 판단과 전문가 상담을 거쳐 이루어져야 합니다. 과거 배당 기록이 미래 배당을 보장하지 않으며, 2008년 GFC 당시 미 메이저 은행들의 *배당 90% 컷* 사례를 반드시 인지해야 합니다.
```

---

## 프롬프트 구조 설명

### Dual-Engine 모델

본 프롬프트는 *두 가지 자본 회전 메커니즘* 을 LLM 이 *통합 평가* 하도록 강제합니다:

| 엔진 | 자본 회전 메커니즘 | 핵심 KPI | 거시 민감도 |
| --- | --- | --- | --- |
| **Financial Engine** | NIM·수수료·운용보수 (자본 듀레이션 활용) | ROE, NIM, AUM 성장 | 금리 + 신용 사이클 |
| **Retail Engine** | 재고 회전 + 소비자 현금흐름 (단주기) | ROIC, SSS, 재고 회전 | 소비자 신뢰 + 임금 |

> **두 엔진의 비대칭성**: 금리 상승 국면에서 *금융 엔진의 NIM은 확장* 되지만, *리테일 엔진은 소비 위축* 으로 압박. 반대로 금리 하락 국면에서는 *금융 NIM 압박* + *리테일 소비 회복*. 동시 보유 시 *거시 사이클 변동성을 자연 헤지* 합니다.

### 점수 가중치 설계 철학

| 차원 | 가중치 | 핵심 질문 |
| --- | --- | --- |
| **수익 품질 & 자본 환원** | **35%** | "이 회사가 *주주에게 얼마나 많이* 환원하는가?" |
| **배당 성장 모멘텀** | **30%** | "환원이 *복리로 증가* 하는가?" |
| **밸류에이션** | **20%** | "지금 *가격이 합리적* 인가?" |
| **사이클 방어력** | **15%** | "*경기 침체에서 살아남을* 수 있는가?" |

> **AI Super Cycle 프롬프트 대비 차이**: AI 매출 노출도(35%) 가중치가 *수익 품질 & 자본 환원율(35%)* 로 대체됨. *모멘텀·수급(15%)* 이 *사이클 방어력(15%)* 으로 대체 — 배당주 투자에서는 *생존 능력* 이 *기술적 모멘텀* 보다 중요하기 때문입니다.

---

## 추천 포트폴리오 및 전망

본 프롬프트의 LLM 결과로 *권장* 되는 10종목 (시뮬레이션 기준):

### 🏦 Financial Engine (5종)

| # | 티커 | 회사명 | Sub-segment | 점수 | 배당수익률 | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **JPM** | JPMorgan Chase | Megabank | **88** | 2.05% | 6.5% |
| 2 | **BLK** | BlackRock | Asset Mgmt | **86** | 1.90% | 4.8% |
| 3 | **V** | Visa | Card Network | **90** | 0.65% | 4.7% |
| 4 | **AXP** | American Express | Premium Card | **85** | 1.05% | 5.1% |
| 5 | **CB** | Chubb | Insurance (P&C) | **82** | 1.25% | 4.0% |

### 🛒 Retail Engine (5종)

| # | 티커 | 회사명 | Sub-segment | 점수 | 배당수익률 | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | **HD** | Home Depot | Home Improvement | **87** | 2.17% | 6.2% |
| 7 | **WMT** | Walmart | Mass Retail | **84** | 0.87% | 2.9% |
| 8 | **TGT** | Target | Discount Retail | **80** | 2.89% | 6.5% |
| 9 | **TJX** | TJX Companies | Off-Price Retail | **86** | 1.15% | 4.7% |
| 10 | **MCD** | McDonald's | QSR | **83** | 2.28% | 5.4% |

> **TCRY (Total Capital Return Yield) = 배당수익률 + 자사주 매입수익률** — 자본 환원의 *완전한* 측정치. 단순 배당수익률보다 약 2-3배 높은 것이 일반적.

### 포트폴리오 선택 근거 (Quant 관점)

1. **이중 헤지 구조**: 금리 상승기에는 JPM·BLK 의 *NIM·AUM 가중* 매출이 증가하지만 HD·TGT 의 *주택 관련 소비* 가 약세. 금리 하락기에는 *반대 패턴* 이 발현 → **두 엔진의 음의 상관관계가 변동성 흡수**.

2. **Card Networks 의 양면 노출**: V 와 AXP 는 *Financial 섹터로 분류* 되지만 매출 메커니즘은 *Retail 의 거래 수수료* 에 가까움 → **두 엔진의 가교 역할**. 카드 네트워크 두 종목이 양 엔진의 베타를 자연스럽게 융합.

3. **Dividend Aristocrat/King 비중 60% 이상**:
   - **Dividend Aristocrats (25년+)**: TJX, MCD (28년+), TGT (54년+, *King*), CB (31년+)
   - **장기 배당 인상 기록**: HD (15년+), JPM (재시작 14년+), V (16년+), BLK (21년+)
   - 이 우량 배당 트랙은 *시스템 위기* 에서도 배당 컷 가능성이 *통계적으로 낮음*.

### 12개월 시장 전망 시나리오

| 시나리오 | 확률 | S&P 500 수익률 | 본 포트폴리오 |
| --- | --- | --- | --- |
| 🟢 **Goldilocks** (성장 + 인플레이션 둔화 + 금리 하락) | 30% | +18% | **+22%** |
| 🟡 **기본** (완만한 성장 + 안정 금리 + 소비 견조) | 45% | +9% | **+13%** |
| 🟠 **스태그플레이션** (인플레이션 재발 + 성장 둔화) | 20% | -5% | **-2%** |
| 🔴 **경기 침체** (실업률 6%+ + 신용 사이클 악화) | 5% | -22% | **-15%** |

> **기대수익률 가중평균**: S&P 500 +9.5% vs 본 포트폴리오 **+12.6%** → **초과 알파 약 +3.1%p**

> **방어력 우위**: 침체 시나리오에서 S&P 500 (-22%) 대비 본 포트폴리오 (-15%) 의 *7%p 방어력 우위* 가 핵심. 이 방어력은 배당 컷 안정성 + 리테일 매출 비탄력성에서 비롯됩니다.

### 사이클 전환점 시그널 (모니터링 체크리스트)

- ⚠️ **금융 사이클**: 미 4대 은행 합산 Net Charge-off ≥ 1.0% (*현재 0.6%대*) 진입 시 신용 사이클 악화 신호
- ⚠️ **카드 결제**: V 와 MA 의 결제 거래량 YoY 성장률이 +5% 미만으로 둔화 시 소비 약화 시그널
- ⚠️ **소비자 신뢰**: Conference Board 소비자 신뢰지수 ≤ 90 진입 시 리테일 매출 압박
- ⚠️ **주택 사이클**: 30년 모기지 금리 ≥ 7.5% 또는 기존주택 매매 SAAR ≤ 350만 단위 진입 시 HD/LOW 매출 압박
- ⚠️ **자산운용**: BLK·BX 의 운용수수료 마진이 14bp 미만으로 압축 시 패시브 경쟁 가속

---

## 출력 결과 활용 가이드

### Part 1 (Top 10 종목)

* **점수 85점 이상**: *Core 포지션* 후보 — 비중 12-15% 가능 (V, JPM, HD, TJX)
* **점수 80-85점**: *Satellite 포지션* — 비중 8-10%, 분기별 재평가
* **점수 80점 미만**: *Tactical 포지션* — 비중 5% 이하, 거시 신호 활용 진입

### Part 2 (Dual-Engine 균형)

* **Early Cycle (회복기)**: Financial 비중 ↑ (60-70%) — 신용 사이클 회복 + 대출 성장
* **Mid Cycle (확장기)**: 50:50 균형 유지
* **Late Cycle (정점기)**: Retail 비중 ↑ (60%) — 방어 + 임금 인플레 수혜
* **Recession (침체기)**: Cash 비중 확대 + Retail Staples (WMT, COST) 집중

### Part 3 (동일가중 포트폴리오)

* 예상 배당수익률 + TCRY (세전): *5.0~6.5%* 범위
* 추정 베타: *0.85~1.00* (시장 베타 1.0 대비 약간 방어적)
* 한국 거주자 *원천징수 15% + 양도소득세 22%* 별도 고려
* S&P 500 대비 *outperform 가능성* 은 *late cycle / 스태그플레이션 환경* 에서 우호적

---

## 토큰 효율성 비교

| 언어 | 입력 토큰 | 출력 토큰 | 총 비용 (Claude Opus 4.7 기준) |
| --- | --- | --- | --- |
| 한국어 | 약 1,800 tokens | 약 4,500 tokens | 약 $0.099 |
| 영어 | 약 1,200 tokens | 약 3,200 tokens | 약 $0.069 |
| 중국어 (간체) | 약 1,300 tokens | 약 3,500 tokens | 약 $0.076 |

> **권장**: *반복 사용 (월 1회 리밸런싱 등)* 시 영문판 사용으로 *연간 약 $7-12 절감* 가능. 결과 *해석* 만 한국어로 받으려면 프롬프트 끝에 *"답변은 한국어로 작성"* 추가.

---

## 한국 거주자 추가 고려 사항

### 세금

* **배당 원천징수**: 미국 15% + 한국 종합과세 (배당소득 2,000만원 초과 시 누진세율) — 본 포트폴리오는 *연 5.0~6.5% TCRY* 중 배당 비중이 절반 → *연 10만 달러 투자 시 약 $2,500-3,250 의 배당 발생* → 한국 종합과세 대상 가능
* **양도소득세**: 미국 주식 매매차익 22% (250만원 공제 후) — *분할매도로 250만원 공제 활용* 권장
* **외환차손익**: 매매시 환율 차이 별도 과세

### 절세 계좌 활용

* **ISA (개인종합자산관리계좌)**: 국내 ETF 한정. *KODEX 미국 S&P500 금융주, KODEX 미국 S&P500 자유소비재, TIGER 미국 S&P500 헬스케어* 등으로 간접 노출
* **연금저축**: 국내 운용사 운용 ETF 한정. *KODEX 미국S&P500 배당귀족 (Dividend Aristocrats 추종)* 활용
* **퇴직연금 (DC/IRP)**: 70% 위험자산 규제 내에서 미국 ETF 활용

### 한국 상장 미국 배당주 ETF 대안

| 한국 ETF | 추종 지수 | 본 전략과의 매칭도 |
| --- | --- | --- |
| KODEX 미국S&P500 배당귀족 | S&P 500 Dividend Aristocrats | ★★★★★ (TGT, CB, MCD 등 직접 포함) |
| TIGER 미국 S&P500 금융 | S&P 500 Financials | ★★★★ (JPM, V, BLK 등 비중) |
| ACE 미국빅테크TOP7 Plus | M7 | ★★ (테크 위주, 본 전략과 다름) |
| TIGER 미국 컨슈머스테이플 | S&P 500 Cons. Staples | ★★★ (WMT, COST 등 포함) |

> 위 ETF 들은 *한국 ISA 계좌* 에서 활용 가능 (절세 효과). 단, *해외주식형 ETF는 분배금에서 15.4% 원천징수* 후 추가 종합과세 가능.

### 환헤지 의사결정

* **환노출형** (직접 보유 JPM, HD 등): 달러 강세 시 추가 수익. *late cycle 진입기에는 달러 강세 가능성 높음*
* **환헤지형** (예: KODEX 미국S&P500선물(H)): 환율 변동 위험 차단. *원/달러 1,400원대 진입 시 환헤지 비중 확대 검토*

---

## 위험 고지

* 본 프롬프트의 결과는 *교육·연구 목적의 가상 시뮬레이션* 이며, 실제 투자 권유가 아닙니다
* LLM 의 데이터는 *2025년 4월까지의 알려진 정보* 기반이며, *실시간 가격/배당 데이터가 아닙니다*
* 추정치는 *±5% 오차 범위* 가 있으며, *실제 시장 데이터로 재검증* 필수
* **2008 글로벌 금융위기 당시 BAC 배당 -90%, C 배당 -97% 컷** — *Dividend Aristocrat 자격 박탈* 사례 존재. 메가뱅크의 *시스템 위기 노출도* 인지 필수
* **2020 팬데믹 당시 WMT/COST 등 staples 는 매출 +10~15% 성장**, 그러나 *외식·여행·럭셔리 리테일은 -30~50% 매출 충격*. 리테일 내에서도 *방어/성장 sub-segment 차별화* 필요
* **카드 네트워크(V, MA)의 반독점 리스크**: 미 법무부의 결제 네트워크 독점 소송 + 스테이블코인 확산 (예: USDC, PYUSD) 으로 인한 *장기 점유율 침식* 가능성
* 한국 거주자는 *외환거래법 + 양도소득세 + 종합과세* 별도 검토
* LLM 이 생성한 코드/추천을 실거래에 사용하기 전 반드시 *독립 데이터 소스* (예: SeekingAlpha, Morningstar, Bloomberg) 로 *교차 검증*

---

## 작성 정보

**시리즈**: vibe-investing — Awesome Claude Quant Scripts
**연관 sub-strategy**:

* [Dividend Growth Prompt kr.MD](../Dividend%20growth%20prompt/Dividend%20Growth%20Prompt%20kr.MD) — 6-섹터 분산 배당 성장 (본 프롬프트의 *전신*)
* [AI Super Cycle Prompt kr.MD](../AI%20Super%20Cycle%20Prompt/AI%20Super%20Cycle%20Prompt%20kr.MD) — 4-Layer AI 가치사슬 분산
* [Long-Term Dividend Investing](../Long-Term%20Dividend%20Investing) — 장기 보유 코드 구현
* [DAT Quant Strategy](../DAT%20quant%20strategy) — 디지털 자산 보유 기업 전략

**저자**: 김호광 (Dennis Kim / HoKwang Kim)

* Independent Researcher, Betalabs Inc. CEO, Cyworld Z 전 CEO
* ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
* GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
* Email: [gameworker@gmail.com](mailto:gameworker@gmail.com)

**작성일**: 2026년 5월 2일 v1.0
**라이선스**: MIT (자유 사용, 출처 표기 권장)

---

> *"Compounding is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."* — Albert Einstein
> *"복리는 세계 8번째 불가사의다. 이해하는 자는 얻고, 이해하지 못하는 자는 잃는다."*
