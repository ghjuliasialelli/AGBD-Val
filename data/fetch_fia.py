#!/usr/bin/env python
"""Fetch + derive FIA PUBLIC-LAND plot AGB [Mg/ha] for all US states (Tier-B: coords fuzzed ~0.8-1.6 km).

Per state, download PLOT/COND/TREE CSVs from the FIA DataMart, then:
  - keep LIVE trees (STATUSCD==1) with DRYBIO_AG>0, TPA_UNADJ>0;
  - restrict to PUBLIC plots -- every forested condition (COND_STATUS_CD==1) owned public
    (OWNGRPCD in {10 Forest Service, 20 other federal, 30 state/local}); this also AVOIDS the ~20%
    private-plot coordinate SWAP (swapping is a private-landowner privacy measure);
  - plot AGB density = Σ(DRYBIO_AG[lb] · TPA_UNADJ[/acre]) = lb/acre -> Mg/ha (× 0.00112085);
  - one row per plot-VISIT (PLT_CN); keep measurement years 2014-2025 (AEF window).

Biomass is the FIA precomputed value (post-2023 DataMart = NSVB, National-Scale Volume & Biomass;
~15% higher than the older CRM -- recorded). No allometry run here. Coordinates remain Tier-B (fuzzed);
public-land plots are fuzzed but NOT swapped, so they are the cleanest FIA subset. Resumable per state
(skips a state whose by_state output exists); raw TREE CSVs are deleted after processing to save disk.

Run:  .venv/bin/python -u data/fetch_fia.py  > data/logs/fia.log 2>&1
"""
from __future__ import annotations
import json
import subprocess
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
RAW = ROOT / "data" / "fia" / "raw"
BYST = ROOT / "data" / "fia" / "by_state"
OUT = ROOT / "data" / "derived"
BASE = "https://apps.fs.usda.gov/fia/datamart/CSV"
LB_AC_TO_MG_HA = 0.00112085
PUBLIC = {10, 20, 30}
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
          "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
          "VA", "WA", "WV", "WI", "WY", "PR"]


def dl(st, tbl):
    z = RAW / f"{st}_{tbl}.zip"
    if not z.exists() or z.stat().st_size == 0:
        subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "1800", "-o", str(z),
                        f"{BASE}/{st}_{tbl}.zip"], check=False)
    with zipfile.ZipFile(z) as zf:
        name = zf.namelist()[0]
        zf.extract(name, RAW)
    return RAW / name


def process(st):
    out = BYST / f"{st}.csv"
    if out.exists():
        return pd.read_csv(out)
    try:
        plot = pd.read_csv(dl(st, "PLOT"), usecols=lambda c: c in
                           {"CN", "LAT", "LON", "MEASYEAR", "STATECD", "PLOT_STATUS_CD"}, low_memory=False)
        cond = pd.read_csv(dl(st, "COND"), usecols=lambda c: c in
                           {"PLT_CN", "CONDID", "OWNGRPCD", "COND_STATUS_CD"}, low_memory=False)
        tp = dl(st, "TREE")
        tree = pd.read_csv(tp, usecols=lambda c: c in
                           {"PLT_CN", "CONDID", "STATUSCD", "DRYBIO_AG", "TPA_UNADJ"}, low_memory=False)
    except Exception as e:
        print(f"[{st}] FAIL download/read: {e}", flush=True)
        return None

    # public plots: every forested condition is public-owned
    cf = cond[cond["COND_STATUS_CD"] == 1]
    n_forest = cf.groupby("PLT_CN").size()
    n_pub = cf[cf["OWNGRPCD"].isin(PUBLIC)].groupby("PLT_CN").size()
    aligned = n_pub.reindex(n_forest.index).fillna(0)
    public_plots = set(n_forest.index[(n_forest > 0) & (n_forest == aligned)])

    tree = tree[(tree["STATUSCD"] == 1) & (tree["DRYBIO_AG"] > 0) & (tree["TPA_UNADJ"] > 0)]
    tree = tree[tree["PLT_CN"].isin(public_plots)]
    tree["lb_ac"] = tree["DRYBIO_AG"] * tree["TPA_UNADJ"]
    agg = tree.groupby("PLT_CN").agg(agb_lb_ac=("lb_ac", "sum"), n_trees=("lb_ac", "size")).reset_index()
    agg["agb_mg_ha"] = agg["agb_lb_ac"] * LB_AC_TO_MG_HA

    g = agg.merge(plot, left_on="PLT_CN", right_on="CN", how="inner")
    g["in_window"] = g["MEASYEAR"].between(2014, 2025)
    g = g[["PLT_CN", "STATECD", "LAT", "LON", "MEASYEAR", "in_window", "n_trees", "agb_mg_ha"]]
    g.insert(1, "state", st)
    BYST.mkdir(parents=True, exist_ok=True)
    g.to_csv(out, index=False)
    # free disk: drop the big TREE csv + zip
    for p in (tp, RAW / f"{st}_TREE.zip"):
        try:
            p.unlink()
        except OSError:
            pass
    print(f"[{st}] {len(g):,} public plot-visits ({int(g.in_window.sum())} in-window), "
          f"median {g.agb_mg_ha.median():.0f} Mg/ha", flush=True)
    return g


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    frames = []
    for st in STATES:
        r = process(st)
        if r is not None and len(r):
            frames.append(r)
    g = pd.concat(frames, ignore_index=True)
    iw = g[g.in_window]
    med = g["agb_mg_ha"].median()
    print(f"\n[TOTAL] {len(g):,} public plot-visits, {g.state.nunique()} states; "
          f"{len(iw):,} in-window (2014-2025)", flush=True)
    print(f"[TOTAL] Mg/ha median={med:.1f} mean={g.agb_mg_ha.mean():.1f} p95={g.agb_mg_ha.quantile(0.95):.1f}",
          flush=True)
    assert 10 < med < 400, f"implausible FIA median {med:.1f} Mg/ha"

    dest = OUT / "fia_public_plot_agb.csv"
    g.sort_values(["state", "MEASYEAR"]).to_csv(dest, index=False)
    prov = {
        "output": str(dest), "origin": "USDA FIA DataMart per-state CSV (PLOT/COND/TREE)",
        "subset": "PUBLIC-LAND plots only (OWNGRPCD 10/20/30; every forest condition public) -- avoids "
                  "the ~20% private-plot coordinate swap",
        "biomass": "FIA precomputed DRYBIO_AG (post-2023 DataMart = NSVB, ~15% > old CRM); no allometry run",
        "agb": "Σ(DRYBIO_AG lb · TPA_UNADJ /acre) = lb/acre × 0.00112085 -> Mg/ha, per plot-visit (PLT_CN)",
        "n_plot_visits": int(len(g)), "n_in_window": int(len(iw)), "n_states": int(g.state.nunique()),
        "agb_median_mg_ha": float(med),
        "coord_tier": "B -- public coords fuzzed up to ~0.8-1.6 km (not swapped for public land). Usable "
                      "for aggregate/coarse (county/ecoregion/~1 km) validation, NOT 10 m pixels. True "
                      "coords only via FIA Spatial Data Services (paused).",
    }
    (OUT / "fia_public_plot_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[write] {dest} + provenance", flush=True)


if __name__ == "__main__":
    main()
