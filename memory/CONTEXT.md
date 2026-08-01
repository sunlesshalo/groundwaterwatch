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

## 2026-08-01 (later) — Secrets set, archive verified, deploy ref bug found

Closed every blocker from the session above except the native translation read.

- **Completed:**
  - `EARTHDATA_USER` / `EARTHDATA_PASS` set as repository secrets, piped from
    the local `~/.netrc` into `gh secret set` via stdin so the values never
    appeared in a command line, shell history, or a transcript.
  - Fixed the deploy workflow to check out `ref: main` (see landmines).
  - Country pages reordered: region table now sits **above** the trend line and
    heatmap, matching the homepage's map → categorisation → charts rhythm.
  - Share card baseline note wrapped onto two lines; it was overrunning the
    text panel by 14px onto the map background.

- **Verified:**
  - **Archive workflow ran green end to end for the first time** (run
    30705952636, 42s). Auth, backfill, freshness, card, build, commit all
    passed. The 1217-week archive came through **byte-identical** — the
    resume-and-merge safety held under a real CI checkout.
  - Deploy fix confirmed by the checkout refspec changing shape: from
    `+<pinned-sha>:refs/remotes/origin/main` to `+refs/heads/main*:…`.
  - Section order checked in the rendered HTML of all six country pages
    (EN/RO/HU × RO/HU) and in DOM element order, then live after deploy.
  - Share card measured by rendering the text layer with the map group
    stripped out, so the map's antialiased edge could not be mistaken for
    glyph ink. All 17 possible values of "N of 16" rendered: widest 508px,
    24px clear of the panel edge at 532.
  - Playback click/drag and the 12-column heatmap confirmed working in a real
    browser by the user — this closes the two long-standing "verified in
    markup but not in a browser" gaps on `timelapse-playback` and `charts`.

- **Blockers:**
  - RO/HU translations are still machine-authored and want a native read
    before this is pitched to an editor. **This is now the only one.**

- **Next:** native-review the RO/HU copy. Then optional: the embed widget,
  the domain, and bumping the GitHub Actions versions (all are behind —
  checkout/setup-node are on v4 against v7 latest, and Node 20 is deprecated
  on the runners). Do the Actions bump as its own change; the Pages actions
  move together and a bad bump breaks publishing.

## 2026-08-01 (third) — The homepage map was the wrong continent

Started from a question about a chart label and turned into a launch-blocking
find.

- **Completed:**
  - **The "NASA's current map" on the homepage was the contiguous United
    States**, in all three locales, directly under the RO/HU charts.
    `unl_mirror` pointed at UNL's `/data/Web/` tree, which is the CONUS
    product. Switched to the EU cut of the global run (see landmines).
  - `is_current()` now also compares the pointer's recorded URLs against the
    URLs today's config would build, so changing the source invalidates the
    cache instead of skipping forever.
  - Methodology (both `docs/methodology.md` and the public page) now states
    that the map and the regional numbers use different baselines.
  - New `pipeline/operational.py`: ingests UNL's operational percentile
    GeoTIFF and runs it through the *same* `zonal.aggregate` as the archive.
  - New `pipeline/verify_operational.py`: measures operational vs archive.
  - `docs/path-b-plan.md` rewritten around the measurements.
  - Trend-chart end label now reads `Románia 6/100` and no longer clips.
  - Checkpoint sweep caught `verify_operational --annual` being inert
    (`store_true` with `default=True` can never be switched off, and the
    docstring advertised it). Replaced with `--no-annual`.

- **Verified:**
  - EU and CONUS feeds publish in lockstep across the 8 weeks to 2026-07-27.
  - The mirrored PNG's sha256 matches the EU download byte-for-byte in `dist`.
  - Grids align exactly: per-region `valid_cells` from the operational GeoTIFF
    match the archive (HU11 = 1, HU12 = 13, …), so the comparison is cell-for-cell.
  - Mirror re-fetched after the source swap, then skipped on the second run.
  - Trend label rasterised and measured: worst case `Magyarország 100/100`
    is 129.3px ending at x=813.3 inside a 820-wide viewBox.
  - **Live after deploy** (run 30710225912): the served map's sha256 matches
    the EU download byte-for-byte, all 10 routes return 200, end labels carry
    `/100` in all three locales, and the methodology page shows both baselines.
  - Checkpoint regression sweep: all 11 pipeline modules import; mirror skips
    on re-run; freshness 0 weeks behind; 10 routes build; `timeseries.json`
    untouched this session (so no operational data leaked into the archive);
    working tree still clean after every command, i.e. the runs really are
    side-effect free.

