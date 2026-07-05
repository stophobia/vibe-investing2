import type { RedisPort } from "../cache/redisPort.js";
import type { TossApiClient } from "./tossClient.js";
import type { QuotePrice, RawTossPrice } from "../types.js";

const SYMBOLS_PER_REQUEST = 200;

function toQuote(row: RawTossPrice): QuotePrice | null {
  const symbol = row.symbol ?? row.code;
  if (!symbol) return null;
  return {
    symbol,
    price: row.price ?? row.close ?? row.last ?? null,
    change: row.change ?? null,
    changeRate: row.changeRate ?? row.rate ?? null,
  };
}

/** 현재가 조회. 종목별로 캐시하고, 캐시 미스인 종목만 모아 최대 200개씩 배치 조회한다. */
export class PriceService {
  constructor(
    private readonly client: TossApiClient,
    private readonly redis: RedisPort,
    private readonly pricesPath: string,
    private readonly ttlSec: number,
  ) {}

  async getPrices(symbols: string[]): Promise<Map<string, QuotePrice>> {
    const result = new Map<string, QuotePrice>();
    const missing: string[] = [];

    for (const symbol of symbols) {
      const cached = await this.redis.get(`toss:price:${symbol}`);
      if (cached) result.set(symbol, JSON.parse(cached) as QuotePrice);
      else missing.push(symbol);
    }

    for (let i = 0; i < missing.length; i += SYMBOLS_PER_REQUEST) {
      const chunk = missing.slice(i, i + SYMBOLS_PER_REQUEST);
      const raw = await this.client.get<{ prices?: RawTossPrice[]; data?: RawTossPrice[] }>(this.pricesPath, {
        symbols: chunk.join(","),
      });

      for (const row of raw.prices ?? raw.data ?? []) {
        const quote = toQuote(row);
        if (!quote) continue;
        result.set(quote.symbol, quote);
        await this.redis.set(`toss:price:${quote.symbol}`, JSON.stringify(quote), this.ttlSec);
      }
    }

    return result;
  }
}
