/**
 * 일1회 크론 IO 오케스트레이션: 수집 → computeSignals → D1/R2 영속화 + 히스테리시스 상태.
 */
import { fetchSparkMany } from "./providers/yahoo";
import { fetchFredMany } from "./providers/fred";
import { reconcileWithCache } from "./cache";
import { computeSignals, ALL_YAHOO_SYMBOLS, FRED_IDS, type SignalRow } from "./signals";
import { freshState, type HystState } from "../../shared/strategy/ards/hysteresis";
import type { D1Like } from "../../shared/ingest";

export interface DailyEnv {
  DB: D1Database;
  SNAPSHOTS: R2Bucket;
}

const STATE_KEY = "state/ards-regime.json";
const SNAPSHOT_KEY = "signals/latest.json";

export async function loadHystState(bucket: R2Bucket): Promise<HystState | null> {
  const obj = await bucket.get(STATE_KEY);
  if (!obj) return null;
  try {
    return JSON.parse(await obj.text()) as HystState;
  } catch {
    return null;
  }
}

export async function saveHystState(bucket: R2Bucket, state: HystState): Promise<void> {
  await bucket.put(STATE_KEY, JSON.stringify(state), {
    httpMetadata: { contentType: "application/json" },
  });
}

/** D1 signals upsert (PK date,strategy,ticker). */
export async function persistSignals(db: D1Like, rows: SignalRow[]): Promise<void> {
  if (rows.length === 0) return;
  const stmt = db.prepare(
    `INSERT INTO signals (date, strategy, ticker, signal, score, detail_json)
     VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(date, strategy, ticker) DO UPDATE SET
       signal=excluded.signal, score=excluded.score, detail_json=excluded.detail_json`,
  );
  await db.batch(rows.map((r) => stmt.bind(r.date, r.strategy, r.ticker, r.signal, r.score, r.detail_json)));
}

export async function runDailySignals(
  env: DailyEnv,
  opts: { today?: string } = {},
): Promise<{
  date: string;
  n_rows: number;
  ards_state: string | null;
  yahoo_from_cache: number;
  yahoo_missing: number;
  fred_from_cache: number;
  fred_missing: number;
}> {
  const today = opts.today ?? new Date().toISOString().slice(0, 10);
  const prevState = (await loadHystState(env.SNAPSHOTS)) ?? freshState();

  // 수집(spark 배치) → R2 캐시와 reconcile (실패분은 직전 저장본으로 폴백 = 가용성)
  const yahooFetch = await fetchSparkMany(ALL_YAHOO_SYMBOLS, "2y");
  const px = await reconcileWithCache(env.SNAPSHOTS, "prices", ALL_YAHOO_SYMBOLS, yahooFetch.data);
  const fredFetch = await fetchFredMany(FRED_IDS); // best-effort (막히면 엔진이 프록시 폴백)
  const fred = await reconcileWithCache(env.SNAPSHOTS, "fred", FRED_IDS, fredFetch.data);

  const { payload, rows, newState } = computeSignals(px.data, fred.data, prevState, today);
  payload.updated_at = new Date().toISOString();
  payload.data_quality = {
    yahoo_ok: Object.keys(px.data).length,
    yahoo_fail: px.missing.length,
    fred_ok: Object.keys(fred.data).length,
    fred_fail: fred.missing.length,
    yahoo_from_cache: px.fromCache.length,
    fred_from_cache: fred.fromCache.length,
  };

  await persistSignals(env.DB, rows);
  await env.SNAPSHOTS.put(SNAPSHOT_KEY, JSON.stringify(payload), {
    httpMetadata: { contentType: "application/json", cacheControl: "public, s-maxage=300" },
  });
  await saveHystState(env.SNAPSHOTS, newState);

  return {
    date: today,
    n_rows: rows.length,
    ards_state: newState.committed,
    yahoo_from_cache: px.fromCache.length,
    yahoo_missing: px.missing.length,
    fred_from_cache: fred.fromCache.length,
    fred_missing: fred.missing.length,
  };
}
