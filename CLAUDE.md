# groundwaterwatch — working notes

Public-facing data dashboard for European groundwater depletion. Awareness project, not a commercial product. Built to be press-credible (Átlátszó, Telex, G4Media, PressOne) and embed-friendly.

## Hard constraints (read before changing anything)

- **Resolution floor is NUTS-2.** GRACE-DA native resolution is 0.25° ≈ 25 km. Romania ~380 cells, Hungary ~150 cells. NUTS-3 (județe / megyék) is too small to be defensible. Do not promise it.
- **The data shows aquifer storage anomalies, not individual wells.** Never frame the product as "your well" or "empty wells." That overpromises and invites expert pushback.
- **Percentiles are pre-computed in the source product.** We aggregate; we do not recompute the baseline.
- **Latency is 2–9 days operational, 3–6 months for the final archive.** Updates are weekly (Monday-stamped), not real-time.

## Data product

`GRACEDADM_CLSM025GL_7D V3.0` — NASA GES DISC.
- Variables: `Groundwater Percentile`, `Root Zone Soil Moisture Percentile`, `Surface Soil Moisture Percentile`
- Format: NetCDF (also HDF, ASCII, KMZ)
- Access: free NASA Earthdata login required; OPeNDAP and direct HTTP both supported
- License: NASA public domain
- Mirror: `nasagrace.unl.edu` (operational feed)

## Architecture (target)

1. **Ingest** — weekly cron pulls latest `.nc4` from GES DISC, retains last ~1200 weeks
2. **Process** — clip to RO+HU bbox; zonal stats via `rasterstats` against NUTS-0/NUTS-2 GeoJSON from Eurostat
3. **Store** — flat JSON time series per region (~20 regions × 1200 weeks ≈ 24k rows; no DB needed)
4. **Frontend** — static site, MapLibre GL choropleth + week scrubber + per-country page with sparkline + share-card OG image generator
5. **Embed widget** — `<iframe>` per country for press partners
6. **Hosting** — Hetzner CX22 + Cloudflare; cron on the same box

Stack: Astro (static) for frontend, Python (xarray + regionmask) for ingest.

## v1 scope

- Languages: EN (default, unprefixed) + RO + HU. Methodology page is EN-only for now — its hydrology vocabulary is where a translation slip costs the most credibility.
- Countries: RO + HU
- Domain: groundwaterwatch.eu (purchase pending)
- GitHub: sunlesshalo/groundwaterwatch (public since 2026-08-01)

## Open decisions

- [x] Frontend framework — Astro, static output
- [x] Hosting — GitHub Pages (project site at /groundwaterwatch/), deployed by
      .github/workflows/deploy.yml. Hetzner was never provisioned and is not
      needed: the site is fully static. BASE_PATH/SITE_URL make a move to a
      root-served host or a custom domain a config change, not a code change.
- [ ] Press partner outreach plan and timing relative to launch

## What this project is not

- Not an agent. No Claude API calls, no agentic loops.
- Not a service users log into. Static site, public data.
- Not real-time. Weekly cadence is the source's cadence.
- Not sub-NUTS-2. Don't add features that imply finer resolution than the data supports.
