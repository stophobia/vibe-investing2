# 미국 금융 섹터 LLM 퀀트 투자 프롬프트 시스템

> 기준일: 2026-06-13 | 버전: v2.1 | 작성: Dennis Kim

---

## 기본 컨셉

이 시스템은 **FQS(Fundamental Quality Score) + OHS(Overheating Score)** 두 축을 독립 채점한 뒤 **사분면**으로 결합하여 투자 판단을 내리는 규율 기반 프레임워크이다.

### 핵심 아이디어

```
좋은 기업(FQS↑) + 좋은 타이밍(OHS↓) → Accumulate (매수)
좋은 기업(FQS↑) + 나쁜 타이밍(OHS↑) → Hold/Trim-Wait (보유/일부매도)
나쁜 기업(FQS↓) + 좋은 타이밍(OHS↓) → Avoid/Value-Trap (회피)
나쁜 기업(FQS↓) + 나쁜 타이밍(OHS↑) → Overheated-Speculation (매도)
```

- **FQS (펀더멘털 품질 점수, 0~100):** 7개 축(성장의 질, 수익성·자본효율성, 안정성·예측가능성, 자본적정성, 자본배분, 해자·경쟁력, 회계 투명성)으로 기업의 정성적 펀더멘털 품질을 평가
- **OHS (과열도 점수, 0~100):** 밸류에이션, 기술적 지표, 포지셔닝, 내구성(역가중), 매크로(ARDS) 5개 성분으로 타이밍 과열도를 평가
- **사분면 결합:** FQS 65 / OHS 56 임계값으로 4개 구간 분류 → 포지션 사이징 직결

> "좋은 기업 ≠ 좋은 가격" 원칙을 구조화한 점이 핵심이다.

### ARDS 연계 사이클

```
Phase 1 (Expansion)         → 공격적 매수
Phase 2 (Late-Cycle)         → 선별적 접근 (MODERATE CAUTION)
Phase 3 (Recession-Warning)  → 방어적 포지션
Phase 4 (Recession)          → 현금 + 인버스 우선
```

---

## 장점

| 장점 | 설명 |
|------|------|
| **품질-타이밍 분리 구조** | "좋은데 비싼" 종목과 "나쁜데 싼" 종목을 명확히 구분. 밸류 트랩 회피에 유용 |
| **LLM 네이티브 설계** | JSON 출력 강제, 추정치 `[추정]` 표기 규칙, 세부 채점 루브릭 명시로 LLM 환각 최소화 |
| **섹터 특화 루브릭** | Banking / Cards & Payments / Insurance / Asset Management 등 세부 섹터별로 맞춤형 지표와 채점 기준 제공 |
| **매크로 사이클 연계** | ARDS 페이즈를 타이밍 모듈에 반영하여 경기 국면을 고려한 판단 가능 |
| **명확한 액션 매핑** | 사분면 → 포지션 사이징(1.0x / 0.5x / 0.0x)으로 직결, 주관적 판단 배제 |
| **리스크 관리 효과** | 백테스트 결과 MDD(최대낙폭)를 평균 30%p 이상 개선 (JPM -43.1%→-13.0%, BAC -48.5%→-13.8%) |

---

## 단점

| 단점 | 설명 |
|------|------|
| **펀더멘털 데이터 수동 입력 필요** | 모든 FQS 입력값(ROE, NIM, CET1, 결합비율 등)을 사용자가 채워야 함. 자동화되지 않으면 실용성 반감 |
| **백테스트는 가격 프록시 기반** | 실제 FQS/OHS가 아닌 RSI·이동평균·모멘텀으로 추정하므로 실제 전략 성과를 온전히 반영하지 않음 |
| **채점 주관성 리스크** | LLM이 루브릭을 해석하는 방식에 따라 동일 기업도 다른 점수가 나올 수 있음 (프롬프트 일관성 문제) |
| **제한적 섹터 커버리지** | 전통 금융(은행, 카드, 보험, 자산운용)에 특화. 핀테크, 암호화폐 거래소, 네오뱅크 등 신규 섹터 루브릭 부재 |
| **강세장에서 기회비용 큼** | Avoid/Overheated 구간에서 0% 포지션 → 상승장에서 Buy & Hold 대비 언더퍼폼 가능성 |
| **룩어헤드 바이어스** | README에 "현재 추천 종목"이 하드코딩되어 있어 LLM이 편향된 답변을 생성할 위험 |

---

## 주의할 점

