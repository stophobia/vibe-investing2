import type { RedisPort } from "./redisPort.js";

interface Entry {
  value: string;
  expiresAt: number | null;
}

/** Redis 서버 없이 단위 테스트/로컬 실행을 위한 인메모리 구현. 프로덕션에서는 사용하지 말 것. */
export function createMemoryAdapter(): RedisPort {
  const store = new Map<string, Entry>();

  function isExpired(entry: Entry): boolean {
    return entry.expiresAt !== null && Date.now() > entry.expiresAt;
  }

  return {
    async get(key) {
      const entry = store.get(key);
      if (!entry || isExpired(entry)) {
        store.delete(key);
        return null;
      }
      return entry.value;
    },
    async set(key, value, ttlSec) {
      store.set(key, { value, expiresAt: ttlSec !== undefined ? Date.now() + ttlSec * 1000 : null });
    },
    async setNX(key, value, ttlSec) {
      const existing = store.get(key);
      if (existing && !isExpired(existing)) return false;
      store.set(key, { value, expiresAt: Date.now() + ttlSec * 1000 });
      return true;
    },
    async del(key) {
      store.delete(key);
    },
  };
}
