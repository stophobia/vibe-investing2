import { describe, it, expect } from "vitest";
import { createHmac } from "node:crypto";
import {
  hmacHex,
  timingSafeEqualHex,
  isFreshTimestamp,
  verifySignature,
  validateNewsPayload,
  persistNews,
  handleIngestNews,
  TIMESTAMP_TOLERANCE_SEC,
  type D1Like,
  type NewsPayload,
} from "../shared/ingest";

// ---------------------------------------------------------------------------
// Fake D1 — prepare/bind/batch 만 흉내 (persistNews 가 쓰는 부분)
// ---------------------------------------------------------------------------
function makeFakeD1() {
  const calls: { sql: string; args: unknown[] }[] = [];
  let batchCount = 0;
  const db: D1Like = {
    prepare(sql: string) {
      return {
        bind(...args: unknown[]) {
          return { run: async () => {}, sql, args } as unknown as { run(): Promise<unknown> };
        },
      };
    },
    async batch(statements) {
      batchCount++;
      for (const s of statements as unknown as Array<{ sql: string; args: unknown[] }>) {
        calls.push({ sql: s.sql, args: s.args });
      }
    },
  };
  return { db, calls, getBatchCount: () => batchCount };
}

const SECRET = "test-ingest-secret";

function samplePayload(): NewsPayload {
  return {
    ts: "2026-06-06T09:00:00Z",
    market_summary: "지수는 보합권에서 혼조세를 보였다. 반도체가 강세였다.",
    items: [
      {
        id: "fh-1001",
        ts: "2026-06-06T08:55:00Z",
        title_ko: "엔비디아 신제품 공개",
        summary_ko: "엔비디아가 차세대 GPU를 공개했다.",
        category: "반도체",
        tickers: ["NVDA"],
        source: "Finnhub",
        url: "https://example.com/a",
      },
      {
        id: "fh-1002",
        ts: "2026-06-06T08:50:00Z",
        title_ko: "연준 위원 발언",
        summary_ko: "연준 위원이 금리 인하에 신중한 입장을 보였다.",
        category: "금리",
        tickers: [],
        source: "Finnhub",
        url: "https://example.com/b",
      },
    ],
  };
}

async function signedRequest(secret: string, tsSec: number, bodyStr: string, sigOverride?: string) {
  const sig = sigOverride ?? (await hmacHex(secret, `${tsSec}.${bodyStr}`));
  return new Request("https://x.workers.dev/api/ingest/news", {
    method: "POST",
    headers: {
      "X-Timestamp": String(tsSec),
      "X-Signature": sig,
      "content-type": "application/json; charset=utf-8",
    },
    body: bodyStr,
  });
}

// ---------------------------------------------------------------------------
// 순수 함수
// ---------------------------------------------------------------------------
describe("hmacHex", () => {
  it("Node crypto(=Python hmac.sha256 hexdigest)와 동일한 값을 낸다", async () => {
    const msg = "1717660800.{\"a\":1}";
    const mine = await hmacHex(SECRET, msg);
    const node = createHmac("sha256", SECRET).update(msg).digest("hex");
    expect(mine).toBe(node);
    expect(mine).toMatch(/^[0-9a-f]{64}$/);
  });
});

describe("timingSafeEqualHex", () => {
  it("같으면 true, 다르거나 길이 다르면 false", () => {
    expect(timingSafeEqualHex("abcd", "abcd")).toBe(true);
    expect(timingSafeEqualHex("abcd", "abce")).toBe(false);
    expect(timingSafeEqualHex("abcd", "abc")).toBe(false);
  });
});

describe("isFreshTimestamp", () => {
  const now = 1_717_660_800;
  it("허용 범위 내 true", () => {
    expect(isFreshTimestamp(String(now), now)).toBe(true);
    expect(isFreshTimestamp(String(now - TIMESTAMP_TOLERANCE_SEC), now)).toBe(true);
  });
  it("범위 밖/형식오류/누락 false", () => {
    expect(isFreshTimestamp(String(now - TIMESTAMP_TOLERANCE_SEC - 1), now)).toBe(false);
    expect(isFreshTimestamp(null, now)).toBe(false);
    expect(isFreshTimestamp("not-a-number", now)).toBe(false);
    expect(isFreshTimestamp("", now)).toBe(false);
  });
});

