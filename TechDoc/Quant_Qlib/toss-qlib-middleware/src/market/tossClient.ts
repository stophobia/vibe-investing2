import type { TossAuthService } from "../auth/tokenService.js";

export type HttpFetcher = (url: string, init?: RequestInit) => Promise<Response>;

/** 인증 헤더 부착, 401 시 토큰 재발급, 429 시 backoff 재시도를 처리하는 얇은 HTTP 클라이언트. */
export class TossApiClient {
  constructor(
    private readonly auth: TossAuthService,
    private readonly baseUrl: string,
    private readonly fetchImpl: HttpFetcher = fetch,
  ) {}

  async get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
    const query = new URLSearchParams(params).toString();
    const url = `${this.baseUrl}${path}${query ? `?${query}` : ""}`;

    const call = async (): Promise<Response> => {
      const token = await this.auth.getAccessToken();
      return this.fetchImpl(url, { headers: { Authorization: `Bearer ${token}` } });
    };

    let res = await call();

    if (res.status === 401) {
      await this.auth.invalidate();
      res = await call();
    }

    if (res.status === 429) {
      const retryAfterSec = Number(res.headers.get("retry-after") ?? "1");
      await new Promise((resolve) => setTimeout(resolve, retryAfterSec * 1000));
      res = await call();
    }

    if (!res.ok) {
      throw new Error(`TOSS API 오류: ${res.status} ${path}`);
    }
    return (await res.json()) as T;
  }
}
