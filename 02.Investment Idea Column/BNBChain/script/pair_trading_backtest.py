"""
Phase 5 Paper - Cointegration-Based BNB/ETH Pair Trading Strategy
Walk-Forward Backtest with Transaction Costs

Author: HoKwang Kim (Dennis Kim)
Date: 2026-05-01
ORCID: 0009-0002-0962-2175

Prior research:
- Engle & Granger (1987): Cointegration test methodology
- Gatev et al. (2006): Pair trading classic (Distance method)
- Fama & French (1988): Mean reversion theoretical foundation
- Jegadeesh & Titman (1993): Momentum/mean-reversion trading strategy
- Kim, H. (2026, SSRN 6632838): The 72-Hour Shock - Token unlock price impact

This module performs:
1. ETH-BNB cointegration test (Engle-Granger simplified)
2. Hedge ratio beta estimation
3. Z-score based entry/exit signal generation
4. Walk-forward validation (50/50 split)
5. Transaction costs reflection (commission + slippage)
6. Performance metrics: Sharpe ratio, Calmar ratio, Max Drawdown, Win rate

NOTE: This is an exploratory backtest using daily series interpolated from
quarterly verified prices. Section 5.4 of the paper warns this is observational
evidence only and not recommended for trading strategy use. Real daily OHLCV
data should be used in subsequent versions.

Reproducibility: pip install pandas numpy scipy
Run: python pair_trading_backtest.py
"""

import numpy as np
import pandas as pd
from scipy import stats

# ============= Data Generation (based on verified quarterly data) =============

QUARTERLY_DATA = {
    '2024Q1': {'btc': 71280, 'eth': 3500, 'bnb': 556, 'days': 91},
    '2024Q2': {'btc': 62800, 'eth': 3422, 'bnb': 576, 'days': 91},
    '2024Q3': {'btc': 63300, 'eth': 2607, 'bnb': 572, 'days': 92},
    '2024Q4': {'btc': 93390, 'eth': 3337, 'bnb': 720, 'days': 92},
    '2025Q1': {'btc': 82534, 'eth': 1820, 'bnb': 629, 'days': 90},
    '2025Q2': {'btc': 107175, 'eth': 2510, 'bnb': 655, 'days': 91},
    '2025Q3': {'btc': 114000, 'eth': 4215, 'bnb': 1030, 'days': 92},
    '2025Q4': {'btc': 108000, 'eth': 4500, 'bnb': 1200, 'days': 92},
    '2026Q1': {'btc': 95000, 'eth': 3800, 'bnb': 1100, 'days': 90},
}


def generate_daily_series(seed=42):
    """Generate daily price time series from verified quarterly closing prices.
    
    Quarterly closes are anchors. Daily volatility uses verified BNB/ETH/BTC
    historical volatility (sigma_d ~ 3-5%) with GBM-style noise.
    """
    np.random.seed(seed)
    
    quarters = list(QUARTERLY_DATA.keys())
    btc_prices, eth_prices, bnb_prices, dates = [], [], [], []
    
    base_date = pd.Timestamp('2024-01-01')
    days_offset = 0
    
    for i in range(len(quarters) - 1):
        q_start = QUARTERLY_DATA[quarters[i]]
        q_end = QUARTERLY_DATA[quarters[i+1]]
        n_days = q_start['days']
        
        for d in range(n_days):
            frac = d / n_days
            btc_lin = q_start['btc'] + (q_end['btc'] - q_start['btc']) * frac
            eth_lin = q_start['eth'] + (q_end['eth'] - q_start['eth']) * frac
            bnb_lin = q_start['bnb'] + (q_end['bnb'] - q_start['bnb']) * frac
            
            # Asset correlation reflected (BTC-BNB ~0.66, ETH-BNB ~0.85)
            btc_noise = np.random.normal(0, 0.025)
            eth_noise = 0.85 * btc_noise + np.random.normal(0, 0.015)
            bnb_noise = 0.66 * btc_noise + 0.30 * eth_noise + np.random.normal(0, 0.012)
            
            btc_prices.append(btc_lin * (1 + btc_noise))
            eth_prices.append(eth_lin * (1 + eth_noise))
            bnb_prices.append(bnb_lin * (1 + bnb_noise))
            dates.append(base_date + pd.Timedelta(days=days_offset + d))
        
        days_offset += n_days
    
    df = pd.DataFrame({
        'date': dates,
        'btc': btc_prices,
        'eth': eth_prices,
        'bnb': bnb_prices,
    })
    df.set_index('date', inplace=True)
    return df


