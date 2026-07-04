/**
 * Portfolio constructor — selects target holdings from scored snapshots.
 * Implements the Buffer rule and sector concentration cap of BuyKorea.md:
 *
 *  · 신규 편입: 종합 점수 전체 순위 상위 numHoldings(20) 이내.
 *  · 기존 보유: 순위가 bufferOut(30) 이내이면 계속 보유, 벗어나면 매도.
 *  · 매도 발생 시 상위 순위 미보유 종목부터 순서대로 신규 편입하여 20종목 유지.
 *  · 단일 WICS 대분류 섹터 비중 <= sectorCapPct(35% -> 7종목).
 */
import type { BacktestParams, SectorCode, StockSnapshot } from "../types.js";

export interface Target {
  code: string;
  sector: SectorCode;
}

export function portfolioConstructor(
  scored: StockSnapshot[],
  currentHoldings: Set<string>,
  params: BacktestParams,
): Target[] {
  const ranked = [...scored]
    .filter((s) => s.compositeScore !== undefined)
    .sort((a, b) => (b.compositeScore! - a.compositeScore!));
  const rankOf = new Map<string, number>();
  ranked.forEach((s, i) => rankOf.set(s.code, i + 1)); // 1-based

  const held = ranked.filter((s) => currentHoldings.has(s.code) && rankOf.get(s.code)! <= params.bufferOut);
  const newEntries = ranked.filter((s) => !currentHoldings.has(s.code));

  // Priority: keep eligible existing holdings, then best-ranked new names,
  // finally (fallback) any remaining to reach the target count.
  const ordered = [...held, ...newEntries];

  const sectorCap = Math.floor(params.sectorCapPct * params.numHoldings);
  const sectorCount = new Map<SectorCode, number>();
  const selected: Target[] = [];

  for (const s of ordered) {
    if (selected.length >= params.numHoldings) break;
    const c = sectorCount.get(s.sector) ?? 0;
    if (c >= sectorCap) continue; // 섹터 집중 한도 초과 -> 차순위 타 섹터로 대체
    selected.push({ code: s.code, sector: s.sector });
    sectorCount.set(s.sector, c + 1);
  }

  // If sector caps left us short, relax the cap to still hold numHoldings.
  if (selected.length < params.numHoldings) {
    const chosen = new Set(selected.map((t) => t.code));
    for (const s of ordered) {
      if (selected.length >= params.numHoldings) break;
      if (chosen.has(s.code)) continue;
      selected.push({ code: s.code, sector: s.sector });
      chosen.add(s.code);
    }
  }

  return selected;
}
