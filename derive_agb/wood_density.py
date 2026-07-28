"""Wood-density lookup from the Global Wood Density Database (Zanne et al. 2009), as bundled/cleaned by
the R BIOMASS package (data/wdData.rda). Mirrors BIOMASS::getWoodDensity's taxonomic fallback:

  species mean -> genus mean -> family mean -> regional/dataset mean,

recording which LEVEL supplied each value (never silently defaulting). Region-restricted means are used
for genus/family fallbacks so the estimate is biogeographically appropriate; species-level uses the
global record set (a species' wood density is a species property). Family is resolved from genus via
the BIOMASS genusFamily table when the input lacks it.

Citation: Zanne A.E. et al. 2009, Global wood density database, Dryad doi:10.5061/dryad.234;
Chave et al. 2009 Ecology Letters. Values in g cm^-3 (oven-dry mass / green volume).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

_DIR = Path("/scratch3/gsialelli/AGBD-Val/data/wood-density")
_WD = None
_G2F = None


def _load():
    global _WD, _G2F
    if _WD is None:
        _WD = pd.read_csv(_DIR / "global_wood_density_zanne2009.csv")
        gf = pd.read_csv(_DIR / "genus_family.csv")
        _G2F = dict(zip(gf["genus"], gf["family"]))
    return _WD, _G2F


def lookup(genus, species, region_id=None):
    """Vectorised. genus, species: array-like (species may be NaN). region_id: e.g. 'SouthAmericaTrop'
    (see wdData.regionId) restricts the genus/family fallback means; None = global. Returns
    (wd: float array, level: object array in {'species','genus','family','region','none'})."""
    wd, g2f = _load()
    g = pd.Series(genus, dtype="object").str.strip().str.capitalize()
    s = pd.Series(species, dtype="object").astype("object").str.strip().str.lower()

    reg = wd[wd["regionId"] == region_id] if region_id else wd
    sp_mean = wd.groupby(["genus", "species"])["wd"].mean()          # species: global
    gen_mean = reg.groupby("genus")["wd"].mean()                     # genus: region-restricted
    fam_mean = reg.groupby("family")["wd"].mean()                    # family: region-restricted
    region_mean = float(reg["wd"].mean()) if len(reg) else float(wd["wd"].mean())

    n = len(g)
    out = np.full(n, np.nan)
    lvl = np.array(["none"] * n, dtype=object)
    fam = g.map(lambda x: g2f.get(x) if isinstance(x, str) else None)

    for i in range(n):
        gi, si, fi = g.iat[i], s.iat[i], fam.iat[i]
        if isinstance(gi, str) and isinstance(si, str) and (gi, si) in sp_mean.index:
            out[i] = sp_mean.loc[(gi, si)]; lvl[i] = "species"
        elif isinstance(gi, str) and gi in gen_mean.index:
            out[i] = gen_mean.loc[gi]; lvl[i] = "genus"
        elif isinstance(fi, str) and fi in fam_mean.index:
            out[i] = fam_mean.loc[fi]; lvl[i] = "family"
        else:
            out[i] = region_mean; lvl[i] = "region"
    return out, lvl
