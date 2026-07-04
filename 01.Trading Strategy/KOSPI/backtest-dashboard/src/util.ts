// Small numeric / date / stats / csv utilities (no external deps).

// Deterministic PRNG (mulberry32) for reproducibility.
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Box-Muller standard normal from a uniform generator.
export function makeNormal(rng: () => number): () => number {
  let spare: number | null = null;
  return function () {
    if (spare !== null) {
      const s = spare;
      spare = null;
      return s;
    }
    let u = 0;
    let v = 0;
    let s = 0;
    do {
      u = rng() * 2 - 1;
      v = rng() * 2 - 1;
      s = u * u + v * v;
    } while (s >= 1 || s === 0);
    const mul = Math.sqrt((-2 * Math.log(s)) / s);
    spare = v * mul;
    return u * mul;
  };
}

export function mean(xs: number[]): number {
  if (xs.length === 0) return NaN;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

export function std(xs: number[], sample = true): number {
  const n = xs.length;
  if (n < 2) return 0;
  const m = mean(xs);
  const ss = xs.reduce((a, b) => a + (b - m) * (b - m), 0);
  return Math.sqrt(ss / (n - (sample ? 1 : 0)));
}

export function median(xs: number[]): number {
  if (xs.length === 0) return NaN;
  const s = [...xs].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}

// Cross-sectional z-score.
export function zscore(xs: number[]): number[] {
  const m = mean(xs);
  const s = std(xs);
  if (s === 0) return xs.map(() => 0);
  return xs.map((x) => (x - m) / s);
}

// Winsorize at the given tail fraction (e.g. 0.01 = 1% both sides).
export function winsorize(xs: number[], p = 0.01): number[] {
  if (xs.length === 0) return xs;
  const s = [...xs].sort((a, b) => a - b);
  const lo = s[Math.floor(p * (s.length - 1))];
  const hi = s[Math.ceil((1 - p) * (s.length - 1))];
  return xs.map((x) => Math.min(hi, Math.max(lo, x)));
}

// Percentile rank in [0,1] within an array of values.
export function percentileRank(xs: number[]): number[] {
  const n = xs.length;
  if (n === 1) return [0.5];
  const idx = xs.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const rank = new Array<number>(n);
  for (let k = 0; k < n; k++) rank[idx[k].i] = k / (n - 1);
  return rank;
}

// Spearman rank correlation. Returns null if not computable.
export function spearman(a: number[], b: number[]): number | null {
  const pairs = a.map((v, i) => [v, b[i]] as const).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 5) return null;
  const ra = rankArray(pairs.map((p) => p[0]));
  const rb = rankArray(pairs.map((p) => p[1]));
  const mra = mean(ra);
  const mrb = mean(rb);
  let num = 0;
  let da = 0;
  let db = 0;
  for (let i = 0; i < ra.length; i++) {
    const x = ra[i] - mra;
    const y = rb[i] - mrb;
    num += x * y;
    da += x * x;
    db += y * y;
  }
  if (da === 0 || db === 0) return null;
  return num / Math.sqrt(da * db);
}

function rankArray(xs: number[]): number[] {
  const idx = xs.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const rank = new Array<number>(xs.length);
  let i = 0;
  while (i < idx.length) {
    let j = i;
    while (j + 1 < idx.length && idx[j + 1].v === idx[i].v) j++;
    const avg = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) rank[idx[k].i] = avg;
    i = j + 1;
  }
  return rank;
}

// ---- Date helpers (operate on YYYY-MM-DD strings, UTC-safe) ----

export function parseDate(s: string): Date {
  return new Date(s + "T00:00:00Z");
}

export function fmtDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function addDays(s: string, days: number): string {
  const d = parseDate(s);
  d.setUTCDate(d.getUTCDate() + days);
  return fmtDate(d);
}

export function addMonths(s: string, months: number): string {
  const d = parseDate(s);
  d.setUTCMonth(d.getUTCMonth() + months);
  return fmtDate(d);
}

export function monthKey(s: string): string {
  return s.slice(0, 7);
}

export function yearOf(s: string): number {
  return Number(s.slice(0, 4));
}

// ---- CSV ----

export function toCsv(rows: Record<string, unknown>[], columns?: string[]): string {
  if (rows.length === 0) return (columns ?? []).join(",") + "\n";
  const cols = columns ?? Object.keys(rows[0]);
  const esc = (v: unknown) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [cols.join(",")];
  for (const r of rows) lines.push(cols.map((c) => esc(r[c])).join(","));
  return lines.join("\n") + "\n";
}

export function parseCsv(text: string): Record<string, string>[] {
  const lines = text.split(/\r?\n/).filter((l) => l.length > 0);
  if (lines.length === 0) return [];
  const cols = splitCsvLine(lines[0]);
  const out: Record<string, string>[] = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = splitCsvLine(lines[i]);
    const row: Record<string, string> = {};
    for (let c = 0; c < cols.length; c++) row[cols[c]] = vals[c] ?? "";
    out.push(row);
  }
  return out;
}

function splitCsvLine(line: string): string[] {
  const out: string[] = [];
  let cur = "";
  let inQ = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQ) {
      if (ch === '"') {
        if (line[i + 1] === '"') {
          cur += '"';
          i++;
        } else inQ = false;
      } else cur += ch;
    } else {
      if (ch === '"') inQ = true;
      else if (ch === ",") {
        out.push(cur);
        cur = "";
      } else cur += ch;
    }
  }
  out.push(cur);
  return out;
}

export function round(x: number, dp = 6): number {
  const f = Math.pow(10, dp);
  return Math.round(x * f) / f;
}
