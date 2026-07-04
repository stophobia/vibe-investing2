/**
 * Score combiner — turns raw factors into a composite score.
 * Implements the [종합 점수 및 종목 선정] block of BuyKorea.md:
 *
 *  1. Winsorize (1% tails) + cross-sectional z-score, missing -> 중앙값(0).
 *  2. Reverse-direction factors (부채비율, ROE 안정성, 변동성, 베타) 부호 반전.
 *  3. 각 팩터를 WICS 대분류 섹터 내 percentile rank 로 변환 (섹터 중립화).
 *  4. 팩터 그룹 가중치(퀄리티40 / 밸류25 / 저변동20 / 모멘텀15)로 가중합.
 */
import type { BacktestParams, FactorKey, StockSnapshot } from "../types.js";
import { percentileRank, winsorize } from "../util.js";

const GROUPS: Record<"quality" | "value" | "lowVol" | "momentum", FactorKey[]> = {
  quality: ["roe", "gpa", "debtRatio", "roeStability"],
  value: ["ep", "bp", "divYield"],
  lowVol: ["vol60", "beta"],
  momentum: ["mom12_1", "mom6_1"],
};

// Factors where a LOWER raw value is better (reverse direction).
const REVERSE = new Set<FactorKey>(["debtRatio", "roeStability", "vol60", "beta"]);

const ALL_FACTORS: FactorKey[] = [...GROUPS.quality, ...GROUPS.value, ...GROUPS.lowVol, ...GROUPS.momentum];

export function scoreCombiner(snapshots: StockSnapshot[], params: BacktestParams): StockSnapshot[] {
  if (snapshots.length === 0) return snapshots;
  const n = snapshots.length;

  // Sign-adjusted, winsorized, z-scored value per factor (missing -> 0).
  const adjusted: Record<string, number[]> = {};
  for (const key of ALL_FACTORS) {
    const raw = snapshots.map((s) => {
      const v = s.factors[key];
      return v === undefined || !Number.isFinite(v) ? NaN : (REVERSE.has(key) ? -v : v);
    });
    const finiteIdx = raw.map((v, i) => (Number.isFinite(v) ? i : -1)).filter((i) => i >= 0);
    const finiteVals = finiteIdx.map((i) => raw[i]);
    const wins = winsorize(finiteVals, 0.01);
    const m = finiteVals.length ? finiteVals.reduce((a, b) => a + b, 0) / finiteVals.length : 0;
    const sd = std(wins);
    const z = raw.map((v) => (Number.isFinite(v) && sd > 0 ? (v - m) / sd : 0));
    // Winsorize on the winsorized-clipped scale already applied to finite; map back.
    const clip = new Map<number, number>();
    finiteIdx.forEach((idx, k) => clip.set(idx, wins[k]));
    adjusted[key] = raw.map((v, i) => {
      if (!Number.isFinite(v)) return 0; // missing -> median (0 after z)
      const w = clip.get(i)!;
      return sd > 0 ? (w - m) / sd : 0;
    });
  }

  // Store z-scores on snapshots (for IC diagnostics).
  snapshots.forEach((s, i) => {
    s.zscores = {};
    for (const key of ALL_FACTORS) s.zscores![key] = adjusted[key][i];
  });

  // Sector-neutral percentile rank per factor.
  const sectors = [...new Set(snapshots.map((s) => s.sector))];
  const rankByFactor: Record<string, number[]> = {};
  for (const key of ALL_FACTORS) {
    const ranks = new Array<number>(n).fill(0.5);
    for (const sec of sectors) {
      const idx = snapshots.map((s, i) => (s.sector === sec ? i : -1)).filter((i) => i >= 0);
      if (idx.length === 0) continue;
      const vals = idx.map((i) => adjusted[key][i]);
      const pr = percentileRank(vals);
      idx.forEach((i, k) => (ranks[i] = pr[k]));
    }
    rankByFactor[key] = ranks;
  }

  // Group scores + weighted composite.
  const gw = params.weights;
  snapshots.forEach((s, i) => {
    const groupScore = (keys: FactorKey[]) => keys.reduce((a, k) => a + rankByFactor[k][i], 0) / keys.length;
    const q = groupScore(GROUPS.quality);
    const v = groupScore(GROUPS.value);
    const l = groupScore(GROUPS.lowVol);
    const mo = groupScore(GROUPS.momentum);
    s.qualityScore = q;
    s.valueScore = v;
    s.lowVolScore = l;
    s.momentumScore = mo;
    s.compositeScore = gw.quality * q + gw.value * v + gw.lowVol * l + gw.momentum * mo;
  });

  return snapshots;
}

function std(xs: number[]): number {
  const n = xs.length;
  if (n < 2) return 0;
  const m = xs.reduce((a, b) => a + b, 0) / n;
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) * (b - m), 0) / (n - 1));
}
