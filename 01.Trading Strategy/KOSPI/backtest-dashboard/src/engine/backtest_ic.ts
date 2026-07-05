/**
 * IC / RankIC analysis — Spearman rank correlation between each factor's
 * sign-adjusted z-score and the next-month forward return, per rebalance date.
 * Implements the [검증 및 진단] block of BuyKorea.md.
 */
import type { FactorKey, ICPoint, ICSummaryRow, StockSnapshot } from "../types.js";
import { mean, spearman, std } from "../util.js";

export const IC_FACTORS: FactorKey[] = [
  "roe",
  "gpa",
  "debtRatio",
  "roeStability",
  "ep",
  "bp",
  "divYield",
  "vol60",
  "beta",
  "mom12_1",
  "mom6_1",
];

export interface RebalanceSnapshot {
  date: string;
  snapshots: StockSnapshot[];
  forwardReturn: Map<string, number>; // code -> next-month return
}

export function icAnalysis(history: RebalanceSnapshot[]): { series: ICPoint[]; summary: ICSummaryRow[] } {
  const series: ICPoint[] = [];
  const perFactor: Record<string, number[]> = {};
  for (const f of IC_FACTORS) perFactor[f] = [];

  for (const h of history) {
    const point: ICPoint = { date: h.date, ic: {} as Record<FactorKey, number | null> };
    const withFwd = h.snapshots.filter((s) => h.forwardReturn.has(s.code));
    const fwd = withFwd.map((s) => h.forwardReturn.get(s.code)!);
    for (const f of IC_FACTORS) {
      const z = withFwd.map((s) => s.zscores?.[f] ?? NaN);
      const ic = spearman(z, fwd);
      point.ic[f] = ic;
      if (ic !== null) perFactor[f].push(ic);
    }
    series.push(point);
  }

  const summary: ICSummaryRow[] = IC_FACTORS.map((f) => {
    const xs = perFactor[f];
    const m = xs.length ? mean(xs) : 0;
    const s = xs.length > 1 ? std(xs) : 0;
    const icIR = s > 0 ? m / s : 0;
    const tStat = xs.length > 1 ? icIR * Math.sqrt(xs.length) : 0;
    const hitRate = xs.length ? xs.filter((x) => x > 0).length / xs.length : 0;
    return { factor: f, meanIC: m, icIR, tStat, hitRate };
  });

  return { series, summary };
}
