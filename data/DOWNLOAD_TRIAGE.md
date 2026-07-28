# Download triage — reshaped by user feedback (2026-07-23)

User directives applied to the 37-dataset catalog:
1. **Dense 10 m predictions** → wary of tree-by-tree / point-plot comparison. Prioritise dense rasters
   (airborne-lidar wall-to-wall AGB) and only aggregatable plots (≥ ~0.25 ha). GEO-TREES flagged: it is
   plot-*aggregated* at 0.25 ha (NOT tree-by-tree — 0.25 ha = a 5×5 block of 10 m pixels), so it is
   actually one of the better-matched plot references; keep but treat as aggregate points.
2. **AEF year filter** = AlphaEarth Foundations Satellite Embedding coverage **2017–2025** (annual, 10 m,
   64-band). Only generating predictions for those years → reference must overlap 2017–2025.
3. **No spaceborne** (GEDI/ICESat-2) — already excluded from catalog.

## Effect of the 2017–2025 filter on airborne-lidar AGB rasters (the best-matched class)
Most AGB lidar campaigns predate the AEF window:

| dataset | acq years | in AEF window? | variable | host / auth |
|---|---|---|---|---|
| afrisar-agb-maps-ornl1681 | 2010–2016 | **NO** | AGB | ORNL DAAC (Earthdata) |
| afrisar-lvis-gridded-ornl1775 | Feb–Mar 2016 | **NO** | AGB | ORNL DAAC (Earthdata) |
| gao-peru-carbon | 2012 | **NO** | AGC | Zenodo (open) |
| gao-sabah-carbon | 2016 | **NO** (edge) | AGC | Zenodo (open) |
| cms-lidar-agb-california-1537 | 2005–2014 | **NO** | AGB | ORNL DAAC (Earthdata) |
| cms-lidar-biomass-sonoma-1523 | 2013 | **NO** | AGB | ORNL DAAC (Earthdata) |
| cms-forest-agb-nw-usa-2443 | 2002–2016 | **NO** (edge) | AGB | ORNL DAAC (Earthdata) |
| safe-borneo-lidar | Nov 2014 | **NO** | AGC | NERC/registration |
| drc-central-africa-lidar | 2012–2015 | **NO** | AGC | journal supp |
| sustainable-landscapes-brazil | 2008–2018 | **partial** (2017–18) | AGB | ORNL DAAC (Earthdata) |
| neon-aop | 2013–present | **YES** | canopy-structure (CHM; AGB derived) | NEON portal (open) / GEE |
| g-liht | 2011–present | **YES** | canopy-structure | ORNL/NASA (Earthdata) |
| paracou-french-guiana-als | Nov 2019 (+2004,2009,2013,2015) | **YES** | canopy-structure | CEDA (registration) |
| tern-auscover-supersites | 2012–present | **YES** | AGB | TERN portal (open) |

→ Strict 2017–2025 leaves very few genuine **AGB** rasters; most survivors are canopy-structure (CHM) or
ongoing programs. This is the key decision (see questions).

## In-situ plots surviving the AEF window and openly gettable
- **usa-fia** — ~2000–present annualised; open DataMart; aggregate tier (fuzzed coords). AGB direct (NSVB).
- **neon-veg-structure** — 2013–present; open API; AGB user-derived from DBH/H. Small (0.16 ha) plots.
- **france-ign-nfi** — continuous; open (DataIFN); growing-stock-volume (needs BEF→AGB); aggregate.
- **spain-ifn** — IFN4/IFN5 partly in-window; open; pixel-ish.
- **swamp-mangrove** — post-2000; open CIFOR Dataverse; mangrove specialist.
- Restricted-coord EU NFIs / ForestPlots / ForestGEO / GFBI / TmFO / ICP: not openly downloadable.
- **tern-biomass-plot-library** — ends 2015 → mostly OUT of AEF window.

## From the older AEF catalog (agb_validation_data_catalog.md) — strong open candidate
- **AGBref (Araza et al. 2025)** — global reference AGB, epochs 2005/2010/2015/2020 (→ **2020 in-window**),
  grids 500 m / 1 / 25 km. Zenodo, CC-BY-4.0. Coarse (≥500 m) but the single best openly-downloadable
  global reference; compiled from NFI+plots+lidar. Not dense 10 m, but usable after aggregation.

## Auth reality
- `.netrc` holds **only wandb** — **no NASA Earthdata login**. All ORNL DAAC / G-LiHT (and NEON's
  Earthdata mirror) downloads are blocked without it. NEON's own API is open (no Earthdata).
