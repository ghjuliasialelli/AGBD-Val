# Validation data partition by coordinate usability

Two evaluation regimes need two data tiers. The scarce resource across the whole survey is **usable
coordinates**, not biomass data — most sources have AGB/dbh but degrade or withhold plot locations.

- **Tier A — pixel / plot-level** (`coord_usability_tier = precise`): coordinates good to ~10 m, or a
  precise plot footprint/polygon. Sample AEF at the plot and compare directly. This is real validation.
- **Tier B — aggregated** (`coord_usability_tier = grid_1km | fuzzed | coarse`): location known only to
  ~1 km (grid snap, deliberate fuzz, or coarse cluster grid). Usable ONLY for distributional / regional
  cross-checks — NEVER for 10 m pixel co-location. Treating a Tier-B source as pixel-level silently
  samples the wrong cell.

Cross-cutting flags (orthogonal to the tier):
- `[held]` already downloaded/derived under `data/`.
- `[gated]` needs NDA / country approval / research agreement (not one-click).
- `[circular?]` these plots calibrate CCI Biomass / GEDI L4 / JAXA — if AEF training touched them,
  validation is circular. Must check the model's training set before use.
- `[temporal]` field epoch outside/at the edge of 2014–2025 (relaxed rule: OK only for slow-change forest).

Status: all 6 regional scans folded in (US-FIA, tropical networks, Asia-Pacific/Africa, Central/West
Europe, Nordic/Baltic). Confirmed conclusion: **usable coordinates are the scarce resource** — the data
mostly exists; ~10 m-usable geolocation is what's rare, and it is almost always agreement-gated.

---

## Tier A — pixel / plot-level (usable at 10 m)

| Source | Region | n | Content | Coord basis | Window | Flags | Action |
|---|---|---|---|---|---|---|---|
| **France IGN NFI** | France | 61,472 | vol+species→AGB | Lambert-93 full precision | 2017–2024 ✓ | [held] | **have — workhorse** |
| **NEON** | US | 4,150 py | dbh+species (Chojnacky) | survey-grade | 2014–2025 ✓ | [held] | **have — workhorse** |
| **Mondah (AfriSAR)** | Gabon | 15 | dbh+ρ→AGB (Chave) | 1 ha footprints | 2016 | [held] | **have — anchor, validated** |
| **GAO Sabah** | Malaysia | raster | ACD→AGB | wall-to-wall raster | mid-2010s | [held] | **have — anchor** |
| **Spain IFN4** | Spain | ~province | dbh+species→AGB (Montero05) | per-plot UTM, "approximate" | 2008–2020s, per-province | verify coords | **FETCH-NOW (top)** |
| **Nepal DFRS/FRTC** | Nepal | 2,009 | AGB t/ha direct | exact GPS | 2010–2014 | [temporal] | **FETCH-NOW** (slow-change only) |
| **Labrière 2018** | FG + Gabon | 6 sites | plot AGB | polygon footprints | FG ~2009 / Gabon ~2015 | [temporal] partial | **FETCH-NOW** (Gabon in-window) |
| **India–Kashmir** (Rather24) | India | 275 | dbh+species→AGB | exact GPS ±3 m | 2021 ✓ | CC-BY-NC; 0.04 ha≈2×2 px | **FETCH-NOW** (regional) |
| **SAFE Sabah ALS** | Malaysia | raster | ALS ACD | precise WGS84 | 2014 ✓ | overlaps GAO Sabah | fetch if non-overlapping |
| **Indonesia HCSA 2023** | Indonesia | — | biomass/carbon | verify | 2023 ✓ | verify coords+indep. | verify then fetch |
| **Switzerland LFI4/5** | CH | — | vol/biomass | exact, **NDA-only** | 2009–2026 ✓ | [gated] | request (best true-coord EU) |
| **FIA (true coords)** | US CONUS | ~100k s | DRYBIO_AG precomputed | true centres via SDS | 2014–2025 ✓ | [gated] paused | request later (see below) |
| **CTFS-ForestGEO** | global | per-site | stem-mapped→AGB | precise local xy | many 2014–25 ✓ | [gated][circular?] | request per-site if needed |
| **South Korea NFI** | Korea | ~4,500 | dbh+species→AGB | **unverified** | 5-yr →2020s ✓ | verify coords | verify then fetch |
| **BCI ForestGEO** | Panama | 50 ha | per-stem dbh+species (derive AGB) | local grid gx/gy (m); needs affine→UTM17N w/ rotation | 1982–2015 old-growth | [circular?] CC0 | **REGISTER** — Dryad now gates downloads (Cloudflare + API bearer token); needs a Dryad account/token or browser DL |
| **Colombia IFN / IDEAM** | Colombia | plots | dbh+species→AGB | decimal lat/lon (verify) | 2015–2017 ✓ | CC-BY, "sin validar" | **FETCH-NOW** (provisional) |
| **BC ground plots (PSP/VRI)** | Canada | plots | dbh+species+vol | PSP/VRI real coords (CMI/NFI generalized) | incl. 2014–2025 ✓ | OGL-BC | **FETCH-NOW** (PSP/VRI subset) |
| **Quebec PEP** | Canada | ~12,000 | dbh+species+vol | GPKG geometry (verify) | 1970–, ~10yr remeas ✓ | CC-BY QC | **FETCH-NOW** (verify coords) |
| **Sust. Landscapes Brazil field AGB** | Brazil | 93 sites | dbh+ht+species, AGB | per-site (verify exact) | 2009–2018 ✓ | NASA open ORNL 2007/1301 | **FETCH-NOW** (verify coords) |

