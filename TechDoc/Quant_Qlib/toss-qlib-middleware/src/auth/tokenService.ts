import type { RedisPort } from "../cache/redisPort.js";
import type { TossTokenResponse } from "../types.js";

const TOKEN_KEY = "toss:access_token";
const LOCK_KEY = "toss:access_token:lock";

export type TokenFetcher = (
  clientId: string,
  clientSecret: string,
  baseUrl: string,
  tokenPath: string,
) => Promise<TossTokenResponse>;

/**
 * OAuth2 Client Credentials Grant. 토스증권 Open API는 client_id/secret을 Basic Auth가 아니라
 * form-urlencoded 바디로 전달한다 (../../../Toss/src/toss.js, ../../../Toss/GUIDE.md 기준 확인).
 * fetchImpl을 주입받게 해 테스트에서 실제 네트워크 없이 요청 형태를 검증할 수 있게 한다.
 */
export function createTokenFetcher(fetchImpl: typeof fetch = fetch): TokenFetcher {
  return async (clientId, clientSecret, baseUrl, tokenPath) => {
    const body = new URLSearchParams({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    });
    const res = await fetchImpl(`${baseUrl}${tokenPath}`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!res.ok) {
      throw new Error(`토큰 발급 실패: ${res.status} ${await res.text()}`);
    }
    return (await res.json()) as TossTokenResponse;
  };
}

export const defaultTokenFetcher: TokenFetcher = createTokenFetcher();

/**
 * 액세스 토큰을 Redis에 캐시한다. 여러 인스턴스/요청이 동시에 만료를 감지해도
 * setNX 락으로 한 번만 재발급하도록 해 thundering herd를 방지한다.
 */
export class TossAuthService {
  constructor(
    private readonly redis: RedisPort,
    private readonly clientId: string,
    private readonly clientSecret: string,
    private readonly baseUrl: string,
    private readonly tokenPath: string,
    private readonly safetyMarginSec: number,
    private readonly fetchToken: TokenFetcher = defaultTokenFetcher,
  ) {}

  async getAccessToken(): Promise<string> {
    const cached = await this.redis.get(TOKEN_KEY);
    if (cached) return cached;

    const gotLock = await this.redis.setNX(LOCK_KEY, "1", 10);
    if (!gotLock) {
      // 다른 요청이 이미 재발급 중이므로 잠깐 대기 후 캐시를 다시 확인한다.
      await new Promise((resolve) => setTimeout(resolve, 300));
      const retried = await this.redis.get(TOKEN_KEY);
      if (retried) return retried;
      throw new Error("토큰 발급 락 대기 중 타임아웃");
    }

    try {
      const token = await this.fetchToken(this.clientId, this.clientSecret, this.baseUrl, this.tokenPath);
      const ttl = Math.max(token.expires_in - this.safetyMarginSec, 30);
      await this.redis.set(TOKEN_KEY, token.access_token, ttl);
      return token.access_token;
    } finally {
      await this.redis.del(LOCK_KEY);
    }
  }

  /** 401 응답을 받았을 때 강제로 캐시를 비우고 다음 호출에서 재발급하도록 한다. */
  async invalidate(): Promise<void> {
    await this.redis.del(TOKEN_KEY);
  }
}
