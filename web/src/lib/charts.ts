/** Series preparation for the trend line and the month grid.
 *
 * Both aggregate across regions with the same cell weighting the lede uses:
 * an unweighted mean would let HU11 Budapest (1 grid cell) count as much as
 * RO21 Nord-Est (69). See src/lib/lede.ts.
 */

import type { Region, Timeseries } from "./data";

export type Series = (number | null)[];

function weightedMean(regions: Region[], week: string): number | null {
  let weighted = 0;
  let cells = 0;
  for (const region of regions) {
    const w = region.weeks[week];
    if (!w || typeof w.mean_percentile !== "number" || !w.valid_cells) continue;
    weighted += w.mean_percentile * w.valid_cells;
    cells += w.valid_cells;
  }
  return cells > 0 ? weighted / cells : null;
}

export function weeklySeries(ts: Timeseries, country?: "RO" | "HU"): Series {
  const regions = country ? ts.regions.filter((r) => r.country === country) : ts.regions;
  return ts.weeks.map((w) => weightedMean(regions, w));
}

/** Trailing rolling mean: each point is the average of the `window` weeks up to
 * and including it. A raw weekly line is dominated by seasonal swing, and the
 * question "has it changed over the years" is a question about the trend.
 *
 * Trailing rather than centred on purpose. A centred window cannot be computed
 * for the most recent half-window, so the line would stop months short of the
 * archive and its end label would read as current while lagging by a season —
 * beside a headline about the latest week, that is a contradiction the reader
 * cannot see. Trailing ends exactly at the newest week and means something a
 * reader can state out loud: the average of the last year. The cost is the
 * first `window` weeks have no line, which is honest and visible. */
export function rollingMean(values: Series, window: number): Series {
  return values.map((_, i) => {
    if (i < window - 1) return null;
    let sum = 0;
    let n = 0;
    for (let j = i - window + 1; j <= i; j++) {
      const v = values[j];
      if (typeof v === "number") {
        sum += v;
        n++;
      }
    }
    return n >= window * 0.8 ? sum / n : null;
  });
}

export interface MonthGrid {
  years: number[];
  /** [yearIndex][month 0-11] — mean score, or null where no week fell in it. */
  cells: (number | null)[][];
}

export function monthGrid(ts: Timeseries, country?: "RO" | "HU"): MonthGrid {
  const weekly = weeklySeries(ts, country);
  const acc = new Map<number, { sum: number; n: number }[]>();

  ts.weeks.forEach((week, i) => {
    const v = weekly[i];
    if (typeof v !== "number") return;
    const year = Number(week.slice(0, 4));
    const month = Number(week.slice(5, 7)) - 1;
    if (!acc.has(year)) acc.set(year, Array.from({ length: 12 }, () => ({ sum: 0, n: 0 })));
    const row = acc.get(year)!;
    row[month].sum += v;
    row[month].n++;
  });

  const years = [...acc.keys()].sort((a, b) => a - b);
  return {
    years,
    cells: years.map((y) => acc.get(y)!.map((m) => (m.n > 0 ? m.sum / m.n : null))),
  };
}

/** Ticks at clean year boundaries, thinned so labels never collide. */
export function yearTicks(weeks: string[], maxTicks = 8): { index: number; year: number }[] {
  const firsts: { index: number; year: number }[] = [];
  let seen = -1;
  weeks.forEach((w, i) => {
    const y = Number(w.slice(0, 4));
    if (y !== seen) {
      firsts.push({ index: i, year: y });
      seen = y;
    }
  });
  const step = Math.ceil(firsts.length / maxTicks);
  return firsts.filter((_, i) => i % step === 0);
}
