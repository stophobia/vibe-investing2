import "dotenv/config";

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`환경변수 ${name}가 설정되지 않았습니다. .env 파일을 확인할 것 (scripts/setup.sh 참고).`);
  }
  return value;
}

export const config = {
  port: Number(process.env.PORT ?? 4000),
  toss: {
    // 경로/베이스 URL은 ../../../Toss/src/toss.js, ../../../Toss/GUIDE.md에서 확인한 값과 동일하게 맞춘다.
    baseUrl: process.env.TOSS_BASE_URL ?? "https://openapi.tossinvest.com",
    tokenPath: process.env.TOSS_TOKEN_PATH ?? "/oauth2/token",
    candlesPath: process.env.TOSS_CANDLES_PATH ?? "/api/v1/candles",
    pricesPath: process.env.TOSS_PRICES_PATH ?? "/api/v1/prices",
    // 지연 평가: 서버 부팅 시점이 아니라 실제 인증이 필요한 시점에만 존재 여부를 검사한다.
    clientId: (): string => required("TOSS_CLIENT_ID"),
    clientSecret: (): string => required("TOSS_CLIENT_SECRET"),
  },
  redis: {
    url: process.env.REDIS_URL ?? "redis://127.0.0.1:6379",
  },
  cache: {
    // 토큰 유효기간은 24시간(86400초)이고 refresh token이 없어 직접 선제 재발급해야 한다.
    // 만료 임박 재발급 경쟁을 피하기 위해 기본 안전마진을 1시간으로 넉넉히 잡는다.
    tokenSafetyMarginSec: Number(process.env.TOKEN_SAFETY_MARGIN_SEC ?? 60 * 60),
    candleTtlHistoricalSec: Number(process.env.CANDLE_TTL_HISTORICAL_SEC ?? 60 * 60 * 24),
    candleTtlTodaySec: Number(process.env.CANDLE_TTL_TODAY_SEC ?? 30),
    priceTtlSec: Number(process.env.PRICE_TTL_SEC ?? 5),
    instrumentsTtlSec: Number(process.env.INSTRUMENTS_TTL_SEC ?? 60 * 60 * 24),
  },
  qlib: {
    exportDir: process.env.QLIB_CSV_EXPORT_DIR ?? "./csv_kr",
  },
};
