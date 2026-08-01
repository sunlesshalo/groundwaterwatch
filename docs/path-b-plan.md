# Reducing current-state latency

**Status: measured 2026-08-01. The original plan's premise was wrong, and its
proposed shortcut turned out to be unusable. Read the verdict before planning
work here.**

The problem this document exists to solve: the NUTS-2 numbers come from the GES
DISC final archive, which runs 3-6 months behind. The archive currently ends
2026-05-25 while the operational map on the same page shows 2026-07-27. The
regional figures are therefore always a season stale.

## What changed

The original plan assumed the only way to get current numeric values was to
recompute percentiles ourselves from the `GLDAS_CLSM025_DA1_D_EP.2.2` daily
Early Product — requiring a ~50 GB, ~24,000-file baseline backfill and an
empirical-CDF implementation.

That is not the only way. UNL publishes the operational percentile **grid**
alongside the rendered PNGs:

```
https://nasagrace.unl.edu/globaldata/<YYYYMMDD>/gws_perc_025deg_GL_<YYYYMMDD>.tif
```

Float32, 1440x600, WGS84, 0.25 degree, nodata -999, values 0-100, weekly stamps
back to 2003-02-03. It is on the identical grid to the archive NetCDF — verified
by tags (`ModelPixelScale` 0.25, `ModelTiepoint` (0,0) -> (-180, 90)) and
confirmed empirically: per-region `valid_cells` counts match the archive exactly
(HU11 = 1 cell, HU12 = 13, and so on).

`pipeline/operational.py` ingests it and runs it through the same
`pipeline.zonal.aggregate` the archive uses, so the two are directly comparable.
No Earthdata credentials, no baseline backfill, no CDF implementation. What the
original plan budgeted 1-2 days for is a single HTTP GET.

## The verdict: usable as a separate series, NOT as an extension of the archive

The operational product is baselined **1948-2012**; GRACEDADM V3.0 is baselined
**1948-2014**. The operational stream is also produced in near-real time and is
not reprocessed end-to-end the way the archive is. We measured the size of the
resulting disagreement rather than assuming it.

Run `uv run python -m pipeline.verify_operational` to reproduce.

### Measured, 2026-08-01

768 region-weeks: the 26 most recent archive weeks plus one week per year back
to 2003. Units are NUTS-2 mean percentile points — the number readers see.

| Sample | median abs diff | p90 | max | bias |
|---|---|---|---|---|
| All 768 region-weeks | **1.44** | 7.05 | 24.50 | +0.23 |
| Join point (26 weeks from 2025-12-01) | 0.14 | 5.35 | 17.38 | +1.28 |

The original plan set the tolerance at **< 1 percentile point** for the
aggregated NUTS-2 mean. The overall median is 1.44 and the p90 is 7.05. It fails
its own bar, and not narrowly.

Worst individual region-weeks:

```
2024-01-01  RO22  operational=40.53  archive=16.03  d=+24.50
2022-01-03  RO22  operational=47.52  archive=27.07  d=+20.46
2024-01-01  HU21  operational=55.07  archive=34.80  d=+20.26
2026-03-02  RO41  operational=24.86  archive= 7.48  d=+17.38
```

A reader being told a region sits at the 40th percentile when the archive says
the 16th is not a rounding disagreement. It is a different story.

### Two findings that matter more than the headline number

**1. The disagreement is seasonal, not a constant offset.** Sampling only early
January (as the first pass did) suggested the bias flipped sign around 2020.
Re-sampling early July shows that was an artifact of the season, not the year —
in July the operational product reads *wetter* than the archive in every year
from 2003 to 2024, by +0.9 to +10.6 points, while pre-2020 Januaries run
*drier* by 1 to 5.6 points. Different baseline periods produce different
day-of-year climatologies, which is exactly what a seasonally structured
difference looks like.

This is disqualifying for splicing specifically. The trend chart's whole purpose
is a 52-week rolling mean that removes seasonal swing, and the heatmap is
explicitly year x month. Appending operational weeks would inject a seasonal
artifact into the two views built to be free of it.

**2. Present agreement is an illusion of saturation.** The join-point median
looks excellent at 0.14 points — but only because RO and HU are currently pinned
near percentile 0 by the ongoing drought, where two products *cannot* disagree
much. The p90 of 5.35 and max of 17.38 in that same window are the regions not
pinned to the floor. Splice today and it would look seamless; the error would
appear later, when conditions normalise, in a series already published and
quoted. That is the worst possible time to discover it.

## What to do instead

Keep two clearly labelled series:

- **Archive series** (V3.0, 1948-2014) — the multi-year trend, the heatmap, the
  region tables, the computed lede. Authoritative, 3-6 months behind.
- **Operational current week** (1948-2012) — the map, and optionally a numeric
  current-week readout from `pipeline/operational.py`. Current, coarser
  provenance, never differenced against the archive.

`docs/methodology.md` and the public methodology page already state that these
are two products on two baselines and should not be expected to agree to the
percentile point. That note is load-bearing — do not remove it.

### Not yet wired into the site

`pipeline/operational.py` computes the numbers but nothing renders them. That is
deliberate: a current-week numeric readout needs new user-facing copy in EN, RO
and HU, and the RO/HU translations are still awaiting a native read. Adding more
unreviewed translated strings ahead of that review would enlarge the blocker.
Wire it up after the copy review, not before.

## If archive-consistent current numbers are genuinely needed

Then the original Path B is still the only route, because the requirement is
specifically *percentiles on the 1948-2014 baseline for a week the archive has
not published yet*. The operational grid cannot supply that at any latency,
since it is computed against a different baseline. That means the full job:
download `GLDAS_CLSM025_DA1_D.2.2` for the baseline span, build per-cell
day-of-year empirical CDFs, map EP dailies through them, 7-day rolling mean.

Before starting it, re-read the verification section above and set the
acceptance bar in advance. The lesson from this round is that a plausible
shortcut can agree beautifully in the current regime and still be wrong.

## Known source defects

Isolated cells fall outside the valid 0-100 percentile range. Confirmed case:
`gws_perc_025deg_GL_20250707.tif` has exactly one cell at -46.721
(36.875N, 108.125E, central China), with neighbours reading 1.5-3.1.
`open_operational_grid` drops such cells and warns, but raises if more than 100
cells or 0.1% are out of range — an isolated defect on another continent should
not cost a Romanian data point, while systemic corruption must stop the run.

## Out of scope

- Real-time (sub-day) updates. GRACE-FO's mission cadence is ~weekly at best.
- Sub-NUTS-2 detail. The native 0.25 degree grid does not support it regardless
  of which product we ingest.
