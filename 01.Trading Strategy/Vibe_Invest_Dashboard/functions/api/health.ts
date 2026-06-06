import { jsonResponse } from "../../shared/http";

/** GET /api/health — 스캐폴드 동작 확인용. */
export const onRequestGet: PagesFunction = () =>
  jsonResponse({ ok: true, service: "vibe-investing", stage: "scaffold" });
