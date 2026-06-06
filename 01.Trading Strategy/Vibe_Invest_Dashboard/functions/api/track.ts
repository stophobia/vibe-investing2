import { notImplemented } from "../../shared/http";

/**
 * POST /api/track — DAU/AU 기록 후 {dau, total_au} 반환.
 * 쓰기 + 개인화이므로 캐시 금지(no-store). user_hash = SHA-256(IP+UA+date+salt), 원본 IP 미저장.
 */
export const onRequestPost: PagesFunction = () => notImplemented("POST /api/track");
