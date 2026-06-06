/**
 * AMQS-AI-Infra — Adaptive Momentum Quant Strategy (TS 포팅).
 *
 * 원본: "Adaptive Momentum Quant Strategy (AMQS) for AI Infra/script/strategy.py"
 * 충실 포팅: 4-Factor 모멘텀 z합 + 5차원 100점 + 사전필터 + 레짐 + Top-N(서브테마 캡) + tilted 사이징.
 * 동작은 Python 결과(골든 fixture)와 대조 검증한다(test/strategy/amqs.test.ts).
 * 룰/상수 변경 금지 — 원본 strategy.py 가 최종 권위.
 */

import {
  SQRT_252,
  isNum,
  dropNaN,
  atFromEnd,
  mean,
  std,
  diff,
  pctChange,
  ewmMeanAdjustFalse,
  cumMax,
  maxOf,
  minOf,
  clip,
} from "./series";
import type { DashboardSignal } from "./types";

// --- Universe (strategy.py) ------------------------------------------------
export const AI_INFRA_SUBTHEMES: Record<string, string[]> = {
  "Compute/GPU": ["NVDA", "AMD", "INTC", "AVGO", "MRVL", "TSM"],
  "Memory/Storage": ["MU", "STX", "WDC", "PSTG"],
  "Systems/Server": ["DELL", "SMCI", "HPE"],
  Networking: ["ANET", "CSCO"],
  "Data/Software": ["SNOW", "ORCL", "PLTR"],
  "Power/Cooling": ["VRT"],
};
export const AI_INFRA_TICKERS: string[] = Object.values(AI_INFRA_SUBTHEMES).flat();
export const TICKER_SUBTHEME: Record<string, string> = Object.fromEntries(
  Object.entries(AI_INFRA_SUBTHEMES).flatMap(([theme, names]) => names.map((t) => [t, theme])),
);
export const DEFENSIVE_BASKET = ["BRK-B", "WMT", "COST", "JNJ", "KO", "PG", "PEP"];

// --- Config (AMQSConfig) ---------------------------------------------------
export interface AmqsConfig {
  wFactorA: number;
  wFactorB: number;
  wFactorC: number;
  wFactorD: number;
  wMomentumSignal: number;
  wPullbackBuy: number;
  wTrendQuality: number;
  wVolAdjAlpha: number;
  wMacroFit: number;
  minMktCapUsd: number;
  maxVolAnnualized: number;
  maxBeta: number;
  maxSingleDayDrop90d: number;
  pullbackMin5d: number;
  pullbackMin20d: number;
  pullbackRsiOversold: number;
  requireAbove50dma: boolean;
  topN: number;
  maxPerSubtheme: number;
  tiltStrength: number;
  maxWeightPerName: number;
  minWeightPerName: number;
  maxDrawdown252d: number;
  riskOnVixMax: number;
  riskOffVixMin: number;
  defensiveQqq5dThreshold: number;
}

export const DEFAULT_AMQS_CONFIG: AmqsConfig = {
  wFactorA: 0.5,
  wFactorB: 0.3,
  wFactorC: 0.15,
  wFactorD: 0.05,
  wMomentumSignal: 0.35,
  wPullbackBuy: 0.15,
  wTrendQuality: 0.25,
  wVolAdjAlpha: 0.15,
  wMacroFit: 0.1,
  minMktCapUsd: 10e9,
  maxVolAnnualized: 1.0,
  maxBeta: 3.0,
  maxSingleDayDrop90d: -0.35,
  pullbackMin5d: -0.03,
  pullbackMin20d: -0.05,
  pullbackRsiOversold: 30.0,
  requireAbove50dma: true,
  topN: 10,
  maxPerSubtheme: 4,
  tiltStrength: 1.5,
  maxWeightPerName: 0.18,
  minWeightPerName: 0.04,
  maxDrawdown252d: -0.3,
  riskOnVixMax: 25.0,
  riskOffVixMin: 30.0,
  defensiveQqq5dThreshold: -0.08,
};

