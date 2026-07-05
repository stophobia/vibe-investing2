import { test } from "node:test";
import assert from "node:assert/strict";
import { TossAuthService, createTokenFetcher } from "../src/auth/tokenService.js";
import { createMemoryAdapter } from "../src/cache/memoryAdapter.js";

test("발급받은 토큰을 캐시하고 재사용한다 (중복 발급 호출 방지)", async () => {
  const redis = createMemoryAdapter();
  let calls = 0;
  const fetchToken = async () => {
    calls++;
    return { access_token: `token-${calls}`, token_type: "Bearer", expires_in: 3600 };
  };

  const auth = new TossAuthService(redis, "id", "secret", "https://example.com", "/oauth2/token", 60, fetchToken);

  const first = await auth.getAccessToken();
  const second = await auth.getAccessToken();

  assert.equal(first, "token-1");
  assert.equal(second, "token-1");
  assert.equal(calls, 1);
});

test("invalidate 이후에는 토큰을 다시 발급한다 (401 대응 시나리오)", async () => {
  const redis = createMemoryAdapter();
  let calls = 0;
  const fetchToken = async () => {
    calls++;
    return { access_token: `token-${calls}`, token_type: "Bearer", expires_in: 3600 };
  };

  const auth = new TossAuthService(redis, "id", "secret", "https://example.com", "/oauth2/token", 60, fetchToken);

  await auth.getAccessToken();
  await auth.invalidate();
  const reissued = await auth.getAccessToken();

  assert.equal(reissued, "token-2");
  assert.equal(calls, 2);
});

test("createTokenFetcher는 client_credentials를 Basic Auth가 아니라 form-urlencoded 바디로 전송한다", async () => {
  let capturedUrl = "";
  let capturedInit: RequestInit | undefined;

  const fakeFetch = (async (url: string | URL | Request, init?: RequestInit) => {
    capturedUrl = String(url);
    capturedInit = init;
    return new Response(JSON.stringify({ access_token: "abc", token_type: "Bearer", expires_in: 86400 }), {
      status: 200,
    });
  }) as typeof fetch;

  const fetcher = createTokenFetcher(fakeFetch);
  const token = await fetcher("id1", "secret1", "https://openapi.tossinvest.com", "/oauth2/token");

  assert.equal(capturedUrl, "https://openapi.tossinvest.com/oauth2/token");
  assert.equal(capturedInit?.method, "POST");
  const headers = (capturedInit?.headers ?? {}) as Record<string, string>;
  assert.equal(headers["Content-Type"], "application/x-www-form-urlencoded");
  assert.equal("Authorization" in headers, false);

  const body = String(capturedInit?.body);
  assert.match(body, /grant_type=client_credentials/);
  assert.match(body, /client_id=id1/);
  assert.match(body, /client_secret=secret1/);
  assert.equal(token.access_token, "abc");
  assert.equal(token.expires_in, 86400);
});
