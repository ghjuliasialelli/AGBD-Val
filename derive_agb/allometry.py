"""Allometric AGB equations for deriving above-ground biomass from structure data.

Every model here is a PUBLISHED equation with an explicit citation and validity domain.
Coefficients are function defaults / arguments (flags, not buried constants) so they can be
overridden per site. Nothing fabricates a calibration: models that require site-specific
coefficients raise NotCalibratedError rather than guessing.

Units are stated per function. The single most common silent bug in this domain is a units
mismatch (DBH cm vs m; AGB kg vs Mg; carbon MgC vs biomass Mg) -> every function documents them.
"""
from __future__ import annotations
import numpy as np


class NotCalibratedError(RuntimeError):
    """Raised when an area-based model is requested without published coefficients for the site."""


# --------------------------------------------------------------------------------------
# Tree-level allometry — Chave et al. 2014 (Glob. Change Biol. 20:3177), pantropical.
# --------------------------------------------------------------------------------------
def chave2014_agb_H(dbh_cm, wood_density, height_m):
    """Chave et al. 2014, Eq. 4 (with height). AGB per tree in KILOGRAMS.

    dbh_cm       : stem diameter at breast height [cm]
    wood_density : wood specific gravity / density [g cm^-3]  (oven-dry mass / green volume)
    height_m     : total tree height [m]
        AGB = 0.0673 * (rho * D^2 * H)^0.976
    """
    D = np.asarray(dbh_cm, float)
    rho = np.asarray(wood_density, float)
    H = np.asarray(height_m, float)
    return 0.0673 * (rho * D**2 * H) ** 0.976


def chave2005_agb_moist(dbh_cm, wood_density):
    """Chave et al. 2005 (Oecologia 145:87), MOIST-forest pantropical, DIAMETER-ONLY. AGB in KILOGRAMS.

    Use when neither height nor Chave's E index is available (e.g. Colombia IFN gives only dbh+species).
    dbh_cm : diameter at breast height [cm];  wood_density : wood specific gravity [g cm^-3].
        AGB = rho * exp(-1.499 + 2.148*ln(D) + 0.207*ln(D)^2 - 0.0281*ln(D)^3)
    Valid ~5-156 cm DBH. Less accurate than the height/E forms; cite it explicitly where used.
    """
    D = np.asarray(dbh_cm, float)
    rho = np.asarray(wood_density, float)
    lnD = np.log(D)
    return rho * np.exp(-1.499 + 2.148 * lnD + 0.207 * lnD**2 - 0.0281 * lnD**3)


def chave2014_agb_noH(dbh_cm, wood_density, E):
    """Chave et al. 2014, Eq. 7 (no height; uses environmental stress index E). AGB in KILOGRAMS.

    E is Chave's bioclimatic index (dimensionless), available as a global 2.5-arcmin raster or
    computed from temperature seasonality, climatic water deficit and precipitation seasonality.
        AGB = exp(-1.803 - 0.976*E + 0.976*ln(rho) + 2.673*ln(D) - 0.0299*ln(D)^2)
    """
    D = np.asarray(dbh_cm, float)
    rho = np.asarray(wood_density, float)
    E = np.asarray(E, float)
    lnD = np.log(D)
    return np.exp(-1.803 - 0.976 * E + 0.976 * np.log(rho) + 2.673 * lnD - 0.0299 * lnD**2)


