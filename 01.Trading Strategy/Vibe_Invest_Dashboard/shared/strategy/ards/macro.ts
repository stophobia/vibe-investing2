/**
 * ARDS-X 5-Factor Recession Composite — 원본 quant/macro.py 1:1.
 * FRED 무료 CSV + 시장 프록시로 침체 Composite(0~100) 산출. 결측 성분은 가중치 재정규화.
 */
import { isNum, mean, minOf, lin, clip, pyRound } from "../series";
import { DSeries, dlen, dlast, datEnd, ratioIntersect, rollingMeanEndingAt } from "./dseries";
import { RECESSION_WEIGHTS, MACRO_PHASES } from "./config";

type Px = Record<string, DSeries>;
type Fred = Record<string, DSeries>;
type Detail = Record<string, number | boolean>;
interface FactorResult {
  score: number | null;
  status: string;
  detail: Detail;
}

/** a-b 를 날짜 교집합으로 정렬한 DSeries (yield curve 프록시용). */
function subIntersect(a: DSeries, b: DSeries): DSeries {
  const bMap = new Map<string, number>();
  for (let i = 0; i < b.dates.length; i++) if (isNum(b.values[i])) bMap.set(b.dates[i], b.values[i]);
  const dates: string[] = [];
  const values: number[] = [];
  for (let i = 0; i < a.dates.length; i++) {
    const bv = bMap.get(a.dates[i]);
    if (isNum(a.values[i]) && bv !== undefined) {
      dates.push(a.dates[i]);
      values.push(a.values[i] - bv);
    }
  }
  return { dates, values };
}

function factorYieldCurve(fred: Fred, px: Px): FactorResult {
  let s3m: DSeries | null = fred["T10Y3M"] ?? null;
  let s2y: DSeries | null = fred["T10Y2Y"] ?? null;
  let status = "live";
  const detail: Detail = {};
  const scores: number[] = [];

  if (!s3m && px["^TNX"] && px["^IRX"]) {
    const sub = subIntersect(px["^TNX"], px["^IRX"]);
    if (sub.values.length > 30) {
      s3m = sub;
      status = "proxy";
    }
  }
  if (!s2y && px["^TNX"] && px["^FVX"]) {
    const sub = subIntersect(px["^TNX"], px["^FVX"]);
    if (sub.values.length > 30) {
      s2y = sub;
      status = "proxy";
    }
  }
  if (!s3m && !s2y) return { score: null, status: "no data", detail: {} };

  if (s3m) {
    const v = dlast(s3m);
    detail[status === "live" ? "T10Y3M" : "T10Y3M(mkt)"] = pyRound(v, 2);
    scores.push(lin(v, 1.5, -0.5));
    const recent = s3m.values.length > 378 ? s3m.values.slice(-378) : s3m.values;
    if (v > 0 && minOf(recent) < 0) {
      detail["un_inversion_window"] = true;
      scores[scores.length - 1] = clip(scores[scores.length - 1] + 18, 0, 100);
    }
  }
  if (s2y) {
    const v2 = dlast(s2y);
    detail[status === "live" ? "T10Y2Y" : "T10Y5Y(mkt)"] = pyRound(v2, 2);
    scores.push(lin(v2, 1.5, -0.5));
  }
  return { score: mean(scores), status, detail };
}

function factorSahm(fred: Fred): FactorResult {
  const s = fred["UNRATE"];
  if (!s || dlen(s) < 15) return { score: null, status: "no data", detail: {} };
  const v = s.values;
  const n = v.length;
  const cur = rollingMeanEndingAt(v, n - 1, 3); // ma3.iloc[-1]
  const ma3Last12: number[] = [];
  for (let i = n - 12; i <= n - 1; i++) {
    const x = rollingMeanEndingAt(v, i, 3);
    if (isNum(x)) ma3Last12.push(x);
  }
  const trough = minOf(ma3Last12);
  const gap = cur - trough;
  const detail: Detail = {
    unrate: pyRound(dlast(s), 1),
    unrate_3m_ma: pyRound(cur, 2),
    sahm_gap: pyRound(gap, 2),
  };
  return { score: lin(gap, 0.0, 0.5), status: "live", detail };
}

function factorIsmProxy(px: Px): FactorResult {
  const detail: Detail = {};
  const sub: number[] = [];
  const cop = px["CPER"];
  const gold = px["GLD"];
  if (cop && gold) {
    const ratio = ratioIntersect(cop, gold);
    if (ratio.length > 130) {
      const chg = (ratio[ratio.length - 1] / ratio[ratio.length - 126] - 1) * 100;
      detail["copper_gold_6m_chg"] = pyRound(chg, 1);
      sub.push(lin(chg, 15.0, -15.0));
    }
  }
  const xli = px["XLI"];
  const spy = px["SPY"];
  if (xli && spy) {
    const rs = ratioIntersect(xli, spy);
    if (rs.length > 130) {
      const chg = (rs[rs.length - 1] / rs[rs.length - 126] - 1) * 100;
      detail["xli_spy_6m_chg"] = pyRound(chg, 1);
      sub.push(lin(chg, 8.0, -8.0));
    }
  }
  if (sub.length === 0) return { score: null, status: "no data", detail };
  return { score: mean(sub), status: "proxy", detail };
}

