# ARDS-X — Regime Classifier (조정 · 단기 과매도 · 하락 · 침체 판별)

> *"하락에는 네 가지 얼굴이 있다 — 건강한 조정, 단기 과매도, 구조적 하락, 그리고 침체. 똑같이 빨갛게 보이지만, 처방은 정반대다."*

**시리즈**: vibe-investing — [ARDS](../ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/) 의 실데이터 확장 모듈 (eXtension)
**저자**: 김호광 (Dennis Kim / HoKwang Kim) · Betalabs Inc. · ORCID [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
**작성일**: 2026-06-06 · **라이선스**: MIT

---

## 1. 한눈에 보기 (TL;DR)

ARDS-X 는 **"미국 빅테크 + AI/인프라 복합체와 S&P500·Nasdaq100 이 지금 *조정*인지, *단기 과매도*인지, *구조적 하락*인지, *침체로 인한 자산 리밸런싱*인지"를 실데이터로 자동 분류**하는 퀀트 확장입니다.

- **ARDS 원본**은 LLM 프롬프트로 5-Factor Recession Composite 를 *추정*하고 synthetic 백테스트를 냈습니다.
- **ARDS-X 는 동일한 5-Factor 를 실데이터(FRED 무료 CSV + yfinance)로 직접 계산**하고, 여기에 **가격구조(드로다운·추세·과매도) 축**을 더해 **2-축 레짐 맵**을 만듭니다.
- 결과는 5개 상태 중 하나로 분류되고, 각 상태는 **자매 전략(AMQS / ARDS)으로의 핸드오프**까지 제시합니다.

```
quant/run.py  →  dashboard/data/latest.json  →  dashboard/index.html
 (실데이터 계산)        (레짐 판정 결과)            (대시보드 시각화)
```

---

## 2. 왜 이게 필요한가 — "조정 vs 하락 vs 침체" 의 함정

투자자가 가장 자주 틀리는 지점은 **하락의 *성격*을 오판**하는 것입니다.

| 보이는 현상 | 실제 성격 | 올바른 행동 | 오판 시 결과 |
|---|---|---|---|
| 지수가 빠진다 | **조정** (상승추세 내 눌림) | 분할매수 / 보유 | (오판: 공포 매도 → 바닥에 던짐) |
| 지수가 빠진다 | **단기 과매도** | 전술적 반등 매수 | (오판: 추세 추종 매도) |
| 지수가 빠진다 | **구조적 하락** | 리스크 축소 / 헤지 | (오판: "조정"이라 믿고 물타기 → 큰 손실) |
| 지수가 빠진다 | **침체 리밸런싱** | 방어 포트폴리오 전환 | (오판: 저점매수 → 침체 내내 손실 누적) |

**핵심 통찰**: 같은 -10% 하락이라도, *거시(매크로)가 건강하면 조정*이고, *거시가 무너지고 있으면 침체의 시작*입니다. 가격만 봐서는 절대 구분할 수 없습니다. 그래서 ARDS-X 는 **거시 축과 가격 축을 함께** 봅니다.

---

## 3. 2-축 레짐 맵 (핵심 설계)

```
가격
스트레스
 (Y)
  ▲
높음│   조정/딥          하락 · 분배
    │ (추세 유지, 약세)  (추세 붕괴, 매크로는 아직)
    │                    → 리스크 축소
    │─────────────────┼─────────────────
    │   단기 과매도        침체 리밸런싱
    │ (반등 후보)        (매크로가 하락을 주도)
낮음│ → 전술 매수         → ARDS 방어 전환
    └─────────────────┴─────────────────▶
      낮음                     높음   거시 침체 Composite (X)
```

- **X축 = 거시 침체축**: ARDS 의 5-Factor Recession Composite (0~100). *"이 하락이 매크로 때문인가?"*
- **Y축 = 가격 스트레스축**: 드로다운 깊이 + 추세 붕괴 정도 (0~100). *"테이프가 얼마나 망가졌나?"*
- **오버레이 = 단기 과매도**: RSI(14) · Bollinger %B · 20일선 ATR 이탈. *"단기 반등 여지가 있나?"*

---

## 4. 분류 로직 (5 State)

판정은 **우선순위 순서**로 적용됩니다 (위에서부터 먼저 맞으면 확정).

| # | 상태 | 트리거 조건 | 행동 | 핸드오프 |
|---|---|---|---|---|
| 1 | **자산 리밸런싱 (침체)** `RECESSION_REBALANCE` | 거시 Composite ≥ 55 **AND** (지수 드로다운 ≤ -5% **또는** 추세 붕괴) | 방어 전환·자본보존 | **→ ARDS / ARDS-Defense** |
| 2 | **하락 / 분배** `DOWNTREND_DISTRIBUTION` | 추세 붕괴(200일선 이탈·데드크로스·폭 약화) **AND** 드로다운 ≤ -12%, 거시는 아직 < 55 | 리스크 축소·헤지, 저점매수 보류 | (거시 55 돌파 시 침체로 격상) |
| 3 | **단기 과매도** `OVERSOLD_BOUNCE` | 과매도 점수 높음 **AND** 추세 대체로 유지 | 전술·소규모 분할매수 + 타이트 손절 | **→ AMQS DIP_BUY** |
| 4 | **조정** `CORRECTION` | 드로다운 -5%~-12%, 추세 유지, 거시 양호 | 보유 + 우량 분할매수 | (RSI 과매도 시 ③ 으로) |
| 5 | **정상 상승추세** `UPTREND_HEALTHY` | 드로다운 < -5%, 200일선 위, 거시 양호 | 리스크온 유지 | **→ AMQS 모멘텀** |

> **설계 철학**: ARDS-X 는 *단독으로 매매하지 않습니다.* 이 모듈의 역할은 **"지금 어떤 전략 책(book)을 펴야 하는가"를 판정하는 스위치**입니다 — 조정/과매도면 모멘텀(AMQS), 침체면 방어(ARDS).

---

## 5. 5-Factor Recession Composite — 실데이터판

ARDS 원본과 **동일한 가중치**, 그러나 **실데이터로 계산**합니다. 각 성분은 0~100 정규화 후 가중합.

| 성분 | 가중치 | 1차 소스 (실데이터) | 폴백 (시장 프록시) |
|---|---|---|---|
| **A. 수익률 곡선** | 30% | FRED `T10Y3M`, `T10Y2Y` | yfinance `^TNX-^IRX` (10Y-3M), `^TNX-^FVX` |
| **B. Sahm Rule** | 25% | FRED `UNRATE` (3M MA − 12M 최저) | — (FRED 전용) |
| **C. ISM 프록시** | 15% | 구리/금 `CPER/GLD` + 산업재 `XLI/SPY` 상대강도 | (항상 시장 프록시) |
| **D. LEI 프록시** | 15% | FRED `ICSA`(신규청구) + `PERMIT`(주택허가) | — (FRED 전용) |
| **E. 신용/금융** | 15% | FRED `BAMLH0A0HYM2`(HY OAS) + `NFCI` | yfinance `HYG/IEF` 상대강도 + HYG 드로다운 |

**결측 처리**: 특정 성분 데이터가 없으면 해당 가중치를 빼고 **재정규화**합니다. 대시보드는 각 성분이 `실데이터(live)` / `프록시(proxy)` / `결측(missing)` 인지 라벨로 표시하고, 결측이 2개 이상이면 **신뢰도를 하향**합니다. *조용히 가짜 숫자를 만들지 않습니다.*

> **설계 의의**: 핵심 팩터인 **수익률 곡선(30%)과 신용(15%) = 45%** 는 yfinance 만으로도 계산되므로, FRED 가 다운되어도 시스템은 작동합니다. 노동(Sahm)·선행지수는 FRED 전용이라 best-effort 입니다.

---

## 6. 가격구조 지표 (Technical Layer)

각 종목·지수에 대해 계산:

- **드로다운**: 52주 고점 대비 하락폭 — *"얼마나 빠졌나"*
- **추세 무결성**: 50/200일선 위치, 골든/데드크로스, 200일선 21일 기울기 — *"추세가 깨졌나"*
- **과매도**: RSI(14), Bollinger %B, 20일선 ATR 이탈 배수, 연속 음봉 — *"반등 여지"*
- **폭(Breadth)**: 복합체 종목 중 200일선 위 비중(%) — *"소수만 버티나, 다같이 무너지나"*
- **모멘텀**: 6개월 수익률

여기서 두 합성점수가 나옵니다:
- **하락 점수(Decline Score, 0~100)**: 드로다운 깊이 + 200일선 이탈 + 데드크로스 + 하락 기울기 + 음의 모멘텀
- **과매도 점수(Oversold Score, 0~100)**: RSI + 볼린저 하단 + ATR 이탈 + 연속 음봉

---

## 6.5 백테스트 검증 (2014–2026, ^NDX 2,914 거래일)

`quant/backtest.py` 는 과거 매 거래일에 ARDS-X 가 내렸을 분류를 **룩어헤드 없이** 재현하고, 그 분류가 맞았는지를 *향후 수익률*로 검증합니다. (거시 축은 역사적 FRED 가 없어 시장 프록시 60%만 사용 — 실시간판보다 거시 정밀도는 낮습니다.)

### (a) 상태별 향후 수익률 — 가설: 조정/과매도는 +, 하락/침체는 −

| 상태 | 비중(시간) | 향후 20일 | 향후 60일 | 60일 승률 | 판정 |
|---|---|---|---|---|---|
| 정상 상승 | 66.7% | +1.05% | +3.02% | 71.0% | ✅ |
| **조정** | 12.4% | +2.19% | **+5.24%** | 77.5% | ✅ 저점매수 유효 |
| **단기 과매도** | 1.5% | +1.60% | **+5.64%** | 76.7% | ✅ 반등 유효 |
| **하락 / 분배** | 5.3% | +0.01% | **−0.37%** | 44.5% | ✅ 경계 정당 |
| 침체 리밸런싱 | 14.2% | +3.54% | **+11.22%** | 87.4% | ⚠️ **역신호** |

> **핵심 발견 (정직하게)**: 조정·과매도·하락 분류는 가설대로 작동했습니다 — *조정/과매도 구간의 60일 수익률이 +5%대, 하락 구간은 마이너스*. 그러나 **`침체 리밸런싱` 은 오히려 향후 수익률이 가장 높았습니다(+11%)**. 이는 *시장 프록시만으로 만든 거시 축이 2022–24 수익률 곡선 역전 내내 침체를 과다 발화(BEAR_TRAP)* 했기 때문입니다. **이것이 바로 실시간판이 FRED 의 Sahm Rule·LEI(실데이터)를 쓰고, 결측 시 신뢰도를 낮추는 이유**입니다 — 진짜 침체와 "곡선 역전만 된 무착륙"을 가르는 건 노동·선행지표이기 때문입니다.

### (b) 레짐 스위치 전략 vs Buy & Hold (^NDX)

risk-on{상승·조정·과매도} = NDX 롱, 방어{하락·침체} = 현금 (익일 적용):

| | 총수익 | CAGR | 변동성 | Sharpe | MDD | 시장노출 |
|---|---|---|---|---|---|---|
| Buy & Hold | +594.5% | 18.3% | 22.0% | 0.87 | −35.6% | 100% |
| **ARDS-X 스위치** | +190.5% | 9.7% | 15.6% | 0.67 | **−25.6%** | 80% |

> **해석**: 2014–2026 은 역사적 강세장이라 방어 오버레이는 *수익을 깎는 대신(−)* MDD 를 −35.6%→−25.6% 로 낮췄습니다. 이는 *"강세장에서 방어는 세금"* 이라는 철학과 정확히 일치합니다. ARDS-X 는 **단독 알파 도구가 아니라 레짐 스위치**이므로, 이 결과는 "방어 비용"의 크기를 보여주는 참고치이지 전략 수익률이 아닙니다.

실행: `python backtest.py` → `backtest_state_stats.csv`, `backtest_equity.csv` 생성.

---

## 7. 분석 유니버스

```
┌─ 지수 (분류 대상)
│   ^GSPC (S&P 500) · ^NDX (Nasdaq-100)
│
├─ 빅테크 / Mega-cap
│   AAPL · MSFT · GOOGL · AMZN · META · NVDA · TSLA
│
├─ AI 반도체 / 네트워킹
│   AVGO · AMD · TSM · MU · ASML
│
└─ AI 인프라 (전력·냉각·데이터센터·DB)
    VRT · SMCI · ANET · DELL · ORCL · CEG
```

거시 시장 프록시(보이지 않는 입력): `^TNX ^IRX ^FVX HYG LQD IEF CPER GLD XLI SPY`

---

## 8. 사용법

### 8.1 퀀트 실행 (데이터 생성)

```bash
cd quant
pip install -r requirements.txt          # yfinance, pandas, numpy
python run.py                            # → ../dashboard/data/latest.json 생성
python run.py --print                    # 콘솔에 전체 JSON 도 출력
python run.py --out /tmp/snapshot.json   # 출력 경로 지정
```

- 데이터는 **전부 무료** (yfinance + FRED 무료 CSV, **API 키 불필요**).
- 네트워크가 막히면 `quant/data/cache/` 캐시로 폴백합니다.
- FRED 서버가 느리거나 다운(504)이어도 **빠르게 실패**하고 시장 프록시로 계속 진행합니다.

### 8.2 대시보드 보기

```bash
cd dashboard
python3 -m http.server 8080
# 브라우저에서 http://localhost:8080  (정적 파일이라 어떤 서버든 OK)
```

대시보드는 `data/latest.json` 을 읽어:
- 최종 레짐 판정 + 행동/핸드오프
- 2-축 레짐 맵 (현재 위치 점)
- 5-Factor 거시 분해 (실데이터/프록시/결측 라벨)
- 지수·복합체 테이블 (드로다운·추세·RSI·하락/과매도 점수)
- 그룹별(빅테크/AI반도체/AI인프라) 집계

를 보여줍니다.

### 8.3 자동화 (선택)

```bash
# 매 영업일 장 마감 후 갱신 (cron 예시)
0 6 * * 2-6  cd /path/to/quant && /usr/bin/python3 run.py
```

---

## 9. 리포지토리 구조

```
ARDS — Adaptive Recession-Defensive Strategy for AI_QQQ/   (= ARDS-X)
├── README.md                ← 본 문서 (설명 + 철학)
├── README_EN.md             ← English
├── llms.txt                 ← LLM 에이전트용 요약
├── prompts/                 ← LLM 교차검증용 프롬프트 (코드와 동일 로직)
│   ├── ARDS-X_kr.MD         ← 한국어
│   ├── ARDS-X_en.MD         ← English
│   └── ARDS-X_cn.MD         ← 中文
├── quant/
│   ├── config.py            ← 유니버스·가중치·임계값
│   ├── datafeed.py          ← yfinance + FRED 무료 CSV (캐시·폴백)
│   ├── macro.py             ← 5-Factor Recession Composite (실데이터)
│   ├── technical.py         ← 드로다운·추세·과매도·폭 지표
│   ├── classifier.py        ← 2-축 레짐 분류 엔진 (핵심)
│   ├── run.py               ← 파이프라인 → latest.json
│   ├── backtest.py          ← 과거 레짐 분류 검증 (룩어헤드 없음)
│   ├── backtest_state_stats.csv   ← 상태별 향후 수익률
│   ├── backtest_equity.csv        ← 일별 NAV (스위치 vs Buy&Hold)
│   └── requirements.txt
└── dashboard/
    ├── index.html · styles.css · app.js · serve.py
    └── data/latest.json     ← 엔진이 생성 (샘플 포함)
```

---

## 10. ARDS 계보 & 자매 전략

| 전략 | 역할 | 입력 | 본 모듈과의 관계 |
|---|---|---|---|
| **AMQS** (Momentum) | 강세장 알파 | 4-Factor Momentum | ARDS-X 가 *조정/과매도/상승* 판정 시 핸드오프 |
| **ARDS** (Defensive) | 침체 헤지 | 5-Factor Recession (LLM 추정) | ARDS-X 의 거시 축이 **실데이터판** |
| **ARDS-Defense** | 방어 심화 | — | 침체 판정 시 방어 포트폴리오 |
| **ARDS-X** (본 모듈) | **레짐 스위치** | 실데이터 거시 + 가격구조 | *"어떤 책을 펼지"* 판정 |

> ARDS-X 는 ARDS 가 던진 질문 — *"지금이 침체 경고 구간인가?"* — 을 **LLM 추정이 아니라 실데이터로** 다시 답하고, 거기에 *"그렇다면 이 하락은 조정인가 침체인가?"* 라는 가격구조 질문을 더한 확장입니다.

---

## 11. 한계와 면책

- **레짐 분류는 후행/동행 지표 기반**입니다. 전환점을 정확히 예측하지 못하며, 급변장에서는 늦을 수 있습니다.
- **임계값(55점, -12% 등)은 휴리스틱**입니다. 시장 국면에 따라 보정이 필요합니다. `config.py` 에서 조정하세요.
- **시장 프록시(구리/금, HYG/IEF)는 진짜 ISM/HY OAS 가 아닙니다.** FRED 실데이터가 더 정확하므로, 가능하면 FRED 가 살아있을 때 캐시를 채워두세요.
- **BEAR_TRAP 위험**: 2022–23 처럼 수익률 곡선이 역전돼도 18개월 무착륙(no-landing)이 이어질 수 있습니다. 거시 신호가 항상 옳지 않습니다.
- 본 자료는 **교육·연구용 시뮬레이션**이며 투자 권유가 아닙니다. 모든 판단과 책임은 투자자 본인에게 있습니다.

---

## 12. 인용

```bibtex
@misc{kim2026ardsx,
  author       = {Kim, HoKwang (Dennis)},
  title        = {ARDS-X: A Real-Data Regime Classifier for Distinguishing
                  Correction, Oversold, Downtrend, and Recession-Driven
                  Rebalancing in US Big-Tech / AI Infrastructure},
  year         = {2026}, month = {June}, publisher = {GitHub},
  journal      = {vibe-investing series},
  howpublished = {\url{https://github.com/gameworkerkim/vibe-investing}},
  note         = {ORCID: 0009-0002-0962-2175}
}
```

---

> *"In a bull market, defense is a tax. In a bear market, defense is oxygen. ARDS-X is the barometer that tells you which one the air is."*

**라이선스**: MIT · **최종 수정**: 2026-06-06
