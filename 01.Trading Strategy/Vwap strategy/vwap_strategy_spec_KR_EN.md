# VWAP 컨플루언스 거래량 매매 전략 사양서 / VWAP Confluence Volume Strategy Specification

문서 버전 v1.0 · 대상 코드: `vwap_confluence_backtest.py`, `volume_normalization.py`

---

## 0. 설계 원칙 / Design Principle

**KR.** 가격에서 파생된 지표(BB, RSI, MACD, EMA)는 서로 강하게 상관되어 있어 "독립 확인표"로 취급하면 신뢰 과잉을 부른다. 따라서 각 지표에 **단 하나의 직무**만 배정하고, 가격 외부 정보인 **거래량을 최종 승인 게이트**로 둔다. 거래량 승인이 없으면 다른 모든 신호는 잠정 신호로만 취급한다.

**EN.** Price-derived indicators (BB, RSI, MACD, EMA) are mutually correlated; treating them as independent confirmations creates overconfidence. Each indicator is therefore assigned a **single role**, and **volume — the only non-price information — is the final approval gate**. Without volume approval, all other signals remain provisional.

---

## 1. 지표 직무 분담 / Indicator Role Assignment

| 지표 / Indicator | 직무 / Role | 답하는 질문 / Question answered |
|---|---|---|
| EMA(trend) | 추세 레짐 필터 / regime filter | 롱만? 숏만? / long-only or short-only? |
| VWAP + σ band | 공정가치·진입위치·과열청산 / fair value, entry, exit | 비싼가 싼가? / cheap or expensive? |
| Bollinger Bands | 변동성 상태 / volatility state | 응축인가 분출인가? / squeeze or expansion? |
| Volume (RVOL / Z) | 신호 승인 게이트 / approval gate | 믿어도 되는가? / is the move trustworthy? |
| RSI | 모멘텀 극단·다이버전스 / momentum extreme | 지쳤는가? / is the trend exhausted? |
| MACD histogram | 진입 타이밍 / entry timing | 지금인가? / is it time to act? |

---

## 2. 전체 파라미터 / Full Parameter Set

`StrategyConfig` 의 모든 필드와 1:1 대응한다. / Maps 1:1 to every field of `StrategyConfig`.

### 2.1 추세·VWAP / Trend & VWAP

| 파라미터 / Param | 기본값 / Default | 권장 범위 / Range | 설명 / Description |
|---|---|---|---|
| `trend_ema` | 200 | 100–250 | 레짐 판정용 EMA / regime EMA |
| `vwap_session_reset` | True (stock) | bool | 일 단위 세션 리셋 / daily session reset |
| `vwap_rolling_window` | 0 | 0 또는 48–192 | 0=anchored, >0=rolling VWAP 봉수 |
| `vwap_band_k_entry` | 1.0 | 0.5–1.5 | 눌림 매수 기준 −kσ / pullback entry band |
| `vwap_band_k_exit` | 2.0 | 1.5–3.0 | 과열 익절 기준 +kσ / overheat take-profit |

### 2.2 Bollinger / RSI / MACD

| 파라미터 / Param | 기본값 / Default | 권장 범위 / Range | 설명 / Description |
|---|---|---|---|
| `bb_period` | 20 | 14–30 | BB 이동평균 기간 |
| `bb_k` | 2.0 | 1.5–2.5 | BB 표준편차 배수 |
| `bb_squeeze_pctl` | 0.25 | 0.10–0.35 | 밴드폭 하위 분위 = squeeze |
| `rsi_period` | 14 | 9–21 | RSI 기간 (Wilder) |
| `rsi_long_floor` | 50.0 | 45–55 | 롱 트리거: RSI 상향 돌파선 |
| `rsi_overbought` | 70.0 | 65–80 | 과매수 참고선 |
| `macd_fast / slow / signal` | 12 / 26 / 9 | 표준 | MACD EMA 기간 |
| `trigger_window` | 3 | 2–5 | 모멘텀 트리거 유효 봉 수 / trigger lookback |

