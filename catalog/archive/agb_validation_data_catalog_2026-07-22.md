# AGB validation & reference data — a catalog for the AEF temporal-AGB work

Compiled 2026-07-22. Purpose: what to use to validate (a) **absolute** per-year AGB, (b) **real ΔAGB / temporal** change, and (c) to build **stand-age chronosequence** supervision. The hard one is (b): almost nothing gives repeated AGB of the *same* ground over years, so those sources are called out explicitly.

Tags: `[abs]` absolute-AGB validation · `[ΔAGB]` genuine repeated-measure change · `[age]` disturbance/stand-age for chronosequence · `[compare]` map-to-map only (not ground truth).

---

## A. Curated / harmonised reference datasets (closest to plug-and-play)

- **AGBref (Araza et al., 2025/26)** `[abs]` `[compare]` — Global reference AGB compiled from **45 sources (64% NFI, 20% research plots, 18% airborne LiDAR)**, plots 1996–2022 (mean 2009), sizes 0.02–25 ha (median 0.2 ha). Provided at **four epochs (2005/2010/2015/2020)** and four grids (**500 m, 1, 10, 25 km**), with measurement / within-pixel / temporal-adjustment uncertainty and five quality filters. Zenodo, CC-BY-4.0. **Caveat for you:** Europe-heavy (67% of plots; boreal/temperate-conifer under-sampled), and the epoch-to-epoch change is partly **IPCC Tier-1 growth-adjusted**, so treat its multi-epoch values as absolute snapshots, *not* as independent ΔAGB truth (using them to validate growth would be partly circular). Best use: absolute validation at ≥500 m across epochs. https://doi.org/10.21203/rs.3.rs-8211898/v1
- **Forest Observation System (FOS)** `[abs]` — Schepaschenko et al. 2019, *Sci Data*. Harmonised **~1-ha in-situ plots** worldwide, purpose-built as a biomass reference for EO. Good at the footprint/hectare support you'd validate a 10 m product against after aggregation. https://www.nature.com/articles/s41597-019-0196-1 · portal: forest-observation-system.net
- **GEO-TREES — Forest Biomass Reference System** `[abs]` (some `[ΔAGB]`) — GEO initiative building *traceable* reference AGB "from tree to satellite": long-term forest **supersites** (drawing on ForestGEO, RAINFOR, AfriTRON, …) each with **tree-by-tree inventory + airborne + terrestrial LiDAR**, explicitly to calibrate/validate **GEDI, BIOMASS, NISAR**. Open, expanding, and the sites with repeat censuses give change too. This is the current gold standard for site-level reference. https://geo-trees.org · https://earthobservations.org/groups/forest-biomass-reference-system-from-tree-by-tree-inventory-data
- **CEOS WGCV LPV Biomass Validation Protocol (2021)** — not data but the community **good-practice** doc + curated reference-data pointers; align your validation design to it for credibility. https://lpvs.gsfc.nasa.gov/PDF/CEOS_WGCV_LPV_Biomass_Protocol_2021_V1.0.pdf · reference list: https://lpvs.gsfc.nasa.gov/AGB/AGB_references.html
- **LiDAR reference AGB maps — tropical South Asia & Central Africa** `[abs]` — Nature *Sci Data* 2024; ready-made ALS-derived reference AGB over tropical regions. https://www.nature.com/articles/s41597-024-03162-x

## B. In-situ plot networks (raw censuses → real ΔAGB at plot scale)

- **ForestPlots.net** `[ΔAGB]` `[abs]` — umbrella for **RAINFOR** (Amazonia), **AfriTRON** (Africa), **T-FORCES**; long-term *re-censused* permanent plots → genuine AGB increment/mortality over time. Access is governed/collaborative, not fully open. https://forestplots.net
- **ForestGEO (Smithsonian/CTFS)** `[ΔAGB]` `[abs]` — large plots (up to 50 ha), ~5-yr repeat censuses → true stand-level ΔAGB. https://forestgeo.si.edu
- **National Forest Inventories** `[ΔAGB]` `[abs]` — **US FIA** is the most usable: remeasured panels + the new **NSVB** biomass models, with net growth/removals/mortality in FIADB → real ΔAGB, openly downloadable. European NFIs similar but access varies. https://research.fs.usda.gov/programs/fia/nsvb
- **TmFO (Tropical managed Forests Observatory)** `[ΔAGB]` `[age]` — logging/disturbance-recovery plot network; directly relevant to the recovery-slope story.

## C. Airborne / terrestrial LiDAR (mid-scale wall-to-wall AGB; repeat = ΔAGB)

