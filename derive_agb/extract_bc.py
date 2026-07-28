#!/usr/bin/env python
"""Derive plot-level AGB [Mg/ha] from BC FAIB ground-plot compilations (PSP, TRUE coords).

Per-tree Chojnacky-2014 allometry AGB = exp(b0 + b1 ln(dbh)) [kg], expanded to per-hectare with the
FAIB-provided PHF_TREE (already encodes plot area, plot weight, and walkthrough tree weight), summed
per plot-visit. Chojnacky is a generalized North-American allometry; BC's flora overlaps the NEON set
it was validated on. Species with no confident code mapping or no Chojnacky group are DROPPED and
reported (coverage_ok), never defaulted.

Keys: faib_tree_detail (CLSTR_ID = plot-visit) + faib_sample_byvisit (MEAS_YR) + faib_header (coords,
by SITE_IDENTIFIER). Only LIVE stems (LV_D='L'). Coordinates carry UTM_SOURCE so the coord-usability
tier can be set per plot (DGPS/RGPS/VGPS = GPS-grade; MAP/UNKNOWN/NaN = lower precision).

Run:  .venv/bin/python -u derive_agb/extract_bc.py [--min-tree-coverage 0.90] [--dbh-min-cm 4]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chojnacky2014_agb  # noqa: E402
from chojnacky_taxonomy import chojnacky_group  # noqa: E402
from bc_species import BC_CODE_TO_SCINAME  # noqa: E402

SRC = Path("/scratch3/gsialelli/AGBD-Val/data/bc-ground-plots/psp")
OUT = Path("/scratch3/gsialelli/AGBD-Val/data/derived")
GPS_SOURCES = {"DGPS", "RGPS", "VGPS", "PPP"}  # GPS-grade coordinate provenance


def sha(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-tree-coverage", type=float, default=0.90)
    ap.add_argument("--dbh-min-cm", type=float, default=4.0)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    t = pd.read_csv(SRC / "faib_tree_detail.csv",
                    usecols=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "SPECIES",
                             "DBH", "LV_D", "PHF_TREE"], low_memory=False)
    sv = pd.read_csv(SRC / "faib_sample_byvisit.csv",
                     usecols=["CLSTR_ID", "SITE_IDENTIFIER", "VISIT_NUMBER", "MEAS_YR"], low_memory=False)
    h = pd.read_csv(SRC / "faib_header.csv",
                    usecols=["SITE_IDENTIFIER", "Longitude", "Latitude", "BC_ALBERS_X", "BC_ALBERS_Y",
                             "UTM_SOURCE", "SAMPLE_ESTABLISHMENT_TYPE"], low_memory=False)
    print(f"[load ] {len(t):,} tree-obs, {len(sv):,} plot-visits, {len(h):,} sites")

    t["DBH"] = pd.to_numeric(t["DBH"], errors="coerce")
    t["PHF_TREE"] = pd.to_numeric(t["PHF_TREE"], errors="coerce")
    live = (t.LV_D == "L") & (t.DBH >= args.dbh_min_cm) & t.PHF_TREE.notna() & (t.PHF_TREE > 0)
    tl = t[live].copy()
    print(f"[filter] live stems dbh>={args.dbh_min_cm}cm w/ PHF: {len(tl):,} of {len(t):,}")

    # species -> scientific name -> Chojnacky group
    tl["sciname"] = tl["SPECIES"].map(BC_CODE_TO_SCINAME)
    uniq = tl["sciname"].dropna().unique()
    grp_lut = {n: chojnacky_group(n)[0] for n in uniq}
    tl["grp"] = tl["sciname"].map(lambda n: grp_lut.get(n) if isinstance(n, str) else None)
    mapped = tl["grp"].notna()
    print(f"[taxon] {len(uniq)} mapped scinames; stems mapped {int(mapped.sum()):,}/{len(tl):,} "
          f"({100*mapped.mean():.1f}%)")
    unm = tl.loc[~mapped, "SPECIES"].value_counts().head(10)
    if len(unm):
        print("[taxon] top unmapped BC codes (dropped):", unm.to_dict())

    tm = tl[mapped].copy()
    agb_kg = np.empty(len(tm))
    for g, idx in tm.groupby("grp").groups.items():
        rows = tm.loc[idx]
        agb_kg[tm.index.get_indexer(idx)] = chojnacky2014_agb(rows["DBH"].values, g)
    tm["agb_ha"] = agb_kg * tm["PHF_TREE"].values / 1000.0  # kg/ha -> Mg/ha contribution per tree

    # aggregate per plot-visit
    allc = tl.groupby("CLSTR_ID").size().rename("n_live_stems")
    agg = tm.groupby("CLSTR_ID").agg(agb_mg_ha=("agb_ha", "sum"),
                                     n_mapped=("agb_ha", "size")).reset_index()
    g = agg.merge(allc, on="CLSTR_ID", how="left")
    g["frac_unmapped"] = 1.0 - g["n_mapped"] / g["n_live_stems"]
    g["coverage_ok"] = g["frac_unmapped"] <= (1.0 - args.min_tree_coverage)

    g = g.merge(sv[["CLSTR_ID", "SITE_IDENTIFIER", "VISIT_NUMBER", "MEAS_YR"]], on="CLSTR_ID", how="left")
    g = g.merge(h, on="SITE_IDENTIFIER", how="left")
    g["in_window"] = g["MEAS_YR"].between(2014, 2025)
    g["coord_gps"] = g["UTM_SOURCE"].isin(GPS_SOURCES)
    g["has_coord"] = g["Latitude"].notna()

    med = g.loc[g.coverage_ok, "agb_mg_ha"].median()
    inw = g[g.in_window & g.coverage_ok & g.has_coord]
    print(f"[AGB  ] {len(g):,} plot-visits; coverage_ok {int(g.coverage_ok.sum()):,}; "
          f"in-window+coord+ok {len(inw):,}")
    print(f"[AGB  ] Mg/ha (coverage_ok): median={med:.1f} mean={g.loc[g.coverage_ok,'agb_mg_ha'].mean():.1f} "
          f"p95={g.loc[g.coverage_ok,'agb_mg_ha'].quantile(0.95):.1f} max={g.agb_mg_ha.max():.1f}")
    print(f"[AGB  ] in-window subset: median={inw.agb_mg_ha.median():.1f}  GPS-coord {int(inw.coord_gps.sum()):,}")
    assert 20 < med < 800, f"implausible BC median {med:.1f} Mg/ha"

    cols = ["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "MEAS_YR", "in_window",
            "Longitude", "Latitude", "BC_ALBERS_X", "BC_ALBERS_Y", "UTM_SOURCE", "coord_gps",
            "has_coord", "SAMPLE_ESTABLISHMENT_TYPE", "n_live_stems", "n_mapped", "frac_unmapped",
            "coverage_ok", "agb_mg_ha"]
    dest = OUT / "bc_psp_plot_agb.csv"
    g[cols].sort_values(["SITE_IDENTIFIER", "VISIT_NUMBER"]).to_csv(dest, index=False)
    print(f"[write] {dest} ({len(g):,} plot-visits)")

    prov = {
        "output": str(dest),
        "origin": "BC FAIB ground-plot compilations (PSP), psp/ subset",
        "sources_sha256": {f: sha(SRC / f) for f in
                           ("faib_tree_detail.csv", "faib_sample_byvisit.csv", "faib_header.csv")},
        "allometry": "Chojnacky, Heath & Jenkins 2014 (US generalized, applied to BC — flora overlaps)",
        "expansion": "FAIB PHF_TREE (per-ha factor incl. plot area/weight/walkthrough)",
        "filters": {"LV_D": "L (live)", "dbh_min_cm": args.dbh_min_cm},
        "species_map": "derive_agb/bc_species.py (confident BC codes only; rest dropped+reported)",
        "n_plot_visits": int(len(g)), "n_coverage_ok": int(g.coverage_ok.sum()),
        "n_in_window_coord_ok": int(len(inw)),
        "agb_median_mg_ha_coverage_ok": float(med),
        "CAVEAT": ("Chojnacky is a US generalized allometry applied to BC; coordinates are TRUE (PSP) "
                   "but precision varies by UTM_SOURCE (GPS-grade DGPS/RGPS/VGPS vs MAP/UNKNOWN) — "
                   "filter coord_gps + in_window for 10 m validation. Woodland juniper (JR), yew (TW) "
                   "and rare maple/misc codes are dropped, not defaulted."),
    }
    (OUT / "bc_psp_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov ] {OUT/'bc_psp_plot_agb.provenance.json'}")


if __name__ == "__main__":
    main()
