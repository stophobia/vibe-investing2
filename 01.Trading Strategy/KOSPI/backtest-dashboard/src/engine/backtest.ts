/**
 * Backtest engine — monthly rebalanced, long-only. Ties together universe,
 * factors, scoring, portfolio construction, trading costs and the crisis filter.
 * Implements the [리밸런싱 및 거래 비용] and [위험 관리] blocks of BuyKorea.md.
 *
 * Look-ahead safety:
 *  · Signals use only data with date/disclose <= 신호일(month-end).
 *  · Execution assumed at the NEXT trading day open (다음 영업일 시가).
 */
import type { DataStore } from "../data/loader.js";
import type {
  BacktestParams,
  EquityPoint,
  RebalanceRecord,
  StockSnapshot,
} from "../types.js";
import { universeFilter } from "./universe.js";
import { factorCalculator } from "./factors.js";
import { scoreCombiner } from "./score.js";
import { portfolioConstructor } from "./portfolio.js";
import { std } from "../util.js";
import type { RebalanceSnapshot } from "./backtest_ic.js";

export interface EngineOutput {
  rebalances: RebalanceRecord[];
  equity: EquityPoint[];
  monthly: { date: string; strategy: number; benchmark: number }[];
  icHistory: RebalanceSnapshot[];
  factorExposure: { date: string; quality: number; value: number; lowVol: number; momentum: number }[];
  navGross: number;
  monthlyGross: number[];
}

function priceOpen(ds: DataStore, code: string, idx: number): number {
  const o = ds.open.get(code);
  if (o && Number.isFinite(o[idx])) return o[idx];
  const c = ds.close.get(code);
  if (c) for (let i = idx; i >= Math.max(0, idx - 25); i--) if (Number.isFinite(c[i])) return c[i];
  return NaN;
}

function crisisFilter(ds: DataStore, asOf: string, params: BacktestParams): boolean {
  const idx = ds.idxOnOrBefore(asOf);
  if (idx < 260) return false;
  // (a) 지수가 12개월 이동평균 아래.
  let sum = 0;
  let cnt = 0;
  for (let i = Math.max(0, idx - 251); i <= idx; i++) {
    if (Number.isFinite(ds.benchPrice[i])) {
      sum += ds.benchPrice[i];
      cnt++;
    }
  }
  const ma = cnt ? sum / cnt : Infinity;
  const belowMA = ds.benchPrice[idx] < ma;
  // (b) 60거래일 실현변동성(연율화) >= 30%.
  const rets: number[] = [];
  for (let i = idx - 59; i <= idx; i++) {
    if (i > 0 && ds.benchPrice[i - 1] > 0) rets.push(ds.benchPrice[i] / ds.benchPrice[i - 1] - 1);
  }
  const vol = std(rets) * Math.sqrt(252);
  const highVol = vol >= params.crisis.volThreshold;
  return belowMA && highVol; // 두 조건 모두 충족 시 위기
}

