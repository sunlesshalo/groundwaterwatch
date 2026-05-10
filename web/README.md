# web

Astro static site. Multi-page (home, RO, HU, methodology) with a MapLibre
GL choropleth as a client-side island. Builds to `dist/`.

## Run

```sh
cd web
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # static output in dist/
npm run preview  # serve dist/
```

## Pages (v1)

- `/` — home, framing
- `/ro/` — Romania, 8 NUTS-2 regions
- `/hu/` — Hungary, 8 NUTS-2 regions
- `/methodology/` — methodology, sources, what we don't measure

## Data inputs (TBD wiring)

- `/data/unl-latest.json` — pointer to current week's UNL maps (Path C)
- `/data/timeseries.json` — multi-region multi-week trend data (compiled
  from `pipeline/src/pipeline/backfill.py`)
- `/data/weekly_<YYYY-MM-DD>.json` — individual weekly snapshots (compiled
  by `pipeline/src/pipeline/run.py`)

## What's not here yet

- The choropleth (MapLibre GL with NUTS-2 GeoJSON)
- The week scrubber
- The per-region trend sparkline
- OG share-card generator
- Embed widget for press partners

These wire up after the archive backfill produces `timeseries.json`.
