import { notImplemented } from "../../shared/http";

/**
 * GET /api/dashboard — 시그널+스냅샷+통계 통합 1콜 (프론트 초기 로딩).
 * 구현 시: 크론이 미리 만든 D1/R2 데이터를 읽기만, jsonResponse(..., {cacheSeconds: 60}) 로 엣지 캐시.
 */
export const onRequestGet: PagesFunction = () => notImplemented("GET /api/dashboard");
