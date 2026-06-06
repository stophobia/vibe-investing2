import { notImplemented } from "../../shared/http";

/**
 * GET /api/movers — 나스닥 급등10/급락10.
 * 구현 시: D1 movers 최신 ts 읽기, cacheSeconds: 300 (10분 크론 주기 기준).
 */
export const onRequestGet: PagesFunction = () => notImplemented("GET /api/movers");
