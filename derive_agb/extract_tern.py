#!/usr/bin/env python
"""Build a validation-ready plot AGB table from the TERN Biomass Plot Library (CC-BY-4.0).

Source: JRSRP GeoServer WFS `aus:biolib_sitelist` (15,904 sites) + `aus:biolib_treelist`
(274,228 stems). The library already carries provider AGB from published Australian allometries,
so this script's job is (a) filter to the usable subset and (b) VERIFY the provider numbers by
re-aggregating the stem table, rather than trusting them.

Two filters, both FLAGS because both are judgement calls with measured consequences:

  --year-min/--year-max   AEF embeddings are annual 2017-2025; the user relaxed this to 2014+.
                          The library ENDS in Oct 2015, so the usable window is 2014-2015 only.

  --min-area-ha           Plot support must be big enough to average over 10 m pixels. MEASURED
                          consequence of this threshold on the in-window subset:
                              >=0.04 ha  n=698  4 sources  lon 115.3-153.1  median AGB  39.9
                              >=0.10 ha  n=612  4 sources  lon 115.3-153.1  median AGB  38.5
                              >=0.125ha  n= 75  3 sources  lon 115.3-153.1  median AGB  72.5
                              >=0.25 ha  n= 25  2 sources  lon 140.6-149.7  median AGB  10.3
                          0.1 ha (=1000 m^2, ~3x3 block of 10 m pixels) is the natural cliff.
                          Going to the nominal 0.25 ha target does NOT buy cleaner data: it keeps
                          25 sites of which 21 are arid AusPlots at ~6 Mg/ha, and it DROPS THE
                          ENTIRE WESTERN AUSTRALIAN LONGITUDE RANGE (115-140 E). That is a
                          different population, not a better-supported one -- a support filter
                          that silently becomes a biome filter.

Run:  .venv/bin/python -u derive_agb/extract_tern.py
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
SRC = ROOT / "data" / "tern-biomass-plot-library"
SITES = SRC / "biolib_sitelist.csv"
TREES = SRC / "biolib_treelist.csv"
OUT = ROOT / "data" / "derived"
OUT.mkdir(exist_ok=True)


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year-min", type=int, default=2014)
    ap.add_argument("--year-max", type=int, default=2025)
    ap.add_argument("--min-area-ha", type=float, default=0.10)
    args = ap.parse_args()

    sites = pd.read_csv(SITES)
    sites["year"] = pd.to_datetime(sites["obs_time"], errors="coerce").dt.year

    n0 = len(sites)
    w = sites[(sites.year >= args.year_min) & (sites.year <= args.year_max)]
    n_win = len(w)
    w = w[w.agb_drymass_ha.notna()]
    n_agb = len(w)
    w = w[w.sampledarea_ha >= args.min_area_ha].copy()
    print(f"[filter] {n0} sites -> {n_win} in {args.year_min}-{args.year_max} "
          f"-> {n_agb} with AGB -> {len(w)} with support >= {args.min_area_ha} ha")

    # Per the playbook: assert the filtered population is non-empty and REPORT n with every metric.
    assert len(w) > 0, "no TERN sites survive the year+support filter"

    # ---- VERIFY the provider's per-hectare AGB by re-aggregating the stem table ----------------
    # We do not take agb_drymass_ha on faith. Sum per-stem agb_drymass (kg) over each site and
    # divide by the sampled area; this must reproduce the site-level column.
    trees = pd.read_csv(
        TREES,
        usecols=["obs_key", "plot", "subplot", "subplotarea_ha", "species", "ht", "condition",
                 "measurement", "diameter", "nstems", "agb_allometric_model", "agb_drymass"],
        low_memory=False,
    )
    keys = set(w.obs_key)
    t = trees[trees.obs_key.isin(keys)].copy()
    # `condition` 0 = live; 1/2/5/6 are dead/decay classes. The site-level `agb_drymass_ha` is a
    # LIVE-only figure -- including dead stems moves the median ratio from 1.0188 to 1.0002, which
    # is how this was established (whole-population ratio, not a spot check).
    t = t[t.condition == 0]
    print(f"[trees ] {len(t):,} live stems across {t.obs_key.nunique()} of {len(w)} in-window sites")

    agg = (t.groupby("obs_key")
             .agg(agb_kg_sum=("agb_drymass", "sum"),
                  n_stems=("agb_drymass", "size"),
                  n_species=("species", "nunique"),
                  mean_dbh_cm=("diameter", "mean"),
                  mean_ht_m=("ht", "mean"),
                  n_allom_models=("agb_allometric_model", "nunique"))
             .reset_index())
    m = w.merge(agg, on="obs_key", how="left")
    # kg over `sampledarea_ha` hectares -> Mg/ha
    m["agb_ha_rederived"] = m.agb_kg_sum / 1000.0 / m.sampledarea_ha
    m["verify_ratio"] = m.agb_ha_rederived / m.agb_drymass_ha

    # Every plot carries the status of its OWN check. Shipping one undifferentiated table would
    # let 573 never-checked plots inherit the credibility of 20 that reproduce exactly.
    #   verified_exact     -- stem re-aggregation reproduces the provider to <1%
    #   provider_disagrees -- stems exist but do not sum to the site value (cause unresolved:
    #                         no area denominator explains it; implied area/sampled area scatters
    #                         0.41-100x, so the site value is not a sum of its own stem table)
    #   no_stem_data       -- site-level AGB only; the tree table covers just 2,449/15,904 sites,
    #                         and NONE of the 537 NSW-Forestry or 36 WA plots. UNVERIFIABLE here.
    r = m["verify_ratio"]
    m["verify_status"] = np.where(m.agb_kg_sum.isna(), "no_stem_data",
                          np.where((r - 1).abs() < 0.01, "verified_exact", "provider_disagrees"))
    print("[verify] status breakdown:")
    for st, sub in m.groupby("verify_status"):
        print(f"          {st:20s} n={len(sub):4d}  sources={sorted(sub.source.unique())}")
    chk = m[m.verify_status != "no_stem_data"]
    print(f"[verify] of {len(chk)} checkable sites: median ratio={chk.verify_ratio.median():.4f}  "
          f"within 1%={(chk.verify_ratio.sub(1).abs()<0.01).sum()}")

    # ---- sanity bounds on the surviving population --------------------------------------------
    hi = m[m.agb_drymass_ha > 1000]
    if len(hi):
        print(f"[warn  ] {len(hi)} sites with AGB > 1000 Mg/ha (max {m.agb_drymass_ha.max():.0f}). "
              f"Tall wet-eucalypt forest does reach this, but check before using as truth.")
    # A provider value can be the broken side. One AusPlot reports 0.031 Mg/ha over 1 ha while
    # carrying 489 live stems totalling 5.8 t -- i.e. 63 g per tree. Flag it as suspect.
    bad = m[(m.verify_ratio > 10) & m.verify_ratio.notna()]
    for _, b in bad.iterrows():
        print(f"[SUSPECT] {b.obs_key}: provider {b.agb_drymass_ha:.3f} Mg/ha but "
              f"{int(b.n_stems)} live stems = {b.agb_kg_sum/1000:.1f} Mg over {b.sampledarea_ha} ha "
              f"(ratio {b.verify_ratio:.0f}x) -- provider value looks wrong, not the aggregation")
    m.loc[bad.index, "verify_status"] = "provider_suspect"

    cols = ["obs_key", "source", "project", "site", "obs_time", "year", "longitude", "latitude",
            "sampledarea_ha", "nplots", "agb_drymass_ha", "agb_ha_rederived",
            "verify_ratio", "verify_status",
            "bgb_drymass_ha", "live_basal_area_ha", "live_tree_density_ha",
            "n_stems", "n_species", "mean_dbh_cm", "mean_ht_m", "n_allom_models"]
    out = m[cols].sort_values(["source", "obs_key"])
    dest = OUT / "tern_biomass_plot_library_agb.csv"
    out.to_csv(dest, index=False)
    print(f"[write ] {dest}  ({len(out)} plots)")
    print(out.groupby("source").agg(n=("obs_key", "size"),
                                    med_area_ha=("sampledarea_ha", "median"),
                                    med_agb=("agb_drymass_ha", "median")).to_string())

    prov = {
        "output": str(dest),
        "sources": [{"path": str(p), "mtime": p.stat().st_mtime, "sha256": sha256(p)}
                    for p in (SITES, TREES)],
        "origin": "TERN Biomass Plot Library via JRSRP GeoServer WFS (aus:biolib_sitelist / aus:biolib_treelist)",
        "licence": "CC-BY-4.0",
        "agb_units": "Mg/ha dry mass, aboveground; provider allometry (per-stem agb_allometric_model)",
        "filters": {"year_min": args.year_min, "year_max": args.year_max,
                    "min_area_ha": args.min_area_ha},
        "counts": {"sites_total": n0, "in_window": n_win, "with_agb": n_agb, "kept": len(out)},
        "verification": {
            "method": ("re-aggregated live (condition==0) per-stem agb_drymass over sampledarea_ha "
                       "and compared to the provider's site-level agb_drymass_ha"),
            "status_counts": out.verify_status.value_counts().to_dict(),
            "n_checkable": int((m.verify_status != "no_stem_data").sum()),
            "median_ratio_checkable": float(chk.verify_ratio.median()),
            "note": ("The stem table covers only 2,449 of 15,904 sites and NONE of the NSW-Forestry "
                     "or WA plots, so most kept rows are 'no_stem_data' = provider value taken on "
                     "faith. Filter on verify_status before using these as reference truth."),
        },
        "caveat": ("Library ends Oct 2015, so no overlap with AEF 2017-2025; usable only under the "
                   "user's 2014+ relaxation, and only for slow-change sites. Australian woodland/"
                   "savanna is fire-prone, so a 2014 plot is NOT safely comparable to a 2017 map."),
    }
    (OUT / "tern_biomass_plot_library_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov  ] {OUT/'tern_biomass_plot_library_agb.provenance.json'}")


if __name__ == "__main__":
    main()
