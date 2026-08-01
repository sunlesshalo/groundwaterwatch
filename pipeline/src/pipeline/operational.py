"""Read UNL's operational percentile GeoTIFF and aggregate it to NUTS-2.

This is the numeric counterpart to `unl_mirror`, which only mirrors a rendered
PNG. UNL publishes the operational grid itself alongside the pictures:

    https://nasagrace.unl.edu/globaldata/<YYYYMMDD>/gws_perc_025deg_GL_<YYYYMMDD>.tif

Float32, 1440x600, WGS84, 0.25 degree, nodata -999, values 0-100. Verified from
the file's own tags: ModelPixelScale (0.25, 0.25), ModelTiepoint mapping raster
(0,0) to (-180, 90) as the upper-left *corner*. Weekly stamps go back to
2003-02-03, the same start as the GES DISC archive.

**Why this exists.** The GES DISC final archive runs 3-6 months behind, so the
NUTS-2 series stops months short of the operational map on the same page. This
module computes the same statistics from the operational grid, so the current
week can be reported numerically and not just as a picture.

**It does not extend the archive series, and must not.** The operational product
is baselined 1948-2012; GRACEDADM V3.0 is baselined 1948-2014. Appending one to
the other would splice two baselines into a single line and silently change what
the trend chart means at its most-read end. See docs/path-b-plan.md for the
measured size of that disagreement. Keep the two series separate and labelled.

No credentials needed: unlike GES DISC, this host is public.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

import numpy as np
import requests
import xarray as xr
from PIL import Image

from pipeline.boundaries import load_ro_hu_nuts2
from pipeline.zonal import aggregate

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "pipeline" / "data"

TIF_URL = (
    "https://nasagrace.unl.edu/globaldata/{stamp}/gws_perc_025deg_GL_{stamp}.tif"
)
NODATA = -999.0

# The archive NetCDF grid, which we must match exactly for the two products to
# be comparable cell for cell. Read off GRACEDADM_CLSM025GL_7D.A20260525.030.nc4:
# ascending, cell centres, 0.25 deg.
LAT = np.arange(-59.875, 90.0, 0.25)
LON = np.arange(-179.875, 180.0, 0.25)


def tif_url(week: date) -> str:
    return TIF_URL.format(stamp=week.strftime("%Y%m%d"))


def fetch_tif(week: date, cache_dir: Path) -> Path:
    """Download the operational grid for `week`, caching by filename."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"gws_perc_025deg_GL_{week.strftime('%Y%m%d')}.tif"
    if path.exists() and path.stat().st_size > 0:
        return path
    r = requests.get(tif_url(week), timeout=120)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path


def open_operational_grid(path: Path) -> xr.DataArray:
    """Load the GeoTIFF as a DataArray on the archive's lat/lon grid.

    The raster is stored north-to-south; the archive NetCDF is south-to-north.
    We flip rather than reindex so no interpolation is involved — the two grids
    are the same cells in a different row order.
    """
    with Image.open(path) as im:
        arr = np.array(im, dtype="float64")
    if arr.shape != (LAT.size, LON.size):
        raise ValueError(f"unexpected grid {arr.shape}, expected {(LAT.size, LON.size)}")
    arr = arr[::-1, :]
    arr[arr == NODATA] = np.nan

    # Percentiles are 0-100 by definition. The operational product does contain
    # isolated cells outside that range — 2025-07-07 has exactly one, -46.721 at
    # 36.875N 108.125E in central China, surrounded by neighbours reading 1.5-3.1.
    # Drop such cells rather than reject the week: one bad cell on another
    # continent should not cost us a Romanian data point. But a *large* count
    # means the product changed shape under us, and aggregating it would be
    # meaningless, so that still raises.
    bad = np.isfinite(arr) & ((arr < 0) | (arr > 100))
    n_bad = int(bad.sum())
    if n_bad:
        n_valid = int(np.isfinite(arr).sum())
        share = n_bad / n_valid
        if n_bad > 100 or share > 0.001:
            raise ValueError(
                f"{n_bad} cells ({share:.3%}) outside 0-100 — product likely changed; "
                f"range {np.nanmin(arr)}..{np.nanmax(arr)}"
            )
        print(f"  [warn] {path.name}: dropped {n_bad} cell(s) outside 0-100")
        arr[bad] = np.nan

    return xr.DataArray(arr, coords={"lat": LAT, "lon": LON}, dims=("lat", "lon"))


def stats_for_week(week: date, cache_dir: Path | None = None) -> dict:
    """NUTS-2 statistics for one operational week, same shape as pipeline.run."""
    cache_dir = cache_dir or (DATA_DIR / "operational")
    da = open_operational_grid(fetch_tif(week, cache_dir))
    regions = load_ro_hu_nuts2(DATA_DIR / "boundaries")
    stats = aggregate(da, regions, regions["NUTS_ID"].tolist())
    return {
        "week_start": week.isoformat(),
        "source": "nasagrace.unl.edu operational grid",
        "source_url": tif_url(week),
        "baseline": "1948-2012",
        "regions": [
            {
                "nuts_id": nid,
                "country": regions.loc[regions["NUTS_ID"] == nid, "CNTR_CODE"].iloc[0],
                "name": regions.loc[regions["NUTS_ID"] == nid, "NAME_LATN"].iloc[0],
                **stats[nid],
            }
            for nid in regions["NUTS_ID"]
        ],
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--date",
        required=True,
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        help="Monday of the week to aggregate",
    )
    p.add_argument("--out", type=Path, default=None, help="write JSON here")
    return p.parse_args()


def main():
    args = parse_args()
    if args.date.weekday() != 0:
        raise SystemExit(f"--date must be a Monday; got {args.date} ({args.date:%A})")
    payload = stats_for_week(args.date)
    text = json.dumps(payload, indent=2)
    if args.out:
        args.out.write_text(text)
        print(f"[ok] wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
