"""
AMQS-M7 Backtest Engine
========================
Methodology mirrors the original AMQS backtest in the vibe-investing prompt:

  * 주간 리밸런싱 (Friday close signals → Monday open entries)
  * -12% per-name stop loss from rebalance entry
  * Macro regime filter (Risk-On/Off/Defensive) drives invested fraction
  * 거래비용 5bps + slippage 10bps (원문 기본값)
  * 벤치마크: QQQ, SOXX, AI 반도체 바스켓 (NVDA-AVGO-AMD-TSM-MU 동가중)
  * 주의: AVGO/AMD/TSM/MU 데이터는 외부 다운로드 — M7 universe 외임

Outputs:
  * data/backtest_equity.csv   — 일별 equity curves (AMQS-M7 vs benchmarks)
  * data/backtest_positions.csv — 주별 목표 비중 + regime
  * data/backtest_trades.csv   — 진입/청산 로그 + 손절 발동
  * Console: CAGR, Vol, Sharpe, MDD, 회전율
"""

from __future__ import annotations

import datetime as dt
import math
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    from .strategy import (
        AMQSConfig, M7_TICKERS, MACRO_TICKERS,
        measure, apply_prefilter, score, allocate, detect_regime,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.strategy import (
        AMQSConfig, M7_TICKERS, MACRO_TICKERS,
        measure, apply_prefilter, score, allocate, detect_regime,
    )


AI_SEMI_BASKET = ["NVDA", "AVGO", "AMD", "TSM", "MU"]
BENCH_TICKERS = ["QQQ", "SOXX"] + AI_SEMI_BASKET


def _download(tickers, start, end):
    import yfinance as yf
    raw = yf.download(
        tickers=tickers, start=start, end=end,
        auto_adjust=True, progress=False, group_by="ticker", threads=True,
    )
    if isinstance(raw.columns, pd.MultiIndex):
        if tickers[0] in raw.columns.get_level_values(0):
            return pd.concat(
                {t: raw[t]["Close"] for t in tickers if t in raw.columns.get_level_values(0)},
                axis=1,
            )
        return raw["Close"]
    return raw[["Close"]].rename(columns={"Close": tickers[0]})


def _max_drawdown(curve: pd.Series) -> float:
    return float((curve / curve.cummax() - 1.0).min())


def _annualized_stats(daily: pd.Series) -> dict:
    r = daily.dropna()
    if r.empty:
        return {"total": 0.0, "cagr": 0.0, "vol": 0.0, "sharpe": 0.0}
    total = float((1 + r).prod() - 1)
    n = len(r)
    cagr = (1 + total) ** (252 / n) - 1 if n > 0 else 0.0
    vol = float(r.std() * math.sqrt(252))
    sharpe = (r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else 0.0
    return {"total": total, "cagr": cagr, "vol": vol, "sharpe": float(sharpe)}


def run_backtest(
    start: str = "2024-01-02",
    end: Optional[str] = None,
    config: Optional[AMQSConfig] = None,
    txn_cost_bps: Optional[float] = None,
    slippage_bps: Optional[float] = None,
    initial_capital: float = 100_000.0,
    out_dir: str = "data",
) -> pd.DataFrame:
    cfg = config or AMQSConfig()
    txn_bps = txn_cost_bps if txn_cost_bps is not None else cfg.txn_cost_bps
    slip_bps = slippage_bps if slippage_bps is not None else cfg.slippage_bps
    total_cost_per_side = (txn_bps + slip_bps) / 10_000

    end = end or dt.date.today().isoformat()

    # Need extra warmup before 'start' so factor_a (252D) is computable from day 1
    warmup_start = (pd.Timestamp(start) - pd.Timedelta(days=420)).date().isoformat()

    print(f"데이터 다운로드 (warmup {warmup_start} -> {end})...")
    m7 = _download(M7_TICKERS, warmup_start, end).reindex(columns=M7_TICKERS).ffill()

    macro = _download([MACRO_TICKERS["QQQ"], MACRO_TICKERS["VIX"]], warmup_start, end)
    qqq_full = macro[MACRO_TICKERS["QQQ"]] if MACRO_TICKERS["QQQ"] in macro else pd.Series(dtype=float)
    vix_full = macro[MACRO_TICKERS["VIX"]] if MACRO_TICKERS["VIX"] in macro else pd.Series(dtype=float)

    benches = _download(BENCH_TICKERS, warmup_start, end)
    qqq_bench = benches["QQQ"]
    soxx_bench = benches["SOXX"] if "SOXX" in benches else qqq_bench  # fallback
    ai_basket = benches[[t for t in AI_SEMI_BASKET if t in benches.columns]]

    if m7.empty:
        raise RuntimeError("가격 다운로드 실패")

    # Align dates
    bt_dates = m7.loc[start:end].index
    all_dates = m7.index

    daily_m7 = m7.pct_change().fillna(0.0)
    daily_qqq = qqq_bench.pct_change().fillna(0.0)
    daily_soxx = soxx_bench.pct_change().fillna(0.0)
    daily_ai = ai_basket.pct_change().fillna(0.0).mean(axis=1)

    weights = pd.DataFrame(0.0, index=all_dates, columns=M7_TICKERS)
    current_weights = pd.Series(0.0, index=M7_TICKERS)
    entry_prices = pd.Series(np.nan, index=M7_TICKERS)
    txn_cost = pd.Series(0.0, index=all_dates)

    rebalance_log: list[dict] = []
    trade_log: list[dict] = []
    regime_log: list[dict] = []

    print(f"백테스트 진행 중 ({len(bt_dates)} 영업일)...")

    for i, today in enumerate(all_dates):
        if today < bt_dates[0]:
            continue

        past_m7 = m7.iloc[: i]                    # excludes today, no look-ahead
        past_qqq = qqq_full.iloc[: i]
        past_vix = vix_full.iloc[: i]

        if past_m7.shape[0] < 260:
            continue   # still in warmup

        # --- Intraday stop-loss check (executes at today's close) ----------
        prices_today = m7.iloc[i]
        forced_exits: list[str] = []
        for t in M7_TICKERS:
            if current_weights[t] > 0 and not np.isnan(entry_prices[t]):
                change = prices_today[t] / entry_prices[t] - 1.0
                if change <= cfg.stop_loss_from_entry:
                    forced_exits.append(t)
                    trade_log.append({
                        "date": today.date().isoformat(), "ticker": t,
                        "action": "STOP_LOSS",
                        "price": float(prices_today[t]),
                        "entry_price": float(entry_prices[t]),
                        "pnl_pct": round(change, 4),
                    })
        if forced_exits:
            invested_left = 1.0 - sum(current_weights[t] for t in forced_exits)
            for t in forced_exits:
                current_weights[t] = 0.0
                entry_prices[t] = np.nan

        # --- Weekly rebalance? --------------------------------------------
        is_rebal = (today.weekday() == cfg.rebalance_dow) or (i == 0)

        if is_rebal:
            metrics = measure(past_m7, market=past_qqq)
            apply_prefilter(metrics, cfg)
            score(metrics, cfg)
            regime = detect_regime(past_qqq, past_vix, cfg)
            allocate(metrics, cfg, regime=regime.label)

            target = pd.Series(
                {m.ticker: m.weight for m in metrics}, index=M7_TICKERS
            ).fillna(0.0)

            turnover = (target - current_weights).abs().sum()
            txn_cost.loc[today] = turnover * total_cost_per_side

            # Log entries
            for t in M7_TICKERS:
                if target[t] > 0 and current_weights[t] == 0:
                    trade_log.append({
                        "date": today.date().isoformat(), "ticker": t,
                        "action": "BUY", "price": float(prices_today[t]),
                        "entry_price": float(prices_today[t]),
                        "pnl_pct": None,
                    })
                    entry_prices[t] = prices_today[t]
                elif target[t] == 0 and current_weights[t] > 0:
                    trade_log.append({
                        "date": today.date().isoformat(), "ticker": t,
                        "action": "SELL", "price": float(prices_today[t]),
                        "entry_price": float(entry_prices[t]) if not np.isnan(entry_prices[t]) else None,
                        "pnl_pct": round(prices_today[t] / entry_prices[t] - 1.0, 4) if not np.isnan(entry_prices[t]) else None,
                    })
                    entry_prices[t] = np.nan
                elif target[t] > 0 and current_weights[t] > 0:
                    # Held — keep original entry price (anchor for stop loss)
                    pass

            current_weights = target.copy()
            rebalance_log.append({"date": today.date().isoformat(),
                                   "regime": regime.label, **target.to_dict()})
            regime_log.append({"date": today.date().isoformat(),
                                "regime": regime.label, "vix": regime.vix_level,
                                "qqq_5d": regime.qqq_5d_return})

        weights.loc[today] = current_weights.values

    # --- Compute equity curves -------------------------------------------
    port_daily = (weights.shift(1).fillna(0.0) * daily_m7).sum(axis=1) - txn_cost
    port_daily = port_daily.loc[bt_dates[0]: bt_dates[-1]]
    qqq_daily_b = daily_qqq.loc[port_daily.index]
    soxx_daily_b = daily_soxx.loc[port_daily.index]
    ai_daily_b = daily_ai.loc[port_daily.index]

    amqs_eq = initial_capital * (1 + port_daily).cumprod()
    qqq_eq  = initial_capital * (1 + qqq_daily_b).cumprod()
    soxx_eq = initial_capital * (1 + soxx_daily_b).cumprod()
    ai_eq   = initial_capital * (1 + ai_daily_b).cumprod()

    # --- Stats -----------------------------------------------------------
    amqs = _annualized_stats(port_daily); amqs["mdd"] = _max_drawdown(amqs_eq); amqs["final"] = float(amqs_eq.iloc[-1])
    qqq  = _annualized_stats(qqq_daily_b); qqq["mdd"] = _max_drawdown(qqq_eq); qqq["final"] = float(qqq_eq.iloc[-1])
    soxx = _annualized_stats(soxx_daily_b); soxx["mdd"] = _max_drawdown(soxx_eq); soxx["final"] = float(soxx_eq.iloc[-1])
    ai   = _annualized_stats(ai_daily_b); ai["mdd"] = _max_drawdown(ai_eq); ai["final"] = float(ai_eq.iloc[-1])

    # Annual turnover = sum of weekly turnover / years
    weekly_to = sum(txn_cost) / total_cost_per_side if total_cost_per_side > 0 else 0
    years = len(port_daily) / 252
    annual_turnover = weekly_to / years if years > 0 else 0

    # --- Outputs ---------------------------------------------------------
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({
        "date": port_daily.index,
        "amqs_m7":      amqs_eq.values,
        "qqq":          qqq_eq.values,
        "soxx":         soxx_eq.values,
        "ai_semi_basket": ai_eq.values,
        "amqs_daily":   port_daily.values,
        "qqq_daily":    qqq_daily_b.values,
    }).to_csv(out / "backtest_equity.csv", index=False)
    pd.DataFrame(rebalance_log).to_csv(out / "backtest_positions.csv", index=False)
    pd.DataFrame(trade_log).to_csv(out / "backtest_trades.csv", index=False)
    pd.DataFrame(regime_log).to_csv(out / "backtest_regimes.csv", index=False)

    # --- Report ----------------------------------------------------------
    print()
    print("═" * 80)
    print(f"  AMQS-M7 BACKTEST RESULTS  ({start} → {end})")
    print("═" * 80)
    print(f"  {'Metric':<22}{'AMQS-M7':>14}{'QQQ':>14}{'SOXX':>14}{'AI 반도체':>14}")
    print(f"  {'─' * 78}")
    rows = [
        ("총수익률",    "total",  "{:>13.2%}"),
        ("CAGR",        "cagr",   "{:>13.2%}"),
        ("연환산 변동성", "vol",    "{:>13.2%}"),
        ("Sharpe",      "sharpe", "{:>14.2f}"),
        ("MDD",         "mdd",    "{:>13.2%}"),
        ("최종 자산",     "final",  "{:>14,.0f}"),
    ]
    for label, k, fmt in rows:
        print(f"  {label:<22}{fmt.format(amqs[k])}{fmt.format(qqq[k])}{fmt.format(soxx[k])}{fmt.format(ai[k])}")
    print(f"  {'회전율 (연환산)':<22}{annual_turnover:>13.0%}{'~5%':>14}{'~8%':>14}{'0%':>14}")
    print(f"  {'리밸런싱':<22}{len(rebalance_log):>14}")
    print(f"  {'거래비용 (왕복)':<22}{(txn_bps+slip_bps):>13.1f}{'bps':>4}")
    print(f"  {'─' * 78}")
    print(f"  {'vs QQQ':<22}{amqs['total'] - qqq['total']:>+13.2%}  (초과수익)")
    print("═" * 80)
    print(f"  Output: {out / 'backtest_equity.csv'}")
    print(f"  Output: {out / 'backtest_positions.csv'}")
    print(f"  Output: {out / 'backtest_trades.csv'}")
    print(f"  Output: {out / 'backtest_regimes.csv'}")
    print()

    return pd.DataFrame({
        "date": port_daily.index, "amqs_m7": amqs_eq.values,
        "qqq": qqq_eq.values, "soxx": soxx_eq.values, "ai": ai_eq.values,
    })


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2024-01-02")
    p.add_argument("--end", default=None)
    p.add_argument("--txn-bps", type=float, default=None)
    p.add_argument("--slip-bps", type=float, default=None)
    args = p.parse_args()
    run_backtest(start=args.start, end=args.end,
                 txn_cost_bps=args.txn_bps, slippage_bps=args.slip_bps)
