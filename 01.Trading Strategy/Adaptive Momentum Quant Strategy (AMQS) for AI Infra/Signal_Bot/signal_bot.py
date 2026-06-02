#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMQS-AI-Infra 매수 시그널 봇
============================
AMQS-AI-Infra 전략 엔진(../script/strategy.py)을 그대로 호출해 **매수 시그널**을
산출하고 signals.json / signals.js 로 출력한다. index.html(정적 웹뷰)이 이 JSON 을
읽어 매수 후보·DIP_BUY 알림·거시 레짐·점수표를 대시보드로 렌더링한다.

매수 시그널 정의(웹뷰 'BUY'로 강조):
  CENTER / SATELLITE / TACTICAL / DIP_BUY  중 Top-N 에 선별(selected)되어 목표 비중>0 인 종목.
  (DIP_BUY = 단기 하락 매수, 별도 강조)

사용
----
    python signal_bot.py --period 2y --outdir .
    python signal_bot.py --mock --outdir .       # 네트워크 없이 로직 검증

면책: 연구·교육용 보조 지표이며 투자 권유가 아니다. 모든 신호는 참고용이고,
AI 인프라는 고변동·고베타 섹터로 실제 투자에는 상당한 리스크가 따른다.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ../script 를 import 경로에 추가 → 전략 엔진 재사용
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "script"
sys.path.insert(0, str(SCRIPT_DIR))

from strategy import (  # noqa: E402
    AMQSConfig, AI_INFRA_TICKERS, AI_INFRA_SUBTHEMES, MACRO_TICKERS,
    run_amqs_ai_infra,
)

TIER_LABEL = {
    "CENTER": "중심 매수",
    "SATELLITE": "위성 매수",
    "TACTICAL": "전술 매수",
    "DIP_BUY": "단기 하락 매수",
    "REDUCE": "비중 축소",
    "EXIT": "청산",
    "EXCLUDED": "필터 탈락",
}
BUY_TIERS = {"CENTER", "SATELLITE", "TACTICAL", "DIP_BUY"}


# --------------------------------------------------------------------------- #
# 데이터
# --------------------------------------------------------------------------- #
def fetch_prices(tickers, period="2y") -> pd.DataFrame:
    import yfinance as yf
    raw = yf.download(tickers=tickers, period=period, interval="1d",
                      auto_adjust=True, progress=False, group_by="ticker", threads=True)
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        if tickers[0] in lvl0:
            closes = pd.concat({t: raw[t]["Close"] for t in tickers if t in lvl0}, axis=1)
        else:
            closes = raw["Close"]
    else:
        closes = raw[["Close"]].rename(columns={"Close": tickers[0]})
    return closes.dropna(how="all")


def make_mock(period_years=3, seed=11):
    rng = np.random.default_rng(seed)
    n = period_years * 252
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    common = rng.normal(0.0006, 0.016, n)
    px = {}
    for i, t in enumerate(AI_INFRA_TICKERS):
        beta = 0.7 + (i % 5) * 0.25
        drift = 0.0004 + (i % 7) * 0.00015
        r = drift + beta * common + rng.normal(0, 0.018, n)
        px[t] = 50 * (1 + i * 0.1) * np.exp(np.cumsum(r))
    qqq = 380 * np.exp(np.cumsum(0.0004 + 0.9 * common + rng.normal(0, 0.006, n)))
    vix = 16 + 6 * np.abs(rng.normal(0, 1, n))
    prices = pd.DataFrame(px, index=idx)
    return prices, pd.Series(qqq, index=idx), pd.Series(vix, index=idx)


# --------------------------------------------------------------------------- #
def _row(r):
    return {
        "ticker": r["ticker"],
        "subtheme": r["subtheme"],
        "price": r["price"],
        "score": r["total_100"],
        "weight": r["weight"],
        "signal": r["signal"],
        "tier_label": TIER_LABEL.get(r["signal"], r["signal"]),
        "selected": bool(r.get("selected", False)),
        "factor_A_12_1": r["factor_A_12-1"],
        "factor_B_6_1": r["factor_B_6-1"],
        "ret_5d": r["ret_5d"],
        "ret_20d": r["ret_20d"],
        "rsi_14": r["rsi_14"],
        "dist_52w_high": r["dist_52w_high"],
        "above_200dma": bool(r["above_200dma"]),
        "s_momentum": r["score_momentum"],
        "s_pullback": r["score_pullback"],
        "s_quality": r["score_quality"],
        "s_vol_alpha": r["score_vol_alpha"],
        "reason": r["reason"],
    }


