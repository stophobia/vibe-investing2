# BNB-ETH 정량 분석 및 트레이딩 시그널

> **Binance Coin (BNB) 와 Ethereum (ETH) 의 4년치 통계 분석, MM/HODLer 가설 검증, 그리고 ETH 추세 기반 BNB 트레이딩 전략**

[![Language](https://img.shields.io/badge/Language-한국어-blue)](README.md)
[![English](https://img.shields.io/badge/Language-English-red)](README_EN.md)
[![Chinese](https://img.shields.io/badge/Language-中文-green)](README_CN.md)
[![Data](https://img.shields.io/badge/Data-CoinMetrics-orange)](https://coinmetrics.io/)
[![Period](https://img.shields.io/badge/Period-2022.05~2026.04-yellow)](#)

---

## 프로젝트 개요

본 프로젝트는 다음 핵심 가설들을 **통계적으로 검증**합니다:

1. ETH는 BNB를 가격 측면에서 선행하는가?
2. BNB는 ETH 추세 전환을 따라가는데, 상승과 하락의 추종 속도가 다른가?
3. Binance HODLer Airdrops 같은 BNB 보유자 우대 프로그램이 BNB 가격 구조를 변화시켰는가?
4. BNB체인에 상장되는 에어드롭 프로젝트는 BNB 가격과 무관하게 움직이는가?
5. 결과적으로 **BNB 홀더만 구조적으로 수혜**를 받는 구조인가?

이를 검증하기 위해 4년간(1,460일) 일별 가격 데이터로 정량 분석을 수행하고, 결과 기반의 트레이딩 시그널 프로그램을 제공합니다.

---

## 핵심 결론 (TL;DR)

| 지표 | 값 | 해석 |
|---|---|---|
| BNB-ETH Pearson 상관 | **0.7283** | 매우 강한 동시 움직임 |
| 최적 Lead-Lag | lag=0 | 일별 선행 관계 없음 |
| Granger 인과 (ETH→BNB, lag1) | p=0.2546 | 일별 인과 불유의 |
| ETH 골든크로스 → BNB 추종 | 중앙값 **6일** | 상승은 빨리 추종 |
| ETH 데드크로스 → BNB 추종 | 중앙값 **11일** | 하락은 1.8배 늦게 추종 |
| ETH 하락일 중 BNB가 덜 떨어진 비율 | **68.7%** | 하방 방어 강력한 증거 |
| HODLer 이전 BNB의 ETH 베타 | 0.643 | - |
| HODLer 이후 BNB의 ETH 베타 | **0.534** | **-16.9% 감소 (디커플링)** |

**가장 중요한 발견**: HODLer 에어드롭 본격화 이후 **상관계수는 그대로지만 베타만 감소**했습니다. 즉 같은 방향으로 움직이지만 같은 폭으로는 안 움직입니다 — 사용자 가설("MM/재단 USDT 매수 방어")의 정량적 흔적입니다.

---

## 사용자 가설 검증 결과

| # | 가설 | 결과 | 통계적 증거 |
|---|---|---|---|
| 1 | ETH가 BNB를 선행 | △ 부분 부합 | 일별 미관측, 추세 단위만 추종 |
| 2 | BNB는 추세 전환을 따라간다 (느리게) | ○ 부합 | 하락 11일 vs 상승 6일 |
| 3 | 하락 시 BNB가 ETH보다 덜 떨어진다 | ◎ **강하게 부합** | 68.7%의 ETH 하락일에서 BNB 하락폭 더 작음 |
| 4 | HODLer 이후 디커플링 진행 | ◎ **부합** | BNB의 ETH 베타 0.643 → 0.534 (-16.9%) |
| 5 | BNB와 BNB체인 상장 코인 가격은 무관 | ○ 정성적 부합 | NIGHT, BREV, ALLO 등 에어드롭 직후 즉시 매도 압력 |
| 6 | BNB 홀더만 구조적 이익 | ○ 부합 | 베타 감소 + 에어드롭 토큰 하락 동시 관측 |

**범례**: ◎ 강하게 부합 · ○ 부합 · △ 부분 부합 · × 부합 안함

---

## 윈도우별 누적 수익률 (2026-04-30 기준)

| 기간 | BNB | ETH | BTC |
|---|---|---|---|
| 24시간 | -0.38% | +0.11% | +0.67% |
| 72시간 | -1.78% | -1.80% | -1.24% |
| 7일 | -3.69% | -3.17% | -2.47% |
| 30일 | -0.25% | +7.38% | +11.85% |
| 90일 | -28.22% | -16.41% | -9.19% |
| 180일 | -43.81% | -41.72% | -30.64% |
| 365일 | +2.51% | +25.70% | -19.03% |
| **3년** | **+87.08%** | **+23.19%** | **+171.38%** |

> 단기적으로 BNB가 부진하지만 3년 누적으로는 ETH를 압도. 자체 수익 사이클(에어드롭/스테이킹) 효과로 해석됩니다.

---

## 트레이딩 전략 및 백테스트

### 전략 정의

```
진입 (LONG BNB):  ETH 20일 이동평균 > 50일 이동평균  (골든크로스)
청산 (CASH):       ETH 20일 이동평균 < 50일 이동평균  (데드크로스)
실행:              시그널 발생 다음 날 종가 매매
거래비용:          0.10% (왕복 0.20%)
```

### 백테스트 결과 (2022-05 ~ 2026-04, 1,461일)

| 전략 | 총수익 | CAGR | Sharpe | MDD | 변동성 |
|---|---|---|---|---|---|
| ETH MA Cross → BNB | **+123.21%** | 23.07% | 0.738 | -38.44% | 37.77% |
| BNB Buy & Hold | +211.85% | 34.18% | 0.818 | -55.49% | 53.24% |
| ETH Buy & Hold | +127.30% | 23.65% | 0.649 | -63.88% | 67.88% |

- 절대 수익은 BNB 단순 보유가 우수
- **변동성/MDD/Sharpe(ETH 대비)** 는 전략이 우수
- 시장 보유 시간 47.9% (절반은 현금), 총 14쌍 거래

### 현재 시그널 (2026-04-30)

```
BNB LONG 보유 중
ETH 추세    : UPTREND (MA20=$2,318 > MA50=$2,203)
BNB 가격    : $614.98
진입일자    : 2026-03-20 @ $642.11
현재 손익   : -4.23%
보유 일수   : 42일
```

---

## 사용법

### 의존성 설치

```bash
pip install pandas numpy yfinance ccxt scipy statsmodels
```

### 시그널 프로그램 실행

```bash
# 현재 시그널 출력
python bnb_signal.py

# 백테스트 실행 + CSV 저장
python bnb_signal.py --backtest

# 시그널 이력 CSV만 저장
python bnb_signal.py --csv-only

# 파라미터 변경
python bnb_signal.py --ma-short 10 --ma-long 30 --backtest

# 데이터 기간 조정
python bnb_signal.py --days 730 --backtest
```

### 데이터 소스 자동 Fallback

프로그램은 다음 순서로 시도합니다:

1. **yfinance** (Yahoo Finance, BNB-USD/ETH-USD)
2. **ccxt + Binance** (BNBUSDT/ETHUSDT spot)
3. **CoinGecko REST API** (최대 365일 한정)

---

## 산출물 파일 구성

| 파일 | 내용 |
|---|---|
| `BNB_ETH_분석보고서.docx` | 종합 분석 보고서 (한국어 DOCX) |
| `bnb_signal.py` | 독립 실행형 트레이딩 시그널 프로그램 |
| `00_summary.json` | 핵심 통계 요약 |
| `01_prices.csv` | BNB/ETH/BTC 일별 가격 (4년) |
| `02_returns.csv` | 일별 로그수익률 |
| `03_window_returns.csv` | 윈도우별 누적 수익률 |
| `04_yearly_correlation.csv` | 연도별 BNB-ETH 상관계수 |
| `05_rolling_corr_30d.csv` | 30일 롤링 상관계수 시계열 |
| `06_lead_lag.csv` | ±7일 시차 교차상관 |
| `07_granger_eth_to_bnb.csv` | Granger 인과성 검정 결과 |
| `08_trend_transition_delays.csv` | 추세 전환별 BNB 추종 일수 |
| `09_backtest_metrics.csv` | 백테스트 성과 지표 |
| `10_individual_trades.csv` | 개별 거래 내역 (15건) |
| `11_backtest_daily.csv` | 일별 백테스트 (포지션, 자산곡선) |
| `12_current_signal.json` | 현재 시그널 상태 |

---

## 분석 방법론

### 데이터 처리
- 일별 종가 기준 로그수익률
- 4년치 (1,460 거래일) 동일 기간 정렬
- 결측값 제거

### 통계 검정
- **Pearson / Spearman 상관계수** 및 30일/90일 롤링 상관
- **±7일 교차상관** 시차별 분석
- **Granger 인과성 검정** (5 lag, F-test)
- **추세 전환** MA(20/50) 골든/데드크로스 기반
- **비대칭 베타** OLS, ETH 부호별 회귀
- **z-test** (베타 차이 유의성)

### 백테스트
- Look-ahead bias 방지 (T+1 진입)
- 거래비용 0.10% per trade
- 누적 자산곡선, MDD, Sharpe Ratio 계산

---

## 한계 및 주의사항

- **표본 크기**: 4년 1,460일, 14쌍 거래로 표본 작음
- **MA 파라미터**: (20, 50) 표준값, 최적화 미실시 (과적합 회피)
- **HODLer 디커플링 진행 중**: ETH 시그널 유효성이 시간 갈수록 약해질 가능성
- **규제 리스크**: Binance/BNB는 글로벌 규제 변화에 직접 노출
- **본 자료는 투자 자문이 아니며**, 학술적 정량 분석 결과의 정리입니다

---

## 📚 참고 자료

- [CoinMetrics Reference Rate Methodology](https://coinmetrics.io/reference-rates/)
- [Binance HODLer Airdrops Program](https://www.binance.com/en/airdrop)
- [Binance Megadrop](https://www.binance.com/en/megadrop)
- BNB Chain 생태계 분석 보고서 (Binance Research, 2025)

---

## 라이선스 및 인용

본 분석 결과는 학술/연구 목적으로 자유롭게 인용 가능합니다. 인용 시 다음을 기재해 주십시오:

```
Kim, HoKwang. (2026). BNB-ETH 정량 분석 및 트레이딩 시그널.
 https://github.com/gameworkerkim
```

---

**작성**: Dennis Kim (김호광), CEO, Cyworld , Betalabs Inc.  
**문의**: gameworker@gmail.com  
**GitHub**: [github.com/gameworkerkim](https://github.com/gameworkerkim)