- **NEON Airborne Observation Platform** `[ΔAGB]` `[abs]` — annual airborne lidar + coincident field plots across US sites, fully open; **revisits give real multi-year AGB change** — one of the few clean ΔAGB sources. https://www.neonscience.org/data-collection/airborne-remote-sensing
- **Sustainable Landscapes Brazil (EMBRAPA/USFS)** `[ΔAGB]` `[abs]` — airborne-lidar transects across Amazonia, some **repeat-flown**; public. Plus multitemporal-lidar logging studies (e.g. *RS* 11(6):709) for disturbance/recovery. Amazon biomass map: https://www.nature.com/articles/s41597-023-02575-4
- **National repeat-ALS programs** `[ΔAGB]` — Nordic/other NFIs fly ALS on cycles; where two epochs exist you get ΔAGB. Access national.

## D. Spaceborne AGB products (cross-comparison / weak reference — not ground truth)

- **GEDI L4A / L4B** — L4A footprint AGBD (~25 m footprints; your supervision source); **L4B** 1 km gridded mean AGBD for coarse comparison. `[compare]`
- **ESA CCI Biomass v5** `[compare]` — global maps for **2010, 2015–2021 (~100 m)**; multi-epoch, so tempting for temporal comparison, but its *own* year-to-year change is uncertain — compare, don't treat as truth. https://climate.esa.int/en/projects/biomass/data/ · "Past-decade AGB change from four global maps": https://www.sciencedirect.com/science/article/pii/S1569843223000961
- **ESA BIOMASS (P-band)** `[compare]` (future gold standard) — launched Apr 2025, now **live with L1/L2A open**; tomographic/PolInSAR, tropical-forest AGB & disturbance the headline products (still upstream of the L2 AGB map). Worth tracking as an independent tropical AGB/change reference as products mature. https://earth.esa.int/eogateway/missions/biomass
- **NISAR (NASA-ISRO, L-band)** `[compare]` — launched 2025, biomass-sensitive; forest disturbance/structure products upcoming. https://www.eoportal.org/satellite-missions/nisar
- **Legacy pantropical maps** `[compare]` — Saatchi 2011, Baccini, Harris et al. 2021 carbon-flux — comparison context only.

## E. Disturbance / stand-age references (build the age→AGB chronosequence, per Lever 2)

- **Hansen Global Forest Change** `[age]` — annual tree-cover **loss year** 2000→ (30 m); gives time-since-disturbance = stand age for regrowth. https://glad.earthengine.app/view/global-forest-change
- **JRC Tropical Moist Forest (TMF)** `[age]` — annual deforestation/degradation/**regrowth** (30 m), and the companion **pan-tropical regrowth *age* dataset** (Nature Ecol Evol 2025) — a ready map of regeneration age, ideal for the age-curve. https://forobs.jrc.ec.europa.eu/TMF/data · age: https://www.nature.com/articles/s41559-025-02721-8
- **Fire**: MTBS (US severity), GABAM / MODIS-VIIRS burned area, national fire perimeters. `[age]`
- **DETER / PRODES** (Amazon) `[age]` — deforestation timing.

## F. Allometry (to compute/curate plot AGB and quantify label error)

- **Chave et al. 2014** pantropical AGB allometric models — the standard. https://stri-sites.si.edu/docs/publications/pdfs/Chave-et-al_2014_GlobChangeBio-new_biomass_equations.pdf
- **BIOMASS R package** (Réjou-Méchain et al. 2017) — implements Chave 2014 with full **uncertainty propagation** (diameter, wood density, allometry) — use it so plot-AGB error bars are honest.
- **Tallo (Jucker et al. 2022)** — global tree allometry & crown-architecture DB, ~498k trees (H–D–crown). https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.16302
- **BAAD (Falster et al. 2015)** — biomass & allometry of woody plants (destructive harvests).
- **Global wood density DB** (Zanne/Chave); **GlobAllomeTree** platform; **US NSVB** national biomass models.

---

## Recommendations for this project (by need)

1. **Absolute per-year AGB validation** → AGBref (≥500 m, multi-epoch) + FOS/GEO-TREES (site/hectare) + GEDI L4A held-out. Match analysis unit to each footprint.
2. **Real ΔAGB / recovery-slope validation (the scarce, decisive one)** → **repeat ALS (NEON, Sustainable Landscapes Brazil, national) + NFI remeasurement (FIA) + ForestPlots/ForestGEO censuses.** These are the only true repeated-measure AGB. Sparse but gold — reserve them strictly for temporal validation, not training.
3. **Stand-age chronosequence supervision (scalable substitute for repeats)** → Hansen loss-year + **JRC TMF regrowth-age** + fire perimeters, paired with GEDI AGB, to estimate AGB(age) and its slope.
4. **Independent map comparison** → ESA CCI Biomass (multi-epoch), and watch **ESA BIOMASS** + **NISAR** as they deliver L2 AGB.

**Two cautions:** (i) don't use AGBref's epoch differences as ΔAGB truth — they're partly growth-model-adjusted (circular for validating growth); (ii) mind support/footprint mismatch at 10 m (GEDI ~25 m; plots 0.02–25 ha) — aggregate to the reference's support before comparing.
