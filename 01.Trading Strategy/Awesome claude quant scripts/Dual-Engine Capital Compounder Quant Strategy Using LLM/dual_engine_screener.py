#!/usr/bin/env python3
"""
Dual-Engine Capital Compounder Quant Screener
==============================================
Screens S&P 500 Financials + Retail (Consumer Discretionary/Staples) constituents
for the Dual-Engine Capital Compounder strategy.

Two engines:
  - Financial Engine: NIM, fees, asset management revenue (capital duration)
  - Retail Engine:    inventory turnover + consumer cash flow (short cycle)

These engines respond asymmetrically to macro cycles, naturally hedging volatility
when held simultaneously.

Author:  Dennis Kim (HoKwang Kim / 김호광)
GitHub:  https://github.com/gameworkerkim/vibe-investing
License: MIT
Version: 1.0 (2026-05-02)

Usage:
    python dual_engine_screener.py                         # Default run
    python dual_engine_screener.py --engine financial      # Filter to Financial only
    python dual_engine_screener.py --engine retail         # Filter to Retail only
    python dual_engine_screener.py --min-score 80
    python dual_engine_screener.py --output results.csv

Dependencies:
    pip install yfinance pandas numpy tabulate
"""

from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance is required. Install with: pip install yfinance")
    sys.exit(1)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# -------------------------------------------------------------------
# Dual-Engine Universe
# -------------------------------------------------------------------
# Curated U.S. names from S&P 500 across the two engines.
# 'engine': "financial" or "retail"
# 'sub_segment': finer classification within each engine
# 'aristocrat_years': consecutive years of dividend growth (Aristocrat 25+, King 50+)
# -------------------------------------------------------------------

