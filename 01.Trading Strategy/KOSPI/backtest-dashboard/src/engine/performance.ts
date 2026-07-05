/**
 * Performance metrics — CAGR, vol, Sharpe, MDD & recovery, information ratio,
 * turnover, monthly win rate. Implements the [성과 지표] block of BuyKorea.md.
 */
import type { PerformanceStats } from "../types.js";
import { mean, std } from "../util.js";

export function computeStats(monthly: number[], bench: number[], avgTurnover: number): PerformanceStats {
  const nMonths = monthly.length;
  if (nMonths === 0) {
    return {
      cagr: 0,
      vol: 0,
      sharpe: 0,
      mdd: 0,
      mddRecoveryMonths: null,
      informationRatio: 0,
      avgTurnover,
      winRateMonthly: 0,
      totalReturn: 0,
    };
  }

  let equity = 1;
  const curve: number[] = [1];
  for (const r of monthly) {
    equity *= 1 + r;
    curve.push(equity);
  }
  const totalReturn = equity - 1;
  const years = nMonths / 12;
  const cagr = Math.pow(equity, 1 / years) - 1;
  const vol = std(monthly) * Math.sqrt(12);
  const annReturn = mean(monthly) * 12;
  const sharpe = vol > 0 ? annReturn / vol : 0;

  // Max drawdown and recovery.
  let peak = curve[0];
  let peakIdx = 0;
  let mdd = 0;
  let troughIdx = 0;
  let mddPeakIdx = 0;
  for (let i = 1; i < curve.length; i++) {
    if (curve[i] > peak) {
      peak = curve[i];
      peakIdx = i;
    }
    const dd = curve[i] / peak - 1;
    if (dd < mdd) {
      mdd = dd;
      troughIdx = i;
      mddPeakIdx = peakIdx;
    }
  }
  let mddRecoveryMonths: number | null = null;
  const recoverTo = curve[mddPeakIdx];
  for (let i = troughIdx; i < curve.length; i++) {
    if (curve[i] >= recoverTo) {
      mddRecoveryMonths = i - troughIdx;
      break;
    }
  }

  // Information ratio (annualized) vs benchmark.
  const excess = monthly.map((r, i) => r - (bench[i] ?? 0));
  const teMonthly = std(excess);
  const informationRatio = teMonthly > 0 ? (mean(excess) * 12) / (teMonthly * Math.sqrt(12)) : 0;

  const winRateMonthly = monthly.filter((r) => r > 0).length / nMonths;

  return {
    cagr,
    vol,
    sharpe,
    mdd,
    mddRecoveryMonths,
    informationRatio,
    avgTurnover,
    winRateMonthly,
    totalReturn,
  };
}
