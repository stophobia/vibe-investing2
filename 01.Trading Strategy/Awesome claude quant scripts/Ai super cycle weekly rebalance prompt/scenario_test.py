#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시나리오 검증 하니스 — 4위상 + 시장악화 + 급락 케이스에서
엔진이 의도대로 (목표 비중·액션) 반응하는지 확인.
"""
import json
from ai_supercycle_rebalancer import WeeklySignals, WeeklyEngine, Phase

BASE_WEIGHTS = {
    "NVDA": 52.0, "L1_other(SNDK+INTC)": 16.0,
    "MSFT": 0.0, "GOOGL": 0.0, "QQQ": 12.0, "CASH": 0.0,
}

SCENARIOS = {
    "1) ACCEL (현재, 가속)": dict(
        capex_yoy_growth=67, capex_yoy_growth_prev=62,
        hbm_leadtime_weeks=20, hbm_leadtime_prev=18, hbm_spot_mom=4,
        nvda_dc_qoq=22, nvda_dc_qoq_prev=22, nvda_inventory_mom=2, nvda_gpu_asp_qoq=1,
        market_stress=False, fed_hiking=False,
        nvda_drawdown_from_high=-8, hbm_proxy_drawdown=-10),

    "2) NEUTRAL (중립)": dict(
        capex_yoy_growth=40, capex_yoy_growth_prev=42,
        hbm_leadtime_weeks=16, hbm_leadtime_prev=16, hbm_spot_mom=0,
        nvda_dc_qoq=12, nvda_dc_qoq_prev=14, nvda_inventory_mom=4, nvda_gpu_asp_qoq=-1,
        market_stress=False, fed_hiking=False,
        nvda_drawdown_from_high=-12, hbm_proxy_drawdown=-15),

    "3) PEAK (정점: 재고증가+ASP하락)": dict(
        capex_yoy_growth=30, capex_yoy_growth_prev=40,
        hbm_leadtime_weeks=12, hbm_leadtime_prev=16, hbm_spot_mom=-6,
        nvda_dc_qoq=6, nvda_dc_qoq_prev=14, nvda_inventory_mom=12, nvda_gpu_asp_qoq=-7,
        market_stress=False, fed_hiking=False,
        nvda_drawdown_from_high=-15, hbm_proxy_drawdown=-18),

    "4) DOWN+급락 (하강, -32%)": dict(
        capex_yoy_growth=10, capex_yoy_growth_prev=30,
        hbm_leadtime_weeks=8, hbm_leadtime_prev=14, hbm_spot_mom=-12,
        nvda_dc_qoq=-5, nvda_dc_qoq_prev=6, nvda_inventory_mom=18, nvda_gpu_asp_qoq=-9,
        market_stress=True, fed_hiking=False,
        nvda_drawdown_from_high=-32, hbm_proxy_drawdown=-40),

    "5) DOWN 바닥+급락 (-46%, capex 안정)": dict(
        capex_yoy_growth=8, capex_yoy_growth_prev=9,
        hbm_leadtime_weeks=10, hbm_leadtime_prev=9, hbm_spot_mom=2,
        nvda_dc_qoq=-2, nvda_dc_qoq_prev=-4, nvda_inventory_mom=6, nvda_gpu_asp_qoq=-3,
        market_stress=True, fed_hiking=False,
        nvda_drawdown_from_high=-46, hbm_proxy_drawdown=-50),

    "6) FED 인상 전환": dict(
        capex_yoy_growth=35, capex_yoy_growth_prev=40,
        hbm_leadtime_weeks=15, hbm_leadtime_prev=16, hbm_spot_mom=-2,
        nvda_dc_qoq=10, nvda_dc_qoq_prev=14, nvda_inventory_mom=5, nvda_gpu_asp_qoq=-2,
        market_stress=False, fed_hiking=True,
        nvda_drawdown_from_high=-18, hbm_proxy_drawdown=-20),
}

def main():
    engine = WeeklyEngine()
    for name, kw in SCENARIOS.items():
        s = WeeklySignals(current_weights=dict(BASE_WEIGHTS), **kw)
        r = engine.run(s)
        print("=" * 70)
        print(name)
        print(f"  → 위상: {r['phase']}  (score={r['phase_detail']['composite_score']})")
        print(f"  → NVDA 목표: {r['targets']['NVDA']}%  | CASH 목표: {r['targets']['CASH']}%"
              f"  | L2(MSFT+GOOGL): {r['targets']['MSFT']+r['targets']['GOOGL']:.1f}%"
              f"  | L3: {r['targets']['L3(VRT 등)']}%")
        for a in r["actions"]:
            print(f"     [{a['side']:4}] {a['asset']:18} {a['delta_pct']:+5.1f}%p  · {a['reason']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
