# Verify numbers end-to-end

**Rule:** Any aggregate number a dashboard, report, or API shows must be cross-checked against the raw source at least once before shipping.

## Why

Silent aggregation bugs (double-counting, dedup-off-by-one, timezone shifts, missed field) produce numbers that *look* plausible and pass unit tests. The only reliable catch is: "does the dashboard number equal what I can count myself from the raw data?"

**Evidence (claude-gauge, 2026-04-11):** Dashboard showed `17,174,533` total tokens. 30-second cross-check against raw JSONL with `jq | awk` returned the same number. That step was the only guard between a silent aggregation bug and production.

## How to apply

Before marking a dashboard/report feature `passing`:

1. Pick **one** number the dashboard shows.
2. Compute it independently from the raw source — `jq`, `awk`, `pandas`, SQL, whatever is shortest.
3. Both values must match to the last digit (or the spec must explain the discrepancy, e.g., "dashboard rounds to nearest 1k").
4. Log the cross-check in CONTEXT.md: `verified: dashboard=X, raw=X ✓`.

## When to skip

Never skip for aggregate numbers. For pass-through fields (dashboard shows a single raw value unchanged), sampling 1–2 records is enough.
