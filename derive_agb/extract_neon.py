#!/usr/bin/env python
"""Derive plot-level AGB [Mg/ha] from NEON Woody Plant Vegetation Structure (DP1.10098.001).

Chain: apparentindividual (stemDiameter, growthForm, plantStatus, plotID) + mappingandtagging
(individualID -> scientificName) + perplotperyear (totalSampledAreaTrees). Apply Chojnacky et al.
2014 per-stem allometry AGB = exp(b0 + b1 ln(dbh)) [kg], grouped by taxon, then sum per plot-year
and divide by the sampled tree area to get Mg/ha.

Traps handled (each would silently corrupt the result):
- growthForm filter to TREES only. NEON tags every shrub/vine/liana in the plot; feeding poison ivy
  or wild grape a tree allometry inflates biomass. Only single/multi-bole and small trees are used.
- plantStatus filter to LIVE. Standing-dead/broken-bole stems are excluded (AGB of live biomass).
- measurementHeight: keep dbh measured near breast height (110-140 cm). basalStemDiameter (root
  collar) is a DIFFERENT convention and would need the woodland drc equations, not these.
- area denominator = totalSampledAreaTrees from perplotperyear, which already encodes NEON's
  size-dependent nested-subplot design. Using the nominal 400 m2 plot area instead would misscale
  every plot where large and small trees were sampled on different footprints.
- taxon coverage is REPORTED per plot (frac_biomass_unmapped is impossible to compute without the
  answer, so we report frac_STEMS_unmapped and the mapped biomass separately) and never defaulted.

Run:  .venv/bin/python -u derive_agb/extract_neon.py [--min-tree-coverage 0.90]
"""
from __future__ import annotations
import argparse
import glob
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chojnacky2014_agb, CHOJNACKY2014_TABLE5  # noqa: E402
from chojnacky_taxonomy import chojnacky_group  # noqa: E402

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
SRC = ROOT / "data" / "neon-veg-structure"
OUT = ROOT / "data" / "derived"
OUT.mkdir(exist_ok=True)

TREE_FORMS = {"single bole tree", "multi-bole tree", "small tree"}
LIVE = {"Live", "Live, disease damaged", "Live, physically damaged", "Live, broken bole",
        "Live, insect damaged", "Live, other damage"}


