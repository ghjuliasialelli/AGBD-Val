#!/usr/bin/env python
"""Validity check on the Tier-A fetch (not just 'file exists'): open rasters, test archives,
confirm coordinate/dbh columns. Catches truncated files and HTML-error-pages-saved-as-data."""
from __future__ import annotations
import io
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio

D = Path("/scratch3/gsialelli/AGBD-Val/data")


def raster(p, decim=25):
    with rasterio.open(p) as s:
        print(f"  {p.name}: crs={s.crs} res={tuple(round(x,6) for x in s.res)} "
              f"nodata={s.nodata} shape={s.shape} dtype={s.dtypes[0]}")
        a = s.read(1, out_shape=(1, max(1, s.height // decim), max(1, s.width // decim)))
        v = a.astype("float64").ravel()
        if s.nodata is not None:
            v = v[v != s.nodata]
        v = v[np.isfinite(v)]
        if v.size:
            print(f"     valid px(decim)={v.size:,}  min={v.min():.2f} max={v.max():.2f} "
                  f"mean={v.mean():.2f}")
        else:
            print("     !! no valid pixels in decimated read")


def csv_head(p, cols_like):
    df = pd.read_csv(p, nrows=5, low_memory=False)
    hit = [c for c in df.columns if any(k.lower() in c.lower() for k in cols_like)]
    print(f"  {p.name}: {len(df.columns)} cols; matched {cols_like} -> {hit}")
    return df.columns.tolist()


print("== 2. GAO Peru ACD rasters (expect MgC/ha, ~100 m) ==")
for f in ("peru_acd.tif", "peru_acd_uncertainty.tif"):
    raster(D / "gao-peru-carbon" / f)

print("== 4. ORNL 1648 Paragominas AGB (units MgC/ha per guide; whole-muni + per-site) ==")
for f in ("paragominas_predicted_agb.tif", "par_predicted_agb_mean.tif"):
    raster(D / "sustainable-landscapes-brazil" / "1648_paragominas_lidar_agb" / f)

print("== 3. ORNL 2007 field inventory CSV (dbh+species+UTM) ==")
csv_head(next((D / "sustainable-landscapes-brazil" / "2007_field_inventory").glob("TAP_A01_2009*inventory.csv")),
         ["DBH", "scientific", "UTM", "easting", "northing", "date"])

print("== 5. Colombia IFN DwC-A archive ==")
zp = D / "colombia-ifn" / "ideam_ifn_dwca.zip"
with zipfile.ZipFile(zp) as z:
    names = z.namelist()
    print(f"  members: {names}")
    core = [n for n in names if n.lower() in ("occurrence.txt", "taxon.txt", "event.txt")] or \
           [n for n in names if n.endswith(".txt")]
    if core:
        with z.open(core[0]) as fh:
            head = pd.read_csv(io.TextIOWrapper(fh, "utf-8"), sep="\t", nrows=5, low_memory=False)
        hit = [c for c in head.columns if any(k in c.lower() for k in
               ("decimallat", "decimallon", "eventdate", "coordinateuncertainty", "measurement"))]
        with z.open(core[0]) as fh:
            n = sum(1 for _ in fh) - 1
        print(f"  {core[0]}: {n:,} rows; geo/measure cols -> {hit}")

print("== 6. BC PSP (TRUE coords in plot header; tree detail carries dbh/species) ==")
cols = csv_head(D / "bc-ground-plots" / "psp" / "faib_plot_header.csv",
                ["utm", "easting", "northing", "lat", "lon", "bec", "sample_site", "grid"])
csv_head(D / "bc-ground-plots" / "psp" / "faib_tree_detail.csv",
         ["dbh", "species", "spc", "meas", "year", "phf", "live"])

print("== 7. Quebec PEP GPKG archive ==")
qz = D / "quebec-pep" / "PEP_GPKG.zip"
with zipfile.ZipFile(qz) as z:
    gpkg = [n for n in z.namelist() if n.lower().endswith(".gpkg")]
    print(f"  members: {z.namelist()[:8]}{' ...' if len(z.namelist())>8 else ''}  gpkg={gpkg}")

print("\nDONE validate")
