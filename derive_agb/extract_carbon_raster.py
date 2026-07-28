#!/usr/bin/env python
"""Convert an above-ground CARBON density raster (MgC/ha) to above-ground BIOMASS (Mg/ha).

The halving trap: ACD (Mg C/ha) is NOT AGB (Mg/ha). AGB = ACD / carbon_fraction.
Handles both GAO/Asner Peru (EPSG:32718, 100 m, ~401 M px -> processed WINDOWED to stay in RAM)
and the SLB Paragominas layers. Nodata is masked on RAW values (sentinel AND NaN AND finite-negatives)
BEFORE the divide, per the playbook, then re-stamped; population stats asserted over the whole raster.

Carbon fraction default 0.48 (Asner/Mascaro tropical); a FLAG, not a buried constant — a wrong value
silently scales all biomass by ~2x. Cite the value used.

Run:  .venv/bin/python -u derive_agb/extract_carbon_raster.py --src <in.tif> --dst <out.tif> [--cf 0.48]
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window


def sha256(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--cf", type=float, default=0.48, help="carbon fraction (Asner tropical 0.48; IPCC 0.47)")
    args = ap.parse_args()
    src, dst = Path(args.src), Path(args.dst)

    with rasterio.open(src) as s:
        prof = s.profile.copy()
        nod = s.nodata if s.nodata is not None else -9999.0
        prof.update(dtype="float32", nodata=nod, count=1, compress="deflate")
        for k in ("blockxsize", "blockysize", "tiled"):
            prof.pop(k, None)  # avoid inheriting a non-16-multiple source block size
        n_valid = 0
        n_sent = n_nan = n_neg = 0
        vmin, vmax, vsum = np.inf, -np.inf, 0.0
        dst.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(dst, "w", **prof) as d:
            for _, win in s.block_windows(1):
                acd = s.read(1, window=win).astype("float64")
                sent = (acd == nod)
                nan = ~np.isfinite(acd) & ~sent
                neg = (acd < 0) & np.isfinite(acd) & ~sent
                mask = sent | nan | neg
                n_sent += int(sent.sum()); n_nan += int(nan.sum()); n_neg += int(neg.sum())
                agb = (acd / args.cf).astype("float32")
                agb[mask] = nod
                d.write(agb, 1, window=win)
                v = agb[~mask]
                if v.size:
                    n_valid += v.size
                    vmin = min(vmin, float(v.min())); vmax = max(vmax, float(v.max()))
                    vsum += float(v.sum())
        mean = vsum / n_valid if n_valid else float("nan")

    assert n_valid > 0, "no valid pixels -- check nodata handling"
    assert np.isfinite(mean) and vmin >= 0.0, f"bad stats min={vmin} mean={mean}"
    print(f"[{src.name}] valid={n_valid:,} masked(sent={n_sent:,} nan={n_nan:,} neg={n_neg:,}) "
          f"cf={args.cf}")
    print(f"[{dst.name}] AGB Mg/ha: min={vmin:.2f} max={vmax:.2f} mean={mean:.2f}")

    prov = {
        "output": str(dst), "source": str(src), "source_sha256": sha256(src),
        "source_mtime": src.stat().st_mtime,
        "transform": "AGB = ACD / carbon_fraction (carbon->biomass)",
        "carbon_fraction": args.cf, "carbon_fraction_ref": "Asner & Mascaro 2014 (tropical 0.48)",
        "n_valid_px": n_valid, "agb_min": vmin, "agb_max": vmax, "agb_mean_mg_ha": mean,
        "nodata": nod,
    }
    Path(str(dst) + ".provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[prov] {dst}.provenance.json")


if __name__ == "__main__":
    main()
