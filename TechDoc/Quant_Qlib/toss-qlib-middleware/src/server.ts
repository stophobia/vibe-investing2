import express from "express";
import { config } from "./config.js";
import { createIoRedisAdapter } from "./cache/ioredisAdapter.js";
import { TossAuthService } from "./auth/tokenService.js";
import { TossApiClient } from "./market/tossClient.js";
import { MarketDataService } from "./market/marketDataService.js";
import { PriceService } from "./market/priceService.js";
import { exportToQlibCsv } from "./market/qlibExport.js";
import type { CandleInterval } from "./types.js";

export function createServer() {
  const redis = createIoRedisAdapter(config.redis.url);
  const auth = new TossAuthService(
    redis,
    config.toss.clientId(),
    config.toss.clientSecret(),
    config.toss.baseUrl,
    config.toss.tokenPath,
    config.cache.tokenSafetyMarginSec,
  );
  const client = new TossApiClient(auth, config.toss.baseUrl);
  const marketData = new MarketDataService(
    client,
    redis,
    config.toss.candlesPath,
    config.cache.candleTtlHistoricalSec,
    config.cache.candleTtlTodaySec,
  );
  const priceService = new PriceService(client, redis, config.toss.pricesPath, config.cache.priceTtlSec);

  const app = express();
  app.use(express.json());

  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.get("/api/candles/:symbol", async (req, res) => {
    const { symbol } = req.params;
    const start = String(req.query.start ?? "");
    const end = String(req.query.end ?? "");
    const interval = (req.query.interval as CandleInterval | undefined) ?? "day";

    if (!start || !end) {
      res.status(400).json({ error: "start, end 쿼리 파라미터가 필요합니다 (YYYY-MM-DD)" });
      return;
    }

    try {
      const rows = await marketData.getDailyCandles(symbol, start, end, interval);
      res.json(rows);
    } catch (err) {
      res.status(502).json({ error: (err as Error).message });
    }
  });

  app.get("/api/prices", async (req, res) => {
    const symbols = String(req.query.symbols ?? "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    if (symbols.length === 0) {
      res.status(400).json({ error: "symbols 쿼리 파라미터가 필요합니다 (콤마로 구분)" });
      return;
    }

    try {
      const prices = await priceService.getPrices(symbols);
      res.json(Object.fromEntries(prices));
    } catch (err) {
      res.status(502).json({ error: (err as Error).message });
    }
  });

  app.post("/api/export/qlib", async (req, res) => {
    const { symbols, start, end, outDir } = req.body as {
      symbols?: string[];
      start?: string;
      end?: string;
      outDir?: string;
    };

    if (!symbols?.length || !start || !end) {
      res.status(400).json({ error: "symbols(배열), start, end가 필요합니다" });
      return;
    }

    try {
      const files: string[] = [];
      for (const symbol of symbols) {
        const rows = await marketData.getDailyCandles(symbol, start, end);
        files.push(await exportToQlibCsv(rows, outDir ?? config.qlib.exportDir, symbol));
      }
      res.json({ files });
    } catch (err) {
      res.status(502).json({ error: (err as Error).message });
    }
  });

  return app;
}