// --- Helper indicators (strategy.py _* 함수 1:1) ---------------------------
function safeReturn(closeIn: number[], n: number): number {
  const s = dropNaN(closeIn);
  if (s.length <= n) return Number.NaN;
  return atFromEnd(s, 1) / atFromEnd(s, n + 1) - 1.0;
}
function factor12_1(closeIn: number[]): number {
  const s = dropNaN(closeIn);
  if (s.length < 253) return Number.NaN;
  return atFromEnd(s, 21) / atFromEnd(s, 252) - 1.0;
}
function factor6_1(closeIn: number[]): number {
  const s = dropNaN(closeIn);
  if (s.length < 127) return Number.NaN;
  return atFromEnd(s, 21) / atFromEnd(s, 126) - 1.0;
}
function factor3_1(closeIn: number[]): number {
  const s = dropNaN(closeIn);
  if (s.length < 64) return Number.NaN;
  return atFromEnd(s, 21) / atFromEnd(s, 63) - 1.0;
}
function annVol(retsIn: number[], n = 60): number {
  const r = dropNaN(retsIn).slice(-n);
  if (r.length < Math.floor(n / 2)) return Number.NaN;
  return std(r, 1) * SQRT_252;
}
function sharpeLike(retsIn: number[], n = 126, rfAnn = 0.04): number {
  const r = dropNaN(retsIn).slice(-n);
  const sd = std(r, 1);
  if (r.length < Math.floor(n / 2) || sd === 0) return Number.NaN;
  const dailyRf = Math.pow(1 + rfAnn, 1 / 252) - 1;
  return ((mean(r) - dailyRf) / sd) * SQRT_252;
}
function maxDrawdown(closeIn: number[], n = 252): number {
  const s = dropNaN(closeIn).slice(-n);
  if (s.length < 30) return Number.NaN;
  const peak = cumMax(s);
  return minOf(s.map((v, i) => v / peak[i] - 1.0));
}
function rsi14(closeIn: number[], n = 14): number {
  const s = dropNaN(closeIn);
  if (s.length < n + 1) return Number.NaN;
  const delta = diff(s);
  const gain = ewmMeanAdjustFalse(
    delta.map((d) => (isNum(d) ? Math.max(d, 0) : Number.NaN)),
    1 / n,
  );
  const loss = ewmMeanAdjustFalse(
    delta.map((d) => (isNum(d) ? Math.max(-d, 0) : Number.NaN)),
    1 / n,
  );
  const lossLast = atFromEnd(loss, 1);
  if (lossLast === 0) return Number.NaN; // pandas: loss.replace(0, nan) → rs NaN → rsi NaN
  const rs = atFromEnd(gain, 1) / lossLast;
  return 100 - 100 / (1 + rs);
}
function dist52wHigh(closeIn: number[]): number {
  const s = dropNaN(closeIn).slice(-252);
  if (s.length === 0) return Number.NaN;
  return atFromEnd(s, 1) / maxOf(s) - 1.0;
}
function aboveMa(closeIn: number[], n: number): boolean {
  const s = dropNaN(closeIn);
  if (s.length < n) return false;
  return atFromEnd(s, 1) > mean(s.slice(-n));
}
function positiveMonthCount(closeIn: number[], months = 12): number {
  const s = dropNaN(closeIn);
  if (s.length < months * 21 + 1) return 0;
  const sampled: number[] = []; // s.iloc[::-21] (최근→과거)
  for (let i = s.length - 1; i >= 0; i -= 21) sampled.push(s[i]);
  const recent = sampled.slice(0, months + 1).reverse(); // iloc[:13][::-1] (과거→최근)
  let cnt = 0;
  for (let i = 1; i < recent.length; i++) if (recent[i] / recent[i - 1] - 1 > 0) cnt++;
  return cnt;
}
function maxSingleDayDrop(closeIn: number[], n = 90): number {
  const s = dropNaN(closeIn).slice(-(n + 1));
  if (s.length < 2) return 0.0;
  return minOf(dropNaN(pctChange(s)));
}
function beta(retsIn: number[], mktRetsIn: number[], n = 252): number {
  const r = dropNaN(retsIn).slice(-n);
  const m = dropNaN(mktRetsIn).slice(-n);
  const len = Math.min(r.length, m.length);
  if (len < 60) return Number.NaN;
  const rr = r.slice(-len);
  const mm = m.slice(-len);
  const mVar = std(mm, 1) ** 2;
  if (mVar === 0) return Number.NaN;
  const mr = mean(rr);
  const mm_ = mean(mm);
  let cov = 0;
  for (let i = 0; i < len; i++) cov += (rr[i] - mr) * (mm[i] - mm_);
  cov /= len - 1;
  return cov / mVar;
}

