import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { runArds, freshState } from "../../shared/strategy/ards/index";
import { applyHysteresis, freshState as fresh2 } from "../../shared/strategy/ards/hysteresis";
import type { DSeries } from "../../shared/strategy/ards/dseries";

// Python(quant/*.py)으로 생성한 골든. 재생성: python3 test/fixtures/gen_ards_fixture.py
const golden = JSON.parse(readFileSync(new URL("../fixtures/ards_golden.json", import.meta.url), "utf8"));

const px = golden.px as Record<string, DSeries>;
const fred = golden.fred as Record<string, DSeries>;
const res = runArds(px, fred, freshState(), "2026-06-06");

const TOL = 0.02;

/** 골든(expected) 트리를 따라 재귀 비교. 숫자는 tol, null→NaN/null 허용, 그 외 정확. */
function expectClose(actual: unknown, expected: unknown, path: string): void {
  if (expected === null) {
    expect(actual === null || (typeof actual === "number" && Number.isNaN(actual)), `${path}: want null, got ${actual}`).toBe(true);
    return;
  }
  if (typeof expected === "number") {
    expect(typeof actual === "number", `${path}: not a number (${actual})`).toBe(true);
    expect(Math.abs((actual as number) - expected), `${path}: got ${actual}, want ${expected}`).toBeLessThanOrEqual(TOL);
    return;
  }
  if (typeof expected === "string" || typeof expected === "boolean") {
    expect(actual, path).toEqual(expected);
    return;
  }
  if (Array.isArray(expected)) {
    expect(Array.isArray(actual), `${path}: not array`).toBe(true);
    expect((actual as unknown[]).length, `${path}.length`).toBe(expected.length);
    expected.forEach((e, i) => expectClose((actual as unknown[])[i], e, `${path}[${i}]`));
    return;
  }
  // object
  expect(typeof actual === "object" && actual !== null, `${path}: not object`).toBe(true);
  for (const k of Object.keys(expected as Record<string, unknown>)) {
    expectClose((actual as Record<string, unknown>)[k], (expected as Record<string, unknown>)[k], `${path}.${k}`);
  }
}

describe("ARDS — Python(quant/*.py) 골든 대조", () => {
  it("macro (5-factor recession composite)", () => {
    expectClose(res.macro, golden.macro, "macro");
  });
  it("rate (rate stress + components)", () => {
    expectClose(res.rate, golden.rate, "rate");
  });
  it("complex_agg", () => {
    expectClose(res.complex_agg, golden.complex_agg, "complex_agg");
  });
  it("measure (regime inputs)", () => {
    expectClose(res.measure, golden.measure, "measure");
  });
  it("raw classify + confirm", () => {
    expect(res.raw).toBe(golden.raw);
    expectClose(res.confirm, golden.confirm, "confirm");
  });
  it("verdict (state/action/confidence/axes/evidence/decline_type/narrative)", () => {
    expectClose(res.verdict, golden.verdict, "verdict");
  });

  const idxByT = Object.fromEntries(res.index_rows.map((r) => [r.ticker, r]));
  for (const gr of golden.index_rows as Array<Record<string, unknown>>) {
    it(`index_row ${gr.ticker}`, () => expectClose(idxByT[gr.ticker as string], gr, `idx.${gr.ticker}`));
  }

  const cmpByT = Object.fromEntries(res.complex_rows.map((r) => [r.ticker, r]));
  for (const gr of golden.complex_rows as Array<Record<string, unknown>>) {
    it(`complex_row ${gr.ticker}`, () => expectClose(cmpByT[gr.ticker as string], gr, `cmp.${gr.ticker}`));
  }
});

describe("ARDS 히스테리시스 상태머신 — 시퀀스 골든 대조", () => {
  it("confirm_days=2 전환 시퀀스가 Python과 일치", () => {
    const st = fresh2();
    for (const step of golden.hysteresis_seq as Array<Record<string, unknown>>) {
      const { committed, confirm } = applyHysteresis(step.raw as string, st, step.day as string);
      expect(committed, `committed @${step.day}`).toBe(step.committed);
      expectClose(confirm, step.confirm, `confirm@${step.day}`);
    }
  });
});