### Open airborne-lidar AGB/ACD rasters (Tier A by geolocation; carry carbon + fusion caveats)
Wall-to-wall rasters, so georeferencing is intrinsic — but read the units and note they are **not pure ALS**.

| Source | Region | Content | Resolution | Window | Caveats | Action |
|---|---|---|---|---|---|---|
| **GAO/Asner Peru carbon** | Peru | ACD **MgC/ha** (+unc.) | **100 m / 1 ha** | ALS ~2011–13 | carbon ÷~0.47; **fusion** (lidar+Planet+radar); coarse vs 10 m; check CRS | **FETCH-NOW** (Zenodo 4626309) |
| **Sust. Landscapes Paragominas** | Brazil | AGB GeoTIFF **MgC/ha** | verify px | 2012 | **lidar+PALSAR fusion**; single Pará site; verify px size | **FETCH-NOW** (ORNL 1648) |
| **Paracou ALS** | FG | .laz point cloud (**no AGB**) | <1 m | 2019 | derive metrics; needs calibrated RH→AGB | fetch to derive (CEDA) |

**Americas request-gated (long lead, in-window, rich):** Argentina INBN2 (~4,158 plots, 2015–23 — best in-window) ·
Mexico INFyS (4 cycles, richest content; coords confidential) · Chile IFN · Canada NFI/Alberta (DUA; public=generalized) ·
Peru INFFS · Ecuador ENF · Costa Rica INF (coords "approx. for security"). **Skip:** Brazil EBA AGB (1° aggregated).

## Tier B — aggregated only (~1 km / coarse; distributional cross-check, NOT pixel)

