// Shared domain types for the KOSPI blue-chip multi-factor backtest.

export type SectorCode =
  | "IT"
  | "산업재"
  | "경기소비재"
  | "필수소비재"
  | "헬스케어"
  | "소재"
  | "커뮤니케이션"
  | "에너지"
  | "유틸리티"
  | "금융"; // 금융 is excluded by the universe filter but present in data.

// ---- Raw input rows (mirror the CSV schema documented in src/data/generate.ts) ----

export interface PriceRow {
  date: string; // YYYY-MM-DD (trading day)
  code: string; // stock code, e.g. "A005930"
  open: number;
  close: number;
  value: number; // 거래대금 (traded value, KRW)
  marketCap: number; // 시가총액 (KRW)
}

export interface FinancialRow {
  fiscalDate: string; // 결산일 (period end) YYYY-MM-DD
  discloseDate: string; // 공시일 (release date, lag applied) YYYY-MM-DD
  code: string;
  account: string; // 계정과목
  value: number;
}

export interface UniverseRow {
  asOf: string; // 기준일 YYYY-MM-DD (monthly point-in-time snapshot)
  code: string;
  inKospi200: boolean;
  sector: SectorCode; // WICS 대분류
  listedDate: string; // 상장일
  delistedDate: string; // 상장폐지일 or "" if active
  managed: boolean; // 관리종목 여부
  suspended: boolean; // 거래정지 여부
}

// ---- Engine intermediate structures ----

export interface FactorValues {
  // Quality
  roe: number;
  gpa: number;
  debtRatio: number; // reverse
  roeStability: number; // reverse
  // Value
  ep: number;
  bp: number;
  divYield: number;
  // Low vol
  vol60: number; // reverse
  beta: number; // reverse
  // Momentum
  mom12_1: number;
  mom6_1: number;
}

export type FactorKey = keyof FactorValues;

export interface StockSnapshot {
  code: string;
  sector: SectorCode;
  factors: Partial<FactorValues>;
  zscores?: Partial<Record<FactorKey, number>>; // sign-adjusted cross-sectional z-scores (for IC)
  compositeScore?: number;
  qualityScore?: number;
  valueScore?: number;
  lowVolScore?: number;
  momentumScore?: number;
}

export interface Holding {
  code: string;
  weight: number;
  shares: number;
}

export interface RebalanceRecord {
  date: string; // signal date (month end)
  execDate: string; // execution date (next trading day open)
  holdings: { code: string; weight: number; sector: SectorCode }[];
  turnover: number; // one-way turnover fraction
  riskOff: boolean; // crisis filter engaged
  equityRatio: number; // fraction invested in equities (1.0 or 0.5)
}

export interface EquityPoint {
  date: string;
  strategy: number; // strategy NAV (index, start = 100)
  benchmark: number; // KOSPI200 TR NAV (index, start = 100)
}

export interface ICPoint {
  date: string;
  ic: Record<FactorKey, number | null>; // Spearman rank correlation w/ next-month return
}

export interface PerformanceStats {
  cagr: number;
  vol: number;
  sharpe: number;
  mdd: number;
  mddRecoveryMonths: number | null;
  informationRatio: number;
  avgTurnover: number;
  winRateMonthly: number;
  totalReturn: number;
}

export interface YearlyRow {
  year: number;
  strategy: number;
  benchmark: number;
  excess: number;
}

export interface ICSummaryRow {
  factor: FactorKey;
  meanIC: number;
  icIR: number; // mean/std
  tStat: number;
  hitRate: number; // fraction of months IC > 0
}

export interface SensitivityRow {
  label: string;
  cagr: number;
  sharpe: number;
  mdd: number;
}

export interface BacktestResult {
  params: BacktestParams;
  equityCurve: EquityPoint[];
  monthlyReturns: { date: string; strategy: number; benchmark: number }[];
  drawdown: { date: string; strategy: number; benchmark: number }[];
  rebalances: RebalanceRecord[];
  stats: PerformanceStats;
  statsBenchmark: PerformanceStats;
  statsGross: PerformanceStats; // before trading costs
  yearly: YearlyRow[];
  icSeries: ICPoint[];
  icSummary: ICSummaryRow[];
  factorExposure: { date: string; quality: number; value: number; lowVol: number; momentum: number }[];
  sensitivity: SensitivityRow[];
  generatedAt: string;
}

export interface BacktestParams {
  startDate: string;
  endDate: string;
  numHoldings: number;
  bufferOut: number; // rank threshold to keep existing holdings
  sectorCapPct: number;
  weights: { quality: number; value: number; lowVol: number; momentum: number };
  positionWeight: number; // target per-name weight
  rebalanceBand: number; // skip trade if within this band of target
  maxPositionWeight: number; // trim threshold
  cost: {
    sellTaxByYear: Record<string, number>; // 증권거래세 (year -> rate)
    commission: number; // per side
    marketImpact: number; // bps -> fraction
  };
  crisis: {
    maBenchmarkMonths: number;
    volThreshold: number; // annualized realized vol
    equityRatioRiskOff: number;
    cashRate: number; // annual risk-free applied to cash sleeve
  };
  disclosureLag: { quarterDays: number; annualDays: number };
  minListedMonths: number;
  minAvgValue: number; // liquidity filter (KRW)
  seed: number;
}