describe("validateNewsPayload", () => {
  it("정상 페이로드 통과", () => {
    const r = validateNewsPayload(samplePayload());
    expect(r.ok).toBe(true);
  });
  it("알 수 없는 카테고리는 '기타'로 정규화", () => {
    const p = samplePayload();
    (p.items[0] as { category: string }).category = "코인";
    const r = validateNewsPayload(p);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.value.items[0].category).toBe("기타");
  });
  it("id 누락 항목 거절", () => {
    const p = samplePayload();
    (p.items[0] as { id: string }).id = "";
    const r = validateNewsPayload(p);
    expect(r.ok).toBe(false);
  });
  it("market_summary 누락 거절", () => {
    const r = validateNewsPayload({ ts: "x", items: [] });
    expect(r.ok).toBe(false);
  });
  it("숫자 id 도 문자열로 수용", () => {
    const p = samplePayload();
    (p.items[0] as unknown as { id: number }).id = 1001;
    const r = validateNewsPayload(p);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.value.items[0].id).toBe("1001");
  });
});

describe("verifySignature", () => {
  it("유효 서명 true, 위조 false", async () => {
    const body = JSON.stringify(samplePayload());
    const sig = await hmacHex(SECRET, `123.${body}`);
    expect(await verifySignature(SECRET, "123", body, sig)).toBe(true);
    expect(await verifySignature(SECRET, "123", body, sig.replace(/.$/, "0"))).toBe(false);
    expect(await verifySignature("wrong", "123", body, sig)).toBe(false);
    expect(await verifySignature(SECRET, "123", body, null)).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// persistNews
// ---------------------------------------------------------------------------
describe("persistNews", () => {
  it("항목 upsert + market_summary 1행을 batch 로 실행", async () => {
    const { db, calls, getBatchCount } = makeFakeD1();
    const n = await persistNews(db, samplePayload());
    expect(n).toBe(2);
    expect(getBatchCount()).toBe(1);
    // 2 항목 upsert + 1 market_summary
    expect(calls.length).toBe(3);
    expect(calls.filter((c) => c.sql.includes("news_summary")).length).toBe(2);
    expect(calls.filter((c) => c.sql.includes("market_summary")).length).toBe(1);
    // tickers 는 JSON 직렬화되어 들어감
    const first = calls.find((c) => c.args[0] === "fh-1001");
    expect(first?.args[5]).toBe(JSON.stringify(["NVDA"]));
  });

  it("market_summary 가 비면 그 행은 생략", async () => {
    const { db, calls } = makeFakeD1();
    const p = samplePayload();
    p.market_summary = "   ";
    await persistNews(db, p);
    expect(calls.filter((c) => c.sql.includes("market_summary")).length).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// handleIngestNews (계약 종단)
// ---------------------------------------------------------------------------
describe("handleIngestNews", () => {
  const now = 1_717_660_800;

  it("유효 요청 → 200 {ok, ingested}", async () => {
    const { db, calls } = makeFakeD1();
    const body = JSON.stringify(samplePayload());
    const req = await signedRequest(SECRET, now, body);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true, ingested: 2 });
    expect(calls.length).toBe(3);
  });

  it("시크릿 미설정 → 500", async () => {
    const { db } = makeFakeD1();
    const req = await signedRequest(SECRET, now, JSON.stringify(samplePayload()));
    const res = await handleIngestNews(req, db, undefined, now);
    expect(res.status).toBe(500);
  });

  it("만료된 타임스탬프 → 401", async () => {
    const { db } = makeFakeD1();
    const body = JSON.stringify(samplePayload());
    const staleTs = now - TIMESTAMP_TOLERANCE_SEC - 10;
    const req = await signedRequest(SECRET, staleTs, body);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(401);
    expect((await res.json() as { error: string }).error).toBe("invalid_or_stale_timestamp");
  });

  it("본문 변조(서명 불일치) → 401", async () => {
    const { db, calls } = makeFakeD1();
    const origBody = JSON.stringify(samplePayload());
    const sig = await hmacHex(SECRET, `${now}.${origBody}`);
    // 같은 서명으로 다른 본문 전송
    const tamperedBody = origBody.replace("혼조세", "급등세");
    const req = await signedRequest(SECRET, now, tamperedBody, sig);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(401);
    expect((await res.json() as { error: string }).error).toBe("invalid_signature");
    expect(calls.length).toBe(0); // 저장 안 함
  });

  it("잘못된 시크릿 → 401", async () => {
    const { db } = makeFakeD1();
    const body = JSON.stringify(samplePayload());
    const req = await signedRequest("attacker-secret", now, body);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(401);
  });

  it("서명은 유효하나 JSON 파싱 불가 → 400", async () => {
    const { db } = makeFakeD1();
    const notJson = "this is not json";
    const req = await signedRequest(SECRET, now, notJson);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(400);
    expect((await res.json() as { error: string }).error).toBe("invalid_json");
  });

  it("서명 유효 + 페이로드 형식 오류 → 400", async () => {
    const { db } = makeFakeD1();
    const body = JSON.stringify({ ts: "x", items: [] }); // market_summary 누락
    const req = await signedRequest(SECRET, now, body);
    const res = await handleIngestNews(req, db, SECRET, now);
    expect(res.status).toBe(400);
  });
});
