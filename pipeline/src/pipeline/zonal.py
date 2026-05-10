"""Zonal statistics: area-weighted mean groundwater percentile per NUTS-2 region.

Uses regionmask to rasterize the polygon set against the GRACE 0.25-deg grid,
then computes area-weighted means with cosine-of-latitude weighting (cells near
the equator are wider in m^2 than cells near the poles, but RO/HU sit at
44-49 N so the correction is small but worth applying).
"""

from __future__ import annotations

from typing import Iterable

import geopandas as gpd
import numpy as np
import regionmask
import xarray as xr

# Drought severity thresholds — matches U.S. Drought Monitor convention applied
# to percentile rather than to dollar-loss class. Bottom = driest.
DROUGHT_BANDS = {
    "d4_exceptional": 2,
    "d3_extreme": 5,
    "d2_severe": 10,
    "d1_moderate": 20,
    "d0_abnormally_dry": 30,
}


def open_grace_nc(path) -> xr.Dataset:
    ds = xr.open_dataset(path)
    return ds


def pick_groundwater_var(ds: xr.Dataset) -> str:
    """Find the groundwater-percentile variable by name or long_name."""
    candidates = [
        "gws_inst",
        "gws_perc",
        "groundwater_percentile",
        "GWS_inst_percentile",
    ]
    for name in candidates:
        if name in ds.data_vars:
            return name
    for name, var in ds.data_vars.items():
        ln = str(var.attrs.get("long_name", "")).lower()
        if "groundwater" in ln and "percent" in ln:
            return name
    raise KeyError(
        f"Could not locate groundwater-percentile variable. Available: {list(ds.data_vars)}"
    )


def build_mask(da: xr.DataArray, regions: gpd.GeoDataFrame) -> xr.DataArray:
    rm = regionmask.from_geopandas(
        regions, names="NAME_LATN", abbrevs="NUTS_ID", name="nuts2"
    )
    return rm.mask(da)


def area_weights(da: xr.DataArray) -> xr.DataArray:
    """cos(lat) area weights matching the cell grid."""
    lat_name = "lat" if "lat" in da.coords else "latitude"
    return np.cos(np.deg2rad(da[lat_name]))


def aggregate(
    da: xr.DataArray, regions: gpd.GeoDataFrame, region_ids: Iterable[str]
) -> dict:
    """Return {NUTS_ID: {mean, count, drought_band_share}} for one timestep."""
    mask = build_mask(da, regions)
    weights = area_weights(da)
    result: dict[str, dict] = {}
    for i, nuts_id in enumerate(region_ids):
        sel = da.where(mask == i)
        w = weights.where(mask == i)
        valid = sel.notnull()
        weighted = (sel * w).where(valid).sum().item()
        denom = w.where(valid).sum().item()
        if denom == 0 or np.isnan(denom):
            result[nuts_id] = {
                "mean_percentile": None,
                "valid_cells": 0,
                "bands": {k: None for k in DROUGHT_BANDS},
            }
            continue
        mean_pct = weighted / denom
        bands = {}
        for label, threshold in DROUGHT_BANDS.items():
            in_band = (sel <= threshold) & valid
            band_w = w.where(in_band).sum().item()
            bands[label] = band_w / denom if denom else None
        result[nuts_id] = {
            "mean_percentile": mean_pct,
            "valid_cells": int(valid.sum().item()),
            "bands": bands,
        }
    return result
