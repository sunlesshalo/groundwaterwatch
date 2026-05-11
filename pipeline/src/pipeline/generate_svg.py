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
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon

from pipeline.boundaries import load_ro_hu_nuts2

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_OUT = REPO_ROOT / "data" / "svg-ro-hu.json"
BOUNDARIES_CACHE = REPO_ROOT / "pipeline" / "data" / "boundaries"

VIEWBOX_PADDING_DEG = 0.3
TARGET_WIDTH = 1000


def project_polygon(poly: Polygon, west: float, north: float, scale: float) -> str:
    parts = []
    for ring_idx, ring in enumerate([poly.exterior, *poly.interiors]):
        coords = list(ring.coords)
        pts = [f"{(x - west) * scale:.2f},{(north - y) * scale:.2f}" for x, y in coords]
        cmd_letter = "M" if ring_idx == 0 else "M"
        parts.append(f"{cmd_letter}{pts[0]} L{' L'.join(pts[1:])} Z")
    return " ".join(parts)


def project_geometry(geom, west: float, north: float, scale: float) -> str:
    if isinstance(geom, Polygon):
        return project_polygon(geom, west, north, scale)
    if isinstance(geom, MultiPolygon):
        return " ".join(project_polygon(p, west, north, scale) for p in geom.geoms)
    raise TypeError(f"Unsupported geometry type: {type(geom)}")


def main():
    gdf = load_ro_hu_nuts2(BOUNDARIES_CACHE)
    minx, miny, maxx, maxy = gdf.total_bounds
    west = minx - VIEWBOX_PADDING_DEG
    east = maxx + VIEWBOX_PADDING_DEG
    south = miny - VIEWBOX_PADDING_DEG
    north = maxy + VIEWBOX_PADDING_DEG
    scale = TARGET_WIDTH / (east - west)
    height = (north - south) * scale
    view_box = f"0 0 {TARGET_WIDTH:.0f} {height:.0f}"

    paths = {}
    centroids = {}
    for _, row in gdf.iterrows():
        nuts_id = row["NUTS_ID"]
        paths[nuts_id] = project_geometry(row["geometry"], west, north, scale)
        c = row["geometry"].representative_point()
        centroids[nuts_id] = {
            "x": round((c.x - west) * scale, 1),
            "y": round((north - c.y) * scale, 1),
        }

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.write_text(json.dumps({
        "viewBox": view_box,
        "bbox": [west, south, east, north],
        "paths": paths,
        "centroids": centroids,
    }, indent=2))
    print(f"[ok] wrote {DATA_OUT.relative_to(REPO_ROOT)} ({len(paths)} regions, viewBox={view_box})")


if __name__ == "__main__":
    main()
