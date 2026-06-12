import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 섹터 ETF 매핑
SECTORS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Consumer Disc": "XLY",
    "Consumer Staples": "XLP",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE"
}

def fear_greed_score(etf, spy_returns_20d):
    data = yf.download(etf, period="60d", interval="1d")
    if len(data) < 30:
        return np.nan
    close = data['Close']
    
    # 1. RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(lower=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    rsi_score = np.clip((rsi - 30) / (70 - 30) * 100, 0, 100)  # 30→0, 70→100
    
    # 2. Price vs MA20
    ma20 = close.rolling(20).mean().iloc[-1]
    price = close.iloc[-1]
    pct_ma = (price / ma20 - 1) * 100
    ma_score = np.clip((pct_ma + 5) / 10 * 100, 0, 100)  # -5%→0, +5%→100
    
    # 3. Volatility ratio (IV proxy: historical vol)
    returns = close.pct_change().dropna()
    hist_vol_20d = returns.tail(20).std() * np.sqrt(252)
    hist_vol_60d = returns.tail(60).std() * np.sqrt(252) if len(returns)>=60 else hist_vol_20d
    vol_ratio = hist_vol_20d / hist_vol_60d
    vol_score = np.clip((1.2 - vol_ratio) / (1.2 - 0.8) * 100, 0, 100)  # >1.2→0, <0.8→100
    
    # 4. Sector momentum vs SPY
    sector_ret_20d = close.pct_change(20).iloc[-1] * 100
    spy_ret = spy_returns_20d  # precomputed
    rel_mom = sector_ret_20d - spy_ret
    # 상대적 순위 (지금은 단순 클리핑: -10%~+10% 범위)
    mom_score = np.clip((rel_mom + 10) / 20 * 100, 0, 100)
    
    # 5. Volume surge
    vol = data['Volume']
    avg_vol = vol.tail(20).mean()
    vol_surge = vol.iloc[-1] / avg_vol
    vol_score = np.clip((vol_surge - 0.7) / (1.5 - 0.7) * 100, 0, 100)
    
    # 가중 합산
    weights = [0.25, 0.20, 0.20, 0.20, 0.15]
    final = (rsi_score * weights[0] +
             ma_score * weights[1] +
             vol_score * weights[2] +
             mom_score * weights[3] +
             vol_score * weights[4])
    return final

def main():
    spy = yf.download("SPY", period="60d", interval="1d")
    spy_ret_20d = spy['Close'].pct_change(20).iloc[-1] * 100
    
    print("\n" + "="*60)
    print("미국 주식 섹터별 공포-탐욕 지표 (실시간)")
    print("미국 장 마감 기준 업데이트 | 데이터: Yahoo Finance")
    print("="*60)
    print(f"{'섹터':<15} {'점수':<8} {'상태'}")
    print("-"*60)
    
    for name, ticker in SECTORS.items():
        score = fear_greed_score(ticker, spy_ret_20d)
        if np.isnan(score):
            status = "데이터 부족"
        elif score < 40:
            status = "🔥 극단적 공포"
        elif score < 50:
            status = "😨 공포"
        elif score < 60:
            status = "😐 중립"
        elif score < 80:
            status = "😈 탐욕"
        else:
            status = "🤑 극단적 탐욕"
        print(f"{name:<15} {score:>5.1f}    {status}")
    print("="*60)
    
if __name__ == "__main__":
    main()
