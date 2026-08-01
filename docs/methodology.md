# Methodology

## Data source

We ingest the NASA GRACE-FO Data Assimilation drought-indicator product `GRACEDADM_CLSM025GL_7D V3.0`, distributed by GES DISC and mirrored at nasagrace.unl.edu.

The product is generated at NASA Goddard Space Flight Center by assimilating GRACE/GRACE-FO terrestrial water storage observations into the Catchment Land Surface Model (CLSM), forced by ECMWF meteorological data.

## Variables we use

- **Groundwater Percentile** — the headline metric. Where current groundwater storage falls relative to the same week-of-year across the 1948–2014 baseline. 0 = driest ever observed; 100 = wettest.

> **On the baseline period.** NASA's own materials cite two different figures, so
> to be explicit: **1948–2014 is correct for V3.0**, the version we ingest. The
> GES DISC catalogue entry for `GRACEDADM_CLSM025GL_7D` V3.0 states percentiles
> give "the probability of occurrence within the period of record from 1948 to
> 2014", as does the NASA GRACE-DA-DM entry in the AWS Registry of Open Data.
> drought.gov still says "1948-2012 for global data"; that describes an earlier
> release, whose climatology came from a CLSM run forced by the Princeton
> meteorological dataset (which ends in 2012). V3.0 is forced by ECMWF data
> instead — see the forcing note above. Do not quote 1948–2012 for this product,
> and note the baseline is ~66 years, not 75.
>
> **But the map on the homepage is baselined 1948–2012, and says so.** The
> current-week map we mirror is the operational global run (Europe cut), and its
> own footer reads "Wetness percentiles are relative to the period 1948-2012".
> That is the older baseline described in the paragraph above. So the homepage
> carries both figures: 1948–2012 rendered into the map image, 1948–2014 behind
> the NUTS-2 numbers. This is not an inconsistency we introduced — they are two
> NASA products on two release lines, and neither one is ours to restate. Read
> the map as the current picture and the regional series as the archive-grade
> record. Do not difference a map colour against a NUTS-2 value and expect them
> to agree to the percentile point.
- Root-zone soil moisture and surface soil moisture percentiles are available and may be added later.

## Spatial resolution

- Native: 0.25° × 0.25° grid (~25 km per cell)
- Romania: ~380 cells
- Hungary: ~150 cells
- We aggregate to **NUTS-2 regions** (8 in each country). Each NUTS-2 polygon contains 20–50 cells, enough for stable area-weighted statistics.
- We do not report below NUTS-2 because the source data does not support it.

## Temporal resolution

- Weekly, Monday-timestamped
- Operational latency: 2–9 days
- Final-archive latency: 3–6 months
- Coverage: February 2003 → present

## Aggregation

For each NUTS-2 region and each week:

1. Clip the global percentile raster to the region polygon (Eurostat NUTS GeoJSON, 1:1M scale).
2. Compute area-weighted mean of the cell percentiles inside the polygon.
3. Compute the share of polygon area in the bottom percentile bands (commonly D1–D4 thresholds: ≤30, ≤20, ≤10, ≤5, ≤2).
4. Persist the result as one row in the region's time-series JSON.

Country-level scores are area-weighted aggregates of the constituent NUTS-2 regions.

## What this measures

The percentile compares the current state to the same week across the 1948–2014 baseline. A value of 2 means: in only 2% of historical weeks at this time of year was groundwater this depleted or worse.

## What this does not measure

- Individual well levels. The product is a modeled aquifer-storage anomaly, not a well registry.
- Drinking-water quality or salinity.
- Surface-water (rivers, lakes). Those have separate products.
- Sub-NUTS-2 detail. Do not interpret a single 25 km cell as authoritative for any specific location within it.

## Updates

The pipeline runs weekly. When a region crosses a threshold (e.g. enters the bottom 5%), it is logged as a state change for press notifications.