| Source | Region | n | Content | Coord basis | Window | Flags | Action |
|---|---|---|---|---|---|---|---|
| **FIA (public)** | US 51 st | 224,291 (74,550 in-win) | DRYBIO_AG precomputed, med 85.3 | fuzz ~0.8–1.6 km (public: no swap) | 2014–2025 ✓ | ✅ DERIVED | `fia_public_plot_agb.csv` |
| **Germany BWI4** | DE | open | direct AGB + dbh/vol | 1 km INSPIRE grid | 2017/2022 ✓ | open REST API | fetch as grid_1km |
| **Italy INFC** | IT | open* | phytomass + C direct | 1 km grid | ~2017–2020 ✓ | free reg. | register as grid_1km |
| **Netherlands NBI-7** | NL | open | dbh/vol→BEF biomass | 1 km grid | 2017–2022 ✓ | | fetch as grid_1km |
| **GEO-TREES / FOS** | global | 274+ | plot AGB + CI | ~1 km rounded (open tier) | census→2018 | [circular?] CC-BY | fetch as coarse |
| **ForestPlots.net / RAINFOR / AfriTRON** | tropics | 1000s | dbh+species→AGB | ~1 km fuzz (2 dp cap) | ongoing | [gated][circular?] co-author | request only if needed |
| **TERN Biomass Plot Library** | Australia | 612 | plot AGB | variable/"where avail" | **≤2015** | [held][temporal] | **have — but pre-window** |
| **DRC NFI** | DRC | — | biomass | 111 km grid | 2017–2021 ✓ | [gated] FAO | request; grid too coarse |
| **Tanzania NAFORMA** | TZ | 30,382 | dbh+ht→AGB | cluster, not released | 2010–12 + 2020 | [gated] | request; coarse |

### Nordic / Baltic NFIs — all coordinate-gated (Tier B unless an agreement grants true coords → then Tier A)
Excellent temporal fit (all annual/rolling panels covering 2014–2025) and dbh+species biomass, but **every
one treats exact plot coords as confidential**. None fetch-now for 10 m. Native biomass models differ —
record which one produced any delivered AGB (Marklund/Petersson SE·NO, Repola FI, Nord-Larsen DK).

| Source | Region | Content | Coord basis | Window | Flags | Action |
|---|---|---|---|---|---|---|
| **Sweden** Riksskogstax. (SLU) | SE | dbh+species→Marklund/Petersson | public coords **deliberately offset** ("unusable w/ ALS"); true = agreement | 2007–present ✓ | [gated] | **request true coords**; CC0 sample-tree/temp sets = context only |
| **Finland** VMI (Luke) | FI | dbh+species→Repola | exact confidential; Luke agreement | VMI12/13 2014–23 ✓ | [gated] | request (Luke contract) |
| **Norway** Landsskog. (NIBIO) | NO | dbh+ht→Marklund/Petersson; 250 m² | exact confidential | 5-yr panel ✓ | [gated] | request (NIBIO) |
| **Denmark** Skovstatistik (KU-IGN) | DK | dbh+species→Nord-Larsen | exact confidential; 2×2 km placement grid ≠ location | rolling ✓ | [gated] | request (KU-IGN) |
| **Estonia** SMI (Keskkonnaag.) | EE | dbh+species; ~4,000 plots | full-precision but scientists-only agreement | annual ✓ | [gated] | **request** (best open-data culture) |
| **Latvia** MSI (Silava) | LV | dbh+species; 500 m² | not public | cycles III/IV ✓ | [gated] | request; skip CC0 Register (non-indep.) |
| **Lithuania** NFI (VMT) | LT | dbh+species; ~6,154 plots | **explicitly secret** | 5-yr ✓ | [gated] | request; skip Cadastre (non-indep.) |
| **Iceland** NFI (Land&Forest) | IS | dbh+species→Snorrason | not public | rolling ✓ | [gated] | near-skip (tiny low-biomass birch) |

**Baltic independence trap:** Latvia's Forest State Register (CC0) and Lithuania's Forest Cadastre (open)
are the only openly downloadable forest datasets, but both are **stand-level ocular/management inventories
with modelled volumes — NOT independent field plots.** Do not substitute them for NFI reference data.

## Skip (no usable structure, out of scope, or closed with no path)

China CNFI (coords = state secret) · India FSI/ISFR (reports only) · Japan NFI (volume only, closed) ·
Vietnam/Philippines/Malaysia national NFIs (closed) · sPlot / DRYFLOR (floristic, no biomass) ·
Duncanson GEDI DB (spaceborne product; field DB ALS-coupled → non-independent) · FAO FRA (national totals).

---

