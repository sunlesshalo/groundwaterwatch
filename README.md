# groundwaterwatch

Europe's hidden drought, mapped weekly.

A public dashboard that tracks groundwater depletion across Europe using NASA GRACE-FO data assimilation. v1 focuses on Romania and Hungary at NUTS-2 resolution.

## Status

Pre-launch. Repository scaffolded 2026-05-10.

## Automation

Two scheduled workflows keep the committed data current. Neither deploys —
hosting is still an open decision, so today they refresh data and prove the
site builds.

| Workflow | Schedule | What it does | Secrets |
| --- | --- | --- | --- |
| [`mirror.yml`](.github/workflows/mirror.yml) | daily, 06:23 UTC | Mirrors NASA's operational map from UNL | none — UNL is public |
| [`archive.yml`](.github/workflows/archive.yml) | Mondays, 06:43 UTC | Pulls new weeks from the GES DISC final archive | `EARTHDATA_USER`, `EARTHDATA_PASS` |

The cadences differ because the feeds do. UNL publishes on an unpredictable
weekday (1–7 day lag), so a weekly run could miss a map by nearly a cycle;
daily runs exit early when nothing new is out. The final archive lags 2–6
months and advances about a week per week, so weekly is ample.

Both verify the site builds *before* committing, so the build-time guards gate
what lands. Both also run `pipeline.freshness`, which fails the job when a feed
stops advancing — a frozen feed otherwise looks exactly like a quiet one.

Before the first run, set the two repository secrets under *Settings → Secrets
and variables → Actions*. The Earthdata account must have the **NASA GESDISC
DATA ARCHIVE** application authorized; see [pipeline/README.md](pipeline/README.md).

Note that GitHub disables scheduled workflows after 60 days of repository
inactivity, and pushes made with `GITHUB_TOKEN` do not themselves trigger other
workflows.

## Data source

[GRACEDADM_CLSM025GL_7D V3.0](https://data.nasa.gov/dataset/groundwater-and-soil-moisture-conditions-from-grace-and-grace-fo-data-assimilation-l4-7-da-31ce9) — NASA GES DISC. Weekly cadence, 0.25° resolution, NetCDF format. Coverage Feb 2003 → present. Public domain.

The product publishes pre-computed percentiles vs. a 1948–2014 baseline for groundwater, root-zone soil moisture, and surface soil moisture. (NASA's materials cite 1948–2012 in places; that describes a pre-V3.0 release — see [docs/methodology.md](docs/methodology.md).)

## Scope at v1

- Countries: Romania, Hungary
- Resolution floor: NUTS-2 (RO has 8 regions, HU has 8 regions; ~25 km grid cells)
- Language: English only

## Methodology

See [docs/methodology.md](docs/methodology.md).

## License

MIT (code). Data is NASA public domain.
