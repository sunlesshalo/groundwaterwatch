"""Mirror NASA's operational weekly percentile maps from UNL.

UNL/National Drought Mitigation Center publishes the operational GRACE-DA
percentile maps with ~2-9 day latency. URL pattern:
  https://nasagrace.unl.edu/data/Web/GRACE_GWS_<YYYYMMDD>.png    (groundwater)
  https://nasagrace.unl.edu/data/Web/GRACE_RTZSM_<YYYYMMDD>.png  (root-zone)
  https://nasagrace.unl.edu/data/Web/GRACE_SFSM_<YYYYMMDD>.png   (surface)

Files are Monday-stamped. We probe back from the most recent Monday until we
get a 200, then mirror the three layers + write a manifest.

This is the Path C approach: show NASA's official current map alongside our
own archive-derived NUTS-2 trend chart. Path B (compute our own percentiles
from the EP daily product) is the v2 upgrade documented in docs/path-b-plan.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

UNL_BASE = "https://nasagrace.unl.edu/data/Web"
LAYERS = {
    "gws": "GRACE_GWS_{stamp}.png",
    "rtzsm": "GRACE_RTZSM_{stamp}.png",
    "sfsm": "GRACE_SFSM_{stamp}.png",
}
LAYER_NAMES = {
    "gws": "Groundwater storage percentile",
    "rtzsm": "Root-zone soil moisture percentile",
    "sfsm": "Surface soil moisture percentile",
}


def probe_latest(today: date | None = None, max_lookback_weeks: int = 12) -> date:
    today = today or date.today()
    monday = today - timedelta(days=today.weekday())
    for weeks_back in range(max_lookback_weeks):
        candidate = monday - timedelta(weeks=weeks_back)
        url = f"{UNL_BASE}/{LAYERS['gws'].format(stamp=candidate.strftime('%Y%m%d'))}"
        r = requests.head(url, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return candidate
    raise RuntimeError(f"No UNL map found in the {max_lookback_weeks} weeks before {monday}")


def prune_other_weeks(out_dir: Path, keep: date) -> list[str]:
    """Drop mirrored week directories other than `keep`.

    The site only ever renders the latest week, and these PNGs are regenerable
    from UNL, so retaining older ones just grows the repo. Only touches
    directories whose name parses as a date, so an unrelated sibling directory
    is never removed.
    """
    removed = []
    for child in sorted(out_dir.iterdir()):
        if not child.is_dir() or child.name == keep.isoformat():
            continue
        try:
            datetime.strptime(child.name, "%Y-%m-%d")
        except ValueError:
            continue
        shutil.rmtree(child)
        removed.append(child.name)
    return removed


def resolve_layers(layers: Sequence[str] | None) -> list[str]:
    selected = list(layers) if layers else list(LAYERS)
    unknown = [k for k in selected if k not in LAYERS]
    if unknown:
        raise SystemExit(f"unknown layer(s): {', '.join(unknown)}; choose from {', '.join(LAYERS)}")
    return selected


def is_current(pointer_path: Path, out_dir: Path, week: date, layers: Sequence[str]) -> bool:
    """True when the pointer already names `week` and every selected layer is on disk.

    Lets the daily job be a no-op on the six days out of seven when UNL has not
    published anything new, instead of re-downloading and rewriting the pointer's
    `fetched_at` — which would commit a no-change diff every single day.
    """
    if not pointer_path.exists():
        return False
    try:
        pointer = json.loads(pointer_path.read_text())
    except json.JSONDecodeError:
        return False
    if pointer.get("week_start") != week.isoformat():
        return False
    week_dir = out_dir / week.isoformat()
    return all((week_dir / f"{key}.png").exists() for key in layers)


def mirror(week_start: date, out_dir: Path, layers: Sequence[str] | None = None) -> dict:
    selected = resolve_layers(layers)

    week_dir = out_dir / week_start.isoformat()
    week_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"week_start": week_start.isoformat(), "layers": {}}
    for key in selected:
        fmt = LAYERS[key]
        url = f"{UNL_BASE}/{fmt.format(stamp=week_start.strftime('%Y%m%d'))}"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out = week_dir / f"{key}.png"
        out.write_bytes(r.content)
        manifest["layers"][key] = {
            "name": LAYER_NAMES[key],
            "url": url,
            "file": out.name,
            "bytes": len(r.content),
            "sha256": hashlib.sha256(r.content).hexdigest(),
        }
    # Drop layers left behind by an earlier run with a wider --layers, so the
    # directory always matches its manifest.
    kept = {info["file"] for info in manifest["layers"].values()}
    for stale in week_dir.glob("*.png"):
        if stale.name not in kept:
            stale.unlink()

    (week_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--out", type=Path, default=None)
    p.add_argument(
        "--layers",
        type=lambda s: [x.strip() for x in s.split(",") if x.strip()],
        default=None,
        help=f"comma-separated subset of {', '.join(LAYERS)} (default: all)",
    )
    p.add_argument(
        "--prune",
        action="store_true",
        help="remove previously mirrored weeks from --out, keeping only this one",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="re-download even when the pointer already names the latest week",
    )
    return p.parse_args()


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    out_dir = args.out or (repo_root / "pipeline" / "data" / "unl")
    pointer_path = repo_root / "data" / "unl-latest.json"
    selected = resolve_layers(args.layers)
    week = args.date or probe_latest()

    if not args.force and is_current(pointer_path, out_dir, week, selected):
        print(f"[skip] already current for week {week.isoformat()}; nothing to do")
        return

    print(f"[ok] mirroring UNL maps for week {week.isoformat()}")
    manifest = mirror(week, out_dir, selected)
    for key, info in manifest["layers"].items():
        print(f"  {key}: {info['file']} ({info['bytes'] / 1024:.1f} KB)")

    if args.prune:
        # Only after a fully successful mirror, so a failed run never leaves
        # the out dir empty.
        for name in prune_other_weeks(out_dir, week):
            print(f"[ok] pruned old week {name}")

    # Write a top-level pointer so the frontend can find the latest week.
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text(json.dumps({
        "week_start": week.isoformat(),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "nasagrace.unl.edu",
        "layers": {k: v["url"] for k, v in manifest["layers"].items()},
    }, indent=2))
    print(f"[ok] wrote {pointer_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
