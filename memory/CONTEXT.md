# CONTEXT — groundwaterwatch

## 2026-06-05 — Scaffold
Base session-protocol commands + memory added via scaffold_agent.sh.

# Session Log

## 2026-08-01 — Launch: data catch-up, automation, i18n, charts

Went from a stale local repo to a live public site in one session.
**Live: https://sunlesshalo.github.io/groundwaterwatch/**

- **Completed:**
  - Backfilled 17 weeks; archive now 2003-02-03 → 2026-05-25 (1217 weeks × 16
    regions). GES DISC cutoff currently ~9 weeks back. UNL operational map
    refreshed to 2026-07-27.
  - Fixed the pipeline's packaging so the documented `uv run python -m
    pipeline.run` works (was `package = false`, needed a manual PYTHONPATH).
  - Homepage lede is now computed from the archive behind guarded claim
    templates, not hardcoded. The old text had gone false — it claimed "driest
    ever at this time of year" when the week ranked 5th of 24.
  - Settled the baseline period at **1948–2014** (V3.0). Removed "75-year",
    wrong under either candidate. Reasoning recorded in docs/methodology.md.
  - Two scheduled workflows (daily UNL mirror, weekly archive) + a Pages deploy.
    Cadences follow measured publication behaviour, not round numbers.
  - Repo made public; GitHub Pages project site with BASE_PATH support.
  - Generated OG share card + absolute social metadata.
  - Plain-language rewrite + EN/RO/HU. English at root, `/ro/`, `/hu/`.
  - Visitor-controlled playback of all 1217 weeks, with a speed control.
  - Trend line (trailing 52-week mean) and a year × month heatmap.

- **Verified:**
  - Clean build, 10 routes, **zero broken internal links**; all 13 live URLs 200.
  - Every pipeline command runs as documented with PYTHONPATH unset; a full
    no-op run leaves data byte-identical (the property daily cron depends on).
  - Mirror workflow ran green in CI and correctly made no commit.
  - Deploy workflow green across several runs.
  - Chart values cross-checked against `timeseries.json` independently
    (heatmap May 2026 = 5.4 both ways; trend endpoints 5.9/1.3 → 6/1).
  - Charts rasterised and visually inspected for collisions and overflow.
  - Playback timing simulated at 60 Hz and 120 Hz across all four speeds.
  - Freshness guard fails correctly when simulated forward to 2026-11-01.

- **Blockers:**
  - **`EARTHDATA_USER` / `EARTHDATA_PASS` secrets are not set.** The archive
    workflow runs Mondays 06:43 UTC and will fail until they are. It has
    therefore **never run** — it is the one untested workflow.
  - RO/HU translations are machine-authored and want a native read before this
    is pitched to an editor.
  - Interactive playback (click/drag) was never exercised in a real browser —
    no browser automation was available. Logic and markup are verified; DOM
    event wiring is not.

- **Next:** set the two secrets (before Monday), native-review the translations,
  open the site on a phone to check playback and the 12-column heatmap.

### Landmines worth remembering

- `data/weekly_*.json` are gitignored (one is grandfathered in). A fresh
  checkout has almost none, so `backfill` resumes from `timeseries.json` and
  `compile_timeseries()` **merges** rather than rebuilds. Reverting either
  would have CI silently overwrite the 1217-week archive with ~18 weeks.
- Pushes made with `GITHUB_TOKEN` do not trigger other workflows, so both data
  workflows call the deploy explicitly. Without that the site freezes while the
  data keeps updating.
- GitHub disables scheduled workflows after 60 days of repo inactivity.
  Unconfirmed whether the bot's own commits reset that timer.
