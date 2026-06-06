/**
 * ARDS-X Technical / 가격구조 — 원본 quant/technical.py 1:1.
 * 드로다운 + 추세 무결성 + 과매도 → decline_score / oversold_score.
 * 주의: metrics 를 반올림(pyRound)한 뒤 그 값으로 점수를 계산(원본 analyze_universe 순서).
 */
import {
  isNum,
  dropNaN,
  atFromEnd,
  mean,
  std,
  median,
  diff,
  ewmMeanAdjustFalse,
  maxOf,
  pyRound,
} from "../series";
import { rollingMeanEndingAt } from "./dseries";
import { TECH } from "./config";

function rsiLast(s: number[], period = 14): number {
  const d = diff(s);
  const up = ewmMeanAdjustFalse(d.map((x) => (isNum(x) ? Math.max(x, 0) : Number.NaN)), 1 / period);
  const dn = ewmMeanAdjustFalse(d.map((x) => (isNum(x) ? Math.max(-x, 0) : Number.NaN)), 1 / period);
  const dnLast = atFromEnd(dn, 1);
  if (!isNum(dnLast) || dnLast === 0) return 50.0; // dn.replace(0,nan) → rs nan → fillna(50)
  const rs = atFromEnd(up, 1) / dnLast;
  const r = 100 - 100 / (1 + rs);
  return isNum(r) ? r : 50.0;
}

function atrProxyLast(s: number[], period = 14): number {
  const a = ewmMeanAdjustFalse(diff(s).map((x) => (isNum(x) ? Math.abs(x) : Number.NaN)), 1 / period);
  return atFromEnd(a, 1);
}

export interface TechMetrics {
  last: number;
  dd_from_high: number;
  pct_vs_50dma: number;
  pct_vs_200dma: number;
  above_200dma: boolean;
  golden_cross: boolean;
  ma200_slope: number;
  rsi14: number;
  bb_pctb: number;
  atr_stretch: number;
  mom6m: number;
  down_streak: number;
}

export interface TechRow extends TechMetrics {
  ticker: string;
  name: string;
  group: string | null;
  decline_score: number;
  oversold_score: number;
}

export function metricsFor(closeIn: number[]): TechMetrics | null {
  const s = dropNaN(closeIn);
  if (s.length < 60) return null;
  const n = s.length;
  const last = atFromEnd(s, 1);
  const hi252 = n >= 252 ? maxOf(s.slice(n - 252)) : maxOf(s);
  const dd = (last / hi252 - 1) * 100.0;

  const ma20 = mean(s.slice(n - 20));
  const ma50 = mean(s.slice(n - 50));
  const W = n >= 200 ? 200 : Math.min(n, 150);
  const ma200 = mean(s.slice(n - W));

  // 200일선 기울기 (최근 21거래일 변화%)
  let slope = 0.0;
  if (n - W + 1 > 22) {
    const maLast = rollingMeanEndingAt(s, n - 1, W);
    const ma21 = rollingMeanEndingAt(s, n - 21, W);
    slope = (maLast / ma21 - 1) * 100;
  }

  const r = rsiLast(s);
  const maB = mean(s.slice(n - 20));
  const sdB = std(s.slice(n - 20), 1);
  const rng = 4 * sdB;
  let pctb = rng === 0 ? Number.NaN : (last - (maB - 2 * sdB)) / rng;
  if (!isNum(pctb)) pctb = 0.5;
  const atr = atrProxyLast(s) || 1e-9;
  const atrStretch = (ma20 - last) / atr;

  const mom6 = n >= 126 ? (last / s[n - 126] - 1) * 100 : (last / s[0] - 1) * 100;

  const diffs = diff(s).slice(n - 10);
  let downStreak = 0;
  for (let i = diffs.length - 1; i >= 0; i--) {
    if (diffs[i] < 0) downStreak++;
    else break;
  }

  return {
    last: pyRound(last, 2),
    dd_from_high: pyRound(dd, 1),
    pct_vs_50dma: pyRound((last / ma50 - 1) * 100, 1),
    pct_vs_200dma: pyRound((last / ma200 - 1) * 100, 1),
    above_200dma: last > ma200,
    golden_cross: ma50 > ma200,
    ma200_slope: pyRound(slope, 1),
    rsi14: pyRound(r, 1),
    bb_pctb: pyRound(pctb, 2),
    atr_stretch: pyRound(atrStretch, 1),
    mom6m: pyRound(mom6, 1),
    down_streak: downStreak,
  };
}

function declineScore(m: TechMetrics): number {
  const t = TECH;
  let score = 0.0;
  const dd = -m.dd_from_high;
  score += Math.min(45, (dd / t.dd_bear) * 45);
  if (!m.above_200dma) score += 15;
  if (!m.golden_cross) score += 12;
  if (m.ma200_slope < 0) score += Math.min(15, -m.ma200_slope * 5);
  if (m.mom6m < 0) score += Math.min(13, (-m.mom6m / 20) * 13);
  return Math.min(100.0, score);
}

function oversoldScore(m: TechMetrics): number {
  const t = TECH;
  let score = 0.0;
  if (m.rsi14 < t.rsi_oversold) score += Math.min(45, ((t.rsi_oversold - m.rsi14) / (t.rsi_oversold - 10)) * 45);
  if (m.bb_pctb < t.bb_oversold) score += 25;
  else if (m.bb_pctb < 0.2) score += 12;
  if (m.atr_stretch > 0) score += Math.min(20, (m.atr_stretch / t.atr_stretch) * 20);
  score += Math.min(10, m.down_streak * 2.5);
  return Math.min(100.0, score);
}

export interface NameGroup {
  [ticker: string]: [string, string | null];
}

export function analyzeUniverse(priceMap: Record<string, number[]>, nameGroup: NameGroup): TechRow[] {
  const rows: TechRow[] = [];
  for (const t of Object.keys(priceMap)) {
    const m = metricsFor(priceMap[t]);
    if (m === null) continue;
    const [name, group] = nameGroup[t] ?? [t, null];
    rows.push({
      ...m,
      ticker: t,
      name,
      group,
      decline_score: pyRound(declineScore(m), 1),
      oversold_score: pyRound(oversoldScore(m), 1),
    });
  }
  return rows;
}

export interface TechAgg {
  n: number;
  breadth_above_200dma: number;
  breadth_golden_cross: number;
  avg_dd_from_high: number;
  median_dd_from_high: number;
  avg_rsi14: number;
  avg_decline_score: number;
  avg_oversold_score: number;
  n_oversold: number;
  n_below_200dma: number;
}

export function aggregate(rows: TechRow[]): TechAgg | Record<string, never> {
  if (rows.length === 0) return {};
  const n = rows.length;
  const above200 = rows.filter((r) => r.above_200dma).length;
  const golden = rows.filter((r) => r.golden_cross).length;
  return {
    n,
    breadth_above_200dma: pyRound((above200 / n) * 100, 0),
    breadth_golden_cross: pyRound((golden / n) * 100, 0),
    avg_dd_from_high: pyRound(mean(rows.map((r) => r.dd_from_high)), 1),
    median_dd_from_high: pyRound(median(rows.map((r) => r.dd_from_high)), 1),
    avg_rsi14: pyRound(mean(rows.map((r) => r.rsi14)), 1),
    avg_decline_score: pyRound(mean(rows.map((r) => r.decline_score)), 1),
    avg_oversold_score: pyRound(mean(rows.map((r) => r.oversold_score)), 1),
    n_oversold: rows.filter((r) => r.rsi14 < TECH.rsi_oversold).length,
    n_below_200dma: n - above200,
  };
}
