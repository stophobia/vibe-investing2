#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turtle Trading vs. 다른 트레이딩 기법 — 3년 백테스트 비교 엔진
================================================================
대상: NVDA(단일), M7, AI 인프라 바스켓
전략:
  1) Buy & Hold              (벤치마크)
  2) Turtle (System 1)       돈키언 20일 돌파 진입 / 10일 이탈 청산 + ATR 2N 손절
  3) SMA 50/200 Golden Cross 추세추종 고전
  4) 200-day MA Trend Filter 시계열 모멘텀(가격 > 200일선일 때만 보유)
  5) VWAP Confluence         롤링 VWAP −1σ 눌림 + 거래량 승인 게이트(RVOL≥1.5)
                             + RSI/MACD 트리거, 청산: ATR 2N · VWAP 이탈 · +2σ 과열

방법론
  - yfinance auto_adjust(분할/배당 조정) 종가·고가·저가·거래량 사용
  - 신호는 t일 종가 기준 계산, 포지션은 t+1일부터 반영(룩어헤드 제거)
  - 단일자산은 in/out 이진 노출(보유 시 자산수익, 청산 시 현금 0%)로 공정 비교
  - 바스켓은 각 종목을 독립적으로 동일 전략 매매 후 동일비중 평균
  - 무위험수익률 0% 가정(샤프 = 평균/표준편차 * sqrt(252)), 거래비용 미반영(전 전략 공통)

