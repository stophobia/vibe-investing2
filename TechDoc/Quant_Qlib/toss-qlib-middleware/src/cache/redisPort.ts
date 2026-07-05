/**
 * Redis 의존성을 추상화한 포트. 프로덕션은 ioredisAdapter, 테스트/로컬 검증은
 * memoryAdapter로 교체해 실제 Redis 서버 없이도 로직을 검증할 수 있다.
 */
export interface RedisPort {
  get(key: string): Promise<string | null>;
  set(key: string, value: string, ttlSec?: number): Promise<void>;
  /** SET NX + TTL. 락 선점에 성공하면 true. */
  setNX(key: string, value: string, ttlSec: number): Promise<boolean>;
  del(key: string): Promise<void>;
}