## The FIA special case (both tiers, one dataset)
FIA public data is **Tier B**: biomass (`DRYBIO_AG`) and per-plot dates are open and excellent, but public
coordinates are fuzzed ~0.8–1.6 km with ~20% private-plot swaps → aggregate/QA only. **Tier A requires the
true-coordinate route through FIA Spatial Data Services**, which is currently:
- **PAUSED** ("cannot process requests for confidential information at this time" — federal workforce cut),
- **months-long** and may be denied, **collaborator-gated** (needs an FIA co-investigator + MTA/NDA),
- and returns **predicted-vs-observed pairs, never coordinates** (you submit your map; they extract).
Do not block the pipeline on it. For independence, hold out **whole regions** (FIA survey units / states
aligned to EPA L3 / Bailey provinces), not individual plots — nominees: **PNW westside** + **SE pine belt**.

## Load-bearing verification to-dos (per the geospatial playbook)
- **Spain IFN4**: coords are officially "approximate" — empirically verify accuracy on ≥2 provinces before
  trusting at 10 m; read per-region field year from the DB (some regions still IFN3 / pre-window).
- **Circularity check**: before using GEO-TREES / ForestPlots / ForestGEO in ANY tier, confirm AEF training
  did not ingest them (they calibrate CCI/GEDI/JAXA). Record per-plot source-network + census year.
- **Per-plot year, not campaign midpoint**: Nepal, Korea, Spain — confirm a per-plot measurement-year column.
- **Small plots**: Kashmir 0.04 ha ≈ 2×2 px, Labrière sub-plots — expect co-registration sensitivity;
  sample at pixel centres.
- **Overlap**: SAFE Sabah ALS vs GAO Sabah — check AOIs before treating as new coverage.

---

## Fetch status (2026-07-27) — open Tier-A batch downloaded + validity-checked
Downloaded via `data/fetch_tier_a.py` (serial, resumable), validated via `data/validate_tier_a.py`
(rasters opened, archives tested, coord/dbh columns confirmed — not just "file exists"). **ok=87, fail=5**
(the 5 = BCI, see below). Derivation (carbon→AGB, allometry, coord reprojection, per-plot AGB) is a
SEPARATE next step, deliberately NOT done yet.

| dataset | dir | validated facts | derive-time TODO |
|---|---|---|---|
| GAO Peru ACD | `data/gao-peru-carbon/` (3.0 GB) | 2 GeoTIFFs, **EPSG:32718 (UTM18S), 100 m**, MgC/ha, nodata −9999, range 0–157 | ÷~0.47 carbon→AGB; note single-zone raster spans all Peru |
| SLB Brazil field | `data/sustainable-landscapes-brazil/2007_field_inventory/` | 34 files; CSV has `scientific_name`, `DBH_09/10/11`, `date_09/10/11`, `UTM_Easting/Northing`; **per-site UTM 22S/23S** | derive AGB (Chave); honor per-site zone; no AGB column |
| SLB Paragominas AGB | `.../1648_paragominas_lidar_agb/` | whole-muni **EPSG:4326 ~50 m** (0–247), per-site **UTM23S** 100 m; nodata −99999 | **units MgC/ha but mislabeled Mg/ha in guide — resolve before use** |
| Colombia IFN | `data/colombia-ifn/ideam_ifn_dwca.zip` | DwC-A; `event.txt` **1,886 plots** w/ `decimalLat/Lon`, `eventDate`, **`coordinateUncertaintyInMeters`**; dbh in `extendedmeasurementorfact.txt` | check `coordinateUncertaintyInMeters` per plot → assign coord tier; "datos sin validar" |
| BC PSP | `data/bc-ground-plots/psp/` (803 MB) | coords in **`faib_header.csv`** (`IP_UTM/IP_EAST/IP_NRTH`, `BC_ALBERS_X/Y`, `Lon/Lat`, `UTM_SOURCE`, `SAMPLE_ESTABLISHMENT_TYPE`); `MEAS_YR` in `faib_sample_byvisit.csv`; `SPECIES/DBH/PHF_TREE` in `faib_tree_detail.csv` (740 MB) | join on `SITE_IDENTIFIER`; filter to true-coord PSP via `SAMPLE_ESTABLISHMENT_TYPE`/`UTM_SOURCE`; derive AGB |
| Quebec PEP | `data/quebec-pep/PEP.gpkg` (128 MB zip) | valid GPKG + data dictionary | read CRS from GPKG; derive AGB from `essence`+`dhp` |

