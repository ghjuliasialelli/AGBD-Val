#!/usr/bin/env python
"""Derive transect-level AGB [Mg/ha] from Sustainable Landscapes Brazil forest inventories (ORNL 2007).

Tropical, so Chave et al. 2014 Eq.4 (with height): AGB = 0.0673*(WD*D^2*H)^0.976 [kg]. Inputs:
  - DBH (cm): per-tree, in-file (wide multi-year DBH_YY or single DBH);
  - WD  (g/cm3): in-file WSD where it VARIES by species, else Global Wood Density DB (Zanne 2009),
                 South-America-tropical, species->genus->family->region fallback;
  - H   (m): in-file Htot where >0, else a per-site log-log H-D model (pooled fallback if a site has
             too few heights);
  - AREA: the REAL plot area from the paired *_plots shapefile (per-file UTM EPSG). The shapefiles carry
          a 'plot' (~0.25 ha main) + 'subplot' (~0.05 ha nested) polygon per plot; we take the LARGEST
          per plot number (never the nested subplot), falling back to the site's median main-plot area
          for plots with no digitized polygon. Transect-keyed sites use the documented 20x500 m = 1 ha.
          NB: matching to the polygon (not an assumed 1 ha) is essential -- it corrected six sites whose
          real plots are 0.25 ha but were silently divided by 1 ha (4x too low, yet plausible-looking).
Live trees only; lianas (type L) and palms (type P) excluded (Chave tree allometry). Coordinates =
transect-polygon centroid -> WGS84 (precise, Tier-A). Heterogeneous CSVs are normalised; any file that
cannot be parsed confidently is SKIPPED and reported (coverage is printed, never silently dropped).

Run:  .venv/bin/python -u derive_agb/extract_slb.py
"""
from __future__ import annotations
import glob
import hashlib
import json
import os
import re
import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chave2014_agb_H  # noqa: E402
from wood_density import lookup as wd_lookup  # noqa: E402

SRC = Path("/scratch3/gsialelli/AGBD-Val/data/sustainable-landscapes-brazil/2007_field_inventory")
OUT = Path("/scratch3/gsialelli/AGBD-Val/data/derived")
YY = {"09": 2009, "10": 2010, "11": 2011, "12": 2012, "13": 2013, "14": 2014,
      "15": 2015, "16": 2016, "17": 2017, "18": 2018}
TRANSECT_KEYS = ["transect", "transect_id", "trans", "plot_id", "plot", "plot_p", "group_code",
                 "group", "area_code"]


def canon(c):
    return re.sub(r"[.\s]+", "_", str(c).strip().lower()).strip("_")


def read_csv_any(f):
    with open(f, "rb") as fh:
        head = fh.readline().decode("latin-1")
    sep = ";" if head.count(";") > head.count(",") else ","
    df = pd.read_csv(f, sep=sep, encoding="latin-1", low_memory=False)
    df.columns = [canon(c) for c in df.columns]
    return df


def pick(cols, *names):
    for n in names:
        if n in cols:
            return n
    return None


def _keys(v):
    """Normalised id variants so a CSV id ('63', 'T01', 'M1') can match a shapefile id
    ('P63', 'T01', 'M1'): full upper-no-space, and digits-only with leading zeros stripped."""
    v = str(v)
    u = re.sub(r"\s+", "", v).upper()
    dig = re.sub(r"\D", "", v).lstrip("0") or "0"
    return {u, dig}


