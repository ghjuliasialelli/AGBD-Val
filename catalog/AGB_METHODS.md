# How AGB was obtained — per data source

One record of the exact method behind every above-ground-biomass value in `data/derived/`. Each output
also carries a machine-readable `*.provenance.json` (source sha256 + mtime + parameters) next to it, and
the code is in `derive_agb/`. Units are **AGB in Mg/ha** (dry biomass), not carbon, unless stated.

Allometry/coefficient sources are never fabricated — each is transcribed from or bundled with its
citation (`derive_agb/allometry.py`, `chojnacky_taxonomy.py`, `wood_density.py`, PDFs in `derive_agb/refs/`).

Legend: **route** = how structure→AGB; **coords** = tier for 10 m pixel use (A precise / B ≥~1 km).

---

## In-situ plot networks (dbh/volume → AGB)

### France IGN NFI — `france_ifn_plot_agb.csv` (61,472 plots) · coords A
- **Route:** IPCC volume→biomass. `AGB = Σ V·ρ(species)·BCEF·W` — V = per-tree stem volume (IGN-provided),
  ρ = basic wood density (Zanne 2009 / IPCC, 25-species table), BCEF = 1.30 conifer / 1.40 broadleaf,
  W = per-tree expansion (stems/ha).
- **Key traps handled:** volume computed only on `VISITE==1` (revisits carry V=0 → would give median 0);
  ESPAR species code leading-zero normalisation (else oak+beech = 34% of volume silently dropped).
- **Coords:** Lambert-93 (EPSG:2154), full precision.

### Spain IFN4 (MITECO) — `spain_ifn4_plot_agb.csv` (52,552 plots, 45 provinces) · coords A ("approx")
- **Route:** per-tree **Ruiz-Peinado 2011 (softwoods) + 2012 (hardwoods)** above-ground biomass by IFN
  species code (`spain_biomass.py`, 24 species; the NFI's own INIA models, published refinement of
  Montero 2005). dbh = (Dn1+Dn2)/2 mm→cm; height Ht (per-province log-log H-D fill where missing).
- **Expansion:** IFN variable-radius concentric-plot design — 5/10/15/25 m radii for dbh 7.5–12.5 /
  12.5–22.5 / 22.5–42.5 / ≥42.5 cm → 127.32/31.83/14.15/5.09 trees/ha; plot AGB = Σ(tree AGB × factor).
- **Coords:** `PCDatosMap` CoorX/CoorY + Huso, with the **per-province datum** (ED50 / ETRS89 / WGS84 —
  a ~200 m error if confused) → WGS84; missing Huso filled from province modal/default.
- **Two traps handled:** (1) `access-parser` drops the `PCMayores` Provincia column, shifting the *text*
  columns — so `Estadillo` (join) and `Especie` (species) are resolved by **content** (Especie by overlap
  with real IFN codes, since the `Subclase`/order columns are also 3-digit and would otherwise win).
  (2) per-province datum. Result median **58 Mg/ha** (biome-correct: arid SE ~22–35, wet N ~110–167).
- **Caveats:** IFN4 fieldwork ~2008–2019, province-dependent, and the field DB has **no per-tree date** —
  much predates the 2014 window (use the province campaign year). Coords "approximate" per MITECO.
  Species without an INIA equation (P. radiata, Q. robur/petraea, …) dropped+reported.
- **Reader trap:** `access-parser` throws (`KeyError` in column defs) on the **Extremadura** DB — so it
  now falls back to **mdbtools** (`mdb-export`), which preserves the `Provincia` column (no shift, so
  species/estadillo are read by label, not by content). Recovered Badajoz(06)+Cáceres(10) = 1,992 plots
  (median 38 Mg/ha, dehesa). Note: mdb-export yields float species codes (`62.0`) → normalised via
  numeric to `"062"`. Still absent: Almería(04), Castellón(12), Granada(18), Huelva(21), Sevilla(41).
  Of these, a **Castellón(12) IFN4 URL exists** in the scrape (`data/spain-ifn4/docs/fielddb_urls.txt`,
  `Ifn4p12_Castellón.zip`) but was not downloaded — recoverable; the four Andalucía provinces are IFN3-only.

