/**
 * ARDS-X Regime Classifier — 원본 quant/classifier.py 1:1.
 * 2축(거시 침체 × 가격 스트레스) + 과매도 + 금리 라벨로 5상태 판정.
 */
import { minOf, pyRound } from "../series";
import { TECH, DECISION, HYSTERESIS } from "./config";
import type { TechRow } from "./technical";
import type { MacroComposite } from "./macro";
import { declineType, type RateStress, type DeclineType } from "./rates";
import type { HystConfirm } from "./hysteresis";

export const STATE_KR: Record<string, string> = {
  UPTREND_HEALTHY: "정상 상승추세",
  CORRECTION: "조정",
  OVERSOLD_BOUNCE: "단기 과매도 (반등 후보)",
  DOWNTREND_DISTRIBUTION: "하락 / 분배",
  RECESSION_REBALANCE: "자산 리밸런싱 (침체)",
};
export const STATE_ACTION: Record<string, string> = {
  UPTREND_HEALTHY: "RISK_ON",
  CORRECTION: "HOLD_ACCUMULATE",
  OVERSOLD_BOUNCE: "BUY_DIP_TACTICAL",
  DOWNTREND_DISTRIBUTION: "REDUCE",
  RECESSION_REBALANCE: "DEFENSIVE_ARDS",
};
const DECLINE_STATES = new Set(["CORRECTION", "OVERSOLD_BOUNCE", "DOWNTREND_DISTRIBUTION", "RECESSION_REBALANCE"]);

export interface Measure {
  tape_dd: number;
  breadth: number;
  complex_dd: number;
  trend_broken: boolean;
  idx_below_200: boolean;
  idx_deadcross: boolean;
  breadth_weak: boolean;
  decline_score: number;
  oversold_score: number;
  idx_rsi: number;
  price_stress: number;
}

type Agg = Record<string, number>;

export function measureRegime(indexRows: TechRow[], complexAgg: Agg): Measure {
  const T = TECH;
  const byT: Record<string, TechRow> = Object.fromEntries(indexRows.map((r) => [r.ticker, r]));
  const idxList = ["^GSPC", "^NDX"].filter((t) => t in byT).map((t) => byT[t]);
  const techRef = byT["^NDX"] ?? byT["^GSPC"] ?? null;

  const tapeDd = idxList.length ? minOf(idxList.map((r) => r.dd_from_high)) : 0.0;
  const breadth = complexAgg.breadth_above_200dma ?? 100.0;
  const complexDd = complexAgg.avg_dd_from_high ?? 0.0;

  const idxBelow200 = idxList.some((r) => !r.above_200dma);
  const idxDeadcross = idxList.some((r) => !r.golden_cross);
  const breadthWeak = breadth < T.breadth_weak;
  const trendBroken = idxBelow200 || idxDeadcross || breadthWeak;

  const declineScore = Math.max(complexAgg.avg_decline_score ?? 0.0, techRef ? techRef.decline_score : 0.0);
  const oversoldScore = Math.max(complexAgg.avg_oversold_score ?? 0.0, techRef ? techRef.oversold_score : 0.0);
  const idxRsi = idxList.length ? minOf(idxList.map((r) => r.rsi14)) : 50.0;
  const priceStress = pyRound(Math.min(100.0, 0.6 * declineScore + 0.4 * Math.min(100, (-tapeDd / T.dd_bear) * 100)), 1);

  return {
    tape_dd: tapeDd,
    breadth,
    complex_dd: complexDd,
    trend_broken: trendBroken,
    idx_below_200: idxBelow200,
    idx_deadcross: idxDeadcross,
    breadth_weak: breadthWeak,
    decline_score: declineScore,
    oversold_score: oversoldScore,
    idx_rsi: idxRsi,
    price_stress: priceStress,
  };
}

export function rawClassify(M: number, m: Measure, prevState: string | null): string {
  const H = HYSTERESIS;
  const recThr = prevState === "RECESSION_REBALANCE" ? H.macro_rec_exit : H.macro_rec_enter;
  const ddCorr = prevState === "CORRECTION" || prevState === "OVERSOLD_BOUNCE" ? H.dd_corr_exit : H.dd_corr_enter;
  const ddDeep = prevState === "DOWNTREND_DISTRIBUTION" ? H.dd_deep_exit : H.dd_deep_enter;
  const rsiThr = prevState === "OVERSOLD_BOUNCE" ? H.rsi_exit : H.rsi_enter;

  const dd = m.tape_dd;
  const isOs = m.oversold_score >= 55 || m.idx_rsi < rsiThr;

  if (M >= recThr && (dd <= -ddCorr || m.trend_broken)) return "RECESSION_REBALANCE";
  if (m.trend_broken && dd <= -ddDeep) return "DOWNTREND_DISTRIBUTION";
  if (dd <= -ddCorr) return isOs ? "OVERSOLD_BOUNCE" : "CORRECTION";
  if (isOs) return "OVERSOLD_BOUNCE";
  return "UPTREND_HEALTHY";
}

