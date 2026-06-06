/**
 * Vibe Investing — Cron Worker (스케줄 전용).
 *
 * Pages 는 Cron Trigger 를 지원하지 않으므로, 주기 작업만 담당하는 별도 Worker.
 * 결과는 R2/D1 에 미리 계산·저장 → Pages Functions(API)는 읽기만 + CDN 엣지 캐시.
 * (HTTP 라우팅·API 는 functions/ 의 Pages Functions 가 담당. 이 Worker 는 fetch 핸들러 없음.)
 *
 * 절대 규칙(요약): 무료 한도 준수, D1 쓰기 최소화, CPU 작업 최소화, 키는 env/secret만.
 */

export interface Env {
  DB: D1Database;
  SNAPSHOTS: R2Bucket;
  // secrets (wrangler secret put). 로컬은 .dev.vars.
  FINNHUB_KEY?: string;
  FMP_KEY?: string;
}

export default {
  // Cron 핸들러 (가이드 §2.1 / §2.3).
  // crons (cron-worker/wrangler.toml): 10분 주기 + 평일 미장마감(30 21 * * 1-5 UTC).
  async scheduled(event: ScheduledController, _env: Env, _ctx: ExecutionContext): Promise<void> {
    switch (event.cron) {
      case "*/10 * * * *":
        // TODO(#9): 시세/섹터/급등급락 수집 → R2 snapshots + D1 요약 (장외시간 조기 return)
        break;
      case "30 21 * * 1-5":
        // TODO(#9): 일봉 수집 → ARDS/AMQS 시그널 엔진(shared) 실행 → D1 signals
        break;
    }
  },
} satisfies ExportedHandler<Env>;