/** numpy 기반 _zscore: 모집단 std(ddof=0), nan→0, 표본<2 또는 sd==0 → 전부 0. */
export function zscore(values: number[]): number[] {
  const valid = values.filter(isNum);
  if (valid.length < 2) return values.map(() => 0);
  const mu = mean(valid);
  const sd = std(valid, 0);
  if (sd === 0) return values.map(() => 0);
  return values.map((v) => (isNum(v) ? (v - mu) / sd : 0));
}

// --- Per-ticker metrics ----------------------------------------------------
export interface TickerMetrics {
  ticker: string;
  price: number;
  subtheme: string;
  factorA12_1: number;
  factorB6_1: number;
  factorC3_1: number;
  factorDInvVol: number;
  ret5d: number;
  ret20d: number;
  ret60d: number;
  vol60d: number;
  sharpe6m: number;
  mdd12m: number;
  rsi14: number;
  dist52wHigh: number;
  above50dma: boolean;
  above200dma: boolean;
  positiveMonths12m: number;
  maxSingleDayDrop90d: number;
  betaQqq: number;
  filteredOut: boolean;
  filterReason: string;
  zA: number;
  zB: number;
  zC: number;
  zD: number;
  fourFactorComposite: number;
  scoreMomentum: number;
  scorePullback: number;
  scoreQuality: number;
  scoreVolAlpha: number;
  scoreMacro: number;
  totalScore100: number;
  selected: boolean;
  signal: AmqsSignal;
  reason: string;
  weight: number;
}

export type AmqsSignal =
  | "DIP_BUY"
  | "CENTER"
  | "SATELLITE"
  | "TACTICAL"
  | "REDUCE"
  | "EXIT"
  | "EXCLUDED"
  | "HOLD";

export interface AmqsTickerInput {
  ticker: string;
  closes: number[]; // 시간 오름차순 종가
}

function measure(inputs: AmqsTickerInput[], qqqCloses?: number[]): TickerMetrics[] {
  const marketRets = qqqCloses ? pctChange(qqqCloses) : null;
  const out: TickerMetrics[] = [];
  for (const { ticker, closes: p } of inputs) {
    if (dropNaN(p).length === 0) continue;
    const r = pctChange(p);
    const vol = annVol(r, 60);
    out.push({
      ticker,
      price: atFromEnd(dropNaN(p), 1),
      subtheme: TICKER_SUBTHEME[ticker] ?? "Other",
      factorA12_1: factor12_1(p),
      factorB6_1: factor6_1(p),
      factorC3_1: factor3_1(p),
      factorDInvVol: isNum(vol) && vol > 0 ? 1.0 / vol : Number.NaN,
      ret5d: safeReturn(p, 5),
      ret20d: safeReturn(p, 20),
      ret60d: safeReturn(p, 60),
      vol60d: vol,
      sharpe6m: sharpeLike(r, 126),
      mdd12m: maxDrawdown(p, 252),
      rsi14: rsi14(p, 14),
      dist52wHigh: dist52wHigh(p),
      above50dma: aboveMa(p, 50),
      above200dma: aboveMa(p, 200),
      positiveMonths12m: positiveMonthCount(p, 12),
      maxSingleDayDrop90d: maxSingleDayDrop(p, 90),
      betaQqq: marketRets ? beta(r, marketRets) : Number.NaN,
      filteredOut: false,
      filterReason: "",
      zA: 0,
      zB: 0,
      zC: 0,
      zD: 0,
      fourFactorComposite: 0,
      scoreMomentum: 0,
      scorePullback: 0,
      scoreQuality: 0,
      scoreVolAlpha: 0,
      scoreMacro: 0,
      totalScore100: 0,
      selected: false,
      signal: "HOLD",
      reason: "",
      weight: 0,
    });
  }
  return out;
}

function applyPrefilter(metrics: TickerMetrics[], cfg: AmqsConfig, marketCaps: Record<string, number>): void {
  for (const m of metrics) {
    const reasons: string[] = [];
    const mc = marketCaps[m.ticker];
    if (mc !== undefined && mc < cfg.minMktCapUsd) reasons.push(`mkt_cap<$${(cfg.minMktCapUsd / 1e9).toFixed(0)}B`);
    if (isNum(m.vol60d) && m.vol60d > cfg.maxVolAnnualized) reasons.push(`vol60d>${(cfg.maxVolAnnualized * 100).toFixed(0)}%`);
    if (isNum(m.betaQqq) && m.betaQqq > cfg.maxBeta) reasons.push(`beta>${cfg.maxBeta.toFixed(1)}`);
    if (m.maxSingleDayDrop90d < cfg.maxSingleDayDrop90d) reasons.push(`단일일${(m.maxSingleDayDrop90d * 100).toFixed(0)}%폭락`);
    if (reasons.length) {
      m.filteredOut = true;
      m.filterReason = reasons.join(" · ");
    }
  }
}

