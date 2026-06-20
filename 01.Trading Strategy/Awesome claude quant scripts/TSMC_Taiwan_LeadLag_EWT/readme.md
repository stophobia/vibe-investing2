# TSMC × 대만 GDP × 대만 ETF(EWT) — 선행지표 검증 & 슈퍼사이클 백테스트

> **한 줄 요약**: 통념("TSMC가 대만 GDP의 22% → 선행지표")을 데이터로 검정한 결과,
> 원계열 YoY 기준 TSMC는 대만 GDP를 *깨끗하게 선행하지 않았고*, TSMC 모멘텀으로
> 대만 ETF를 타이밍한 전략은 단순 보유를 이기지 못했다. TSMC의 진짜 강점은
> '선행'이 아니라 '적시성(고빈도 동행지표)'이다.

이건 한국도 마찬가지 아닌가라는 말이 있겠지만 한국보다 대만이 자본시장이 개방되어 있고 미국 나스닥에 올라가 있기 때문에 더 깨끗하게 노이즈 없이 투자 커플링을 만들 수 있다.

분석 구간: **2020-01 ~ 2026-05** · 관점: **퀀트(매크로 + 시스템 트레이딩)**

---

## 폴더 구조

```
TSMC_Taiwan_LeadLag_EWT/
├── README.md                      ← (현재 파일)
├── requirements.txt
├── data/
│   └── anchors.md                 ← 실측 앵커 데이터 & 출처
├── prompts/
│   ├── 01_data_and_leadlag_prompt.md
│   ├── 02_backtest_prompt.md
│   └── 03_column_prompt.md
├── src/
│   ├── data_lib.py                ← 실데이터 fetch + 캘리브레이션 폴백
│   ├── leadlag.py                 ← 교차상관 / 그레인저 인과
│   ├── backtest.py                ← 모멘텀 타이밍 vs 매수후보유
│   └── run_all.py                 ← 전체 파이프라인
├── results/                       ← 실행 산출물(json/csv/png)
└── column/
    └── TSMC_Taiwan_Column_KR.md   ← 한국어 심층 칼럼
```

## 실행

```bash
pip install -r requirements.txt
cd src && python run_all.py
```

- 온라인이면 `data_lib.py`가 EWT 실데이터(yfinance→stooq)를 받아온다.
- 오프라인이면 **실측 앵커에 캘리브레이션된 재현 가능 데이터셋**으로 자동 폴백한다.
  (`results/*.json`의 `data_source` 필드가 `real-EWT`인지 `reconstructed`인지 표시.)

---

## 핵심 결과 (data_source = reconstructed 기준 예시)

### 1) 선행지표 검증 — 통념을 반증

| 항목 | 값 | 해석 |
|---|---|---|
| 교차상관 최대 lag | **−8개월** | TSMC가 아니라 *GDP가* TSMC를 선행하는 쪽 |
| 최대 상관계수 | 0.53 | 동행성은 있으나 'TSMC→GDP' 선행 아님 |
| TSMC의 그레인저 증분 R² | **+0.2%p** | GDP 예측에 거의 기여 못 함 |

→ "TSMC = 대만 경제 선행지표"라는 통념은 원계열 YoY에서 성립하지 않았다.
원인: 기저효과, TSMC의 긴 주문 백로그(다운사이클에 늦게 꺾임), 분기 GDP vs
월간 매출의 공시 시차. TSMC의 가치는 *선행*이 아니라 *적시성*(45~60일 빠른 공시)과
*전환점 신호*에 있다. (`results/leadlag.png`)

### 2) 투자 시나리오 백테스트 — 타이밍은 단순 보유를 못 이김

| 전략 | 누적수익 | CAGR | 변동성 | Sharpe | MDD |
|---|---|---|---|---|---|
| **Buy & Hold (EWT)** | +132% | +14.2% | 19.3% | **0.79** | −35% |
| TSMC-Momentum Timing | +61% | +7.9% | 13.8% | 0.62 | **−29%** |

→ 타이밍은 낙폭을 ~6%p 줄였지만 수익의 절반 이상을 반납, 위험조정수익(Sharpe)도
더 낮았다. 반도체 슈퍼사이클의 V자 반등을 비중축소 상태로 놓친 탓.
(`results/backtest_equity.png`)

### 3) 세 가지 시나리오
- **항상-롱(슈퍼사이클 베팅)**: 장기·고위험 감내형. 이 구간 최강.
- **모멘텀 타이밍**: 낙폭/심리 부담↓, 강추세장 기회비용↑.
- **다운사이클 방어**: 평소 풀롱, 모멘텀 명백 붕괴 시에만 방어(임계치 조정 가능).

> ⚠️ 집중 리스크: EWT는 사실상 TSMC 단일종목 쏠림 + 양안 지정학 꼬리위험.

---

## ⚠️ 데이터 면책

분기 GDP 일부와 2026년 수치는 추정/재구성치를 포함한다. `reconstructed` 산출물은
*방법론 예시*이며, 온라인 환경에서 실데이터로 교체 후 재실행을 권장한다. 본 분석은
교육·연구용이며 투자 권유가 아니다. 출처는 `data/anchors.md` 참조.

## 📝 칼럼

→ [`column/TSMC_Taiwan_Column_KR.md`](column/TSMC_Taiwan_Column_KR.md)
