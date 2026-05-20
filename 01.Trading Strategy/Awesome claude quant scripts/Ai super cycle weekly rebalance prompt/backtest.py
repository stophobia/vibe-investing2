#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Super Cycle — 전략 백테스트 v2 (몬테카를로 3-Way 비교)
========================================================

비교: A) DYNAMIC  B) QQQ_HOLD  C) NVDA_HOLD
시나리오: CONSERVATIVE(깊은 조정) / OPTIMAL(얕은 조정·강세지속)
방법: 몬테카를로 N회 평균 (단일경로 왜곡 제거)

⚠️ 합성 데이터 기반 *구조 비교* 시뮬레이션. 실제 수익 보장 아님.
실시간 가격 데이터 접근 불가 환경이라, NVDA/QQQ의 알려진 변동성·드로다운
특성을 반영한 합성 경로 위에서 전략 간 상대 성과를 비교합니다.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict

WEEKS = 156
DT = 1/52


@dataclass
class AssetParams:
    mu: float
    sigma: float


def make_path(p, weeks, dip_week, dip_depth, dip_len, rng):
    """GBM + 일시적 드로다운(dip) 후 회복."""
    prices = np.empty(weeks + 1); prices[0] = 100.0
    dip_mult = np.ones(weeks + 1)
    half = max(1, dip_len // 2)
    for i in range(dip_len):
        wk = dip_week + i
        if wk > weeks: break
        frac = (i/half) if i <= half else (2 - i/half)
        dip_mult[wk] = 1 + dip_depth*min(1.0, max(0.0, frac))
    for t in range(1, weeks + 1):
        z = rng.standard_normal()
        ret = (p.mu - 0.5*p.sigma**2)*DT + p.sigma*np.sqrt(DT)*z
        prices[t] = prices[t-1]*np.exp(ret)
    return prices*dip_mult


def scenario_params(kind):
    if kind == "CONSERVATIVE":
        return dict(nvda=AssetParams(0.30,0.50), qqq=AssetParams(0.12,0.20),
                    msft=AssetParams(0.15,0.24), googl=AssetParams(0.16,0.28),
                    dip_week=70, dip_depth=-0.45, dip_len=40, qqq_dip=-0.18, big_dip=-0.20)
    return dict(nvda=AssetParams(0.42,0.48), qqq=AssetParams(0.18,0.19),
                msft=AssetParams(0.22,0.23), googl=AssetParams(0.24,0.27),
                dip_week=85, dip_depth=-0.22, dip_len=24, qqq_dip=-0.10, big_dip=-0.10)


def build_paths(kind, rng):
    sp = scenario_params(kind)
    return {
        "NVDA": make_path(sp["nvda"], WEEKS, sp["dip_week"], sp["dip_depth"], sp["dip_len"], rng),
        "QQQ":  make_path(sp["qqq"],  WEEKS, sp["dip_week"], sp["qqq_dip"],  sp["dip_len"], rng),
        "MSFT": make_path(sp["msft"], WEEKS, sp["dip_week"], sp["big_dip"],  sp["dip_len"], rng),
        "GOOGL":make_path(sp["googl"],WEEKS, sp["dip_week"], sp["big_dip"],  sp["dip_len"], rng),
        "CASH": np.array([100.0*(1.04)**(t*DT) for t in range(WEEKS+1)]),
    }


@dataclass
class DynCfg:
    stress_cap: float = 0.35
    frac: float = 1/3
    dd1: float = -0.30
    dd2: float = -0.45
    buy: float = 0.03
    cash_base: float = 0.05
    cash_stress: float = 0.20
    fee: float = 0.001


def phase_of(nvda, t):
    if t < 8: return "NEUTRAL"
    mom = nvda[t]/nvda[t-8]-1
    peak = nvda[max(0,t-52):t+1].max()
    dd = nvda[t]/peak-1
    if dd <= -0.30: return "DOWN"
    if mom > 0.10:  return "ACCEL"
    if mom < -0.04: return "PEAK"
    return "NEUTRAL"


def run_dynamic(prices, init=1_000_000, cfg=DynCfg()):
    h = {"NVDA":0.52*init/prices["NVDA"][0],
         "QQQ":0.32*init/prices["QQQ"][0],
         "MSFT":0.0,"GOOGL":0.0,"CASH":0.0}
    curve=[]; fees=0.0
    anchor_map={"ACCEL":0.40,"NEUTRAL":0.325,"PEAK":0.28,"DOWN":0.25}
    tgt_l2_map={"ACCEL":0.15,"NEUTRAL":0.20,"PEAK":0.25,"DOWN":0.25}
    for t in range(WEEKS+1):
        val={k:h[k]*prices[k][t] for k in h}; port=sum(val.values()); curve.append(port)
        if t==WEEKS: break
        ph=phase_of(prices["NVDA"],t)
        peak=prices["NVDA"][max(0,t-52):t+1].max(); dd=prices["NVDA"][t]/peak-1
        stress=dd<=-0.25
        cur_w=val["NVDA"]/port
        anchor=anchor_map[ph]
        if stress: anchor=min(anchor,cfg.stress_cap)
        gap=anchor-cur_w; trade=gap*cfg.frac*port
        if ph=="DOWN":
            m8=prices["NVDA"][t]/prices["NVDA"][max(0,t-8)]-1
            if m8>-0.15 and dd<=cfg.dd1:
                trade+=cfg.buy*port
        if abs(trade)>port*0.005:
            f=abs(trade)*cfg.fee; fees+=f
            h["NVDA"]+=(trade-np.sign(trade)*f)/prices["NVDA"][t]
            if trade>0:
                cv=h["CASH"]*prices["CASH"][t]; pay=min(cv,trade)
                h["CASH"]-=pay/prices["CASH"][t]; rest=trade-pay
                if rest>0: h["QQQ"]-=rest/prices["QQQ"][t]
            else:
                freed=-trade; cur_l2=(val["MSFT"]+val["GOOGL"])/port
                need=max(0.0,(tgt_l2_map[ph]-cur_l2)*port); to_l2=min(freed,need)
                h["MSFT"]+=(to_l2*0.55)/prices["MSFT"][t]
                h["GOOGL"]+=(to_l2*0.45)/prices["GOOGL"][t]
                h["CASH"]+=(freed-to_l2)/prices["CASH"][t]
        val={k:h[k]*prices[k][t] for k in h}; port=sum(val.values())
        tgt_cash=cfg.cash_stress if stress else cfg.cash_base
        cgap=(tgt_cash-val["CASH"]/port)*0.5
        if cgap>0.005:
            mv=cgap*port; h["QQQ"]-=mv/prices["QQQ"][t]; h["CASH"]+=mv/prices["CASH"][t]
    return metrics("DYNAMIC",np.array(curve),fees,init)


def buy_hold(prices,name,init=1_000_000):
    u=init/prices[0]; return metrics(name,u*prices,0.0,init)


def metrics(name,curve,fees,init):
    tr=curve[-1]/init-1
    peak=np.maximum.accumulate(curve); mdd=((curve-peak)/peak).min()
    rets=np.diff(curve)/curve[:-1]
    sharpe=(rets.mean()/(rets.std()+1e-9))*np.sqrt(52)
    cagr=(curve[-1]/init)**(52/len(curve))-1
    return dict(name=name,total_return=tr,cagr=cagr,mdd=mdd,sharpe=sharpe,final=curve[-1],fees=fees)


def monte_carlo(kind,n=300):
    agg={k:{m:[] for m in ["total_return","cagr","mdd","sharpe"]}
         for k in ["DYNAMIC","QQQ_HOLD","NVDA_HOLD"]}
    for i in range(n):
        rng=np.random.default_rng(1000+i)
        p=build_paths(kind,rng)
        res={"DYNAMIC":run_dynamic(p),
             "QQQ_HOLD":buy_hold(p["QQQ"],"QQQ_HOLD"),
             "NVDA_HOLD":buy_hold(p["NVDA"],"NVDA_HOLD")}
        for k in res:
            for m in agg[k]: agg[k][m].append(res[k][m])
    return agg


def summarize(kind,n=300):
    agg=monte_carlo(kind,n)
    print("="*86)
    print(f"[{kind}] 몬테카를로 {n}회 평균 · 3년 · 초기 100만 단위")
    print("-"*86)
    print(f"{'전략':10} | {'총수익(중앙)':>11} | {'CAGR':>7} | {'MDD':>8} | {'Sharpe':>7} | {'QQQ초과승률':>10}")
    dyn=np.array(agg["DYNAMIC"]["total_return"])
    qqq=np.array(agg["QQQ_HOLD"]["total_return"])
    nv=np.array(agg["NVDA_HOLD"]["total_return"])
    for name,key,win in [("DYNAMIC","DYNAMIC",(dyn>qqq).mean()*100),
                         ("QQQ_HOLD","QQQ_HOLD",None),
                         ("NVDA_HOLD","NVDA_HOLD",(nv>qqq).mean()*100)]:
        a=agg[key]
        tr=np.median(a["total_return"])*100; cg=np.median(a["cagr"])*100
        md=np.median(a["mdd"])*100; sh=np.median(a["sharpe"])
        ws=f"{win:5.0f}%" if win is not None else "   —"
        print(f"{name:10} | {tr:10.1f}% | {cg:6.1f}% | {md:7.1f}% | {sh:6.2f} | {ws:>10}")
    print("="*86)
    return agg


if __name__=="__main__":
    for s in ["CONSERVATIVE","OPTIMAL"]:
        summarize(s,300)
