/**
 * 공통 HTTP 응답 헬퍼 — Pages Functions / Worker 양쪽에서 사용.
 *
 * CDN 캐시 원칙(중요): 주기 갱신 데이터는 크론이 R2/D1에 미리 계산·저장하고,
 * 읽기 API 는 연산 없이 그걸 반환하면서 `Cache-Control: public, s-maxage=...` 로
 * Cloudflare 엣지에 캐싱한다. 사용자 요청당 origin 연산을 0에 가깝게 유지(무료 한도 절약).
 *   - s-maxage : 공유(CDN) 캐시 TTL. 브라우저 max-age 와 분리.
 *   - stale-while-revalidate : TTL 만료 후에도 갱신 동안 직전값 제공(빈 화면 방지).
 *   - 쓰기/개인화 응답은 cacheSeconds 생략 → no-store.
 */

export interface JsonOptions {
  status?: number;
  /** 데이터 갱신 시각 (ISO8601). envelope 의 updated_at. */
  updatedAt?: string | null;
  /** CDN 공유 캐시 TTL(초). 지정 시 public+s-maxage, 미지정 시 no-store. */
  cacheSeconds?: number;
}

/** 공통 envelope: { data, updated_at, disclaimer } (가이드 §4). */
export function jsonResponse(data: unknown, opts: JsonOptions = {}): Response {
  const { status = 200, updatedAt = null, cacheSeconds } = opts;
  const cacheControl =
    cacheSeconds && cacheSeconds > 0
      ? `public, s-maxage=${cacheSeconds}, stale-while-revalidate=${cacheSeconds * 2}`
      : "no-store";
  return new Response(JSON.stringify({ data, updated_at: updatedAt, disclaimer: true }), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": cacheControl,
    },
  });
}

export function notImplemented(endpoint: string): Response {
  return jsonResponse({ error: "not_implemented", endpoint }, { status: 501 });
}

export function notFound(): Response {
  return jsonResponse({ error: "not_found" }, { status: 404 });
}
