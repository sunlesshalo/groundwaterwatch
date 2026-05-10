"""Fetch and cache Eurostat NUTS-2 boundaries for Romania and Hungary.

Source: Eurostat GISCO at 1:1M scale, CRS WGS84 (EPSG:4326), 2021 release.
Free, public, no auth.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import requests

NUTS_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
    "NUTS_RG_01M_2021_4326.geojson"
)
TARGET_COUNTRIES = ("RO", "HU")
TARGET_LEVEL = 2


def fetch_raw(cache_path: Path) -> Path:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path
    r = requests.get(NUTS_URL, timeout=120)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    return cache_path


def load_ro_hu_nuts2(cache_dir: Path) -> gpd.GeoDataFrame:
    raw = fetch_raw(cache_dir / "NUTS_RG_01M_2021_4326.geojson")
    gdf = gpd.read_file(raw)
    mask = gdf["CNTR_CODE"].isin(TARGET_COUNTRIES) & (gdf["LEVL_CODE"] == TARGET_LEVEL)
    out = gdf.loc[mask, ["NUTS_ID", "CNTR_CODE", "NAME_LATN", "geometry"]].copy()
    out = out.sort_values("NUTS_ID").reset_index(drop=True)
    return out
