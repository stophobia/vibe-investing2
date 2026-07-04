/**
 * Universe filter — determines the eligible stock set at each rebalance date,
 * strictly point-in-time. Implements the [유니버스] block of BuyKorea.md.
 */
import type { DataStore } from "../data/loader.js";
import type { BacktestParams, SectorCode } from "../types.js";
import { addMonths } from "../util.js";

export interface UniverseMember {
  code: string;
  sector: SectorCode;
}

export function universeFilter(ds: DataStore, asOf: string, params: BacktestParams): UniverseMember[] {
  const snapshot = ds.universe.get(asOf);
  if (!snapshot) return [];
  const dayIdx = ds.idxOnOrBefore(asOf);
  const out: UniverseMember[] = [];

  for (const row of snapshot.values()) {
    // 코스피200 구성 종목만.
    if (!row.inKospi200) continue;
    // 금융업 제외 (WICS 대분류 '금융').
    if (row.sector === "금융") continue;
    // 관리종목 / 거래정지 제외.
    if (row.managed || row.suspended) continue;
    // 상장 후 12개월 미경과 제외.
    if (row.listedDate > addMonths(asOf, -params.minListedMonths)) continue;
    // 상장폐지 종목 제외 (해당 시점 기준).
    if (row.delistedDate && row.delistedDate <= asOf) continue;

    // 완전자본잠식 (equity <= 0) 제외 — 포인트인타임 재무.
    const equity = ds.pitLatest(row.code, "equity", asOf);
    if (equity && equity.value <= 0) continue;

    // 유동성 필터: 최근 20거래일 평균 거래대금 >= 50억.
    if (dayIdx >= 0) {
      const val = ds.value.get(row.code);
      if (!val) continue;
      let sum = 0;
      let cnt = 0;
      for (let i = Math.max(0, dayIdx - 19); i <= dayIdx; i++) {
        if (Number.isFinite(val[i])) {
          sum += val[i];
          cnt++;
        }
      }
      if (cnt < 15) continue; // insufficient trading history
      if (sum / cnt < params.minAvgValue) continue;
    }

    out.push({ code: row.code, sector: row.sector });
  }
  return out;
}