1. **LLM별 출력 일관성 검증 필수**: Claude, GPT-4o, Gemini 간 동일 입력 → 다른 점수 산출 확인. 각 LLM의 편향 파악 필요
2. **펀더멘털 입력값의 품질 = 결과의 품질**: LLM이 추정한 값(특히 Fwd P/E 백분위, 스트레스테스트 결과 등)은 신뢰도가 낮을 수 있음. 가능한 한 실제 재무제표/블룸버그 데이터 사용
3. **프록시 기반 시그널 한계 인지**: 가격 기반 FQS/OHS 프록시는 후행성(lag)이 있어 실제 펀더멘털 기반 신호보다 늦게 반응. 실전에서는 펀더멘털 + 가격 지표 혼합 사용 권장
4. **주간 리밸런싱 시 비용 고려**: 거래비용 0.1% + 시그널 노이즈로 인한 회전율이 수익률을 잠식할 수 있음. 임계값 조정 검토
5. **섹터 ETF 활용 시 주의**: XLF는 대형 은행 비중이 높아 실제 금융 섹터 다각화 효과 제한적. KBE(은행), KRE(지역은행), IAK(보험), IPAY(결제) 병행 고려
6. **Survivorship Bias 존재**: 2020~2026 구간에서 생존한 대형주만 분석됨. SVB, FRB 등 파산 은행들의 시그널 패턴 미포함
7. **레버리지/인버스 ETF 30일 규칙**: FAS(3x), FAZ(3x)는 일일 리셋 decay 존재. 규칙상 30일 이내 청산 반드시 준수

---

## 금융 세부 섹터별 대표 주식

### Banking (은행)

| 티커 | 기업 | 특징 | 핵심 지표 |
|:--|:--|:--|:--|
| **JPM** | JPMorgan Chase | 미국 최대 은행. ROE 25%+ 5년 연속 초과달성. 퀄리티 최상이나 P/B 고평가 | NIM, ROTCE, CET1 |
| **BAC** | Bank of America | 금리 민감도 최고. NIM 확대 시 직결 수혜. P/B 1.1x로 섹터 내 저평가 | NIM, 대출성장률, 효율성비율 |
| **WFC** | Wells Fargo | Fed 자산상한(Asset Cap) 규제로 성장 구조적 제약. 소매금융 강점 | 무보험예금비중, NPL |
| **GS** | Goldman Sachs | M&A·트레이딩 사이클 민감. IB 수수료 + 성과보수 변동성 큼 | IB Pipeline, 트레이딩 수익 |
| **KBE** | S&P Bank ETF | 미국 은행 전종목. 순수 은행주 노출 | - |
| **KRE** | S&P Regional Bank ETF | 지역은행 집중. 금리 인하 시 수혜 | - |

### Cards & Payments (카드·결제)

| 티커 | 기업 | 특징 | 핵심 지표 |
|:--|:--|:--|:--|
| **V** | Visa | 글로벌 결제 네트워크 해자. 영업이익률 65%+. 반독점 규제 상시 리스크 | GPV 성장률, 크로스보더 |
| **MA** | Mastercard | Visa와 동일 구조. 크로스보더 거래 회복 수혜 | GPV 성장률, 건당 수익 |
| **IPAY** | Mobile Payments ETF | 모바일 결제·핀테크 전반 노출. 섹터 분산용 | - |

### Insurance (보험)

| 티커 | 기업 | 특징 | 핵심 지표 |
|:--|:--|:--|:--|
| **PGR** | Progressive | P&C 보험 직판 모델 1위. 결합비율(Combined Ratio) 업계 최저 수준 | 결합비율, 경과보험료 성장률 |
| **UNH** | UnitedHealth Group | 건강보험 1위. 규제 리스크·결합비율 악화 주의 | 결합비율, RBC, Medical Loss Ratio |
| **IAK** | iShares U.S. Insurance ETF | 보험 섹터 전반 ETF | - |

### Asset Management (자산운용)

| 티커 | 기업 | 특징 | 핵심 지표 |
|:--|:--|:--|:--|
| **BLK** | BlackRock | iShares ETF로 패시브 시장 지배. AUM $10T+. 안정적 수수료 수익 | AUM, 순유입률, Fee Rate |
| **KKR** | KKR & Co. | PE·인프라 대체투자 선두. AI 인프라 투자 파이프라인 확대 | AUM, 순유입, FRE |
| **APO** | Apollo Global Mgmt | 대체투자 AUM 고성장. 연금 자본 유입 수혜 | AUM, Fee-Related Earnings |