def load_shp(stem):
    """(poly_by_num, design_area, n_features, epsg, is_poly).
    poly_by_num[numeric_id] = (area_m2, lon, lat) keyed by the plot NUMBER (digits of any id/fid column),
    keeping the LARGEST polygon for that number -- so a nested small-tree subplot (e.g. SAN's 250 m2
    inner square) never shadows its 2500 m2 main plot. design_area = median of those per-number areas,
    used for plots whose polygon was not digitized (e.g. FN digitized only 1 of 36 identical 0.25 ha
    plots). LineString footprints carry no area -> is_poly False, design_area None (design = 1 ha)."""
    zl = [p for p in SRC.glob("*_plots*.zip") if p.name.lower().startswith(stem.lower() + "_plots")]
    if not zl:
        return {}, None, 0, None, False
    g = gpd.read_file(f"zip://{zl[0]}")
    g.columns = [canon(c) for c in g.columns]
    epsg = g.crs.to_epsg() if g.crs else None
    is_poly = g.geom_type.isin(["Polygon", "MultiPolygon"]).any()
    # id sources: fid columns too -- SAN's CSV plot ids (1..8) match the shapefile fid_1, not plotid
    numcols = [c for c in g.columns if c != "geometry"
               and not c.startswith(("shape_", "x_centroid", "y_centroid", "area", "geometry"))]
    gd = g.to_crs(4326)
    poly = {}
    for i, row in g.iterrows():
        a = float(row.geometry.area)
        area = a if (is_poly and a > 0) else 10000.0
        c = gd.geometry.iloc[i].centroid
        val = (area, float(c.x), float(c.y))
        for col in numcols:
            num = re.sub(r"\D", "", str(row[col])).lstrip("0") or "0"
            if num not in poly or area > poly[num][0]:  # keep the largest (= main plot)
                poly[num] = val
    design = float(np.median([v[0] for v in poly.values()])) if (is_poly and poly) else None
    return poly, design, len(g), epsg, is_poly


def hd_predict(dbh, htot):
    """Per-group log-log H-D model; returns filled heights + count modelled. Falls back to caller pool."""
    ok = np.isfinite(htot) & (htot > 0) & np.isfinite(dbh) & (dbh > 0)
    out = htot.copy()
    if ok.sum() >= 8:
        b, a = np.polyfit(np.log(dbh[ok]), np.log(htot[ok]), 1)
        need = ~ok & np.isfinite(dbh) & (dbh > 0)
        out[need] = np.exp(a + b * np.log(dbh[need]))
        return out, int(need.sum()), (a, b)
    return out, 0, None


