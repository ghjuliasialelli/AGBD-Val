#!/usr/bin/env python
"""Derive plot-level AGB [Mg/ha] from Quebec MFFP PEP (placettes-echantillons permanentes).

Per-tree Chojnacky-2014 allometry AGB = exp(b0 + b1 ln(dbh_cm)) [kg], expanded with the MFFP-provided
per-tree tige_ha (stems/ha), summed per plot-measurement (id_pe_mes). Live stems only (see QC_LIVE_ETAT
-- 14/44 are DEAD, a trap). Species via essence code -> scientific name -> Chojnacky group; unmapped
dropped + reported. Coordinates + GPS flag from the 'placette' layer.

Run:  .venv/bin/python -u derive_agb/extract_quebec.py [--min-tree-coverage 0.90]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyogrio

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chojnacky2014_agb  # noqa: E402
from chojnacky_taxonomy import chojnacky_group  # noqa: E402
from quebec_species import QC_ESSENCE_TO_SCINAME, QC_LIVE_ETAT  # noqa: E402

GPKG = Path("/scratch3/gsialelli/AGBD-Val/data/quebec-pep/gpkg/PEP.gpkg")
OUT = Path("/scratch3/gsialelli/AGBD-Val/data/derived")


def sha(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-tree-coverage", type=float, default=0.90)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    a = pyogrio.read_dataframe(GPKG, layer="dendro_arbres", read_geometry=False,
                               columns=["id_pe", "id_pe_mes", "essence", "dhp", "etat", "tige_ha"])
    m = pyogrio.read_dataframe(GPKG, layer="placette_mes", read_geometry=False,
                               columns=["id_pe", "id_pe_mes", "date_sond"])
    pl = pyogrio.read_dataframe(GPKG, layer="placette", read_geometry=False,
                               columns=["id_pe", "latitude", "longitude", "in_gps"])
    print(f"[load ] {len(a):,} tree-obs, {len(m):,} plot-measurements, {len(pl):,} plots")

    a["dhp"] = pd.to_numeric(a["dhp"], errors="coerce")
    a["tige_ha"] = pd.to_numeric(a["tige_ha"], errors="coerce")
    a["etat"] = a["etat"].astype(str)
    live = a["etat"].isin(QC_LIVE_ETAT) & (a["dhp"] > 0) & a["tige_ha"].notna() & (a["tige_ha"] > 0)
    al = a[live].copy()
    print(f"[filter] live stems w/ dbh+tige_ha: {len(al):,} of {len(a):,} "
          f"(dead 14/44 excluded)")

    al["sciname"] = al["essence"].map(QC_ESSENCE_TO_SCINAME)
    uniq = al["sciname"].dropna().unique()
    lut = {n: chojnacky_group(n)[0] for n in uniq}
    al["grp"] = al["sciname"].map(lambda n: lut.get(n) if isinstance(n, str) else None)
    mapped = al["grp"].notna()
    print(f"[taxon] {len(uniq)} scinames; stems mapped {int(mapped.sum()):,}/{len(al):,} "
          f"({100*mapped.mean():.1f}%)")
    unm = al.loc[~mapped, "essence"].value_counts().head(10)
    if len(unm):
        print("[taxon] top unmapped essence codes (dropped):", unm.to_dict())

    tm = al[mapped].copy()
    dbh_cm = tm["dhp"].values / 10.0  # mm -> cm
    agb_kg = np.empty(len(tm))
    for g, idx in tm.groupby("grp").groups.items():
        rows = tm.loc[idx]
        agb_kg[tm.index.get_indexer(idx)] = chojnacky2014_agb(rows["dhp"].values / 10.0, g)
    tm["agb_ha"] = agb_kg * tm["tige_ha"].values / 1000.0  # kg/ha -> Mg/ha per tree

    allc = al.groupby("id_pe_mes").size().rename("n_live_stems")
    agg = tm.groupby("id_pe_mes").agg(agb_mg_ha=("agb_ha", "sum"),
                                      n_mapped=("agb_ha", "size")).reset_index()
    g = agg.merge(allc, on="id_pe_mes", how="left")
    g["frac_unmapped"] = 1.0 - g["n_mapped"] / g["n_live_stems"]
    g["coverage_ok"] = g["frac_unmapped"] <= (1.0 - args.min_tree_coverage)

    m["year"] = pd.to_datetime(m["date_sond"], errors="coerce").dt.year
    g = g.merge(m[["id_pe_mes", "id_pe", "year"]], on="id_pe_mes", how="left")
    g = g.merge(pl, on="id_pe", how="left")
    g["in_window"] = g["year"].between(2014, 2025)
    g["coord_gps"] = g["in_gps"] == "O"

    med = g.loc[g.coverage_ok, "agb_mg_ha"].median()
    inw = g[g.in_window & g.coverage_ok & g.latitude.notna()]
    print(f"[AGB  ] {len(g):,} plot-measurements; coverage_ok {int(g.coverage_ok.sum()):,}; "
          f"in-window+coord+ok {len(inw):,} (GPS {int(inw.coord_gps.sum()):,})")
    print(f"[AGB  ] Mg/ha (coverage_ok): median={med:.1f} mean={g.loc[g.coverage_ok,'agb_mg_ha'].mean():.1f} "
          f"p95={g.loc[g.coverage_ok,'agb_mg_ha'].quantile(0.95):.1f} max={g.agb_mg_ha.max():.1f}")
    assert 20 < med < 500, f"implausible Quebec median {med:.1f} Mg/ha"

    cols = ["id_pe", "id_pe_mes", "year", "in_window", "latitude", "longitude", "in_gps",
            "coord_gps", "n_live_stems", "n_mapped", "frac_unmapped", "coverage_ok", "agb_mg_ha"]
    dest = OUT / "quebec_pep_plot_agb.csv"
    g[cols].sort_values(["id_pe", "year"]).to_csv(dest, index=False)
    print(f"[write] {dest} ({len(g):,} plot-measurements)")

    prov = {
        "output": str(dest), "origin": "Quebec MFFP PEP (placettes-echantillons permanentes), PEP.gpkg",
        "source_sha256": sha(GPKG),
        "allometry": "Chojnacky, Heath & Jenkins 2014 (US generalized; NE-temperate flora covered)",
        "expansion": "MFFP tige_ha (stems/ha per tree)",
        "live_etat_codes": sorted(QC_LIVE_ETAT),
        "species_map": "derive_agb/quebec_species.py (tree essences only; rest dropped+reported)",
        "n_plot_measurements": int(len(g)), "n_coverage_ok": int(g.coverage_ok.sum()),
        "n_in_window_coord": int(len(inw)),
        "agb_median_mg_ha_coverage_ok": float(med),
        "CAVEAT": ("Chojnacky (US) applied to Quebec; dhp in mm/10=cm; ETAT 14/44='mort' EXCLUDED. "
                   "Coords WGS84 lat/lon with in_gps flag; filter coord_gps + in_window for 10 m use. "
                   "Saplings (dendro_gaules) not included."),
    }
    (OUT / "quebec_pep_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov ] {OUT/'quebec_pep_plot_agb.provenance.json'}")


if __name__ == "__main__":
    main()
