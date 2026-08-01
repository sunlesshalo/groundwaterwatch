import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_DATA = path.resolve(__dirname, "../../../data");
const PUBLIC_DIR = path.resolve(__dirname, "../../public");

export interface RegionWeek {
  mean_percentile: number | null;
  valid_cells: number;
  bands: {
    d4_exceptional: number | null;
    d3_extreme: number | null;
    d2_severe: number | null;
    d1_moderate: number | null;
    d0_abnormally_dry: number | null;
  };
}

export interface Region {
  nuts_id: string;
  country: string;
  name: string;
  weeks: Record<string, RegionWeek>;
}

export interface Timeseries {
  weeks: string[];
  regions: Region[];
}

export interface MapView {
  viewBox: string;
  bbox: [number, number, number, number];
  paths: Record<string, string>;
  centroids: Record<string, { x: number; y: number }>;
}

export interface MapData extends MapView {
  countries: Record<"RO" | "HU", MapView>;
}

export function loadMap(): MapData {
  const raw = fs.readFileSync(path.join(REPO_DATA, "svg-ro-hu.json"), "utf8");
  return JSON.parse(raw) as MapData;
}

export function loadTimeseries(): Timeseries {
  const raw = fs.readFileSync(path.join(REPO_DATA, "timeseries.json"), "utf8");
  return JSON.parse(raw) as Timeseries;
}

/** Prefix a site-absolute path with Astro's configured base.
 *
 * Astro rewrites asset URLs it generates itself, but not paths written by hand
 * in markup or built by our own helpers. Without this, every link 404s on a
 * GitHub Pages project site, which serves from /<repo>/ rather than the root.
 */
export function withBase(pathname: string): string {
  const base = import.meta.env.BASE_URL || "/";
  return `${base.replace(/\/$/, "")}${pathname}`;
}

export type UnlLayer = "gws" | "rtzsm" | "sfsm";

export interface UnlLatest {
  week_start: string;
  fetched_at: string;
  source: string;
  /** Partial: the weekly job mirrors only the layers the site renders. */
  layers: Partial<Record<UnlLayer, string>>;
}

export function loadUnlLatest(): UnlLatest {
  const raw = fs.readFileSync(path.join(REPO_DATA, "unl-latest.json"), "utf8");
  return JSON.parse(raw) as UnlLatest;
}

/** Site-relative href for a mirrored UNL layer. Throws if unl-latest.json names
 * a week we never mirrored — a failed build beats a broken image on a page the
 * press is quoting. */
export function unlLayerHref(week: string, layer: UnlLayer = "gws"): string {
  const file = path.join(PUBLIC_DIR, "maps", week, `${layer}.png`);
  if (!fs.existsSync(file)) {
    throw new Error(
      `unl-latest.json points at week ${week}, but maps/${week}/${layer}.png is not mirrored. ` +
        `Run: cd pipeline && uv run python -m pipeline.unl_mirror --out ../web/public/maps`
    );
  }
  return withBase(`/maps/${week}/${layer}.png`);
}

/** Site-relative href for the share card of the newest week.
 *
 * Versioned by week and guarded the same way as the UNL map: a card is cached
 * by every platform it is shared to, so shipping one that disagrees with the
 * page is worse than failing the build. Regenerate with
 * `uv run python -m pipeline.share_card --out ../web/public/og --prune`.
 */
export function ogImageHref(): string {
  const week = latestWeek();
  const file = path.join(PUBLIC_DIR, "og", `${week}.png`);
  if (!fs.existsSync(file)) {
    throw new Error(
      `no share card for the newest week (${week}); og/${week}.png is missing. ` +
        `Run: cd pipeline && uv run python -m pipeline.share_card --out ../web/public/og --prune`
    );
  }
  return withBase(`/og/${week}.png`);
}

export function regionsForCountry(country: "RO" | "HU"): Region[] {
  return loadTimeseries().regions.filter((r) => r.country === country);
}

export function latestWeek(): string {
  const ts = loadTimeseries();
  return ts.weeks[ts.weeks.length - 1];
}

export function bandColor(band: string): string {
  return {
    d4: "#6e1f1f",
    d3: "#b04a2c",
    d2: "#d28f3a",
    d1: "#e0c068",
    d0: "#a8aa6c",
    normal: "#6a8e6f",
  }[band] || "#cccccc";
}

export function severityBand(p: number | null): "d4" | "d3" | "d2" | "d1" | "d0" | "normal" {
  if (p === null) return "normal";
  if (p <= 2) return "d4";
  if (p <= 5) return "d3";
  if (p <= 10) return "d2";
  if (p <= 20) return "d1";
  if (p <= 30) return "d0";
  return "normal";
}

export function bandLabel(band: string): string {
  return {
    d4: "D4 exceptional",
    d3: "D3 extreme",
    d2: "D2 severe",
    d1: "D1 moderate",
    d0: "D0 abnormally dry",
    normal: "near normal",
  }[band] || band;
}

export function lastNValues(region: Region, weeks: string[], n: number): number[] {
  const slice = weeks.slice(-n);
  return slice
    .map((w) => region.weeks[w]?.mean_percentile)
    .filter((v): v is number => typeof v === "number");
}

export function consecutiveWeeksAtOrBelow(region: Region, weeks: string[], threshold: number): number {
  let count = 0;
  for (let i = weeks.length - 1; i >= 0; i--) {
    const v = region.weeks[weeks[i]]?.mean_percentile;
    if (typeof v === "number" && v <= threshold) {
      count++;
    } else {
      break;
    }
  }
  return count;
}
