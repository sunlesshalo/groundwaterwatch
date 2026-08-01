"""Measure how far UNL's operational grid sits from the GES DISC V3.0 archive.

The two products cover the same cells for the same weeks but are baselined
differently — operational against 1948-2012, GRACEDADM V3.0 against 1948-2014.
Before either splicing them into one series or presenting them side by side, we
need the size of that disagreement in the units readers actually see: the NUTS-2
mean percentile.

Method: for each sampled week where both exist, aggregate the operational grid
through the *same* pipeline.zonal.aggregate the archive goes through, then diff
per region against data/timeseries.json.

    uv run python -m pipeline.verify_operational
    uv run python -m pipeline.verify_operational --recent 26 --annual

Reports median / p90 / max absolute difference and the signed bias, split by
recent weeks (the join point, where splicing would happen) and by year (drift).
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

import numpy as np

from pipeline.boundaries import load_ro_hu_nuts2
from pipeline.operational import DATA_DIR, fetch_tif, open_operational_grid
from pipeline.zonal import aggregate

REPO_ROOT = Path(__file__).resolve().parents[3]
TIMESERIES = REPO_ROOT / "data" / "timeseries.json"


def load_archive() -> tuple[list[str], dict[str, dict[str, float]]]:
    ts = json.loads(TIMESERIES.read_text())
    by_region = {
        r["nuts_id"]: {
            week: w["mean_percentile"]
            for week, w in r["weeks"].items()
            if isinstance(w.get("mean_percentile"), (int, float))
        }
        for r in ts["regions"]
    }
    return ts["weeks"], by_region


def sample_weeks(weeks: list[str], recent: int, annual: bool) -> list[str]:
    """Recent weeks (dense, at the join) plus one per earlier year (drift)."""
    picked = list(weeks[-recent:]) if recent else []
    if annual:
        seen = {w[:4] for w in picked}
        for w in weeks:
            if w[:4] not in seen:
                picked.append(w)
                seen.add(w[:4])
    return sorted(set(picked))


def describe(diffs: list[float]) -> str:
    a = np.abs(np.array(diffs))
    s = np.array(diffs)
    return (
        f"n={a.size:4d}  median|d|={np.median(a):6.3f}  p90|d|={np.percentile(a, 90):6.3f}  "
        f"max|d|={a.max():6.3f}  bias={s.mean():+6.3f}"
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recent", type=int, default=26, help="most recent archive weeks to test")
    p.add_argument("--annual", action="store_true", default=True)
    p.add_argument("--cache", type=Path, default=DATA_DIR / "operational")
    args = p.parse_args()

    weeks, archive = load_archive()
    targets = sample_weeks(weeks, args.recent, args.annual)
    print(f"[ok] archive covers {weeks[0]} .. {weeks[-1]} ({len(weeks)} weeks)")
    print(f"[ok] testing {len(targets)} weeks against the operational grid\n")

    regions = load_ro_hu_nuts2(DATA_DIR / "boundaries")
    ids = regions["NUTS_ID"].tolist()

    rows: list[tuple[str, str, float, float]] = []
    for i, week in enumerate(targets, 1):
        d = datetime.strptime(week, "%Y-%m-%d").date()
        try:
            da = open_operational_grid(fetch_tif(d, args.cache))
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  [{i:3d}/{len(targets)}] {week}  SKIP ({type(exc).__name__}: {exc})")
            continue
        stats = aggregate(da, regions, ids)
        n = 0
        for nid in ids:
            op = stats[nid]["mean_percentile"]
            ar = archive.get(nid, {}).get(week)
            if op is None or ar is None:
                continue
            rows.append((week, nid, float(op), float(ar)))
            n += 1
        print(f"  [{i:3d}/{len(targets)}] {week}  {n} regions")

    if not rows:
        raise SystemExit("no overlapping observations")

    diffs = [op - ar for _, _, op, ar in rows]
    print(f"\n=== all sampled region-weeks ===\n{describe(diffs)}")

    recent_cut = weeks[-args.recent] if args.recent else weeks[0]
    recent = [op - ar for w, _, op, ar in rows if w >= recent_cut]
    if recent:
        print(f"\n=== join point (weeks >= {recent_cut}) ===\n{describe(recent)}")

    print("\n=== by year ===")
    years = sorted({w[:4] for w, _, _, _ in rows})
    for y in years:
        d = [op - ar for w, _, op, ar in rows if w[:4] == y]
        print(f"  {y}  {describe(d)}")

    print("\n=== worst single region-weeks ===")
    worst = sorted(rows, key=lambda r: -abs(r[2] - r[3]))[:8]
    for w, nid, op, ar in worst:
        print(f"  {w}  {nid:5s}  operational={op:7.3f}  archive={ar:7.3f}  d={op - ar:+7.3f}")


if __name__ == "__main__":
    main()
