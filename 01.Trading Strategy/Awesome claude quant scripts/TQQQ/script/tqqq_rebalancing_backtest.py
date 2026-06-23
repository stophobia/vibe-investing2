#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
NASDAQ-100 Leverage Rebalancing Backtest Engine (QLD DCA + TQQQ Trigger)
나스닥 100 레버리지 리밸런싱 백테스트 엔진
================================================================================

전략 요약
---------
1) 월 적립: 매달 투자금의 80% -> QLD(2x) 매수, 20% -> Cash Pool(SGOV) 적립
2) 현금 운용: Cash Pool은 SGOV(초단기 국채) 수익률(rf - 0.09% ER)로 증식
3) 하락장 6단계 트리거: QQQ 전고점 대비 낙폭(MDD)이 단계를 통과할 때마다
   '그 시점 현금풀' 기준 비중으로 TQQQ(3x) 매수. 신고가 갱신 시 트리거 리셋.
4) 매도 전략 비교: (A) 끝까지 보유  vs  (B) 트리거 물량 분할 매도

핵심 모델링 포인트 (LLM 퀀트 — "LLM은 엑셀이지 오라클이 아니다")
----------------------------------------------------------------
- TQQQ/QLD는 상장 기간이 짧아(QLD 2006, TQQQ 2010) 20년 백테스트가 불가능.
  따라서 QQQ(또는 ^NDX) 일간수익률에서 레버리지 ETF를 '일일복리'로 합성한다.
  이 합성 과정이 변동성 잠식(Volatility Decay)과 차입비용을 자동으로 반영한다.

      r_lev(t) = L * r_idx(t)
                 - (L-1) * (rf_annual + spread) / 252   # 차입(financing) 비용
                 - expense_ratio / 252                  # 운용보수
                 NAV_lev(t) = NAV_lev(t-1) * (1 + r_lev(t))

- 세금: 한국 해외주식 양도소득세 22%(20%+지방세 2%), 연 250만원 기본공제.
  '매도(실현)'한 해에만 과세. 끝까지 보유 시 과세이연(tax deferral) 발생.

주의(NOT an oracle)
-------------------
- 이 결과는 '과거 한 개의 실현 경로(N=1)'에 대한 사후(ex-post) 결과다.
  나스닥의 20년 우상향은 결과론(survivorship)일 수 있으며, 일본식 장기횡보가
  재현되면 이 전략은 가장 위험한 선택이 된다. (--regimes 옵션으로 스트레스 테스트)
- FX(USD/KRW)는 단일통화 가정으로 생략했다. 실제 원화 손익에는 환변동이 추가된다.

사용법
------
    # 1) 실제 데이터 (인터넷 필요: yfinance)
    pip install -r requirements.txt
    python tqqq_rebalancing_backtest.py --source yfinance --start 2005-01-01

    # 2) 데이터 없이 메커니즘 검증 (합성 GBM 경로, 재현 가능 seed)
    python tqqq_rebalancing_backtest.py --source synthetic --seed 42

    # 3) 일본식 장기횡보 스트레스 테스트
    python tqqq_rebalancing_backtest.py --source synthetic --regime sideways

================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


# ------------------------------------------------------------------ #
#  Configuration
# ------------------------------------------------------------------ #
@dataclass
class Config:
    # 월 적립 배분
    monthly_contribution: float = 1_000_000.0   # 월 적립금 (단일통화 단위, 예: KRW)
    qld_weight: float = 0.80                     # 적립금 중 QLD 매수 비중
    cash_weight: float = 0.20                    # 적립금 중 Cash Pool 적립 비중

    # 레버리지/비용 (연율)
    qld_leverage: float = 2.0
    tqqq_leverage: float = 3.0
    qld_expense: float = 0.0095                  # QLD ER ~0.95%
    tqqq_expense: float = 0.0084                 # TQQQ ER ~0.84%
    financing_spread: float = 0.0050             # 차입 스프레드 50bp (기준금리 위에)
    sgov_expense: float = 0.0009                 # SGOV ER ~0.09%

    # 하락 6단계 트리거: (전고점 대비 낙폭, 그 시점 현금풀 투입 비중)
    triggers: tuple = field(default_factory=lambda: (
        (-0.10, 0.20),
        (-0.15, 0.30),
        (-0.20, 0.50),
        (-0.25, 0.60),
        (-0.30, 0.70),
        (-0.35, 0.80),
    ))

    # 분할 매도 전략 (B): TQQQ 개별 매수분(lot)이 이 수익률 도달 시 매도
    partial_sell_gain: float = 0.40              # +40%에서 익절(20~60% 구간의 중앙값)

    # 세금: 한국 해외주식 양도세
    cap_gains_tax: float = 0.22                  # 20% + 지방세 2%
    annual_deduction: float = 2_500_000.0        # 연 250만원 기본공제

    trading_days: int = 252


