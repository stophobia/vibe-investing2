/**
 * POST /api/ingest/news — Azure(AIInvestor) → CF Worker 뉴스 요약 수신.
 *
 * 계약(단일 기준): docs/PROMPT-azure-news.md §ingest 계약
 *   헤더: X-Timestamp(unix epoch 초), X-Signature(hex HMAC-SHA256)
 *   서명 base string: `${timestamp}.${rawBody}`  · key = INGEST_SECRET
 *   검증: |now - timestamp| ≤ 300초 AND 서명 일치
 *   성공: 200 {ok:true, ingested:n} / 인증실패: 401 / 페이로드 오류: 400
 *   저장: D1 news_summary upsert(항목별) + market_summary(id=1) 갱신
 */

export const TIMESTAMP_TOLERANCE_SEC = 300;

export const NEWS_CATEGORIES = [
  "거시경제",
  "실적",
  "반도체",
  "AI",
  "금리",
  "지정학",
  "기타",
] as const;
export type NewsCategory = (typeof NEWS_CATEGORIES)[number];

export interface NewsItem {
  id: string;
  ts: string;
  title_ko: string;
  summary_ko: string;
  category: NewsCategory;
  tickers: string[];
  source: string;
  url: string;
}

export interface NewsPayload {
  ts: string;
  market_summary: string;
  items: NewsItem[];
}

/** Minimal D1 surface used here — 테스트에서 fake 로 대체 가능하게 분리. */
export interface D1Like {
  prepare(query: string): {
    bind(...values: unknown[]): { run(): Promise<unknown> };
  };
  batch(statements: Array<{ run(): Promise<unknown> }>): Promise<unknown>;
}

// ---------------------------------------------------------------------------
// 순수 함수 (단위 테스트 대상) — D1·Request 의존성 없음
// ---------------------------------------------------------------------------

/** hex(HMAC-SHA256(secret, message)) — Web Crypto. */
export async function hmacHex(secret: string, message: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  const bytes = new Uint8Array(sig);
  let out = "";
  for (const b of bytes) out += b.toString(16).padStart(2, "0");
  return out;
}

/** 길이 의존 분기 외에는 상수 시간 비교 (타이밍 누수 최소화). */
export function timingSafeEqualHex(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}

/** X-Timestamp(초)가 now 기준 ±tolerance 이내인지. */
export function isFreshTimestamp(
  timestamp: string | null,
  nowSec: number,
  toleranceSec = TIMESTAMP_TOLERANCE_SEC,
): boolean {
  if (!timestamp) return false;
  if (!/^\d{1,15}$/.test(timestamp.trim())) return false;
  const ts = Number(timestamp);
  if (!Number.isFinite(ts)) return false;
  return Math.abs(nowSec - ts) <= toleranceSec;
}

/** 서명 검증: 헤더 timestamp/signature + rawBody 로 재계산해 비교. */
export async function verifySignature(
  secret: string,
  timestamp: string,
  rawBody: string,
  providedSig: string | null,
): Promise<boolean> {
  if (!providedSig || !/^[0-9a-f]+$/i.test(providedSig)) return false;
  const expected = await hmacHex(secret, `${timestamp}.${rawBody}`);
  return timingSafeEqualHex(expected, providedSig.toLowerCase());
}

export type ValidationResult =
  | { ok: true; value: NewsPayload }
  | { ok: false; error: string };

function asString(v: unknown): string {
  return typeof v === "string" ? v : v == null ? "" : String(v);
}