export function runEngine(ds: DataStore, params: BacktestParams): EngineOutput {
  const rebalDates = ds.monthEnds.filter((d) => d >= params.startDate && d <= params.endDate);

  let currentWeights = new Map<string, number>(); // actual weights just after last execution
  let prevExecIdx: number | null = null;
  let navNet = 100;
  let navGross = 100;
  let benchBase = 0;
  let pendingCost = 0;

  const rebalances: RebalanceRecord[] = [];
  const equity: EquityPoint[] = [];
  const monthly: { date: string; strategy: number; benchmark: number }[] = [];
  const monthlyGross: number[] = [];
  const icHistory: RebalanceSnapshot[] = [];
  const factorExposure: EngineOutput["factorExposure"] = [];

  const commission = params.cost.commission;
  const impact = params.cost.marketImpact;
  const taxFor = (year: number) => params.cost.sellTaxByYear[String(year)] ?? params.cost.sellTaxByYear.default;

  for (let k = 0; k < rebalDates.length; k++) {
    const signalDate = rebalDates[k];
    const execIdx = ds.nextTradingIdx(signalDate);
    if (execIdx < 0) break;
    const execDate = ds.dates[execIdx];

    // ---- 1) Realize the period return from previous execution to this execution ----
    if (prevExecIdx !== null) {
      let grossGrowth = 0;
      let weightUsed = 0;
      for (const [code, w] of currentWeights) {
        if (w <= 0) continue;
        const p0 = priceOpen(ds, code, prevExecIdx);
        const p1 = priceOpen(ds, code, execIdx);
        if (Number.isFinite(p0) && Number.isFinite(p1) && p0 > 0) {
          grossGrowth += w * (p1 / p0);
          weightUsed += w;
        } else {
          grossGrowth += w; // fallback: flat
          weightUsed += w;
        }
      }
      const cashWeight = Math.max(0, 1 - weightUsed);
      grossGrowth += cashWeight * (1 + params.crisis.cashRate / 12);

      const netGrowth = grossGrowth * (1 - pendingCost);
      navGross *= grossGrowth;
      navNet *= netGrowth;
      pendingCost = 0;

      const benchRet = ds.benchTR[execIdx] / ds.benchTR[prevExecIdx] - 1;
      monthly.push({ date: execDate, strategy: netGrowth - 1, benchmark: benchRet });
      monthlyGross.push(grossGrowth - 1);

      // Drift current weights to this execution date.
      const drifted = new Map<string, number>();
      for (const [code, w] of currentWeights) {
        if (w <= 0) continue;
        const p0 = priceOpen(ds, code, prevExecIdx);
        const p1 = priceOpen(ds, code, execIdx);
        const grow = Number.isFinite(p0) && Number.isFinite(p1) && p0 > 0 ? p1 / p0 : 1;
        drifted.set(code, (w * grow) / grossGrowth);
      }
      currentWeights = drifted;
    }

    // ---- 2) Build signal at signalDate, rebalance at execDate ----
    const members = universeFilter(ds, signalDate, params);
    let selected: { code: string; sector: string }[] = [];
    let scored: StockSnapshot[] = [];
    if (members.length >= params.numHoldings) {
      scored = scoreCombiner(factorCalculator(ds, members, signalDate), params);
      const currentSet = new Set([...currentWeights.keys()].filter((c) => (currentWeights.get(c) ?? 0) > 0));
      selected = portfolioConstructor(scored, currentSet, params);
    }

    const riskOff = crisisFilter(ds, signalDate, params);
    const equityRatio = riskOff ? params.crisis.equityRatioRiskOff : 1;
    // Equal weight, fully invested across numHoldings (5% each for 20 names).
    const perName = 1 / params.numHoldings;
    const targetPer = perName * equityRatio;
    const trimThreshold = (params.maxPositionWeight / params.positionWeight) * perName; // 8% when 20 names

    // Target weights.
    const target = new Map<string, number>();
    for (const t of selected) target.set(t.code, targetPer);

    // Apply band (skip small trades) & trim (>maxPositionWeight -> positionWeight).
    const finalW = new Map<string, number>();
    const codes = new Set<string>([...currentWeights.keys(), ...target.keys()]);
    for (const code of codes) {
      const w0 = currentWeights.get(code) ?? 0;
      const tgt = target.get(code) ?? 0;
      if (tgt === 0) {
        finalW.set(code, 0); // full sell (dropped)
      } else if (w0 > trimThreshold) {
        finalW.set(code, targetPer); // trim back to target
      } else if (Math.abs(tgt - w0) < params.rebalanceBand && w0 > 0) {
        finalW.set(code, w0); // within band -> skip trade
      } else {
        finalW.set(code, tgt);
      }
    }

    // Trading cost.
    let buys = 0;
    let sells = 0;
    for (const code of codes) {
      const w0 = currentWeights.get(code) ?? 0;
      const w1 = finalW.get(code) ?? 0;
      const d = w1 - w0;
      if (d > 0) buys += d;
      else sells += -d;
    }
    const tax = taxFor(Number(execDate.slice(0, 4)));
    const cost = sells * (tax + commission + impact) + buys * (commission + impact);
    pendingCost = cost;
    const turnover = (buys + sells) / 2;

    currentWeights = new Map([...finalW].filter(([, w]) => w > 0));

    // Records.
    const sectorOf = new Map(scored.map((s) => [s.code, s.sector]));
    rebalances.push({
      date: signalDate,
      execDate,
      holdings: [...currentWeights.entries()].map(([code, weight]) => ({
        code,
        weight,
        sector: (sectorOf.get(code) ?? "IT") as any,
      })),
      turnover,
      riskOff,
      equityRatio,
    });

    // Factor exposure of the held book (mean sign-adjusted z by group).
    if (currentWeights.size > 0 && scored.length) {
      const byCode = new Map(scored.map((s) => [s.code, s]));
      const held = [...currentWeights.keys()].map((c) => byCode.get(c)).filter(Boolean) as StockSnapshot[];
      const gmean = (keys: (keyof NonNullable<StockSnapshot["zscores"]>)[]) => {
        const vals: number[] = [];
        for (const s of held) for (const key of keys) if (s.zscores?.[key] !== undefined) vals.push(s.zscores![key]!);
        return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
      };
      factorExposure.push({
        date: execDate,
        quality: gmean(["roe", "gpa", "debtRatio", "roeStability"]),
        value: gmean(["ep", "bp", "divYield"]),
        lowVol: gmean(["vol60", "beta"]),
        momentum: gmean(["mom12_1", "mom6_1"]),
      });
    }

    // IC snapshot (forward return filled after loop).
    if (scored.length) icHistory.push({ date: signalDate, snapshots: scored, forwardReturn: new Map() });

    // Equity curve point.
    if (benchBase === 0) benchBase = ds.benchTR[execIdx];
    equity.push({
      date: execDate,
      strategy: navNet,
      benchmark: (ds.benchTR[execIdx] / benchBase) * 100,
    });

    prevExecIdx = execIdx;
  }

  // Fill IC forward returns: next-month return per stock (open-to-open, exec dates).
  const execIdxByDate = new Map<string, number>();
  for (let k = 0; k < rebalDates.length; k++) {
    const e = ds.nextTradingIdx(rebalDates[k]);
    if (e >= 0) execIdxByDate.set(rebalDates[k], e);
  }
  for (let i = 0; i < icHistory.length - 1; i++) {
    const e0 = execIdxByDate.get(icHistory[i].date);
    const e1 = execIdxByDate.get(icHistory[i + 1].date);
    if (e0 === undefined || e1 === undefined) continue;
    for (const s of icHistory[i].snapshots) {
      const p0 = priceOpen(ds, s.code, e0);
      const p1 = priceOpen(ds, s.code, e1);
      if (Number.isFinite(p0) && Number.isFinite(p1) && p0 > 0) icHistory[i].forwardReturn.set(s.code, p1 / p0 - 1);
    }
  }

  return { rebalances, equity, monthly, icHistory, factorExposure, navGross, monthlyGross };
}
