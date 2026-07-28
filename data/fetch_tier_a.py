#!/usr/bin/env python
"""Fetch open Tier-A AGB reference datasets (resumable, serial, logged).

Sources + access mechanics verified 2026-07-27 (see catalog/COORD_TIER_PARTITION.md):
  1. BCI ForestGEO 50-ha    Dryad 10.15146/5xcp-0d46  (CC0)  dbh+species, local-grid coords
  2. GAO/Asner Peru carbon  Zenodo 4626309  (CC-BY)  ACD MgC/ha rasters (~3.2 GB)
  3. Sust.Landscapes Brazil field inventory  ORNL 2007 (C2515314177-ORNL_CLOUD)  dbh+species
  4. Sust.Landscapes Paragominas lidar AGB   ORNL 1648 (C2408633153-ORNL_CLOUD)  MgC/ha rasters
  5. Colombia IFN / IDEAM   SiB IPT DwC-A  (CC-BY)  dbh+species, 2015-2017
  6. BC ground plots PSP     FAIB FTP CSVs (OGL-BC)  TRUE coords (PSP subset only)
  7. Quebec PEP             Donnees Quebec GPKG (CC-BY)  dbh+species

Serial by design (per project OOM/serialise rule). Skip-if-exists (size>0). Verify sizes where the
resolver gave exact bytes. Earthdata (ORNL) uses ~/.netrc (machine urs.earthdata.nasa.gov) via curl -n.
Downloading does NOT load rasters into memory, so this is network-bound, not memory-bound; derivation
(carbon->AGB, allometry, coordinate reprojection) is a SEPARATE later step, deliberately not done here.

Run:  .venv/bin/python -u data/fetch_tier_a.py  > data/logs/fetch_tier_a.log 2>&1
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path("/scratch3/gsialelli/AGBD-Val/data")
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
UA = "AGBD-Val/1.0 (gsialelli@ethz.ch)"
COOKIES = "/tmp/urs_cookies_agbd"

DATA_EXT = (".csv", ".zip", ".tif", ".tiff", ".shp", ".dbf", ".shx", ".prj", ".rdata", ".tsv", ".xlsx")


def _api(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def _size(p: Path):
    return p.stat().st_size if p.exists() else 0


def get(url, dest: Path, netrc=False, expect_bytes=None):
    """Resumable single-file download. wget -c for open HTTP; curl -n for Earthdata redirects."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if _size(dest) > 0:
        if expect_bytes and _size(dest) != expect_bytes:
            print(f"[REDO] {dest.name}: {_size(dest)} != expected {expect_bytes}", flush=True)
            dest.unlink()
        else:
            print(f"[skip] {dest}  ({_size(dest):,} B)", flush=True)
            return "skip"
    print(f"[get ] {url}\n       -> {dest}", flush=True)
    if netrc:
        cmd = ["curl", "-sS", "-L", "-n", "-c", COOKIES, "-b", COOKIES,
               "--retry", "3", "--retry-delay", "5", "--max-time", "3600", "-C", "-",
               "-o", str(dest), url]
    else:
        cmd = ["wget", "-c", "--tries=4", "--timeout=300", "-U", UA, "-O", str(dest), url]
    subprocess.run(cmd)
    ok = _size(dest) > 0
    if expect_bytes and ok and _size(dest) != expect_bytes:
        print(f"[BAD ] {dest.name}: {_size(dest):,} != expected {expect_bytes:,}", flush=True)
        return "fail"
    print(f"[{'ok  ' if ok else 'FAIL'}] {dest}  ({_size(dest):,} B)", flush=True)
    return "ok" if ok else "fail"


def cmr_data_links(concept_id):
    """Enumerate ORNL granule DATA file URLs (rel .../data#) for a collection."""
    d = _api(f"https://cmr.earthdata.nasa.gov/search/granules.json"
             f"?concept_id={concept_id}&page_size=2000")
    hrefs = []
    for e in d["feed"]["entry"]:
        for l in e.get("links", []):
            href = l.get("href", "")
            rel = l.get("rel", "")
            if href.startswith("https://") and href.lower().endswith(DATA_EXT) \
                    and (rel.endswith("/data#") or "/protected/" in href):
                hrefs.append(href)
    return sorted(set(hrefs))


