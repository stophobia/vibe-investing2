"""
AMQS-M7 CLI Tracker
====================
Phase 1: command-line alerts (this file)
Phase 2: broker integration via src/broker.py

Outputs a faithful AMQS report:
  * Macro regime (Risk-On / Risk-Off / Defensive) — original AMQS filter
  * 4-Factor Momentum Composite per name
  * 100-point composite (5 dimensions, including NEW 단기 하락 매수)
  * Position tier: CENTER / SATELLITE / TACTICAL / DIP_BUY / REDUCE / EXIT
  * Stop-loss tracking (-12% from rebalance entry)

Usage:
  python -m src.amqs_m7 --mode track
  python -m src.amqs_m7 --mode track --watch --interval 30 --csv data/log.csv
  python -m src.amqs_m7 --mode backtest --start 2024-01-02 --end 2026-04-30
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    from .strategy import (
        AMQSConfig, M7_TICKERS, MACRO_TICKERS, DEFENSIVE_BASKET,
        MacroRegime, run_amqs_m7,
    )
    from .broker import build_broker
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.strategy import (
        AMQSConfig, M7_TICKERS, MACRO_TICKERS, DEFENSIVE_BASKET,
        MacroRegime, run_amqs_m7,
    )
    from src.broker import build_broker


# ---------------------------------------------------------------------------
# Data fetching (yfinance)
# ---------------------------------------------------------------------------

def fetch_prices(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as e:
        raise RuntimeError("yfinance 미설치. `pip install yfinance`") from e

    raw = yf.download(
        tickers=tickers, period=period, interval="1d",
        auto_adjust=True, progress=False, group_by="ticker", threads=True,
    )
    if isinstance(raw.columns, pd.MultiIndex):
        if tickers[0] in raw.columns.get_level_values(0):
            closes = pd.concat(
                {t: raw[t]["Close"] for t in tickers if t in raw.columns.get_level_values(0)},
                axis=1,
            )
        else:
            closes = raw["Close"]
    else:
        closes = raw[["Close"]].rename(columns={"Close": tickers[0]})
    return closes.dropna(how="all")


def fetch_macro(period: str = "2y") -> tuple[pd.Series, pd.Series]:
    """Fetch QQQ and VIX."""
    df = fetch_prices([MACRO_TICKERS["QQQ"], MACRO_TICKERS["VIX"]], period=period)
    qqq = df[MACRO_TICKERS["QQQ"]] if MACRO_TICKERS["QQQ"] in df else pd.Series(dtype=float)
    vix = df[MACRO_TICKERS["VIX"]] if MACRO_TICKERS["VIX"] in df else pd.Series(dtype=float)
    return qqq, vix


# ---------------------------------------------------------------------------
# Stop-loss bookkeeping (persisted)
# ---------------------------------------------------------------------------

STATE_FILE = Path("data/amqs_m7_state.json")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"entries": {}, "last_rebalance": None}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def check_stops(df: pd.DataFrame, state: dict, config: AMQSConfig) -> list[str]:
    """Compare current prices to entry prices; return ticker list that breached stop."""
    triggers = []
    entries = state.get("entries", {})
    for _, row in df.iterrows():
        t, price = row["ticker"], row["price"]
        if t in entries:
            entry_price = entries[t]["price"]
            change = price / entry_price - 1.0
            if change <= config.stop_loss_from_entry:
                triggers.append(t)
    return triggers


def update_entries_on_rebalance(df: pd.DataFrame, state: dict, as_of: dt.datetime) -> None:
    new_entries = {}
    for _, row in df.iterrows():
        if row["weight"] > 0:
            new_entries[row["ticker"]] = {
                "price": float(row["price"]),
                "weight": float(row["weight"]),
                "entry_date": as_of.date().isoformat(),
                "signal_at_entry": row["signal"],
            }
    state["entries"] = new_entries
    state["last_rebalance"] = as_of.isoformat()


# ---------------------------------------------------------------------------
# CLI rendering
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    GREEN = "\033[32m"; BRIGHT_GREEN = "\033[92m"
    YELLOW = "\033[33m"; ORANGE = "\033[38;5;208m"
    RED = "\033[31m"; BRIGHT_RED = "\033[91m"
    CYAN = "\033[36m"; MAGENTA = "\033[35m"
    BLUE = "\033[34m"; GREY = "\033[90m"


if not _supports_color():
    for a in list(vars(C).keys()):
        if not a.startswith("_") and a.isupper():
            setattr(C, a, "")


SIGNAL_STYLE = {
    "DIP_BUY":   (C.BRIGHT_GREEN + C.BOLD, "[++]", "단기 하락 매수"),
    "CENTER":    (C.GREEN + C.BOLD,        "[+ ]", "중심 포지션"),
    "SATELLITE": (C.GREEN,                 "[+ ]", "위성 포지션"),
    "TACTICAL":  (C.CYAN,                  "[ o]", "전술적 보유"),
    "REDUCE":    (C.ORANGE,                "[ -]", "비중 축소"),
    "EXIT":      (C.BRIGHT_RED + C.BOLD,   "[--]", "청산"),
    "EXCLUDED":  (C.GREY,                  "[ x]", "필터 탈락"),
}

REGIME_STYLE = {
    "RISK_ON":   (C.GREEN   + C.BOLD, "[ON ]",  "RISK-ON"),
    "RISK_OFF":  (C.RED     + C.BOLD, "[OFF]",  "RISK-OFF (50% 현금화)"),
    "DEFENSIVE": (C.MAGENTA + C.BOLD, "[DEF]",  "DEFENSIVE (방어 바스켓)"),
}


def _fmt_pct(x) -> str:
    if x is None or pd.isna(x):
        return "  N/A "
    return f"{x * 100:+5.1f}%"


def print_report(df: pd.DataFrame, regime: MacroRegime, config: AMQSConfig,
                 as_of: dt.datetime, stop_triggers: list[str] | None = None) -> None:
    stop_triggers = stop_triggers or []
    W = 102
    print()
    print(f"{C.BOLD}{C.CYAN}{'═' * W}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  AMQS-M7  ·  Adaptive Momentum Quant Strategy (Magnificent 7){C.RESET}")
    print(f"{C.DIM}  vibe-investing extension  ·  as of {as_of.strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * W}{C.RESET}")

    # Macro regime banner
    rstyle, remoji, rlabel = REGIME_STYLE.get(regime.label, ("", "·", regime.label))
    print()
    print(f"  거시 레짐: {rstyle}{remoji} {rlabel}{C.RESET}")
    print(f"  {C.DIM}{regime.reason}{C.RESET}")
    print(f"  {C.DIM}QQQ {'>' if regime.qqq_above_200ma else '<'} 200MA  ·  "
          f"VIX {regime.vix_level:.1f}  ·  QQQ 5D {regime.qqq_5d_return:+.1%}{C.RESET}")
    print()

    # Strategy weights line
    print(f"  {C.DIM}100점 구성: 모멘텀 신호 {config.w_momentum_signal:.0%} · "
          f"단기 하락 매수 {config.w_pullback_buy:.0%} · "
          f"추세 품질 {config.w_trend_quality:.0%} · "
          f"변동성 알파 {config.w_vol_adj_alpha:.0%} · "
          f"거시 {config.w_macro_fit:.0%}{C.RESET}")
    print()

    # Per-name table
    hdr = (
        f"  {'Ticker':<7}{'Price':>9}  {'12-1':>7}{'6-1':>7}{'3-1':>7}  "
        f"{'5D':>7}{'20D':>7}  {'RSI':>5} {'52W':>7}  {'Score':>7} {'Wt':>6}  Signal"
    )
    print(f"{C.BOLD}{hdr}{C.RESET}")
    print(f"  {'─' * (W - 2)}")
    for _, row in df.iterrows():
        style, emoji, label = SIGNAL_STYLE.get(row["signal"], ("", "·", row["signal"]))
        line = (
            f"  {row['ticker']:<7}{row['price']:>9.2f}  "
            f"{_fmt_pct(row['factor_A_12-1']):>7}{_fmt_pct(row['factor_B_6-1']):>7}{_fmt_pct(row['factor_C_3-1']):>7}  "
            f"{_fmt_pct(row['ret_5d']):>7}{_fmt_pct(row['ret_20d']):>7}  "
            f"{(row['rsi_14'] if row['rsi_14'] is not None else 0):>5.0f} "
            f"{_fmt_pct(row['dist_52w_high']):>7}  "
            f"{row['total_100']:>6.1f}  "
            f"{row['weight']:>5.1%}  "
            f"{style}{emoji} {label}{C.RESET}"
        )
        print(line)

    # Per-name rationale
    print()
    print(f"{C.BOLD}  근거 (Rationale){C.RESET}")
    print(f"  {'─' * (W - 2)}")
    for _, row in df.iterrows():
        style, emoji, _ = SIGNAL_STYLE.get(row["signal"], ("", "·", ""))
        breakdown = (
            f"  [{C.DIM}M:{row['score_momentum']:.0f} "
            f"D:{row['score_pullback']:.0f} "
            f"Q:{row['score_quality']:.0f} "
            f"V:{row['score_vol_alpha']:.0f} "
            f"X:{row['score_macro']:.0f}{C.RESET}]"
        )
        print(f"  {style}{emoji} {row['ticker']:<6}{C.RESET}{breakdown} {C.DIM}{row['reason']}{C.RESET}")

    # Active alerts
    alerts = df[df["signal"].isin(["DIP_BUY", "EXIT"])]
    if not alerts.empty or stop_triggers:
        print()
        print(f"{C.BOLD}{C.MAGENTA}  >> 실행 알림 (Action Alerts){C.RESET}")
        print(f"  {'─' * (W - 2)}")
        for _, row in alerts.iterrows():
            style, emoji, label = SIGNAL_STYLE[row["signal"]]
            print(f"  {style}{emoji} [{label}] {row['ticker']} → 목표 {row['weight']:.1%}{C.RESET}")
            print(f"     {C.DIM}{row['reason']}{C.RESET}")
        for t in stop_triggers:
            print(f"  {C.BRIGHT_RED}{C.BOLD}[STOP-LOSS] {t} -> 즉시 청산 (-12% 손절선 도달){C.RESET}")

    print()
    total = df["weight"].sum()
    cash = 1.0 - total
    print(f"  {C.BOLD}투자 비중 합계{C.RESET}: {total:.1%}   "
          f"{C.DIM}현금 {cash:.1%}{C.RESET}")
    if regime.label == "RISK_OFF":
        print(f"  {C.YELLOW}[!] Risk-Off: 자동 50% 현금화 적용{C.RESET}")
    elif regime.label == "DEFENSIVE":
        print(f"  {C.MAGENTA}[!] Defensive: 100% 방어 바스켓 ({', '.join(DEFENSIVE_BASKET)}) 전환 권고{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * W}{C.RESET}")
    print()


# ---------------------------------------------------------------------------
# CSV logging
# ---------------------------------------------------------------------------

def append_csv(df: pd.DataFrame, regime: MacroRegime, csv_path: str, as_of: dt.datetime) -> None:
    out = df.copy()
    out.insert(0, "timestamp", as_of.isoformat(timespec="seconds"))
    out.insert(1, "regime", regime.label)
    out.insert(2, "vix", regime.vix_level)
    out.insert(3, "qqq_5d", regime.qqq_5d_return)
    p = Path(csv_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        out.to_csv(p, mode="a", header=False, index=False)
    else:
        out.to_csv(p, mode="w", header=True, index=False)
    print(f"{C.DIM}  CSV 기록: {p}{C.RESET}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_once(config: AMQSConfig, csv_path: Optional[str], broker_name: str,
             paper_trade: bool, force_rebalance: bool) -> pd.DataFrame:
    as_of = dt.datetime.now()

    print(f"{C.DIM}  가격 데이터 수집...{C.RESET}")
    prices = fetch_prices(M7_TICKERS, period="2y")
    qqq, vix = fetch_macro(period="2y")

    if prices.empty or prices.shape[0] < 260:
        print(f"{C.RED}ERROR: 가격 데이터 부족 ({prices.shape[0]}일){C.RESET}")
        return pd.DataFrame()

    df, regime = run_amqs_m7(prices, qqq=qqq, vix=vix, config=config)

    # Stop-loss check
    state = load_state()
    stop_triggers = check_stops(df, state, config)

    # Force-exit positions that breach stop
    if stop_triggers:
        for i, row in df.iterrows():
            if row["ticker"] in stop_triggers:
                df.at[i, "signal"] = "EXIT"
                df.at[i, "weight"] = 0.0
                df.at[i, "reason"] = f"손절선 도달 (-12%)"

    print_report(df, regime, config, as_of, stop_triggers)

    if csv_path:
        append_csv(df, regime, csv_path, as_of)

    # Rebalance decision (default: Mondays only, unless --force)
    is_monday = as_of.weekday() == config.rebalance_dow
    do_rebalance = force_rebalance or is_monday or stop_triggers or state.get("last_rebalance") is None

    target_weights = dict(zip(df["ticker"], df["weight"]))
    broker = build_broker(broker_name, paper=paper_trade)
    if do_rebalance:
        broker.rebalance(target_weights, as_of=as_of)
        update_entries_on_rebalance(df, state, as_of)
        save_state(state)
    else:
        next_rebal = config.rebalance_dow - as_of.weekday()
        if next_rebal <= 0:
            next_rebal += 7
        print(f"  {C.DIM}리밸런싱 보류: 다음 월요일 (D-{next_rebal}) 또는 손절 트리거 시 실행{C.RESET}")

    return df


def main() -> int:
    p = argparse.ArgumentParser(description="AMQS-M7 tracker")
    p.add_argument("--mode", choices=["track", "backtest"], default="track")
    p.add_argument("--csv", default="data/amqs_m7_log.csv",
                   help="CSV 경로 (빈 문자열이면 비활성화)")
    p.add_argument("--watch", action="store_true")
    p.add_argument("--interval", type=int, default=30, help="--watch 폴링 (분)")
    p.add_argument("--broker", default="cli", choices=["cli", "kis", "dryrun"])
    p.add_argument("--live", action="store_true", help="실거래 (기본 paper)")
    p.add_argument("--force-rebalance", action="store_true", help="요일 무관 즉시 리밸런싱")
    p.add_argument("--start", default="2024-01-02", help="(backtest) 시작일")
    p.add_argument("--end", default=None, help="(backtest) 종료일")
    args = p.parse_args()

    config = AMQSConfig()

    if args.mode == "backtest":
        try:
            from .backtest import run_backtest
        except ImportError:
            from src.backtest import run_backtest
        run_backtest(start=args.start, end=args.end, config=config)
        return 0

    csv_path = args.csv if args.csv else None

    if not args.watch:
        run_once(config, csv_path, args.broker, not args.live, args.force_rebalance)
        return 0

    print(f"{C.CYAN}워치 모드 (간격 {args.interval}분, Ctrl+C 종료){C.RESET}")
    try:
        while True:
            run_once(config, csv_path, args.broker, not args.live, args.force_rebalance)
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}종료{C.RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
