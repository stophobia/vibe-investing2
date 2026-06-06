/**
 * ARDS-X 오케스트레이션 — 원본 quant/run.py build() 1:1 (데이터 fetch 제외).
 * px/fred 를 입력으로 받아 verdict + 보조 데이터를 산출. 데이터 수집은 DataProvider 가 담당.
 */
import { INDICES, COMPLEX, GROUP_KR } from "./config";
import { analyzeUniverse, aggregate, type TechRow, type NameGroup } from "./technical";
import { recessionComposite, type MacroComposite } from "./macro";
import { rateStress, type RateStress } from "./rates";
import { measureRegime, rawClassify, buildVerdict, type Measure, type Verdict } from "./classifier";
import { applyHysteresis, type HystState, type HystConfirm } from "./hysteresis";
import type { DSeries } from "./dseries";

export { freshState } from "./hysteresis";
export type { HystState } from "./hysteresis";

export interface ArdsResult {
  verdict: Verdict;
  macro: MacroComposite;
  rate: RateStress;
  index_rows: TechRow[];
  complex_rows: TechRow[];
  complex_agg: Record<string, number>;
  groups: Record<string, Record<string, number | string>>;
  measure: Measure;
  raw: string;
  confirm: HystConfirm;
  state: HystState;
}

/** 대시보드 통일 시그널 매핑 (STRATEGY-ANALYSIS §1.6). state/action → enum. */
export function toDashboardSignal(action: string): "BUY" | "SELL" | "HOLD" {
  switch (action) {
    case "RISK_ON":
    case "BUY_DIP_TACTICAL":
      return "BUY";
    case "HOLD_ACCUMULATE":
      return "HOLD";
    case "REDUCE":
    case "DEFENSIVE_ARDS":
      return "SELL";
    default:
      return "HOLD";
  }
}

export function runArds(
  px: Record<string, DSeries>,
  fred: Record<string, DSeries>,
  prevState: HystState,
  today: string,
): ArdsResult {
  const macro = recessionComposite(fred, px);
  const rate = rateStress(px, fred);

  const nameGroup: NameGroup = {};
  for (const [t, name] of Object.entries(INDICES)) nameGroup[t] = [name, null];
  for (const [t, [name, group]] of Object.entries(COMPLEX)) nameGroup[t] = [name, group];

  const indexPx: Record<string, number[]> = {};
  for (const t of Object.keys(INDICES)) if (px[t]) indexPx[t] = px[t].values;
  const complexPx: Record<string, number[]> = {};
  for (const t of Object.keys(COMPLEX)) if (px[t]) complexPx[t] = px[t].values;

  const indexRows = analyzeUniverse(indexPx, nameGroup);
  const complexRows = analyzeUniverse(complexPx, nameGroup);
  const complexAgg = aggregate(complexRows) as Record<string, number>;

  const groups: ArdsResult["groups"] = {};
  for (const g of Object.keys(GROUP_KR)) {
    const gr = complexRows.filter((r) => r.group === g);
    if (gr.length) groups[g] = { label: GROUP_KR[g], ...(aggregate(gr) as Record<string, number>) };
  }

  const m = measureRegime(indexRows, complexAgg);
  const raw = rawClassify(macro.composite, m, prevState.committed);
  const { committed, confirm, state } = applyHysteresis(raw, prevState, today);
  const verdict = buildVerdict(committed, raw, confirm, macro, m, rate, today);

  return {
    verdict,
    macro,
    rate,
    index_rows: indexRows,
    complex_rows: complexRows,
    complex_agg: complexAgg,
    groups,
    measure: m,
    raw,
    confirm,
    state,
  };
}
