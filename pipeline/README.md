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
```

Outputs land in `/data/weekly_<YYYY-MM-DD>.json`. Raw `.nc4` files are cached
in `/pipeline/data/` and gitignored.

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
