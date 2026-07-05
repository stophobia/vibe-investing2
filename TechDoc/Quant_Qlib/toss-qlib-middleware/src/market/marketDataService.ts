import type { RedisPort } from "../cache/redisPort.js";
import type { TossApiClient } from "./tossClient.js";
import type { CandleInterval, QlibCandleRow, RawTossCandle } from "../types.js";

const MAX_PAGES = 50;

export function includesToday(endDate: string): boolean {
  const today = new Date().toISOString().slice(0, 10);
  return endDate >= today;
}

function candleDate(row: RawTossCandle): string {
  const raw = row.date ?? row.time ?? row.timestamp;
  if (!raw) throw new Error("캔들 응답에 날짜 필드(date/time/timestamp)가 없습니다");
  return String(raw).slice(0, 10);
}

function toQlibRow(row: RawTossCandle, symbol: string): QlibCandleRow {
  const close = Number(row.close ?? row.c ?? 0);
  return {
    date: candleDate(row),
    open: Number(row.open ?? row.o ?? close),
    high: Number(row.high ?? row.h ?? close),
    low: Number(row.low ?? row.l ?? close),
    close,
    volume: Number(row.volume ?? row.v ?? 0),
    symbol,
    // 토스 캔들의 수정주가 반영 여부가 문서에 명시되지 않아 1.0으로 둔다.
    // 액면분할/배당락 반영이 필요하면 별도 factor 계산 로직을 추가할 것 (Qlib 가이드 7.3절 참고).
    factor: 1.0,
  };
}

/** 시세 조회 + Redis 캐시 + Qlib CSV 관례로의 정규화를 담당한다. */
export class MarketDataService {
  constructor(
    private readonly client: TossApiClient,
    private readonly redis: RedisPort,
    private readonly candlesPath: string,
    private readonly ttlHistoricalSec: number,
    private readonly ttlTodaySec: number,
    // 실 API는 요청당 최대 200개 캔들만 반환한다 (1분봉/일봉 한정).
    // 테스트에서는 작은 값으로 주입해 페이지네이션 로직을 검증한다.
    private readonly pageSize: number = 200,
  ) {}

  async getDailyCandles(
    symbol: string,
    start: string,
    end: string,
    interval: CandleInterval = "day",
  ): Promise<QlibCandleRow[]> {
    const cacheKey = `toss:candles:${symbol}:${interval}:${start}:${end}`;
    const cached = await this.redis.get(cacheKey);
    if (cached) return JSON.parse(cached) as QlibCandleRow[];

    const rows = await this.fetchAllCandles(symbol, start, end, interval);

    // 당일 캔들은 장중 갱신되므로 캐시를 짧게, 확정된 과거 캔들은 길게 유지한다.
    const ttl = includesToday(end) ? this.ttlTodaySec : this.ttlHistoricalSec;
    await this.redis.set(cacheKey, JSON.stringify(rows), ttl);

    return rows;
  }

  /**
   * 토스 캔들 API는 count(최대 200)만 지원하고 start/end 필터가 없다.
   * 최신 캔들부터 역순으로 내려받다가 목표 시작일 이전에 도달하면 멈추는
   * before 커서 페이지네이션이 필요하다 (../../../Toss/src/toss.js의 fetchCandles와 동일한 전략).
   */
  private async fetchAllCandles(
    symbol: string,
    start: string,
    end: string,
    interval: CandleInterval,
  ): Promise<QlibCandleRow[]> {
    const collected = new Map<string, RawTossCandle>();
    let before: string | undefined;

    for (let page = 0; page < MAX_PAGES; page++) {
      const params: Record<string, string> = {
        symbol,
        interval,
        count: String(this.pageSize),
      };
      if (before) params.before = before;

      const raw = await this.client.get<{ candles?: RawTossCandle[]; data?: RawTossCandle[] }>(
        this.candlesPath,
        params,
      );
      const rows = raw.candles ?? raw.data ?? [];
      if (rows.length === 0) break;

      for (const row of rows) collected.set(candleDate(row), row);

      const oldest = candleDate(rows[rows.length - 1]);
      if (rows.length < this.pageSize || oldest <= start) break;
      before = oldest;
    }

    return [...collected.values()]
      .map((row) => toQlibRow(row, symbol))
      .filter((row) => row.date >= start && row.date <= end)
      .sort((a, b) => a.date.localeCompare(b.date));
  }
}