### 2.3 거래량 승인 게이트 / Volume Gate

| 파라미터 / Param | 기본값 / Default | 권장 범위 / Range | 설명 / Description |
|---|---|---|---|
| `rvol_lookback` | 20 | 14–50 | RVOL/Z-score 기준 봉 수 |
| `rvol_min` | 1.5 | 1.3–2.5 | 거래량 팽창 승인 배수 / RVOL approval |
| `vol_z_min` | 1.0 | 1.0–2.5 | 보조 Z-score 기준 |

### 2.4 리스크·비용 / Risk & Cost

| 파라미터 / Param | 기본값 / Default | 권장 범위 / Range | 설명 / Description |
|---|---|---|---|
| `risk_per_trade` | 0.01 | 0.005–0.02 | 1회 위험 = 자본 대비 비율 |
| `stop_atr_mult` | 2.0 | 1.5–3.0 | ATR 배수 손절폭 |
| `atr_period` | 14 | 10–20 | ATR 기간 |
| `partial_take_frac` | 0.5 | 0.3–0.7 | +kσ 도달 시 부분 익절 비율 |
| `allow_short` | False | bool | 숏 허용 여부 |
| `fee_bps` | 5.0 | 시장별 / per market | 편도 수수료 (bps) |
| `slippage_bps` | 5.0 | 시장별 / per market | 슬리피지 (bps) |

---

## 3. 진입·청산 규칙 / Entry & Exit Rules

### 3.1 롱 진입 (모두 충족) / Long Entry (all required)

1. 레짐 / Regime: `close > EMA(trend)`
2. 방향 / Direction: VWAP 상승 중 (`VWAP > VWAP[-3]`)
3. 위치 / Location: `close ≤ VWAP − k_entry·σ` (눌림 / pullback)
4. 변동성 / Volatility: BB 확장 중 또는 비-squeeze
5. **거래량 승인 / Volume gate: `(RVOL ≥ rvol_min OR Z ≥ vol_z_min) AND wash-신뢰`**
6. 타이밍 / Timing: 최근 `trigger_window` 봉 내 (RSI 50 상향 OR MACD 히스토그램 음→양)

> 5번이 빠지면 1–4·6이 충족되어도 진입하지 않는다. / Without (5), no entry even if (1–4, 6) hold.

### 3.2 숏 진입 / Short Entry (`allow_short=True`)

롱의 대칭: `close < EMA`, VWAP 하락, `close ≥ VWAP + k_entry·σ`, 거래량 승인, RSI 하향/MACD 양→음.

### 3.3 청산 / Exit

| 우선순위 / Priority | 조건 / Condition | 행동 / Action |
|---|---|---|
| 1 | 가격 ≤ 손절(`entry − stop_atr_mult·ATR`) | 전량 청산 / full exit |
| 2 | 가격이 VWAP 하향 이탈 + RVOL ≥ rvol_min | 전량 청산 (추세 무효) |
| 3 | 가격 ≥ VWAP + k_exit·σ (최초 1회) | 부분 익절 `partial_take_frac` |

---

## 4. 거래량 정규화 방법론 (c) / Volume Normalization Methodology (c)

### 4.1 시장별 차이 / Market Differences

| 항목 / Aspect | 주식 / Stock | 가상자산 / Crypto |
|---|---|---|
| 단위 / Unit | 주(shares) | 코인수량 또는 호가통화 금액 / coins or quote-ccy |
| 주기 / Cadence | 세션 기반, 장중 U자 계절성 | 24/7 연속, 요일·시간 계절성 |
| VWAP 리셋 / reset | 일 단위 / daily | 없음 → rolling/anchored |
| 데이터 품질 / quality | 거래소 보고 일관 | wash trading 오염 가능 |
| 비교가능성 / comparability | 종목 간 절대량 비교 곤란 | 거래소 간 분절 / fragmented |

### 4.2 정규화 파이프라인 / Normalization Pipeline

