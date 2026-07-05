export interface TossTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export type CandleInterval = "day" | "1min";

/**
 * 실제 토스 Open API 캔들 응답 필드명은 공식 스펙 원문(openapi.json) 미확보로
 * 완전히 확정되지 않아, ../../../Toss/src/toss.js와 동일하게 여러 후보 키를
 * 모두 허용한다 (date/time/timestamp, open/o, close/c 등).
 */
export interface RawTossCandle {
  date?: string;
  time?: string;
  timestamp?: string;
  open?: number;
  o?: number;
  high?: number;
  h?: number;
  low?: number;
  l?: number;
  close?: number;
  c?: number;
  volume?: number;
  v?: number;
}

export interface RawTossPrice {
  symbol?: string;
  code?: string;
  price?: number;
  close?: number;
  last?: number;
  change?: number;
  changeRate?: number;
  rate?: number;
}

export interface QuotePrice {
  symbol: string;
  price: number | null;
  change: number | null;
  changeRate: number | null;
}

/** Qlib CSV 관례(문서 7.1절): date,open,high,low,close,volume,symbol,factor */
export interface QlibCandleRow {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  symbol: string;
  factor: number;
}