function pullbackRaw(m: TickerMetrics, cfg: AmqsConfig): number {
  if (!isNum(m.factorA12_1) || m.factorA12_1 <= 0) return 0.0;
  if (!isNum(m.factorB6_1) || m.factorB6_1 <= 0) return 0.0;
  if (cfg.requireAbove50dma && !m.above50dma) return 0.0;
  const dip5d = isNum(m.ret5d) ? Math.max(0.0, -m.ret5d) : 0.0;
  const dip20d = isNum(m.ret20d) ? Math.max(0.0, -m.ret20d) : 0.0;
  if (dip5d < Math.abs(cfg.pullbackMin5d) && dip20d < Math.abs(cfg.pullbackMin20d)) return 0.0;
  const trendMult = 1.0 + Math.min(Math.max(m.factorA12_1, 0.0), 1.0);
  const base = (0.7 * dip5d + 0.3 * dip20d) * trendMult;
  let bonus = 0.0;
  if (isNum(m.rsi14)) {
    if (m.rsi14 <= cfg.pullbackRsiOversold) bonus = (0.02 * (cfg.pullbackRsiOversold - m.rsi14)) / cfg.pullbackRsiOversold;
    else if (m.rsi14 < 40) bonus = (0.005 * (40 - m.rsi14)) / 10;
  }
  return base + bonus;
}

