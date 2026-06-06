/**
 * POST /api/ingest/news — Pages Function 어댑터.
 * 실제 검증·저장 로직은 shared/ingest.ts (프레임워크 비의존). 계약: docs/PROMPT-azure-news.md.
 */
import { handleIngestNews } from "../../../shared/ingest";

interface Env {
  DB: D1Database;
  INGEST_SECRET?: string;
}

export const onRequestPost: PagesFunction<Env> = (ctx) =>
  handleIngestNews(ctx.request, ctx.env.DB, ctx.env.INGEST_SECRET);