- **Next:** unchanged — native-review the RO/HU copy. Deliberately did **not**
  wire the operational numbers into the site, because that needs new EN/RO/HU
  copy and would enlarge the very blocker we are trying to close.

### Landmines worth remembering

- **UNL publishes two trees and the obvious one is wrong for us.**
  `/data/Web/` is the 0.125° contiguous-US product. `/globaldata/<YYYYMMDD>/`
  is the 0.25° global run, cut into GLOBAL, EU, AF, AS, AU, NA, SA and INDIA.
  We want `GRACE_GWS_EU_<stamp>.png`. The EU render also carries NASA branding,
  a title, the date and the colour scale, where the CONUS file is a bare map.
- **A cache keyed only on "week + files exist" cannot notice that the source
  changed.** That is why the CONUS map survived: after any swap of
  `UNL_BASE`/`LAYERS` the week still matched and `gws.png` still existed, so
  the daily job would have skipped forever while serving the old imagery.
  `is_current()` now compares recorded URLs too. Any future feed change must
  keep that property or it will silently serve stale data.
- **Never splice the operational series onto the archive series.** They are
  baselined 1948-2012 and 1948-2014 respectively. Measured over 768
  region-weeks: median absolute difference 1.44 percentile points, p90 7.05,
  max 24.5 — against the original plan's own tolerance of < 1. Worse, the
  disagreement is **seasonal** (operational reads wetter every July from 2003
  to 2024, drier in pre-2020 Januaries), which would poison precisely the two
  views built to remove seasonality: the 52-week rolling mean and the
  year × month heatmap.
- **Current agreement between the two products is an illusion of saturation.**
  At the join point the median difference is only 0.14 points — because RO/HU
  are pinned near percentile 0 by the drought, where two products cannot
  disagree. p90 in that same window is 5.35 and max 17.38. A splice would look
  seamless today and break later, once published and quoted.
- The operational GeoTIFF contains isolated out-of-range cells:
  `gws_perc_025deg_GL_20250707.tif` has exactly one at -46.721 (central China).
  `open_operational_grid` drops them and warns, but raises above 100 cells or
  0.1%.
- Chart end labels are 11px `font-weight: 600` over a Georgia stack, and
  Georgia ships **no semibold**, so browsers resolve it to Georgia **Bold** —
  measure with Bold, not Regular. Regular would have said the HU label fit.

- `data/weekly_*.json` are gitignored (one is grandfathered in). A fresh
  checkout has almost none, so `backfill` resumes from `timeseries.json` and
  `compile_timeseries()` **merges** rather than rebuilds. Reverting either
  would have CI silently overwrite the 1217-week archive with ~18 weeks.
- Pushes made with `GITHUB_TOKEN` do not trigger other workflows, so both data
  workflows call the deploy explicitly. Without that the site freezes while the
  data keeps updating.
- **That fixes the trigger but not the ref.** Under `workflow_call`,
  `actions/checkout` defaults to `github.sha` — the SHA that *started* the run,
  which for the data workflows is frozen before the bot pushes its data commit.
  So the deploy built the previous week's tree. `deploy.yml` is now pinned to
  `ref: main`; do not remove it. Caught on run 30705952636: the archive pushed
  `dfaeee2`, the deploy fetched `b5e0433`, and the live share card stayed at
  the pre-commit bytes while `main` had the new ones.
  Still only proven via the refspec shape and a push-triggered deploy — a true
  `workflow_call` end-to-end test needs a run where the bot actually commits,
  which only happens when a new archive week lands.
- The share card is **deterministic per platform, not across platforms.**
  macOS rsvg rendered it at 109516 bytes, the ubuntu runner at 108712 — same
  input, same week. So the first CI run after a local regeneration always
  produces one no-op churn commit. Harmless and self-resolving, but do not read
  it as the data having changed.
- Share card text is hand-wrapped SVG `<text>`; it does not reflow. The text
  column must stay left of the map panel at `map_x - 24` (x=532). Re-measure
  the rendered width before re-joining any line.
- GitHub disables scheduled workflows after 60 days of repo inactivity.
  Unconfirmed whether the bot's own commits reset that timer.
