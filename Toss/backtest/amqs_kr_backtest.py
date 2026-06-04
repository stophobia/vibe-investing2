#!/usr/bin/env python3
"""
amqs_kr_backtest.py
===================
국내 종목 대상 AMQS(Adaptive Momentum Quant Strategy) 3년 백테스트.

- 데이터: yfinance(야후 파이낸스) 수정종가. KOSPI=.KS / KOSDAQ=.KQ 자동 판별(2-pass).
- 전략: 4-Factor Composite 모멘텀 + 주간 리밸런싱 + 레짐 필터(KODEX 200) + -12% 트레일링 스탑.
- 벤치마크: KODEX 200 단순보유 / 동일가중 유니버스 단순보유.
- 산출: Toss/data/ 에 일간 NAV, 주간 리밸런싱 로그, 종목별 통계, 성과 요약 CSV.

주의: 결과는 가공 없이 그대로 기록한다. 모멘텀 전략은 구간에 따라 단순보유에 뒤질 수 있다.

Author: Dennis Kim (김호광) · vibe-investing · MIT
"""
from __future__ import annotations
import os, sys, warnings
from datetime import datetime
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
try:
    import yfinance as yf
except ImportError:
    sys.exit("yfinance 필요: pip install yfinance")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)

# ---- 유니버스 (Toss/src/universe.js 와 동일 구성) ----
SECTORS = {
    "반도체/AI": ["005930","000660","042700","000990","058470","039030","240810","036930","403870","399720"],
    "2차전지":   ["373220","006400","005490","247540","086520","003670","066970","096770","005070","121600"],
    "자동차":    ["005380","000270","012330","204320","161390","011210","005850","307950","018880","073240"],
    "인터넷/게임":["035420","035720","259960","036570","251270","293490","263750","112040","192080","194480"],
    "바이오":    ["207940","068270","000100","128940","326030","196170","141080","028300","214150","087010"],
    "방산/조선": ["012450","064350","079550","047810","329180","042660","010140","009540","010620","272210"],
    "금융":      ["105560","055550","086790","316140","138040","032830","000810","024110","006800","071050"],
    "엔터":      ["352820","035900","041510","122870","035760","253450","376300","036420","214320","034120"],
}
ETFS = ["069500","360750","133690","381180","379800","305720","102110","229200","396500","122630"]
NAMES = {  # 표기용(일부)
 "005930":"삼성전자","000660":"SK하이닉스","373220":"LG에너지솔루션","006400":"삼성SDI",
 "005380":"현대차","000270":"기아","035420":"NAVER","035720":"카카오","207940":"삼성바이오로직스",
 "068270":"셀트리온","012450":"한화에어로스페이스","064350":"현대로템","105560":"KB금융","352820":"하이브",
 "069500":"KODEX 200","360750":"TIGER 미국S&P500","133690":"TIGER 미국나스닥100","247540":"에코프로비엠",
}
BENCH = "069500"  # 레짐 벤치마크 = KODEX 200

ALL_CODES = sorted({c for v in SECTORS.values() for c in v} | set(ETFS) | {BENCH})
CODE2SECTOR = {c: s for s, v in SECTORS.items() for c in v}
for c in ETFS: CODE2SECTOR[c] = "ETF"

# ---- 백테스트 파라미터 ----
START_FETCH = "2022-05-01"     # 12개월 룩백 확보용
BT_START    = "2023-06-01"     # 백테스트 시작(약 3년)
TOP_N       = 10               # 보유 종목 수
COST        = 0.0020           # 왕복 거래비용 가정 0.20%/거래 (KR 개인 보수적)
STOP        = 0.12             # -12% 트레일링 스탑
INIT_CAP    = 100_000_000      # 초기자본 1억원
TRADING_DAYS = 252


def resolve_and_download(codes):
    """KS 우선, 실패 시 KQ 재시도. 반환: (close_df[code], ticker_map)"""
    def dl(suffix, cs):
        tks = [f"{c}.{suffix}" for c in cs]
        df = yf.download(tks, start=START_FETCH, auto_adjust=True, progress=False, group_by="column")
        if isinstance(df.columns, pd.MultiIndex):
            df = df["Close"]
        else:
            df = df.to_frame(name=f"{cs[0]}.{suffix}")
        return df

    print(f"[1/4] yfinance 다운로드 (KS) — {len(codes)}종목...")
    ks = dl("KS", codes)
    good, bad = {}, []
    for c in codes:
        col = f"{c}.KS"
        s = ks[col] if col in ks.columns else pd.Series(dtype=float)
        if s.dropna().shape[0] >= 300:
            good[c] = s.rename(c);
        else:
            bad.append(c)
    if bad:
        print(f"[2/4] KS 실패 {len(bad)}종목 → KQ 재시도...")
        kq = dl("KQ", bad)
        for c in bad:
            col = f"{c}.KQ"
            s = kq[col] if col in kq.columns else pd.Series(dtype=float)
            if s.dropna().shape[0] >= 300:
                good[c] = s.rename(c)
    close = pd.concat(good.values(), axis=1)
    close = close.sort_index().ffill()
    return close


