import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, rm } from "node:fs/promises";
import path from "node:path";
import { exportToQlibCsv } from "../src/market/qlibExport.js";

test("문서 7.1/7.2절 pykrx CSV 관례와 동일한 포맷으로 저장한다", async () => {
  const outDir = path.join(process.cwd(), ".tmp-test-csv");
  const rows = [
    { date: "2026-07-01", open: 100, high: 110, low: 95, close: 105, volume: 1000, symbol: "005930", factor: 1.0 },
  ];

  const filePath = await exportToQlibCsv(rows, outDir, "005930");
  const content = await readFile(filePath, "utf-8");
  const lines = content.split("\n");

  assert.equal(lines[0], "date,open,high,low,close,volume,symbol,factor");
  assert.equal(lines[1], "2026-07-01,100,110,95,105,1000,005930,1");
  assert.equal(path.basename(filePath), "005930.csv");

  await rm(outDir, { recursive: true, force: true });
});
