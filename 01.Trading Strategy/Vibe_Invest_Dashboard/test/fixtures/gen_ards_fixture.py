# -*- coding: utf-8 -*-
"""
ARDS-X 골든 fixture 생성기.
실제 quant/{technical,macro,rates,classifier,run}.py 를 결정적 합성 데이터로 실행 →
입력(px/fred) + 모든 중간·최종 산출물을 JSON 으로 덤프. TS 가 동일 입력으로 대조.

datafeed(yfinance 의존)는 더미로 stub (macro/run 이 top-level import 만 함, 함수는 인자로 동작).

실행: python3 test/fixtures/gen_ards_fixture.py
"""
import json
import math
import os
import sys
import types

import numpy as np
import pandas as pd

ARDS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "ARDS — Adaptive Recession-Defensive Strategy for AI_QQQ", "quant",
    )
)
sys.path.insert(0, ARDS_DIR)
sys.modules["datafeed"] = types.ModuleType("datafeed")  # stub (함수 미사용)

import config        # noqa: E402
import technical     # noqa: E402
import macro as macro_mod   # noqa: E402
import rates         # noqa: E402
import classifier    # noqa: E402
import run           # noqa: E402

rng = np.random.default_rng(7)
N = 420
daily = pd.bdate_range("2024-09-01", periods=N)


def walk(start, mu, sig, n=N, index=daily):
    rets = rng.normal(mu, sig, n)
    return pd.Series(start * np.cumprod(1.0 + rets), index=index)


def level(center, sig, n=N, index=daily, lo=None, hi=None):
    v = center + np.cumsum(rng.normal(0.0, sig, n))
    if lo is not None or hi is not None:
        v = np.clip(v, lo if lo is not None else -1e9, hi if hi is not None else 1e9)
    return pd.Series(v, index=index)


# --- 가격 (px) -------------------------------------------------------------
px = {}
# 지수: 완만한 상승 + 최근 눌림
for t in config.INDICES:
    px[t] = walk(5000.0 if t == "^GSPC" else 18000.0, 0.0004, 0.009)
# 복합체 18종: 종목별 상이한 drift/vol
for i, t in enumerate(config.COMPLEX):
    px[t] = walk(100.0 + i, float(rng.uniform(-0.0006, 0.0014)), float(rng.uniform(0.012, 0.028)))
# 거시 시장 프록시
px["^TNX"] = level(4.2, 0.03, lo=2.0, hi=6.0)      # 10Y yield %
px["^IRX"] = level(4.6, 0.02, lo=2.0, hi=6.0)      # 3M
px["^FVX"] = level(4.0, 0.025, lo=2.0, hi=6.0)     # 5Y
px["HYG"] = walk(78.0, 0.0001, 0.004)
px["LQD"] = walk(110.0, 0.0001, 0.004)
px["IEF"] = walk(95.0, 0.0, 0.004)
px["CPER"] = walk(28.0, 0.0002, 0.012)
px["GLD"] = walk(240.0, 0.0005, 0.009)
px["XLI"] = walk(135.0, 0.0003, 0.009)
px["SPY"] = walk(560.0, 0.0004, 0.008)
px["^MOVE"] = level(100.0, 1.2, lo=60.0, hi=160.0)

