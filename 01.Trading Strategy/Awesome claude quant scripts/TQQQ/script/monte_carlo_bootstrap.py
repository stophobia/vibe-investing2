#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Monte Carlo / Block Bootstrap — "HOLD vs PARTIAL" 우위 확률 정량화
================================================================================

목적
----
readme.md §5의 핵심 비판: "끝까지 보유(HOLD) 우위(151억 vs 107억)는 N=1 사후
경로의 결과론일 수 있다." 이를 정면으로 검증한다.

  -> 수천 개의 재표집/재생성 경로에서 다음을 추정한다:
     1. P(HOLD가 PARTIAL을 이길 확률)  — 세전/세후 각각
     2. 두 전략의 MOIC / IRR / MDD 분포 (p5~p95)
     3. P(원금 손실), P(반토막) 등 꼬리 위험

두 가지 경로 생성 방법
----------------------
- block bootstrap (--source yfinance):
    실제 QQQ 일간수익률을 블록 단위로 재표집. 변동성 군집(volatility clustering)과
    단기 자기상관을 보존하므로 IID 가정보다 현실적. **가장 의미 있는 모드.**
- parametric GBM (--source synthetic):
    regime(bull/sideways/crash)별 GBM 경로를 매 시뮬레이션마다 새로 생성.
    데이터 없이 메커니즘/꼬리위험을 보기 위한 스트레스 테스트용.

사용법
------
    pip install -r requirements.txt
    # 실제 데이터 블록 부트스트랩 (권장)
    python monte_carlo_bootstrap.py --source yfinance --start 2005-01-01 --n 1000 --block 21
    # 일본식 횡보 regime 몬테카를로
    python monte_carlo_bootstrap.py --source synthetic --regime sideways --n 500

주의: "LLM은 엑셀이지 오라클이 아니다." 확률은 가정(블록길이/regime/비용)에
      조건부다. 결론이 아니라 가정의 민감도를 읽는 도구로 사용하라.
================================================================================
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tqqq_rebalancing_backtest import (   # noqa: E402
    Config, run_backtest, load_synthetic, load_yfinance,
)


# ------------------------------------------------------------------ #
#  Block bootstrap (실제 수익률 재표집 — 의존성 보존)
# ------------------------------------------------------------------ #
def block_bootstrap(idx_ret: np.ndarray, rf: np.ndarray, target_len: int,
                    block: int, rng: np.random.Generator) -> pd.DataFrame:
    n = len(idx_ret)
    out_r = np.empty(target_len)
    out_f = np.empty(target_len)
    pos = 0
    while pos < target_len:
        start = int(rng.integers(0, n - block + 1))
        take = min(block, target_len - pos)
        out_r[pos:pos + take] = idx_ret[start:start + take]
        out_f[pos:pos + take] = rf[start:start + take]
        pos += take
    dates = pd.bdate_range('2005-01-03', periods=target_len)
    return pd.DataFrame({'idx_ret': out_r, 'rf': out_f}, index=dates)