VWAP 주의: 원전략은 intraday/단기 스윙용(일 세션 리셋 VWAP)이다.
본 비교는 일봉 스윙 적응판으로 rolling VWAP(20일)을 사용한다.
"""
import warnings
warnings.filterwarnings("ignore")
import os
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# 한글 폰트 (macOS AppleGothic), 없으면 기본
try:
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CHARTS = os.path.join(BASE, "charts")
os.makedirs(DATA, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

START_TRADE = "2023-06-01"   # 3년 백테스트 시작
END = "2026-06-04"
DL_START = "2022-06-01"      # 200일 워밍업 여유

M7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
AI_INFRA = ["NVDA", "AMD", "AVGO", "MRVL", "TSM", "MU", "ANET", "VRT", "SMCI", "PLTR", "DELL", "ORCL"]
ALL = sorted(set(M7 + AI_INFRA))

TRADING_DAYS = 252

# ----------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------
def load_data():
    print(f"[*] downloading {len(ALL)} tickers ...")
    raw = yf.download(ALL, start=DL_START, end=END, progress=False, auto_adjust=True)
    close = raw["Close"]
    high = raw["High"]
    low = raw["Low"]
    vol = raw["Volume"]
    close.to_csv(os.path.join(DATA, "prices_close.csv"))
    return close, high, low, vol

# ----------------------------------------------------------------------
# 지표
# ----------------------------------------------------------------------
def atr(high, low, close, n=20):
    prev_close = close.shift(1)
    tr = pd.concat([(high - low),
                    (high - prev_close).abs(),
                    (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi_wilder(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    ag = gain.ewm(alpha=1/n, adjust=False).mean()
    al = loss.ewm(alpha=1/n, adjust=False).mean()
    rs = ag / al.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def macd_hist(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line - sig

# ----------------------------------------------------------------------
# 전략별 '포지션' 시계열 생성 (0 또는 1).  신호는 당일, 노출은 다음날.
# ----------------------------------------------------------------------
def pos_buy_hold(close, high, low, volume=None):
    return pd.Series(1.0, index=close.index)

def pos_sma_cross(close, high, low, volume=None, fast=50, slow=200):
    sf = close.rolling(fast).mean()
    sl = close.rolling(slow).mean()
    return (sf > sl).astype(float)

def pos_ma_filter(close, high, low, volume=None, n=200):
    return (close > close.rolling(n).mean()).astype(float)

def pos_turtle(close, high, low, volume=None, entry_n=20, exit_n=10, atr_n=20, stop_mult=2.0):
    """System 1 롱온리: 20일 신고가 돌파 진입, 10일 신저가 이탈 또는 2N 손절 청산."""
    hi_entry = high.rolling(entry_n).max().shift(1)
    lo_exit = low.rolling(exit_n).min().shift(1)
    n_atr = atr(high, low, close, atr_n).shift(1)
    c, he, le, na = close.values, hi_entry.values, lo_exit.values, n_atr.values
    pos = np.zeros(len(c)); in_pos = False; stop = np.nan
    for i in range(len(c)):
        if not in_pos:
            if not np.isnan(he[i]) and c[i] > he[i] and not np.isnan(na[i]) and na[i] > 0:
                in_pos = True; stop = c[i] - stop_mult * na[i]
            pos[i] = 0.0
        else:
            if (not np.isnan(le[i]) and c[i] < le[i]) or c[i] < stop:
                in_pos = False; pos[i] = 0.0
            else:
                pos[i] = 1.0
    return pd.Series(pos, index=close.index)

def pos_vwap_confluence(close, high, low, volume=None,
                        trend_ema=200, vwap_win=20, k_entry=0.8, k_exit=2.5,
                        rvol_lookback=20, rvol_min=1.5, rsi_floor=50.0,
                        pullback_window=10, atr_n=14, stop_mult=2.0,
                        breakdown_k=0.5):
    """일봉 스윙 적응판 VWAP 컨플루언스 (롱온리).
    진입: 레짐(close>EMA200) & VWAP 상승 & [최근 pullback_window봉 내 VWAP-kσ 눌림 발생]
          & 당일 거래량 승인(RVOL>=rvol_min) & 당일 RSI 50상향 또는 MACD히스토 음→양 (반등 트리거).
      → '눌림(과거 N봉)' 과 '거래량 동반 반등 트리거(당일)'를 분리해 모순 제거.
    청산(택1): ATR 2N 손절 / 종가 < 롤링VWAP(추세 무효) / 종가 >= VWAP+kσ(과열 익절).
    """
    if volume is None:
        return pd.Series(0.0, index=close.index)
    tp = (high + low + close) / 3.0
    pv = (tp * volume).rolling(vwap_win).sum()
    vv = volume.rolling(vwap_win).sum()
    vwap = pv / vv                                   # 롤링 VWAP
    sigma = (close - vwap).rolling(vwap_win).std()   # VWAP 대비 분산
    ema_t = ema(close, trend_ema)
    rvol = volume / volume.rolling(rvol_lookback).mean()
    rsi = rsi_wilder(close, 14)
    mh = macd_hist(close)
    na = atr(high, low, close, atr_n)

    rsi_cross = (rsi > rsi_floor) & (rsi.shift(1) <= rsi_floor)
    macd_turn = (mh > 0) & (mh.shift(1) <= 0)
    trig = (rsi_cross | macd_turn)                    # 당일 반등 트리거
    # 최근 pullback_window봉 내 -kσ 눌림이 있었는가
    dip = (close <= (vwap - k_entry * sigma))
    dip_recent = dip.rolling(pullback_window).max().fillna(0).astype(bool)

    regime = close > ema_t
    vwap_up = vwap > vwap.shift(1)
    vol_ok = rvol >= rvol_min
    entry_sig = (regime & vwap_up & dip_recent & vol_ok & trig)

    c = close.values; vw = vwap.values; sg = sigma.values; nav = na.values
    es = entry_sig.values
    pos = np.zeros(len(c)); in_pos = False; stop = np.nan
    for i in range(len(c)):
        if not in_pos:
            if bool(es[i]) and not np.isnan(nav[i]) and nav[i] > 0:
                in_pos = True; stop = c[i] - stop_mult * nav[i]
            pos[i] = 0.0
        else:
            overheat = (not np.isnan(vw[i]) and not np.isnan(sg[i])
                        and c[i] >= vw[i] + k_exit * sg[i])
            breakdown = (not np.isnan(vw[i]) and not np.isnan(sg[i])
                         and c[i] < vw[i] - breakdown_k * sg[i])
            if c[i] < stop or breakdown or overheat:
                in_pos = False; pos[i] = 0.0
            else:
                pos[i] = 1.0
    return pd.Series(pos, index=close.index)

STRATS = {
    "Buy & Hold": pos_buy_hold,
    "Turtle (Donchian 20/10 + 2N stop)": pos_turtle,
    "SMA 50/200 Golden Cross": pos_sma_cross,
    "200-day MA Trend Filter": pos_ma_filter,
    "VWAP Confluence (vol gate)": pos_vwap_confluence,
}

# ----------------------------------------------------------------------
# 단일 종목 백테스트 → 일간 전략수익률 시계열
# ----------------------------------------------------------------------
def backtest_ticker(close_s, high_s, low_s, vol_s, strat_fn):
    df = pd.DataFrame({"close": close_s, "high": high_s, "low": low_s,
                       "vol": vol_s}).dropna()
    pos = strat_fn(df["close"], df["high"], df["low"], df["vol"])
    ret = df["close"].pct_change().fillna(0.0)
    pos_exec = pos.shift(1).fillna(0.0)
    strat_ret = pos_exec * ret
    mask = strat_ret.index >= pd.Timestamp(START_TRADE)
    return strat_ret[mask], pos_exec[mask], ret[mask]

# ----------------------------------------------------------------------
# 성과지표
# ----------------------------------------------------------------------
def metrics(daily_ret, pos_exec=None):
    eq = (1 + daily_ret).cumprod()
    n = len(daily_ret)
    if n == 0:
        return {}
    total = eq.iloc[-1] - 1
    cagr = eq.iloc[-1] ** (TRADING_DAYS / n) - 1
    vol = daily_ret.std() * np.sqrt(TRADING_DAYS)
    sharpe = (daily_ret.mean() / daily_ret.std() * np.sqrt(TRADING_DAYS)) if daily_ret.std() > 0 else 0
    dd = (eq / eq.cummax() - 1).min()
    trades = wins = np.nan; tim = np.nan
    if pos_exec is not None:
        tim = (pos_exec > 0).mean()
        entries = ((pos_exec > 0) & (pos_exec.shift(1).fillna(0) == 0))
        trade_idx = list(np.where(entries.values)[0])
        n_trades = len(trade_idx)
        win = 0; rv = daily_ret.values
        for k, s in enumerate(trade_idx):
            e = trade_idx[k+1] if k+1 < len(trade_idx) else len(rv)
            seg_ret = (1 + pd.Series(rv[s:e])).prod() - 1
            if seg_ret > 0:
                win += 1
        trades = n_trades
        wins = (win / n_trades * 100) if n_trades else np.nan
    return {
        "Total Return %": round(total * 100, 1),
        "CAGR %": round(cagr * 100, 1),
        "Vol %": round(vol * 100, 1),
        "Sharpe": round(sharpe, 2),
        "MaxDD %": round(dd * 100, 1),
        "Time in Mkt %": round(tim * 100, 1) if tim == tim else np.nan,
        "Trades": int(trades) if trades == trades else np.nan,
        "Win %": round(wins, 0) if wins == wins else np.nan,
    }

# ----------------------------------------------------------------------
# 그룹(바스켓) 백테스트
# ----------------------------------------------------------------------
def backtest_group(tickers, close, high, low, vol, strat_fn):
    rets, poss = [], []
    for t in tickers:
        if t not in close.columns:
            continue
        sr, pe, _ = backtest_ticker(close[t], high[t], low[t], vol[t], strat_fn)
        rets.append(sr.rename(t)); poss.append(pe.rename(t))
    R = pd.concat(rets, axis=1).fillna(0.0)
    P = pd.concat(poss, axis=1).fillna(0.0)
    return R.mean(axis=1), P.mean(axis=1)

# ----------------------------------------------------------------------
# 실행
# ----------------------------------------------------------------------
def run():
    close, high, low, vol = load_data()
    results, equity = {}, {}
    universes = {
        "NVDA (단일)": ["NVDA"],
        "M7": M7,
        "AI 인프라 (12종)": AI_INFRA,
    }
    for uname, tickers in universes.items():
        results[uname], equity[uname] = {}, {}
        for sname, fn in STRATS.items():
            if len(tickers) == 1:
                sr, pe, _ = backtest_ticker(close[tickers[0]], high[tickers[0]],
                                            low[tickers[0]], vol[tickers[0]], fn)
            else:
                sr, pe = backtest_group(tickers, close, high, low, vol, fn)
            results[uname][sname] = metrics(sr, pe)
            equity[uname][sname] = (1 + sr).cumprod()

    rows = []
    for uname in universes:
        for sname in STRATS:
            rows.append({"Universe": uname, "Strategy": sname, **results[uname][sname]})
    res_df = pd.DataFrame(rows)
    res_df.to_csv(os.path.join(DATA, "backtest_results.csv"), index=False)
    print("\n================ RESULTS ================")
    print(res_df.to_string(index=False))

    colors = {
        "Buy & Hold": "#888888",
        "Turtle (Donchian 20/10 + 2N stop)": "#C00000",
        "SMA 50/200 Golden Cross": "#1F77B4",
        "200-day MA Trend Filter": "#2CA02C",
        "VWAP Confluence (vol gate)": "#9467BD",
    }
    for uname in universes:
        plt.figure(figsize=(10, 5.2))
        for sname in STRATS:
            eq = equity[uname][sname]
            plt.plot(eq.index, eq.values, label=sname, color=colors[sname],
                     lw=2.0 if ("Turtle" in sname or "VWAP" in sname) else 1.4)
        plt.title(f"Turtle vs Others — {uname}  (2023-06 ~ 2026-06)")
        plt.ylabel("Growth of $1")
        plt.axhline(1.0, color="#cccccc", lw=0.8)
        plt.legend(fontsize=8, loc="upper left")
        plt.grid(alpha=0.25); plt.tight_layout()
        fn = os.path.join(CHARTS, f"equity_{uname.split()[0].replace('(','')}.png")
        plt.savefig(fn, dpi=130); plt.close()
        print("saved", fn)

    with open(os.path.join(DATA, "results_markdown.md"), "w") as f:
        for uname in universes:
            f.write(f"\n### {uname}\n\n")
            cols = ["Strategy", "Total Return %", "CAGR %", "Vol %", "Sharpe",
                    "MaxDD %", "Time in Mkt %", "Trades", "Win %"]
            f.write("| " + " | ".join(cols) + " |\n")
            f.write("|" + "|".join(["---"] * len(cols)) + "|\n")
            for sname in STRATS:
                m = results[uname][sname]
                f.write("| " + " | ".join([sname] + [str(m.get(c, "")) for c in cols[1:]]) + " |\n")
    print("\n[*] markdown table -> data/results_markdown.md")
    return res_df

if __name__ == "__main__":
    run()
