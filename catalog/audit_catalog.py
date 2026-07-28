#!/usr/bin/env python3
"""Metadata-only audit + build for the AGB reference catalog.

Runs entirely on the catalog metadata (no data downloads). Asserts invariants over the WHOLE
catalog and exits non-zero on any failure, so it can gate a pipeline. Also cross-checks the
hand-authored CSV against the authoritative JSON, and can regenerate the CSV from the JSON.

Usage:
    python -u audit_catalog.py                 # audit JSON + check CSV/JSON parity
    python -u audit_catalog.py --rebuild-csv   # regenerate CSV from JSON (authoritative), then audit
    python -u audit_catalog.py --check-urls     # also HEAD each portal_url (needs network; non-fatal)

The JSON (agb_reference_catalog.json) is the single source of truth. The CSV is a derived,
greppable view; --rebuild-csv guarantees they agree.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "agb_reference_catalog.json"
CSV_PATH = HERE / "agb_reference_catalog.csv"

# Column order for the CSV view (must match the CSV header).
COLUMNS = [
    "id", "name", "category", "subtype", "provider", "coverage_scope", "region", "variable",
    "units", "representation", "support_size", "temporal_coverage", "geometry_type", "native_crs",
    "coord_availability", "coord_usability_tier", "n_records_or_area", "access", "license",
    "format", "portal_url", "doi", "citation_short", "verified", "validation_caveats",
]

# Fields that must be present and non-empty on every row.
REQUIRED_NONEMPTY = [
    "id", "name", "category", "subtype", "provider", "coverage_scope", "variable", "units",
    "representation", "coord_availability", "coord_usability_tier", "access", "portal_url",
    "verified",
]

ENUMS = {
    "category": {"in-situ-plot", "airborne-lidar-agb"},
    "subtype": {"nfi", "plot-network", "supersite", "mapped-plot", "research-campaign"},
    "variable": {"AGB", "AGC", "growing-stock-volume", "canopy-structure"},
    "representation": {"point-plot", "mapped-plot", "transect-raster", "wall-to-wall-raster", "mixed"},
    "coord_availability": {"public-exact", "public-fuzzed", "restricted", "on-request", "site-known"},
    "coord_usability_tier": {"pixel", "aggregate", "restricted"},
}


def load_json():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def audit(datasets):
    """Return list of error strings; empty == pass."""
    errors = []
    ids = [d.get("id", "") for d in datasets]

    # unique, non-empty ids
    seen = set()
    for i in ids:
        if not i:
            errors.append("empty id found")
        elif i in seen:
            errors.append(f"duplicate id: {i}")
        seen.add(i)

    for d in datasets:
        rid = d.get("id", "<no-id>")
        for field in REQUIRED_NONEMPTY:
            if not str(d.get(field, "")).strip():
                errors.append(f"[{rid}] required field empty: {field}")
        for field, allowed in ENUMS.items():
            val = d.get(field, "")
            if val and val not in allowed:
                errors.append(f"[{rid}] {field}='{val}' not in {sorted(allowed)}")
        # portal_url shape
        url = d.get("portal_url", "")
        if url and not url.startswith(("http://", "https://")):
            errors.append(f"[{rid}] portal_url not http(s): {url}")
        # units sanity vs variable (carbon must be MgC, not silently Mg)
        var, units = d.get("variable", ""), d.get("units", "")
        if var == "AGC" and "MgC" not in units and "Mg C" not in units:
            errors.append(f"[{rid}] variable=AGC but units='{units}' lack MgC (carbon-vs-biomass trap)")

    return errors


def check_csv_parity(datasets):
    """Ensure the CSV id-set matches the JSON id-set (catches hand-authoring drift)."""
    errors = []
    if not CSV_PATH.exists():
        return [f"CSV missing: {CSV_PATH}"]
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            errors.append("CSV header does not match expected COLUMNS order")
        csv_ids = {row["id"] for row in reader}
    json_ids = {d["id"] for d in datasets}
    for missing in sorted(json_ids - csv_ids):
        errors.append(f"id in JSON but not CSV: {missing}")
    for extra in sorted(csv_ids - json_ids):
        errors.append(f"id in CSV but not JSON: {extra}")
    return errors


def rebuild_csv(datasets):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for d in datasets:
            writer.writerow({c: d.get(c, "") for c in COLUMNS})
    print(f"[rebuild] wrote {len(datasets)} rows -> {CSV_PATH.name}")


def check_urls(datasets):
    """Optional, non-fatal: HEAD each portal_url. Requires network."""
    import urllib.request
    import urllib.error
    print("[urls] checking portal_url resolvability (non-fatal)...")
    for d in datasets:
        url = d.get("portal_url", "")
        if not url:
            continue
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "agbd-val-audit"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f"  OK  {r.status}  {d['id']}")
        except Exception as e:  # noqa: BLE001 - reachability probe, any error is just a warning
            print(f"  WARN      {d['id']}: {e}")


def summarize(datasets):
    from collections import Counter
    print(f"\n=== catalog summary: {len(datasets)} datasets ===")
    for key in ("category", "coord_usability_tier", "variable", "subtype"):
        counts = Counter(d.get(key, "") for d in datasets)
        pretty = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  by {key:20s}: {pretty}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild-csv", action="store_true", help="regenerate CSV from JSON, then audit")
    ap.add_argument("--check-urls", action="store_true", help="HEAD each portal_url (needs network)")
    args = ap.parse_args()

    data = load_json()
    datasets = data["datasets"]

    if args.rebuild_csv:
        rebuild_csv(datasets)

    errors = audit(datasets) + check_csv_parity(datasets)

    summarize(datasets)

    if args.check_urls:
        check_urls(datasets)

    if errors:
        print(f"\nFAIL: {len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("\nPASS: all metadata invariants hold.")


if __name__ == "__main__":
    main()
