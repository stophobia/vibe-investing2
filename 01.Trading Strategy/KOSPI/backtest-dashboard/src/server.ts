/**
 * Dashboard server — serves the static dashboard and a small API.
 *
 *   GET /api/result           default-parameter backtest (cached)
 *   GET /api/run?...          re-run with parameter overrides (interactive)
 *
 * The DataStore is loaded once at startup and reused across requests.
 */
import express from "express";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { loadData, type DataStore } from "./data/loader.js";
import { runBacktest } from "./engine/index.js";
import { DEFAULT_PARAMS } from "./config.js";
import type { BacktestParams } from "./types.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT ?? 3000);

console.log("Loading data into memory...");
const ds: DataStore = loadData();
console.log(`Ready: ${ds.codes.length} stocks, ${ds.dates.length} trading days`);

let defaultResult = runBacktest(ds, DEFAULT_PARAMS, true);
console.log("Default backtest cached.");

function parseParams(q: Record<string, unknown>): BacktestParams {
  const p: BacktestParams = JSON.parse(JSON.stringify(DEFAULT_PARAMS));
  const num = (v: unknown) => (v === undefined ? undefined : Number(v));

  const nh = num(q.numHoldings);
  if (nh && nh >= 5 && nh <= 40) {
    p.numHoldings = Math.round(nh);
    p.bufferOut = Math.round(nh) + 10;
  }
  let wq = num(q.quality);
  let wv = num(q.value);
  let wl = num(q.lowVol);
  let wm = num(q.momentum);
  if ([wq, wv, wl, wm].some((x) => x !== undefined)) {
    wq = wq ?? DEFAULT_PARAMS.weights.quality;
    wv = wv ?? DEFAULT_PARAMS.weights.value;
    wl = wl ?? DEFAULT_PARAMS.weights.lowVol;
    wm = wm ?? DEFAULT_PARAMS.weights.momentum;
    const sum = wq + wv + wl + wm || 1;
    p.weights = { quality: wq / sum, value: wv / sum, lowVol: wl / sum, momentum: wm / sum };
  }
  if (q.crisis === "off") p.crisis = { ...p.crisis, volThreshold: 999 };
  const tax = num(q.tax);
  if (tax !== undefined) p.cost = { ...p.cost, sellTaxByYear: { ...p.cost.sellTaxByYear, default: tax } };
  return p;
}

const app = express();
app.use(express.static(path.resolve(__dirname, "../public")));

app.get("/api/result", (_req, res) => {
  res.json(defaultResult);
});

app.get("/api/run", (req, res) => {
  try {
    const params = parseParams(req.query as Record<string, unknown>);
    const result = runBacktest(ds, params, false); // skip sensitivity for speed
    res.json(result);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.get("/api/reset", (_req, res) => {
  defaultResult = runBacktest(ds, DEFAULT_PARAMS, true);
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`\nDashboard running at http://localhost:${PORT}\n`);
});
