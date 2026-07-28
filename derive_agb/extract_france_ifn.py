#!/usr/bin/env python
"""Derive plot-level AGB [Mg/ha] from the French NFI (IGN inventaire forestier, Etalab open licence).

Source: `data/france-ifn/bulk/` (export_dataifn_2005_2024.zip). 217,376 plot-visits 2005-2024 with
FULL-PRECISION Lambert-93 coordinates (XL/YL, 1 m spacing -- NOT fuzzed, unlike most EU NFIs), and
2.36 M tree records. In the 2014-2024 window: 88,694 plots / 1.60 M trees.

DERIVATION AND ITS HONEST STATUS
--------------------------------
IGN does NOT publish per-tree biomass. It publishes stem VOLUME `V` [m3] and a per-hectare expansion
weight `W` [stems/ha]. So:

    AGB [Mg/ha] = SUM_i ( V_i [m3] * rho_species [t/m3] * BCEF ) * W_i [1/ha]

`rho` is basic wood density (oven-dry mass / green volume) and `BCEF` expands merchantable stem
biomass to total aboveground biomass (branches, bark, top). This is the IPCC volume-to-biomass route,
NOT a fitted allometry, and it is a FIRST-ORDER estimate: BCEF in particular is a stand-level default
with ~20-30% spread. Treat the output as reference data with a stated uncertainty, not as truth.

Both rho and BCEF are FLAGS/tables, never buried constants (playbook: "a guard tuned for one use case
will silently break another"). Species with no density entry are NOT silently given a mean value --
they are counted, reported, and their volume share per plot is recorded in `frac_volume_unknown_rho`
so a downstream user can drop under-covered plots.

Species-code trap: ESPAR codes carry LEADING ZEROS in ARBRE.csv ("02") but the lookup table
espar-cdref13.csv stores them unpadded ("2"). Joining without normalising silently loses the three
largest species in France -- oak (02/03) and beech (09) alone are 34% of national volume.

Run:  .venv/bin/python -u derive_agb/extract_france_ifn.py [--year-min 2014] [--bcef-broadleaf 1.4]
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
SRC = ROOT / "data" / "france-ifn" / "bulk"
OUT = ROOT / "data" / "derived"
OUT.mkdir(exist_ok=True)

# Basic wood density [t oven-dry / m3 green volume] for the species covering ~94% of French NFI
# volume. Sources: Global Wood Density Database (Zanne et al. 2009 / Chave et al. 2009) and IPCC
# 2006 GL Vol.4 Table 4.14 European values. Keyed by ESPAR code (normalised, no leading zeros).
# `conif` drives which BCEF applies. Anything absent -> counted as unknown, never defaulted.
WOOD_DENSITY = {
    # code: (rho, is_conifer, name)
    "2":  (0.57, False, "Quercus robur"),
    "3":  (0.57, False, "Quercus petraea"),
    "5":  (0.69, False, "Quercus pubescens"),
    "6":  (0.80, False, "Quercus ilex"),
    "9":  (0.58, False, "Fagus sylvatica"),
    "10": (0.48, False, "Castanea sativa"),
    "11": (0.63, False, "Carpinus betulus"),
    "14": (0.58, False, "Robinia pseudoacacia"),
    "19": (0.35, False, "Populus sp."),
    "24": (0.37, False, "Populus tremula"),
    "12V": (0.53, False, "Betula pendula"),
    "13G": (0.45, False, "Alnus glutinosa"),
    "15S": (0.53, False, "Acer pseudoplatanus"),
    "17C": (0.56, False, "Fraxinus excelsior"),
    "21C": (0.60, False, "Acer campestre"),
    "22M": (0.49, False, "Prunus avium"),
    "51": (0.44, True,  "Pinus pinaster"),
    "52": (0.42, True,  "Pinus sylvestris"),
    "53CO": (0.44, True, "Pinus nigra var. corsicana"),
    "54": (0.44, True,  "Pinus nigra"),
    "57A": (0.45, True, "Pinus halepensis"),
    "61": (0.38, True,  "Abies alba"),
    "62": (0.40, True,  "Picea abies"),
    "63": (0.47, True,  "Larix decidua"),
    "64": (0.45, True,  "Pseudotsuga menziesii"),
}


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def norm_espar(s: pd.Series) -> pd.Series:
    """'02' -> '2', '53CO' -> '53CO'. Strips leading zeros only from the numeric prefix."""
    s = s.astype(str).str.strip().str.upper()
    return s.str.replace(r"^0+(?=\d)", "", regex=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year-min", type=int, default=2014)
    ap.add_argument("--year-max", type=int, default=2024)
    ap.add_argument("--bcef-conifer", type=float, default=1.30,
                    help="stem-volume -> total AGB expansion, conifers (IPCC-order default)")
    ap.add_argument("--bcef-broadleaf", type=float, default=1.40,
                    help="stem-volume -> total AGB expansion, broadleaves (IPCC-order default)")
    ap.add_argument("--min-rho-coverage", type=float, default=0.90,
                    help="min fraction of plot volume with a known density to mark a plot usable")
    args = ap.parse_args()

    plc = pd.read_csv(SRC / "PLACETTE.csv", sep=";", encoding="utf-8-sig", low_memory=False,
                      usecols=["CAMPAGNE", "IDP", "XL", "YL", "VISITE"])
    arb = pd.read_csv(SRC / "ARBRE.csv", sep=";", encoding="utf-8-sig", low_memory=False,
                      usecols=["CAMPAGNE", "IDP", "ESPAR", "C13", "HTOT", "V", "W"])

    yr = (args.year_min, args.year_max)
    plc = plc[plc.CAMPAGNE.between(*yr)].copy()
    arb = arb[arb.CAMPAGNE.between(*yr)].copy()
    for c in ("V", "W", "C13", "HTOT"):
        arb[c] = pd.to_numeric(arb[c], errors="coerce")
    print(f"[scope ] {yr[0]}-{yr[1]}: {len(plc):,} plot-visits, {len(arb):,} tree records")

    # VISITE TRAP (this silently produced a median AGB of 0.00 Mg/ha for 2015-2021).
    # Since 2015 IGN publishes both the first visit and the 5-year REVISIT of each plot. Volume `V`
    # is computed ONLY on the first visit: V is present in 99.6% of VISITE==1 tree records and in
    # 0.0% of VISITE==2. Keeping revisits does not add data -- it adds plots whose AGB sums to
    # exactly zero, which halves the median without emptying the table or raising anything.
    plc = plc[plc.VISITE == 1].copy()
    arb = arb.merge(plc[["CAMPAGNE", "IDP"]].drop_duplicates(), on=["CAMPAGNE", "IDP"], how="inner")
    print(f"[visite] VISITE==1 only: {len(plc):,} plots, {len(arb):,} tree records "
          f"(V present in {100*arb.V.notna().mean():.1f}% of them)")

    arb["espar_n"] = norm_espar(arb.ESPAR)
    dens = pd.DataFrame(
        [(k, v[0], v[1], v[2]) for k, v in WOOD_DENSITY.items()],
        columns=["espar_n", "rho", "is_conifer", "sci_name"])
    arb = arb.merge(dens, on="espar_n", how="left")

    known = arb.rho.notna()
    vol = (arb.V * arb.W).fillna(0.0)
    print(f"[rho   ] {known.sum():,}/{len(arb):,} tree records matched a density "
          f"({100*vol[known].sum()/vol.sum():.1f}% of volume). "
          f"{arb.loc[~known, 'espar_n'].nunique()} species codes unmatched.")
    # Loud about what is NOT covered -- a silent 6% would look like completeness.
    miss = (arb.loc[~known].assign(vw=vol[~known]).groupby("espar_n").vw.sum()
            .sort_values(ascending=False).head(8))
    if len(miss):
        print("[rho   ] largest unmatched codes by volume: "
              + ", ".join(f"{k}={100*v/vol.sum():.2f}%" for k, v in miss.items()))

    bcef = np.where(arb.is_conifer.fillna(False), args.bcef_conifer, args.bcef_broadleaf)
    arb["agb_mg_ha"] = arb.V * arb.rho * bcef * arb.W          # m3 * t/m3 * - * 1/ha = Mg/ha
    arb["vol_mg_ha_known"] = np.where(known, arb.V * arb.W, 0.0)
    arb["vol_mg_ha_all"] = vol

    g = arb.groupby(["CAMPAGNE", "IDP"]).agg(
        agb_mg_ha=("agb_mg_ha", "sum"),
        vol_known=("vol_mg_ha_known", "sum"),
        vol_all=("vol_mg_ha_all", "sum"),
        n_trees=("V", "size"),
        n_species=("espar_n", "nunique"),
        mean_dbh_cm=("C13", lambda s: float(np.nanmean(s)) * 100.0 / np.pi if s.notna().any() else np.nan),
        mean_htot_m=("HTOT", "mean"),
    ).reset_index()
    g["frac_volume_unknown_rho"] = 1.0 - (g.vol_known / g.vol_all.replace(0, np.nan))
    g["rho_coverage_ok"] = g.frac_volume_unknown_rho.fillna(1.0) <= (1.0 - args.min_rho_coverage)

    m = plc.merge(g, on=["CAMPAGNE", "IDP"], how="inner")
    assert len(m) > 0, "no French NFI plots survive the join -- check CAMPAGNE/IDP keys"
    # Playbook: assert the joined population, don't eyeball it.
    assert m.XL.between(100_000, 1_300_000).all() and m.YL.between(6_000_000, 7_200_000).all(), \
        "XL/YL outside the Lambert-93 metropolitan France envelope"

    m = m.rename(columns={"XL": "x_lambert93", "YL": "y_lambert93", "CAMPAGNE": "year"})
    m["crs"] = "EPSG:2154"
    print(f"[join  ] {len(m):,} plots with both coordinates and trees "
          f"({m.rho_coverage_ok.sum():,} meet rho coverage >= {args.min_rho_coverage:.0%})")
    print(f"[AGB   ] Mg/ha  median={m.agb_mg_ha.median():.1f}  mean={m.agb_mg_ha.mean():.1f}  "
          f"p95={m.agb_mg_ha.quantile(0.95):.1f}  max={m.agb_mg_ha.max():.1f}")
    print(f"[AGB   ] by year (median Mg/ha):")
    by_year = m.groupby("year").agb_mg_ha.agg(n="size", median="median")
    print(by_year.to_string())

    # Population-level invariant, asserted over EVERY year rather than eyeballed on a sample.
    # A forested NFI plot cannot have a median AGB near zero; this is exactly the check that
    # catches a whole-column join/filter failure like the VISITE trap above.
    bad_years = by_year[by_year["median"] < 10.0]
    assert bad_years.empty, (
        f"median AGB < 10 Mg/ha in year(s) {list(bad_years.index)} -- a whole cohort of plots is "
        f"contributing zero. Check the VISITE filter and the V/W columns before trusting this.\n"
        f"{bad_years.to_string()}")

    dest = OUT / "france_ifn_plot_agb.csv"
    cols = ["year", "IDP", "VISITE", "x_lambert93", "y_lambert93", "crs", "agb_mg_ha",
            "vol_all", "n_trees", "n_species", "mean_dbh_cm", "mean_htot_m",
            "frac_volume_unknown_rho", "rho_coverage_ok"]
    m[cols].to_csv(dest, index=False)
    print(f"[write ] {dest}  ({len(m):,} plots)")

    prov = {
        "output": str(dest),
        "sources": [{"path": str(SRC / f), "mtime": (SRC / f).stat().st_mtime,
                     "sha256": sha256(SRC / f)} for f in ("PLACETTE.csv", "ARBRE.csv")],
        "origin": "IGN Inventaire Forestier National, export_dataifn_2005_2024.zip",
        "licence": "Licence Ouverte / Open Licence Etalab v2.0",
        "coordinates": "Lambert-93 (EPSG:2154), full precision (1 m spacing) -- NOT degraded",
        "equation": "AGB[Mg/ha] = sum_i V_i * rho(species) * BCEF * W_i",
        "bcef_conifer": args.bcef_conifer, "bcef_broadleaf": args.bcef_broadleaf,
        "rho_source": "Zanne et al. 2009 Global Wood Density DB / IPCC 2006 GL Vol.4 Tab.4.14",
        "n_species_with_rho": len(WOOD_DENSITY),
        "window": [args.year_min, args.year_max],
        "n_plots": int(len(m)),
        "n_plots_rho_coverage_ok": int(m.rho_coverage_ok.sum()),
        "agb_median_mg_ha": float(m.agb_mg_ha.median()),
        "CAVEAT": ("First-order IPCC volume-to-biomass route, NOT a fitted allometry. BCEF is a "
                   "stand-level default with ~20-30% spread; rho is a species mean ignoring "
                   "within-species and site variation. Use with a stated uncertainty. Filter on "
                   "rho_coverage_ok before treating a plot as reference data."),
    }
    (OUT / "france_ifn_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov  ] {OUT/'france_ifn_plot_agb.provenance.json'}")


if __name__ == "__main__":
    main()