function scoreAll(metrics: TickerMetrics[], cfg: AmqsConfig, macroFit: Record<string, number>): void {
  // 1. 4-Factor composite (z)
  const za = zscore(metrics.map((m) => m.factorA12_1));
  const zb = zscore(metrics.map((m) => m.factorB6_1));
  const zc = zscore(metrics.map((m) => m.factorC3_1));
  const zd = zscore(metrics.map((m) => m.factorDInvVol));
  metrics.forEach((m, i) => {
    m.zA = za[i];
    m.zB = zb[i];
    m.zC = zc[i];
    m.zD = zd[i];
    m.fourFactorComposite = cfg.wFactorA * za[i] + cfg.wFactorB * zb[i] + cfg.wFactorC * zc[i] + cfg.wFactorD * zd[i];
  });

  // 2. Dim1 모멘텀(35)
  for (const m of metrics) {
    const ffcPct = clip((m.fourFactorComposite + 2) / 4, 0, 1);
    const d52 = m.dist52wHigh;
    let highPts: number;
    if (!isNum(d52)) highPts = 0.5;
    else if (d52 >= -0.01) highPts = 1.0;
    else if (d52 >= -0.05) highPts = 1.0 - ((Math.abs(d52) - 0.01) / 0.04) * 0.5;
    else if (d52 >= -0.1) highPts = 0.5 - ((Math.abs(d52) - 0.05) / 0.05) * 0.5;
    else highPts = 0.0;
    const trendPts = m.positiveMonths12m / 12;
    m.scoreMomentum = 100 * (0.6 * ffcPct + 0.25 * highPts + 0.15 * trendPts);
  }

  // 3. Dim2 단기하락매수(15)
  const pbRaw = metrics.map((m) => pullbackRaw(m, cfg));
  const pbZ = zscore(pbRaw);
  metrics.forEach((m, i) => {
    let pbPct = clip((pbZ[i] + 1) / 3, 0, 1);
    if (pbRaw[i] === 0) pbPct = 0.0;
    m.scorePullback = 100 * pbPct;
  });

  // 4. Dim3 추세품질(25)
  for (const m of metrics) {
    const above200Pts = m.above200dma ? 1.0 : 0.0;
    let accelPts = 0.0;
    if (isNum(m.factorB6_1) && isNum(m.factorC3_1)) {
      const accelDiff = m.factorC3_1 - m.factorB6_1 / 2;
      accelPts = clip((accelDiff + 0.1) / 0.2, 0, 1);
    }
    m.scoreQuality = 100 * (0.6 * above200Pts + 0.4 * accelPts);
  }

  // 5. Dim4 변동성조정알파(15)
  const shZ = zscore(metrics.map((m) => m.sharpe6m));
  metrics.forEach((m, i) => {
    const shPct = clip((shZ[i] + 1.5) / 3, 0, 1);
    let mddPts = 1.0;
    if (isNum(m.mdd12m)) {
      if (m.mdd12m >= -0.3) mddPts = 1.0;
      else if (m.mdd12m >= -0.45) mddPts = 1.0 - (Math.abs(m.mdd12m) - 0.3) / 0.15;
      else mddPts = 0.0;
    }
    m.scoreVolAlpha = 100 * (0.7 * shPct + 0.3 * mddPts);
  });

  // 6. Dim5 거시(10)
  for (const m of metrics) m.scoreMacro = macroFit[m.ticker] ?? 70.0;

  // 7. Total
  for (const m of metrics) {
    m.totalScore100 =
      cfg.wMomentumSignal * m.scoreMomentum +
      cfg.wPullbackBuy * m.scorePullback +
      cfg.wTrendQuality * m.scoreQuality +
      cfg.wVolAdjAlpha * m.scoreVolAlpha +
      cfg.wMacroFit * m.scoreMacro;
  }

  // 8. Signal
  for (const m of metrics) {
    if (m.filteredOut) {
      m.signal = "EXCLUDED";
      m.reason = `사전 필터 탈락: ${m.filterReason}`;
      continue;
    }
    if (isNum(m.mdd12m) && m.mdd12m < cfg.maxDrawdown252d) {
      m.signal = "EXIT";
      m.reason = `12M MDD ${(m.mdd12m * 100).toFixed(1)}% < ${(cfg.maxDrawdown252d * 100).toFixed(0)}% (장기 모멘텀 붕괴)`;
      continue;
    }
    if (m.scorePullback > 60 && m.scoreMomentum > 50) {
      m.signal = "DIP_BUY";
      m.reason = "단기 하락 + 추세 유지";
    } else if (m.totalScore100 >= 80) {
      m.signal = "CENTER";
      m.reason = `중심 포지션 (점수 ${m.totalScore100.toFixed(0)}/100)`;
    } else if (m.totalScore100 >= 65) {
      m.signal = "SATELLITE";
      m.reason = `위성 포지션 (점수 ${m.totalScore100.toFixed(0)}/100)`;
    } else if (m.totalScore100 >= 50) {
      m.signal = "TACTICAL";
      m.reason = `전술적 보유 (점수 ${m.totalScore100.toFixed(0)}/100)`;
    } else {
      m.signal = "REDUCE";
      m.reason = `비중 축소 (점수 ${m.totalScore100.toFixed(0)}/100)`;
    }
  }
}

function selectTopN(metrics: TickerMetrics[], cfg: AmqsConfig): TickerMetrics[] {
  const eligible = metrics
    .filter((m) => !["EXIT", "EXCLUDED", "REDUCE"].includes(m.signal))
    .sort((a, b) => b.totalScore100 - a.totalScore100);
  const selected: TickerMetrics[] = [];
  const perTheme: Record<string, number> = {};
  for (const m of eligible) {
    if (selected.length >= cfg.topN) break;
    if ((perTheme[m.subtheme] ?? 0) >= cfg.maxPerSubtheme) continue;
    selected.push(m);
    perTheme[m.subtheme] = (perTheme[m.subtheme] ?? 0) + 1;
    m.selected = true;
  }
  return selected;
}

function allocate(metrics: TickerMetrics[], cfg: AmqsConfig, regime: RegimeLabel): void {
  const invested = regime === "RISK_OFF" ? 0.5 : regime === "DEFENSIVE" ? 0.0 : 1.0;
  for (const m of metrics) {
    m.selected = false;
    m.weight = 0.0;
  }
  const selected = selectTopN(metrics, cfg);
  if (!selected.length || invested === 0) return;
  const n = selected.length;
  const base = invested / n;
  let raw = selected.map((m) => Math.max(0.0, base * (1.0 + cfg.tiltStrength * (m.totalScore100 - 65) / 30)));
  raw = raw.map((w) => clip(w, cfg.minWeightPerName, cfg.maxWeightPerName));
  const s = raw.reduce((a, b) => a + b, 0);
  if (s > 0) raw = raw.map((w) => (w / s) * invested);
  selected.forEach((m, i) => (m.weight = raw[i]));
}

