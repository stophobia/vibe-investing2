/**
 * 수치 primitive — pandas/numpy 시맨틱을 의도적으로 1:1 재현.
 * (포팅 충실도가 최우선이라 라이브러리 대신 직접 구현. ddof·ewm adjust 등 동작을 원본과 일치시킴.)
 *
 * 규칙:
 *  - NaN 은 JS Number.NaN 으로 표현. 대부분의 통계 함수는 호출 전 dropNaN 을 가정(pandas .dropna() 대응).
 *  - 인덱싱은 "끝에서 n번째" 헬퍼(atFromEnd)로 pandas iloc[-k] 를 재현.
 */

export const SQRT_252 = Math.sqrt(252);

export function isNum(x: number): boolean {
  return typeof x === "number" && !Number.isNaN(x);
}

/** pandas Series.dropna() */
export function dropNaN(xs: number[]): number[] {
  return xs.filter(isNum);
}

/** pandas iloc[-k] (k≥1). 범위 밖이면 NaN. */
export function atFromEnd(xs: number[], k: number): number {
  const i = xs.length - k;
  return i >= 0 && i < xs.length ? xs[i] : Number.NaN;
}

export function sum(xs: number[]): number {
  let s = 0;
  for (const x of xs) s += x;
  return s;
}

/** 산술평균 (clean array 가정). */
export function mean(xs: number[]): number {
  if (xs.length === 0) return Number.NaN;
  return sum(xs) / xs.length;
}

/**
 * 표준편차. ddof=1(표본, pandas .std() 기본) 또는 ddof=0(모집단, numpy .std() 기본).
 * 분모가 0 이하이면 NaN.
 */
export function std(xs: number[], ddof = 1): number {
  const n = xs.length;
  if (n - ddof <= 0) return Number.NaN;
  const m = mean(xs);
  let acc = 0;
  for (const x of xs) acc += (x - m) * (x - m);
  return Math.sqrt(acc / (n - ddof));
}

export function median(xs: number[]): number {
  if (xs.length === 0) return Number.NaN;
  const s = [...xs].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}

/** pandas Series.diff(): 결과[0]=NaN, 결과[i]=x[i]-x[i-1]. */
export function diff(xs: number[]): number[] {
  const out = new Array<number>(xs.length);
  out[0] = Number.NaN;
  for (let i = 1; i < xs.length; i++) out[i] = xs[i] - xs[i - 1];
  return out;
}

/** pandas Series.pct_change(): 결과[0]=NaN, 결과[i]=x[i]/x[i-1]-1. */
export function pctChange(xs: number[]): number[] {
  const out = new Array<number>(xs.length);
  out[0] = Number.NaN;
  for (let i = 1; i < xs.length; i++) out[i] = xs[i] / xs[i - 1] - 1;
  return out;
}

/**
 * 지수가중이동평균, pandas .ewm(alpha, adjust=False).mean().
 *   y[0] = x[0]; y[i] = alpha*x[i] + (1-alpha)*y[i-1]
 * NaN 입력은 직전 y 를 유지(pandas 기본 ignore_na=False 와 근사) — 본 용도(연속 종가)에선 NaN 없음.
 */
export function ewmMeanAdjustFalse(xs: number[], alpha: number): number[] {
  const out = new Array<number>(xs.length);
  let prev = Number.NaN;
  for (let i = 0; i < xs.length; i++) {
    const x = xs[i];
    if (!isNum(x)) {
      out[i] = prev;
      continue;
    }
    prev = isNum(prev) ? alpha * x + (1 - alpha) * prev : x;
    out[i] = prev;
  }
  return out;
}

/** pandas Series.cummax(). */
export function cumMax(xs: number[]): number[] {
  const out = new Array<number>(xs.length);
  let m = -Infinity;
  for (let i = 0; i < xs.length; i++) {
    if (xs[i] > m) m = xs[i];
    out[i] = m;
  }
  return out;
}

export function maxOf(xs: number[]): number {
  let m = -Infinity;
  for (const x of xs) if (x > m) m = x;
  return m;
}

export function minOf(xs: number[]): number {
  let m = Infinity;
  for (const x of xs) if (x < m) m = x;
  return m;
}

/** 마지막 period 개의 단순이동평균(끝점). 길이 부족 시 NaN. */
export function smaLast(xs: number[], period: number): number {
  if (xs.length < period) return Number.NaN;
  return mean(xs.slice(xs.length - period));
}

export function clip(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x));
}

/** ARDS macro/rates 의 _lin: x 가 lo→hi 로 갈수록 0→100 (clip). */
export function lin(x: number, lo: number, hi: number): number {
  if (hi === lo) return 50.0;
  return clip(((x - lo) / (hi - lo)) * 100.0, 0, 100);
}

/**
 * Python 내장 round(x, nd) 재현 — 동률은 짝수로(banker's rounding).
 * ARDS 는 지표를 반올림한 뒤 그 값으로 점수를 계산하므로 반올림 방식을 일치시켜야 한다.
 * 이진 부동소수 표현은 양쪽 언어가 동일하므로 *10^nd 후 정수화로 Python 과 같은 결과를 낸다.
 */
export function pyRound(x: number, nd = 0): number {
  if (!Number.isFinite(x)) return x;
  const m = 10 ** nd;
  const y = x * m;
  const floor = Math.floor(y);
  const frac = y - floor;
  let r: number;
  if (frac === 0.5) {
    // 정확히 절반일 때만 동률 → 짝수(banker's). 근사 epsilon 을 쓰면
    // 1.3499999998 같은 비동률 값을 거짓 동률로 처리해 0.1 오차가 난다.
    r = floor % 2 === 0 ? floor : floor + 1;
  } else {
    r = Math.round(y); // 비동률 → 최근접
  }
  return r / m;
}
