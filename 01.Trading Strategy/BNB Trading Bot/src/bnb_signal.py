#!/usr/bin/env python3
"""
================================================================
  BNB Trading Signal Generator — ETH 추세 추종 기반
================================================================
  분석 결과 기반 전략:
  - ETH MA(20) > ETH MA(50)  → BNB LONG
  - ETH MA(20) < ETH MA(50)  → CASH

  배경 통계 (2022-2026, n=1,460일):
    · BNB-ETH Pearson 상관 = 0.728
    · 비대칭 베타: ETH 음수일 β=0.70, 양수일 β=0.43 (p<0.0001)
    · ETH 골든크로스 → BNB 추종까지 중앙값 6일
    · ETH 데드크로스 → BNB 추종까지 중앙값 11일
    · HODLer 에어드롭 본격화 이후 BNB 베타 0.64 → 0.53 으로 감소

  사용법:
    python bnb_signal.py                # 현재 시그널 출력
    python bnb_signal.py --backtest     # 백테스트 + 결과 CSV 저장
    python bnb_signal.py --csv-only     # 신호 이력 CSV만 저장

  데이터 소스 (자동 시도 순서):
    1) yfinance (BNB-USD, ETH-USD)
    2) ccxt + Binance (BNBUSDT, ETHUSDT spot)
    3) CoinGecko REST API
================================================================
"""
import sys, os, argparse, json, time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# 데이터 소스 (Fallback chain)
# ---------------------------------------------------------------
def fetch_yfinance(days=1500):
    import yfinance as yf
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    bnb = yf.download("BNB-USD", start=start, end=end, progress=False, auto_adjust=True)
    eth = yf.download("ETH-USD", start=start, end=end, progress=False, auto_adjust=True)
    if bnb.empty or eth.empty:
        raise RuntimeError("yfinance returned empty")
    if isinstance(bnb.columns, pd.MultiIndex):
        bnb.columns = bnb.columns.get_level_values(0)
        eth.columns = eth.columns.get_level_values(0)
    out = pd.concat([bnb[['Close']].rename(columns={'Close':'BNB'}),
                     eth[['Close']].rename(columns={'Close':'ETH'})], axis=1).dropna()
    return out

