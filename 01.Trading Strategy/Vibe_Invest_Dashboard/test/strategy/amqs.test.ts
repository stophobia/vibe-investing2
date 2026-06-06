import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import {
  runAmqs,
  AI_INFRA_TICKERS,
  TICKER_SUBTHEME,
  toDashboardSignal,
  type AmqsTickerInput,
  type TickerMetrics,
} from "../../shared/strategy/amqs";

// Python(strategy.py) 으로 생성한 골든. 재생성: python3 test/fixtures/gen_amqs_fixture.py
interface GoldenRow {
  ticker: string;
  [k: string]: number | string | boolean | null;
}
interface Golden {
  prices: Record<string, number[]>;
  qqq: number[];
  vix: number[];
  marketCaps: Record<string, number>;
  regime: { label: string; qqq_above_200ma: boolean; vix_level: number; qqq_5d_return: number };
  rows: GoldenRow[];
}

const golden: Golden = JSON.parse(
  readFileSync(new URL("../fixtures/amqs_golden.json", import.meta.url), "utf8"),
);

/** |a-b| ≤ atol + rtol·|b| (부동소수 합산 순서 차이 흡수). */
function approx(a: number, b: number, label: string): void {
  expect(Math.abs(a - b), `${label}: got ${a}, want ${b}`).toBeLessThanOrEqual(1e-6 + 1e-6 * Math.abs(b));
}
/** golden 이 null(=NaN)이면 TS 도 NaN, 아니면 근사 일치. */
function approxOrNull(a: number, b: number | null, label: string): void {
  if (b === null) expect(Number.isNaN(a), `${label}: want NaN, got ${a}`).toBe(true);
  else approx(a, b, label);
}

const NUM_FIELDS: Array<[keyof TickerMetrics, string]> = [
  ["price", "price"],
  ["factorA12_1", "factor_a_12_1"],
  ["factorB6_1", "factor_b_6_1"],
  ["factorC3_1", "factor_c_3_1"],
  ["factorDInvVol", "factor_d_inv_vol"],
  ["ret5d", "ret_5d"],
  ["ret20d", "ret_20d"],
  ["ret60d", "ret_60d"],
  ["vol60d", "vol_60d"],
  ["sharpe6m", "sharpe_6m"],
  ["mdd12m", "mdd_12m"],
  ["rsi14", "rsi_14"],
  ["dist52wHigh", "dist_52w_high"],
  ["betaQqq", "beta_qqq"],
  ["zA", "z_factor_a"],
  ["zB", "z_factor_b"],
  ["zC", "z_factor_c"],
  ["zD", "z_factor_d"],
  ["fourFactorComposite", "four_factor_composite"],
  ["scoreMomentum", "score_momentum"],
  ["scorePullback", "score_pullback"],
  ["scoreQuality", "score_quality"],
  ["scoreVolAlpha", "score_vol_alpha"],
  ["scoreMacro", "score_macro"],
  ["totalScore100", "total_score_100"],
  ["weight", "weight"],
];

describe("AMQS — Python(strategy.py) 골든 대조", () => {
  const inputs: AmqsTickerInput[] = AI_INFRA_TICKERS.map((t) => ({ ticker: t, closes: golden.prices[t] }));
  const { regime, metrics } = runAmqs(inputs, {
    qqqCloses: golden.qqq,
    vixCloses: golden.vix,
    marketCaps: golden.marketCaps,
  });
  const byTicker: Record<string, TickerMetrics> = Object.fromEntries(metrics.map((m) => [m.ticker, m]));

  it("레짐 일치", () => {
    expect(regime.label).toBe(golden.regime.label);
    expect(regime.qqqAbove200ma).toBe(golden.regime.qqq_above_200ma);
    approx(regime.vixLevel, golden.regime.vix_level, "vix_level");
    approx(regime.qqq5dReturn, golden.regime.qqq_5d_return, "qqq_5d_return");
  });

  it("종목 수 일치", () => {
    expect(metrics.length).toBe(golden.rows.length);
  });

  for (const row of golden.rows) {
    it(`${row.ticker}: 지표·점수·시그널 일치`, () => {
      const m = byTicker[row.ticker as string];
      expect(m, `missing ${row.ticker}`).toBeTruthy();
      for (const [tsKey, gKey] of NUM_FIELDS) {
        approxOrNull(m[tsKey] as number, row[gKey] as number | null, `${row.ticker}.${gKey}`);
      }
      expect(m.subtheme).toBe(row.subtheme);
      expect(m.above50dma).toBe(row.above_50dma);
      expect(m.above200dma).toBe(row.above_200dma);
      expect(m.positiveMonths12m).toBe(row.positive_months_12m);
      expect(m.filteredOut).toBe(row.filtered_out);
      expect(m.selected).toBe(row.selected);
      expect(m.signal).toBe(row.signal);
    });
  }

  it("정렬: total_score_100 내림차순", () => {
    for (let i = 1; i < metrics.length; i++) {
      expect(metrics[i - 1].totalScore100).toBeGreaterThanOrEqual(metrics[i].totalScore100);
    }
  });
});

describe("AMQS 부가", () => {
  it("서브테마 매핑 — NVDA=Compute/GPU, MU=Memory/Storage", () => {
    expect(TICKER_SUBTHEME["NVDA"]).toBe("Compute/GPU");
    expect(TICKER_SUBTHEME["MU"]).toBe("Memory/Storage");
  });
  it("대시보드 시그널 매핑(STRATEGY-ANALYSIS §2.5)", () => {
    expect(toDashboardSignal("CENTER")).toBe("BUY");
    expect(toDashboardSignal("DIP_BUY")).toBe("BUY");
    expect(toDashboardSignal("SATELLITE")).toBe("HOLD");
    expect(toDashboardSignal("TACTICAL")).toBe("HOLD");
    expect(toDashboardSignal("REDUCE")).toBe("SELL");
    expect(toDashboardSignal("EXIT")).toBe("SELL");
    expect(toDashboardSignal("EXCLUDED")).toBeNull();
  });
});