DUAL_ENGINE_UNIVERSE: Dict[str, Dict] = {
    # ---------------- Financial Engine ----------------
    # Megabanks
    "JPM":   {"engine": "financial", "name": "JPMorgan Chase",     "sub_segment": "Megabank",       "aristocrat_years": 14},
    "BAC":   {"engine": "financial", "name": "Bank of America",    "sub_segment": "Megabank",       "aristocrat_years": 11},
    "WFC":   {"engine": "financial", "name": "Wells Fargo",        "sub_segment": "Megabank",       "aristocrat_years": 4},
    "C":     {"engine": "financial", "name": "Citigroup",          "sub_segment": "Megabank",       "aristocrat_years": 5},
    # Asset Management & Exchanges
    "BLK":   {"engine": "financial", "name": "BlackRock",          "sub_segment": "Asset Mgmt",     "aristocrat_years": 21},
    "BX":    {"engine": "financial", "name": "Blackstone",         "sub_segment": "Alt Asset Mgmt", "aristocrat_years": 13},
    "TROW":  {"engine": "financial", "name": "T. Rowe Price",      "sub_segment": "Asset Mgmt",     "aristocrat_years": 38},
    "AMP":   {"engine": "financial", "name": "Ameriprise",         "sub_segment": "Asset Mgmt",     "aristocrat_years": 19},
    "SCHW":  {"engine": "financial", "name": "Charles Schwab",     "sub_segment": "Brokerage",      "aristocrat_years": 19},
    "CME":   {"engine": "financial", "name": "CME Group",          "sub_segment": "Exchange",       "aristocrat_years": 11},
    "ICE":   {"engine": "financial", "name": "Intercontinental",   "sub_segment": "Exchange",       "aristocrat_years": 11},
    # Card Networks
    "V":     {"engine": "financial", "name": "Visa",               "sub_segment": "Card Network",   "aristocrat_years": 16},
    "MA":    {"engine": "financial", "name": "Mastercard",         "sub_segment": "Card Network",   "aristocrat_years": 13},
    "AXP":   {"engine": "financial", "name": "American Express",   "sub_segment": "Premium Card",   "aristocrat_years": 13},
    "DFS":   {"engine": "financial", "name": "Discover",           "sub_segment": "Card Network",   "aristocrat_years": 14},
    # Insurance
    "CB":    {"engine": "financial", "name": "Chubb",              "sub_segment": "P&C Insurance",  "aristocrat_years": 31},
    "AFL":   {"engine": "financial", "name": "Aflac",              "sub_segment": "Life Insurance", "aristocrat_years": 42},
    "TRV":   {"engine": "financial", "name": "Travelers",          "sub_segment": "P&C Insurance",  "aristocrat_years": 19},
    "PGR":   {"engine": "financial", "name": "Progressive",        "sub_segment": "Auto Insurance", "aristocrat_years": 6},
    "ALL":   {"engine": "financial", "name": "Allstate",           "sub_segment": "P&C Insurance",  "aristocrat_years": 14},

    # ---------------- Retail Engine ----------------
    # Mass Retail
    "WMT":   {"engine": "retail",    "name": "Walmart",            "sub_segment": "Mass Retail",       "aristocrat_years": 51},
    "COST":  {"engine": "retail",    "name": "Costco",             "sub_segment": "Warehouse Club",    "aristocrat_years": 20},
    "TGT":   {"engine": "retail",    "name": "Target",             "sub_segment": "Discount Retail",   "aristocrat_years": 54},
    "BJ":    {"engine": "retail",    "name": "BJ's Wholesale",     "sub_segment": "Warehouse Club",    "aristocrat_years": 0},
    # Home Improvement
    "HD":    {"engine": "retail",    "name": "Home Depot",         "sub_segment": "Home Improvement",  "aristocrat_years": 15},
    "LOW":   {"engine": "retail",    "name": "Lowe's",             "sub_segment": "Home Improvement",  "aristocrat_years": 60},
    # Off-Price & Specialty
    "TJX":   {"engine": "retail",    "name": "TJX Companies",      "sub_segment": "Off-Price",         "aristocrat_years": 28},
    "ROST":  {"engine": "retail",    "name": "Ross Stores",        "sub_segment": "Off-Price",         "aristocrat_years": 30},
    "DG":    {"engine": "retail",    "name": "Dollar General",     "sub_segment": "Discount",          "aristocrat_years": 0},
    "ULTA":  {"engine": "retail",    "name": "Ulta Beauty",        "sub_segment": "Beauty Specialty",  "aristocrat_years": 0},
    "BBY":   {"engine": "retail",    "name": "Best Buy",           "sub_segment": "Electronics",       "aristocrat_years": 21},
    # Restaurant & QSR
    "MCD":   {"engine": "retail",    "name": "McDonald's",         "sub_segment": "QSR",               "aristocrat_years": 48},
    "SBUX":  {"engine": "retail",    "name": "Starbucks",          "sub_segment": "Coffee",            "aristocrat_years": 14},
    "YUM":   {"engine": "retail",    "name": "Yum! Brands",        "sub_segment": "QSR",               "aristocrat_years": 21},
    "CMG":   {"engine": "retail",    "name": "Chipotle",           "sub_segment": "Fast-Casual",       "aristocrat_years": 0},
    "DPZ":   {"engine": "retail",    "name": "Domino's Pizza",     "sub_segment": "QSR",               "aristocrat_years": 11},
    "TXRH":  {"engine": "retail",    "name": "Texas Roadhouse",    "sub_segment": "Casual Dining",     "aristocrat_years": 13},
}


# -------------------------------------------------------------------
# Configuration & Data Classes
# -------------------------------------------------------------------

@dataclass
class ScreeningConfig:
    """Configuration thresholds for the Dual-Engine screener."""
    # Common
    min_market_cap_b: float = 20.0
    min_avg_dollar_volume_m: float = 200.0
    min_total_score: float = 0.0

    # Financial-specific
    min_roe_financial: float = 12.0
    max_payout_ratio_financial: float = 60.0

    # Retail-specific
    min_roe_retail: float = 15.0       # ROE proxy for ROIC
    max_payout_ratio_retail: float = 65.0
    min_revenue_growth_retail: float = 3.0


@dataclass
class StockMetrics:
    """Container for fetched + computed metrics per stock."""
    ticker: str
    name: str
    engine: str
    sub_segment: str
    aristocrat_years: int

    # Live market data
    current_price: float = 0.0
    market_cap_b: float = 0.0
    avg_dollar_volume_m: float = 0.0

    # Fundamentals
    dividend_yield_pct: float = 0.0
    payout_ratio_pct: float = 0.0
    forward_pe: float = 0.0
    pb_ratio: float = 0.0
    revenue_growth_pct: float = 0.0
    eps_growth_pct: float = 0.0
    roe_pct: float = 0.0

    # Capital return
    buyback_yield_pct: float = 0.0     # Calculated separately
    tcry_pct: float = 0.0              # Total Capital Return Yield = div + buyback

    # Cycle defense
    beta: float = 1.0
    vol_3y_pct: float = 0.0            # 3-year annualized volatility
    max_drawdown_3y_pct: float = 0.0   # 3-year max drawdown

    # Computed scores (out of 35/30/20/15 = 100)
    score_earnings_quality: float = 0.0
    score_dividend_growth: float = 0.0
    score_valuation: float = 0.0
    score_cycle_defense: float = 0.0
    total_score: float = 0.0

    # Pass/fail
    passes_screen: bool = False
    fail_reasons: List[str] = field(default_factory=list)


