"""Backfill weekly archive: download every available Monday from 2003 to the
present final-archive cutoff, run zonal stats, emit one JSON per week.

Resumable: skips weeks whose JSON already exists. Throttled with a small
delay between requests so we don't trigger NASA's rate-limiter.

Usage:
    uv run python -m pipeline.backfill                # full backfill 2003->latest
    uv run python -m pipeline.backfill --start 2024-01-01
    uv run python -m pipeline.backfill --since-last-weekly  # resume from latest weekly_*.json

Output:
    /data/weekly_<YYYY-MM-DD>.json (one per week)
    /data/timeseries.json          (compiled multi-region multi-week, regenerated each run)
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

from pipeline.run import REPO_ROOT, OUT_DIR, run

START_DEFAULT = date(2003, 2, 3)  # First available Monday in archive (Feb 2003 per docs)
SLEEP_BETWEEN = 0.5  # seconds between requests


def all_mondays(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=7)


def latest_existing_weekly() -> date | None:
    files = sorted(OUT_DIR.glob("weekly_*.json"))
    if not files:
        return None
    name = files[-1].stem  # "weekly_YYYY-MM-DD"
    return datetime.strptime(name.split("_", 1)[1], "%Y-%m-%d").date()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--since-last-weekly", action="store_true")
    p.add_argument("--sleep", type=float, default=SLEEP_BETWEEN)
    return p.parse_args()


def compile_timeseries():
    """Walk all weekly_*.json and emit a single timeseries.json for the frontend."""
    weeks = sorted(OUT_DIR.glob("weekly_*.json"))
    by_region: dict[str, dict] = {}
    weeks_index: list[str] = []
    for path in weeks:
        payload = json.loads(path.read_text())
        weeks_index.append(payload["week_start"])
        for r in payload["regions"]:
            nid = r["nuts_id"]
            if nid not in by_region:
                by_region[nid] = {
                    "nuts_id": nid,
                    "country": r["country"],
                    "name": r["name"],
                    "weeks": {},
                }
            by_region[nid]["weeks"][payload["week_start"]] = {
                "mean_percentile": r["mean_percentile"],
                "valid_cells": r["valid_cells"],
                "bands": r["bands"],
            }
    out = {
        "weeks": weeks_index,
        "regions": list(by_region.values()),
    }
    target = OUT_DIR / "timeseries.json"
    target.write_text(json.dumps(out, indent=2, separators=(",", ":")))
    print(f"[ok] compiled timeseries.json: {len(weeks_index)} weeks x {len(by_region)} regions")


def main():
    args = parse_args()
    start = args.start or (latest_existing_weekly() + timedelta(days=7) if args.since_last_weekly and latest_existing_weekly() else START_DEFAULT)
    if start.weekday() != 0:
        start = start + timedelta(days=(7 - start.weekday()) % 7)
    # End: we don't know the latest archive cutoff without probing. Try most recent
    # 30 weeks back from today; the loop will stop on consecutive 404s.
    end = args.end or (date.today() - timedelta(days=date.today().weekday() + 14))

    print(f"[backfill] {start} -> {end}, sleep={args.sleep}s")
    consecutive_404 = 0
    processed = 0
    skipped = 0
    failed = 0

    for week in all_mondays(start, end):
        target = OUT_DIR / f"weekly_{week.isoformat()}.json"
        if target.exists() and target.stat().st_size > 0:
            skipped += 1
            continue
        try:
            run(week)
            processed += 1
            consecutive_404 = 0
            time.sleep(args.sleep)
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status == 404:
                consecutive_404 += 1
                print(f"[skip] {week} not in archive yet (404)")
                if consecutive_404 >= 4:
                    print(f"[stop] {consecutive_404} consecutive 404s; assumed past archive cutoff")
                    break
            else:
                failed += 1
                print(f"[fail] {week}: HTTP {status}")
        except Exception as e:
            failed += 1
            print(f"[fail] {week}: {type(e).__name__}: {e}")

    print(f"[done] processed={processed} skipped={skipped} failed={failed}")
    compile_timeseries()


if __name__ == "__main__":
    main()