function factorLeiProxy(fred: Fred): FactorResult {
  const detail: Detail = {};
  const sub: number[] = [];
  const claims = fred["ICSA"];
  if (claims && dlen(claims) > 30) {
    const v = claims.values;
    const n = v.length;
    const c1 = rollingMeanEndingAt(v, n - 1, 4);
    const c26 = rollingMeanEndingAt(v, n - 26, 4);
    const chg = (c1 / c26 - 1) * 100;
    detail["claims_6m_chg"] = pyRound(chg, 1);
    sub.push(lin(chg, -25.0, 25.0));
  }
  const permit = fred["PERMIT"];
  if (permit && dlen(permit) > 8) {
    const chg = (dlast(permit) / datEnd(permit, 6) - 1) * 100;
    detail["permits_6m_chg"] = pyRound(chg, 1);
    sub.push(lin(chg, 15.0, -15.0));
  }
  if (sub.length === 0) return { score: null, status: "no data", detail };
  return { score: mean(sub), status: "proxy", detail };
}

function factorCredit(fred: Fred, px: Px): FactorResult {
  const oas = fred["BAMLH0A0HYM2"];
  const nfci = fred["NFCI"];
  const detail: Detail = {};
  const sub: number[] = [];
  let status = "live";
  if (oas) {
    const v = dlast(oas);
    detail["hy_oas_bp"] = Math.trunc(pyRound(v * 100, 0));
    sub.push(lin(v, 2.5, 6.0));
  }
  if (nfci) {
    const v = dlast(nfci);
    detail["nfci"] = pyRound(v, 2);
    sub.push(lin(v, -0.5, 0.5));
  }
  if (sub.length === 0 && px["HYG"] && px["IEF"]) {
    const rs = ratioIntersect(px["HYG"], px["IEF"]);
    if (rs.length > 130) {
      const chg = (rs[rs.length - 1] / rs[rs.length - 63] - 1) * 100;
      detail["hyg_ief_3m_chg"] = pyRound(chg, 1);
      sub.push(lin(chg, 4.0, -8.0));
      const hyg = px["HYG"].values;
      const dd = hyg.length >= 252 ? (hyg[hyg.length - 1] / Math.max(...hyg.slice(-252)) - 1) * 100 : 0.0;
      detail["hyg_drawdown"] = pyRound(dd, 1);
      sub.push(lin(dd, -1.0, -12.0));
      status = "proxy";
    }
  }
  if (sub.length === 0) return { score: null, status: "no data", detail: {} };
  return { score: mean(sub), status, detail };
}

export interface MacroComposite {
  composite: number;
  phase: string;
  phase_kr: string;
  n_live: number;
  n_proxy: number;
  n_missing: number;
  components: Record<string, { label: string; weight: number; score: number | null; status: string; detail: Detail }>;
}

const FACTOR_LABELS: Record<string, string> = {
  A_yield_curve: "수익률 곡선",
  B_sahm: "Sahm Rule",
  C_ism_proxy: "ISM 프록시",
  D_lei_proxy: "LEI 프록시",
  E_credit: "신용/금융",
};

export function recessionComposite(fred: Fred, px: Px): MacroComposite {
  const factors: Record<string, FactorResult> = {
    A_yield_curve: factorYieldCurve(fred, px),
    B_sahm: factorSahm(fred),
    C_ism_proxy: factorIsmProxy(px),
    D_lei_proxy: factorLeiProxy(fred),
    E_credit: factorCredit(fred, px),
  };
  const availKeys = Object.keys(factors).filter((k) => factors[k].score !== null);
  const wsum = availKeys.reduce((a, k) => a + RECESSION_WEIGHTS[k], 0) || 1.0;
  const composite = availKeys.reduce((a, k) => a + RECESSION_WEIGHTS[k] * (factors[k].score as number), 0) / wsum;

  let phaseCode = "EXPANSION";
  let phaseKr = "확장기";
  for (const [hi, code, kr] of MACRO_PHASES) {
    if (composite < hi) {
      phaseCode = code;
      phaseKr = kr;
      break;
    }
  }

  const components: MacroComposite["components"] = {};
  for (const k of Object.keys(factors)) {
    const f = factors[k];
    components[k] = {
      label: FACTOR_LABELS[k],
      weight: RECESSION_WEIGHTS[k],
      score: f.score === null ? null : pyRound(f.score, 1),
      status: f.status,
      detail: f.detail,
    };
  }

  return {
    composite: pyRound(composite, 1),
    phase: phaseCode,
    phase_kr: phaseKr,
    n_live: Object.values(factors).filter((f) => f.status === "live").length,
    n_proxy: Object.values(factors).filter((f) => f.status === "proxy").length,
    n_missing: Object.values(factors).filter((f) => f.score === null).length,
    components,
  };
}