def fetch_ccxt(days=1500):
    import ccxt
    ex = ccxt.binance()
    since = ex.milliseconds() - days * 24 * 3600 * 1000
    def ohlcv(sym):
        rows = []
        cur = since
        while True:
            chunk = ex.fetch_ohlcv(sym, '1d', since=cur, limit=1000)
            if not chunk: break
            rows.extend(chunk)
            cur = chunk[-1][0] + 24 * 3600 * 1000
            if len(chunk) < 1000: break
            time.sleep(0.2)
        df = pd.DataFrame(rows, columns=['ts','o','h','l','c','v'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        return df.set_index('ts')[['c']]
    bnb = ohlcv('BNB/USDT').rename(columns={'c':'BNB'})
    eth = ohlcv('ETH/USDT').rename(columns={'c':'ETH'})
    return pd.concat([bnb, eth], axis=1).dropna()

def fetch_coingecko(days=1500):
    """CoinGecko 무료 API. 365일까지만 일별 데이터 제공"""
    import urllib.request, urllib.parse
    days = min(days, 365)
    def get(coin):
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}&interval=daily"
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        df = pd.DataFrame(data['prices'], columns=['ts', 'price'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms').dt.normalize()
        return df.set_index('ts')[['price']]
    bnb = get('binancecoin').rename(columns={'price':'BNB'})
    eth = get('ethereum').rename(columns={'price':'ETH'})
    return pd.concat([bnb, eth], axis=1).dropna()

def get_prices(days=1500):
    last_err = None
    for name, fn in [('yfinance', fetch_yfinance), ('ccxt', fetch_ccxt), ('coingecko', fetch_coingecko)]:
        try:
            print(f"  [data] {name} 시도 중...")
            df = fn(days)
            print(f"  [data] {name} 성공: {len(df)} 일, {df.index.min().date()} ~ {df.index.max().date()}")
            return df
        except Exception as ex:
            print(f"  [data] {name} 실패: {ex}")
            last_err = ex
    raise RuntimeError(f"모든 데이터 소스 실패: {last_err}")

# ---------------------------------------------------------------
# 시그널 엔진
# ---------------------------------------------------------------
def compute_signals(prices, ma_short=20, ma_long=50, mom_window=7):
    df = prices.copy()
    df['ETH_MA_S'] = df['ETH'].rolling(ma_short).mean()
    df['ETH_MA_L'] = df['ETH'].rolling(ma_long).mean()
    df['ETH_mom']  = df['ETH'].pct_change(mom_window)
    df['ETH_trend'] = np.where(df['ETH_MA_S'] > df['ETH_MA_L'], 1, -1)
    df['signal_change'] = df['ETH_trend'].diff()

    df['action'] = ''
    df.loc[df['signal_change'] == +2, 'action'] = 'BUY'    # 골든크로스
    df.loc[df['signal_change'] == -2, 'action'] = 'SELL'   # 데드크로스

    # 포지션 (1=Long, 0=Cash)
    pos = 0
    positions = []
    for a in df['action'].fillna('').values:
        if a == 'BUY': pos = 1
        elif a == 'SELL': pos = 0
        positions.append(pos)
    df['position'] = positions
    return df

# ---------------------------------------------------------------
# 백테스트
# ---------------------------------------------------------------
def backtest(df, tx_cost=0.001):
    df = df.copy()
    df['pos_lag'] = df['position'].shift(1).fillna(0)
    df['BNB_ret'] = df['BNB'].pct_change()
    df['ETH_ret'] = df['ETH'].pct_change()
    df['strat_ret'] = df['pos_lag'] * df['BNB_ret']
    trade = (df['position'] != df['position'].shift(1)).astype(int)
    df['strat_ret_net'] = df['strat_ret'] - trade.shift(1).fillna(0) * tx_cost
    df = df.dropna(subset=['strat_ret_net'])
    df['eq_strat'] = (1 + df['strat_ret_net']).cumprod()
    df['eq_bnb']   = (1 + df['BNB_ret']).cumprod()
    df['eq_eth']   = (1 + df['ETH_ret']).cumprod()
    return df

def perf(returns, name):
    r = pd.Series(returns).dropna()
    if len(r) == 0: return {}
    total = (1 + r).prod() - 1
    cagr = (1 + total) ** (365 / len(r)) - 1
    vol = r.std() * np.sqrt(365)
    sharpe = (r.mean() * 365) / vol if vol > 0 else 0
    cum = (1 + r).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    win = (r[r != 0] > 0).mean() if (r != 0).any() else 0
    return {
        'name': name,
        'total_%': round(total*100, 2),
        'cagr_%': round(cagr*100, 2),
        'vol_%': round(vol*100, 2),
        'sharpe': round(sharpe, 3),
        'mdd_%': round(dd*100, 2),
        'win_%': round(win*100, 2),
    }

# ---------------------------------------------------------------
# 출력
# ---------------------------------------------------------------
def print_current(df):
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    eth_trend = "📈 UPTREND" if last['ETH_trend'] == 1 else "📉 DOWNTREND"
    pos_text = "🟢 LONG BNB" if last['position'] == 1 else "⚪ CASH"
    just_changed = (last['action'] != '') and (last['action'] != prev.get('action', ''))

    print("=" * 64)
    print(f"  BNB TRADING SIGNAL  —  {last.name.date()}")
    print("=" * 64)
    print(f"  BNB price       : ${last['BNB']:,.2f}")
    print(f"  ETH price       : ${last['ETH']:,.2f}")
    print(f"  ETH MA(20)      : ${last['ETH_MA_S']:,.2f}")
    print(f"  ETH MA(50)      : ${last['ETH_MA_L']:,.2f}")
    print(f"  ETH 7d momentum : {last['ETH_mom']*100:+.2f}%")
    print(f"  ETH trend       : {eth_trend}")
    print(f"  Position        : {pos_text}")
    if last['action']:
        print(f"  ⚡ TODAY ACTION : {last['action']}")
    elif just_changed:
        print(f"  ⚡ Recent action: {last['action']}")
    print()

    # 최근 시그널 5건
    actions = df[df['action'] != ''][['BNB','ETH','action']].tail(5)
    if len(actions) > 0:
        print("  최근 시그널:")
        for d, row in actions.iterrows():
            print(f"    {d.date()}  {row['action']:<5s}  BNB ${row['BNB']:>8,.2f}  ETH ${row['ETH']:>8,.2f}")
    print("=" * 64)

# ---------------------------------------------------------------
# 메인
# ---------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--backtest', action='store_true', help='백테스트 결과 CSV 저장')
    p.add_argument('--csv-only', action='store_true', help='시그널 이력만 CSV 저장')
    p.add_argument('--days', type=int, default=1500, help='데이터 기간 (일)')
    p.add_argument('--ma-short', type=int, default=20)
    p.add_argument('--ma-long', type=int, default=50)
    p.add_argument('--out', default='./bnb_signals')
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("📊 데이터 가져오는 중...")
    prices = get_prices(args.days)

    print("🔧 시그널 계산 중...")
    sig = compute_signals(prices, args.ma_short, args.ma_long)

    if args.csv_only:
        sig.to_csv(f"{args.out}/signals.csv")
        print(f"✅ 저장: {args.out}/signals.csv")
        return

    print_current(sig)

    if args.backtest:
        print("\n🔬 백테스트 실행 중...")
        bt = backtest(sig)
        print()
        for met in [perf(bt['strat_ret_net'], 'Strategy'),
                    perf(bt['BNB_ret'], 'BNB B&H'),
                    perf(bt['ETH_ret'], 'ETH B&H')]:
            print(f"  {met['name']:<10s}  Total {met['total_%']:>+8.2f}%  CAGR {met['cagr_%']:>+6.2f}%  "
                  f"Vol {met['vol_%']:>5.2f}%  Sharpe {met['sharpe']:>5.2f}  MDD {met['mdd_%']:>+7.2f}%")
        bt.to_csv(f"{args.out}/backtest.csv")
        sig[sig['action'] != ''].to_csv(f"{args.out}/signals_only.csv")
        print(f"\n✅ 저장:")
        print(f"   {args.out}/backtest.csv     (일별 백테스트 데이터)")
        print(f"   {args.out}/signals_only.csv (BUY/SELL 시그널 이력)")

if __name__ == "__main__":
    main()
