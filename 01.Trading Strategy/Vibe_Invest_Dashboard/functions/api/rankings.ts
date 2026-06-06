import { notImplemented } from "../../shared/http";

/**
 * GET /api/rankings — 오늘 검색 Top 5 (rankings 캐시 테이블 읽기만).
 * 구현 시: D1 rankings 읽기, cacheSeconds: 300.
 */
export const onRequestGet: PagesFunction = () => notImplemented("GET /api/rankings");
