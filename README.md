# groundwaterwatch

Europe's hidden drought, mapped weekly.

A public dashboard that tracks groundwater depletion across Europe using NASA GRACE-FO data assimilation. v1 focuses on Romania and Hungary at NUTS-2 resolution.

## Status

Pre-launch. Repository scaffolded 2026-05-10.

## Data source

[GRACEDADM_CLSM025GL_7D V3.0](https://data.nasa.gov/dataset/groundwater-and-soil-moisture-conditions-from-grace-and-grace-fo-data-assimilation-l4-7-da-31ce9) — NASA GES DISC. Weekly cadence, 0.25° resolution, NetCDF format. Coverage Feb 2003 → present. Public domain.

The product publishes pre-computed percentiles vs. a 1948–2012 baseline for groundwater, root-zone soil moisture, and surface soil moisture.

## Scope at v1

- Countries: Romania, Hungary
- Resolution floor: NUTS-2 (RO has 8 regions, HU has 8 regions; ~25 km grid cells)
- Language: English only

## Methodology

See [docs/methodology.md](docs/methodology.md).

## License

MIT (code). Data is NASA public domain.
