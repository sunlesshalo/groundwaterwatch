# Path B: Compute our own percentiles from the EP daily product

This is the v2 upgrade plan. v1 ships under Path C (UNL PNG mirror for current
state + GES DISC final archive for the multi-year trend). Path B reduces
current-state latency from ~6 days (UNL PNGs) to ~10–18 days (Early Product
NetCDF) and gives us raw numeric values for the current week instead of just
an image.

## What we'd compute

For each day in `GLDAS_CLSM025_DA1_D_EP.2.2`, the file contains daily
groundwater storage (mm) at 0.25° resolution. To match NASA's GRACEDADM
convention we need:

1. A **historical baseline** — the daily groundwater-storage record across a
   reference period (NASA uses 1948–2014). We'd download
   `GLDAS_CLSM025_DA1_D.2.2` for that span (~24,000 daily files,
   ~50 GB raw — manageable as a one-time backfill).
2. For each (cell, day-of-year), the empirical CDF of values across the
   baseline years.
3. Each new daily EP value mapped to its percentile against the matching
   day-of-year CDF.
4. A 7-day rolling mean of percentiles — matching how GRACEDADM aggregates
   to weekly.

## Verification

We must not ship Path B without confirming our computed percentiles match
NASA's published ones. Method:

- For every Monday in the overlap window where both products exist
  (Feb 2003 → 2026-01-26), compute our percentile from EP and compare to
  GRACEDADM's `gws_inst`.
- Per-cell agreement target: median absolute difference < 2 percentile
  points across RO + HU.
- Aggregated NUTS-2 mean: < 1 percentile point absolute difference.
- If we miss those tolerances, ship Path C only and write up the mismatch
  publicly so we don't pretend to a precision we don't have.

## Risks

- **Baseline storage cost.** ~50 GB compressed. Hetzner CX22 has 80 GB SSD;
  fine. If we ever expand beyond RO+HU we'd need a bigger box or to
  pre-aggregate the baseline to per-cell CDF only (~2 GB).
- **Methodology divergence.** NASA's CLSM model has been re-run/reprocessed
  multiple times. The DA1_D historical files use whatever model version was
  current at processing time, while GRACEDADM uses RL06 GRACE data
  re-assimilated end-to-end. There may be a non-trivial gap that the
  verification step uncovers.
- **Effort.** 1–2 days of focused work for the pipeline + 1 day of
  verification. Not v1 critical-path.

## When to do this

After the v1 launch lands press attention. If atlatszo.hu / G4Media / PressOne
embed our widget, the dashboard becomes load-bearing and the 6-day UNL
latency starts to feel slow. That's the trigger.

## Out of scope

- Real-time (sub-day) updates. The underlying GRACE-FO mission cadence is
  ~weekly at best; daily means daily, not hourly.
- Sub-NUTS-2 detail. The native 0.25° grid does not support it regardless
  of which product we ingest.
