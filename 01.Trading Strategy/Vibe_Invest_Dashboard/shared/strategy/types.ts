/**
 * 시그널 엔진 — 데이터 인터페이스 (프레임워크/소스 비의존).
 *
 * 순수 룰 로직(ARDS·AMQS)은 아래 PriceSeries/FredSeries 만 입력으로 받는다.
 * 실제 수집(Stooq CSV · FRED CSV · yfinance 프록시)은 DataProvider 구현체로 분리 →
 * Cron Worker 가 주입. 엔진은 데이터 출처를 모른다(테스트는 fixture provider 로 대체).
 */

/** 일봉 1개. close 만 있으면 동작(Stooq/yfinance 종가 기반). */
export interface Bar {
  date: string; // YYYY-MM-DD
  close: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
}

/** 시간 오름차순(과거→현재) 일봉 시계열. */
export interface PriceSeries {
  ticker: string;
  bars: Bar[];
}

/** FRED 등 매크로 시계열 1점. */
export interface SeriesPoint {
  date: string;
  value: number;
}

/** 데이터 수집 추상화. 구현체(StooqProvider 등)는 후속 단계에서. */
export interface DataProvider {
  /** 일봉 lookback 일치 수집. 영업일 정렬·결측 처리는 구현체 책임. */
  getDaily(ticker: string, lookbackDays: number): Promise<PriceSeries>;
  /** 여러 티커 일괄(레이트리밋 최적화). */
  getDailyBatch?(tickers: string[], lookbackDays: number): Promise<Record<string, PriceSeries>>;
  /** FRED 무료 CSV 시계열(키 불필요). ARDS 거시축용. */
  getFredSeries?(seriesId: string): Promise<SeriesPoint[]>;
}

/** PriceSeries → 종가 배열(엔진 내부 계산용). */
export function closes(s: PriceSeries): number[] {
  return s.bars.map((b) => b.close);
}

/** 대시보드 통일 시그널 enum (D1 signals.signal). */
export type DashboardSignal = "BUY" | "SELL" | "HOLD" | "SHORT_TERM_RISK" | "SURGE";
