#!/usr/bin/env python
"""Download NEON Woody Plant Vegetation Structure (DP1.10098.001) for the AEF year window.

Why this product: it ships per-stem `stemDiameter` (cm), `height` (m), `taxonID` and plot IDs, i.e.
exactly the predictors Chojnacky et al. 2014 / Chave 2014 need. We aggregate to plot level (the user
does NOT want tree-by-tree numbers) -- but we must download stem level to be able to aggregate.

Playbook compliance:
- volume estimate FIRST (HEAD/size from the API manifest), printed before a byte is fetched;
- SERIAL, never concurrent (concurrent loads have OOMed / saturated this box before);
- RESUMABLE: skip-if-output-exists, and "exists" means "size matches the manifest", not just present;
- `python -u` unbuffered so progress survives a SIGKILL;
- writes NEON_STATUS.md so a later session can tell what actually landed.

Run:  .venv/bin/python -u data/fetch_neon.py --product DP1.10098.001 [--plan-only]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
API = "https://data.neonscience.org/api/v0"

# NEON gates the /data/ endpoints behind a free API token (as of 2026-07; /products and /releases
# are still anonymous, which is why scope resolution works and file listing 403s "Access Denied").
# Token: data.neonscience.org -> My Account -> GET API TOKEN. Put it in NEON_TOKEN or .neon_token.
TOKEN_FILE = ROOT / ".neon_token"


def neon_token() -> str | None:
    t = os.environ.get("NEON_TOKEN")
    if not t and TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text().strip()
    return t or None
# AEF window, relaxed by user to 2014-2025 (pre-2017 acceptable for slow-change/undisturbed sites).
YEAR_MIN, YEAR_MAX = 2014, 2025
# Which per-file types we actually need. NEON site-month packages bundle many tables; taking the
# whole package would multiply the volume for tables we never read.
WANTED_SUBSTR = ("apparentindividual", "mappingandtagging", "perplotperyear")


def _req(url):
    r = urllib.request.Request(url)
    t = neon_token()
    if t:
        r.add_header("X-API-Token", t)
    return r


def get_json(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(_req(url), timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            # 403 is a credential problem, not a transient one -- retrying 4x just wastes time
            # and buries the real cause. Fail loudly with the fix.
            if e.code == 403:
                raise SystemExit(
                    "\nHTTP 403 from the NEON /data/ endpoint -- this needs a free API token.\n"
                    "  1. sign in at https://data.neonscience.org  -> My Account -> GET API TOKEN\n"
                    f"  2. save it to {TOKEN_FILE}  (chmod 600)  or export NEON_TOKEN=...\n"
                    "  3. re-run this script; it is resumable and will pick up where it stopped.\n")
            if i == tries - 1:
                raise
            print(f"  [retry {i+1}] HTTPError {e.code} -- {url}", flush=True)
            time.sleep(5 * (i + 1))
        except (urllib.error.URLError, TimeoutError) as e:
            if i == tries - 1:
                raise
            print(f"  [retry {i+1}] {type(e).__name__} {e} -- {url}", flush=True)
            time.sleep(5 * (i + 1))


def in_window(month: str) -> bool:
    return YEAR_MIN <= int(month.split("-")[0]) <= YEAR_MAX


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", default="DP1.10098.001")
    ap.add_argument("--out", default=None)
    ap.add_argument("--plan-only", action="store_true",
                    help="resolve the manifest and print the volume estimate, download nothing")
    args = ap.parse_args()

    out = Path(args.out) if args.out else ROOT / "data" / "neon-veg-structure"
    out.mkdir(parents=True, exist_ok=True)

    prod = get_json(f"{API}/products/{args.product}")["data"]
    print(f"[product] {args.product}  {prod['productName']}", flush=True)

    site_months = []
    for sc in prod["siteCodes"]:
        for m in sc["availableMonths"]:
            if in_window(m):
                site_months.append((sc["siteCode"], m))
    site_months.sort()
    print(f"[scope  ] {len(site_months)} site-months in {YEAR_MIN}-{YEAR_MAX} "
          f"across {len({s for s,_ in site_months})} sites", flush=True)

    # ---- resolve the manifest (this is the slow, API-bound part) -------------------------------
    manifest = []   # (site, month, name, url, size)
    for i, (site, month) in enumerate(site_months, 1):
        try:
            files = get_json(f"{API}/data/{args.product}/{site}/{month}")["data"]["files"]
        except Exception as e:
            print(f"  [skip] {site}/{month}: {type(e).__name__} {e}", flush=True)
            continue
        for f in files:
            n = f["name"].lower()
            if n.endswith(".csv") and any(w in n for w in WANTED_SUBSTR) and "expanded" not in n:
                manifest.append((site, month, f["name"], f["url"], int(f["size"])))
        if i % 50 == 0:
            print(f"  [resolve] {i}/{len(site_months)} site-months, "
                  f"{len(manifest)} files, {sum(m[4] for m in manifest)/1e6:.0f} MB", flush=True)

    total = sum(m[4] for m in manifest)
    print(f"\n[VOLUME ] {len(manifest)} files, {total/1e6:.1f} MB "
          f"({total/1e9:.2f} GB) -- estimated BEFORE downloading", flush=True)
    (out / "VOLUME_ESTIMATE.txt").write_text(
        f"product={args.product}\nsite_months={len(site_months)}\nfiles={len(manifest)}\n"
        f"bytes={total}\nMB={total/1e6:.1f}\nwindow={YEAR_MIN}-{YEAR_MAX}\n")
    if args.plan_only:
        return

    # ---- serial resumable download -------------------------------------------------------------
    ok = skipped = failed = 0
    for i, (site, month, name, url, size) in enumerate(manifest, 1):
        dest = out / site / month / name
        # "exists" must mean "valid": size has to match the manifest, not merely be non-zero.
        if dest.exists() and dest.stat().st_size == size:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(_req(url), timeout=300) as r:
                dest.write_bytes(r.read())
            got = dest.stat().st_size
            if got != size:
                print(f"  [SIZE ] {name}: got {got} != manifest {size}", flush=True)
                failed += 1
            else:
                ok += 1
        except Exception as e:
            print(f"  [FAIL ] {site}/{month}/{name}: {type(e).__name__} {e}", flush=True)
            failed += 1
        if i % 100 == 0:
            print(f"  [dl] {i}/{len(manifest)}  ok={ok} skip={skipped} fail={failed}", flush=True)

    print(f"\n[DONE   ] ok={ok} skipped={skipped} failed={failed} of {len(manifest)}", flush=True)
    (out / "NEON_STATUS.md").write_text(
        f"# NEON {args.product} download status\n\n"
        f"- window: {YEAR_MIN}-{YEAR_MAX}\n- site-months in window: {len(site_months)}\n"
        f"- files in manifest: {len(manifest)} ({total/1e6:.1f} MB)\n"
        f"- downloaded ok: {ok}\n- skipped (already valid): {skipped}\n- FAILED: {failed}\n\n"
        f"Tables kept: {', '.join(WANTED_SUBSTR)} (basic package only).\n"
        f"`apparentindividual` = stemDiameter/height per tag; `mappingandtagging` = taxonID;\n"
        f"`perplotperyear` = plot area + sampling design (needed to convert kg -> Mg/ha).\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
