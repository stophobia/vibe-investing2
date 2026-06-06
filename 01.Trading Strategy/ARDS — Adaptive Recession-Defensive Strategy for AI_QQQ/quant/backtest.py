# -*- coding: utf-8 -*-
"""
ARDS-X — Backtest / 레짐 분류 정확도 검증
=========================================
"과거 시점에 ARDS-X 가 내렸을 분류가 실제로 맞았는가?" 를 검증한다.

방법:
  1. yfinance 로 ^NDX·^GSPC + 거시 시장 프록시의 전체 역사를 받는다 (FRED 불필요).
  2. 매 거래일, 그 시점까지의 데이터만으로(룩어헤드 금지) 거시·가격 축을 계산하고
     라이브 엔진과 동일한 우선순위 로직으로 5개 상태 중 하나로 분류한다.
  3. 평가:
     (a) 상태별 *향후 20/60일 수익률* — 조정/과매도는 +, 하락/침체는 - 여야 한다.
     (b) 레짐 스위치 전략 — risk-on {상승·조정·과매도} = NDX 롱, 방어 {하락·침체} = 현금
         → Buy&Hold 대비 CAGR / MDD / Sharpe 비교.
  4. CSV 2개 저장: backtest_state_stats.csv, backtest_equity.csv

거시 축은 역사적 FRED 가 없으므로 *시장 프록시*(수익률곡선 30% + ISM 15% + 신용 15%
= 가중치 60% 재정규화)로만 계산한다. 즉 실시간판보다 거시 정밀도는 낮다(노동/LEI 제외).
가격 축의 breadth(폭)도 단순화를 위해 ^NDX 자체 추세로 대체한다. 이 한계는 명시한다.

    python backtest.py                 # 2018~현재
    python backtest.py --start 2021-01-01
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

import config
import datafeed
import rates as rates_mod

T = config.TECH
D = config.DECISION


def _lin(x, lo, hi):
    if hi == lo:
        return pd.Series(50.0, index=x.index) if hasattr(x, "index") else 50.0
    return ((x - lo) / (hi - lo) * 100.0).clip(0, 100)


# --------------------------------------------------------------------------- #
# 지표 (벡터화)
# --------------------------------------------------------------------------- #
def rsi(s, p=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / p, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / p, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).fillna(50)


def bb_pctb(s, p=20, k=2):
    ma = s.rolling(p).mean()
    sd = s.rolling(p).std()
    return ((s - (ma - k * sd)) / ((2 * k * sd).replace(0, np.nan)))


def price_axis(px_close):
    """^NDX 종가 시계열 → 일별 가격구조 DataFrame (룩어헤드 없음)."""
    s = px_close.dropna()
    hi252 = s.rolling(252, min_periods=60).max()
    dd = (s / hi252 - 1) * 100
    ma20 = s.rolling(20).mean()
    ma50 = s.rolling(50).mean()
    ma200 = s.rolling(200, min_periods=120).mean()
    slope = (ma200 / ma200.shift(21) - 1) * 100
    r = rsi(s)
    pctb = bb_pctb(s)
    atr = s.diff().abs().ewm(alpha=1 / 14, adjust=False).mean().replace(0, np.nan)
    atr_stretch = (ma20 - s) / atr
    mom6 = (s / s.shift(126) - 1) * 100
    down = (s.diff() < 0)
    streak = down * (down.groupby((~down).cumsum()).cumcount() + 1)

    df = pd.DataFrame({
        "px": s, "dd": dd, "above200": s > ma200, "golden": ma50 > ma200,
        "slope": slope, "rsi": r, "pctb": pctb, "stretch": atr_stretch,
        "mom6": mom6, "streak": streak,
    })

    # 하락 점수 (live technical._decline_score 와 동일 공식)
    decline = (dd.mul(-1).div(T["dd_bear"]).mul(45)).clip(upper=45)
    decline += (~df["above200"]).astype(float) * 15
    decline += (~df["golden"]).astype(float) * 12
    decline += slope.where(slope < 0, 0).mul(-5).clip(upper=15)
    decline += mom6.where(mom6 < 0, 0).mul(-1).div(20).mul(13).clip(upper=13)
    df["decline"] = decline.clip(0, 100)

    # 과매도 점수
    os_ = pd.Series(0.0, index=s.index)
    os_ += ((T["rsi_oversold"] - r).div(T["rsi_oversold"] - 10).mul(45)
            ).where(r < T["rsi_oversold"], 0).clip(upper=45)
    os_ += np.where(pctb < T["bb_oversold"], 25, np.where(pctb < 0.2, 12, 0))
    os_ += atr_stretch.where(atr_stretch > 0, 0).div(T["atr_stretch"]).mul(20).clip(upper=20)
    os_ += streak.mul(2.5).clip(upper=10)
    df["oversold"] = os_.clip(0, 100)
    return df


def macro_axis(px):
    """시장 프록시로 일별 거시 Composite (가중치 60% 재정규화)."""
    parts = {}
    weights = {}
    # A 수익률곡선 (30%): ^TNX - ^IRX
    if "^TNX" in px and "^IRX" in px:
        spread = (px["^TNX"] - px["^IRX"]).dropna()
        parts["A"] = _lin(spread, 1.50, -0.50)
        weights["A"] = 0.30
    # C ISM 프록시 (15%): 구리/금 6M + 산업재/SPY 6M
    if "CPER" in px and "GLD" in px and "XLI" in px and "SPY" in px:
        cg = (px["CPER"] / px["GLD"]).dropna()
        cg6 = (cg / cg.shift(126) - 1) * 100
        rs = (px["XLI"] / px["SPY"]).dropna()
        rs6 = (rs / rs.shift(126) - 1) * 100
        c = (_lin(cg6, 15, -15) + _lin(rs6, 8, -8)) / 2
        parts["C"] = c
        weights["C"] = 0.15
    # E 신용 (15%): HYG/IEF 3M + HYG 드로다운
    if "HYG" in px and "IEF" in px:
        hi = (px["HYG"] / px["IEF"]).dropna()
        hi3 = (hi / hi.shift(63) - 1) * 100
        hyg = px["HYG"].dropna()
        hygdd = (hyg / hyg.rolling(252, min_periods=60).max() - 1) * 100
        e = (_lin(hi3, 4, -8) + _lin(hygdd, -1, -12)) / 2
        parts["E"] = e
        weights["E"] = 0.15

    if not parts:
        raise RuntimeError("거시 프록시 데이터 부족 — yfinance 확인 필요")

    idx = None
    for p in parts.values():
        idx = p.index if idx is None else idx.union(p.index)
    df = pd.DataFrame({k: v.reindex(idx).ffill() for k, v in parts.items()})
    wsum = sum(weights.values())
    comp = sum(df[k] * weights[k] for k in parts) / wsum
    return comp.rename("macro")


def rate_axis(px):
    """Rate Stress 프록시 (역사적, yfinance만): 10Y/5Y 20일 변화 + 10Y 실현변동성 백분위."""
    parts, weights = {}, {}
    if "^TNX" in px:
        s = px["^TNX"].dropna()
        bp = (s - s.shift(20)) * 100
        parts["R1"] = _lin(bp, 0.0, config.RATE["yield_vel_bp_hi"]); weights["R1"] = 0.35
        rv = s.pct_change().rolling(20).std() * np.sqrt(252) * 100
        rv_pct = rv.rolling(252, min_periods=120).apply(lambda x: (x <= x.iloc[-1]).mean() * 100, raw=False)
        parts["R4"] = rv_pct; weights["R4"] = 0.20
    if "^FVX" in px:
        s = px["^FVX"].dropna()
        bp = (s - s.shift(20)) * 100
        parts["R2"] = _lin(bp, 0.0, config.RATE["path_vel_bp_hi"]); weights["R2"] = 0.25
    if not parts:
        return None
    idx = None
    for p in parts.values():
        idx = p.index if idx is None else idx.union(p.index)
    dfp = pd.DataFrame({k: v.reindex(idx).ffill() for k, v in parts.items()})
    wsum = sum(weights.values())
    return (sum(dfp[k] * weights[k] for k in parts) / wsum).rename("rate")


# --------------------------------------------------------------------------- #
# 분류 (라이브 classifier 와 동일 우선순위 + 히스테리시스 밴드)
# --------------------------------------------------------------------------- #
def classify_row(macro, dd, above200, golden, decline, oversold, rsi_v):
    trend_broken = (not above200) or (not golden)
    is_os = (oversold >= 55) or (rsi_v < T["rsi_oversold"])
    if macro >= D["macro_recession"] and (dd <= -T["dd_correction"] or trend_broken):
        return "RECESSION_REBALANCE"
    if trend_broken and dd <= -T["dd_deep"]:
        return "DOWNTREND_DISTRIBUTION"
    if dd <= -T["dd_correction"]:
        return "OVERSOLD_BOUNCE" if is_os else "CORRECTION"
    if is_os:
        return "OVERSOLD_BOUNCE"
    return "UPTREND_HEALTHY"


def banded_classify_row(macro, dd, above200, golden, oversold, rsi_v, prev):
    """히스테리시스 진입/이탈 밴드를 적용한 raw 분류 (live classifier.raw_classify 와 동일)."""
    H = config.HYSTERESIS
    rec_thr = H["macro_rec_exit"] if prev == "RECESSION_REBALANCE" else H["macro_rec_enter"]
    dd_corr = H["dd_corr_exit"] if prev in ("CORRECTION", "OVERSOLD_BOUNCE") else H["dd_corr_enter"]
    dd_deep = H["dd_deep_exit"] if prev == "DOWNTREND_DISTRIBUTION" else H["dd_deep_enter"]
    rsi_thr = H["rsi_exit"] if prev == "OVERSOLD_BOUNCE" else H["rsi_enter"]
    trend_broken = (not above200) or (not golden)
    is_os = (oversold >= 55) or (rsi_v < rsi_thr)
    if macro >= rec_thr and (dd <= -dd_corr or trend_broken):
        return "RECESSION_REBALANCE"
    if trend_broken and dd <= -dd_deep:
        return "DOWNTREND_DISTRIBUTION"
    if dd <= -dd_corr:
        return "OVERSOLD_BOUNCE" if is_os else "CORRECTION"
    if is_os:
        return "OVERSOLD_BOUNCE"
    return "UPTREND_HEALTHY"


def hysteresis_pass(df):
    """밴드 + N일 확인 상태머신으로 committed 레짐 시퀀스를 산출."""
    confirm_days = config.HYSTERESIS["confirm_days"]
    committed = None
    candidate, count = None, 0
    raw_list, com_list = [], []
    for macro, dd, a2, g, osc, r in zip(
            df["macro"], df["dd"], df["above200"], df["golden"], df["oversold"], df["rsi"]):
        raw = banded_classify_row(macro, dd, a2, g, osc, r, committed)
        if committed is None:
            committed = raw
        elif raw == committed:
            candidate, count = None, 0
        else:
            if raw == candidate:
                count += 1
            else:
                candidate, count = raw, 1
            if count >= confirm_days:
                committed, candidate, count = raw, None, 0
        raw_list.append(raw)
        com_list.append(committed)
    return raw_list, com_list


def _confidence(macro, stress):
    c = 55
    c += 18 if ((macro >= D["macro_recession"]) == (stress >= 50)) else -5
    c += min(15, abs(macro - 50) / 50 * 15)
    c += min(12, abs(stress - 40) / 60 * 12)
    return max(20, min(95, c))


STATE_KR = {
    "UPTREND_HEALTHY": "정상 상승", "CORRECTION": "조정",
    "OVERSOLD_BOUNCE": "단기 과매도", "DOWNTREND_DISTRIBUTION": "하락/분배",
    "RECESSION_REBALANCE": "침체 리밸런싱",
}
RISK_ON = {"UPTREND_HEALTHY", "CORRECTION", "OVERSOLD_BOUNCE"}


# --------------------------------------------------------------------------- #
# 평가 지표
# --------------------------------------------------------------------------- #
def perf_stats(returns):
    """일간 수익률 시리즈 → CAGR, vol, Sharpe, MDD."""
    r = returns.dropna()
    if len(r) < 30:
        return {}
    nav = (1 + r).cumprod()
    yrs = len(r) / 252
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(252)
    sharpe = (r.mean() * 252) / vol if vol else 0
    mdd = (nav / nav.cummax() - 1).min()
    return {"CAGR": cagr, "vol": vol, "sharpe": sharpe, "mdd": mdd,
            "total": nav.iloc[-1] - 1, "nav": nav}


def run(start=None):
    tickers = list(dict.fromkeys(["^NDX", "^GSPC"] + config.MACRO_MARKET))
    px = datafeed.prices(tickers, lookback_days=3000)   # 최대 역사
    if "^NDX" not in px:
        sys.exit("^NDX 데이터를 받지 못했습니다.")

    pa = price_axis(px["^NDX"])
    ma = macro_axis(px)
    ra = rate_axis(px)

    df = pa.join(ma, how="inner").dropna(subset=["dd", "macro", "rsi"])
    if ra is not None:
        df = df.join(ra, how="left")
        df["rate"] = df["rate"].ffill()
    else:
        df["rate"] = float("nan")
    df = df[df.index >= "2007-01-01"]
    if start:
        df = df[df.index >= start]
    df = df[df["px"].notna()].copy()
    # 200일선/52주 고점이 성숙한 구간만
    df = df.dropna(subset=["decline", "oversold"])

    # raw(밴드 없음, 비교용) + committed(히스테리시스 적용)
    df["state_raw_nohyst"] = [
        classify_row(m, dd, a2, g, dec, osc, r)
        for m, dd, a2, g, dec, osc, r in zip(
            df["macro"], df["dd"], df["above200"], df["golden"],
            df["decline"], df["oversold"], df["rsi"])
    ]
    raw_banded, committed = hysteresis_pass(df)
    df["state_raw"] = raw_banded
    df["state"] = committed                       # 공식 레짐 = 히스테리시스 확정

    # 가격 스트레스 + 하락유형 라벨 + 신뢰도
    df["price_stress"] = (0.6 * df["decline"] +
                          0.4 * (-df["dd"] / T["dd_bear"] * 100).clip(0, 100)).clip(0, 100)
    df["decline_type"] = [
        rates_mod.decline_type(m, (None if pd.isna(rt) else rt), ps)["code"]
        for m, rt, ps in zip(df["macro"], df["rate"], df["price_stress"])
    ]
    df["conf"] = [_confidence(m, ps) for m, ps in zip(df["macro"], df["price_stress"])]

    # 향후 수익률
    fwd20 = df["px"].shift(-20) / df["px"] - 1
    fwd60 = df["px"].shift(-60) / df["px"] - 1
    df["fwd20"] = fwd20 * 100
    df["fwd60"] = fwd60 * 100

    # ---- (a) 상태별 통계 ----
    order = ["UPTREND_HEALTHY", "CORRECTION", "OVERSOLD_BOUNCE",
             "DOWNTREND_DISTRIBUTION", "RECESSION_REBALANCE"]
    rows = []
    for st in order:
        g = df[df["state"] == st]
        if len(g) == 0:
            continue
        rows.append({
            "state": st, "state_kr": STATE_KR[st], "days": len(g),
            "pct_of_time": round(len(g) / len(df) * 100, 1),
            "avg_fwd20_%": round(g["fwd20"].mean(), 2),
            "avg_fwd60_%": round(g["fwd60"].mean(), 2),
            "fwd60_hit_%": round((g["fwd60"] > 0).mean() * 100, 1),
        })
    stats = pd.DataFrame(rows)

    # ---- (b) 레짐 스위치 전략 (히스테리시스 적용된 committed 기준) ----
    ndx_ret = df["px"].pct_change()
    pos = df["state"].isin(RISK_ON).shift(1).fillna(False).astype(float)  # 익일 적용
    strat_ret = pos * ndx_ret
    bh = perf_stats(ndx_ret)
    strat = perf_stats(strat_ret)
    time_in = pos.mean() * 100

    # ---- (c) 히스테리시스: 휩쏘(레짐 전환 횟수) 감소 ----
    sw_nohyst = int((df["state_raw_nohyst"] != df["state_raw_nohyst"].shift(1)).sum())
    sw_hyst = int((df["state"] != df["state"].shift(1)).sum())

    # ---- (d) 하락유형 라벨 분포 (가격 스트레스 구간만) ----
    dt_rows = []
    stressed = df[df["price_stress"] >= config.RATE["label_min_stress"]]
    for code in ["RECESSION_DRIVEN", "RATE_DRIVEN", "VALUATION_DRIVEN"]:
        gg = stressed[stressed["decline_type"] == code]
        if len(gg):
            dt_rows.append({"decline_type": code,
                            "kr": rates_mod.DECLINE_TYPES[code][0], "days": len(gg),
                            "avg_fwd20_%": round(gg["fwd20"].mean(), 2),
                            "avg_fwd60_%": round(gg["fwd60"].mean(), 2)})
    dtypes = pd.DataFrame(dt_rows)

    # ---- (e) 신뢰도 캘리브레이션 (Brier) ----
    #   "행동이 옳았나"를 fwd20 으로 정의: risk-on→상승, 방어→하락이면 정답.
    correct = df.apply(
        lambda x: (x["fwd20"] > 0) if x["state"] in RISK_ON else (x["fwd20"] < 0), axis=1
    ).astype(float)
    p = df["conf"] / 100.0
    valid = df["fwd20"].notna()
    brier = float(((p[valid] - correct[valid]) ** 2).mean())
    cal_rows = []
    for lo, hi in [(20, 50), (50, 60), (60, 70), (70, 80), (80, 95)]:
        mask = valid & (df["conf"] >= lo) & (df["conf"] < (hi if hi < 95 else 96))
        if mask.sum() >= 20:
            cal_rows.append({"conf_bin": f"{lo}-{hi}%", "n": int(mask.sum()),
                             "predicted_%": round(p[mask].mean() * 100, 1),
                             "actual_%": round(correct[mask].mean() * 100, 1)})
    calib = pd.DataFrame(cal_rows)

    # ---- 저장 ----
    here = os.path.dirname(__file__)
    stats.to_csv(os.path.join(here, "backtest_state_stats.csv"), index=False)
    if len(calib):
        calib.to_csv(os.path.join(here, "backtest_calibration.csv"), index=False)
    if len(dtypes):
        dtypes.to_csv(os.path.join(here, "backtest_decline_types.csv"), index=False)
    eq = pd.DataFrame({
        "state": df["state"], "state_kr": df["state"].map(STATE_KR),
        "decline_type": df["decline_type"], "macro": df["macro"].round(1),
        "rate": df["rate"].round(1), "ndx_dd": df["dd"].round(1),
        "conf": df["conf"].round(0),
        "nav_buyhold": bh["nav"].reindex(df.index).round(4),
        "nav_strategy": strat["nav"].reindex(df.index).round(4),
    })
    eq.to_csv(os.path.join(here, "backtest_equity.csv"))

    # ---- 출력 ----
    print(f"[ARDS-X Backtest] {df.index[0].date()} ~ {df.index[-1].date()}  ({len(df)} 거래일)")
    print("\n(a) 상태별 향후 수익률 — 조정/과매도는 +, 하락/침체는 - 여야 정상")
    print(stats.to_string(index=False))
    print("\n(b) 레짐 스위치 전략 vs Buy&Hold(^NDX)")
    def fmt(s):
        return (f"  total {s['total']*100:7.1f}%  CAGR {s['CAGR']*100:6.1f}%  "
                f"vol {s['vol']*100:5.1f}%  Sharpe {s['sharpe']:.2f}  MDD {s['mdd']*100:6.1f}%")
    print("  Buy&Hold :" + fmt(bh))
    print("  ARDS-X   :" + fmt(strat) + f"  (시장노출 {time_in:.0f}%)")
    print(f"\n(c) 히스테리시스 — 레짐 전환 횟수(휩쏘): "
          f"밴드없음 {sw_nohyst}회 → 히스테리시스 {sw_hyst}회 "
          f"({(1 - sw_hyst / sw_nohyst) * 100:.0f}% 감소)")
    if len(dtypes):
        print("\n(d) 하락유형 라벨 분포 (가격 스트레스 구간) — 금리형은 향후수익이 더 약해야 정상")
        print(dtypes.to_string(index=False))
    if len(calib):
        print(f"\n(e) 신뢰도 캘리브레이션 (Brier={brier:.3f}; 0=완벽) — predicted ≈ actual 이면 잘 보정됨")
        print(calib.to_string(index=False))
    print(f"\n저장: backtest_state_stats.csv · backtest_equity.csv · "
          f"backtest_calibration.csv · backtest_decline_types.csv")
    return stats, bh, strat, time_in


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=None)
    args = ap.parse_args()
    run(args.start)