| 단계 / Step | 메서드 / Method | 목적 / Purpose |
|---|---|---|
| 금액 환산 / dollarize | `dollar_volume` | 자산 간 비교가능성 / cross-asset comparability |
| 자기기준 / self-relative | `relative_volume` (RVOL), `volume_zscore` | 레짐 무관 팽창 측정 / regime-free expansion |
| 계절성 제거 / deseasonalize | `seasonal_adjusted_rvol` | 주식=시간대 / 크립토=요일·시간 |
| 품질 필터 / quality | `washtrade_filter` (crypto) | 건당 거래량 극단치 의심 표시 |

**핵심 / Key.** 절대 거래량을 직접 임계값으로 쓰지 말 것. RVOL(배수) 또는 Z-score(통계적 이탈)로 정규화한 뒤 게이트에 투입한다. 로그 변환(`use_log=True`)으로 우측 꼬리(right-skew)를 완화한다.

### 4.3 시장별 권장 설정 / Recommended Settings by Market

| 파라미터 / Param | 주식 / Stock | 가상자산 / Crypto |
|---|---|---|
| `vwap_session_reset` | True | False |
| `vwap_rolling_window` | 0 (anchored daily) | 48–192 (rolling) |
| `rvol_lookback` | 20 (≈1개월 일봉) | 동일 시간단위 24–96 |
| `washtrade_filter` | 미적용 (자동 통과) | 적용 (`trade_count` 필요) |
| `fee_bps` / `slippage_bps` | 1–3 / 2–5 | 5–10 / 5–20 |
| 계절성 버킷 / seasonal bucket | 시간(HH:MM) | 요일+시간 |

---

## 5. 검증 프로토콜 / Validation Protocol

**KR.** 5개 지표 × 다수 파라미터 조합은 in-sample에서 거의 항상 좋아 보인다(과최적화). 반드시 아래를 따른다.

**EN.** Five indicators with many parameter combinations almost always look good in-sample (overfitting). Enforce the following.

1. **분할 / Split.** In-sample(IS) 60% / Out-of-sample(OOS) 40%. OOS 성과만 채택. / Adopt OOS results only.
2. **Walk-forward.** 슬라이딩 윈도우로 재최적화·재검증 반복. / Re-optimize and re-validate on rolling windows.
3. **거래비용 포함 / costs.** `fee_bps + slippage_bps` 항상 반영. / Always include.
4. **민감도 / sensitivity.** 파라미터를 ±1스텝 흔들어 성과 붕괴 여부 확인. 붕괴하면 과최적화. / Perturb ±1 step; collapse ⇒ overfit.
5. **다중자산 / multi-asset.** 단일 종목 성공은 우연일 수 있음. 여러 자산에서 견고성 확인.

---

## 6. 한계 / Limitations

| 한계 / Limitation | 내용 / Detail |
|---|---|
| 다중공선성 / multicollinearity | BB·RSI·MACD는 동일 가격의 변형 → 중복 확인 주의 |
| 시간 종속 / time dependency | intraday VWAP은 장마감 리셋 → 스윙엔 Anchored VWAP |
| 데이터 품질 / data quality | 크립토 wash trading은 거래량 신호를 오염 |
| 선택성 / selectivity | 고선택 컨플루언스는 트레이드 빈도가 낮음(설계상 정상) |
| 미래참조 금지 / no lookahead | 모든 신호는 종가 확정 후 다음 봉 진입 전제로 검증할 것 |

---

## 7. 실행 / Run

```bash
python3 vwap_confluence_backtest.py     # 합성 데이터 데모 / synthetic demo
```

```python
import pandas as pd
from vwap_confluence_backtest import StrategyConfig, backtest

df = pd.read_csv("ohlcv.csv", parse_dates=["timestamp"], index_col="timestamp")
# 필수 컬럼 / required: high, low, close, volume  (crypto 권장: trade_count)
cfg = StrategyConfig(market_type="crypto", vwap_session_reset=False,
                     vwap_rolling_window=96, allow_short=True)
result = backtest(df, cfg)
print(result["total_return"], result["sharpe"], result["max_drawdown"])
```
