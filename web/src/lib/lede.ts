/** Facts and guarded claims for the homepage lede.
 *
 * The rule this module exists to enforce: no superlative is ever written into
 * markup. Every claim is computed from the archive and gated behind a guard,
 * so a sentence can only appear on the page in a week where it is true.
 *
 * Two scoping rules keep the claims defensible:
 *
 *  - Superlatives are scoped to OUR record, which starts 2003. The long-baseline
 *    claim (1948 onward) belongs to NASA and is already carried by the percentile
 *    itself; restating it as our own finding overstates what we can show.
 *  - The cross-region average is used only to rank weeks against each other. It
 *    is a mean of percentiles, not itself a percentile, so it is never printed.
 */

import { consecutiveWeeksAtOrBelow, type Region, type Timeseries } from "./data";

export const STREAK_THRESHOLD = 5;
const D4 = 2;

export interface LedeFacts {
  latestWeek: string;
  recordStart: string;
  recordYears: number;
  totalRegions: number;
  regionsAtOrBelow: (percentile: number) => number;
  /** Rank of the latest week against the same ISO week in every other year. 1 = driest. */
  weekOfYearRank: { rank: number; of: number };
  longestStreak: { region: Region; weeks: number; threshold: number };
}

function isoWeek(day: string): number {
  const d = new Date(`${day}T00:00:00Z`);
  const thursday = new Date(d);
  thursday.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3);
  const jan4 = new Date(Date.UTC(thursday.getUTCFullYear(), 0, 4));
  jan4.setUTCDate(jan4.getUTCDate() - ((jan4.getUTCDay() + 6) % 7) + 3);
  return 1 + Math.round((thursday.getTime() - jan4.getTime()) / (7 * 86_400_000));
}

/** Cell-weighted mean percentile across regions.
 *
 * Weighted by valid_cells because an unweighted mean would give HU11 Budapest
 * (1 grid cell) the same influence as RO21 Nord-Est (69). Used for ranking
 * weeks only — see the module note.
 */
function weightedMean(ts: Timeseries, week: string): number | null {
  let weighted = 0;
  let cells = 0;
  for (const region of ts.regions) {
    const w = region.weeks[week];
    if (!w || typeof w.mean_percentile !== "number" || !w.valid_cells) continue;
    weighted += w.mean_percentile * w.valid_cells;
    cells += w.valid_cells;
  }
  return cells > 0 ? weighted / cells : null;
}

/** `asOf` defaults to the newest week. Passing an earlier one lets the claim
 * guards be exercised against weeks where a superlative actually holds. */
export function ledeFacts(ts: Timeseries, asOf?: string): LedeFacts {
  const latestWeek = asOf ?? ts.weeks[ts.weeks.length - 1];
  const recordStart = ts.weeks[0];
  const recordYears = Math.floor(
    (Date.parse(latestWeek) - Date.parse(recordStart)) / (365.25 * 86_400_000)
  );

  // Everything is computed as-of `latestWeek`, so a historical asOf yields the
  // facts as they stood then rather than peeking at later weeks.
  const weeks = ts.weeks.filter((w) => w <= latestWeek);

  const current = weightedMean(ts, latestWeek);
  const targetWeek = isoWeek(latestWeek);
  const sameWeekOfYear = weeks
    .filter((w) => isoWeek(w) === targetWeek)
    .map((w) => weightedMean(ts, w))
    .filter((v): v is number => v !== null);
  const drier = current === null ? 0 : sameWeekOfYear.filter((v) => v < current).length;

  const longest = ts.regions.reduce((best, r) =>
    consecutiveWeeksAtOrBelow(r, weeks, STREAK_THRESHOLD) >
    consecutiveWeeksAtOrBelow(best, weeks, STREAK_THRESHOLD)
      ? r
      : best
  );

  return {
    latestWeek,
    recordStart,
    recordYears,
    totalRegions: ts.regions.length,
    regionsAtOrBelow: (percentile) =>
      ts.regions.filter((r) => {
        const p = r.weeks[latestWeek]?.mean_percentile;
        return typeof p === "number" && p <= percentile;
      }).length,
    weekOfYearRank: { rank: drier + 1, of: sameWeekOfYear.length },
    longestStreak: {
      region: longest,
      weeks: consecutiveWeeksAtOrBelow(longest, weeks, STREAK_THRESHOLD),
      threshold: STREAK_THRESHOLD,
    },
  };
}

/** What the data supports, with no wording attached.
 *
 * The claim is chosen here and phrased in src/i18n. Keeping the two apart means
 * adding a language cannot quietly change what the site asserts — a translator
 * picks words, never which superlative is allowed to appear.
 */
export type Claim =
  | { key: "driest"; years: number }
  | { key: "nthDriest"; rank: number; years: number }
  | { key: "floor"; depleted: number; total: number };

/** Strongest claim first. The last entry has no guard, so there is always a
 * true statement to print — the page never depends on a superlative holding. */
const CLAIMS: { when: (f: LedeFacts) => boolean; claim: (f: LedeFacts) => Claim }[] = [
  {
    when: (f) => f.weekOfYearRank.rank === 1,
    claim: (f) => ({ key: "driest", years: f.recordYears }),
  },
  {
    when: (f) => f.weekOfYearRank.rank <= 3,
    claim: (f) => ({ key: "nthDriest", rank: f.weekOfYearRank.rank, years: f.recordYears }),
  },
  {
    when: () => true,
    claim: (f) => ({ key: "floor", depleted: f.regionsAtOrBelow(D4), total: f.totalRegions }),
  },
];

export function ledeClaim(facts: LedeFacts): Claim {
  return CLAIMS.find((c) => c.when(facts))!.claim(facts);
}
