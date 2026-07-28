#!/usr/bin/env python
"""Derive conglomerado-level AGB [Mg/ha] from Colombia IFN / IDEAM (SiB DwC-A).

The archive gives, per occurrence (species x subplot-stratum), a summed basal area (m2) and an
individualCount, plus per-event subplot area (sampleSizeValue: F=154 m2, FG=707 m2) in a nested
conglomerado design. No per-stem DBH, no height, no wood density in-file, so:
  - mean DBH per record  = sqrt(4*(BA/count)/pi) [m] -> cm  (all `count` stems set to that mean);
  - wood density         from the Global Wood Density Database (Zanne 2009), South-America-tropical,
                           species->genus->family->region fallback (level recorded);
  - AGB per stem         = Chave et al. 2005 moist-forest, diameter-only (no height/E available);
  - per conglomerado     = area-weighted density = sum(AGB) / sum(subplot area) -> Mg/ha.

COORDINATES ARE TIER-B: public coords are generalized to a ~10.6 km grid (coordinateUncertaintyInMeters
= 10606; informationWithheld says exact location only on request to IDEAM). So this is a DISTRIBUTIONAL
reference, NOT usable for 10 m pixel validation. Data flagged "datos sin validar".

Run:  .venv/bin/python -u derive_agb/extract_colombia.py
"""
from __future__ import annotations
import hashlib
import json
import sys
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import chave2005_agb_moist  # noqa: E402
from wood_density import lookup as wd_lookup  # noqa: E402

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
ZIP = ROOT / "data" / "colombia-ifn" / "ideam_ifn_dwca.zip"
OUT = ROOT / "data" / "derived"


def sha(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def _read(zf, name):
    with zipfile.ZipFile(zf) as z, z.open(name) as fh:
        return pd.read_csv(fh, sep="\t", low_memory=False)


def main():
    OUT.mkdir(exist_ok=True)
    occ = _read(ZIP, "occurrence.txt")
    emof = _read(ZIP, "extendedmeasurementorfact.txt")
    ev = _read(ZIP, "event.txt")
    print(f"[load ] {len(occ):,} occurrences, {len(emof):,} measurements, {len(ev):,} subplot-events")

    # basal area (m2) per occurrence -- emof.occurrenceID matches occ.occurrenceID (unique per tree)
    ba = emof[emof["measurementType"].str.contains("basal", case=False, na=False)].copy()
    ba["BA_m2"] = pd.to_numeric(ba["measurementValue"], errors="coerce")
    ba = ba.groupby("occurrenceID")["BA_m2"].sum().reset_index()
    occ = occ.merge(ba, on="occurrenceID", how="left")
    occ["individualCount"] = pd.to_numeric(occ["individualCount"], errors="coerce").fillna(1).clip(lower=1)
    occ = occ.dropna(subset=["BA_m2"])
    occ = occ[occ["BA_m2"] > 0]

    # mean DBH per record from per-stem basal area
    ba_per_stem = occ["BA_m2"] / occ["individualCount"]
    occ["dbh_cm"] = np.sqrt(4.0 * ba_per_stem / np.pi) * 100.0
    occ = occ[occ["dbh_cm"].between(5, 400)]  # Chave-2005 validity + drop absurd back-calcs

    # wood density (South-America tropical) from the archive's own genus/species columns
    wd, lvl = wd_lookup(occ["genus"].values, occ["specificEpithet"].values, region_id="SouthAmericaTrop")
    occ["wd"] = wd
    print(f"[wd   ] density level: " +
          ", ".join(f"{k}={v}" for k, v in pd.Series(lvl).value_counts().items()))

    # AGB per record (kg) = count * Chave2005moist(mean dbh, wd)
    occ["agb_kg"] = occ["individualCount"] * chave2005_agb_moist(occ["dbh_cm"].values, occ["wd"].values)

    # subplot area per event, then area-weighted density per conglomerado
    ev["area_m2"] = pd.to_numeric(ev["sampleSizeValue"], errors="coerce")
    ev["conglo"] = ev["eventID"].str.extract(r"^(\d+)_")[0]
    occ["conglo"] = occ["eventID"].str.extract(r"^(\d+)_")[0]
    occ = occ.merge(ev[["eventID", "area_m2"]], on="eventID", how="left")

    # area sampled per conglomerado = sum of its distinct subplot-event areas
    ev_area = ev.dropna(subset=["area_m2"]).drop_duplicates("eventID")
    conglo_area = ev_area.groupby("conglo")["area_m2"].sum().rename("area_m2_total")
    conglo_agb = occ.groupby("conglo")["agb_kg"].sum().rename("agb_kg_total")
    coords = ev.dropna(subset=["decimalLatitude"]).drop_duplicates("conglo").set_index("conglo")[
        ["decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters", "year",
         "stateProvince"]]

    g = pd.concat([conglo_agb, conglo_area, coords], axis=1).dropna(subset=["agb_kg_total", "area_m2_total"])
    g["agb_mg_ha"] = (g["agb_kg_total"] / 1000.0) / (g["area_m2_total"] / 10000.0)
    g = g.reset_index().rename(columns={"index": "conglo"})
    g["in_window"] = pd.to_numeric(g["year"], errors="coerce").between(2014, 2025)

    med = g["agb_mg_ha"].median()
    print(f"[AGB  ] {len(g):,} conglomerados; Mg/ha median={med:.1f} mean={g.agb_mg_ha.mean():.1f} "
          f"p95={g.agb_mg_ha.quantile(0.95):.1f} max={g.agb_mg_ha.max():.1f}")
    print(f"[AGB  ] coord uncertainty median={g.coordinateUncertaintyInMeters.median():.0f} m "
          f"(TIER-B: generalized ~10 km grid)")
    assert 20 < med < 500, f"implausible Colombia median {med:.1f} Mg/ha"

    dest = OUT / "colombia_ifn_conglomerado_agb.csv"
    g.to_csv(dest, index=False)
    print(f"[write] {dest} ({len(g):,} conglomerados)")

    prov = {
        "output": str(dest), "origin": "Colombia IFN / IDEAM (SiB Colombia DwC-A ideam_ifn v2.1)",
        "source_sha256": sha(ZIP),
        "allometry": "Chave et al. 2005 moist-forest, diameter-only (no height/E available)",
        "wood_density": "Global Wood Density DB (Zanne 2009) via BIOMASS; SouthAmericaTrop; "
                        "species->genus->family->region fallback",
        "dbh_source": "back-calculated from per-stem basal area = sqrt(4*(BA/count)/pi)",
        "aggregation": "per-conglomerado area-weighted density = sum(AGB)/sum(subplot area)",
        "n_conglomerados": int(len(g)), "n_in_window": int(g.in_window.sum()),
        "agb_median_mg_ha": float(med),
        "coord_tier": "B (generalized to ~10.6 km grid; exact coords only on request to IDEAM)",
        "CAVEAT": ("TIER-B coordinates (~10.6 km) -> distributional reference only, NOT 10 m pixel "
                   "validation. 'datos sin validar'. DBH back-calculated from basal area; multi-stem "
                   "records use mean DBH. Nested F(154 m2)/FG(707 m2) strata area-weighted."),
    }
    (OUT / "colombia_ifn_conglomerado_agb.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov ] {OUT/'colombia_ifn_conglomerado_agb.provenance.json'}")


if __name__ == "__main__":
    main()
