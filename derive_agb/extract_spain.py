#!/usr/bin/env python
"""Derive plot-level AGB [Mg/ha] from the Spanish NFI (IFN4) per-province Access databases.

Per tree in PCMayores: AGB = Ruiz-Peinado 2011/2012 by IFN species code (derive_agb/spain_biomass.py),
dbh = (Dn1+Dn2)/2 [mm->cm], height Ht [m] (per-province log-log H-D fill where missing). Per-hectare
expansion from the IFN variable-radius concentric-plot design (5/10/15/25 m radii for dbh classes
7.5-12.5 / 12.5-22.5 / 22.5-42.5 / >=42.5 cm -> 127.32 / 31.83 / 14.15 / 5.09 trees/ha). Plot AGB =
Sum(tree AGB x factor) / 1000, per Estadillo. Coordinates from PCDatosMap (CoorX/CoorY, Huso) with the
per-province DATUM (ED50 / ETRS89 / WGS84) -> EPSG -> WGS84; a wrong datum is a ~200 m shift.

access-parser drops the PCMayores Provincia column, shifting the text columns, so the Estadillo (join)
and Especie (species) columns are resolved by CONTENT, not label. Unmapped species dropped + reported.

Run:  .venv/bin/python -u derive_agb/extract_spain.py
"""
from __future__ import annotations
import glob
import io
import json
import re
import shutil
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from access_parser import AccessParser
from pyproj import Transformer

# mdbtools fallback for DBs that access-parser can't parse (e.g. Extremadura -> KeyError in
# column defs). mdb-export preserves the Provincia column, so NO access-parser column shift.
MDBEXPORT = shutil.which("mdb-export") or "/scratch3/gsialelli/envs/mdb/bin/mdb-export"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from spain_biomass import agb_kg, COVERED  # noqa: E402

RAW = Path("/scratch3/gsialelli/AGBD-Val/data/spain-ifn4/raw")
OUT = Path("/scratch3/gsialelli/AGBD-Val/data/derived")
ED50 = {"31", "15", "27", "32", "36", "33", "39", "30", "07", "01", "20", "48", "26", "28",
        "08", "17", "25", "43"}
WGS84 = {"35", "38"}


def epsg_for(prov, huso):
    huso = int(huso)
    if prov in WGS84:
        return 32600 + huso
    if prov in ED50:
        return 23000 + huso
    return 25800 + huso  # ETRS89


def expansion(d):
    return np.select([d < 12.5, d < 22.5, d < 42.5],
                     [127.323955, 31.830989, 14.147106], default=5.092958)


def resolve(M, dm_estad):
    """Return (estadillo_col, especie_col) resolved by content (access-parser shifts text cols).
    Estadillo = max overlap with the plot-coord table's Estadillo; Especie = max overlap with real IFN
    species codes (NOT just '3-digit' -- the Subclase/tree-order columns are also 3-digit and would win)."""
    cand = [c for c in M.columns if M[c].dtype not in ("int64", "float64")]
    est = max(cand, key=lambda c: len(set(M[c].astype(str)) & dm_estad))
    def sp(c):
        return -1.0 if c == est else M[c].astype(str).str.zfill(3).isin(COVERED).mean()
    esp = max(cand, key=sp)
    return est, esp


