/**
 * Backtest orchestrator — runs the engine, assembles the full BacktestResult:
 * performance stats (net & gross), yearly table, drawdown series, IC analysis,
 * factor exposure and parameter-sensitivity table.
 */
import type { DataStore } from "../data/loader.js";
import type {
  BacktestParams,
  BacktestResult,
  SensitivityRow,
  YearlyRow,
} from "../types.js";
import { runEngine } from "./backtest.js";
import { computeStats } from "./performance.js";
import { icAnalysis } from "./backtest_ic.js";
import { mean, round, yearOf } from "../util.js";

function yearlyTable(monthly: { date: string; strategy: number; benchmark: number }[]): YearlyRow[] {
  const byYear = new Map<number, { s: number; b: number }>();
  for (const m of monthly) {
    const y = yearOf(m.date);
    const cur = byYear.get(y) ?? { s: 1, b: 1 };
    cur.s *= 1 + m.strategy;
    cur.b *= 1 + m.benchmark;
    byYear.set(y, cur);
  }
  return [...byYear.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([year, v]) => ({ year, strategy: v.s - 1, benchmark: v.b - 1, excess: v.s - v.b }));
}

function drawdownSeries(equity: { date: string; strategy: number; benchmark: number }[]) {
  let ps = -Infinity;
  let pb = -Infinity;
  return equity.map((e) => {
    ps = Math.max(ps, e.strategy);
    pb = Math.max(pb, e.benchmark);
    return { date: e.date, strategy: e.strategy / ps - 1, benchmark: e.benchmark / pb - 1 };
  });
}

function statsFromRun(ds: DataStore, params: BacktestParams) {
  const out = runEngine(ds, params);
  const avgTurnover = out.rebalances.length ? mean(out.rebalances.map((r) => r.turnover)) : 0;
  const stats = computeStats(
    out.monthly.map((m) => m.strategy),
    out.monthly.map((m) => m.benchmark),
    avgTurnover,
  );
  return { out, stats, avgTurnover };
}

function sensitivity(ds: DataStore, base: BacktestParams): SensitivityRow[] {
  const rows: SensitivityRow[] = [];
  const push = (label: string, p: BacktestParams) => {
    const { stats } = statsFromRun(ds, p);
    rows.push({ label, cagr: round(stats.cagr, 4), sharpe: round(stats.sharpe, 3), mdd: round(stats.mdd, 4) });
  };
  // 종목 수 민감도.
  for (const n of [15, 20, 25]) {
    push(`종목수 ${n}`, { ...base, numHoldings: n, bufferOut: n + 10 });
  }
  // 퀄리티 가중치 민감도 (나머지는 비례 축소).
  for (const q of [0.3, 0.4, 0.5]) {
    const rest = 1 - q;
    const base2 = base.weights.value + base.weights.lowVol + base.weights.momentum;
    const w = {
      quality: q,
      value: (base.weights.value / base2) * rest,
      lowVol: (base.weights.lowVol / base2) * rest,
      momentum: (base.weights.momentum / base2) * rest,
    };
    push(`퀄리티 ${Math.round(q * 100)}%`, { ...base, weights: w });
  }
  return rows;
}

export function runBacktest(ds: DataStore, params: BacktestParams, withSensitivity = true): BacktestResult {
  const { out, stats, avgTurnover } = statsFromRun(ds, params);

  const statsBenchmark = computeStats(
    out.monthly.map((m) => m.benchmark),
    out.monthly.map((m) => m.benchmark),
    0,
  );
  const statsGross = computeStats(out.monthlyGross, out.monthly.map((m) => m.benchmark), avgTurnover);

  const { series: icSeries, summary: icSummary } = icAnalysis(out.icHistory);

  return {
    params,
    equityCurve: out.equity,
    monthlyReturns: out.monthly,
    drawdown: drawdownSeries(out.equity),
    rebalances: out.rebalances,
    stats,
    statsBenchmark,
    statsGross,
    yearly: yearlyTable(out.monthly),
    icSeries,
    icSummary,
    factorExposure: out.factorExposure,
    sensitivity: withSensitivity ? sensitivity(ds, params) : [],
    generatedAt: new Date().toISOString(),
  };
}