# --------------------------------------------------------------------------------------
# Tree-level allometry — Chojnacky, Heath & Jenkins 2014 (Forestry 87:129-151), USA
# (updates Jenkins et al. 2003). For NEON / FIA. AGB = exp(b0 + b1 * ln(D)) in KILOGRAMS.
#
# THE FULL, AUTHORITATIVE Table 5 (all 35 groups: 13 conifer, 18 hardwood, 4 woodland),
# transcribed verbatim from the paper (derive_agb/refs/Chojnacky2014_Forestry.pdf, p.140).
# Groups are split by wood specific gravity (spg); see chojnacky_group() for the taxon->group
# resolver. `measure` is the diameter convention the equation was fitted on:
#   'dbh' = diameter at breast height (~130 cm), 'drc' = diameter at root collar (woodland,
#   multi-stem juniper/pinyon/mesquite/scrub-oak). MIXING THESE SILENTLY BIASES BIOMASS.
#
# NOTE: the previous version of this table carried approximate/incorrect coefficients for
# "pine" (-2.5356, 2.4349) and "spruce" (-2.5384, 2.4814) that matched NEITHER real Pinus nor
# Picea group in the paper. Verified and replaced 2026-07-24 against the source PDF.
# --------------------------------------------------------------------------------------
CHOJNACKY2014_TABLE5 = {
    # key: (b0, b1, measure)
    # --- conifers (13) ---
    "conifer_Abies_lt035":        (-2.3123, 2.3482, "dbh"),
    "conifer_Abies_ge035":        (-3.1774, 2.6426, "dbh"),
    "conifer_Cupressaceae_lt030": (-1.9615, 2.1063, "dbh"),
    "conifer_Cupressaceae_030_039": (-2.7765, 2.4195, "dbh"),
    "conifer_Cupressaceae_ge040": (-2.6327, 2.4757, "dbh"),
    "conifer_Larix":              (-2.3012, 2.3853, "dbh"),
    "conifer_Picea_lt035":        (-3.0300, 2.5567, "dbh"),
    "conifer_Picea_ge035":        (-2.1364, 2.3233, "dbh"),
    "conifer_Pinus_lt045":        (-2.6177, 2.4638, "dbh"),
    "conifer_Pinus_ge045":        (-3.0506, 2.6465, "dbh"),
    "conifer_Pseudotsuga":        (-2.4623, 2.4852, "dbh"),
    "conifer_Tsuga_lt040":        (-2.3480, 2.3876, "dbh"),
    "conifer_Tsuga_ge040":        (-2.9208, 2.5697, "dbh"),
    # --- hardwoods (18) ---
    "hardwood_Aceraceae_lt050":   (-2.0470, 2.3852, "dbh"),
    "hardwood_Aceraceae_ge050":   (-1.8011, 2.3852, "dbh"),
    "hardwood_Betulaceae_lt040":  (-2.5932, 2.5349, "dbh"),
    "hardwood_Betulaceae_040_049": (-2.2271, 2.4513, "dbh"),
    "hardwood_Betulaceae_050_059": (-1.8096, 2.3480, "dbh"),
    "hardwood_Betulaceae_ge060":  (-2.2652, 2.5349, "dbh"),
    "hardwood_mixed":             (-2.2118, 2.4133, "dbh"),  # Cornaceae/Ericaceae/Lauraceae/Platanaceae/Rosaceae/Ulmaceae
    "hardwood_Fabaceae_Juglandaceae_Carya": (-2.5095, 2.6175, "dbh"),
    "hardwood_Fabaceae_Juglandaceae_other": (-2.5095, 2.5437, "dbh"),
    "hardwood_Fagaceae_deciduous": (-2.0705, 2.4410, "dbh"),
    "hardwood_Fagaceae_evergreen": (-2.2198, 2.4410, "dbh"),
    "hardwood_Hamamelidaceae":    (-2.6390, 2.5466, "dbh"),
    "hardwood_Hippocastanaceae_Tiliaceae": (-2.4108, 2.4177, "dbh"),
    "hardwood_Magnoliaceae":      (-2.5497, 2.5011, "dbh"),
    "hardwood_Oleaceae_lt055":    (-2.0314, 2.3524, "dbh"),
    "hardwood_Oleaceae_ge055":    (-1.8384, 2.3524, "dbh"),
    "hardwood_Salicaceae_lt035":  (-2.6863, 2.4561, "dbh"),
    "hardwood_Salicaceae_ge035":  (-2.4441, 2.4561, "dbh"),
    # --- woodland (4) — fitted on drc, NOT dbh ---
    "woodland_Cupressaceae":      (-2.7096, 2.1942, "drc"),
    "woodland_Fabaceae_Rosaceae": (-2.9255, 2.4109, "drc"),
    "woodland_Fagaceae":          (-3.0304, 2.4982, "drc"),
    "woodland_Pinaceae":          (-3.2007, 2.5339, "drc"),
}


def chojnacky2014_agb(diameter_cm, group):
    """Chojnacky et al. 2014 generalized US allometry. AGB per tree in KILOGRAMS.

    group : one of CHOJNACKY2014_TABLE5 keys. Use chojnacky_group() to resolve a species.
    diameter_cm : dbh for forest groups, drc for woodland_* groups (see the group's `measure`).
    """
    if group not in CHOJNACKY2014_TABLE5:
        raise NotCalibratedError(
            f"no Chojnacky-2014 group '{group}'. Resolve the taxon with chojnacky_group() "
            f"or pick from {sorted(CHOJNACKY2014_TABLE5)}."
        )
    b0, b1, _measure = CHOJNACKY2014_TABLE5[group]
    D = np.asarray(diameter_cm, float)
    return np.exp(b0 + b1 * np.log(D))


# --------------------------------------------------------------------------------------
# Carbon <-> biomass. THE halving trap: ACD (Mg C / ha) is NOT AGB (Mg / ha).
# --------------------------------------------------------------------------------------
def acd_to_agb(acd, carbon_fraction=0.48):
    """Above-ground carbon density -> above-ground biomass. Same spatial units in and out.

    carbon_fraction : mass fraction of carbon in dry biomass. Default 0.48 (Asner/Mascaro,
        tropical); IPCC generic default is 0.47. This is a FLAG on purpose — a wrong value
        silently scales all biomass by ~2x. Cite the value you use.
    """
    return np.asarray(acd, float) / float(carbon_fraction)


def agb_to_acd(agb, carbon_fraction=0.48):
    """Inverse of acd_to_agb."""
    return np.asarray(agb, float) * float(carbon_fraction)


# --------------------------------------------------------------------------------------
# Area-based lidar height -> AGB/ACD. Coefficients are STRICTLY per published calibration.
# --------------------------------------------------------------------------------------
def asner_tch_to_acd(tch_m, a, b):
    """Asner & Mascaro (2014) form ACD = a * TCH^b [Mg C / ha]. Coefficients are regional and
    MUST be supplied from a published calibration for the site (e.g. Asner et al. 2018 for
    Malaysian Borneo used a region-specific fit). No default is provided — passing wrong
    coefficients yields plausible, wrong carbon."""
    return float(a) * np.asarray(tch_m, float) ** float(b)


def lvis_rh_to_agb(*_args, **_kwargs):
    """AfriSAR LVIS RH-metric area-based AGB. Requires the campaign-specific published model
    (e.g. Duncanson et al. 2017 / the AfriSAR AGB workflow). We do NOT ship coefficients here:
    the AfriSAR ready-made AGB product (ORNL 1681) already encodes that calibration. Use 1681
    for values; use this hook only if you have the exact published RH->AGB coefficients."""
    raise NotCalibratedError(
        "LVIS RH->AGB needs AfriSAR-specific published coefficients. For ready AGB use ORNL 1681 "
        "(afrisar-agb-1681/). Supply coefficients explicitly to calibrate an independent model."
    )