# --- FRED (fred) -----------------------------------------------------------
monthly = pd.period_range("2022-06", periods=30, freq="M").to_timestamp()
weekly = pd.period_range("2024-01-01", periods=70, freq="W").to_timestamp()
weekly120 = pd.period_range("2023-09-01", periods=120, freq="W").to_timestamp()
fred = {}
fred["T10Y3M"] = level(0.3, 0.02, n=400, index=pd.bdate_range("2023-06-01", periods=400), lo=-1.2, hi=1.5)
fred["T10Y2Y"] = level(0.5, 0.02, n=400, index=pd.bdate_range("2023-06-01", periods=400), lo=-1.0, hi=1.5)
fred["UNRATE"] = pd.Series(np.clip(3.7 + np.cumsum(rng.normal(0.01, 0.05, 30)), 3.0, 6.0), index=monthly)
fred["BAMLH0A0HYM2"] = level(3.2, 0.03, n=400, index=pd.bdate_range("2023-06-01", periods=400), lo=2.0, hi=8.0)
fred["NFCI"] = level(-0.2, 0.01, n=120, index=weekly120, lo=-1.0, hi=1.0)
fred["ICSA"] = pd.Series(np.clip(220000 + np.cumsum(rng.normal(500, 4000, 70)), 150000, 400000), index=weekly)
fred["PERMIT"] = pd.Series(np.clip(1400 + np.cumsum(rng.normal(-3, 25, 30)), 1000, 1800), index=monthly)
fred["DGS2"] = level(4.3, 0.02, n=400, index=pd.bdate_range("2023-06-01", periods=400), lo=2.0, hi=6.0)
fred["T5YIE"] = level(2.3, 0.01, n=400, index=pd.bdate_range("2023-06-01", periods=400), lo=1.0, hi=4.0)

# --- 파이프라인 (run.build 와 동일 순서) -----------------------------------
macro_res = macro_mod.recession_composite(fred, px)
rate_res = rates.rate_stress(px, fred)

name_group = {**{t: (n, None) for t, n in config.INDICES.items()},
              **{t: (n, g) for t, (n, g) in config.COMPLEX.items()}}
index_px = {t: px[t] for t in config.INDICES if t in px}
complex_px = {t: px[t] for t in config.COMPLEX if t in px}
index_rows = technical.analyze_universe(index_px, name_group)
complex_rows = technical.analyze_universe(complex_px, name_group)
complex_agg = technical.aggregate(complex_rows)

today = "2026-06-06"
m = classifier._measure(macro_res, index_rows, complex_agg)
raw = classifier.raw_classify(macro_res["composite"], m, None)
state = {"committed": None, "since": None, "candidate": None, "count": 0}
committed, confirm = run._apply_hysteresis(raw, state, today)
verdict = classifier.build_verdict(committed, raw, confirm, macro_res, m, rate_res, today)

# --- 히스테리시스 시퀀스 골든 (상태머신 단독 검증) -------------------------
seq = ["UPTREND_HEALTHY", "CORRECTION", "CORRECTION", "OVERSOLD_BOUNCE",
       "CORRECTION", "CORRECTION", "CORRECTION", "UPTREND_HEALTHY"]
hyst_steps = []
st = {"committed": None, "since": None, "candidate": None, "count": 0}
for i, rraw in enumerate(seq):
    d = f"2026-06-{i+1:02d}"
    cm, cf = run._apply_hysteresis(rraw, st, d)
    hyst_steps.append({"day": d, "raw": rraw, "committed": cm, "confirm": cf})


def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, np.floating):
        return clean(float(v))
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.bool_):
        return bool(v)
    return v


def dump_series(s):
    s = s.dropna()
    return {"dates": [d.strftime("%Y-%m-%d") for d in s.index],
            "values": [float(x) for x in s.values]}


out = {
    "meta": {"n": N, "seed": 7},
    "px": {t: dump_series(s) for t, s in px.items()},
    "fred": {t: dump_series(s) for t, s in fred.items()},
    "macro": clean(macro_res),
    "rate": clean(rate_res),
    "index_rows": clean(index_rows),
    "complex_rows": clean(complex_rows),
    "complex_agg": clean(complex_agg),
    "measure": clean(m),
    "raw": raw,
    "confirm": clean(confirm),
    "verdict": clean(verdict),
    "hysteresis_seq": clean(hyst_steps),
}

dst = os.path.join(os.path.dirname(__file__), "ards_golden.json")
with open(dst, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"wrote {dst}")
print(f"verdict.state={verdict['state']} raw={raw} macro={macro_res['composite']} "
      f"phase={macro_res['phase']} rate={rate_res['score']} price_stress={m['price_stress']}")
print(f"macro live/proxy/missing={macro_res['n_live']}/{macro_res['n_proxy']}/{macro_res['n_missing']}")