export interface Verdict {
  state: string;
  state_kr: string;
  action: string;
  confidence: number;
  headline: string;
  handoff: string;
  decline_type: DeclineType;
  hysteresis: HystConfirm;
  axes: {
    macro: number;
    macro_phase: string;
    macro_phase_kr: string;
    price_stress: number;
    rate_stress: number | null;
    decline_score: number;
    oversold_score: number;
  };
  evidence: {
    tape_drawdown: number;
    complex_avg_drawdown: number;
    breadth_above_200dma: number;
    index_min_rsi14: number;
    trend_broken: boolean;
    idx_below_200dma: boolean;
    idx_deadcross: boolean;
    breadth_weak: boolean;
  };
}

function f0(x: number): string {
  return pyRound(x, 0).toFixed(0);
}
function f1(x: number): string {
  return pyRound(x, 1).toFixed(1);
}

function narrative(
  state: string,
  M: number,
  macro: MacroComposite,
  m: Measure,
  R: number | null,
  dtype: DeclineType,
): [string, string] {
  const p = macro.phase_kr;
  const dd = m.tape_dd;
  const br = m.breadth;
  const rtxt = R === null ? "" : ` · Rate Stress ${f0(R)}`;
  let h: string;
  let ho: string;
  if (state === "RECESSION_REBALANCE") {
    h = `거시 침체 신호(Composite ${f0(M)}, ${p}${rtxt})가 가격 하락을 주도. 지수 고점 대비 ${f1(dd)}%, 200일선 위 ${f0(br)}%. **자산 리밸런싱(침체) 국면**.`;
    ho = "➡️ ARDS / ARDS-Defense 방어 포트폴리오로 전환. 자본보존 우선.";
  } else if (state === "DOWNTREND_DISTRIBUTION") {
    h = `추세 붕괴 + 고점 대비 ${f1(dd)}%. 거시(Composite ${f0(M)}${rtxt})는 아직 침체 미만이나 **구조적 하락/분배**.`;
    ho = "➡️ '조정'으로 보지 말 것. 신규 저점매수 보류, 리스크 축소·헤지.";
  } else if (state === "OVERSOLD_BOUNCE") {
    h = `단기 과매도(과매도 ${f0(m.oversold_score)}, 지수 RSI ${f0(m.idx_rsi)}${rtxt}). 고점 대비 ${f1(dd)}%이나 추세 유지 → **기술적 반등 후보**.`;
    ho = "➡️ AMQS DIP_BUY 영역. 전술적·소규모 분할매수 + 타이트한 손절.";
  } else if (state === "CORRECTION") {
    h = `상승추세 내 건강한 눌림(고점 대비 ${f1(dd)}%, 200일선 위 ${f0(br)}%, 거시 Composite ${f0(M)}${rtxt}) → **조정**.`;
    ho = "➡️ 보유 유지 + 우량 빅테크/AI 인프라 분할매수.";
  } else {
    h = `정상 상승추세(고점 대비 ${f1(dd)}%, 200일선 위 ${f0(br)}%, 거시 Composite ${f0(M)}/${p}${rtxt}). 하락·침체 신호 없음.`;
    ho = "➡️ 리스크온 유지. AMQS 모멘텀 전략 비중 정상.";
  }
  if (dtype.code !== "NONE") {
    h += `  하락유형: **${dtype.kr}**.`;
    ho += `  〔${dtype.kr}〕 ${dtype.tlt_guidance}`;
  }
  return [h, ho];
}

export function buildVerdict(
  state: string,
  rawState: string,
  confirm: HystConfirm,
  macro: MacroComposite,
  m: Measure,
  rate: RateStress,
  _asofDate: string,
): Verdict {
  void rawState;
  const M = macro.composite;
  const R = rate.score;
  const dtype = DECLINE_STATES.has(state)
    ? declineType(M, R, m.price_stress)
    : { code: "NONE", kr: "해당없음", tlt_guidance: "유의미한 하락 스트레스 없음." };

  const [headline, handoff] = narrative(state, M, macro, m, R, dtype);

  const macroHigh = M >= DECISION.macro_recession;
  const priceHigh = m.price_stress >= 50;
  let conf = 55;
  conf += macroHigh === priceHigh ? 18 : -5;
  conf += Math.min(15, (Math.abs(M - 50) / 50) * 15);
  conf += Math.min(12, (Math.abs(m.price_stress - 40) / 60) * 12);
  if (macro.n_missing >= 2) conf -= 12;
  if (rate.score === null) conf -= 6;
  if (confirm.pending) conf -= 10;
  conf = Math.trunc(Math.max(20, Math.min(95, conf)));

  return {
    state,
    state_kr: STATE_KR[state],
    action: STATE_ACTION[state],
    confidence: conf,
    headline,
    handoff,
    decline_type: dtype,
    hysteresis: confirm,
    axes: {
      macro: M,
      macro_phase: macro.phase,
      macro_phase_kr: macro.phase_kr,
      price_stress: m.price_stress,
      rate_stress: R,
      decline_score: pyRound(m.decline_score, 1),
      oversold_score: pyRound(m.oversold_score, 1),
    },
    evidence: {
      tape_drawdown: pyRound(m.tape_dd, 1),
      complex_avg_drawdown: pyRound(m.complex_dd, 1),
      breadth_above_200dma: m.breadth,
      index_min_rsi14: pyRound(m.idx_rsi, 1),
      trend_broken: m.trend_broken,
      idx_below_200dma: m.idx_below_200,
      idx_deadcross: m.idx_deadcross,
      breadth_weak: m.breadth_weak,
    },
  };
}