def _concat(pattern, usecols):
    fs = glob.glob(str(SRC / "**" / pattern), recursive=True)
    if not fs:
        raise SystemExit(f"no files match {pattern} under {SRC} -- is the download complete?")
    frames = []
    for f in fs:
        try:
            frames.append(pd.read_csv(f, usecols=lambda c: c in usecols, low_memory=False))
        except Exception as e:
            print(f"  [skip] {Path(f).name}: {e}")
    return pd.concat(frames, ignore_index=True), len(fs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-tree-coverage", type=float, default=0.90,
                    help="min fraction of a plot's tree stems that must map to a Chojnacky group")
    ap.add_argument("--dbh-min-cm", type=float, default=1.0)
    args = ap.parse_args()

    ind, n_ind = _concat("*apparentindividual*.csv",
                         {"individualID", "plotID", "siteID", "eventID", "growthForm",
                          "plantStatus", "stemDiameter", "measurementHeight"})
    tag, n_tag = _concat("*mappingandtagging*.csv", {"individualID", "scientificName"})
    ppy, n_ppy = _concat("*perplotperyear*.csv",
                         {"plotID", "eventID", "totalSampledAreaTrees", "plotType"})
    print(f"[load  ] {len(ind):,} individual-obs ({n_ind} files), {len(tag):,} taggings, "
          f"{len(ppy):,} plot-years")

    # De-dup taggings (a stem keeps one scientificName; later re-tags rare) and join name onto stems.
    tag = tag.dropna(subset=["individualID", "scientificName"]).drop_duplicates("individualID")
    ind = ind.merge(tag, on="individualID", how="left")

    # ---- filters, each counted so the drop is visible -----------------------------------------
    n0 = len(ind)
    ind["stemDiameter"] = pd.to_numeric(ind["stemDiameter"], errors="coerce")
    ind["measurementHeight"] = pd.to_numeric(ind["measurementHeight"], errors="coerce")
    is_tree = ind["growthForm"].isin(TREE_FORMS)
    is_live = ind["plantStatus"].isin(LIVE)
    has_dbh = ind["stemDiameter"] >= args.dbh_min_cm
    # breast-height measurement only (accept NaN height as dbh by convention; exclude clear root-collar)
    is_bh = ind["measurementHeight"].between(110, 140) | ind["measurementHeight"].isna()
    keep = is_tree & is_live & has_dbh & is_bh
    print(f"[filter] {n0:,} obs -> tree {int(is_tree.sum()):,} -> &live {int((is_tree&is_live).sum()):,} "
          f"-> &dbh {int((is_tree&is_live&has_dbh).sum()):,} -> &breast-height {int(keep.sum()):,}")
    t = ind[keep].copy()

    # ---- taxon -> Chojnacky group -------------------------------------------------------------
    uniq = t["scientificName"].fillna("Unknown").unique()
    lut = {n: chojnacky_group(n) for n in uniq}
    t["grp"] = t["scientificName"].fillna("Unknown").map(lambda n: lut[n][0])
    mapped = t["grp"].notna()
    print(f"[taxon ] {t['scientificName'].nunique()} distinct tree taxa; "
          f"{int(mapped.sum()):,}/{len(t):,} stems mapped ({100*mapped.mean():.1f}%)")
    unmapped = (t.loc[~mapped, "scientificName"].value_counts().head(12))
    if len(unmapped):
        print("[taxon ] top unmapped tree taxa (dropped, not defaulted):")
        for nm, c in unmapped.items():
            print(f"          {c:6d}  {lut.get(nm, (None,'?'))[1]:22s} {str(nm)[:42]}")

    # ---- per-stem AGB [kg] --------------------------------------------------------------------
    tm = t[mapped].copy()
    agb_kg = np.empty(len(tm))
    for g, idx in tm.groupby("grp").groups.items():
        rows = tm.loc[idx]
        agb_kg[tm.index.get_indexer(idx)] = chojnacky2014_agb(rows["stemDiameter"].values, g)
    tm["agb_kg"] = agb_kg

    # ---- aggregate to plot-year ---------------------------------------------------------------
    # stems per plot-year (all trees vs mapped) to report coverage
    allc = t.groupby(["plotID", "eventID"]).size().rename("n_tree_stems")
    mapc = tm.groupby(["plotID", "eventID"]).agg(agb_kg=("agb_kg", "sum"),
                                                 n_mapped=("agb_kg", "size")).reset_index()
    g = mapc.merge(allc, on=["plotID", "eventID"], how="left")
    g["frac_stems_unmapped"] = 1.0 - g["n_mapped"] / g["n_tree_stems"]

    ppy["totalSampledAreaTrees"] = pd.to_numeric(ppy["totalSampledAreaTrees"], errors="coerce")
    ppy = ppy.dropna(subset=["totalSampledAreaTrees"])
    ppy = ppy[ppy["totalSampledAreaTrees"] > 0].drop_duplicates(["plotID", "eventID"])
    g = g.merge(ppy[["plotID", "eventID", "totalSampledAreaTrees", "plotType"]],
                on=["plotID", "eventID"], how="inner")
    assert len(g) > 0, "no plot-years joined to a sampled-tree area -- check eventID keys"

    # kg over m2 -> Mg/ha :  (kg/1000) / (m2/10000) = kg/m2 * 10
    g["agb_mg_ha"] = (g["agb_kg"] / 1000.0) / (g["totalSampledAreaTrees"] / 10000.0)
    g["siteID"] = g["plotID"].str.slice(0, 4)
    g["year"] = g["eventID"].str.extract(r"(\d{4})")[0]  # eventID = 'vst_<SITE>_<YYYY>'
    g["coverage_ok"] = g["frac_stems_unmapped"] <= (1.0 - args.min_tree_coverage)

    # Population invariant: a NEON forest plot's live-tree AGB should be a sane, positive number.
    med = g.loc[g.coverage_ok, "agb_mg_ha"].median()
    print(f"[AGB   ] {len(g):,} plot-years; {int(g.coverage_ok.sum()):,} with >= "
          f"{args.min_tree_coverage:.0%} stem coverage")
    print(f"[AGB   ] Mg/ha (coverage_ok): median={med:.1f}  mean={g.loc[g.coverage_ok,'agb_mg_ha'].mean():.1f}  "
          f"p95={g.loc[g.coverage_ok,'agb_mg_ha'].quantile(0.95):.1f}  max={g.agb_mg_ha.max():.1f}")
    assert 20 < med < 400, f"implausible median plot AGB {med:.1f} Mg/ha -- check area units / filters"

    top = g.sort_values("agb_mg_ha", ascending=False).head(3)
    print("[check ] highest plots:", ", ".join(
        f"{r.plotID}/{r.year} {r.agb_mg_ha:.0f}Mg/ha({int(r.n_tree_stems)}st,{r.totalSampledAreaTrees:.0f}m2)"
        for r in top.itertuples()))

    cols = ["plotID", "siteID", "eventID", "year", "plotType", "totalSampledAreaTrees",
            "n_tree_stems", "n_mapped", "frac_stems_unmapped", "coverage_ok", "agb_mg_ha"]
    dest = OUT / "neon_plot_agb.csv"
    g[cols].sort_values(["siteID", "plotID", "year"]).to_csv(dest, index=False)
    print(f"[write ] {dest}  ({len(g):,} plot-years, {g.siteID.nunique()} sites)")

    prov = {
        "output": str(dest),
        "origin": "NEON DP1.10098.001 Woody Plant Vegetation Structure (basic package)",
        "n_source_files": {"apparentindividual": n_ind, "mappingandtagging": n_tag,
                           "perplotperyear": n_ppy},
        "allometry": "Chojnacky, Heath & Jenkins 2014 Forestry 87:129, Table 5 (forest dbh groups)",
        "allometry_ref": "derive_agb/refs/Chojnacky2014_Forestry.pdf",
        "n_chojnacky_groups_used": int(tm["grp"].nunique()),
        "filters": {"growthForm": sorted(TREE_FORMS), "plantStatus": "Live*",
                    "measurementHeight_cm": "110-140 or NaN", "dbh_min_cm": args.dbh_min_cm},
        "area_denominator": "perplotperyear.totalSampledAreaTrees (NEON nested-subplot design)",
        "min_tree_coverage": args.min_tree_coverage,
        "n_plot_years": int(len(g)), "n_coverage_ok": int(g.coverage_ok.sum()),
        "n_sites": int(g.siteID.nunique()),
        "agb_median_mg_ha_coverage_ok": float(med),
        "CAVEAT": ("Chojnacky is a TEMPERATE North-American generalized allometry; NEON tropical "
                   "sites (Puerto Rico: GUAN/LAJA, and palms) are largely unmapped and excluded, "
                   "not defaulted. Woodland juniper/pinyon/mesquite (drc species) are dropped. "
                   "Filter on coverage_ok before use."),
    }
    (OUT / "neon_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov  ] {OUT/'neon_plot_agb.provenance.json'}")


if __name__ == "__main__":
    main()
