# -*- coding: utf-8 -*-
"""
AMQS 골든 fixture 생성기.
실제 strategy.py 를 결정적 합성 데이터로 실행 → 입력 배열 + 원본 결과를 JSON 으로 덤프.
TS 테스트(test/strategy/amqs.test.ts)가 동일 입력으로 runAmqs() 를 돌려 결과를 대조한다.

실행: python3 test/fixtures/gen_amqs_fixture.py
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

AMQS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..",
        "Adaptive Momentum Quant Strategy (AMQS) for AI Infra", "script",
    )
)
sys.path.insert(0, AMQS_DIR)
import strategy as S  # noqa: E402

N = 320
rng = np.random.default_rng(42)
dates = pd.bdate_range("2025-01-01", periods=N)
tickers = S.AI_INFRA_TICKERS

data = {}
for i, t in enumerate(tickers):
    mu = float(rng.uniform(-0.0009, 0.0016))
    sig = float(rng.uniform(0.010, 0.030))
    rets = rng.normal(mu, sig, N)
    data[t] = 100.0 * np.cumprod(1.0 + rets)

prices = pd.DataFrame(data, index=dates)
qqq = pd.Series(100.0 * np.cumprod(1.0 + rng.normal(0.0005, 0.010, N)), index=dates)
vix = pd.Series(np.clip(18.0 + rng.normal(0.0, 3.0, N), 10.0, 40.0), index=dates)

# market caps: 하나는 사전필터(시총 미달) 트리거
caps = {t: 50e9 for t in tickers}
caps[tickers[0]] = 5e9

cfg = S.AMQSConfig()
regime = S.detect_regime(qqq, vix, cfg)
metrics = S.measure(prices, market=qqq)
S.apply_prefilter(metrics, cfg, caps)
S.score(metrics, cfg)
S.allocate(metrics, cfg, regime=regime.label)

ATTRS = [
    "ticker", "price", "subtheme",
    "factor_a_12_1", "factor_b_6_1", "factor_c_3_1", "factor_d_inv_vol",
    "ret_5d", "ret_20d", "ret_60d", "vol_60d", "sharpe_6m", "mdd_12m",
    "rsi_14", "dist_52w_high", "above_50dma", "above_200dma",
    "positive_months_12m", "max_single_day_drop_90d", "beta_qqq",
    "filtered_out", "z_factor_a", "z_factor_b", "z_factor_c", "z_factor_d",
    "four_factor_composite", "score_momentum", "score_pullback",
    "score_quality", "score_vol_alpha", "score_macro", "total_score_100",
    "selected", "signal", "weight",
]


def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, (np.floating,)):
        return clean(float(v))
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


rows = [{k: clean(getattr(m, k)) for k in ATTRS} for m in metrics]

out = {
    "meta": {"n": N, "seed": 42, "n_tickers": len(tickers)},
    "prices": {t: [float(x) for x in data[t]] for t in tickers},
    "qqq": [float(x) for x in qqq.values],
    "vix": [float(x) for x in vix.values],
    "marketCaps": caps,
    "regime": {
        "label": regime.label,
        "qqq_above_200ma": bool(regime.qqq_above_200ma),
        "vix_level": float(regime.vix_level),
        "qqq_5d_return": float(regime.qqq_5d_return),
    },
    "rows": rows,
}

dst = os.path.join(os.path.dirname(__file__), "amqs_golden.json")
with open(dst, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

sig_counts = {}
for r in rows:
    sig_counts[r["signal"]] = sig_counts.get(r["signal"], 0) + 1
print(f"wrote {dst}")
print(f"regime={regime.label}  signals={sig_counts}  selected={sum(1 for r in rows if r['selected'])}")