### USA FIA — `fia_public_plot_agb.csv` (224,291 plot-visits, 51 states; 74,550 in-window) · **coords B**
- **Route:** **no allometry run** — FIA ships a precomputed per-tree oven-dry above-ground biomass
  `DRYBIO_AG` [lb]. Plot AGB = `Σ(DRYBIO_AG · TPA_UNADJ)` [lb/acre] × 0.00112085 → Mg/ha, per plot-visit
  (`PLT_CN`). Post-2023 DataMart `DRYBIO_AG` = **NSVB** (National Scale Volume & Biomass, ~15% higher than
  the old CRM component estimates) — so these are NSVB tonnes, worth noting against older FIA comparisons.
- **Public-land subset:** `COND.OWNGRPCD ∈ {10,20,30}` (federal/state/local) only. This deliberately
  **avoids the ~20% private-plot coordinate swap** (FIA perturbs *and* swaps a fraction of private-plot
  coordinates; public-land plots are only fuzzed, never swapped). Every forest condition on a kept plot
  is public.
- **Coords:** **TIER B** — public coordinates are fuzzed up to ~0.8–1.6 km (never swapped for public land).
  Good for aggregate / coarse (county / ecoregion / ~1 km) validation, **not 10 m pixels**. True plot
  centres only via **FIA Spatial Data Services** (collaborator-gated, months-long — route PAUSED).
- **Result:** national median **85.3 Mg/ha** (mean 110.9, p95 303.7); regional medians sane (UT 29, WV 186,
  OR 123, PR 43). Per-plot `MEASYEAR` retained → in-window (2014–2025) subset = 74,550.
- **Independence:** for holdout, exclude **whole FIA survey units / states** rather than nearby plots.

### NEON Woody Veg Structure — `neon_plot_agb.csv` (4,150 plot-years) · coords A
- **Route:** Chojnacky, Heath & Jenkins 2014 (Forestry 87:129), Table 5 per-stem `AGB = exp(b0+b1·ln dbh)` [kg],
  grouped by taxon via wood specific gravity; summed per plot ÷ `totalSampledAreaTrees`.
- **Coefficients:** authoritative Table 5 (35 groups) transcribed from the PDF (`refs/Chojnacky2014_Forestry.pdf`);
  the pre-existing "pine"/"spruce" coeffs were wrong and were replaced.
- **Traps:** growthForm filtered to trees (NEON tags every shrub/vine); Live only; breast-height dbh;
  area denominator = `totalSampledAreaTrees` (nested-subplot design), not nominal 400 m².

