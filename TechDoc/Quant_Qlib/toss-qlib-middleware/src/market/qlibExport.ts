import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import type { QlibCandleRow } from "../types.js";

const CSV_HEADER = "date,open,high,low,close,volume,symbol,factor";

function toCsvRow(row: QlibCandleRow): string {
  return [row.date, row.open, row.high, row.low, row.close, row.volume, row.symbol, row.factor].join(",");
}

/** 문서 7.1/7.2절의 pykrx CSV 관례와 동일한 포맷으로 저장해 dump_bin.py에 바로 넘길 수 있게 한다. */
export async function exportToQlibCsv(rows: QlibCandleRow[], outDir: string, symbol: string): Promise<string> {
  await mkdir(outDir, { recursive: true });
  const filePath = path.join(outDir, `${symbol}.csv`);
  const csv = [CSV_HEADER, ...rows.map(toCsvRow)].join("\n");
  await writeFile(filePath, csv, "utf-8");
  return filePath;
}