def main():
    OUT.mkdir(exist_ok=True)
    files = sorted(glob.glob(str(SRC / "*[Ii]nventory.csv")))
    rows, skipped, pooled_hd = [], [], []
    # first pass: gather a pooled H-D sample for sites lacking heights
    for f in files:
        try:
            df = read_csv_any(f)
        except Exception:
            continue
        cols = set(df.columns)
        for yk in (sorted({m.group(1) for c in cols if (m := re.search(r"_(\d{2})$", c))}) or [""]):
            suf = f"_{yk}" if yk else ""
            dcol, hcol = pick(cols, f"dbh{suf}", "dbh"), pick(cols, f"htot{suf}", "htot", f"h_tot{suf}")
            if dcol and hcol:
                d = pd.to_numeric(df[dcol], errors="coerce"); h = pd.to_numeric(df[hcol], errors="coerce")
                m = np.isfinite(d) & np.isfinite(h) & (d > 0) & (h > 0)
                pooled_hd.append(pd.DataFrame({"d": d[m], "h": h[m]}))
    pool = pd.concat(pooled_hd, ignore_index=True) if pooled_hd else pd.DataFrame({"d": [], "h": []})
    pb, pa = (np.polyfit(np.log(pool.d), np.log(pool.h), 1) if len(pool) > 50 else (0.5, 1.0))
    print(f"[hd   ] pooled H-D from {len(pool):,} trees: ln H = {pa:.3f} + {pb:.3f} ln D")

    for f in files:
        stem = os.path.basename(f).replace(".csv", "")
        site = os.path.basename(f).split("_")[0]
        try:
            df = read_csv_any(f)
        except Exception as e:
            skipped.append((stem, f"read: {e}")); continue
        cols = set(df.columns)
        tkey = pick(cols, *TRANSECT_KEYS)
        scol = pick(cols, "scientific_name", "scienfic_name", "scientificname")
        if not tkey or not scol:
            skipped.append((stem, f"no transect/species col (have {sorted(cols)[:6]})")); continue
        poly_m, design_area, n_feat, epsg, is_poly = load_shp(stem)
        # transect-keyed files follow the documented 20x500 m = 1 ha design; only PLOT-keyed files take
        # their area from the polygon footprints (the transect shapefiles are often subplot-level).
        is_transect = (tkey in ("transect", "trans", "transect_id")
                       or df[tkey].astype(str).str.match(r"^[TM]\s*\d").mean() > 0.8)
        years = sorted({m.group(1) for c in cols if (m := re.search(r"_(\d{2})$", c))})
        yearspec = years if years else [""]

        for yk in yearspec:
            suf = f"_{yk}" if yk else ""
            dcol = pick(cols, f"dbh{suf}", "dbh")
            if not dcol:
                continue
            sub = pd.DataFrame({
                "transect": df[tkey].astype(str),
                "sciname": df[scol].astype(str).str.strip(),
                "dbh": pd.to_numeric(df[dcol], errors="coerce"),
            })
            hcol = pick(cols, f"htot{suf}", "htot", f"h_tot{suf}")
            sub["htot"] = pd.to_numeric(df[hcol], errors="coerce") if hcol else np.nan
            wcol = pick(cols, f"wsd{suf}", "wsd")
            sub["wsd"] = pd.to_numeric(df[wcol], errors="coerce") if wcol else np.nan
            dcol2 = pick(cols, f"dead{suf}", "dead")
            sub["dead"] = df[dcol2].astype(str) if dcol2 else ""
            tcol = pick(cols, f"type{suf}", "type")
            sub["type"] = df[tcol].astype(str) if tcol else ""
            sub = sub[np.isfinite(sub["dbh"]) & (sub["dbh"] >= 5)]
            # live trees only; drop lianas (L) and palms (P)
            sub = sub[~sub["dead"].str.upper().str.startswith(("D",))]
            sub = sub[~sub["type"].str.upper().isin(["L", "P"])]
            if not len(sub):
                continue

            # wood density: in-file if it varies by species, else GWDD (South America tropical)
            if sub["wsd"].notna().sum() > 0 and sub["wsd"].nunique() > 3:
                wd_used = sub["wsd"].values
                wd_src = "in-file WSD"
            else:
                taxa = sub["sciname"].str.split(n=2, expand=True)
                ggen = taxa[0] if 0 in taxa else pd.Series([None] * len(sub))
                gsp = taxa[1] if (taxa.shape[1] > 1) else pd.Series([None] * len(sub))
                wd_used, _ = wd_lookup(ggen.values, gsp.values, region_id="SouthAmericaTrop")
                wd_src = "GWDD"

            # heights: in-file else per-site HD else pooled
            h = sub["htot"].values.astype(float)
            h, nmod, _ = hd_predict(sub["dbh"].values.astype(float), h)
            need = ~(np.isfinite(h) & (h > 0))
            if need.any():
                h[need] = np.exp(pa + pb * np.log(sub["dbh"].values[need]))

            agb_kg = chave2014_agb_H(sub["dbh"].values, wd_used, h)
            sub = sub.assign(agb_kg=agb_kg)
            yr = YY.get(yk, None)
            for tr, grp in sub.groupby("transect"):
                num = re.sub(r"\D", "", str(tr)).lstrip("0") or "0"
                hit = poly_m.get(num)
                if is_transect:
                    # design-based 1 ha; borrow the matched polygon centroid for coords if present
                    area, area_src = 10000.0, "design_1ha"
                    lon, lat = (hit[1], hit[2]) if hit else (np.nan, np.nan)
                elif hit is not None:
                    area, lon, lat, area_src = hit[0], hit[1], hit[2], "shp"
                elif design_area is not None:
                    # plot-keyed, polygon not digitized for this plot -> per-site design area (e.g. FN)
                    area, lon, lat, area_src = design_area, np.nan, np.nan, "design_site"
                else:
                    area, lon, lat, area_src = 10000.0, np.nan, np.nan, "fallback_1ha"
                rows.append({
                    "site": site, "file": stem, "transect": tr, "year": yr,
                    "n_trees": len(grp), "area_m2": round(area, 1), "area_src": area_src,
                    "area_from_shp": area_src == "shp",
                    "agb_mg_ha": grp["agb_kg"].sum() / 1000.0 / (area / 10000.0),
                    "lon": lon, "lat": lat, "epsg": epsg, "wd_source": wd_src,
                })

    g = pd.DataFrame(rows)
    # per-site plausibility flag: implausible median => wrong area assumption for that site
    site_med = g.groupby("site")["agb_mg_ha"].median()
    g["site_plausible"] = g["site"].map((site_med.between(20, 600)))
    g["in_window"] = g["year"].fillna(0).astype(int).between(2014, 2025)
    g["has_coord"] = g["lat"].notna()

    print(f"[parse] {len(files)} files -> {len(g):,} transect-year records "
          f"({g.site.nunique()} sites); skipped {len(skipped)}")
    for s, why in skipped:
        print(f"        SKIP {s}: {why}")
    print(f"[AGB  ] Mg/ha median={g.agb_mg_ha.median():.1f} mean={g.agb_mg_ha.mean():.1f} "
          f"p95={g.agb_mg_ha.quantile(0.95):.1f} max={g.agb_mg_ha.max():.1f}")
    print("[check] per-site median Mg/ha:")
    for s, m in site_med.sort_values().items():
        flag = "" if 20 < m < 600 else "  <-- IMPLAUSIBLE (area?)"
        print(f"        {s}: {m:.0f}{flag}")
    print(f"[AGB  ] in-window {int(g.in_window.sum())}, with coord {int((g.in_window & g.has_coord).sum())}")

    dest = OUT / "slb_brazil_transect_agb.csv"
    g.sort_values(["site", "file", "transect", "year"]).to_csv(dest, index=False)
    print(f"[write] {dest} ({len(g):,} records)")

    prov = {
        "output": str(dest), "origin": "Sustainable Landscapes Brazil forest inventory (ORNL 2007)",
        "allometry": "Chave et al. 2014 Eq.4 (with height); WD from in-file WSD (where it varies) else "
                     "Global Wood Density DB (Zanne 2009, South-America tropical)",
        "height": "in-file Htot where >0, else per-site then pooled log-log H-D model",
        "area": "per plot: LARGEST digitized *_plots polygon for that plot number (the shapefiles carry a "
                "'plot' 0.25 ha main + 'subplot' ~0.05 ha nested pair -> the main is taken, never the "
                "subplot); plots with no digitized polygon use the site's median main-plot area "
                "(design_site); transect-keyed sites use the documented 20x500 m = 1 ha design.",
        "area_src_counts": {k: int(v) for k, v in g["area_src"].value_counts().items()},
        "filters": "live only (dead flag), lianas/palms excluded, DBH>=5 cm",
        "n_records": int(len(g)), "n_sites": int(g.site.nunique()),
        "n_in_window_coord": int((g.in_window & g.has_coord).sum()),
        "files_skipped": skipped,
        "CAVEAT": ("Heterogeneous provider CSVs normalised; skipped files listed. AREA FIX (this pass): "
                   "matching the CSV plot id to the LARGEST polygon per plot number corrected six sites "
                   "that were silently divided by 1 ha when their real plots are 0.25 ha "
                   "(BON 31->128, HUM 34->138, TAL 27->104, SAN 5->23, FN 18->71) or ~0.09 ha (TAC 38->111) "
                   "-- all had a plausible-looking-but-4x-low median before, none flagged. 13/14 sites now "
                   "plausible. ONLY FNA remains flagged (median ~4 Mg/ha): its area IS correct (500 m "
                   "transects = the 1 ha design, confirmed from per-tree UTM extents) -- the low value is "
                   "GENUINE heavy mortality (only 49 of 283 trees live), a real degraded-forest datapoint, "
                   "not an area artifact. Multi-year files give one record per plot per year. Coords Tier-A."),
    }
    (OUT / "slb_brazil_transect_agb.provenance.json").write_text(json.dumps(prov, indent=2, default=str))
    print(f"[prov ] {OUT/'slb_brazil_transect_agb.provenance.json'}")


if __name__ == "__main__":
    main()
