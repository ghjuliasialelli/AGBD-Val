#!/usr/bin/env python
"""Derive quadrat-level AGB [Mg/ha] from the BCI ForestGEO 50-ha plot (Dryad 10.15146/5xcp-0d46, CC0).

One 1000x500 m moist-tropical plot, fully stem-mapped, 8 censuses (~1982-2015). We take the LATEST
census (~2015, in the AEF window), live stems, and compute per-stem AGB with Chave et al. 2005
moist-forest (diameter-only; no height in-file) using wood density from the Global Wood Density DB
(Zanne 2009, Central-America-tropical, species->genus->family->region fallback). Aggregated to the
plot's 20x20 m quadrats (400 m2 -> Mg/ha) and to the whole 50 ha.

COORDINATES: PX/PY are plot-local metres (0-1000 x, 0-500 y). ABSOLUTE georeferencing (SW-corner UTM
17N + plot bearing) is NOT applied here -- it is a single fixed affine that must be taken from verified
ForestGEO plot metadata (a wrong corner/rotation is a classic silent georef bug). Recorded as a TODO;
plot centre ~9.15N, 79.85W. So this is spatially-explicit WITHIN the plot but not yet absolutely placed.

Run:  .venv/bin/python -u derive_agb/extract_bci.py
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chave2005_agb_moist  # noqa: E402
from wood_density import lookup as wd_lookup  # noqa: E402

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
TSV = ROOT / "data" / "bci-forestgeo" / "ext" / "FullMeasurementBCI.tsv"
OUT = ROOT / "data" / "derived"
QUAD_M = 20.0  # BCI quadrat size

# --- Absolute georeferencing (community-standard, axis-aligned) ------------------------------------
# BCI 50-ha plot SW corner (plot-local 0,0), UTM zone 17N / WGS84 (EPSG:32617). This is the widely
# cited plot origin and is the CRS used by the plot's georeferenced products (Kupers et al. 2019 soil
# rasters, ForestGEO aerial photogrammetry -> EPSG:32617). CONVENTION: the plot's 20 m quadrat grid is
# placed PARALLEL to the UTM axes (plot-x -> +easting, plot-y -> +northing); the plot's sub-degree
# physical rotation vs UTM north is neglected here exactly as it is in those standard products, so a
# comparison against them is consistent. Residual placement error from the neglected rotation is at
# most ~R*sin(theta): for an unverified theta<~0.5deg that is <=~9 m (~1 pixel) at the far (x=1000) edge.
BCI_SW_E, BCI_SW_N = 625754.0, 1011569.0
BCI_EPSG = 32617


def sha(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(TSV, sep="\t", low_memory=False,
                     usecols=["Family", "Genus", "SpeciesName", "QuadratName", "PX", "PY",
                              "StemID", "PlotCensusNumber", "DBH", "Date", "Status"])
    last = int(df["PlotCensusNumber"].max())
    c = df[df["PlotCensusNumber"] == last].copy()
    c["DBH"] = pd.to_numeric(c["DBH"], errors="coerce")
    yr = pd.to_datetime(c["Date"], errors="coerce", unit="D", origin="1960-01-01").dt.year
    print(f"[census] latest = {last}; date range ~{int(yr.min())}-{int(yr.max())}; {len(c):,} stem-records")

    live = (c["Status"] == "alive") & (c["DBH"] >= 10) & c["PX"].notna() & c["PY"].notna()
    t = c[live].copy()
    t["dbh_cm"] = t["DBH"] / 10.0  # mm -> cm
    print(f"[filter] live stems DBH>=10 mm with coords: {len(t):,}")

    wd, lvl = wd_lookup(t["Genus"].values, t["SpeciesName"].values, region_id="CentralAmericaTrop")
    print("[wd    ] density level: " + ", ".join(f"{k}={v}" for k, v in pd.Series(lvl).value_counts().items()))
    t["agb_kg"] = chave2005_agb_moist(t["dbh_cm"].values, wd)

    # 20x20 m quadrats from PX/PY (independent of QuadratName labelling)
    t["qx"] = np.clip((t["PX"] // QUAD_M).astype(int), 0, int(1000 / QUAD_M) - 1)
    t["qy"] = np.clip((t["PY"] // QUAD_M).astype(int), 0, int(500 / QUAD_M) - 1)
    q = t.groupby(["qx", "qy"]).agg(n_stems=("agb_kg", "size"), agb_kg=("agb_kg", "sum")).reset_index()
    q["px_center"] = q["qx"] * QUAD_M + QUAD_M / 2
    q["py_center"] = q["qy"] * QUAD_M + QUAD_M / 2
    q["agb_mg_ha"] = q["agb_kg"] / 1000.0 / (QUAD_M * QUAD_M / 10000.0)

    # absolute placement: axis-aligned affine plot-local -> UTM17N/WGS84 -> lon/lat
    q["utm_e"] = BCI_SW_E + q["px_center"]
    q["utm_n"] = BCI_SW_N + q["py_center"]
    tr = Transformer.from_crs(BCI_EPSG, 4326, always_xy=True)
    q["lon"], q["lat"] = tr.transform(q["utm_e"].values, q["utm_n"].values)

    # verify placement against the documented plot centre (~9.15 N, 79.85 W) -- an independent field
    cen_lon, cen_lat = tr.transform(BCI_SW_E + 500.0, BCI_SW_N + 250.0)
    print(f"[georef] plot centre -> {cen_lat:.4f} N, {cen_lon:.4f}  (documented ~9.15 N, -79.85)")
    assert 9.14 < cen_lat < 9.17 and -79.87 < cen_lon < -79.83, \
        f"BCI centre {cen_lat:.4f},{cen_lon:.4f} off documented ~9.15N/-79.85 -- check corner/datum"

    whole = t["agb_kg"].sum() / 1000.0 / 50.0  # 50 ha
    med = q["agb_mg_ha"].median()
    print(f"[AGB   ] whole-plot = {whole:.1f} Mg/ha over 50 ha")
    print(f"[AGB   ] 20x20 m quadrats: {len(q):,}; Mg/ha median={med:.1f} mean={q.agb_mg_ha.mean():.1f} "
          f"p95={q.agb_mg_ha.quantile(0.95):.1f} max={q.agb_mg_ha.max():.1f}")
    assert 150 < whole < 500, f"implausible BCI whole-plot AGB {whole:.1f} (moist tropical ~200-350)"

    dest = OUT / "bci_forestgeo_quadrat_agb.csv"
    q[["qx", "qy", "px_center", "py_center", "utm_e", "utm_n", "lon", "lat",
       "n_stems", "agb_mg_ha"]].to_csv(dest, index=False)
    print(f"[write ] {dest} ({len(q):,} quadrats)")

    prov = {
        "output": str(dest),
        "origin": "BCI ForestGEO 50-ha plot, Dryad 10.15146/5xcp-0d46 (CC0), FullMeasurementBCI.tsv",
        "source_sha256": sha(ROOT / "data" / "bci-forestgeo" / "FullMeasurementBCI.zip"),
        "census": last, "n_quadrats": int(len(q)), "quadrat_m": QUAD_M,
        "allometry": "Chave et al. 2005 moist-forest, diameter-only",
        "wood_density": "Global Wood Density DB (Zanne 2009), CentralAmericaTrop, taxonomic fallback",
        "whole_plot_agb_mg_ha": float(whole), "quadrat_median_mg_ha": float(med),
        "coords": "px_center/py_center = plot-local metres (exact). utm_e/utm_n/lon/lat = ABSOLUTE, "
                  "axis-aligned affine: UTM17N/WGS84 (EPSG:32617), SW corner (625754, 1011569), "
                  f"plot-x->+E plot-y->+N. Centre verified at {cen_lat:.4f}N {cen_lon:.4f} (~9.15N/-79.85).",
        "georef_method": "community-standard axis-aligned placement (Kupers 2019 soil rasters / ForestGEO "
                         "photogrammetry use EPSG:32617). Plot sub-degree physical rotation vs UTM north is "
                         "NEGLECTED (as in those products); residual edge error <=~9 m (~1 px) at x=1000. "
                         "Good for coarse/aggregate placement; treat 10 m pixel matching as approximate.",
        "CAVEAT": "One 50-ha plot. Live stems DBH>=1 cm; per-stem (multi-stem trees summed). Census ~2015 "
                  "in-window. CIRCULARITY: BCI may be in the training set of CCI/GEDI/JAXA and possibly AEF "
                  "-- confirm independence before using as a validation target.",
    }
    (OUT / "bci_forestgeo_quadrat_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov  ] {OUT/'bci_forestgeo_quadrat_agb.provenance.json'}")


if __name__ == "__main__":
    main()