def _mdb_table(dbf, name):
    """Read one table via mdb-export -> DataFrame (labelled columns, no access-parser shift)."""
    out = subprocess.run([MDBEXPORT, str(dbf), name], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return pd.read_csv(io.StringIO(out.stdout), low_memory=False)


def load(dbf):
    """Return (M, DM, shifted). shifted=True => access-parser dropped Provincia (resolve by content);
    False => mdbtools fallback with real column labels. (None,None,None) on unreadable."""
    try:
        db = AccessParser(str(dbf))
        if "PCMayores" not in db.catalog or "PCDatosMap" not in db.catalog:
            return None, None, None
        M = pd.DataFrame({k: v for k, v in db.parse_table("PCMayores").items()})
        DM = pd.DataFrame({k: v for k, v in db.parse_table("PCDatosMap").items()})
        return M, DM, True
    except Exception:
        M = _mdb_table(dbf, "PCMayores")
        DM = _mdb_table(dbf, "PCDatosMap")
        return M, DM, False


def process(dbf):
    M, DM, shifted = load(dbf)
    if M is None or DM is None:
        return None, f"unreadable by access-parser and mdbtools ({dbf.name})"
    if not len(M) or not len(DM):
        return None, f"empty ({dbf.name})"

    if shifted:
        dm_estad = set(DM["Estadillo"].astype(str))
        est_col, esp_col = resolve(M, dm_estad)
    else:  # mdbtools path: columns are correctly labelled
        est_col, esp_col = "Estadillo", "Especie"
    M = M.rename(columns={est_col: "Estadillo_r", esp_col: "Especie_r"})
    M["Estadillo_r"] = M["Estadillo_r"].astype(str)  # mdb-export gives int64; DM Estadillo is str
    M["dbh"] = (pd.to_numeric(M["Dn1"], errors="coerce") + pd.to_numeric(M["Dn2"], errors="coerce")) / 2 / 10
    M["ht"] = pd.to_numeric(M["Ht"], errors="coerce")
    M = M[(M["dbh"] >= 7.5) & np.isfinite(M["dbh"])]
    if not len(M):
        return None, f"no valid trees ({dbf.name})"

    # per-file H-D fill for missing heights
    ok = np.isfinite(M["ht"]) & (M["ht"] > 0) & np.isfinite(M["dbh"])
    if ok.sum() >= 20:
        b, a = np.polyfit(np.log(M.loc[ok, "dbh"]), np.log(M.loc[ok, "ht"]), 1)
        miss = ~ok
        M.loc[miss, "ht"] = np.exp(a + b * np.log(M.loc[miss, "dbh"]))
    M = M[np.isfinite(M["ht"]) & (M["ht"] > 0)]

    # normalise species code via numeric (mdb-export yields floats like 62.0 -> must be "062", not "62.0")
    M["code"] = pd.to_numeric(M["Especie_r"], errors="coerce").astype("Int64").astype(str).str.zfill(3)
    mapped = M["code"].isin(COVERED)
    tm = M[mapped].copy()
    agb = np.empty(len(tm))
    for cd, idx in tm.groupby("code").groups.items():
        rows = tm.loc[idx]
        agb[tm.index.get_indexer(idx)] = agb_kg(cd, rows["dbh"].values, rows["ht"].values)
    tm["agb_ha"] = agb * expansion(tm["dbh"].values) / 1000.0  # kg/ha -> Mg/ha per tree

    allc = M.groupby("Estadillo_r").size().rename("n_stems")
    mapc = M[mapped].groupby("Estadillo_r").size().rename("n_mapped")
    agg = tm.groupby("Estadillo_r").agg(agb_mg_ha=("agb_ha", "sum")).reset_index()
    g = agg.merge(allc, on="Estadillo_r").merge(mapc, on="Estadillo_r", how="left")
    g["frac_unmapped"] = 1.0 - g["n_mapped"].fillna(0) / g["n_stems"]

    # coordinates + province per plot (handles combined multi-province DBs: Canarias, Cataluna, ...)
    DM = DM.copy()
    DM["Estadillo"] = DM["Estadillo"].astype(str)
    DM["prov"] = DM["Provincia"].astype(str).str.zfill(2)
    DM["huso"] = pd.to_numeric(DM["Huso"], errors="coerce")
    DM["x"] = pd.to_numeric(DM["CoorX"], errors="coerce")
    DM["y"] = pd.to_numeric(DM["CoorY"], errors="coerce")
    # fill a missing/invalid Huso from the province's modal zone, else province default (Galicia=29 etc.)
    DEF_HUSO = {"15": 29, "27": 29, "32": 29, "36": 29, "31": 30}
    DM.loc[~DM["huso"].between(27, 31), "huso"] = np.nan
    for prov, sub in DM.groupby("prov"):
        if sub["huso"].isna().any():
            m = sub["huso"].mode()
            DM.loc[sub.index, "huso"] = sub["huso"].fillna(m.iloc[0] if len(m) else DEF_HUSO.get(prov, 30))
    DM = DM.dropna(subset=["huso", "x", "y"]).drop_duplicates("Estadillo")
    lon = np.full(len(DM), np.nan); lat = np.full(len(DM), np.nan)
    for (prov, huso), sub in DM.groupby(["prov", "huso"]):
        tr = Transformer.from_crs(epsg_for(prov, int(huso)), 4326, always_xy=True)
        ii = DM.index.get_indexer(sub.index)
        lo, la = tr.transform(sub["x"].values, sub["y"].values)
        lon[ii] = lo; lat[ii] = la
    DM["lon"] = lon; DM["lat"] = lat

    g = g.merge(DM[["Estadillo", "prov", "lon", "lat"]], left_on="Estadillo_r", right_on="Estadillo",
                how="left")
    g = g.rename(columns={"prov": "provincia"})
    g["coverage_ok"] = g["frac_unmapped"] <= 0.10
    return g[["provincia", "Estadillo_r", "lon", "lat", "n_stems", "n_mapped", "frac_unmapped",
              "coverage_ok", "agb_mg_ha"]].rename(columns={"Estadillo_r": "estadillo"}), None


def main():
    sys.stdout.reconfigure(errors="replace")  # parser can emit surrogate chars in names
    OUT.mkdir(exist_ok=True)
    dbs = sorted(set(glob.glob(str(RAW / "*.accdb")) + glob.glob(str(RAW / "*.mdb"))))
    print(f"[scan ] {len(dbs)} province databases")
    frames, skipped = [], []
    for dbf in dbs:
        try:
            g, err = process(Path(dbf))
        except Exception as e:
            g, err = None, f"{Path(dbf).name}: {e}"
        if g is None:
            skipped.append(err); print(f"  SKIP {err}"); continue
        frames.append(g)
        provs = "/".join(sorted(g.provincia.dropna().unique())[:4])
        okmed = g.loc[g.coverage_ok, "agb_mg_ha"].median()
        print(f"  [{provs}] {Path(dbf).name}: {len(g):,} plots, "
              f"median {okmed:.0f} Mg/ha, {int(g.lat.notna().sum())} w/ coord", flush=True)

    g = pd.concat(frames, ignore_index=True)
    ok = g[g.coverage_ok]
    med = ok["agb_mg_ha"].median()
    print(f"\n[TOTAL] {len(g):,} plots, {g.provincia.nunique()} provinces; coverage_ok {len(ok):,}")
    print(f"[TOTAL] Mg/ha median={med:.1f} mean={ok.agb_mg_ha.mean():.1f} "
          f"p95={ok.agb_mg_ha.quantile(0.95):.1f}; {int(g.lat.notna().sum()):,} w/ coord")
    assert 10 < med < 300, f"implausible Spain median {med:.1f} Mg/ha"

    dest = OUT / "spain_ifn4_plot_agb.csv"
    g.sort_values(["provincia", "estadillo"]).to_csv(dest, index=False)
    prov = {
        "output": str(dest), "origin": "Spain IFN4 (MITECO) per-province Access DBs",
        "allometry": "Ruiz-Peinado 2011 (softwoods) + 2012 (hardwoods), above-ground total, by IFN code",
        "expansion": "IFN variable-radius concentric plots (5/10/15/25 m by dbh class)",
        "coords": "PCDatosMap CoorX/CoorY + Huso, per-province datum (ED50/ETRS89/WGS84) -> WGS84",
        "n_plots": int(len(g)), "n_coverage_ok": int(len(ok)), "n_provinces": int(g.provincia.nunique()),
        "agb_median_mg_ha": float(med), "provinces_skipped": skipped,
        "CAVEAT": ("access-parser shifts PCMayores text columns -> Estadillo/Especie resolved by content. "
                   "IFN4 fieldwork ~2008-2019 (province-dependent), so much predates the 2014-2025 window "
                   "(no per-tree date in the field DB; use the province campaign year). Coords 'approximate' "
                   "per MITECO -- verify before 10 m use. Species without an INIA equation dropped+reported."),
    }
    (OUT / "spain_ifn4_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2, default=str))
    print(f"[write] {dest} + provenance")


if __name__ == "__main__":
    main()
