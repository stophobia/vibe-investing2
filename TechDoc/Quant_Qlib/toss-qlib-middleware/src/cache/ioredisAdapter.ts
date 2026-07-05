import Redis from "ioredis";
import type { RedisPort } from "./redisPort.js";

export function createIoRedisAdapter(url: string): RedisPort {
  const client = new Redis(url);

  return {
    async get(key) {
      return client.get(key);
    },
    async set(key, value, ttlSec) {
      if (ttlSec) {
        await client.set(key, value, "EX", ttlSec);
      } else {
        await client.set(key, value);
      }
    },
    async setNX(key, value, ttlSec) {
      const result = await client.set(key, value, "EX", ttlSec, "NX");
      return result === "OK";
    },
    async del(key) {
      await client.del(key);
    },
  };
}
