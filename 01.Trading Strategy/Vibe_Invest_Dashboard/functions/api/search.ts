import { notImplemented } from "../../shared/http";

/**
 * GET /api/search?q=NVDA — 종목 기본정보 + 해당 종목 시그널. 검색 로그 D1 INSERT.
 * 쓰기(검색 로그)가 있으므로 캐시 금지(no-store). rate limit: 동일 user_hash 분당 30회.
 */
export const onRequestGet: PagesFunction = () => notImplemented("GET /api/search");