/** 페이로드 형식 검증 + 정규화. 알 수 없는 카테고리는 거절하지 않고 '기타'로. */
export function validateNewsPayload(obj: unknown): ValidationResult {
  if (typeof obj !== "object" || obj === null) return { ok: false, error: "body must be a JSON object" };
  const o = obj as Record<string, unknown>;
  if (typeof o.market_summary !== "string") return { ok: false, error: "market_summary must be a string" };
  if (!Array.isArray(o.items)) return { ok: false, error: "items must be an array" };

  const catSet = new Set<string>(NEWS_CATEGORIES);
  const items: NewsItem[] = [];
  for (let i = 0; i < o.items.length; i++) {
    const raw = o.items[i];
    if (typeof raw !== "object" || raw === null) return { ok: false, error: `items[${i}] must be an object` };
    const it = raw as Record<string, unknown>;
    const id = asString(it.id).trim();
    if (!id) return { ok: false, error: `items[${i}].id is required` };
    const category = catSet.has(asString(it.category)) ? (asString(it.category) as NewsCategory) : "기타";
    const tickers = Array.isArray(it.tickers) ? it.tickers.map(asString).filter(Boolean) : [];
    items.push({
      id,
      ts: asString(it.ts),
      title_ko: asString(it.title_ko),
      summary_ko: asString(it.summary_ko),
      category,
      tickers,
      source: asString(it.source),
      url: asString(it.url),
    });
  }

  return {
    ok: true,
    value: { ts: asString(o.ts), market_summary: o.market_summary, items },
  };
}

// ---------------------------------------------------------------------------
// D1 저장
// ---------------------------------------------------------------------------

/** news_summary 항목별 upsert + market_summary(id=1) 갱신을 batch 로 실행. */
export async function persistNews(db: D1Like, payload: NewsPayload): Promise<number> {
  const upsertItem = db.prepare(
    `INSERT INTO news_summary (id, ts, title_ko, summary_ko, category, tickers_json, source, url)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       ts=excluded.ts, title_ko=excluded.title_ko, summary_ko=excluded.summary_ko,
       category=excluded.category, tickers_json=excluded.tickers_json,
       source=excluded.source, url=excluded.url`,
  );

  const statements = payload.items.map((it) =>
    upsertItem.bind(
      it.id,
      it.ts,
      it.title_ko,
      it.summary_ko,
      it.category,
      JSON.stringify(it.tickers),
      it.source,
      it.url,
    ),
  );

  // market_summary 는 비어있지 않을 때만 갱신
  if (payload.market_summary.trim()) {
    statements.push(
      db
        .prepare(
          `INSERT INTO market_summary (id, ts, summary_ko) VALUES (1, ?, ?)
           ON CONFLICT(id) DO UPDATE SET ts=excluded.ts, summary_ko=excluded.summary_ko`,
        )
        .bind(payload.ts, payload.market_summary),
    );
  }

  if (statements.length > 0) await db.batch(statements);
  return payload.items.length;
}

// ---------------------------------------------------------------------------
// HTTP 핸들러
// ---------------------------------------------------------------------------

function reply(status: number, body: Record<string, unknown>): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

/**
 * @param secret  INGEST_SECRET (없으면 500 — 서버 설정 오류)
 * @param nowSec  현재 unix 초 (테스트 주입용; 기본 Date.now)
 */
export async function handleIngestNews(
  request: Request,
  db: D1Like,
  secret: string | undefined,
  nowSec: number = Math.floor(Date.now() / 1000),
): Promise<Response> {
  if (!secret) return reply(500, { ok: false, error: "ingest_not_configured" });

  const timestamp = request.headers.get("X-Timestamp");
  const signature = request.headers.get("X-Signature");
  if (!isFreshTimestamp(timestamp, nowSec)) {
    return reply(401, { ok: false, error: "invalid_or_stale_timestamp" });
  }

  const rawBody = await request.text();
  if (!(await verifySignature(secret, timestamp as string, rawBody, signature))) {
    return reply(401, { ok: false, error: "invalid_signature" });
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawBody);
  } catch {
    return reply(400, { ok: false, error: "invalid_json" });
  }

  const validated = validateNewsPayload(parsed);
  if (!validated.ok) return reply(400, { ok: false, error: validated.error });

  try {
    const ingested = await persistNews(db, validated.value);
    return reply(200, { ok: true, ingested });
  } catch (err) {
    return reply(500, { ok: false, error: "persist_failed", detail: String(err) });
  }
}
