import { test } from "node:test";
import assert from "node:assert/strict";
import { MarketDataService, includesToday } from "../src/market/marketDataService.js";
import { createMemoryAdapter } from "../src/cache/memoryAdapter.js";
import type { TossApiClient } from "../src/market/tossClient.js";

function fakeClient(candles: { date: string; open: number; high: number; low: number; close: number; volume: number }[]) {
  let calls = 0;
  const client = {
    get: async () => {
      calls++;
      return { candles };
    },
  };
  return { client: client as unknown as TossApiClient, getCalls: () => calls };
}

test("과거 구간 조회는 Redis에 캐시되어 두 번째 호출부터 API를 다시 부르지 않는다", async () => {
  const { client, getCalls } = fakeClient([
    { date: "2020-01-02", open: 100, high: 105, low: 95, close: 102, volume: 1000 },
  ]);
  const redis = createMemoryAdapter();
  const service = new MarketDataService(client, redis, "/api/v1/candles", 86400, 30);

  const first = await service.getDailyCandles("005930", "2020-01-01", "2020-01-31");
  const second = await service.getDailyCandles("005930", "2020-01-01", "2020-01-31");

  assert.equal(getCalls(), 1);
  assert.deepEqual(first, second);
  assert.equal(first[0]?.symbol, "005930");
  assert.equal(first[0]?.factor, 1.0);
});

test("includesToday: end 날짜가 오늘 이상이면 당일 포함으로 판단한다", () => {
  const today = new Date().toISOString().slice(0, 10);
  assert.equal(includesToday(today), true);
  assert.equal(includesToday("2000-01-01"), false);
  assert.equal(includesToday("2999-01-01"), true);
});

test("당일이 포함된 구간은 짧은 TTL(ttlTodaySec)로 캐시된다", async () => {
  const today = new Date().toISOString().slice(0, 10);
  const { client } = fakeClient([{ date: today, open: 1, high: 1, low: 1, close: 1, volume: 1 }]);
  const redis = createMemoryAdapter();
  const service = new MarketDataService(client, redis, "/api/v1/candles", 86400, 1);

  await service.getDailyCandles("005930", "2026-07-01", today);

  await new Promise((resolve) => setTimeout(resolve, 1100));
  const cached = await redis.get(`toss:candles:005930:day:2026-07-01:${today}`);
  assert.equal(cached, null, "ttlTodaySec=1초 경과 후에는 만료되어야 한다");
});

/**
 * 실 API는 요청당 최대 count개(문서 기준 200) 캔들만 반환하고 start/end 필터가 없어,
 * 최신 캔들부터 before 커서로 역순 페이지네이션해야 한다 (../../../Toss/src/toss.js와 동일한 전략).
 * pageSize를 작게 주입해 여러 페이지를 걸쳐야 하는 상황을 재현한다.
 */
function pagedFakeClient(allDescending: { date: string; close: number }[], pageSize: number) {
  let calls = 0;
  const client = {
    get: async (_path: string, params: Record<string, string>) => {
      calls++;
      let startIdx = 0;
      if (params.before) {
        startIdx = allDescending.findIndex((c) => c.date === params.before) + 1;
      }
      return { candles: allDescending.slice(startIdx, startIdx + pageSize) };
    },
  };
  return { client: client as unknown as TossApiClient, getCalls: () => calls };
}

test("count 제한을 넘는 구간은 before 커서로 여러 페이지를 이어붙여 오름차순 정렬한다", async () => {
  const allDescending = [
    { date: "2020-01-05", close: 5 },
    { date: "2020-01-04", close: 4 },
    { date: "2020-01-03", close: 3 },
    { date: "2020-01-02", close: 2 },
    { date: "2020-01-01", close: 1 },
  ];
  const { client, getCalls } = pagedFakeClient(allDescending, 2);
  const redis = createMemoryAdapter();
  const service = new MarketDataService(client, redis, "/api/v1/candles", 86400, 30, 2);

  const rows = await service.getDailyCandles("005930", "2020-01-01", "2020-01-05");

  assert.deepEqual(
    rows.map((r) => r.date),
    ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"],
  );
  assert.ok(getCalls() >= 3, `pageSize=2로 5건을 받으려면 최소 3페이지 필요 (실제 ${getCalls()})`);
});