# ============= 1. Cointegration Test =============

def cointegration_test(y, x, alpha_level=0.05):
    """Simplified Engle-Granger cointegration test.
    
    Steps:
    1. y = alpha + beta * x + epsilon (linear regression)
    2. ADF test on residual epsilon
    3. p-value < alpha indicates cointegration
    
    Note: Production code should use statsmodels.tsa.stattools.coint().
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    residuals = y - (slope * x + intercept)
    
    eps_lag = residuals[:-1]
    eps_diff = np.diff(residuals)
    
    if np.std(eps_lag) == 0:
        return {'cointegrated': False, 'p_value': 1.0, 'beta': slope}
    
    rho_slope, _, _, rho_p, rho_se = stats.linregress(eps_lag, eps_diff)
    
    if rho_se > 0:
        t_stat = rho_slope / rho_se
    else:
        t_stat = 0
    
    # Approximate p-value (normal distribution; actual ADF uses non-standard distribution)
    approx_p = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    cointegrated = approx_p < alpha_level and rho_slope < 0
    
    return {
        'cointegrated': cointegrated,
        'beta': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        't_statistic': t_stat,
        'p_value': approx_p,
        'residual_std': np.std(residuals),
    }


# ============= 2. Z-score Trading Signal =============

def calculate_zscore(spread, lookback=30):
    """Rolling Z-score - prevents look-ahead bias.
    
    Walk-forward principle: at time t, only use data up to t-1 for Z-score.
    """
    z = np.zeros(len(spread))
    z[:lookback] = np.nan
    
    for t in range(lookback, len(spread)):
        window = spread[t-lookback:t]
        mean = np.mean(window)
        std = np.std(window)
        if std > 0:
            z[t] = (spread[t] - mean) / std
    
    return z


def generate_signals(zscore, entry_threshold=2.0, exit_threshold=0.5):
    """Generate trading signals.
    
    LONG SPREAD entry (buy BNB, sell ETH): Z_t < -entry_threshold
    SHORT SPREAD entry (sell BNB, buy ETH): Z_t > +entry_threshold
    Position exit: |Z_t| < exit_threshold
    """
    signals = np.zeros(len(zscore))
    position = 0
    
    for t in range(len(zscore)):
        if np.isnan(zscore[t]):
            continue
        
        if position == 0:
            if zscore[t] < -entry_threshold:
                position = 1
            elif zscore[t] > entry_threshold:
                position = -1
        else:
            if abs(zscore[t]) < exit_threshold:
                position = 0
            elif position == 1 and zscore[t] > entry_threshold:
                position = -1
            elif position == -1 and zscore[t] < -entry_threshold:
                position = 1
        
        signals[t] = position
    
    return signals


# ============= 3. Backtest =============

def run_backtest(prices_train, prices_test, 
                 lookback=30,
                 entry_threshold=2.0,
                 exit_threshold=0.5,
                 commission=0.001,   # 0.1% per trade
                 slippage=0.0015):   # 0.15% per trade
    """Walk-forward pair trading backtest with transaction costs."""
    coint_result = cointegration_test(prices_train['bnb'].values, prices_train['eth'].values)
    
    if not coint_result['cointegrated']:
        return {
            'cointegrated': False,
            'message': 'No cointegration in training period - backtest skipped',
            'beta': coint_result['beta'],
            'p_value': coint_result['p_value'],
        }
    
    beta = coint_result['beta']
    
    spread_test = prices_test['bnb'].values - beta * prices_test['eth'].values
    zscore_test = calculate_zscore(spread_test, lookback=lookback)
    signals = generate_signals(zscore_test, entry_threshold, exit_threshold)
    
    bnb_returns = np.diff(np.log(prices_test['bnb'].values))
    eth_returns = np.diff(np.log(prices_test['eth'].values))
    
    pair_returns = np.zeros(len(bnb_returns))
    for t in range(len(bnb_returns)):
        signal = signals[t]
        pair_returns[t] = signal * (bnb_returns[t] - beta * eth_returns[t])
    
    position_changes = np.diff(np.concatenate([[0], signals]))
    trade_costs = np.abs(position_changes) * (commission + slippage)
    pair_returns_after_costs = pair_returns - trade_costs[:len(pair_returns)]
    
    cumulative_returns = np.exp(np.cumsum(pair_returns_after_costs)) - 1
    cumulative_return_final = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0
    
    if np.std(pair_returns_after_costs) > 0:
        sharpe = np.mean(pair_returns_after_costs) / np.std(pair_returns_after_costs) * np.sqrt(365)
    else:
        sharpe = 0
    
    cum_max = np.maximum.accumulate(1 + cumulative_returns)
    drawdowns = (1 + cumulative_returns - cum_max) / cum_max
    max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
    
    if abs(max_drawdown) > 0:
        n_years = len(pair_returns_after_costs) / 365
        annualized_return = (1 + cumulative_return_final) ** (1/n_years) - 1 if n_years > 0 else 0
        calmar = annualized_return / abs(max_drawdown)
    else:
        calmar = float('inf')
    
    n_trades = int(np.sum(np.abs(position_changes) > 0))
    if len(pair_returns_after_costs) > 0:
        win_rate = np.sum(pair_returns_after_costs > 0) / len(pair_returns_after_costs)
    else:
        win_rate = 0
    
    return {
        'cointegrated': True,
        'beta': beta,
        'cointegration_p_value': coint_result['p_value'],
        'r_squared': coint_result['r_squared'],
        'cumulative_return': cumulative_return_final,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar,
        'win_rate': win_rate,
        'n_trades': n_trades,
        'n_days_test': len(pair_returns_after_costs),
    }


def walk_forward_split(prices, train_ratio=0.5):
    """50/50 split into in-sample (train) and out-of-sample (test)."""
    n = len(prices)
    train_end = int(n * train_ratio)
    return prices.iloc[:train_end], prices.iloc[train_end:]


# ============= Main Execution =============

def main():
    print("=" * 75)
    print("Phase 5 Pair Trading Backtest - Walk-Forward Validation")
    print("=" * 75)
    print()
    print("CAUTION: This is observational evidence based on interpolated daily data.")
    print("         Section 5.4 of the paper warns against trading strategy use.")
    print("         Subsequent versions will use real daily OHLCV data.")
    print()
    
    print("## 1. Daily Time Series Generation")
    df = generate_daily_series(seed=42)
    print(f"  - Period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"  - Total days: {len(df)}")
    print(f"  - BTC: ${df['btc'].iloc[0]:,.0f} -> ${df['btc'].iloc[-1]:,.0f}")
    print(f"  - ETH: ${df['eth'].iloc[0]:,.0f} -> ${df['eth'].iloc[-1]:,.0f}")
    print(f"  - BNB: ${df['bnb'].iloc[0]:,.0f} -> ${df['bnb'].iloc[-1]:,.0f}")
    print()
    
    print("## 2. Walk-Forward Split (50/50)")
    train, test = walk_forward_split(df)
    print(f"  - Train: {train.index[0].date()} to {train.index[-1].date()} ({len(train)} days)")
    print(f"  - Test:  {test.index[0].date()} to {test.index[-1].date()} ({len(test)} days)")
    print()
    
    print("## 3. Cointegration Test (Train Period)")
    coint_result = cointegration_test(train['bnb'].values, train['eth'].values)
    print(f"  - beta: {coint_result['beta']:.4f}")
    print(f"  - Intercept: {coint_result['intercept']:.4f}")
    print(f"  - R-squared: {coint_result['r_squared']:.4f}")
    print(f"  - ADF t-stat: {coint_result['t_statistic']:.4f}")
    print(f"  - p-value (approx): {coint_result['p_value']:.4f}")
    print(f"  - Cointegrated (alpha=0.05): {coint_result['cointegrated']}")
    print()
    
    print("## 4. Walk-Forward Backtest")
    result = run_backtest(train, test,
                          lookback=30,
                          entry_threshold=2.0,
                          exit_threshold=0.5,
                          commission=0.001,
                          slippage=0.0015)
    
    if not result['cointegrated']:
        print(f"  -> {result['message']}")
        return
    
    print(f"  - beta (from train): {result['beta']:.4f}")
    print(f"  - Test period: {result['n_days_test']} days")
    print(f"  - Number of trades: {result['n_trades']}")
    print(f"  - Cumulative return: {result['cumulative_return']*100:.2f}%")
    print(f"  - Sharpe ratio (annualized): {result['sharpe_ratio']:.2f}")
    print(f"  - Max Drawdown: {result['max_drawdown']*100:.2f}%")
    print(f"  - Calmar ratio: {result['calmar_ratio']:.2f}")
    print(f"  - Win rate: {result['win_rate']*100:.2f}%")
    print()
    
    print("## 5. Parameter Sensitivity (Threshold Variation)")
    print()
    scenarios = [
        (1.5, 0.5),
        (2.0, 0.5),
        (2.5, 0.5),
        (2.0, 0.0),
        (2.0, 1.0),
    ]
    print(f"{'Entry sigma':<14}{'Exit sigma':<12}{'Cumul Ret':<12}{'Sharpe':<10}{'Max DD':<10}{'N Trades':<10}")
    print("-" * 70)
    for entry, exit_ in scenarios:
        r = run_backtest(train, test,
                         lookback=30,
                         entry_threshold=entry,
                         exit_threshold=exit_,
                         commission=0.001,
                         slippage=0.0015)
        if r['cointegrated']:
            print(f"{entry:<14.1f}{exit_:<12.1f}{r['cumulative_return']*100:<12.2f}"
                  f"{r['sharpe_ratio']:<10.2f}{r['max_drawdown']*100:<10.2f}{r['n_trades']:<10}")
    print()
    
    print("=" * 75)
    print("Synthesis")
    print("=" * 75)
    print(f"""
1. Cointegration verified: BNB-ETH have cointegration relationship in train period
2. Pair trading performance: Sharpe {result['sharpe_ratio']:.2f}
3. Realistic costs reflected: 0.1% commission + 0.15% slippage = 0.25% per trade
4. Max Drawdown {result['max_drawdown']*100:.2f}% measure of high volatility tolerance

Important Caveats:
- This is daily simulation based on interpolated quarterly data
- Real daily OHLCV data should be used in subsequent versions for full backtest
- Korean tax (22% capital gains) is not reflected
- Out-of-sample period N={result['n_days_test']} days is small for statistical inference

Section 5.4 of the paper limits the BTC dominance pattern to *observational evidence*,
explicitly excluding *trading strategy verification*. This script is supplementary
exploration.

For full SSRN working paper subsequent versions, the following enhancements are needed:
- Real daily OHLCV data from CoinGecko/Binance API
- Walk-forward window rolling
- Multiple asset pairs (BTC-BNB, ETH-BNB, BTC-ETH)
- Bear market 2022 inclusion
- Korean residents tax considerations
""")


if __name__ == '__main__':
    main()
