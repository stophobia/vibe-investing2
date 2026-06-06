/**
 * ARDS-X 설정 상수 — 원본 quant/config.py 1:1.
 * 값 변경 금지(원본이 최종 권위). 변경 시 Python 결과와 어긋난다.
 */

export const INDICES: Record<string, string> = {
  "^GSPC": "S&P 500",
  "^NDX": "Nasdaq-100",
};

export const COMPLEX: Record<string, [string, string]> = {
  AAPL: ["Apple", "bigtech"],
  MSFT: ["Microsoft", "bigtech"],
  GOOGL: ["Alphabet", "bigtech"],
  AMZN: ["Amazon", "bigtech"],
  META: ["Meta", "bigtech"],
  NVDA: ["NVIDIA", "ai_semi"],
  TSLA: ["Tesla", "bigtech"],
  AVGO: ["Broadcom", "ai_semi"],
  AMD: ["AMD", "ai_semi"],
  TSM: ["TSMC", "ai_semi"],
  MU: ["Micron", "ai_semi"],
  ASML: ["ASML", "ai_semi"],
  VRT: ["Vertiv", "ai_infra"],
  SMCI: ["Super Micro", "ai_infra"],
  ANET: ["Arista", "ai_infra"],
  DELL: ["Dell", "ai_infra"],
  ORCL: ["Oracle", "ai_infra"],
  CEG: ["Constellation", "ai_infra"],
};

export const GROUP_KR: Record<string, string> = {
  bigtech: "빅테크",
  ai_semi: "AI 반도체",
  ai_infra: "AI 인프라",
};

export const MACRO_MARKET = ["^TNX", "^IRX", "^FVX", "HYG", "LQD", "IEF", "CPER", "GLD", "XLI", "SPY"];
export const RATE_MARKET = ["^MOVE"];
export const FRED_SERIES = ["T10Y3M", "T10Y2Y", "UNRATE", "BAMLH0A0HYM2", "NFCI", "ICSA", "PERMIT"];
export const RATE_FRED = ["DGS2", "T5YIE"];

export const RECESSION_WEIGHTS: Record<string, number> = {
  A_yield_curve: 0.3,
  B_sahm: 0.25,
  C_ism_proxy: 0.15,
  D_lei_proxy: 0.15,
  E_credit: 0.15,
};

/** (상한, 코드, 한글) — composite < 상한 이면 해당 Phase. */
export const MACRO_PHASES: Array<[number, string, string]> = [
  [25, "EXPANSION", "확장기"],
  [50, "LATE_CYCLE", "후기 사이클"],
  [70, "RECESSION_WARNING", "침체 경고"],
  [101, "RECESSION", "침체"],
];

export const TECH = {
  dd_correction: 5.0,
  dd_deep: 12.0,
  dd_bear: 20.0,
  rsi_oversold: 32.0,
  rsi_deep_os: 25.0,
  bb_oversold: 0.05,
  atr_stretch: 2.5,
  breadth_weak: 40.0,
  breadth_strong: 60.0,
};

export const DECISION = {
  macro_elevated: 45.0,
  macro_recession: 55.0,
};

export const RATE_WEIGHTS: Record<string, number> = {
  R1_long_yield_vel: 0.35,
  R2_rate_path: 0.25,
  R3_breakeven: 0.2,
  R4_bond_vol: 0.2,
};

export const RATE = {
  yield_vel_bp_hi: 60.0,
  path_vel_bp_hi: 50.0,
  bei_vel_bp_hi: 30.0,
  stress_high: 55.0,
  label_min_stress: 28.0,
};

export const HYSTERESIS = {
  confirm_days: 2,
  rsi_enter: 30.0,
  rsi_exit: 38.0,
  dd_corr_enter: 5.0,
  dd_corr_exit: 3.5,
  dd_deep_enter: 12.0,
  dd_deep_exit: 10.0,
  macro_rec_enter: 55.0,
  macro_rec_exit: 50.0,
};

export const LOOKBACK_DAYS = 420;
