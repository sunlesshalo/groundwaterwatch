"""Fail loudly when a feed has stopped advancing.

This project has already had the failure this guards against: the pipeline went
unrun from May to August 2026 and nothing announced it — the site simply kept
serving old numbers. The build-time guards in the web app catch a *missing*
map or a pointer with no PNG; neither notices a feed that is merely frozen.

Thresholds are deliberately loose. They are meant to catch "NASA moved a URL
and every fetch now 404s", not to alarm on the normal publication lag, which is
1-7 days for the UNL operational maps and 2-6 months for the GES DISC archive.

Usage:
    uv run python -m pipeline.freshness --unl-max-weeks 3
    uv run python -m pipeline.freshness --archive-max-weeks 26
    uv run python -m pipeline.freshness --unl-max-weeks 3 --archive-max-weeks 26
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"


def weeks_behind(week: str, today: date) -> int:
    return (today - datetime.strptime(week, "%Y-%m-%d").date()).days // 7


def check(label: str, week: str, max_weeks: int, today: date) -> str | None:
    behind = weeks_behind(week, today)
    status = "ok" if behind <= max_weeks else "STALE"
    print(f"[{status}] {label}: newest week {week}, {behind} weeks behind (limit {max_weeks})")
    if behind > max_weeks:
        return f"{label} is {behind} weeks behind, over the {max_weeks}-week limit (newest: {week})"
    return None


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--unl-max-weeks", type=int, default=None)
    p.add_argument("--archive-max-weeks", type=int, default=None)
    p.add_argument(
        "--today",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        default=None,
        help="override today's date (for testing)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    if args.unl_max_weeks is None and args.archive_max_weeks is None:
        raise SystemExit("nothing to check: pass --unl-max-weeks and/or --archive-max-weeks")

    today = args.today or date.today()
    failures = []

    if args.unl_max_weeks is not None:
        pointer = json.loads((DATA_DIR / "unl-latest.json").read_text())
        failures.append(check("UNL map", pointer["week_start"], args.unl_max_weeks, today))

    if args.archive_max_weeks is not None:
        weeks = json.loads((DATA_DIR / "timeseries.json").read_text())["weeks"]
        failures.append(check("GES DISC archive", weeks[-1], args.archive_max_weeks, today))

    real = [f for f in failures if f]
    if real:
        raise SystemExit("[fail] " + "; ".join(real))


if __name__ == "__main__":
    main()
