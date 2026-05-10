import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_DATA = path.resolve(__dirname, "../../../data");

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

let cached: Timeseries | null = null;

export function loadTimeseries(): Timeseries {
  if (cached) return cached;
  const raw = fs.readFileSync(path.join(REPO_DATA, "timeseries.json"), "utf8");
  cached = JSON.parse(raw) as Timeseries;
  return cached;
}

export function regionsForCountry(country: "RO" | "HU"): Region[] {
  return loadTimeseries().regions.filter((r) => r.country === country);
}

export function latestWeek(): string {
  const ts = loadTimeseries();
  return ts.weeks[ts.weeks.length - 1];
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