def main():
    tally = {"ok": 0, "skip": 0, "fail": 0}

    def do(url, dest, **kw):
        r = get(url, dest, **kw)
        tally[r] = tally.get(r, 0) + 1

    # ---- 1. BCI ForestGEO (Dryad) --------------------------------------------------------------
    print("\n=== 1. BCI ForestGEO 50-ha (Dryad, CC0) ===", flush=True)
    files = _api("https://datadryad.org/api/v2/versions/31849/files?per_page=100")
    want = {"bci.tree.zip", "bci.stem.zip", "bci.spptable.rdata", "BCIelev.tsv",
            "FullMeasurementBCI.zip"}  # skip the 109 MB MySQL dump (redundant)
    for f in files["_embedded"]["stash:files"]:
        name = f["path"]
        if name not in want:
            continue
        href = f["_links"]["stash:download"]["href"]
        do("https://datadryad.org" + href, ROOT / "bci-forestgeo" / name)

    # ---- 2. GAO/Asner Peru carbon (Zenodo) -----------------------------------------------------
    print("\n=== 2. GAO/Asner Peru ACD (Zenodo 4626309, CC-BY, MgC/ha) ===", flush=True)
    for fn, nb in (("peru_acd.tif", 1605318158), ("peru_acd_uncertainty.tif", 1605317964)):
        do(f"https://zenodo.org/api/records/4626309/files/{fn}/content",
           ROOT / "gao-peru-carbon" / fn, expect_bytes=nb)

    # ---- 3 + 4. Sustainable Landscapes Brazil (ORNL, Earthdata) --------------------------------
    for cid, sub, label in (("C2515314177-ORNL_CLOUD", "2007_field_inventory",
                             "3. SLB field inventory (ORNL 2007, dbh+species)"),
                            ("C2408633153-ORNL_CLOUD", "1648_paragominas_lidar_agb",
                             "4. SLB Paragominas lidar AGB (ORNL 1648, MgC/ha)")):
        print(f"\n=== {label} ===", flush=True)
        try:
            links = cmr_data_links(cid)
        except Exception as e:
            print(f"[FAIL] CMR enumerate {cid}: {e}", flush=True)
            tally["fail"] += 1
            continue
        print(f"[cmr ] {cid}: {len(links)} data files", flush=True)
        for href in links:
            do(href, ROOT / "sustainable-landscapes-brazil" / sub / href.rsplit("/", 1)[-1],
               netrc=True)

    # ---- 5. Colombia IFN / IDEAM (SiB IPT DwC-A) -----------------------------------------------
    print("\n=== 5. Colombia IFN / IDEAM (SiB IPT, CC-BY, 2015-2017) ===", flush=True)
    do("https://ipt.biodiversidad.co/sib/archive.do?r=ideam_ifn&v=2.1",
       ROOT / "colombia-ifn" / "ideam_ifn_dwca.zip")

    # ---- 6. BC ground plots PSP (FAIB) — TRUE coords subset ------------------------------------
    print("\n=== 6. BC ground plots PSP (FAIB, OGL-BC, TRUE coords) ===", flush=True)
    base = "https://www.for.gov.bc.ca/ftp/HTS/external/!publish/ground_plot_compilations/psp/"
    idx = urllib.request.urlopen(urllib.request.Request(base, headers={"User-Agent": UA}),
                                 timeout=90).read().decode("utf-8", "replace")
    import re
    for m in sorted(set(re.findall(r'href="([^"]+\.(?:csv|xlsx))"', idx, re.I))):
        name = m.rsplit("/", 1)[-1]
        url = m if m.startswith("http") else "https://www.for.gov.bc.ca" + m
        do(url, ROOT / "bc-ground-plots" / "psp" / name)

    # ---- 7. Quebec PEP (Donnees Quebec) --------------------------------------------------------
    print("\n=== 7. Quebec PEP (Donnees Quebec, CC-BY) ===", flush=True)
    qbase = "https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/DONNEES_FOR_ECO_SUD/Placettes_permanentes"
    do(f"{qbase}/02-Donnees/PROV/PEP_GPKG.zip", ROOT / "quebec-pep" / "PEP_GPKG.zip")
    do(f"{qbase}/01-Documentation/DICTIONNAIRE_PLACETTE.xlsx",
       ROOT / "quebec-pep" / "DICTIONNAIRE_PLACETTE.xlsx")

    print(f"\n=== DONE: ok={tally.get('ok',0)} skip={tally.get('skip',0)} "
          f"fail={tally.get('fail',0)} ===", flush=True)
    sys.exit(1 if tally.get("fail", 0) else 0)


if __name__ == "__main__":
    main()