### Diversified (복합·기타)

| 티커 | 기업 | 특징 | 핵심 지표 |
|:--|:--|:--|:--|
| **BRK.B** | Berkshire Hathaway | 시총 $1T+. 현금 $300B+ 누적. 자본효율성(ROE) 희석 우려 | Book Value 성장률, 현금비중 |
| **XLF** | Financial Select Sector SPDR | S&P500 금융 전종목. 섹터 벤치마크 | Expense 0.08% |

---

## 투자 도구 매핑

| 전략 | 도구 | 설명 | 주의 |
|:--|:--|:--|:--|
| 섹터 롱 | **XLF** | S&P500 금융 전종목, Expense 0.08% | 대형은행 편중 |
| 은행 집중 | **KBE** | S&P 은행 ETF | XLF 대비 순수 은행 |
| 지역은행 | **KRE** | 지역은행 집중 | 금리 인하기 수혜 가능 |
| 보험 | **IAK** | iShares U.S. Insurance ETF | P&C + 생명보험 혼합 |
| 결제·핀테크 | **IPAY** | 모바일 결제 ETF | V, MA, PYPL 등 포함 |
| 레버리지(단기) | **FAS** | 금융 3배 레버리지 | ⚠️ 30일 이내 청산 |
| 인버스(단기) | **FAZ** | 금융 3배 인버스 | ⚠️ 30일 이내 청산 |

> **레버리지·인버스 ETF는 일일 리셋 decay 존재. 반드시 30일 이내 청산.**

---

## LLM 마스터 프롬프트

아래 프롬프트를 Claude, GPT-4o, Gemini 등 LLM에 복사하여 사용하세요. `{}` 부분을 실제 데이터로 채워서 입력하세요.

