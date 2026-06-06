/**
 * ARDS-X Rate Stress 서브컴포지트 + 하락유형 라벨 — 원본 quant/rates.py 1:1.
 */
import { isNum, std, pctChange, lin, pyRound, SQRT_252 } from "../series";
import { DSeries, ddropNaN, dlen, dlast, datEnd } from "./dseries";
import { RATE, RATE_WEIGHTS, DECISION } from "./config";

type Px = Record<string, DSeries>;
type Fred = Record<string, DSeries>;

/** 금리 시리즈(%)의 days일 변화 → bp. */
function chgBp(series: DSeries, days = 20): number | null {
  const s = ddropNaN(series);
  if (dlen(s) <= days) return null;
  return (dlast(s) - datEnd(s, days + 1)) * 100.0;
}

/** (window <= last).mean()*100 — 1년(252) 또는 전체 백분위. */
function percentileOfLast(values: number[]): number {
  const last = values[values.length - 1];
  const window = values.length >= 252 ? values.slice(-252) : values;
  const cnt = window.reduce((a, v) => a + (v <= last ? 1 : 0), 0);
  return (cnt / window.length) * 100;
}

export interface RateStress {
  score: number | null;
  components: Record<string, { label: string; weight: number; score: number | null; status: string }>;
  detail: Record<string, number>;
  n_live: number;
  n_proxy: number;
  n_missing: number;
}

const RATE_LABELS: Record<string, string> = {
  R1_long_yield_vel: "10Y 금리속도",
  R2_rate_path: "정책경로(2Y/5Y)",
  R3_breakeven: "기대인플레",
  R4_bond_vol: "채권변동성",
};

export function rateStress(px: Px, fred: Fred): RateStress {
  const parts: Record<string, number> = {};
  const detail: Record<string, number> = {};
  const status: Record<string, string> = {};

  // R1: 10Y 금리 속도 (^TNX)
  if (px["^TNX"]) {
    const bp = chgBp(px["^TNX"], 20);
    if (bp !== null) {
      detail["us10y_20d_bp"] = pyRound(bp, 1);
      parts["R1_long_yield_vel"] = lin(bp, 0.0, RATE.yield_vel_bp_hi);
      status["R1_long_yield_vel"] = "live";
    }
  }

  // R2: 2Y(FRED DGS2) 우선, 없으면 5Y(^FVX)
  const s2 = fred["DGS2"];
  if (s2) {
    const bp = chgBp(s2, 20);
    if (bp !== null) {
      detail["us2y_20d_bp"] = pyRound(bp, 1);
      parts["R2_rate_path"] = lin(bp, 0.0, RATE.path_vel_bp_hi);
      status["R2_rate_path"] = "live";
    }
  } else if (px["^FVX"]) {
    const bp = chgBp(px["^FVX"], 20);
    if (bp !== null) {
      detail["us5y_20d_bp(mkt)"] = pyRound(bp, 1);
      parts["R2_rate_path"] = lin(bp, 0.0, RATE.path_vel_bp_hi);
      status["R2_rate_path"] = "proxy";
    }
  }

  // R3: 5Y 브레이크이븐 (FRED T5YIE)
  const bei = fred["T5YIE"];
  if (bei) {
    const bp = chgBp(bei, 20);
    if (bp !== null) {
      detail["bei5y_20d_bp"] = pyRound(bp, 1);
      detail["bei5y_level"] = pyRound(dlast(ddropNaN(bei)), 2);
      parts["R3_breakeven"] = lin(bp, 0.0, RATE.bei_vel_bp_hi);
      status["R3_breakeven"] = "live";
    }
  }

  // R4: 채권 변동성 — MOVE 우선, 없으면 10Y 실현변동성 백분위
  if (px["^MOVE"]) {
    const s = ddropNaN(px["^MOVE"]);
    if (dlen(s) > 130) {
      const pct = percentileOfLast(s.values);
      detail["move_level"] = pyRound(dlast(s), 1);
      detail["move_pctile_1y"] = pyRound(pct, 0);
      parts["R4_bond_vol"] = pct;
      status["R4_bond_vol"] = "live";
    }
  }
  if (!("R4_bond_vol" in parts) && px["^TNX"]) {
    const s = ddropNaN(px["^TNX"]);
    if (dlen(s) > 130) {
      const pc = pctChange(s.values);
      const rv: number[] = [];
      for (let i = 0; i < pc.length; i++) {
        const win = pc.slice(i - 19, i + 1);
        if (i >= 20 && win.every(isNum)) rv.push(std(win, 1) * SQRT_252 * 100);
      }
      if (rv.length > 130) {
        const pct = percentileOfLast(rv);
        detail["us10y_realvol_pctile_1y(mkt)"] = pyRound(pct, 0);
        parts["R4_bond_vol"] = pct;
        status["R4_bond_vol"] = "proxy";
      }
    }
  }

  if (Object.keys(parts).length === 0) {
    return { score: null, components: {}, detail: {}, n_live: 0, n_proxy: 0, n_missing: 4 };
  }

  const wsum = Object.keys(parts).reduce((a, k) => a + RATE_WEIGHTS[k], 0) || 1.0;
  const score = Object.keys(parts).reduce((a, k) => a + RATE_WEIGHTS[k] * parts[k], 0) / wsum;

  const components: RateStress["components"] = {};
  for (const k of Object.keys(RATE_WEIGHTS)) {
    components[k] = {
      label: RATE_LABELS[k],
      weight: RATE_WEIGHTS[k],
      score: k in parts ? pyRound(parts[k], 1) : null,
      status: status[k] ?? "no data",
    };
  }

  return {
    score: pyRound(score, 1),
    components,
    detail,
    n_live: Object.values(status).filter((v) => v === "live").length,
    n_proxy: Object.values(status).filter((v) => v === "proxy").length,
    n_missing: 4 - Object.keys(parts).length,
  };
}

// --- 하락유형 라벨 ---------------------------------------------------------
export interface DeclineType {
  code: string;
  kr: string;
  tlt_guidance: string;
}
const DECLINE_TYPES: Record<string, [string, string]> = {
  RECESSION_DRIVEN: ["침체형", "TLT/IEF 듀레이션 = 헤지 (금리 인하 수혜). ARDS Tier 2 장기국채 비중 활성화 OK."],
  RATE_DRIVEN: ["금리형", "⚠️ TLT/IEF = 추가 익스포저 (주식과 동반 하락). ARDS Tier 2 장기국채 축소 → 단기채(BIL/SHV)·금(GLD) 대체."],
  VALUATION_DRIVEN: ["밸류에이션형", "금리·침체 무관한 멀티플 압축/크라우딩 청산. TLT 헤지 효과 제한적, 현금·인버스(SH/PSQ)가 더 적합."],
  NONE: ["해당없음", "유의미한 하락 스트레스 없음."],
};

export function declineType(macroComposite: number, rateScore: number | null, priceStress: number): DeclineType {
  let code: string;
  if (priceStress < RATE.label_min_stress) code = "NONE";
  else if (macroComposite >= DECISION.macro_recession) code = "RECESSION_DRIVEN";
  else if (rateScore !== null && rateScore >= RATE.stress_high) code = "RATE_DRIVEN";
  else code = "VALUATION_DRIVEN";
  const [kr, guidance] = DECLINE_TYPES[code];
  return { code, kr, tlt_guidance: guidance };
}
