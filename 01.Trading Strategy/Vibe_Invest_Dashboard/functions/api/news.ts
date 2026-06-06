import { notImplemented } from "../../shared/http";

/**
 * GET /api/news?limit=10 — 최신 뉴스 요약 + 시장 요약 (D1 news_summary / market_summary 읽기).
 * 구현 시: cacheSeconds: 300 (Azure 뉴스 갱신 주기보다 짧게).
 */
export const onRequestGet: PagesFunction = () => notImplemented("GET /api/news");
