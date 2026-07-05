/**
 * Factor calculator — computes the raw quality / value / low-vol / momentum
 * factors for each stock at a rebalance date, strictly point-in-time.
 * Implements the [팩터 정의] block of BuyKorea.md.
 *
 * Raw values are returned here; cross-sectional winsorize / z-score / sector
 * neutralization happens in score.ts.
 */
import type { DataStore } from "../data/loader.js";
import type { FactorValues, StockSnapshot } from "../types.js";
import type { UniverseMember } from "./universe.js";
import { std } from "../util.js";

const TRADING_MONTH = 21; // ~ trading days per month

function dailyReturns(close: Float64Array, from: number, to: number): number[] {
  const out: number[] = [];
  for (let i = from + 1; i <= to; i++) {
    const a = close[i - 1];
    const b = close[i];
    if (Number.isFinite(a) && Number.isFinite(b) && a > 0) out.push(b / a - 1);
  }
  return out;
}

function realizedVolAnnualized(rets: number[]): number {
  if (rets.length < 20) return NaN;
  return std(rets, true) * Math.sqrt(252);
}

function beta(stockRets: number[], mktRets: number[]): number {
  const n = Math.min(stockRets.length, mktRets.length);
  if (n < 60) return NaN;
  const s = stockRets.slice(stockRets.length - n);
  const m = mktRets.slice(mktRets.length - n);
  const ms = s.reduce((a, b) => a + b, 0) / n;
  const mm = m.reduce((a, b) => a + b, 0) / n;
  let cov = 0;
  let varM = 0;
  for (let i = 0; i < n; i++) {
    cov += (s[i] - ms) * (m[i] - mm);
    varM += (m[i] - mm) * (m[i] - mm);
  }
  if (varM === 0) return NaN;
  return cov / varM;
}

function benchReturns(ds: DataStore, from: number, to: number): number[] {
  const out: number[] = [];
  for (let i = from + 1; i <= to; i++) {
    const a = ds.benchPrice[i - 1];
    const b = ds.benchPrice[i];
    if (a > 0) out.push(b / a - 1);
  }
  return out;
}

function computeOne(ds: DataStore, code: string, asOf: string, dayIdx: number): Partial<FactorValues> {
  const f: Partial<FactorValues> = {};
  const close = ds.close.get(code);
  const mcapArr = ds.mcap.get(code);
  const mcap = mcapArr && Number.isFinite(mcapArr[dayIdx]) ? mcapArr[dayIdx] : NaN;

  // ---- Quality ----
  const niTTM = ds.pitTTM(code, "net_income", asOf);
  const equitySeries = ds.pitSeries(code, "equity", asOf, 20);
  const equityNow = equitySeries[0]?.value;
  const equityPrev = equitySeries[3]?.value; // ~4 quarters ago
  if (niTTM !== null && equityNow && equityPrev) {
    const avgEquity = (equityNow + equityPrev) / 2;
    if (avgEquity > 0) f.roe = niTTM / avgEquity;
  }
  const gpTTM = ds.pitTTM(code, "gross_profit", asOf);
  const assets = ds.pitLatest(code, "total_assets", asOf);
  if (gpTTM !== null && assets && assets.value > 0) f.gpa = gpTTM / assets.value;

  const debt = ds.pitLatest(code, "total_debt", asOf);
  if (debt && equityNow && equityNow > 0) f.debtRatio = debt.value / equityNow;

  // ROE stability: std of last 20 quarterly ROE (net_income_q / equity_q).
  const niSeries = ds.pitSeries(code, "net_income", asOf, 20);
  const eqMap = new Map(equitySeries.map((p) => [p.fiscalDate, p.value]));
  const roeQ: number[] = [];
  for (const p of niSeries) {
    const eq = eqMap.get(p.fiscalDate);
    if (eq && eq > 0) roeQ.push(p.value / eq);
  }
  if (roeQ.length >= 8) f.roeStability = std(roeQ, true);

  // ---- Value ----
  if (niTTM !== null && Number.isFinite(mcap) && mcap > 0) f.ep = niTTM / mcap;
  if (equityNow && Number.isFinite(mcap) && mcap > 0) f.bp = equityNow / mcap;
  const dps = ds.pitLatest(code, "dps", asOf);
  if (dps && close && Number.isFinite(close[dayIdx]) && close[dayIdx] > 0) f.divYield = dps.value / close[dayIdx];

  // ---- Low volatility ----
  if (close) {
    const vol = realizedVolAnnualized(dailyReturns(close, dayIdx - 60, dayIdx));
    if (Number.isFinite(vol)) f.vol60 = vol;
    const sRets = dailyReturns(close, dayIdx - 250, dayIdx);
    const mRets = benchReturns(ds, dayIdx - 250, dayIdx);
    const b = beta(sRets, mRets);
    if (Number.isFinite(b)) f.beta = b;
  }

  // ---- Momentum (skip last 1 month) ----
  if (close) {
    const skip = dayIdx - TRADING_MONTH;
    const p12 = close[dayIdx - 12 * TRADING_MONTH];
    const p6 = close[dayIdx - 6 * TRADING_MONTH];
    const pSkip = close[skip];
    if (Number.isFinite(pSkip) && Number.isFinite(p12) && p12 > 0) f.mom12_1 = pSkip / p12 - 1;
    if (Number.isFinite(pSkip) && Number.isFinite(p6) && p6 > 0) f.mom6_1 = pSkip / p6 - 1;
  }

  return f;
}

export function factorCalculator(ds: DataStore, members: UniverseMember[], asOf: string): StockSnapshot[] {
  const dayIdx = ds.idxOnOrBefore(asOf);
  const out: StockSnapshot[] = [];
  for (const m of members) {
    out.push({ code: m.code, sector: m.sector, factors: computeOne(ds, m.code, asOf, dayIdx) });
  }
  return out;
}
