import { config } from "./config.js";
import { createIoRedisAdapter } from "./cache/ioredisAdapter.js";
import { TossAuthService } from "./auth/tokenService.js";
import { TossApiClient } from "./market/tossClient.js";
import { MarketDataService } from "./market/marketDataService.js";
import { exportToQlibCsv } from "./market/qlibExport.js";

function parseArgs(argv: string[]): Record<string, string> {
  const args: Record<string, string> = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i]?.replace(/^--/, "");
    if (key) args[key] = argv[i + 1] ?? "";
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const symbols = (args.symbols ?? "").split(",").filter(Boolean);
  const { start, end } = args;

  if (symbols.length === 0 || !start || !end) {
    console.error("사용법: npm run export:qlib -- --symbols 005930,000660 --start 2020-01-01 --end 2026-07-01");
    process.exit(1);
  }

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

  for (const symbol of symbols) {
    const rows = await marketData.getDailyCandles(symbol, start, end);
    const filePath = await exportToQlibCsv(rows, args.outDir ?? config.qlib.exportDir, symbol);
    console.log(`${symbol} -> ${filePath} (${rows.length} rows)`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