# ------------------------------------------------------------------ #
#  Leveraged ETF synthesis  (변동성 잠식이 여기서 자동 발생)
# ------------------------------------------------------------------ #
def synth_leverage(idx_ret: pd.Series, rf_annual: pd.Series, lev: float,
                   expense: float, spread: float, td: int) -> pd.Series:
    """일간 인덱스 수익률 -> 레버리지 ETF 일간 수익률(일일복리 모델)."""
    financing = (lev - 1.0) * (rf_annual + spread) / td
    daily_cost = financing + expense / td
    return lev * idx_ret - daily_cost


# ------------------------------------------------------------------ #
#  Money-weighted return (XIRR)  — DCA에 맞는 연환산 수익률
# ------------------------------------------------------------------ #
def xirr(cashflows: list[tuple[pd.Timestamp, float]], guess: float = 0.1) -> float:
    """불규칙 시점 현금흐름의 내부수익률(연율). 이분법으로 안정적으로 해를 찾음."""
    if not cashflows:
        return float('nan')
    t0 = cashflows[0][0]
    days = np.array([(t - t0).days / 365.25 for t, _ in cashflows])
    amts = np.array([a for _, a in cashflows], dtype=float)

    def npv(r):
        return np.sum(amts / (1.0 + r) ** days)

    lo, hi = -0.999, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if np.isnan(f_lo) or np.isnan(f_hi) or f_lo * f_hi > 0:
        return float('nan')
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ #
#  Tax lots
# ------------------------------------------------------------------ #
@dataclass
class Lot:
    shares: float
    cost: float          # 총 취득원가 (단일통화)


class Position:
    """주식 수와 lot(취득원가) 단위 추적. 세금 계산을 위해 lot별 관리."""
    def __init__(self):
        self.lots: list[Lot] = []

    @property
    def shares(self) -> float:
        return sum(l.shares for l in self.lots)

    def buy(self, shares: float, price: float):
        if shares > 0:
            self.lots.append(Lot(shares, shares * price))

    def value(self, price: float) -> float:
        return self.shares * price

    def sell_lots_at_gain(self, price: float, gain_threshold: float) -> tuple[float, float]:
        """수익률이 threshold 이상인 lot 전량 매도.
        반환: (매도대금 proceeds, 실현이익 realized_gain)."""
        proceeds = 0.0
        realized = 0.0
        keep: list[Lot] = []
        for l in self.lots:
            avg = l.cost / l.shares if l.shares else 0.0
            if avg > 0 and (price / avg - 1.0) >= gain_threshold:
                proceeds += l.shares * price
                realized += l.shares * price - l.cost
            else:
                keep.append(l)
        self.lots = keep
        return proceeds, realized


