"""Render the Open Graph share card as a 1200x630 PNG.

A link posted to Facebook or Bluesky is mostly its card, and the card is usually
seen at thumbnail size — so the design leads with one large number and the map,
not prose that would be illegible at 300px wide.

Everything on the card is read from the archive. Nothing here is hardcoded
editorial, for the same reason the homepage lede is computed: a card is shared
and cached far from the page it came from, so a stale claim on one outlives any
correction made later.

Requires `rsvg-convert` (librsvg). Usage:
    uv run python -m pipeline.share_card --out ../web/public/og --prune
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from html import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"

WIDTH, HEIGHT = 1200, 630
D4 = 2  # percentile threshold for "exceptional" on the US Drought Monitor scale

PAPER = "#f7f4ec"
INK = "#0c1a14"
INK_SOFT = "#4a5953"
LINE = "#d4cdba"
MAP_BG = "#efe9db"
NO_DATA = "#e7e1d3"

# Mirrors severityBand()/bandColor() in web/src/lib/data.ts.
BANDS = [(2, "#6e1f1f"), (5, "#b04a2c"), (10, "#d28f3a"), (20, "#e0c068"), (30, "#a8aa6c")]
NORMAL = "#6a8e6f"

# rsvg picks the first family present, so this renders the same on a macOS
# laptop and an ubuntu runner.
FONT = "DejaVu Sans, Helvetica Neue, Helvetica, Arial, sans-serif"


def band_color(pct: float | None) -> str:
    if pct is None:
        return NO_DATA
    for threshold, color in BANDS:
        if pct <= threshold:
            return color
    return NORMAL


def build_svg(timeseries: dict, mapdata: dict) -> tuple[str, str]:
    week = timeseries["weeks"][-1]
    regions = timeseries["regions"]
    total = len(regions)
    depleted = sum(
        1
        for r in regions
        if isinstance(r["weeks"].get(week, {}).get("mean_percentile"), (int, float))
        and r["weeks"][week]["mean_percentile"] <= D4
    )

    # Map occupies the right half. Source viewBox is 1000x565.
    scale = 0.60
    map_x, map_y = 556, (HEIGHT - 565 * scale) / 2

    shapes = []
    for r in regions:
        path = mapdata["paths"].get(r["nuts_id"])
        if not path:
            continue
        pct = r["weeks"].get(week, {}).get("mean_percentile")
        shapes.append(
            f'<path d="{path}" fill="{band_color(pct)}" stroke="#ffffff" stroke-width="1.4"/>'
        )

    pretty_week = datetime.strptime(week, "%Y-%m-%d").strftime("%-d %B %Y")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>
  <rect x="{map_x - 24}" y="0" width="{WIDTH - map_x + 24}" height="{HEIGHT}" fill="{MAP_BG}"/>
  <rect x="0" y="{HEIGHT - 10}" width="{WIDTH}" height="10" fill="#6e1f1f"/>

  <!-- Every line is wrapped by hand: SVG <text> does not reflow, and the text
       column has to stay left of the map panel, which starts at map_x - 24.
       Do not re-join these lines without re-measuring the rendered width. -->
  <g font-family="{escape(FONT)}">
    <text x="72" y="96" font-size="23" font-weight="700" letter-spacing="3.4" fill="{INK_SOFT}">GROUNDWATERWATCH</text>

    <text x="72" y="236" font-size="118" font-weight="700" fill="#6e1f1f">{depleted} of {total}</text>
    <text x="72" y="292" font-size="35" font-weight="600" fill="{INK}">NUTS-2 regions in Romania</text>
    <text x="72" y="338" font-size="35" font-weight="600" fill="{INK}">and Hungary sit at or below</text>
    <text x="72" y="384" font-size="35" font-weight="600" fill="{INK}">the 2nd percentile</text>

    <text x="72" y="438" font-size="24" fill="{INK_SOFT}">of NASA&#8217;s 1948&#8211;2014</text>
    <text x="72" y="470" font-size="24" fill="{INK_SOFT}">groundwater baseline.</text>

    <line x1="72" y1="500" x2="496" y2="500" stroke="{LINE}" stroke-width="2"/>
    <text x="72" y="538" font-size="23" fill="{INK_SOFT}">Week of {escape(pretty_week)}</text>
    <text x="72" y="572" font-size="23" fill="{INK_SOFT}">NASA GRACE-FO data assimilation</text>
  </g>

  <g transform="translate({map_x}, {map_y:.1f}) scale({scale})">
    {"".join(shapes)}
  </g>
</svg>
"""
    return svg, week


def render(svg: str, png_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["rsvg-convert", "-w", str(WIDTH), "-h", str(HEIGHT), "-o", str(png_path)],
            input=svg.encode("utf-8"),
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            "rsvg-convert not found. macOS: brew install librsvg. "
            "Debian/Ubuntu: apt-get install -y librsvg2-bin"
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"rsvg-convert failed: {e.stderr.decode('utf-8', 'replace')}")


def prune_other_cards(out_dir: Path, keep: str) -> list[str]:
    removed = []
    for child in sorted(out_dir.glob("*.png")):
        if child.stem == keep:
            continue
        try:
            datetime.strptime(child.stem, "%Y-%m-%d")
        except ValueError:
            continue
        child.unlink()
        removed.append(child.stem)
    return removed


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=REPO_ROOT / "web" / "public" / "og")
    p.add_argument("--prune", action="store_true", help="drop cards for older weeks")
    return p.parse_args()


def main():
    args = parse_args()
    timeseries = json.loads((DATA_DIR / "timeseries.json").read_text())
    mapdata = json.loads((DATA_DIR / "svg-ro-hu.json").read_text())

    out_dir = args.out.resolve()
    svg, week = build_svg(timeseries, mapdata)
    png = out_dir / f"{week}.png"
    render(svg, png)
    shown = png.relative_to(REPO_ROOT) if png.is_relative_to(REPO_ROOT) else png
    print(f"[ok] wrote {shown} ({png.stat().st_size / 1024:.1f} KB)")

    if args.prune:
        for name in prune_other_cards(out_dir, week):
            print(f"[ok] pruned old card {name}")


if __name__ == "__main__":
    main()
