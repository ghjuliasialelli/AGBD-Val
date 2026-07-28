# PROJECT STATE — AGB reference/validation catalog

> **2026-07-27 UPDATE — ACQUISITION + AGB-DERIVATION PHASE (large).** Went well beyond the catalog:
> downloaded real reference data and DERIVED plot/pixel AGB [Mg/ha] for many sources. Everything below
> is on disk under `/scratch3/gsialelli/AGBD-Val/`. Per the machine rule this file (in `/scratch3`) is
> the project memory. Companion docs: **`catalog/AGB_METHODS.md`** (exact per-source AGB method +
> citations), **`catalog/COORD_TIER_PARTITION.md`** (Tier A pixel / Tier B aggregate split + fetch/derive
> status), **`data/ACCESS_REQUESTS.md`** (ready-to-send letters for gated sources), **`data/DOWNLOAD_TRIAGE.md`**.
>
> ### Derived AGB products — `data/derived/` (each has a `*.provenance.json`: source sha256 + params)
> | product | n | method | tier |
> |---|---|---|---|
> | `france_ifn_plot_agb.csv` | 61,472 | IPCC volume→biomass (V·ρ·BCEF·W); VISITE==1 + ESPAR-zero traps | A |
> | `spain_ifn4_plot_agb.csv` | 50,560 (43 prov) | Ruiz-Peinado 2011/2012 by IFN code; concentric-plot expansion; per-prov datum | A ("approx" coords; mostly pre-2014) |
> | `quebec_pep_plot_agb.csv` | 50,105 | Chojnacky 2014 × tige_ha; etat 14/44=DEAD excluded | A (11,262 in-window GPS) |
> | `bc_psp_plot_agb.csv` | 23,942 | Chojnacky 2014 × PHF_TREE; coords in faib_header.csv | A (1,593 in-window GPS) |
> | `neon_plot_agb.csv` | 4,150 | Chojnacky 2014 Table 5 | A |
> | `bci_forestgeo_quadrat_agb.csv` | 1,250 | Chave 2005 moist + GWDD; whole-plot 302 Mg/ha (validates) | A (coords plot-local; abs georef TODO) |
> | `slb_brazil_transect_agb.csv` | 309 (14 sites) | Chave 2014 Eq4 + WSD/GWDD; **use site_plausible=True (11/14)** | A partial |
> | `colombia_ifn_conglomerado_agb.csv` | 283 | Chave 2005 moist + GWDD; DBH from basal area | **B (10.6 km coords)** |
> | `mondah_plot1ha_agb_derived.csv` | 15 | Chave 2014 Eq4 — VALIDATED to 1e-4 | A |
> | `tern_biomass_plot_library_agb.csv` | 612 | provider agb re-aggregated | B (pre-window) |
> | `fia_public_plot_agb.csv` | **IN PROGRESS** | FIA precomputed DRYBIO_AG×TPA; PUBLIC-LAND subset (no swap) | **B (fuzzed ~0.8km)** |
> | rasters: `GAO_Sabah_AGB_30m.tif`, `GAO_Peru_AGB_100m.tif`, `SLB_Paragominas_AGB_50m.tif` | — | ACD÷0.48 (carbon→AGB), nodata masked on raw | A |
>
> ### FIA — running DETACHED (survives session exit)
> `data/fetch_fia.py`, launched via `setsid` (own session, ppid=1), **resumable per state** (skips
> `data/fia/by_state/<ST>.csv` that exist), writes the national `fia_public_plot_agb.csv` + provenance
> ITSELF at the end. All 51 states/PR; public-land only (OWNGRPCD 10/20/30). **TODO after it finishes:**
> re-run to retry states whose TREE download failed (saw `[OR] FAIL: not a zip` — a partial raw zip;
> `dl()` won't re-fetch a nonzero-but-corrupt zip, so `rm data/fia/raw/<ST>_TREE.zip` before re-running).
> To check: `tail data/logs/fia.log`; `ls data/fia/by_state | wc -l`.
>
> ### Code — `derive_agb/`
> `allometry.py` (Chave2014 Eq4/Eq7, **Chave2005 moist**, Chojnacky2014 Table5, acd_to_agb) ·
> `chojnacky_taxonomy.py` · `bc_species.py` · `quebec_species.py` · `spain_biomass.py` (RP2011/2012, 24 sp) ·
> `wood_density.py` (Global Wood Density DB Zanne2009 via R BIOMASS → `data/wood-density/`, sp→genus→family→region) ·
> extract_{mondah,gao_sabah,carbon_raster,bc,quebec,colombia,slb,bci,spain}.py.
> Fetchers: `data/fetch_tier_a.py`, `fetch_fia.py`, `fetch_neon.py`, `fetch_earthdata.sh`, `spain_ifn4_files.txt`.
>
> ### Access mechanics learned (reusable)
> - **Dryad** gates downloads (API 401 needs bearer token + Cloudflare on web path). BCI pulled with a
>   user-supplied token in `.dryad_credentials` (600). **SECURITY: that token was pasted in chat → tell
>   user to ROTATE it.** NEON token in `.neon_token` (600). Never write `/home`.
> - **FIA DataMart**: `https://apps.fs.usda.gov/fia/datamart/CSV/<ST>_<PLOT|COND|TREE>.zip`. Biomass
>   precomputed (post-2023 = NSVB, ~15% > old CRM). OWNGRPCD/COND_STATUS_CD in COND; LAT/LON/MEASYEAR in PLOT.
> - **Spain IFN4** (MITECO): per-province `.accdb` under `.../dam/miteco/.../inventarios-nacionales/`
>   (no clean naming — list in `data/spain_ifn4_files.txt`). Read with `access-parser` (pip) NOT ogr
>   (no MDB driver). **TRAP: access-parser drops PCMayores.Provincia → text cols shift** → resolve
>   Estadillo (join) + Especie (species) BY CONTENT (Especie by overlap with real IFN codes, since
>   Subclase/order cols are also 3-digit). **TRAP: per-province datum** ED50/ETRS89/WGS84 → EPSG.
> - **ORNL DAAC**: CMR `granules.json?concept_id=…` + `~/.netrc` (urs.earthdata). Zenodo API for GAO.
>
> ### Remaining TODOs
> 1. FIA: finish + retry failed states (OR…), then update AGB_METHODS.md + COORD_TIER_PARTITION.md.
> 2. BCI absolute georef: apply verified UTM17N SW-corner + plot bearing to PX/PY (currently plot-local).
> 3. SLB: 3 flagged sites (FNA/SAN/FN) need per-file plot areas (provider shapefiles can't give them).
> 4. Spain: Extremadura (combined 2-prov DB) skipped; 4 Andalucía provinces still IFN3; coords "approx"
>    + IFN4 fieldwork ~2008–2019 (no per-tree date) so mostly pre-window — it's biome-fill, not in-window A.
> 5. Gated true-coord sources (USER ACTION): send `data/ACCESS_REQUESTS.md` letters — Estonia & Sweden
>    (documented YES on exact coords), Canada NFI DUA, Argentina INBN2, Mexico INFyS. FIA SDS is PAUSED.
> 6. Next phase (not started): sample AEF embeddings at plot coords per year → validation X/Y pairs
>    (reproject to AEF tile CRS, sample pixel CENTRES, mask AEF nodata on raw values). Watch circularity:
>    GEO-TREES/ForestPlots/ForestGEO/BCI may have trained CCI/GEDI — confirm before use.

> **2026-07-23 UPDATE — quota freed; deferred actions DONE.** `/home/gsialelli` is writable again.
> The memory entry now exists at
> `/home/gsialelli/.claude/projects/-scratch3-gsialelli-AGBD-Val/memory/agbd-val-catalog.md`
> (with a `MEMORY.md` pointer). The audit has been run: `audit_catalog.py --rebuild-csv` →
> **PASS, all invariants hold**; CSV regenerated from the authoritative JSON so parity is guaranteed
> (37 rows). `--check-urls` → 34/37 resolve 200; 3 benign warnings (germany-bwi SSL cert chain,
> switzerland-lfi HTTP 429, uk-nfi HTTP 403 bot-block — all live sites, not dead links).

---

Building `/scratch3/gsialelli/AGBD-Val` into a **validation testbed for AGB maps**. First deliverable
(agreed with user 2026-07-23): a **metadata catalog** of independent AGB *reference* data.

**Scope (user's choices):** global; **in-situ plots + airborne-lidar AGB only**. Spaceborne lidar
(GEDI/ICESat-2) and gridded intercomparison maps (CCI, Spawn, Avitabile) deliberately EXCLUDED as
non-independent — addable later as separate `category` values.

**Deliverables under `/scratch3/gsialelli/AGBD-Val/catalog/`:** ALL WRITTEN (2026-07-23)
- `README.md` — DONE (schema + scope + validation-trap rationale).
- `agb_reference_catalog.json` — DONE (authoritative; 37 datasets, full metadata).
- `agb_reference_catalog.csv` — DONE (hand-authored greppable view; run `audit_catalog.py --rebuild-csv`
  once the shell works to guarantee it matches the JSON — hand-authored, so verify parity).
- `SOURCES.md` — DONE (provenance URL/DOI + verified date; flags unconfirmed DOIs/coords).
- `audit_catalog.py` — DONE (metadata-only invariant checker; exits non-zero; --rebuild-csv, --check-urls).
- `../CLAUDE.md` — DONE (project brief + the pf-pc28 write-location rule).

**STILL TO RUN (needs shell):** `python -u audit_catalog.py --rebuild-csv` to validate invariants and
regenerate the CSV from JSON. Optionally `--check-urls`.

**NEW MACHINE RULE (pf-pc28, user 2026-07-23):** ALWAYS write to `/scratch3/gsialelli`, NEVER under
`/home/gsialelli`. Recorded in `../CLAUDE.md`. Fix for the quota deadlock the user will run in a real
terminal: `mv ~/.claude /scratch3/gsialelli/dotclaude && ln -s /scratch3/gsialelli/dotclaude ~/.claude`
(or set `CLAUDE_CONFIG_DIR` for zero /home footprint), then relaunch — unblocks shell + memory.

**~40 datasets, all web-verified 2026-07-23** via 3 research agents. Full verified per-dataset metadata
(provider, coverage, units, temporal, coord availability, access, portal URL, DOI, caveats) is in the
three agent results in the originating conversation. Datasets:
- In-situ plot networks: GEO-TREES, ForestPlots.net (+RAINFOR/AfriTRON/T-FORCES/PPBio), Smithsonian
  ForestGEO, TmFO, GFBI, NEON veg structure, TERN Biomass Plot Library, SWAMP mangroves, ICP Forests.
- NFIs: USA FIA, France (IGN), Spain (IFN), Sweden (SLU), Finland (Luke), Germany (BWI), Switzerland
  (WSL/LFI), Norway (NIBIO), Italy (INFC), UK (Forest Research), Canada, Poland (WISL), Netherlands
  (NBI), Australia (TERN/AusPlots).
- Airborne-lidar AGB: Sustainable Landscapes Brazil (EMBRAPA/ORNL), AfriSAR AGB maps (ORNL 1681),
  AfriSAR LVIS gridded (ORNL 1775), NEON AOP (structure; AGB user-derived), NASA G-LiHT (structure),
  NASA CMS California (1537), CMS Sonoma (1523), CMS NW-USA V2 (2443), CMS Tri-State + RGGI, GAO Peru
  carbon (zenodo 4626309), GAO Sabah carbon (zenodo 4549461), SAFE/Borneo, Paracou/French Guiana ALS
  (CEDA/zenodo), TERN AusCover SuperSites, DRC + Central-Africa reference AGB.

**Headline design decision — `coord_usability_tier` column** (pixel | aggregate | restricted):
- Pixel-usable open: France (±700m node), Spain (plot UTM; ED50→ETRS89 ~200m shift), TERN, GEO-TREES
  (≥0.25ha aggregated), NEON (m-level uncertainty), SWAMP, all open airborne-lidar rasters. Canada
  partial (exact coords on request).
- Public but coarsened (aggregate only): US FIA (fuzzed ±0.5–1mi + private-plot swap; publishes tree
  dry-biomass directly), Germany BWI (1km INSPIRE grid).
- Restricted/on-application: Sweden, Finland (open product is a MODELED 16m raster = circular; true
  plots restricted), Switzerland, Norway, Italy (open tree data, no precise coords), Poland, UK (open
  woodland polygons only), + raw tiers of ForestPlots/ForestGEO/GFBI/TmFO/ICP.

**Data-accuracy flags to encode as caveats:**
- carbon-not-biomass: GAO Peru/Sabah + most DRC = Mg C/ha → `variable=AGC`, convert ÷≈0.47 (silent
  factor-~2 halving trap).
- not-wall-to-wall: Sustainable Landscapes Brazil, G-LiHT, NEON AOP, DRC national map = transects/
  swaths/structure-only — a site name is not a geometry; assert per-axis overlap + n>0.
- volume-not-biomass: most EU NFIs publish m³/ha growing stock (needs allometric/BEF conversion);
  FIA/INFC/Canada/Australia give biomass directly.
- unconfirmed DOIs: Sustainable Landscapes Brazil, CMS Tri-State/RGGI, some TERN site records — leave
  `doi` blank + SOURCES.md note; do NOT transcribe a maybe-wrong DOI.

**Schema** (in `catalog/README.md`): id, name, category, subtype, provider, coverage_scope, region,
variable, units, representation, support_size, temporal_coverage, geometry_type, native_crs,
coord_availability, n_records_or_area, access, license, format, portal_url, doi, citation_short,
verified, validation_caveats (+ derived coord_usability_tier).

**Later phase (needs shell + separate approval):** `validate.py` — for a (map, reference) pair:
reproject ref→map CRS, assert per-axis intersection + `assert n>0`, match variable/units, aggregate to
coarser support_size, sample map at pixel centres (handle south-up transform.e>0), mask nodata on raw
values, record mtime/hash of every source raster a number came from.

**BLOCKER (2026-07-23):** `/home/gsialelli` volume is OVER QUOTA (`EDQUOT: mkdir …session-env/…`).
Blocks the shell (no session-env → no Bash), the plan file, AND memory writes. `/scratch3` writes work.
Fix: clear `/home/gsialelli/.claude/session-env/*` or raise the home quota → unblocks shell, downloads,
audit run, plan file, and memory. No project `.md` brief found in repo root (couldn't list dir due to
blocker); following global `~/.claude/CLAUDE.md` playbook as ruleset.

**Next action when user returns:** free home quota (or approve writing to /scratch3), then write
CSV/JSON/SOURCES/audit script, and copy this file into the real memory store.