# ------------------------------------------------------------------ #
#  Core backtest
# ------------------------------------------------------------------ #
def run_backtest(prices: pd.DataFrame, cfg: Config, exit_mode: str) -> dict:
    """
    prices: index=DatetimeIndex, columns=['idx_ret', 'rf'] (rf=연율 무위험수익률)
    exit_mode: 'hold' (끝까지 보유) | 'partial' (분할 매도)
    """
    # 레버리지/현금 ETF NAV 합성 (1.0에서 시작하는 가격지수)
    qld_ret = synth_leverage(prices['idx_ret'], prices['rf'], cfg.qld_leverage,
                             cfg.qld_expense, cfg.financing_spread, cfg.trading_days)
    tqqq_ret = synth_leverage(prices['idx_ret'], prices['rf'], cfg.tqqq_leverage,
                              cfg.tqqq_expense, cfg.financing_spread, cfg.trading_days)
    sgov_ret = (prices['rf'] - cfg.sgov_expense) / cfg.trading_days

    # numpy 배열로 추출 (일별 루프에서 .iloc 스칼라 조회는 매우 느림 -> MC 가속)
    qld_px = np.asarray((1.0 + qld_ret).cumprod(), dtype=float)
    tqqq_px = np.asarray((1.0 + tqqq_ret).cumprod(), dtype=float)
    qqq_px = np.asarray((1.0 + prices['idx_ret']).cumprod(), dtype=float)  # 트리거 판정용
    sgov_a = np.asarray(sgov_ret, dtype=float)
    idx = prices.index
    years = idx.year.to_numpy()
    months = idx.month.to_numpy()
    n = len(idx)

    qld = Position()
    tqqq = Position()
    cash = 0.0                       # SGOV에 들어있는 현금풀 (가치)
    invested = 0.0                   # 누적 납입 원금
    tax_paid = 0.0
    realized_ytd = 0.0               # 올해 실현이익 누적

    peak = qqq_px[0]
    triggers_fired = [False] * len(cfg.triggers)
    equity_curve = np.empty(n, dtype=float)
    cashflows: list[tuple[pd.Timestamp, float]] = []   # (date, amount) for IRR
    current_month = None
    current_year = years[0]
    is_partial = (exit_mode == 'partial')

    for i in range(n):
        qpx, tpx, gpx = qld_px[i], tqqq_px[i], qqq_px[i]

        # --- SGOV 현금풀 일일 증식 ---
        if i > 0:
            cash *= (1.0 + sgov_a[i])

        # --- 월초 적립 (월이 바뀌는 첫 거래일) ---
        ym = (years[i], months[i])
        if ym != current_month:
            current_month = ym
            contrib = cfg.monthly_contribution
            invested += contrib
            cashflows.append((idx[i], -contrib))
            qld.buy((contrib * cfg.qld_weight) / qpx, qpx)
            cash += contrib * cfg.cash_weight

        # --- 전고점/낙폭 & 트리거 ---
        if gpx > peak:
            peak = gpx
            triggers_fired = [False] * len(cfg.triggers)   # 신고가 시 리셋
        dd = gpx / peak - 1.0
        for k, (level, deploy) in enumerate(cfg.triggers):
            if not triggers_fired[k] and dd <= level:
                amount = cash * deploy
                if amount > 0:
                    tqqq.buy(amount / tpx, tpx)
                    cash -= amount
                triggers_fired[k] = True

        # --- 분할 매도 (exit_mode == 'partial') ---
        if is_partial:
            proceeds, realized = tqqq.sell_lots_at_gain(tpx, cfg.partial_sell_gain)
            if proceeds > 0:
                cash += proceeds            # 매도대금 전액을 현금풀로 환수 -> 재투자 탄약
                realized_ytd += realized    # 실현이익만 과세 대상으로 누적

        # --- 연말 과세 정산 ---
        if years[i] != current_year:
            taxable = max(0.0, realized_ytd - cfg.annual_deduction)
            t = taxable * cfg.cap_gains_tax
            tax_paid += t
            cash = max(0.0, cash - t)            # 세금은 현금에서 납부
            realized_ytd = 0.0
            current_year = years[i]

        equity_curve[i] = qld.value(qpx) + tqqq.value(tpx) + cash

    eq = pd.Series(equity_curve, index=idx)

    # 종료 시점 미실현이익에 대한 청산세(hold 전략의 '과세이연'을 정직하게 비교)
    unrealized = (qld.value(qld_px[-1]) - sum(l.cost for l in qld.lots)) \
                 + (tqqq.value(tqqq_px[-1]) - sum(l.cost for l in tqqq.lots))
    liquidation_tax = max(0.0, unrealized - cfg.annual_deduction) * cfg.cap_gains_tax

    final_gross = eq.iloc[-1]
    final_net = final_gross - liquidation_tax       # 전부 청산한다고 가정한 세후
    years = (prices.index[-1] - prices.index[0]).days / 365.25
    moic = final_gross / invested if invested > 0 else np.nan
    # DCA는 일시불이 아니므로 money-weighted IRR(XIRR)로 연환산 수익률 계산
    cf = cashflows + [(prices.index[-1], final_gross)]
    irr = xirr(cf)
    cf_net = cashflows + [(prices.index[-1], final_net)]
    irr_net = xirr(cf_net)
    roll_max = eq.cummax()
    mdd = (eq / roll_max - 1.0).min()

    return {
        'exit_mode': exit_mode,
        'invested': invested,
        'final_gross': final_gross,
        'tax_paid_during': tax_paid,
        'liquidation_tax': liquidation_tax,
        'final_net_if_liquidated': final_net,
        'moic': moic,
        'irr': irr,
        'irr_net': irr_net,
        'mdd': mdd,
        'equity': eq,
    }