- Open-now, no-auth: Zenodo (AGBref, GAO), FIA DataMart, NEON API, TERN portal, CIFOR Dataverse.
- Registration: CEDA (Paracou), NERC (SAFE).

---
## DOWNLOAD STATUS (2026-07-23, live)
**Downloaded + integrity-checked:**
- `agbref/agb-ref-v2.zip` (48 MB) — global reference AGB, Zenodo CC-BY. 2020 epoch in-window.
- `gao-sabah-carbon/` (1.2 GB) — GAO Sabah 2016 ACD + TCH, 30 m, Zenodo.
- `afrisar-agb-1681/` (4 tiles, 568 KB) — AfriSAR AGB 50 m, Gabon 2016 (Lope/Mabounie/Mondah/Rabi). **sha256 verified.**

**Earthdata pipeline:** works via `~/.netrc` (urs.earthdata.nasa.gov) + `fetch_earthdata.sh` (curl, URS cookies,
resumable, sha256 verify). Files live at data.ornldaac.earthdata.nasa.gov/protected/... resolved via CMR
granule API (collections.json?doi=... -> granules.umm_json).

**Reclassification of remaining Earthdata targets (found during resolution):**
- AfriSAR LVIS 1775 = 176 **structure** rasters (RH/PAI/canopy-cover), NOT AGB → skip for AGB focus.
- CMS NW-USA V2 "2443" → DOI did not resolve in CMR; correct ORNL id still to be found.
- Brazil 1644 (LiDAR_Forest_Inventory_Brazil) = raw lidar surveys 2008-18, huge, not an AGB raster → not
  ideal for aggregated-AGB validation; a derived-AGB Brazil product would be better if one exists.
- G-LiHT = separate portal (gliht.gsfc.nasa.gov), structure/CHM.
=> AfriSAR 1681 is the one clean in-window AGB raster from ORNL so far.

**Next (open, no-auth, no decision needed):** TERN AusCover supersites (THREDDS), NEON AOP+veg-structure
(open API), France IGN (DataIFN), Spain IFN (MITECO). Then revisit NW-USA/Brazil AGB DOIs.

---
## STRUCTURE/CHM ADDITION (2026-07-23) — relaxed criterion
User bar: product must expose **usable allometric predictors** (tree DBH+species, OR area-based
height/RH/cover/PAI for a *published* height-AGB equation). Coincident field calibration NOT required.

**Downloaded + sha256-verified:**
- `afrisar-lvis-1775/` (176 rasters, 1.6 GB) — RH50/75/95/98/100 + canopy cover + PAI + FHD, 25 m, Gabon 2016.
  Area-based lidar-AGB predictors. Pair with published LVIS/AfriSAR AGB models or with 1681 AGB.
- `afrisar-mondah-field-1580/` (5 CSVs) — Mondah tree DBH/species/biomass + **pre-aggregated plot AGB at
  0.0625 / 0.25 / 1 ha**. Allometry-ready (Chave 2014); 0.25 ha matches the 10 m-pixel aggregation support.

**Delegated (background agent running):** NEON veg structure (DP1.10098.001, tree DBH/H/species → US
allometry) + NEON AOP CHM (DP3.30015.001, height predictor), in-window 2017–2025, volume-estimated first,
complete-chain sites, serial + resumable. Output to `neon-veg-structure/` and `neon-chm/`.

**Qualify on variables but need bespoke portal access (not one-shot):**
- G-LiHT — gliht.gsfc.nasa.gov order form (CHM + lidar metrics). Not in ORNL CMR.
- Paracou / French Guiana ALS — CEDA registration (canopy height; pair with Paracou census + Chave 2014).

**Excluded here:** AfriSAR LVIS quality-mask/flightline layers count as predictors-free but were bundled in
1775; GEDI/TanDEM-X fusion products (spaceborne — user rule).

---

## SESSION UPDATE (2026-07-23, later)

### DONE — derived AGB products (`data/derived/`)
| output | source | status |
|---|---|---|
| `mondah_plot1ha_agb_derived.csv` | AfriSAR Mondah 1580 | **PASS** — Chave-2014 Eq.4 reproduces provider `m_agb` at mass-weighted 1.085e-4 |
| `GAO_Sabah_AGB_30m.tif` (+provenance) | GAO Sabah ACD 30 m | **DONE** — ACD/0.48, 77.6 M valid px, mean 149.4 Mg/ha |
| `tern_biomass_plot_library_agb.csv` (+provenance) | TERN Biomass Plot Library | **DONE, mostly UNVERIFIED — read caveats** |

