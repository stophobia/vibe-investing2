"""
vwap_confluence_backtest.py  -- VWAP 컨플루언스 백테스트 엔진 (a)
=================================================================
거래량을 '승인 게이트'로 두고 VWAP / Bollinger / RSI / MACD / EMA 를
서로 다른 직무로 결합한 추세추종(+선택적 평균회귀 청산) 전략의
백테스트 가능한 구현체.

지표별 직무
  - EMA(trend)   : 레짐 필터 (롱만/숏만 결정)
  - VWAP + band  : intraday 공정가치, 진입 위치 & 통계적 과열 청산
  - Bollinger    : 변동성 상태 (squeeze->expansion 확인)
  - Volume(RVOL) : 신호 승인/기각 (최종 게이트)  <-- volume_normalization 모듈
  - RSI          : 모멘텀 극단 / 다이버전스
  - MACD hist    : 진입 타이밍 (음->양 전환)

의존: numpy, pandas, volume_normalization.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from volume_normalization import VolumeNormalizer


# ====================================================================== #
# 설정 (모든 파라미터를 한 곳에서 관리 -> 문서 (b)의 표와 1:1 대응)
# ====================================================================== #
@dataclass
class StrategyConfig:
    market_type: str = "stock"          # "stock" | "crypto"
    # --- 추세 레짐 ---
    trend_ema: int = 200
    # --- VWAP ---
    vwap_session_reset: bool = True     # 주식 True(일 리셋) / 크립토 False
    vwap_rolling_window: int = 0        # crypto rolling VWAP 봉수 (0이면 anchored)
    vwap_band_k_entry: float = 1.0      # 눌림 매수 기준 -k*sigma
    vwap_band_k_exit: float = 2.0       # 과열 익절 기준 +k*sigma
    # --- Bollinger ---
    bb_period: int = 20
    bb_k: float = 2.0
    bb_squeeze_pctl: float = 0.25       # 밴드폭이 하위 25%면 squeeze
    # --- RSI ---
    rsi_period: int = 14
    rsi_long_floor: float = 50.0        # 롱 진입 시 RSI 상향 돌파 기준
    rsi_overbought: float = 70.0
    # --- MACD ---
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    trigger_window: int = 3             # 모멘텀 트리거가 최근 N봉 내 발생하면 유효
    # --- 거래량 승인 게이트 ---
    rvol_lookback: int = 20
    rvol_min: float = 1.5               # RVOL >= 1.5 면 거래량 팽창 승인
    vol_z_min: float = 1.0              # 보조: Z-score 기준
    # --- 리스크/포지션 ---
    risk_per_trade: float = 0.01        # 1회 트레이드 위험 = 자본의 1%
    stop_atr_mult: float = 2.0
    atr_period: int = 14
    partial_take_frac: float = 0.5      # +k*sigma 도달 시 부분 익절 비율
    allow_short: bool = False
    # --- 비용 ---
    fee_bps: float = 5.0                # 편도 수수료 (basis points)
    slippage_bps: float = 5.0


# ====================================================================== #
# 지표 계산 함수
# ====================================================================== #
def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi_wilder(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def macd_hist(close: pd.Series, fast: int, slow: int, signal: int) -> pd.Series:
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    return macd_line - signal_line


def bollinger(close: pd.Series, n: int, k: float):
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    upper, lower = mid + k * sd, mid - k * sd
    width = (upper - lower) / mid
    return mid, upper, lower, width


def atr(df: pd.DataFrame, n: int) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def vwap_with_bands(df: pd.DataFrame, cfg: StrategyConfig):
    """VWAP 및 거래량가중 표준편차 밴드.

    주식: 일자(session) 단위로 누적 리셋.
    크립토: rolling_window>0 이면 rolling VWAP, 아니면 전체 anchored.
    """
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"]

    if cfg.vwap_session_reset and isinstance(df.index, pd.DatetimeIndex):
        grp = df.index.normalize()  # 날짜별 그룹
        cum_pv = pv.groupby(grp).cumsum()
        cum_v = df["volume"].groupby(grp).cumsum()
        vwap = cum_pv / cum_v
        cum_pv2 = (tp.pow(2) * df["volume"]).groupby(grp).cumsum()
        var = cum_pv2 / cum_v - vwap.pow(2)
    elif cfg.vwap_rolling_window and cfg.vwap_rolling_window > 0:
        w = cfg.vwap_rolling_window
        cum_v = df["volume"].rolling(w).sum()
        vwap = pv.rolling(w).sum() / cum_v
        var = (tp.pow(2) * df["volume"]).rolling(w).sum() / cum_v - vwap.pow(2)
    else:  # anchored (전체 누적)
        cum_v = df["volume"].cumsum()
        vwap = pv.cumsum() / cum_v
        var = (tp.pow(2) * df["volume"]).cumsum() / cum_v - vwap.pow(2)

    sigma = np.sqrt(var.clip(lower=0))
    return vwap, sigma


# ====================================================================== #
# 시그널 생성
# ====================================================================== #
def build_signals(df: pd.DataFrame, cfg: StrategyConfig) -> pd.DataFrame:
    d = df.copy()
    norm = VolumeNormalizer(cfg.market_type, cfg.rvol_lookback)
    d = norm.normalize(d, seasonal=False)

    d["ema_trend"] = ema(d["close"], cfg.trend_ema)
    d["rsi"] = rsi_wilder(d["close"], cfg.rsi_period)
    d["macd_h"] = macd_hist(d["close"], cfg.macd_fast, cfg.macd_slow, cfg.macd_signal)
    _, _, _, d["bb_width"] = bollinger(d["close"], cfg.bb_period, cfg.bb_k)
    d["vwap"], d["vwap_sigma"] = vwap_with_bands(d, cfg)
    d["atr"] = atr(d, cfg.atr_period)

    # squeeze: 밴드폭이 과거 분포 하위 분위면 응축
    d["bb_squeeze"] = d["bb_width"] <= d["bb_width"].rolling(120, min_periods=20).quantile(
        cfg.bb_squeeze_pctl
    )
    bb_expanding = d["bb_width"] > d["bb_width"].shift(1)

    above_trend = d["close"] > d["ema_trend"]
    below_trend = d["close"] < d["ema_trend"]
    near_lower_band = d["close"] <= d["vwap"] - cfg.vwap_band_k_entry * d["vwap_sigma"]
    near_upper_band = d["close"] >= d["vwap"] + cfg.vwap_band_k_entry * d["vwap_sigma"]
    # 기관 평균단가(VWAP)의 방향 = 매수/매도측 control. 눌림 진입의 추세 필터로 사용.
    vwap_rising = d["vwap"] > d["vwap"].shift(3)
    vwap_falling = d["vwap"] < d["vwap"].shift(3)

    # 거래량 승인 게이트 (핵심): RVOL 또는 Z-score 충족 + wash 신뢰
    vol_ok = (
        ((d["rvol"] >= cfg.rvol_min) | (d["vol_z"] >= cfg.vol_z_min))
        & d["vol_trustworthy"]
    )

    rsi_cross_up = (d["rsi"] > cfg.rsi_long_floor) & (d["rsi"].shift(1) <= cfg.rsi_long_floor)
    rsi_cross_dn = (d["rsi"] < (100 - cfg.rsi_long_floor)) & (
        d["rsi"].shift(1) >= (100 - cfg.rsi_long_floor)
    )
    macd_turn_up = (d["macd_h"] > 0) & (d["macd_h"].shift(1) <= 0)
    macd_turn_dn = (d["macd_h"] < 0) & (d["macd_h"].shift(1) >= 0)
    # 정확히 같은 봉이 아니라 '최근 trigger_window 봉 내' 발생을 유효 트리거로 본다
    w = cfg.trigger_window
    momo_up = (rsi_cross_up | macd_turn_up).rolling(w, min_periods=1).max().astype(bool)
    momo_dn = (rsi_cross_dn | macd_turn_dn).rolling(w, min_periods=1).max().astype(bool)

    # 롱 진입: 레짐(상승, EMA 위) + VWAP 상승 + 가격이 VWAP -1sigma로 눌림
    #          + 변동성 확장 + 거래량 승인 + (RSI 상향 OR MACD 음->양)
    d["long_entry"] = (
        above_trend & vwap_rising & near_lower_band
        & (bb_expanding | ~d["bb_squeeze"])
        & vol_ok
        & momo_up
    )

    if cfg.allow_short:
        d["short_entry"] = (
            below_trend & vwap_falling & near_upper_band
            & (bb_expanding | ~d["bb_squeeze"])
            & vol_ok
            & momo_dn
        )
    else:
        d["short_entry"] = False

    return d


# ====================================================================== #
# 백테스트 루프 (이벤트 기반, 단일 포지션)
# ====================================================================== #
def backtest(df: pd.DataFrame, cfg: StrategyConfig, init_cash: float = 100_000.0) -> dict:
    d = build_signals(df, cfg)
    cost = (cfg.fee_bps + cfg.slippage_bps) / 10_000.0

    cash = init_cash
    qty = 0.0
    side = 0          # +1 long, -1 short, 0 flat
    entry = stop = 0.0
    took_partial = False
    equity_curve, trades = [], []

    rows = d.itertuples()
    for r in rows:
        price = r.close
        sig = r.vwap_sigma if not np.isnan(r.vwap_sigma) else 0.0

        # ---- 보유 중 청산 판단 ----
        if side == 1:
            take = r.vwap + cfg.vwap_band_k_exit * sig
            exit_flag, reason = False, ""
            if price <= stop:
                exit_flag, reason = True, "stop"
            elif (price < r.vwap) and (r.rvol >= cfg.rvol_min):
                exit_flag, reason = True, "vwap_break"
            elif (not took_partial) and price >= take:
                # 부분 익절
                sell_q = qty * cfg.partial_take_frac
                cash += sell_q * price * (1 - cost)
                qty -= sell_q
                took_partial = True
                trades.append(("partial_exit", r.Index, price))
            if exit_flag:
                cash += qty * price * (1 - cost)
                trades.append((reason, r.Index, price))
                qty, side, took_partial = 0.0, 0, False

        elif side == -1:
            take = r.vwap - cfg.vwap_band_k_exit * sig
            exit_flag, reason = False, ""
            if price >= stop:
                exit_flag, reason = True, "stop"
            elif (price > r.vwap) and (r.rvol >= cfg.rvol_min):
                exit_flag, reason = True, "vwap_break"
            elif (not took_partial) and price <= take:
                buy_q = qty * cfg.partial_take_frac
                cash -= buy_q * price * (1 + cost)
                qty -= buy_q
                took_partial = True
                trades.append(("partial_cover", r.Index, price))
            if exit_flag:
                cash -= qty * price * (1 + cost)  # 숏 커버
                trades.append((reason, r.Index, price))
                qty, side, took_partial = 0.0, 0, False

        # ---- 진입 판단 (플랫일 때만) ----
        if side == 0 and not np.isnan(r.atr) and r.atr > 0:
            if r.long_entry:
                stop = price - cfg.stop_atr_mult * r.atr
                risk_per_unit = price - stop
                qty = (init_cash * cfg.risk_per_trade) / max(risk_per_unit, 1e-9)
                cash -= qty * price * (1 + cost)
                side, entry, took_partial = 1, price, False
                trades.append(("long_entry", r.Index, price))
            elif r.short_entry:
                stop = price + cfg.stop_atr_mult * r.atr
                risk_per_unit = stop - price
                qty = (init_cash * cfg.risk_per_trade) / max(risk_per_unit, 1e-9)
                cash += qty * price * (1 - cost)
                side, entry, took_partial = -1, price, False
                trades.append(("short_entry", r.Index, price))

        # ---- 평가자산 ----
        mtm = qty * price if side == 1 else (-qty * price if side == -1 else 0.0)
        equity_curve.append((r.Index, cash + mtm))

    eq = pd.Series(dict(equity_curve))
    return _metrics(eq, trades, cfg)


def _metrics(eq: pd.Series, trades: list, cfg: StrategyConfig) -> dict:
    ret = eq.pct_change().dropna()
    total_return = eq.iloc[-1] / eq.iloc[0] - 1 if len(eq) else 0.0
    # 봉 주기 추정 -> 연율화 계수
    ann = 252 if cfg.market_type == "stock" else 365
    if isinstance(eq.index, pd.DatetimeIndex) and len(eq) > 1:
        per_day = pd.Series(1, index=eq.index).resample("1D").sum().mean()
        ann_factor = np.sqrt(ann * max(per_day, 1))
    else:
        ann_factor = np.sqrt(ann)
    sharpe = (ret.mean() / ret.std(ddof=0) * ann_factor) if ret.std(ddof=0) > 0 else 0.0
    cummax = eq.cummax()
    max_dd = ((eq - cummax) / cummax).min()
    entries = [t for t in trades if "entry" in t[0]]
    return {
        "total_return": round(float(total_return), 4),
        "sharpe": round(float(sharpe), 3),
        "max_drawdown": round(float(max_dd), 4),
        "n_trades": len(entries),
        "final_equity": round(float(eq.iloc[-1]), 2) if len(eq) else 0.0,
        "equity": eq,
        "trades": trades,
    }


# ====================================================================== #
# 데모: 합성 데이터로 동작 확인
# ====================================================================== #
def _synthetic_ohlcv(n: int = 2000, seed: int = 7, freq: str = "1h") -> pd.DataFrame:
    """추세 + 주기적 눌림 + (눌림 반등 시 거래량 팽창) 구조를 가진 합성 OHLCV.

    실제 시장의 핵심 미시구조(반등 지점에서 매수 거래량 유입)를 반영해야
    거래량 승인 전략이 의미 있게 동작한다.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=n, freq=freq)
    # 완만한 상승 추세 + 사이클성 눌림
    trend = np.linspace(0, 0.9, n)
    cycle = 0.12 * np.sin(np.linspace(0, 24 * np.pi, n))
    noise = rng.normal(0, 0.012, n).cumsum()
    log_close = np.log(100) + trend + cycle + noise
    close = np.exp(log_close)

    ret = np.diff(log_close, prepend=log_close[0])
    # 기저 거래량(로그정규) + 큰 변동(반등/급락) 시 거래량 스파이크
    base_vol = rng.lognormal(11, 0.4, n)
    spike = 1 + 6.0 * np.clip(np.abs(ret) / (np.std(ret) + 1e-9) - 0.5, 0, None)
    vol = base_vol * spike

    high = close * (1 + np.abs(rng.normal(0, 0.004, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.004, n)))
    return pd.DataFrame(
        {"high": high, "low": low, "close": close, "volume": vol,
         "trade_count": rng.integers(100, 2000, n)},
        index=idx,
    )


if __name__ == "__main__":
    data = _synthetic_ohlcv()
    for mt in ("stock", "crypto"):
        cfg = StrategyConfig(
            market_type=mt,
            vwap_session_reset=(mt == "stock"),
            vwap_rolling_window=(0 if mt == "stock" else 96),
            allow_short=(mt == "crypto"),
        )
        res = backtest(data, cfg)
        print(f"\n[{mt}]  trades={res['n_trades']}  "
              f"return={res['total_return']:.2%}  "
              f"sharpe={res['sharpe']}  maxDD={res['max_drawdown']:.2%}")