# ------------------------------------------------------------------ #
#  Monte Carlo driver
# ------------------------------------------------------------------ #
def run_monte_carlo(args, cfg: Config) -> pd.DataFrame:
    rng = np.random.default_rng(args.seed)
    target_len = args.years * 252

    src_r = src_f = None
    if args.source == 'yfinance':
        hist = load_yfinance(args.start, args.end)
        src_r = hist['idx_ret'].to_numpy()
        src_f = hist['rf'].to_numpy()
        print(f"[bootstrap] 실제 QQQ {len(src_r)}일 표본에서 "
              f"블록(len={args.block}) 재표집 x {args.n}")
    else:
        print(f"[GBM] regime={args.regime} 경로 재생성 x {args.n} "
              f"(메커니즘/스트레스 — 결론 아님)")

    rows = []
    for s in range(args.n):
        if args.source == 'yfinance':
            prices = block_bootstrap(src_r, src_f, target_len, args.block, rng)
        else:
            prices = load_synthetic(args.years, seed=int(rng.integers(1, 2**31)),
                                    regime=args.regime)
        h = run_backtest(prices, cfg, 'hold')
        p = run_backtest(prices, cfg, 'partial')
        rows.append({
            'hold_gross': h['final_gross'], 'part_gross': p['final_gross'],
            'hold_net': h['final_net_if_liquidated'],
            'part_net': p['final_net_if_liquidated'],
            'hold_moic': h['moic'], 'part_moic': p['moic'],
            'hold_irr': h['irr_net'], 'part_irr': p['irr_net'],
            'hold_mdd': h['mdd'], 'part_mdd': p['mdd'],
        })
        if (s + 1) % max(1, args.n // 10) == 0:
            print(f"  ... {s + 1}/{args.n}")
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
#  Summary
# ------------------------------------------------------------------ #
def pct(series, qs=(5, 25, 50, 75, 95)):
    return {q: np.percentile(series, q) for q in qs}


def summarize(df: pd.DataFrame, cfg: Config):
    n = len(df)
    p_hold_gross = (df['hold_gross'] > df['part_gross']).mean()
    p_hold_net = (df['hold_net'] > df['part_net']).mean()
    p_loss_hold = (df['hold_moic'] < 1.0).mean()
    p_loss_part = (df['part_moic'] < 1.0).mean()
    p_half_hold = (df['hold_moic'] < 0.5).mean()
    p_half_part = (df['part_moic'] < 0.5).mean()

    print("\n" + "=" * 74)
    print(f"  MONTE CARLO 요약  (N = {n} paths)")
    print("=" * 74)
    print("  ▶ 핵심 질문: HOLD가 PARTIAL을 이길 확률")
    print(f"      P(HOLD > PARTIAL | 세전)     = {p_hold_gross*100:5.1f}%")
    print(f"      P(HOLD > PARTIAL | 세후청산) = {p_hold_net*100:5.1f}%   <- 세금 포함 공정비교")
    print("-" * 74)
    print(f"  ▶ 꼬리 위험 (원금 대비)")
    print(f"      P(손실, MOIC<1.0)   HOLD {p_loss_hold*100:5.1f}%  |  PARTIAL {p_loss_part*100:5.1f}%")
    print(f"      P(반토막, MOIC<0.5) HOLD {p_half_hold*100:5.1f}%  |  PARTIAL {p_half_part*100:5.1f}%")
    print("-" * 74)
    print(f"  ▶ 분포 (p5 / p25 / p50 / p75 / p95)")
    for label, col in (('MOIC  HOLD', 'hold_moic'), ('MOIC  PART', 'part_moic'),
                       ('IRR   HOLD', 'hold_irr'), ('IRR   PART', 'part_irr'),
                       ('MDD   HOLD', 'hold_mdd'), ('MDD   PART', 'part_mdd')):
        q = pct(df[col])
        if 'IRR' in label or 'MDD' in label:
            vals = "  ".join(f"{q[k]*100:6.1f}%" for k in (5, 25, 50, 75, 95))
        else:
            vals = "  ".join(f"{q[k]:6.2f}x" for k in (5, 25, 50, 75, 95))
        print(f"      {label}: {vals}")
    print("=" * 74)
    print("  해석: P(HOLD>PARTIAL)가 100%에서 멀수록, '끝까지 보유 우위'는")
    print("        보편 법칙이 아니라 '그 경로에서만' 성립한 결과론에 가깝다.")
    print("        LLM은 엑셀이지 오라클이 아니다 — 확률은 가정에 조건부다.")
    print("=" * 74 + "\n")

    return {
        'n': n, 'p_hold_gross': p_hold_gross, 'p_hold_net': p_hold_net,
        'p_loss_hold': p_loss_hold, 'p_loss_part': p_loss_part,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', choices=['yfinance', 'synthetic'], default='synthetic')
    ap.add_argument('--start', default='2005-01-01')
    ap.add_argument('--end', default=None)
    ap.add_argument('--regime', choices=['bull', 'sideways', 'crash'], default='bull')
    ap.add_argument('--n', type=int, default=500, help='시뮬레이션 경로 수')
    ap.add_argument('--years', type=int, default=20)
    ap.add_argument('--block', type=int, default=21, help='블록 길이(거래일), ~1개월')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--save', default=None, help='per-path 결과 CSV 저장 경로')
    args = ap.parse_args()

    cfg = Config()
    df = run_monte_carlo(args, cfg)
    summarize(df, cfg)

    if args.save:
        os.makedirs(os.path.dirname(args.save) or '.', exist_ok=True)
        df.to_csv(args.save, index=False)
        print(f"  per-path 결과 저장: {args.save}\n")


if __name__ == '__main__':
    main()
