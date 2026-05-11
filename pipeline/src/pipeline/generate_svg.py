"""Pre-project RO+HU NUTS-2 polygons to SVG paths for server-rendered maps.

Output: data/svg-ro-hu.json
  {
    "viewBox": "x y w h",
    "bbox": [west, south, east, north],
    "paths": { "RO11": "M ... Z", ... }
  }

We use a simple equirectangular projection. For the RO+HU lat range (~44-49 N)
the visual distortion is negligible; switching to Albers later is a one-file
change if we ever want pixel-perfect cartographic accuracy.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon

from pipeline.boundaries import load_ro_hu_nuts2

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_OUT = REPO_ROOT / "data" / "svg-ro-hu.json"
BOUNDARIES_CACHE = REPO_ROOT / "pipeline" / "data" / "boundaries"

VIEWBOX_PADDING_DEG = 0.3
TARGET_WIDTH = 1000


def project_polygon(poly: Polygon, west: float, north: float, scale: float, lon_scale: float) -> str:
    parts = []
    for ring_idx, ring in enumerate([poly.exterior, *poly.interiors]):
        coords = list(ring.coords)
        pts = [f"{(x - west) * lon_scale * scale:.2f},{(north - y) * scale:.2f}" for x, y in coords]
        cmd_letter = "M" if ring_idx == 0 else "M"
        parts.append(f"{cmd_letter}{pts[0]} L{' L'.join(pts[1:])} Z")
    return " ".join(parts)


def project_geometry(geom, west: float, north: float, scale: float, lon_scale: float) -> str:
    if isinstance(geom, Polygon):
        return project_polygon(geom, west, north, scale, lon_scale)
    if isinstance(geom, MultiPolygon):
        return " ".join(project_polygon(p, west, north, scale, lon_scale) for p in geom.geoms)
    raise TypeError(f"Unsupported geometry type: {type(geom)}")


def compute_view(bounds, target_width=TARGET_WIDTH, padding=VIEWBOX_PADDING_DEG):
    """Equirectangular projection with cos(lat) longitude correction so the
    map preserves visual proportions at the mid-latitude standard parallel.
    Sufficient for RO+HU (~5-degree N-S extent). Switch to Albers if/when
    we expand beyond ~10 degrees of latitude.
    """
    minx, miny, maxx, maxy = bounds
    west = minx - padding
    east = maxx + padding
    south = miny - padding
    north = maxy + padding
    mid_lat = (south + north) / 2
    lon_scale = math.cos(math.radians(mid_lat))
    width_units = (east - west) * lon_scale
    scale = target_width / width_units
    height = (north - south) * scale
    return {
        "viewBox": f"0 0 {target_width:.0f} {height:.0f}",
        "bbox": [west, south, east, north],
        "west": west,
        "north": north,
        "scale": scale,
        "lon_scale": lon_scale,
    }


def project_set(gdf, view):
    paths = {}
    centroids = {}
    for _, row in gdf.iterrows():
        nuts_id = row["NUTS_ID"]
        paths[nuts_id] = project_geometry(
            row["geometry"], view["west"], view["north"], view["scale"], view["lon_scale"]
        )
        c = row["geometry"].representative_point()
        centroids[nuts_id] = {
            "x": round((c.x - view["west"]) * view["lon_scale"] * view["scale"], 1),
            "y": round((view["north"] - c.y) * view["scale"], 1),
        }
    return paths, centroids


def main():
    gdf = load_ro_hu_nuts2(BOUNDARIES_CACHE)

    combined_view = compute_view(gdf.total_bounds)
    combined_paths, combined_centroids = project_set(gdf, combined_view)

    countries = {}
    for code in ("RO", "HU"):
        sub = gdf[gdf["CNTR_CODE"] == code]
        view = compute_view(sub.total_bounds)
        paths, centroids = project_set(sub, view)
        countries[code] = {
            "viewBox": view["viewBox"],
            "bbox": view["bbox"],
            "paths": paths,
            "centroids": centroids,
        }

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.write_text(json.dumps({
        "viewBox": combined_view["viewBox"],
        "bbox": combined_view["bbox"],
        "paths": combined_paths,
        "centroids": combined_centroids,
        "countries": countries,
    }, indent=2))
    print(f"[ok] wrote {DATA_OUT.relative_to(REPO_ROOT)} ({len(combined_paths)} regions combined, plus RO + HU per-country views)")


if __name__ == "__main__":
    main()