### BC FAIB PSP — `bc_psp_plot_agb.csv` (23,942 plot-visits; 1,593 in-window GPS) · coords A
- **Route:** Chojnacky 2014 per-stem (reused from NEON; BC's NW-conifer flora overlaps), expanded by the
  FAIB-provided `PHF_TREE` (per-ha factor incl. plot area/weight/walkthrough), summed per plot-visit.
- **Species:** BC 2-letter codes → scientific name (`bc_species.py`, confident codes only; 99.7% of stems;
  rest dropped+reported). Live only (`LV_D='L'`), dbh ≥ 4 cm.
- **Coords:** TRUE (PSP), precision flagged per plot via `UTM_SOURCE` (DGPS/RGPS/VGPS = GPS-grade).
- **Result:** median 192 Mg/ha.

### Quebec MFFP PEP — `quebec_pep_plot_agb.csv` (50,105 measurements; 11,262 in-window GPS) · coords A
- **Route:** Chojnacky 2014 per-stem (NE-temperate flora), expanded by the MFFP `tige_ha` (stems/ha),
  summed per plot-measurement. dbh = `dhp`/10 (mm→cm).
- **Species:** essence code → scientific name (`quebec_species.py`, from the dictionary ESSENCES sheet).
- **Trap:** ETAT `14`/`44` = "mort sur pied" (DEAD) — excluded (549k stems); live set = 10/12/30/32/40/42/50/52.
- **Coords:** WGS84 lat/lon, `in_gps` flag. **Result:** median 78 Mg/ha (boreal/mixedwood).

### BCI ForestGEO 50-ha — `bci_forestgeo_quadrat_agb.csv` (1,250 quadrats) · coords A (axis-aligned)
- **Route:** latest census (8, ~2013–2016, in-window), live stems ≥1 cm; per-stem **Chave 2005 moist**
  (diameter-only) with wood density from GWDD (Central-America-tropical); aggregated to the plot's
  **20×20 m quadrats** (400 m² → Mg/ha) and whole-50-ha.
- **Result:** whole-plot **302.5 Mg/ha** (matches published BCI ~280–320 → validates the chain); quadrat
  median 240 Mg/ha.
- **Coords: absolute georef NOW APPLIED.** Community-standard **axis-aligned** affine: plot-local PX/PY →
  UTM 17N/WGS84 (EPSG:32617), SW corner **(625754, 1011569)**, plot-x→+E, plot-y→+N → lon/lat. Same
  convention as the plot's own georeferenced products (Kupers 2019 soil rasters, ForestGEO photogrammetry),
  so comparisons against them are consistent. **Centre verified at 9.1516 °N, 79.8509 °W** (documented
  ~9.15 N/79.85 W — asserted in code). CSV keeps both `px_center/py_center` (exact plot-local) and
  `utm_e/utm_n/lon/lat` (absolute). The plot's **sub-degree physical rotation vs UTM north is neglected**
  (as in those standard products) → residual edge error ≤~9 m (~1 px) at the far x=1000 edge; fine for
  coarse/aggregate placement, treat 10 m pixel matching as approximate.
- **Access:** Dryad gates downloads (API bearer token + Cloudflare); fetched with a user-supplied token.
- **CIRCULARITY:** BCI may be in the training set of CCI/GEDI/JAXA (and possibly AEF) — confirm independence.

### Mondah (AfriSAR field) — `mondah_plot1ha_agb_derived.csv` (15 plots) · coords A — VALIDATED
- **Route:** Chave et al. 2014 Eq.4 `AGB = 0.0673·(ρ·D²·H)^0.976` [kg], per tree → 1-ha plots.
- **Validation:** reproduces the provider's published per-tree `m_agb` to mass-weighted 1.1e-4 (PASS).
  Height rule: measured `h_t` where >0 else `h_t_mod`. 47/6692 sentinel stems documented.

### TERN Biomass Plot Library — `tern_biomass_plot_library_agb.csv` (612 plots) · coords B, pre-window
- **Route:** provider `agb_drymass_ha`, re-aggregated from live (`condition==0`) stems to verify;
  per-row `verify_status` (verified_exact / provider_disagrees / provider_suspect / no_stem_data).
- **Caveats:** library ends Oct 2015 (zero AEF overlap); support filter `--min-area-ha` (biome-sensitive).

### Colombia IFN / IDEAM — `colombia_ifn_conglomerado_agb.csv` (283 conglomerados) · **coords B**
- **Route:** DBH back-calculated from per-record basal area (`dbh = √(4·(BA/count)/π)`); wood density from
  the Global Wood Density DB (Zanne 2009, South-America-tropical, species→genus→family→region fallback,
  `wood_density.py`); **Chave et al. 2005 moist-forest, diameter-only** (no height/E in-file); per
  conglomerado area-weighted (nested F=154 m² / FG=707 m² subplot areas from `sampleSizeValue`).
- **Coords:** **TIER B** — generalized to ~10.6 km grid (`coordinateUncertaintyInMeters`=10606; exact only
  on request to IDEAM). Distributional reference, not pixel validation. "datos sin validar."
- **Result:** median 58 Mg/ha.

### SLB Brazil field inventory — `slb_brazil_transect_agb.csv` (309 records, 14 sites) · coords A where present
- **Route:** Chave 2014 Eq.4 (height); WD = in-file `WSD` where it varies by species else GWDD
  (South-America tropical); height = in-file `Htot` else per-site/pooled log-log H-D model. Live trees;
  lianas/palms excluded; DBH ≥ 5 cm.
- **Area (the crux — now correct):** the `*_plots` shapefiles carry, per plot, a **`plot` (~0.25 ha main)
  + `subplot` (~0.05 ha nested)** polygon pair. We match each CSV plot to the **LARGEST polygon for that
  plot number** (so the nested subplot never shadows its main plot), falling back to the site's median
  main-plot area for undigitized plots (`design_site`), and to the documented **20×500 m = 1 ha** for
  transect-keyed sites. `area_src` column records which was used (shp 154 / design_1ha 119 / design_site 36).
- **AREA FIX (this pass) — caught six silently-wrong sites:** the earlier granularity-guarded matcher fell
  back to 1 ha for plot-keyed sites whose real plots are 0.25 ha, giving medians that *looked* plausible
  but were **4× too low** and so were never flagged: **BON 31→128, HUM 34→138, TAL 27→104, SAN 5→23,
  FN 18→71** (0.25 ha), **TAC 38→111** (~0.09 ha). Verified against the shapefiles' explicit `plot`/`subplot`
  labels (~2500 vs ~490 m²). **13 of 14 sites now plausible** (medians 23–273 Mg/ha).
- **FNA is the one remaining flag — and it's genuine, not a bug:** its area *is* correct (500 m transects =
  the 1 ha design, confirmed from per-tree UTM extents), but only **49 of 283 trees are live** → a real
  **degraded/heavily-logged** site at ~4 Mg/ha live biomass. Keep it, but treat as a low-biomass outlier,
  not a normal-forest point. **Filter `site_plausible=True` for the clean set.** SLB is mostly 2009–2013,
  so its in-window Tier-A subset is small regardless (32 records).

