/**
 * 날짜 인덱스 시계열 — ARDS macro/rates 의 pandas Series(.index.intersection 등) 재현.
 * macro 의 구리/금·XLI/SPY·HYG/IEF 비율은 서로 다른 날짜를 교집합으로 정렬해야 하므로
 * 단순 number[] 가 아니라 날짜를 가진 시계열이 필요하다.
 */
import { isNum, mean } from "../series";

export interface DSeries {
  dates: string[]; // 오름차순
  values: number[];
}

export function dlen(s: DSeries): number {
  return s.values.length;
}
export function dlast(s: DSeries): number {
  return s.values[s.values.length - 1];
}
/** pandas iloc[-k] (k≥1). */
export function datEnd(s: DSeries, k: number): number {
  const i = s.values.length - k;
  return i >= 0 ? s.values[i] : Number.NaN;
}
/** 마지막 n개 값. */
export function dtail(s: DSeries, n: number): number[] {
  return s.values.slice(Math.max(0, s.values.length - n));
}
export function ddropNaN(s: DSeries): DSeries {
  const dates: string[] = [];
  const values: number[] = [];
  for (let i = 0; i < s.values.length; i++) {
    if (isNum(s.values[i])) {
      dates.push(s.dates[i]);
      values.push(s.values[i]);
    }
  }
  return { dates, values };
}

/**
 * 두 시계열을 날짜 교집합으로 정렬한 a/b 비율 시계열을 반환.
 * pandas: (a / b).dropna() 와 동일(공통 날짜만, 양쪽 유효값).
 */
export function ratioIntersect(a: DSeries, b: DSeries): number[] {
  const bMap = new Map<string, number>();
  for (let i = 0; i < b.dates.length; i++) if (isNum(b.values[i])) bMap.set(b.dates[i], b.values[i]);
  const out: number[] = [];
  for (let i = 0; i < a.dates.length; i++) {
    const av = a.values[i];
    const bv = bMap.get(a.dates[i]);
    if (isNum(av) && bv !== undefined && bv !== 0) out.push(av / bv);
  }
  return out;
}

/** pandas Series.rolling(w).mean() 의 끝점 = mean(마지막 w개). 길이 부족 시 NaN. */
export function rollingMeanEndingAt(values: number[], endIdx: number, w: number): number {
  const start = endIdx - w + 1;
  if (start < 0) return Number.NaN;
  return mean(values.slice(start, endIdx + 1));
}
