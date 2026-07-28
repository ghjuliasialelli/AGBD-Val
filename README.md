# AGBD-Val — AGB map validation testbed

A testbed for validating above-ground biomass (AGB) maps — primarily 10 m AlphaEarth Foundations
(AEF) embedding-based AGB predictions — against **independent** field and airborne-lidar reference
data. The current phase builds a documented reference base (biomass in **Mg/ha, dry**, with per-plot
coordinates and usability tiers); the AEF-sampling / evaluation phase has not started yet.

> **Machine rule (pf-pc28):** write only under `/scratch3/gsialelli`. Never write to `/home/gsialelli`.
> See `CLAUDE.md`. The `~/.claude` symlink resolves into `/scratch3`, so agent memory is safe.

## Layout

```
AGBD-Val/
├── README.md                  ← you are here (repo map)
├── CLAUDE.md                  ← project + machine rules for the coding agent
├── pyproject.toml             ← uv venv (.venv); python 3.13, geo stack
│
├── catalog/                   ← the reference-data catalog + project state (docs-first)
│   ├── README.md                schema + validation traps
│   ├── PROJECT_STATE.md         full state / handoff
│   ├── AGB_METHODS.md           HOW each AGB value was derived (equation, coeffs, area, tier, caveats)
│   ├── COORD_TIER_PARTITION.md  Tier A (pixel) vs Tier B (aggregate) split + fetch/derive status
│   ├── agb_reference_catalog.{csv,json}   machine-readable catalog (one row per dataset)
│   ├── SOURCES.md · audit_catalog.py      sources + the catalog audit gate
│   └── archive/                 superseded origin docs (kept for provenance)
│
├── derive_agb/                ← structure → AGB derivation code (one extract_*.py per source)
│   ├── allometry.py             Chave 2014/2005, Chojnacky 2014, ACD→AGB
│   ├── wood_density.py          Global Wood Density DB (Zanne 2009) lookup w/ taxonomic fallback
│   ├── spain_biomass.py · bc_species.py · quebec_species.py · chojnacky_taxonomy.py
│   ├── extract_<source>.py      per-source extractors (see AGB_METHODS.md for what each does)
│   └── refs/                    method reference papers (Chojnacky 2014, Ruiz-Peinado 2011/2012)
│
└── data/
    ├── fetch_*.py · fetch_*.sh · dl_common.py   downloaders (resumable, provenance-stamped)
    ├── manifest_*.tsv · *.log                   download manifests + logs
    ├── ACCESS_REQUESTS.md                        drafted letters for gated true-coord sources
    ├── DOWNLOAD_TRIAGE.md · spain_ifn4_files.txt
    ├── <source>/                                 raw downloads, one dir per dataset
    │   └── spain-ifn4/docs/                      IFN4 dataset manuals + acquisition provenance
    ├── logs/                                      all run logs (consolidated)
    └── derived/                                   ← THE OUTPUTS: <name>_agb.csv/.tif + .provenance.json
```

## Derived outputs (`data/derived/`)

Every output carries a `*.provenance.json` (source sha256 + mtime + parameters) and was written by a
script that asserts a plausible population median before saving. See `catalog/AGB_METHODS.md` for the
exact method behind each, and `catalog/COORD_TIER_PARTITION.md` for the usability tier.

| Output | Source | Tier | n |
|---|---|---|---|
| `france_ifn_plot_agb.csv` | France IGN NFI | A | 61,472 |
| `spain_ifn4_plot_agb.csv` | Spain IFN4 (MITECO) | A | 52,552 / 45 prov |
| `quebec_pep_plot_agb.csv` | Quebec MFFP PEP | A | 50,105 |
| `bc_psp_plot_agb.csv` | BC FAIB PSP | A | 23,942 |
| `neon_plot_agb.csv` | NEON woody veg | A | 4,150 |
| `bci_forestgeo_quadrat_agb.csv` | BCI ForestGEO 50-ha | A | 1,250 quad |
| `mondah_plot1ha_agb_derived.csv` | AfriSAR Mondah field | A | 15 |
| `fia_public_plot_agb.csv` | USDA FIA (public land) | B | 224,291 |
| `tern_biomass_plot_library_agb.csv` | TERN (Australia) | B | 612 |
| `colombia_ifn_conglomerado_agb.csv` | Colombia IDEAM IFN | B | 283 |
| `slb_brazil_transect_agb.csv` | SLB Brazil field | A | 309 / 14 sites |
| `GAO_Sabah_AGB_30m.tif` | Asner Sabah ACD | raster | 77.6 M px |
| `GAO_Peru_AGB_100m.tif` | Asner Peru ACD | raster | — |
| `SLB_Paragominas_AGB_50m.tif` | ORNL 1648 lidar+radar | raster | — |

- **Tier A** = precise coordinates (about 10 m), usable for per-pixel validation.
- **Tier B** = coordinates fuzzed/aggregated (≥1 km) — aggregate/distributional cross-checks only.

## Running

```bash
.venv/bin/python -u derive_agb/extract_<source>.py     # re-derive one source (idempotent)
.venv/bin/python catalog/audit_catalog.py              # catalog audit gate (exits non-zero on failure)
```

The venv is at `.venv` (uv, python 3.13). Base `python` has no pandas — always use `.venv/bin/python`.

## Status & next step

Reference base is built (see the table). **Next phase (not started):** fetch AEF embeddings, then sample
them at plot coordinates → `(embedding, AGB)` validation pairs — reproject to the AEF tile CRS, sample at
**pixel centres**, mask AEF nodata on **raw** values, and run a **circularity audit** first
(BCI/ForestGEO/GEO-TREES may be in AEF's training set). Full handoff: `catalog/PROJECT_STATE.md`.

## Known gaps
- Every derived output now carries a `*.provenance.json`. Naming: raster provenance is
  `*.tif.provenance.json`, CSV provenance is `*.provenance.json`.
- Spain: 5 provinces (04/12/18/21/41) not yet derived — a `Ifn4p12_Castellón` URL exists
  (`data/spain-ifn4/docs/fielddb_urls.txt`) and is recoverable; the 4 Andalucía ones are IFN3-only.
