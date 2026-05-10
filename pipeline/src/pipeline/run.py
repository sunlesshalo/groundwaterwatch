"""End-to-end: download one week of GRACE-DA, compute NUTS-2 zonal stats, emit JSON.

Usage:
    uv run python -m pipeline.run                       # latest archive Monday
    uv run python -m pipeline.run --date 2026-01-26     # specific Monday
    uv run python -m pipeline.run --inspect             # print NetCDF metadata only

Requires:
    - ~/.netrc with `machine urs.earthdata.nasa.gov login <uid> password <pw>` (chmod 600)
    - NASA Earthdata account with "NASA GESDISC DATA ARCHIVE" application authorized
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import xarray as xr

from pipeline.boundaries import load_ro_hu_nuts2
from pipeline.download import download
from pipeline.zonal import aggregate, open_grace_nc, pick_groundwater_var

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "pipeline" / "data"
OUT_DIR = REPO_ROOT / "data"


def latest_archive_monday(today: date | None = None) -> date:
    """Best-effort latest week available in the GES DISC final archive.

    Final archive lags 3-6 months, so we ask for ~14 weeks back from the most
    recent Monday. The download will 404 if it isn't published yet; the caller
    can step back week by week.
    """
    today = today or date.today()
    monday = today - timedelta(days=today.weekday() + 14 * 7)
    return monday


def run(week_start: date, inspect_only: bool = False) -> Path | None:
    nc_path = download(week_start, DATA_DIR)
    print(f"[ok] downloaded {nc_path.name} ({nc_path.stat().st_size / 1024:.1f} KB)")

    with open_grace_nc(nc_path) as ds:
        if inspect_only:
            print("\n--- variables ---")
            for name, var in ds.data_vars.items():
                print(f"  {name}: dims={var.dims} long_name={var.attrs.get('long_name', '?')}")
            print("\n--- coords ---")
            for name, var in ds.coords.items():
                print(f"  {name}: shape={var.shape}")
            return None

        gw_var = pick_groundwater_var(ds)
        print(f"[ok] groundwater variable: {gw_var}")
        da = ds[gw_var]
        # Many GES DISC products have a length-1 time dim; squeeze it.
        if "time" in da.dims and da.sizes["time"] == 1:
            da = da.isel(time=0)

        regions = load_ro_hu_nuts2(DATA_DIR / "boundaries")
        print(f"[ok] loaded {len(regions)} NUTS-2 regions ({regions['CNTR_CODE'].value_counts().to_dict()})")

        stats = aggregate(da, regions, regions["NUTS_ID"].tolist())

    payload = {
        "week_start": week_start.isoformat(),
        "source_file": nc_path.name,
        "variable": gw_var,
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"weekly_{week_start.isoformat()}.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"[ok] wrote {out.relative_to(REPO_ROOT)}")
    return out


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--inspect", action="store_true", help="Print NetCDF metadata and exit")
    return p.parse_args()


def main():
    args = parse_args()
    week = args.date or latest_archive_monday()
    if week.weekday() != 0:
        raise SystemExit(f"--date must be a Monday; got {week} ({week.strftime('%A')})")
    run(week, inspect_only=args.inspect)


if __name__ == "__main__":
    main()