def momentum_scores(close, asof):
    """asof 시점 4-factor composite z-score (보유 후보 횡단면)."""
    hist = close.loc[:asof]
    if len(hist) < 130:
        return pd.Series(dtype=float)
    last = hist.iloc[-1]
    def p_ago(n):
        idx = max(0, len(hist)-1-n)
        return hist.iloc[idx]
    p1, p3, p6, p12 = p_ago(21), p_ago(63), p_ago(126), p_ago(min(252, len(hist)-1))
    r12 = last/p12 - 1; r6 = last/p6 - 1; r3 = last/p3 - 1
    rets = hist.tail(61).pct_change().dropna()
    vol = rets.std()*np.sqrt(TRADING_DAYS)
    inv = 1/vol.replace(0, np.nan)
    def z(s):
        s = s.dropna()
        if len(s) < 5: return s*0
        return (s - s.mean())/(s.std(ddof=0) or 1)
    comp = (0.50*z(r12) + 0.30*z(r6) + 0.15*z(r3) + 0.05*z(inv))
    # 최소 데이터 요건: 12개월 수익률 계산 가능 종목만
    valid = r12.dropna().index
    return comp.reindex(valid).dropna().sort_values(ascending=False)


def regime(close, asof):
    """KODEX 200 기반 레짐: RISK_ON / RISK_OFF / DEFENSIVE."""
    s = close[BENCH].loc[:asof].dropna()
    if len(s) < 60: return "RISK_ON"
    now = s.iloc[-1]; ma200 = s.tail(200).mean()
    ret5 = now/s.iloc[-6]-1 if len(s) >= 6 else 0
    vol20 = s.tail(21).pct_change().dropna().std()*np.sqrt(TRADING_DAYS)
    if ret5 < -0.08: return "DEFENSIVE"
    if now < ma200 or vol20 > 0.30: return "RISK_OFF"
    return "RISK_ON"


def run_backtest(close):
    dates = close.loc[BT_START:].index
    fridays = [d for d in dates if d.weekday() == 4]  # 주간 리밸런싱(금)
    rebal_set = set(fridays)

    universe = [c for c in ALL_CODES if c != BENCH and c in close.columns]

    nav = INIT_CAP
    weights = {}                 # code -> weight
    entry_peak = {}              # code -> 보유중 최고가(스탑 기준)
    nav_hist, log_rows = [], []
    prev_close = close.iloc[0]

    for i, d in enumerate(dates):
        px = close.loc[d]
        # 1) 일간 수익 반영
        if i > 0 and weights:
            day_ret = 0.0
            for c, w in weights.items():
                if c in px and c in prev_close and prev_close[c] > 0 and not np.isnan(px[c]):
                    day_ret += w * (px[c]/prev_close[c] - 1)
            nav *= (1 + day_ret)
        prev_close = px

        # 2) 트레일링 스탑(보유분 중 고점대비 -12% 이탈 → 현금화)
        stopped = []
        for c in list(weights.keys()):
            if c in px and not np.isnan(px[c]):
                entry_peak[c] = max(entry_peak.get(c, px[c]), px[c])
                if px[c] <= entry_peak[c]*(1-STOP):
                    stopped.append(c)
        if stopped:
            turn = sum(weights[c] for c in stopped)
            nav *= (1 - turn*COST)
            for c in stopped:
                weights.pop(c, None); entry_peak.pop(c, None)

        # 3) 주간 리밸런싱
        if d in rebal_set:
            reg = regime(close, d)
            sc = momentum_scores(close[universe], d)
            sc = sc[sc.index.isin(px.dropna().index)]
            if reg == "DEFENSIVE":
                target = {}
            else:
                top = list(sc.head(TOP_N).index)
                gross = 0.5 if reg == "RISK_OFF" else 1.0
                w = (gross/len(top)) if top else 0
                target = {c: w for c in top}
            # 회전율 비용
            allc = set(target) | set(weights)
            turnover = sum(abs(target.get(c,0) - weights.get(c,0)) for c in allc)
            nav *= (1 - turnover*COST)
            # 신규 진입분 스탑 기준 초기화
            for c in target:
                if c not in weights:
                    entry_peak[c] = px[c] if (c in px and not np.isnan(px[c])) else entry_peak.get(c)
            weights = target
            log_rows.append({
                "date": d.strftime("%Y-%m-%d"), "regime": reg,
                "n_holdings": len(target), "turnover": round(turnover,3),
                "nav": round(nav,0),
                "holdings": ",".join(f"{c}({NAMES.get(c,c)})" for c in list(target)[:TOP_N]),
            })

        nav_hist.append((d, nav))

    nav_s = pd.Series({d: v for d, v in nav_hist}).sort_index()
    return nav_s, pd.DataFrame(log_rows)