### Derived to AGB (2026-07-27) — `data/derived/`, each with provenance JSON
The downloaded batch turned into AGB (allometry/carbon-conversion applied, population invariants asserted):

| product | output | result |
|---|---|---|
| GAO Peru | `GAO_Peru_AGB_100m.tif` | ACD÷0.48 → **AGB mean 112, max 361 Mg/ha**; 128.6 M valid px, UTM18S |
| SLB Paragominas | `SLB_Paragominas_AGB_50m.tif` | MgC/ha÷0.48 (units confirmed from guide) → **mean 198, max 602 Mg/ha** |
| BC PSP | `bc_psp_plot_agb.csv` | **23,942 plot-visits**, 99.7% stem coverage, median 192 Mg/ha; **1,593 in-window + GPS-coord** |
| Quebec PEP | `quebec_pep_plot_agb.csv` | **50,105 plot-measurements**, 100% coverage, median 78 Mg/ha; **11,262 in-window + GPS** |

BC/Quebec used per-tree DBH+species → **Chojnacky 2014** (reused from NEON) × the provider's per-ha
expansion factor (`PHF_TREE` / `tige_ha`). Traps caught by checking source dictionaries, not guessing:
Quebec `etat=14/44` = **dead** (549k stems correctly excluded); BC species map limited to confidently
attributable codes (99.7% covered, rest dropped+reported).

**Second-pass derivations (2026-07-27), after fetching the Global Wood Density DB (Zanne 2009, via R
BIOMASS → `data/wood-density/`):**
| product | output | result |
|---|---|---|
| Colombia IFN | `colombia_ifn_conglomerado_agb.csv` | **283 conglomerados**, median 58 Mg/ha (Chave 2005 moist, DBH from basal area, GWDD). **Tier B — coords generalized to ~10.6 km** (recategorize from Tier A) |
| SLB Brazil field | `slb_brazil_transect_agb.csv` | **309 records / 14 sites; 13/14 plausible** after matching each plot to its LARGEST `*_plots` polygon (main plot, not the nested subplot). This area fix corrected **six silently-4×-low sites** (BON 31→128, HUM 34→138, TAL 27→104, SAN 5→23, FN 18→71 at 0.25 ha; TAC 38→111 at ~0.09 ha) that all *looked* plausible before. Only **FNA** still flagged — its 1-ha area is correct (500 m transects); low value is GENUINE degradation (49/283 trees live), not a bug. Filter `site_plausible=True`. Mostly 2009–2013 |

Full per-source method writeup: **`catalog/AGB_METHODS.md`**.

**BCI — DONE (2026-07-27; georef added 2026-07-28):** Dryad gates downloads (API bearer token +
Cloudflare); fetched with a user-supplied Dryad token (5 files, exact sizes). Derived →
`bci_forestgeo_quadrat_agb.csv`: census 8 (~2015, in-window), Chave 2005 moist + GWDD, **whole-plot
302.5 Mg/ha** (matches published ~300), 1,250 20×20 m quadrats. **Absolute georef NOW APPLIED:**
community-standard axis-aligned affine → UTM17N/WGS84 (EPSG:32617), SW corner (625754, 1011569); CSV
now has `utm_e/utm_n/lon/lat` alongside plot-local `px_center/py_center`; centre verified 9.1516 N /
79.8509 W. Sub-degree plot rotation neglected (as in the plot's own soil/photogrammetry products) →
≤~9 m edge error. Still TODO for the user: rotate the Dryad token (it was pasted in chat).
