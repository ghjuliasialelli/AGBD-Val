#!/usr/bin/env python
"""Derive AGB [Mg/ha] from the GAO Sabah aboveground CARBON density (ACD, Mg C/ha) raster.

The GAO product is CARBON, not biomass (Asner et al. 2018). AGB = ACD / carbon_fraction.
This is the silent halving trap: skipping the conversion under-reports biomass ~2x.

Playbook compliance:
- nodata (-9999) is masked on the RAW values, before the arithmetic.
- carbon_fraction is a FLAG (default 0.48, Asner/Mascaro tropical), not a buried constant.
- records the source raster's mtime + sha256 so any number is traceable to the exact input.

Run:  .venv/bin/python derive_agb/extract_gao_sabah.py [--cf 0.48]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parent))
from allometry import acd_to_agb  # noqa: E402

ROOT = Path("/scratch3/gsialelli/AGBD-Val")
SRC = ROOT / "data" / "gao-sabah-carbon" / "GAO_ACD_30m_unmasked.tif"
OUT = ROOT / "data" / "derived"
OUT.mkdir(exist_ok=True)
OUT_TIF = OUT / "GAO_Sabah_AGB_30m.tif"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cf", type=float, default=0.48,
                    help="carbon fraction (Asner/Mascaro tropical 0.48; IPCC 0.47)")
    args = ap.parse_args()

    with rasterio.open(SRC) as src:
        acd = src.read(1)                      # raw values, ACD [Mg C/ha]
        profile = src.profile
        nodata = src.nodata if src.nodata is not None else -9999.0

    # TWO nodata conventions coexist in this file: the declared -9999 sentinel AND bare NaN
    # (0.0247% of pixels). Masking only the declared one let NaN through and turned every
    # summary statistic into nan -- the silent version of this bug would have been a mean
    # poisoned by -9999/0.48 = -20831 Mg/ha. Mask BOTH, on the RAW values, before arithmetic.
    mask = (acd == nodata) | ~np.isfinite(acd)
    n_sentinel = int((acd == nodata).sum())
    n_nan = int((~np.isfinite(acd)).sum())
    n_other_neg = int(((acd < 0) & ~mask).sum())
    if n_other_neg:
        print(f"[warn ] {n_other_neg:,} finite NEGATIVE ACD pixels that are not the sentinel "
              f"-- these are masked too (carbon density cannot be < 0)")
        mask |= (acd < 0) & np.isfinite(acd)

    agb = acd_to_agb(acd, carbon_fraction=args.cf).astype("float32")
    agb[mask] = nodata                         # keep the sentinel where input was nodata

    valid = agb[~mask]
    assert np.isfinite(valid).all() and (valid >= 0).all(), "non-finite/negative AGB survived masking"
    print(f"[mask ] sentinel={n_sentinel:,}  nan={n_nan:,}  other_neg={n_other_neg:,}  "
          f"masked={int(mask.sum()):,} / {acd.size:,} ({100*mask.mean():.2f}%)")
    profile.update(dtype="float32", nodata=nodata, compress="lzw")
    with rasterio.open(OUT_TIF, "w", **profile) as dst:
        dst.write(agb, 1)

    prov = {
        "output": str(OUT_TIF),
        "source": str(SRC),
        "source_mtime": SRC.stat().st_mtime,
        "source_sha256": sha256(SRC),
        "variable_in": "ACD (aboveground carbon density) [Mg C/ha]",
        "variable_out": "AGB (aboveground biomass) [Mg/ha]",
        "carbon_fraction": args.cf,
        "equation": "AGB = ACD / carbon_fraction",
        "citation": "Asner et al. 2018 Biol. Conserv. 217:289 (GAO Sabah ACD)",
        "nodata": nodata,
        "nodata_conventions_masked": ["-9999 sentinel", "NaN", "finite negatives"],
        "n_masked_px": int(mask.sum()),
        "n_sentinel_px": n_sentinel, "n_nan_px": n_nan, "n_other_negative_px": n_other_neg,
        "n_valid_px": int(valid.size),
        "agb_min": float(valid.min()), "agb_max": float(valid.max()),
        "agb_mean": float(valid.mean()), "agb_median": float(np.median(valid)),
    }
    (OUT / "GAO_Sabah_AGB_30m.provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"[write] {OUT_TIF}")
    print(f"[stats] valid px={valid.size:,}  AGB Mg/ha: min={valid.min():.1f} "
          f"mean={valid.mean():.1f} median={np.median(valid):.1f} max={valid.max():.1f}  (cf={args.cf})")
    print(f"[prov ] {OUT/'GAO_Sabah_AGB_30m.provenance.json'}")


if __name__ == "__main__":
    main()
