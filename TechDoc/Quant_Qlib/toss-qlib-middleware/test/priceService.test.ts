import { test } from "node:test";
import assert from "node:assert/strict";
import { PriceService } from "../src/market/priceService.js";
import { createMemoryAdapter } from "../src/cache/memoryAdapter.js";
import type { TossApiClient } from "../src/market/tossClient.js";

function fakePriceClient(byCall: Record<string, { symbol: string; price: number }[]>) {
  let calls = 0;
  const client = {
    get: async (_path: string, params: Record<string, string>) => {
      calls++;
      return { prices: byCall[params.symbols] ?? [] };
    },
  };
  return { client: client as unknown as TossApiClient, getCalls: () => calls };
}

test("현재가는 종목별로 캐시되어 다음 조회에서는 API를 다시 부르지 않는다", async () => {
  const { client, getCalls } = fakePriceClient({
    "005930": [{ symbol: "005930", price: 71000 }],
  });
  const redis = createMemoryAdapter();
  const service = new PriceService(client, redis, "/api/v1/prices", 5);

  const first = await service.getPrices(["005930"]);
  const second = await service.getPrices(["005930"]);

  assert.equal(getCalls(), 1);
  assert.equal(first.get("005930")?.price, 71000);
  assert.deepEqual(first.get("005930"), second.get("005930"));
});

test("일부만 캐시 미스인 경우 미스난 종목만 배치로 재조회한다", async () => {
  const redis = createMemoryAdapter();
  await redis.set("toss:price:005930", JSON.stringify({ symbol: "005930", price: 71000, change: 0, changeRate: 0 }), 5);

  const { client, getCalls } = fakePriceClient({
    "000660": [{ symbol: "000660", price: 180000 }],
  });
  const service = new PriceService(client, redis, "/api/v1/prices", 5);

  const result = await service.getPrices(["005930", "000660"]);

  assert.equal(getCalls(), 1);
  assert.equal(result.get("005930")?.price, 71000);
  assert.equal(result.get("000660")?.price, 180000);
});
