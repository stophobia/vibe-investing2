/**
 * CLI runner — loads data, runs the backtest, prints a terminal report and
 * writes machine-readable outputs consumed by the dashboard.
 *
 *   out/result.json      full BacktestResult (dashboard data source)
 *   out/monthly.csv      월별 전략/벤치마크 수익률
 *   out/holdings.csv     월별 포트폴리오 구성 내역
 *   out/ic_summary.csv   팩터별 IC 분석 테이블
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { loadData } from "./data/loader.js";
import { runBacktest } from "./engine/index.js";
import { DEFAULT_PARAMS } from "./config.js";
import { toCsv, round } from "./util.js";
import type { PerformanceStats } from "./types.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.resolve(__dirname, "../out");

const pct = (x: number) => (x * 100).toFixed(2) + "%";
const num = (x: number, d = 2) => x.toFixed(d);

function printStats(label: string, s: PerformanceStats) {
  console.log(
    `  ${label.padEnd(14)} CAGR ${pct(s.cagr).padStart(8)} | Vol ${pct(s.vol).padStart(7)} | Sharpe ${num(
      s.sharpe,
    ).padStart(5)} | MDD ${pct(s.mdd).padStart(8)} | IR ${num(s.informationRatio).padStart(5)} | 승률 ${pct(
      s.winRateMonthly,
    ).padStart(7)}`,
  );
}

function main() {
  console.log("Loading data...");
  const t0 = Date.now();
  const ds = loadData();
  console.log(`Loaded ${ds.codes.length} stocks, ${ds.dates.length} trading days in ${Date.now() - t0}ms`);

  console.log("Running backtest...");
  const t1 = Date.now();
  const result = runBacktest(ds, DEFAULT_PARAMS, true);
  console.log(`Backtest complete in ${Date.now() - t1}ms\n`);

  console.log("=== 코스피 우량주 멀티팩터 전략 백테스트 (2012-2024) ===\n");
  printStats("전략(순)", result.stats);
  printStats("전략(총)", result.statsGross);
  printStats("벤치마크", result.statsBenchmark);
  console.log(
    `\n  월평균 턴오버(one-way): ${pct(result.stats.avgTurnover)} | MDD 회복: ${
      result.stats.mddRecoveryMonths ?? "미회복"
    }개월`,
  );

  console.log("\n--- 연도별 수익률 ---");
  console.log("  연도    전략      벤치      초과");
  for (const y of result.yearly) {
    console.log(`  ${y.year}  ${pct(y.strategy).padStart(8)}  ${pct(y.benchmark).padStart(8)}  ${pct(y.excess).padStart(8)}`);
  }

  console.log("\n--- 팩터별 RankIC 분석 ---");
  console.log("  팩터            평균IC    IC_IR    t-stat   승률");
  for (const r of result.icSummary) {
    console.log(
      `  ${r.factor.padEnd(14)} ${num(r.meanIC, 3).padStart(7)} ${num(r.icIR, 2).padStart(7)} ${num(
        r.tStat,
        2,
      ).padStart(7)} ${pct(r.hitRate).padStart(7)}`,
    );
  }

  console.log("\n--- 파라미터 민감도 ---");
  console.log("  설정            CAGR     Sharpe   MDD");
  for (const s of result.sensitivity) {
    console.log(`  ${s.label.padEnd(14)} ${pct(s.cagr).padStart(8)} ${num(s.sharpe).padStart(7)} ${pct(s.mdd).padStart(8)}`);
  }

  // ---- Write outputs ----
  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(path.join(OUT_DIR, "result.json"), JSON.stringify(result));
  writeFileSync(
    path.join(OUT_DIR, "monthly.csv"),
    toCsv(
      result.monthlyReturns.map((m) => ({
        date: m.date,
        strategy: round(m.strategy, 6),
        benchmark: round(m.benchmark, 6),
      })),
    ),
  );
  const holdingRows = result.rebalances.flatMap((r) =>
    r.holdings.map((h) => ({
      date: r.date,
      execDate: r.execDate,
      code: h.code,
      sector: h.sector,
      weight: round(h.weight, 4),
      riskOff: r.riskOff,
    })),
  );
  writeFileSync(path.join(OUT_DIR, "holdings.csv"), toCsv(holdingRows));
  writeFileSync(
    path.join(OUT_DIR, "ic_summary.csv"),
    toCsv(result.icSummary.map((r) => ({ ...r, meanIC: round(r.meanIC, 4), icIR: round(r.icIR, 4), tStat: round(r.tStat, 3), hitRate: round(r.hitRate, 4) }))),
  );

  console.log(`\nOutputs written to ${OUT_DIR}`);
}

main();
