# pipeline

Ingests GRACE-DA NetCDF from NASA GES DISC, runs zonal stats against the
RO + HU NUTS-2 polygon set, and emits one JSON file per processed week to
`/data/`.

## One-time setup

### 1. NASA Earthdata account

Register a free account at https://urs.earthdata.nasa.gov/users/new, then log
in to that page and authorize the **NASA GESDISC DATA ARCHIVE** application
under *Applications → Authorized Apps*. Without this step, GES DISC will
return HTTP 401 even with valid credentials.

### 2. ~/.netrc

```
machine urs.earthdata.nasa.gov login <your-uid> password <your-pw>
```

```sh
chmod 600 ~/.netrc
```

### 3. Python env (uv)

```sh
cd pipeline
uv sync
```

## Run

```sh
# latest archive week (auto-picks ~14 weeks back to stay inside the 3-6 month lag)
uv run python -m pipeline.run

# specific Monday
uv run python -m pipeline.run --date 2026-01-26

# inspect NetCDF schema only (no zonal stats)
uv run python -m pipeline.run --date 2026-01-26 --inspect

# catch the archive up from the newest weekly_*.json to the archive cutoff
uv run python -m pipeline.backfill --since-last-weekly
```

Outputs land in `/data/weekly_<YYYY-MM-DD>.json`. Raw `.nc4` files are cached
in `/pipeline/data/` and gitignored. `backfill` also recompiles
`/data/timeseries.json`, which is what the frontend reads.

### UNL operational maps

The homepage shows NASA's official current-week map alongside our archive-derived
figures. The mirror **must** write into the site's public directory — the web
build reads `/data/unl-latest.json` and fails if the week it names has no
mirrored PNG:

```sh
# what the weekly job runs: only the layer the site renders, one week retained
uv run python -m pipeline.unl_mirror --out ../web/public/maps --layers gws --prune

# full archival mirror (all three layers, every week kept) to the gitignored dir
uv run python -m pipeline.unl_mirror
```

The mirror exits early when the pointer already names the newest published
week and its PNGs are on disk, so running it daily costs one HEAD request on
the six days out of seven when UNL has published nothing. Pass `--force` to
re-download anyway.

`--layers gws --prune` is what keeps `web/public/maps/` at ~350 KB instead of
growing ~1 MB a week. The two unused layers are one command away if a
root-zone or surface soil-moisture page is ever built. A mirrored week
directory always matches its `manifest.json`; `--prune` runs only after every
selected layer downloads, so a UNL outage leaves the previous week in place
rather than emptying the directory.

### Share card

Renders the 1200×630 Open Graph card from the newest week's data. Needs
`rsvg-convert` (`brew install librsvg` / `apt-get install -y librsvg2-bin`):

```sh
uv run python -m pipeline.share_card --out ../web/public/og --prune
```

The card is versioned by week and the web build fails if the newest week has no
card, so it cannot silently drift from the page. The archive workflow
regenerates it whenever the archive advances.

### Freshness guard

Fails when a feed has stopped advancing, which otherwise looks identical to a
feed that is merely quiet:

```sh
uv run python -m pipeline.freshness --unl-max-weeks 3
uv run python -m pipeline.freshness --archive-max-weeks 26
```

Thresholds are loose on purpose — they catch "every fetch now 404s", not the
normal 1–7 day (UNL) and 2–6 month (GES DISC) publication lags.

## Output schema

```json
{
  "week_start": "2026-01-26",
  "source_file": "GRACEDADM_CLSM025GL_7D.A20260126.030.nc4",
  "variable": "gws_inst",
  "regions": [
    {
      "nuts_id": "RO11",
      "country": "RO",
      "name": "Nord-Vest",
      "mean_percentile": 12.4,
      "valid_cells": 47,
      "bands": {
        "d4_exceptional": 0.04,
        "d3_extreme": 0.18,
        "d2_severe": 0.62,
        "d1_moderate": 0.91,
        "d0_abnormally_dry": 1.00
      }
    }
  ]
}
```

`mean_percentile` is the cosine-of-latitude-weighted area mean of GRACE-DA
groundwater percentile cells inside the NUTS-2 polygon. `bands` is the share
of valid cells whose percentile is at-or-below the U.S. Drought Monitor
threshold (D4 ≤ 2nd, D3 ≤ 5th, ..., D0 ≤ 30th percentile).