# -------------------------------------------------------------------
# Data Fetching
# -------------------------------------------------------------------

def fetch_stock_metrics(ticker: str, meta: Dict) -> Optional[StockMetrics]:
    """Pull market data + fundamentals for a single ticker via yfinance."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info

        if not info or info.get("regularMarketPrice") is None:
            print(f"  ⚠ {ticker}: no market data, skipping")
            return None

        m = StockMetrics(
            ticker=ticker,
            name=meta["name"],
            engine=meta["engine"],
            sub_segment=meta["sub_segment"],
            aristocrat_years=meta["aristocrat_years"],
        )

        # Price + market cap
        m.current_price = float(info.get("regularMarketPrice") or info.get("currentPrice") or 0)
        m.market_cap_b = float(info.get("marketCap") or 0) / 1e9

        # Liquidity
        hist = tk.history(period="3mo", auto_adjust=True)
        if not hist.empty:
            m.avg_dollar_volume_m = float((hist["Close"] * hist["Volume"]).mean()) / 1e6

        # Fundamentals
        m.dividend_yield_pct = float(info.get("dividendYield") or 0) * 100
        m.payout_ratio_pct = float(info.get("payoutRatio") or 0) * 100
        m.forward_pe = float(info.get("forwardPE") or 0)
        m.pb_ratio = float(info.get("priceToBook") or 0)
        m.revenue_growth_pct = float(info.get("revenueGrowth") or 0) * 100
        m.eps_growth_pct = float(info.get("earningsGrowth") or 0) * 100
        m.roe_pct = float(info.get("returnOnEquity") or 0) * 100
        m.beta = float(info.get("beta") or 1.0)

        # Buyback yield approximation (shares change × current price / market cap)
        # yfinance does not directly expose buyback yield — approximate via shares delta
        shares_change = info.get("sharesPercentSharesOut") or 0
        # Use net common equity issuance from cashflow if available
        try:
            cashflow = tk.cashflow
            if cashflow is not None and not cashflow.empty:
                # 'Repurchase Of Capital Stock' or 'Common Stock Repurchased'
                buyback_lines = [
                    x for x in cashflow.index
                    if "repurchase" in str(x).lower() or "buyback" in str(x).lower()
                ]
                if buyback_lines and m.market_cap_b > 0:
                    last_buyback = abs(float(cashflow.loc[buyback_lines[0]].iloc[0]))
                    m.buyback_yield_pct = (last_buyback / (m.market_cap_b * 1e9)) * 100
        except Exception:
            m.buyback_yield_pct = 0.0

        m.tcry_pct = m.dividend_yield_pct + m.buyback_yield_pct

        # 3-year price stats for cycle defense
        hist_3y = tk.history(period="3y", auto_adjust=True)
        if len(hist_3y) > 20:
            returns = hist_3y["Close"].pct_change().dropna()
            m.vol_3y_pct = float(returns.std() * np.sqrt(252) * 100)
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative / running_max) - 1
            m.max_drawdown_3y_pct = float(drawdown.min() * 100)

        return m

    except Exception as exc:
        print(f"  ✗ {ticker}: fetch error — {type(exc).__name__}: {exc}")
        return None


# -------------------------------------------------------------------
# Scoring Engine (0-35 / 0-30 / 0-20 / 0-15 = 100)
# -------------------------------------------------------------------

def score_earnings_quality(m: StockMetrics) -> float:
    """Score 0-35 based on ROE + TCRY + payout efficiency."""
    score = 0.0

    # ROE component (0-12 points)
    if m.engine == "financial":
        if m.roe_pct >= 25: score += 12
        elif m.roe_pct >= 18: score += 9
        elif m.roe_pct >= 12: score += 6
        elif m.roe_pct >= 8: score += 3
    else:  # retail
        if m.roe_pct >= 40: score += 12
        elif m.roe_pct >= 25: score += 9
        elif m.roe_pct >= 15: score += 6
        elif m.roe_pct >= 10: score += 3

    # TCRY component (0-15 points) — the most critical metric for compounders
    if m.tcry_pct >= 7: score += 15
    elif m.tcry_pct >= 5: score += 12
    elif m.tcry_pct >= 4: score += 9
    elif m.tcry_pct >= 3: score += 6
    elif m.tcry_pct >= 2: score += 3

    # Payout sustainability (0-8 points) — lower payout = more reinvestment runway
    if m.payout_ratio_pct > 0:
        if m.payout_ratio_pct <= 30: score += 8
        elif m.payout_ratio_pct <= 50: score += 6
        elif m.payout_ratio_pct <= 65: score += 4
        elif m.payout_ratio_pct <= 80: score += 2

    return min(score, 35)


def score_dividend_growth(m: StockMetrics) -> float:
    """Score 0-30 based on Aristocrat status + dividend yield + growth signals."""
    score = 0.0

    # Aristocrat status (0-15 points) — major weight
    if m.aristocrat_years >= 50: score += 15      # King
    elif m.aristocrat_years >= 25: score += 12    # Aristocrat
    elif m.aristocrat_years >= 15: score += 9
    elif m.aristocrat_years >= 10: score += 6
    elif m.aristocrat_years >= 5: score += 3

    # Dividend yield component (0-8 points)
    if m.dividend_yield_pct >= 3.0: score += 8
    elif m.dividend_yield_pct >= 2.0: score += 6
    elif m.dividend_yield_pct >= 1.0: score += 4
    elif m.dividend_yield_pct >= 0.5: score += 2

    # EPS growth as proxy for sustainable dividend growth (0-7 points)
    if m.eps_growth_pct >= 15: score += 7
    elif m.eps_growth_pct >= 8: score += 5
    elif m.eps_growth_pct >= 3: score += 3
    elif m.eps_growth_pct >= 0: score += 1

    return min(score, 30)


def score_valuation(m: StockMetrics) -> float:
    """Score 0-20 based on engine-specific valuation lens."""
    score = 0.0

    # Forward P/E (0-10 points)
    if m.forward_pe > 0:
        if m.engine == "financial":
            # Financials: lower P/E preferred (typical 8-20)
            if m.forward_pe <= 10: score += 10
            elif m.forward_pe <= 15: score += 8
            elif m.forward_pe <= 20: score += 5
            elif m.forward_pe <= 30: score += 2
        else:  # retail
            # Retail: typical 15-30, growth premium tolerated
            if m.forward_pe <= 18: score += 10
            elif m.forward_pe <= 25: score += 8
            elif m.forward_pe <= 35: score += 5
            elif m.forward_pe <= 50: score += 2

    # P/B for Financials, P/E-yield for Retail (0-6 points)
    if m.engine == "financial":
        if m.pb_ratio > 0:
            if m.pb_ratio <= 1.0: score += 6
            elif m.pb_ratio <= 1.5: score += 5
            elif m.pb_ratio <= 2.5: score += 3
            elif m.pb_ratio <= 4.0: score += 1
    else:
        # Retail: dividend yield as inverse valuation proxy
        if m.dividend_yield_pct >= 2.5: score += 6
        elif m.dividend_yield_pct >= 1.5: score += 4
        elif m.dividend_yield_pct >= 0.8: score += 2

    # PEG-like check (0-4 points)
    if m.eps_growth_pct > 0 and m.forward_pe > 0:
        peg = m.forward_pe / m.eps_growth_pct
        if peg <= 1.0: score += 4
        elif peg <= 1.5: score += 3
        elif peg <= 2.0: score += 2
        elif peg <= 3.0: score += 1

    return min(score, 20)


def score_cycle_defense(m: StockMetrics) -> float:
    """Score 0-15 based on beta, drawdown, and volatility."""
    score = 0.0

    # Beta (0-6 points) — closer to 1.0 or below preferred for defensive compounders
    if 0.7 <= m.beta <= 1.0: score += 6
    elif 0.5 <= m.beta < 0.7 or 1.0 < m.beta <= 1.15: score += 4
    elif 0.3 <= m.beta < 0.5 or 1.15 < m.beta <= 1.30: score += 2

    # Max drawdown defense (0-5 points) — shallow drawdowns score higher
    if m.max_drawdown_3y_pct >= -15: score += 5
    elif m.max_drawdown_3y_pct >= -25: score += 4
    elif m.max_drawdown_3y_pct >= -35: score += 2

    # Volatility (0-4 points)
    if 0 < m.vol_3y_pct <= 18: score += 4
    elif m.vol_3y_pct <= 25: score += 3
    elif m.vol_3y_pct <= 32: score += 1

    return min(score, 15)


def compute_scores(m: StockMetrics) -> StockMetrics:
    """Run all scoring functions + total."""
    m.score_earnings_quality = round(score_earnings_quality(m), 1)
    m.score_dividend_growth = round(score_dividend_growth(m), 1)
    m.score_valuation = round(score_valuation(m), 1)
    m.score_cycle_defense = round(score_cycle_defense(m), 1)
    m.total_score = round(
        m.score_earnings_quality
        + m.score_dividend_growth
        + m.score_valuation
        + m.score_cycle_defense,
        1,
    )
    return m


# -------------------------------------------------------------------
# Screening Logic
# -------------------------------------------------------------------

def apply_screen(m: StockMetrics, cfg: ScreeningConfig) -> StockMetrics:
    """Mark pass/fail + record reasons."""
    m.fail_reasons = []

    if m.market_cap_b < cfg.min_market_cap_b:
        m.fail_reasons.append(f"mcap<${cfg.min_market_cap_b}B")
    if m.avg_dollar_volume_m < cfg.min_avg_dollar_volume_m:
        m.fail_reasons.append(f"liquidity<${cfg.min_avg_dollar_volume_m}M")

    if m.engine == "financial":
        if m.roe_pct < cfg.min_roe_financial:
            m.fail_reasons.append(f"roe<{cfg.min_roe_financial}%")
        if m.payout_ratio_pct > cfg.max_payout_ratio_financial:
            m.fail_reasons.append(f"payout>{cfg.max_payout_ratio_financial}%")
    else:  # retail
        if m.roe_pct < cfg.min_roe_retail:
            m.fail_reasons.append(f"roe<{cfg.min_roe_retail}%")
        if m.payout_ratio_pct > cfg.max_payout_ratio_retail:
            m.fail_reasons.append(f"payout>{cfg.max_payout_ratio_retail}%")
        if m.revenue_growth_pct < cfg.min_revenue_growth_retail:
            m.fail_reasons.append(f"rev_growth<{cfg.min_revenue_growth_retail}%")

    if m.total_score < cfg.min_total_score:
        m.fail_reasons.append(f"total_score<{cfg.min_total_score}")

    m.passes_screen = len(m.fail_reasons) == 0
    return m


# -------------------------------------------------------------------
# Main Pipeline
# -------------------------------------------------------------------

def run_screener(
    engine_filter: Optional[str] = None,
    min_score: float = 0.0,
    output_csv: str = "dual_engine_screen_results.csv",
    config: Optional[ScreeningConfig] = None,
) -> pd.DataFrame:
    """Execute the full Dual-Engine screener."""
    cfg = config or ScreeningConfig()
    cfg.min_total_score = max(cfg.min_total_score, min_score)

    print("=" * 76)
    print(f"  Dual-Engine Capital Compounder Screener  (Run: {datetime.now():%Y-%m-%d %H:%M})")
    print("=" * 76)
    print(f"Universe size:       {len(DUAL_ENGINE_UNIVERSE)} tickers")
    print(f"Engine filter:       {engine_filter or 'Both engines'}")
    print(f"Min total score:     {cfg.min_total_score}")
    print(f"Min market cap:      ${cfg.min_market_cap_b}B")
    print("=" * 76)

    results: List[StockMetrics] = []

    for ticker, meta in DUAL_ENGINE_UNIVERSE.items():
        if engine_filter is not None and meta["engine"] != engine_filter:
            continue

        print(f"  → fetching {ticker} ({meta['name']})...")
        m = fetch_stock_metrics(ticker, meta)
        if m is None:
            continue
        m = compute_scores(m)
        m = apply_screen(m, cfg)
        results.append(m)

    if not results:
        print("\nNo stocks fetched. Check network connectivity.")
        return pd.DataFrame()

    rows = []
    for m in results:
        rows.append({
            "ticker": m.ticker,
            "name": m.name,
            "engine": m.engine,
            "sub_segment": m.sub_segment,
            "aristocrat_yrs": m.aristocrat_years,
            "price": round(m.current_price, 2),
            "mcap_$B": round(m.market_cap_b, 1),
            "div_yield_%": round(m.dividend_yield_pct, 2),
            "buyback_yield_%": round(m.buyback_yield_pct, 2),
            "TCRY_%": round(m.tcry_pct, 2),
            "payout_%": round(m.payout_ratio_pct, 1),
            "roe_%": round(m.roe_pct, 1),
            "fwd_PE": round(m.forward_pe, 1),
            "P/B": round(m.pb_ratio, 2),
            "beta": round(m.beta, 2),
            "vol_3y_%": round(m.vol_3y_pct, 1),
            "max_dd_3y_%": round(m.max_drawdown_3y_pct, 1),
            "score_earn": m.score_earnings_quality,
            "score_div": m.score_dividend_growth,
            "score_val": m.score_valuation,
            "score_def": m.score_cycle_defense,
            "total_score": m.total_score,
            "passes": "✓" if m.passes_screen else "✗",
            "fail_reasons": "; ".join(m.fail_reasons) if m.fail_reasons else "",
        })

    df = pd.DataFrame(rows).sort_values("total_score", ascending=False)

    print("\n" + "=" * 76)
    print("  Screening Results (sorted by total score)")
    print("=" * 76)
    display_cols = ["ticker", "engine", "sub_segment", "div_yield_%", "TCRY_%",
                    "roe_%", "fwd_PE", "total_score", "passes"]
    try:
        from tabulate import tabulate
        print(tabulate(df[display_cols], headers="keys", tablefmt="github", showindex=False))
    except ImportError:
        print(df[display_cols].to_string(index=False))

    df.to_csv(output_csv, index=False)
    print(f"\n✓ Full results saved to: {output_csv}")

    # Summary
    passes = df[df["passes"] == "✓"]
    print(f"\n  Total fetched:       {len(df)}")
    print(f"  Passed all filters:  {len(passes)}")
    print(f"  Score ≥ 80:          {len(df[df['total_score'] >= 80])}")
    print(f"  Score ≥ 70:          {len(df[df['total_score'] >= 70])}")

    # Engine breakdown
    print("\n  Engine breakdown (passes only):")
    for engine in ["financial", "retail"]:
        engine_passes = passes[passes["engine"] == engine]
        if len(engine_passes) > 0:
            print(f"    {engine.capitalize():10}: {len(engine_passes)} names "
                  f"(avg score {engine_passes['total_score'].mean():.1f}, "
                  f"avg TCRY {engine_passes['TCRY_%'].mean():.1f}%)")
        else:
            print(f"    {engine.capitalize():10}: 0 names")

    # Top picks suggestion
    print("\n  Suggested 5+5 Dual-Engine portfolio (top scores by engine):")
    for engine in ["financial", "retail"]:
        engine_passes = passes[passes["engine"] == engine].head(5)
        tickers = ", ".join(engine_passes["ticker"].tolist())
        print(f"    {engine.capitalize():10}: {tickers}")

    return df


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Dual-Engine Capital Compounder Quant Screener for U.S. equities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dual_engine_screener.py
  python dual_engine_screener.py --engine financial --min-score 80
  python dual_engine_screener.py --engine retail --output retail_screen.csv
        """,
    )
    parser.add_argument("--engine", type=str, choices=["financial", "retail"],
                        help="Filter by engine (financial or retail). Default: both")
    parser.add_argument("--min-score", type=float, default=0.0,
                        help="Minimum total score (default: 0)")
    parser.add_argument("--output", type=str, default="dual_engine_screen_results.csv",
                        help="Output CSV path (default: dual_engine_screen_results.csv)")
    parser.add_argument("--min-mcap", type=float, default=20.0,
                        help="Minimum market cap in $B (default: 20)")

    args = parser.parse_args()

    cfg = ScreeningConfig(min_market_cap_b=args.min_mcap)

    run_screener(
        engine_filter=args.engine,
        min_score=args.min_score,
        output_csv=args.output,
        config=cfg,
    )


if __name__ == "__main__":
    main()