# ------------------------------------------------------------------ #
#  Data loaders
# ------------------------------------------------------------------ #
def load_yfinance(start: str, end: str | None) -> pd.DataFrame:
    import yfinance as yf
    qqq = yf.download('QQQ', start=start, end=end, auto_adjust=True, progress=False)['Close']
    irx = yf.download('^IRX', start=start, end=end, progress=False)['Close']  # 13주 T-bill, %
    qqq = qqq.squeeze().dropna()
    rf = (irx.squeeze() / 100.0).reindex(qqq.index).ffill().fillna(0.04)
    df = pd.DataFrame({'idx_ret': qqq.pct_change().fillna(0.0), 'rf': rf})
    return df


def load_synthetic(years: int = 20, seed: int = 42, regime: str = 'bull') -> pd.DataFrame:
    """GBM 합성 경로. regime: bull(우상향) / sideways(일본식 횡보) / crash(반복 폭락)."""
    rng = np.random.default_rng(seed)
    n = years * 252
    if regime == 'bull':
        mu, sigma = 0.11, 0.20
    elif regime == 'sideways':
        mu, sigma = 0.00, 0.22       # 드리프트 0, 변동성 큰 횡보 -> 잠식 극대화
    elif regime == 'crash':
        mu, sigma = 0.04, 0.35
    else:
        raise ValueError(regime)
    dt = 1 / 252
    rets = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
    idx = pd.bdate_range('2005-01-03', periods=n)
    rf = pd.Series(np.full(n, 0.03), index=idx)
    return pd.DataFrame({'idx_ret': pd.Series(rets, index=idx), 'rf': rf})


# ------------------------------------------------------------------ #
#  Reporting
# ------------------------------------------------------------------ #
def fmt(x): return f"{x:,.0f}"


def report(results: list[dict], cfg: Config):
    inv = results[0]['invested']
    print("\n" + "=" * 72)
    print("  NASDAQ-100 레버리지 리밸런싱 백테스트 결과")
    print("=" * 72)
    print(f"  누적 납입 원금        : {fmt(inv)}")
    print("-" * 72)
    header = (f"  {'전략':<16}{'세전 최종':>15}{'MOIC':>7}{'IRR(세전)':>10}"
              f"{'IRR(세후)':>10}{'MDD':>9}")
    print(header)
    print("-" * 72)
    for r in results:
        name = '끝까지 보유(HOLD)' if r['exit_mode'] == 'hold' else '분할 매도(PARTIAL)'
        print(f"  {name:<16}{fmt(r['final_gross']):>15}{r['moic']:>6.2f}x"
              f"{r['irr']*100:>9.1f}%{r['irr_net']*100:>9.1f}%{r['mdd']*100:>8.1f}%")
    print("-" * 72)
    for r in results:
        name = 'HOLD' if r['exit_mode'] == 'hold' else 'PARTIAL'
        print(f"  [{name}] 보유기간 납부세금: {fmt(r['tax_paid_during'])}  "
              f"| 청산세: {fmt(r['liquidation_tax'])}  "
              f"| 세후최종(청산): {fmt(r['final_net_if_liquidated'])}")
    print("=" * 72)
    print("  주의: N=1 사후 경로. 결과론(survivorship) 가능성. FX 미반영.")
    print("        LLM은 엑셀이지 오라클이 아니다 — 가정이 바뀌면 결론도 바뀐다.")
    print("=" * 72 + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', choices=['yfinance', 'synthetic'], default='synthetic')
    ap.add_argument('--start', default='2005-01-01')
    ap.add_argument('--end', default=None)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--years', type=int, default=20)
    ap.add_argument('--regime', choices=['bull', 'sideways', 'crash'], default='bull')
    args = ap.parse_args()

    cfg = Config()
    if args.source == 'yfinance':
        prices = load_yfinance(args.start, args.end)
    else:
        prices = load_synthetic(args.years, args.seed, args.regime)
        print(f"[synthetic] regime={args.regime} seed={args.seed} "
              f"(메커니즘 검증용 — 실제 결론 아님)")

    results = [run_backtest(prices, cfg, m) for m in ('hold', 'partial')]
    report(results, cfg)


if __name__ == '__main__':
    main()
