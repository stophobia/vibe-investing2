"""QQQUpDownSignal — NASDAQ 100 일일 상승/하락 Top 10 시그널.

yfinance로 NASDAQ 100 구성 종목의 직전 거래일 종가 대비 변동률을 계산하고
상승률 상위 10개, 하락률 상위 10개 종목을 콘솔에 출력한다.
"""

from __future__ import annotations

import sys
from datetime import datetime

import pandas as pd # type: ignore
import yfinance as yf # type: ignore


NASDAQ_100_TICKERS: list[str] = [
    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD", "AMGN",
    "AMZN", "ANSS", "APP", "ARM", "ASML", "AVGO", "AZN", "BIIB", "BKNG", "BKR",
    "CCEP", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST", "CPRT", "CRWD", "CSCO",
    "CSGP", "CSX", "CTAS", "CTSH", "DASH", "DDOG", "DXCM", "EA", "EXC", "FANG",
    "FAST", "FTNT", "GEHC", "GFS", "GILD", "GOOG", "GOOGL", "HON", "IDXX", "INTC",
    "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN", "LRCX", "LULU", "MAR", "MCHP",
    "MDB", "MDLZ", "MELI", "META", "MNST", "MRVL", "MSFT", "MSTR", "MU", "NFLX",
    "NVDA", "NXPI", "ODFL", "ON", "ORLY", "PANW", "PAYX", "PCAR", "PDD", "PEP",
    "PLTR", "PYPL", "QCOM", "REGN", "ROP", "ROST", "SBUX", "SHOP", "SNPS", "TEAM",
    "TMUS", "TSLA", "TTD", "TTWO", "TXN", "VRSK", "VRTX", "WBD", "WDAY", "XEL",
    "ZS",
]


def fetch_daily_returns(tickers: list[str]) -> pd.DataFrame:
    data = yf.download(
        tickers=tickers,
        period="5d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    rows: list[dict[str, float | str]] = []
    for ticker in tickers:
        try:
            close = data[ticker]["Close"].dropna()
        except (KeyError, TypeError):
            continue
        if len(close) < 2:
            continue
        prev_close = float(close.iloc[-2])
        last_close = float(close.iloc[-1])
        if prev_close == 0:
            continue
        change_pct = (last_close - prev_close) / prev_close * 100
        rows.append(
            {
                "ticker": ticker,
                "prev_close": prev_close,
                "last_close": last_close,
                "change_pct": change_pct,
            }
        )

    return pd.DataFrame(rows)


def print_table(title: str, df: pd.DataFrame) -> None:
    print(f"\n=== {title} ===")
    print(
        df.to_string(
            index=False,
            formatters={
                "prev_close": "{:>10.2f}".format,
                "last_close": "{:>10.2f}".format,
                "change_pct": "{:>+8.2f}%".format,
            },
        )
    )


def main() -> int:
    print(f"QQQUpDownSignal — NASDAQ 100 daily movers")
    print(f"Run at: {datetime.now().isoformat(timespec='seconds')}")

    df = fetch_daily_returns(NASDAQ_100_TICKERS)
    if df.empty:
        print("No price data returned.", file=sys.stderr)
        return 1

    df = df.sort_values("change_pct", ascending=False).reset_index(drop=True)
    gainers = df.head(10)
    losers = df.tail(10).iloc[::-1].reset_index(drop=True)

    print_table("Top 10 Gainers", gainers)
    print_table("Top 10 Losers", losers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
