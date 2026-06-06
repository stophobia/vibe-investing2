-- Vibe Investing — D1 초기 스키마 (가이드 §3)
-- 적용: wrangler d1 migrations apply vibe-investing-db --local | --remote
-- 원칙: D1 쓰기 최소화. 시세 원본은 R2 스냅샷, D1엔 프론트 폴링용 요약만.

-- 시장 스냅샷 (10분 갱신, 최신 1행 + 히스토리)
CREATE TABLE IF NOT EXISTS market_snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,                -- ISO8601 UTC
  indices_json TEXT NOT NULL,      -- {"QQQ":{"price":..,"chg_pct":..}, ...}
  sectors_json TEXT NOT NULL,      -- 11개 섹터 ETF 등락
  vix REAL,
  breadth_json TEXT                -- 상승/하락 종목수 등
);

-- 급등/급락
CREATE TABLE IF NOT EXISTS movers (
  ts TEXT NOT NULL,
  direction TEXT CHECK(direction IN ('gainer','loser')),
  rank INTEGER,
  ticker TEXT, name TEXT, price REAL, chg_pct REAL, volume INTEGER,
  PRIMARY KEY (ts, direction, rank)
);

-- 전략 시그널
CREATE TABLE IF NOT EXISTS signals (
  date TEXT NOT NULL,              -- YYYY-MM-DD (미국 거래일)
  strategy TEXT NOT NULL,          -- ARDS | AMQS | MU_HYNIX
  ticker TEXT NOT NULL,
  signal TEXT CHECK(signal IN ('BUY','SELL','HOLD','SHORT_TERM_RISK','SURGE')),
  score REAL,                      -- 전략 내부 점수 (선택)
  detail_json TEXT,                -- 근거 지표 값 (Phase 2에서 프론트 노출, 수집은 1차부터)
  PRIMARY KEY (date, strategy, ticker)
);

-- 뉴스 요약 (Azure → ingest)
CREATE TABLE IF NOT EXISTS news_summary (
  id TEXT PRIMARY KEY,             -- 뉴스 원본 ID
  ts TEXT NOT NULL,
  title_ko TEXT, summary_ko TEXT,
  category TEXT, tickers_json TEXT,
  source TEXT, url TEXT
);

-- 전체 시장 2문장 요약 (최신 1행 유지)
CREATE TABLE IF NOT EXISTS market_summary (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  ts TEXT, summary_ko TEXT
);

-- 검색 로그 & 랭킹
CREATE TABLE IF NOT EXISTS searches (
  ts TEXT NOT NULL,
  date TEXT NOT NULL,              -- 집계용
  ticker TEXT NOT NULL,
  user_hash TEXT                   -- 익명 해시 (선택)
);
CREATE INDEX IF NOT EXISTS idx_searches_date ON searches(date, ticker);

CREATE TABLE IF NOT EXISTS rankings (   -- 크론이 10분마다 집계해 캐시
  date TEXT NOT NULL,
  rank INTEGER,
  ticker TEXT, search_count INTEGER,
  PRIMARY KEY (date, rank)
);

-- DAU / 누적 AU
CREATE TABLE IF NOT EXISTS daily_users (
  date TEXT NOT NULL,
  user_hash TEXT NOT NULL,         -- SHA-256(IP + UA + date + salt)
  PRIMARY KEY (date, user_hash)
);
CREATE TABLE IF NOT EXISTS all_users (
  user_hash TEXT PRIMARY KEY,      -- SHA-256(IP + UA + salt) — date 미포함
  first_seen TEXT
);
CREATE TABLE IF NOT EXISTS stats_cache (   -- 프론트 표시용 집계 캐시
  key TEXT PRIMARY KEY,            -- 'dau' | 'total_au' | 'last_update'
  value TEXT, ts TEXT
);