```
# ROLE
당신은 규율 기반 미국 금융주 퀀트 애널리스트입니다.
임무는 매수 권유가 아니라 두 모듈로 독립 채점하는 것입니다.
Module 1: 펀더멘털 품질(FQS) / Module 2: 과열도(OHS)
마지막에만 사분면으로 결합합니다.

# CORE PRINCIPLES
1. 품질 vs 타이밍 분리 — 좋은 기업도 비쌀 수 있다
2. 이익의 질 우선 — NIM·결합비율·AUM 순유입 중시
3. 규제 자본 적정성 — CET1, RBC, LCR 필수 확인
4. GAAP vs 핵심이익 분리 — 일회성 제거 후 판단
5. 레버리지 ETF — 30일 이내 청산 원칙
6. 근거 기반 — 수치 지어내기 금지, 추정 시 [추정] 표기
7. 투자자문 아님 — 출력은 진단, 권유 아님

# INPUT (아래 항목을 채워서 입력)
[기업명/티커/기준일/현재가]: {예: JPMorgan Chase / JPM / 2026-06-13 / $309}
[섹터 서브그룹]: {Banking / Cards & Payments / Insurance / Asset Management / Diversified / Brokerage}
[비즈니스 모델]: {간단 설명}

-- 펀더멘털 데이터 --
최근 4분기 매출 YoY: {}
핵심 수익지표:
  ▸ 은행: NIM={} / 비이자수익비중={} / 대출성장률={}
  ▸ 카드: GPV성장={} / 크로스보더={}
  ▸ 보험: 결합비율={} / 경과보험료성장={}
  ▸ 자산운용: AUM={} / 순유입={}
ROE={} / ROA={} / 영업이익률={}
CET1={} (은행) / RBC={} (보험) / 부채비율={}
연체율(NPL)={} / 무보험예금비중={}
FCF마진={} / 배당성향={} / 자사주비율={}
대출손실충당금(LLR)={} / 스트레스테스트={}

-- 타이밍 데이터 --
Fwd P/E={} / P/B={} / P/TBVPS={}
5년 백분위(Fwd P/E)={}%
RSI(14)={} / 200일 이평 이격={}% / 최근 실적 갭={}%
30일 목표가 상향 건수={} / 공매도 비중={}%
ARDS Phase={1 Expansion / 2 Late-Cycle / 3 Recession-Warning / 4 Recession}

# MODULE 1 — FUNDAMENTAL QUALITY SCORE (FQS)
각 축 0~100 채점 → 가중합 = FQS

| 축 | 가중 | 핵심 질문 | 레드플래그 |
|:--|:---:|:--|:--|
| A 성장의 질 | 15% | 유기적 성장 가속? NIM/AUM순유입 추이? | M&A 성장, 연체율 상승 |
| B 수익성·자본효율성 | 20% | ROE·ROA 업계 우위? 조정이익 지속성? | ROE 하락, NIM 축소 |
| C 안정성·예측가능성 | 20% | 예금안정·보험유지율·AUM장기계약? | 예금유출, AUM 순유출 |
| D 자본적정성 | 15% | CET1/RBC 규제치 상회? 배당여력? | CET1 근접, 배당 삭감 이력 |
| E 자본배분 | 10% | 배당·자사주 지속성? | 과도 배당, 무분별 M&A |
| F 해자·경쟁력 | 15% | 전환비용·규제장벽·브랜드? | 핀테크 잠식, 금리리스크 |
| G 회계 투명성 | 5% | 충당금 적정성, 자산건전성? | 충당금 급변동, 빈번한 일회성 |

FQS 등급: 80+ = A / 65~79 = B / 50~64 = C / <50 = D

# MODULE 2 — OVERHEATING SCORE (OHS)
각 성분 0~100 채점 → 가중합 = OHS (높을수록 과열)

| 성분 | 가중 | 채점 기준 |
|:--|:---:|:--|
| A 밸류에이션 | 20% | Fwd P/E·P/B 5년 백분위 고점권↑ |
| B 기술적 | 30% | RSI 70+·200일 이평 +20%+·어닝서프라이즈 클수록↑ |
| C 포지셔닝 | 20% | 목표가 상향 군집·공매도 극저↑ |
| D 내구성(역가중) | 15% | FQS 강할수록 OHS↓ (완충) |
| E 매크로(ARDS) | 15% | Late-Cycle/Recession-Warning일수록↑ |

OHS 페이즈: <36 = Accumulate / 36~55 = Hold / 56~75 = Trim-Wait / 76+ = Overheated

# 사분면 결합 (임계값 FQS 65, OHS 56)
┌─────────────────────────────────────────────────┐
│ FQS≥65 & OHS<56  → Accumulate (매수 기회)       │
│ FQS≥65 & OHS≥56  → Hold/Trim-Wait (보유/일부매도)│
│ FQS<65 & OHS<56  → Avoid/Value-Trap (회피)      │
│ FQS<65 & OHS≥56  → Overheated-Speculation (매도)│
└─────────────────────────────────────────────────┘

# OUTPUT — JSON 형식으로만 출력 (주석 없음)
{
  "ticker": "",
  "as_of": "YYYY-MM-DD",
  "fundamental": {
    "fqs": 0,
    "grade": "A|B|C|D",
    "subscores": {
      "growth": 0,
      "profitability_efficiency": 0,
      "stability_visibility": 0,
      "capital_adequacy": 0,
      "capital_allocation": 0,
      "moat_competition": 0,
      "accounting_transparency": 0
    }
  },
  "timing": {
    "ohs": 0,
    "phase": "Accumulate|Hold|Trim-Wait|Overheated",
    "subscores": {
      "valuation": 0,
      "technical": 0,
      "positioning": 0,
      "durability_inv": 0,
      "macro": 0
    }
  },
  "quadrant": "Accumulate|Hold/Trim-Wait|Avoid/Value-Trap|Overheated-Speculation",
  "gaap_bridge": "GAAP-비GAAP 격차 한줄 설명",
  "price_bands_12m": {
    "bull": [0, 0],
    "base": [0, 0],
    "bear": [0, 0]
  },
  "instruments": {
    "single_lev": "",
    "single_inv": "",
    "sector_long": "XLF / KBE / KRE / IAK / IPAY",
    "index_hedge": "FAS(3x레버리지) / FAZ(3x인버스)"
  },
  "confidence": 0.0,
  "bull_points": ["", "", ""],
  "bear_points": ["", "", ""],
  "estimated_fields": [],
  "data_gaps": []
}

# 면책: 권유 아님. 투자 책임은 본인.
```

---

## Fear/Greed 섹터 진단 프롬프트

금융 섹터 전체 센티먼트를 한 번에 진단할 때 사용합니다.