**Mondah height rule (was a real bug):** provider uses **measured `h_t` where `h_t > 0`**, else modelled
`h_t_mod`. Always-`h_t_mod` left 51 trees off by up to 89%. Worst remaining per-tree residual is *4 grams*
on a 0.22 kg sapling = 2-decimal table rounding. Plot sums run 0.3–4.7% LOW because **47/6692 stems carry
the -9999 sentinel** and are excluded, while the published `agbd_ha` still counts them (summing provider
`m_agb` *with* sentinels gives NEGATIVE plot biomass, e.g. NASA01 −44 Mg/ha — proof the published table is
not a plain column sum).

**GAO nodata (was a real bug):** the raster declares `nodata=-9999` **and also carries bare NaN** in 51,646
px. Masking only the declared sentinel made every statistic `nan`; the quieter failure would have been a
mean poisoned by −9999/0.48 = **−20,831 Mg/ha**. Now masks sentinel + NaN + finite-negatives on RAW values,
with an assert. 62.85% of the grid is nodata.

### NEW — TERN Biomass Plot Library (CC-BY-4.0)
Access route (the metadata page's filenames 404; ignore them): **JRSRP GeoServer WFS**
`https://field-geoserver.jrsrp.com/geoserver/aus/wfs` → layers `aus:biolib_sitelist` (15,904 sites) and
`aus:biolib_treelist` (274,228 stems), `outputFormat=csv`. Saved to `data/tern-biomass-plot-library/`.
Note `data.tern.org.au` returns **HTTP 200 + the SPA shell for any path**, so status codes there are
worthless — always check content, and use a negative control.

Three findings that gate how this data may be used:
1. **Library ends Oct 2015** → zero overlap with AEF 2017–2025. Usable only under the 2014+ relaxation,
   and Australian woodland/savanna is fire-prone, so a 2014 plot is *not* safely comparable to a 2017 map.
2. **A support filter silently becomes a biome filter.** In-window counts by threshold:
   `≥0.04 ha n=698` · `≥0.10 ha n=612` · `≥0.125 ha n=75` · `≥0.25 ha n=25`.
   The nominal 0.25 ha target keeps 25 sites, 21 of them arid AusPlots at ~6 Mg/ha, and **drops the entire
   WA longitude range (115–140°E)**. Chose **0.10 ha** (=1000 m², ~3×3 block of 10 m px) — the natural cliff.
3. **Most kept plots are unverifiable.** The stem table covers only 2,449/15,904 sites and **none** of the
   NSW-Forestry (537) or WA (36) plots. Verification status is now a per-row column:
   - `verified_exact` **19** (TERN AusPlots — reproduce the provider to <1%)
   - `provider_disagrees` **20** (DSITI Qld + 1 AusPlot; no area denominator explains it — implied/sampled
     area scatters 0.41–100×, so the site value is not a sum of its own stem table)
   - `provider_suspect` **1** (`14058685_…`: 0.031 Mg/ha claimed over 1 ha while carrying 489 live stems
     totalling 5.8 Mg = 63 g/tree — the *provider* value is wrong, not the aggregation)
   - `no_stem_data` **573** — provider value taken on faith.
   **Filter on `verify_status` before using any of this as reference truth.**
   Also required: `condition==0` (live) for re-aggregation — including dead stems moves the median ratio
   from 1.0188 to 1.0002.

### BLOCKED — NEON now needs a free API token (user action)
NEON gated its `/api/v0/data/**` endpoints: they return `403 {"error":{"detail":"Access Denied"}}` while
`/products` and `/releases` remain anonymous (that is why scope resolution works and file listing fails).
Not a user-agent issue — curl and urllib both 403.
**Fix (2 min, free):** sign in at https://data.neonscience.org → *My Account* → **GET API TOKEN**, then
`echo '<token>' > /scratch3/gsialelli/AGBD-Val/.neon_token && chmod 600 …` (or `export NEON_TOKEN=…`).
`data/fetch_neon.py` already reads either, sends `X-API-Token`, fails loudly on 403 instead of retrying,
and is serial + resumable + size-validated. Scope already resolved: **1036 site-months, 42 sites, 2014–2025**.

### NEW — France IGN NFI (Etalab open licence) — **best dataset acquired so far**
`https://inventaire-forestier.ign.fr/dataifn/data/export_dataifn_2005_2024.zip` (68 MB) + `…_doc_2024.zip`
→ `data/france-ifn/bulk/`. (The data.gouv.fr API record lists only an HTML landing page — the real
archive links are in the `dataifn/` page HTML.) Tables: `PLACETTE.csv` (217,376 plot-visits),
`ARBRE.csv` (2.36 M trees), plus BOIS_MORT/COUVERT/ECOLOGIE/FLORE/HABITAT and 9 doc PDFs.

**Why this one matters:** coordinates are **Lambert-93 XL/YL at full 1 m precision — NOT degraded**,
unlike most EU NFIs. Annual campaigns run 2005–2024, so **2017–2024 sits entirely inside the strict AEF
window** with ~5,200–6,000 first-visit plots per year. `derive_agb/extract_france_ifn.py` →
`data/derived/france_ifn_plot_agb.csv`: **61,472 plots**, median AGB **115.6 Mg/ha**, stable 110–120
across all 11 years.

Derivation (IPCC volume route, NOT a fitted allometry — stated uncertainty, not truth):
`AGB[Mg/ha] = Σ V_i · ρ(species) · BCEF · W_i`, where `V`=stem volume m³, `W`=stems/ha expansion.
ρ for 25 species (Zanne 2009 GWDD / IPCC Tab 4.14) covers **94.1% of national volume**; 20 species alone
are 90%. BCEF 1.30 conifer / 1.40 broadleaf are **flags**, and are stand-level defaults with ~20–30%
spread — the dominant uncertainty. Unmatched species are counted, never defaulted:
`frac_volume_unknown_rho` per plot + `rho_coverage_ok` (49,160 plots ≥90% covered).

**Three traps hit, all silent:**
1. **VISITE trap (would have shipped).** Since 2015 IGN publishes the first visit *and* the 5-year
   revisit. Volume `V` is computed **only on VISITE==1** — present in 99.6% of first-visit tree records
   and **0.0%** of revisits. Keeping revisits added plots whose AGB summed to exactly zero, giving
   **median AGB = 0.00 Mg/ha for 2015–2021** while the table stayed full and nothing raised. Fixed by
   filtering `VISITE==1`; now guarded by an assert that every year's median exceeds 10 Mg/ha.
2. **ESPAR leading zeros.** `ARBRE.csv` stores `"02"`, the `espar-cdref13.csv` lookup stores `"2"`.
   Joining raw silently drops oak (02/03) and beech (09) — **34% of national volume** — while leaving a
   plausible-looking table. Normalised with `^0+(?=\d)`.
3. `HTOT` is only ~23% populated, so a height-based allometry is not an option here; the volume route is.

### Spain IFN — not yet pulled
MITECO IFN4 publishes per-province downloads + an interactive plot map; no single bulk archive found yet.
IFN4 fieldwork ran ~2008–2019 so only its tail is in-window. Lower priority than France.

### DONE — NEON veg structure → AGB (Chojnacky 2014)
Download complete: **2,798/2,798 files, 0 failures, 1.72 GB** (DP1.10098.001, 2014–2025, 42 sites).
`derive_agb/extract_neon.py` → `data/derived/neon_plot_agb.csv`: **4,150 plot-years across 35 sites**,
3,635 with ≥90% stem coverage, median AGB **144.6 Mg/ha**, years 2014–2025 (fully inside AEF window).

**Allometry: authoritative Chojnacky, Heath & Jenkins 2014 Table 5** (`derive_agb/refs/Chojnacky2014_
Forestry.pdf`, p.140), transcribed verbatim — all 35 groups (13 conifer / 18 hardwood / 4 woodland).
Verifying against the paper caught that the OLD `allometry.py` `"pine"` (-2.5356, 2.4349) and `"spruce"`
(-2.5384, 2.4814) matched **neither** real Pinus nor Picea group — approximate/wrong coefficients that
would have produced plausible wrong biomass. Replaced. Taxon→group resolver in
`derive_agb/chojnacky_taxonomy.py` uses per-species wood specific gravities from the same paper's
Tables 2–3 to pick the spg-split subgroups; **93.0% of tree stems mapped**, unmatched taxa dropped and
reported per plot (`frac_stems_unmapped`, `coverage_ok`), never defaulted.

**Traps handled:** growthForm filter to trees only (NEON tags every shrub/vine — poison ivy, wild grape,
saw palmetto were in the raw stem list); plantStatus→Live; measurementHeight 110–140 cm to keep dbh (not
root-collar basalStemDiameter, which needs the woodland drc equations); **area denominator =
`perplotperyear.totalSampledAreaTrees`** (encodes NEON's size-dependent nested-subplot design — using the
nominal 400 m² would misscale). Correctly-dropped unmapped: tropical PR/HI sites (Metrosideros, Pisonia,
Bucida, Swietenia, Guaiacum — Chojnacky is temperate N. America), woodland Juniperus (drc), Asimina
understory. Max 1377 Mg/ha is WREF old-growth Douglas-fir/hemlock (real, 6 giant stems/400 m²).
