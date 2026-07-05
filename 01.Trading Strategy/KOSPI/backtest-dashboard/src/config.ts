import type { BacktestParams } from "./types.js";

// Default parameters implementing the BuyKorea.md specification (수정본).
export const DEFAULT_PARAMS: BacktestParams = {
  startDate: "2012-01-01",
  endDate: "2024-12-31",
  numHoldings: 20,
  bufferOut: 30, // keep existing holdings while rank <= 30 (buffer rule)
  sectorCapPct: 0.35, // single WICS sector <= 35% (7 names)
  weights: { quality: 0.4, value: 0.25, lowVol: 0.2, momentum: 0.15 },
  positionWeight: 0.05, // 5% equal weight
  rebalanceBand: 0.01, // skip trade if within +-1%p of target
  maxPositionWeight: 0.08, // trim back to 5% if drifts above 8%
  cost: {
    // 증권거래세 by year (2025 이후 0.15%). Parameterized per prompt.
    sellTaxByYear: {
      default: 0.0015,
      "2012": 0.003,
      "2013": 0.003,
      "2014": 0.003,
      "2015": 0.003,
      "2016": 0.003,
      "2017": 0.003,
      "2018": 0.003,
      "2019": 0.0025,
      "2020": 0.0025,
      "2021": 0.0023,
      "2022": 0.0023,
      "2023": 0.002,
      "2024": 0.0018,
      "2025": 0.0015,
    },
    commission: 0.00015, // 0.015% per side
    marketImpact: 0.001, // 10bp of traded value
  },
  crisis: {
    maBenchmarkMonths: 12,
    volThreshold: 0.3, // annualized 60d realized vol >= 30%
    equityRatioRiskOff: 0.5,
    cashRate: 0.0, // 0% risk-free assumption (option: CD91)
  },
  disclosureLag: { quarterDays: 45, annualDays: 90 },
  minListedMonths: 12,
  minAvgValue: 5_000_000_000, // 50억 원 20일 평균 거래대금
  seed: 20240101,
};