---

## Airborne-lidar / carbon rasters (ACD → AGB)

All three: `AGB = ACD / carbon_fraction`, carbon_fraction = **0.48** (Asner/Mascaro tropical; a flag).
Nodata masked on RAW values (sentinel + NaN + finite-negatives) BEFORE the divide, then re-stamped;
population stats asserted (`extract_carbon_raster.py`, `extract_gao_sabah.py`).

| output | source | units in | result |
|---|---|---|---|
| `GAO_Sabah_AGB_30m.tif` | Asner Sabah ACD (Zenodo) | MgC/ha | mean 149 Mg/ha, 77.6 M px |
| `GAO_Peru_AGB_100m.tif` | Asner Peru ACD (Zenodo 4626309) | MgC/ha | mean 112, max 361 Mg/ha; UTM18S |
| `SLB_Paragominas_AGB_50m.tif` | ORNL 1648 (LiDAR+PALSAR) | MgC/ha* | mean 198, max 602 Mg/ha |

*Paragominas: the ORNL guide states "megagrams of carbon per hectare" five times but mislabels axes
"Mg/ha" — treated as **carbon** (confirmed from guide text). Both Peru & Paragominas are lidar+radar
**fusion**, not pure ALS — note for independence claims.

---

## Shared infrastructure
- `derive_agb/allometry.py` — Chave 2014 Eq.4/Eq.7, **Chave 2005 moist** (added for Colombia), Chojnacky 2014
  Table 5, `acd_to_agb` (carbon flag). Models needing site coefficients raise `NotCalibratedError`.
- `derive_agb/wood_density.py` — Global Wood Density DB (Zanne 2009), via R BIOMASS `wdData.rda`
  (`data/wood-density/`); `getWoodDensity`-style species→genus→family→region fallback, level recorded.
- `chojnacky_taxonomy.py` / `bc_species.py` / `quebec_species.py` — taxon→group/species-code resolvers.

## Population invariants asserted (every derivation)
Each script asserts a plausible median AGB over the whole population before writing (e.g. `20 < median < 800`),
reports taxon/stem coverage, and drops-and-reports unmapped taxa rather than defaulting them. Coordinate
usability is recorded per plot, not assumed.