```
# 금융 섹터 Fear/Greed 진단 프롬프트

아래 데이터를 기반으로 미국 금융 섹터의 현재 Fear/Greed 상태를 
0(Extreme Fear) ~ 100(Extreme Greed) 척도로 채점하고 판정하라.

## 입력 데이터
- XLF 현재가 및 52주 위치: {}
- XLF Fwd P/E 및 5년 백분위: {}
- 금융 섹터 ETF 자금 흐름(4주): {}
- 금융주 평균 RSI(14): {}
- 실적 시즌 어닝 서프라이즈율: {}
- 공매도 비중(XLF): {}
- Fed 금리 방향성: {}
- 신용 스프레드(HY-IG): {}
- VIX: {}
- ARDS Phase: {}

## 채점 기준 (7개 지표 균등 가중)
1. 밸류에이션 백분위 (낮을수록 Fear)
2. 기술적 모멘텀 RSI (낮을수록 Fear)
3. 자금 흐름 (순유출일수록 Fear)
4. 실적 서프라이즈 (하향일수록 Fear)
5. 공매도 비중 (높을수록 Fear)
6. 신용 환경 (스프레드 확대일수록 Fear)
7. 매크로 ARDS (Recession-Warning일수록 Fear)

## 출력 형식
{
  "fear_greed_score": 0~100,
  "label": "Extreme Fear|Fear|Neutral|Greed|Extreme Greed",
  "component_scores": {...},
  "key_signal": "가장 강한 Fear 또는 Greed 신호",
  "tactical_implication": "현재 지수 수준에서의 포지셔닝 가이드"
}
```

---

## 섹터별 특화 채점 루브릭

### Banking (은행)

| 축 | 핵심 지표 | 채점 포인트 | 기준 |
|:--|:--|:--|:--|
| A 성장 | NIM + 비이자수익 유기적 성장 | NIM 확대 중: +, 축소 중: - | NIM ≥ 2.5%: 우수 |
| B 수익성 | ROTCE, ROE, 효율성비율(Cost/Income) | ROTCE 15%+: A | 효율성비율 <55%: 우수 |
| C 안정성 | 무보험예금 비중, CET1, NPL 90일+ | 무보험예금 <25%: 우수 | LDR 80~90%: 적정 |
| D 자본 | CET1 규제치 대비 여유, 스트레스테스트 | 여유 >2%p: 우수 | CET1 ≥ 11.5%: 우수 |
| E 배분 | 배당성향 30~50%, 자사주 | 과잉배당(>70%): 감점 | 배당+자사주 60~80%: 적정 |
| F 해자 | 소매 점포망, 브랜드, 지역 우위 | 디지털 전환 속도 체크 | - |
| G 회계 | ACL 적정성, NPL 분류 엄격성 | 충당금 갑작스런 변동: 감점 | ACL / NPL > 2x: 우수 |

### Cards & Payments (카드·결제)

| 축 | 핵심 지표 | 채점 포인트 | 기준 |
|:--|:--|:--|:--|
| A 성장 | GPV 성장률, 크로스보더 거래 증가 | GPV YoY 10%+: A | 크로스보더 >15%: 강세 |
| B 수익성 | 순이익률, 건당 수익, 영업레버리지 | 영업이익률 50%+: A | - |
| C 안정성 | 반복적 네트워크 수익 비중 | 네트워크 수익 >70%: 우수 | - |
| F 해자 | 네트워크 효과, 전환비용, 규제 감시 | 반독점 규제: 상시 모니터 | - |

### Insurance (보험)

| 축 | 핵심 지표 | 채점 포인트 | 기준 |
|:--|:--|:--|:--|
| A 성장 | 경과보험료 성장, 신계약 증가율 | 경과보험료 YoY 8%+: A | - |
| B 수익성 | 결합비율(손해율+사업비율), ROE | 결합비율 <95%: 우수 | ROE 15%+: A |
| C 안정성 | 보유계약 유지율, 재보험 의존도 | 유지율 >85%: 우수 | 재보험 의존도 <30% |
| D 자본 | RBC 비율 300%+, 부채적정성 | RBC <200%: 감점 | RBC ≥ 400%: 우수 |

### Asset Management (자산운용)

| 축 | 핵심 지표 | 채점 포인트 | 기준 |
|:--|:--|:--|:--|
| A 성장 | AUM 성장, 순유입률(유기적) | 순유입 >3% AUM: A | 유기적 성장 > M&A 성장 |
| B 수익성 | 평균 Fee Rate, 영업이익률, ROE | 영업이익률 40%+: A | Fee Rate 안정성 체크 |
| C 안정성 | 장기계약 AUM 비중, 고객 집중도 | 장기계약 >60%: 우수 | Top 10 고객 <30% |
| G 회계 | 성과보수 일회성 여부, GAAP 격차 | 성과보수 변동성 큼: 주의 | FRE/AUM > 30bp: 우수 |

---

## 백테스팅