// --- Regime ----------------------------------------------------------------
export type RegimeLabel = "RISK_ON" | "RISK_OFF" | "DEFENSIVE";
export interface MacroRegime {
  label: RegimeLabel;
  qqqAbove200ma: boolean;
  vixLevel: number;
  qqq5dReturn: number;
  reason: string;
}

export function detectRegime(qqqCloses: number[], vixCloses: number[], cfg: AmqsConfig): MacroRegime {
  const qqq = dropNaN(qqqCloses);
  const vix = dropNaN(vixCloses);
  if (qqq.length < 200 || vix.length === 0) {
    return { label: "RISK_ON", qqqAbove200ma: true, vixLevel: 20.0, qqq5dReturn: 0.0, reason: "데이터 부족 — 기본 Risk-On" };
  }
  const qqqLast = atFromEnd(qqq, 1);
  const qqq200ma = mean(qqq.slice(-200));
  const above200 = qqqLast > qqq200ma;
  const vixLast = atFromEnd(vix, 1);
  const qqq5d = qqq.length >= 6 ? atFromEnd(qqq, 1) / atFromEnd(qqq, 6) - 1.0 : 0.0;

  if (qqq5d < cfg.defensiveQqq5dThreshold) {
    return { label: "DEFENSIVE", qqqAbove200ma: above200, vixLevel: vixLast, qqq5dReturn: qqq5d, reason: `QQQ 5일 ${(qqq5d * 100).toFixed(1)}% 급락 → 방어 바스켓 전환` };
  }
  if (!above200 || vixLast > cfg.riskOffVixMin) {
    const d: string[] = [];
    if (!above200) d.push(`QQQ < 200MA (${qqqLast.toFixed(1)} vs ${qqq200ma.toFixed(1)})`);
    if (vixLast > cfg.riskOffVixMin) d.push(`VIX ${vixLast.toFixed(1)} > ${cfg.riskOffVixMin.toFixed(0)}`);
    return { label: "RISK_OFF", qqqAbove200ma: above200, vixLevel: vixLast, qqq5dReturn: qqq5d, reason: d.join(" · ") };
  }
  return { label: "RISK_ON", qqqAbove200ma: above200, vixLevel: vixLast, qqq5dReturn: qqq5d, reason: `QQQ +200MA, VIX ${vixLast.toFixed(1)}<25, 5D ${(qqq5d * 100).toFixed(1)}%` };
}

// --- 대시보드 시그널 매핑 (STRATEGY-ANALYSIS.md §2.5) ----------------------
export function toDashboardSignal(s: AmqsSignal): DashboardSignal | null {
  switch (s) {
    case "DIP_BUY":
    case "CENTER":
      return "BUY";
    case "SATELLITE":
    case "TACTICAL":
      return "HOLD";
    case "REDUCE":
    case "EXIT":
      return "SELL";
    default:
      return null; // EXCLUDED / HOLD(미분류) → 미표시
  }
}

// --- End-to-end ------------------------------------------------------------
export interface RunAmqsOptions {
  qqqCloses?: number[];
  vixCloses?: number[];
  marketCaps?: Record<string, number>;
  macroFit?: Record<string, number>;
  config?: AmqsConfig;
}

export interface AmqsResult {
  regime: MacroRegime;
  metrics: TickerMetrics[]; // totalScore100 내림차순
}

export function runAmqs(inputs: AmqsTickerInput[], opts: RunAmqsOptions = {}): AmqsResult {
  const cfg = opts.config ?? DEFAULT_AMQS_CONFIG;
  const regime =
    opts.qqqCloses && opts.vixCloses
      ? detectRegime(opts.qqqCloses, opts.vixCloses, cfg)
      : ({ label: "RISK_ON", qqqAbove200ma: true, vixLevel: 20.0, qqq5dReturn: 0.0, reason: "거시 데이터 없음 — 기본 Risk-On" } as MacroRegime);

  const metrics = measure(inputs, opts.qqqCloses);
  applyPrefilter(metrics, cfg, opts.marketCaps ?? {});
  scoreAll(metrics, cfg, opts.macroFit ?? {});
  allocate(metrics, cfg, regime.label);
  metrics.sort((a, b) => b.totalScore100 - a.totalScore100);
  return { regime, metrics };
}