def buyhold_equal(close):
    u = [c for c in ALL_CODES if c != BENCH and c in close.columns]
    sub = close[u].loc[BT_START:].ffill()
    rets = sub.pct_change().fillna(0)
    port = rets.mean(axis=1)  # 동일가중 일간수익
    return (1+port).cumprod()*INIT_CAP


def buyhold_single(close, code):
    s = close[code].loc[BT_START:].ffill()
    return s/s.iloc[0]*INIT_CAP


def metrics(nav):
    nav = nav.dropna()
    if len(nav) < 2: return {}
    total = nav.iloc[-1]/nav.iloc[0]-1
    yrs = (nav.index[-1]-nav.index[0]).days/365.25
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    rets = nav.pct_change().dropna()
    vol = rets.std()*np.sqrt(TRADING_DAYS)
    sharpe = (rets.mean()*TRADING_DAYS)/vol if vol>0 else 0
    mdd = (nav/nav.cummax()-1).min()
    calmar = cagr/abs(mdd) if mdd<0 else float("nan")
    return {"total_return_pct": round(total*100,1), "cagr_pct": round(cagr*100,2),
            "vol_pct": round(vol*100,1), "mdd_pct": round(mdd*100,1),
            "sharpe": round(sharpe,2), "calmar": round(calmar,2)}


def per_stock_stats(close):
    rows = []
    for c in [x for x in ALL_CODES if x != BENCH and x in close.columns]:
        s = close[c].loc[BT_START:].dropna()
        if len(s) < 50: continue
        m = metrics(s)
        rows.append({"code": c, "name": NAMES.get(c, c), "sector": CODE2SECTOR.get(c,""),
                     **m, "last_price": round(s.iloc[-1],0)})
    df = pd.DataFrame(rows).sort_values("cagr_pct", ascending=False)
    return df


def main():
    print("="*70); print("  AMQS 국내 3년 백테스트"); print("="*70)
    close = resolve_and_download(ALL_CODES)
    print(f"[3/4] 데이터 확보: {close.shape[1]}종목 · {close.index[0].date()}~{close.index[-1].date()}")
    if BENCH not in close.columns:
        sys.exit("KODEX 200(069500) 데이터 없음 — 중단")

    print("[4/4] 백테스트 실행...")
    nav_amqs, log = run_backtest(close)
    nav_kodex = buyhold_single(close, BENCH)
    nav_eqw = buyhold_equal(close)

    # 일간 NAV 정렬
    daily = pd.DataFrame({
        "AMQS": nav_amqs,
        "KODEX200_BuyHold": nav_kodex.reindex(nav_amqs.index).ffill(),
        "EqualWeight_BuyHold": nav_eqw.reindex(nav_amqs.index).ffill(),
    })
    daily.index.name = "date"
    daily.round(0).to_csv(os.path.join(DATA, "daily_nav.csv"))
    log.to_csv(os.path.join(DATA, "weekly_rebalance_log.csv"), index=False)

    # 성과 요약
    summ = pd.DataFrame({
        "AMQS": metrics(nav_amqs),
        "KODEX200_BuyHold": metrics(daily["KODEX200_BuyHold"]),
        "EqualWeight_BuyHold": metrics(daily["EqualWeight_BuyHold"]),
    }).T
    summ.index.name = "strategy"
    summ.to_csv(os.path.join(DATA, "performance_summary.csv"))

    pst = per_stock_stats(close)
    pst.to_csv(os.path.join(DATA, "per_stock_3y_stats.csv"), index=False)

    # 콘솔 출력
    print("\n=== 성과 요약 (백테스트", daily.index[0].date(), "~", daily.index[-1].date(), ") ===")
    print(summ.to_string())
    print(f"\n리밸런싱 횟수: {len(log)} · 레짐 분포:",
          dict(log["regime"].value_counts()) if len(log) else {})
    print("\n=== 상위/하위 종목(3년 CAGR) ===")
    print(pst.head(8)[["name","sector","cagr_pct","mdd_pct","total_return_pct"]].to_string(index=False))
    print("...")
    print(pst.tail(5)[["name","sector","cagr_pct","mdd_pct","total_return_pct"]].to_string(index=False))
    print(f"\nCSV 저장 위치: {os.path.relpath(DATA)}")
    print(" - daily_nav.csv / weekly_rebalance_log.csv / performance_summary.csv / per_stock_3y_stats.csv")


if __name__ == "__main__":
    main()