def build_payload(df: pd.DataFrame, regime, cfg: AMQSConfig, source: str, price_date: str):
    records = [_row(r) for _, r in df.iterrows()]
    buys = [x for x in records if x["signal"] in BUY_TIERS and x["weight"] > 0]
    buys.sort(key=lambda x: x["weight"], reverse=True)
    dip = [x for x in records if x["signal"] == "DIP_BUY"]
    exits = [x for x in records if x["signal"] == "EXIT"]
    watch = [x for x in records
             if x["signal"] not in BUY_TIERS and x["signal"] not in ("EXIT", "EXCLUDED")]

    invested = {"RISK_ON": 1.0, "RISK_OFF": 0.5, "DEFENSIVE": 0.0}.get(regime.label, 1.0)

    return {
        "schema": "amqs_ai_infra_signal_bot/1",
        "strategy": "AMQS-AI-Infra",
        "source": source,
        "generated_at": str(pd.Timestamp.utcnow().tz_localize(None)) + " UTC",
        "price_date": price_date,
        "regime": {
            "label": regime.label,
            "reason": regime.reason,
            "vix": round(regime.vix_level, 1),
            "qqq_5d": round(regime.qqq_5d_return, 4),
            "qqq_above_200ma": bool(regime.qqq_above_200ma),
            "invested_fraction": invested,
        },
        "config": {
            "top_n": cfg.top_n,
            "max_per_subtheme": cfg.max_per_subtheme,
            "stop_loss": cfg.stop_loss_from_entry,
            "weights": {
                "momentum": cfg.w_momentum_signal, "pullback": cfg.w_pullback_buy,
                "quality": cfg.w_trend_quality, "vol_alpha": cfg.w_vol_adj_alpha,
                "macro": cfg.w_macro_fit,
            },
        },
        "universe_subthemes": AI_INFRA_SUBTHEMES,
        "summary": {
            "n_buys": len(buys), "n_dip": len(dip), "n_exits": len(exits),
            "total_weight": round(sum(x["weight"] for x in buys), 4),
        },
        "buy_signals": buys,
        "dip_buys": dip,
        "exits": exits,
        "watchlist": watch,
        "all": records,
        "disclaimer": (
            "본 봇과 결과는 통계·기술적 모멘텀 신호에 기반한 연구·교육용 보조 지표이며, "
            "특정 종목의 매매를 권유하지 않는다. AI 인프라는 고변동·고베타 섹터로 종목 간 "
            "상관이 높아 분산 효과가 제한적이다. 모든 수치는 인샘플 강세장 특성과 레짐 의존성을 "
            "품고 있어 그대로 미래에 작동한다는 보장이 없으며, 실제 투자에는 원금 손실을 포함한 "
            "상당한 리스크가 따른다. 거래비용·세금·환전·슬리피지는 별도이며, 모든 투자 판단과 "
            "그 결과의 책임은 사용자 본인에게 있다."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="AMQS-AI-Infra 매수 시그널 봇")
    ap.add_argument("--period", default="2y")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    cfg = AMQSConfig()
    if args.mock:
        prices, qqq, vix = make_mock()
        source = "MOCK"
    else:
        prices = fetch_prices(AI_INFRA_TICKERS, period=args.period)
        macro = fetch_prices([MACRO_TICKERS["QQQ"], MACRO_TICKERS["VIX"]], period=args.period)
        qqq = macro[MACRO_TICKERS["QQQ"]] if MACRO_TICKERS["QQQ"] in macro else None
        vix = macro[MACRO_TICKERS["VIX"]] if MACRO_TICKERS["VIX"] in macro else None
        source = "yfinance"

    if prices.empty or prices.shape[0] < 260:
        print(f"ERROR: 가격 데이터 부족 ({0 if prices.empty else prices.shape[0]}일)")
        return 1

    df, regime = run_amqs_ai_infra(prices, qqq=qqq, vix=vix, config=cfg)
    price_date = str(prices.dropna(how="all").index[-1].date())
    payload = build_payload(df, regime, cfg, source, price_date)

    path = os.path.join(args.outdir, "signals.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # file:// 로 index.html 직접 열기용 JS 래퍼
    with open(os.path.join(args.outdir, "signals.js"), "w", encoding="utf-8") as f:
        f.write("window.SIGNALS = " + json.dumps(payload, ensure_ascii=False) + ";\n")

    # 콘솔 요약
    print(f"[signal_bot] source={source}  price_date={price_date}  regime={regime.label}")
    print(f"[buy] {payload['summary']['n_buys']}종목 매수 (총 {payload['summary']['total_weight']:.0%}), "
          f"DIP_BUY {payload['summary']['n_dip']}, EXIT {payload['summary']['n_exits']}")
    for b in payload["buy_signals"]:
        tag = " <DIP>" if b["signal"] == "DIP_BUY" else ""
        print(f"   {b['ticker']:<6} {b['subtheme']:<16} score {b['score']:>5.1f}  wt {b['weight']:>5.1%}  {b['tier_label']}{tag}")
    print(f"[out] {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
