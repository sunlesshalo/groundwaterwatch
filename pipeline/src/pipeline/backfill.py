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


def load_existing_timeseries() -> dict:
    path = OUT_DIR / "timeseries.json"
    if not path.exists():
        return {"weeks": [], "regions": []}
    return json.loads(path.read_text())


def latest_existing_weekly() -> date | None:
    """Newest week we already hold, from the weekly files *or* the compiled series.

    The weekly files are gitignored, so a fresh checkout has almost none of them
    while timeseries.json carries the full history. Resuming from the weekly
    files alone would re-download everything back to the oldest gap on every run.
    """
    candidates = []
    files = sorted(OUT_DIR.glob("weekly_*.json"))
    if files:
        name = files[-1].stem  # "weekly_YYYY-MM-DD"
        candidates.append(datetime.strptime(name.split("_", 1)[1], "%Y-%m-%d").date())
    weeks = load_existing_timeseries().get("weeks") or []
    if weeks:
        candidates.append(datetime.strptime(weeks[-1], "%Y-%m-%d").date())
    return max(candidates) if candidates else None


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    p.add_argument("--since-last-weekly", action="store_true")
    p.add_argument("--sleep", type=float, default=SLEEP_BETWEEN)
    return p.parse_args()


def compile_timeseries():
    """Merge every weekly_*.json into timeseries.json for the frontend.

    Merges rather than rebuilds: the weekly files are gitignored, so anywhere
    but a full local checkout — CI especially — a rebuild-from-disk would
    discard the committed history and leave only the weeks this run happened to
    download. Existing weeks are overwritten by newer weekly files, so a
    reprocessed week still wins.
    """
    existing = load_existing_timeseries()
    by_region: dict[str, dict] = {r["nuts_id"]: r for r in existing.get("regions", [])}
    weeks_index: list[str] = list(existing.get("weeks", []))
    for path in sorted(OUT_DIR.glob("weekly_*.json")):
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
        # Deduped: a week can arrive from both the existing series and a
        # weekly file. The per-region overwrite above already let the weekly
        # file win; this just keeps the index itself unique and ordered.
        "weeks": sorted(set(weeks_index)),
        "regions": list(by_region.values()),
    }
    target = OUT_DIR / "timeseries.json"
    target.write_text(json.dumps(out, indent=2, separators=(",", ":")))
    print(f"[ok] compiled timeseries.json: {len(out['weeks'])} weeks x {len(by_region)} regions")


def main():
    args = parse_args()
    known = latest_existing_weekly() if args.since_last_weekly else None
    start = args.start or (known + timedelta(days=7) if known else START_DEFAULT)
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
