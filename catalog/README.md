# AGB Reference & Validation Data Catalog

A metadata catalog of **independent above-ground biomass (AGB) reference data** for validating
AGB maps. This is a *catalog first*: one row per dataset describing what it is, where it lives, how
to access it, and the traps to watch when using it as validation truth. It is **not** a data mirror —
nothing is downloaded here yet.

## Scope (decided 2026-07-23)

- **Geographic:** global.
- **Reference classes included:**
  1. **In-situ plots** — National Forest Inventories (NFIs) and research plot networks
     (GEO-TREES, ForestPlots.net, ForestGEO, TmFO, NEON field, TERN, …).
  2. **Airborne-lidar AGB** — wall-to-wall or transect biomass rasters derived from airborne lidar
     (Sustainable Landscapes Brazil, AfriSAR, NEON AOP, NASA CMS, GAO, SAFE, …).
- **Deliberately excluded** (they are *maps*, not independent truth — validating a map against
  another map or against the same spaceborne sensor is circular):
  - Spaceborne lidar AGB (GEDI L4A/L4B, ICESat-2).
  - Gridded reference/intercomparison maps (ESA CCI Biomass, Spawn & Gibbs, Avitabile, Saatchi, Baccini).
  - These can be added later as a separate `category` if wanted for map-vs-map intercomparison.

## Files

| File | Purpose |
|------|---------|
| `agb_reference_catalog.csv`  | Machine-readable, one row per dataset (flat, greppable). |
| `agb_reference_catalog.json` | Same records with richer nested notes. |
| `README.md`                  | This file — schema, scope, and validation caveats. |
| `SOURCES.md`                 | Per-dataset provenance: which URL/DOI each field came from and when it was verified. |

## Schema (columns)

| Field | Meaning | Notes |
|-------|---------|-------|
| `id` | kebab-case slug, unique | stable primary key |
| `name` | human name | |
| `category` | `in-situ-plot` \| `airborne-lidar-agb` | top-level class |
| `subtype` | `nfi` \| `plot-network` \| `supersite` \| `mapped-plot` \| `research-campaign` | |
| `provider` | hosting institution / agency | |
| `coverage_scope` | `global` \| `continental` \| `national` \| `regional` \| `site` | |
| `region` | free text (countries / biome / site) | |
| `variable` | `AGB` \| `AGC` (carbon) \| `growing-stock-volume` | **what is actually measured** |
| `units` | e.g. `Mg/ha`, `MgC/ha`, `m3/ha`, `Mg per plot` | see unit trap below |
| `representation` | `point-plot` \| `mapped-plot` \| `transect-raster` \| `wall-to-wall-raster` | the spatial *support* |
| `support_size` | plot area or raster pixel (e.g. `1 ha`, `0.04 ha`, `100 m`) | **scale of the reference** |
| `temporal_coverage` | acquisition/measurement years | |
| `geometry_type` | `point` \| `polygon` \| `raster` | |
| `native_crs` | as distributed (often EPSG:4326 for plots; UTM for lidar) | |
| `coord_availability` | `public-exact` \| `public-fuzzed` \| `restricted` \| `on-request` \| `site-known` | **decides pixel-level usability** |
| `n_records_or_area` | # plots or km² covered | |
| `access` | `open` \| `registration` \| `data-request` \| `collaboration` | |
| `license` | e.g. CC-BY-4.0, CC0, terms-of-use, restricted | |
| `format` | CSV / GeoTIFF / SHP / GPKG / API | |
| `portal_url` | primary access URL (verified to resolve) | |
| `doi` | dataset DOI where one exists | |
| `citation_short` | first author + year | |
| `verified` | `YYYY-MM-DD` the metadata was web-checked | staleness marker |
| `validation_caveats` | free text: allometry, coord precision, scale mismatch, year offset | |

## Why these fields — validation traps this catalog is built to prevent

Encoded from hard-won lessons (see `~/.claude/CLAUDE.md`). Every one of these produced
*plausible-looking wrong numbers*, not a crash:

1. **Units are not interchangeable.** `variable` + `units` are separate columns because half the
   pain is silent AGB (Mg/ha) vs carbon (MgC/ha, ~0.47×) vs growing-stock-volume (m³/ha, needs a
   wood-density × BEF conversion) confusion. Never compare a map to a reference without matching both.
2. **Spatial support must match.** `support_size` is explicit because a 0.04 ha FIA subplot, a 1 ha
   ForestGEO plot, and a 100 m airborne-lidar pixel are *different quantities* than a 10–100 m map
   pixel. Aggregate the finer to the coarser; report the support of every metric.
3. **Coordinate availability decides everything.** `coord_availability` is a first-class field: many
   NFIs legally **fuzz or withhold plot coordinates** (FIA "swaps"/perturbs; several EU NFIs release
   only aggregates). Fuzzed coords make pixel-level validation invalid — you can only validate at the
   aggregation the coordinates support.
4. **CRS is not free.** `native_crs` is recorded so no one assumes 4326. Plot lon/lat vs a UTM/​
   south-up (`transform.e > 0`) lidar raster must be reprojected, not numerically merged.
5. **Intersection is per-axis, and n must be asserted.** Before any metric: reproject reference into
   the map CRS, spatially filter, and `assert n > 0` — reporting `n` alongside every metric. A bbox
   check that ORs the axes will call disjoint regions "overlapping".
6. **Provenance / staleness.** `verified` dates the metadata; `SOURCES.md` records where each field
   came from. Re-check before quoting, because portals move and the same product ships under
   different DOIs/baselines.

## Intended use

The catalog feeds a future `validate.py` that, for a chosen (map, reference) pair:
reprojects reference → map CRS, asserts per-axis intersection and `n>0`, matches units and support,
samples the map at plot centres (not pixel boundaries), and records the mtime/hash of every raster a
number came from. This file defines the contract those steps rely on.
