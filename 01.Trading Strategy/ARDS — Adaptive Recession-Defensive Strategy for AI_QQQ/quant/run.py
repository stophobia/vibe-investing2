# -*- coding: utf-8 -*-
"""
ARDS-X — Runner
===============
전체 파이프라인을 실행하고 대시보드용 JSON 을 생성한다.

    python run.py                 # 기본 실행 → ../dashboard/data/latest.json
    python run.py --print         # 결과를 콘솔에도 요약 출력
    python run.py --out path.json # 출력 경로 지정

데이터는 전부 무료(yfinance + FRED CSV). 네트워크가 없으면 캐시로 폴백한다.
"""

import argparse
import datetime as dt
import json
import os
import sys

import config
import datafeed
import macro as macro_mod
import technical
import classifier


def build():
    # 1) 가격: 지수 + 복합체 + 거시 시장 프록시(국채금리/신용/구리·금/산업재)
    all_tickers = list(dict.fromkeys(
        list(config.INDICES) + list(config.COMPLEX) + config.MACRO_MARKET))
    px = datafeed.prices(all_tickers, config.LOOKBACK_DAYS)

    # 2) 거시 (FRED)
    fred = datafeed.fred_many(list(config.FRED_SERIES))
    macro = macro_mod.recession_composite(fred, px)

    # 3) 가격구조
    name_group = {**{t: (n, None) for t, n in config.INDICES.items()},
                  **{t: (n, g) for t, (n, g) in config.COMPLEX.items()}}
    index_px = {t: px[t] for t in config.INDICES if t in px}
    complex_px = {t: px[t] for t in config.COMPLEX if t in px}

    index_rows = technical.analyze_universe(index_px, name_group)
    complex_rows = technical.analyze_universe(complex_px, name_group)
    complex_agg = technical.aggregate(complex_rows)

    # 그룹별 집계
    groups = {}
    for g in config.GROUP_KR:
        gr = [r for r in complex_rows if r["group"] == g]
        if gr:
            groups[g] = {"label": config.GROUP_KR[g], **technical.aggregate(gr)}

    # 4) 분류
    verdict = classifier.classify(macro, index_rows, complex_rows, complex_agg)

    # 5) 직렬화
    asof = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    out = {
        "asof": asof,
        "title": "ARDS-X Regime Classifier",
        "subtitle": "미국 빅테크·AI 인프라 + S&P500·Nasdaq100 — 조정 / 과매도 / 하락 / 침체 판별",
        "verdict": verdict,
        "macro": macro,
        "indices": sorted(index_rows, key=lambda r: r["ticker"]),
        "complex": sorted(complex_rows, key=lambda r: r["decline_score"], reverse=True),
        "complex_aggregate": complex_agg,
        "groups": groups,
        "data_quality": {
            "macro_live": macro["n_live"],
            "macro_proxy": macro["n_proxy"],
            "macro_missing": macro["n_missing"],
            "n_prices": len(px),
            "n_expected": len(all_tickers),
        },
        "disclaimer": ("교육·연구용. 투자 권유 아님. 신호(레짐/Phase)만 참고하고 "
                       "실제 매매는 본인 판단·전문가 상담 필수. 방어 전략은 강세장에서 "
                       "기회비용을, 헤지는 잘못된 신호에서 휩쏘 손실을 낼 수 있다."),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--print", action="store_true", dest="do_print")
    args = ap.parse_args()

    out = build()

    out_path = args.out or os.path.join(os.path.dirname(__file__), config.OUTPUT_JSON)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    v = out["verdict"]
    print(f"[ARDS-X] {out['asof']}")
    print(f"  레짐: {v['state']}  ({v['state_kr']})   신뢰도 {v['confidence']}%")
    print(f"  거시 Composite: {out['macro']['composite']}  / Phase {out['macro']['phase']} "
          f"({out['macro']['phase_kr']})   [live {out['macro']['n_live']} · proxy {out['macro']['n_proxy']} · 결측 {out['macro']['n_missing']}]")
    print(f"  가격 스트레스: {v['axes']['price_stress']}  | 테이프 DD {v['evidence']['tape_drawdown']}% "
          f"| 200일선 위 {v['evidence']['breadth_above_200dma']}%")
    print(f"  → {v['headline']}")
    print(f"  → {v['handoff']}")
    print(f"  저장: {out_path}")

    if args.do_print:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