Python 백테스팅 코드: `financial_sector_backtest.py`

### 설치 및 실행

```bash
pip install yfinance pandas numpy matplotlib scipy
python financial_sector_backtest.py
```

### 백테스트 결과 (2020-01-01 ~ 2026-06-12, 실제 yfinance 데이터)

```
───────────────────────────────────────────────────────────────────────────
티커   전략          CAGR%    샤프     MDD%     승률%   총수익%
───────────────────────────────────────────────────────────────────────────
XLF    Buy&Hold     10.7%   0.354    -42.9%    52.4%    92.5%
JPM    사분면전략     3.2%  -0.155    -13.0%    11.6%    22.5%
JPM    Buy&Hold     16.7%   0.508    -43.1%    52.8%   169.8%
BAC    사분면전략     5.4%   0.122    -13.8%    12.5%    40.0%
BAC    Buy&Hold      9.9%   0.314    -48.5%    51.4%    83.0%
UNH    사분면전략    -0.9%  -0.455    -25.2%    12.0%    -5.6%
UNH    Buy&Hold      7.0%   0.243    -61.4%    52.4%    55.0%
───────────────────────────────────────────────────────────────────────────
```

### 백테스트 인사이트

| 인사이트 | 내용 |
|----------|------|
| **MDD 개선 효과** | JPM -43.1%→-13.0%, BAC -48.5%→-13.8%, UNH -61.4%→-25.2%. 평균 30%p 이상 개선 |
| **CAGR 희생** | 사분면 전략은 Buy&Hold 대비 CAGR 낮음. 이는 현금 보유 구간(Avoid/Overheated)으로 인한 기회비용 |
| **강세장 불리** | 2020~2026 기간은 전반적 강세장 → Buy & Hold가 우위. 약세장에서 사분면 전략의 방어력이 빛날 것 |
| **FQS/OHS 프록시 한계** | 가격 기반(RSI+모멘텀+변동성)으로만 추정해 후행성(lag) 발생. 실제 펀더멘털 기반 시그널과 괴리 존재 |
| **UNH 마이너스** | 헬스케어 규제 리스크가 가격에 반영되며 가격 기반 FQS가 낮게 유지, Avoid 구간에 오래 머문 영향 |

> **핵심 결론:** 이 프롬프트 시스템의 실전 가치는 **펀더멘털 데이터 입력 + LLM의 정성적 판단**이 결합될 때 발현된다. 가격 프록시만으로는 Buy & Hold를 이기기 어렵지만, **MDD 개선을 통한 리스크 관리 도구**로서의 가치는 유의미하다.

---

### 현재 스냅샷 (2026-06-12 기준)

```
섹터 Fear/Greed Score: 65.9 / 100  [Greed]
ARDS Phase 추정: Phase 2 (Late-Cycle)

티커    현재가    FQS   OHS   사분면                  판정
XLF     $53.22   61.1  36.9  Avoid/Value-Trap        회피
JPM     $319.58  61.0  41.5  Avoid/Value-Trap        회피
BAC     $55.67   72.0  52.4  Accumulate              매수
WFC     $83.40   60.4  41.6  Avoid/Value-Trap        회피
V       $322.24  49.6  21.9  Avoid/Value-Trap        회피
MA      $489.16  49.9  13.7  Avoid/Value-Trap        회피
UNH     $407.82  61.2  65.2  Overheated-Speculation  매도
PGR     $202.76  51.5  26.2  Avoid/Value-Trap        회피
GS      $1065.20 63.2  63.6  Overheated-Speculation  매도
BLK     $1026.84 53.9  17.7  Avoid/Value-Trap        회피
KKR     $97.22   48.1  14.1  Avoid/Value-Trap        회피
APO     $135.73  54.4  42.9  Avoid/Value-Trap        회피
KBE     $66.71   73.8  49.1  Accumulate              매수
KRE     $73.12   73.6  51.2  Accumulate              매수
```

> ⚠️ FQS/OHS는 가격 기반 프록시. 실제 펀더멘털 데이터로 검증 필요.

---

## 면책 고지

```
본 문서는 투자 권유가 아닌 분석 프레임워크 제공을 목적으로 합니다.
모든 투자 결정의 책임은 투자자 본인에게 있으며,
실제 투자 시 전문 투자 자문사와 상담하시기 바랍니다.

작성: Dennis Kim (HoKwang Kim) / Betalabs Inc.
GitHub: github.com/gameworkerkim
ORCID: 0009-0002-0962-2175
```
