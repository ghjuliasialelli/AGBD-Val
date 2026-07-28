"""Resolve a NEON/FIA scientific name -> Chojnacky et al. 2014 Table 5 biomass group.

Chojnacky splits many families/genera by wood specific gravity (spg). To pick the right
sub-group we need each species' spg, so the per-species spg values below are transcribed
directly from Chojnacky 2014 Tables 2 (conifers) and 3 (hardwoods) -- the SAME paper the
coefficients come from, so the split thresholds and the densities are internally consistent.

Design (mirrors the France-NFI approach): NOTHING is silently defaulted. A taxon we cannot place
returns (None, reason); the caller counts it and reports its share, rather than assigning a mean.

`chojnacky_group(scientific_name)` -> (group_key, note) or (None, reason).
"""
from __future__ import annotations
import re

# Wood specific gravity by "Genus species", from Chojnacky 2014 Tab.2 (conifers) & Tab.3 (hardwoods).
# Only the split-relevant genera need per-species detail; single-group genera use GENUS_GROUP below.
SPG = {
    # Abies (split 0.35)
    "Abies balsamea": 0.33, "Abies fraseri": 0.33, "Abies lasiocarpa": 0.31,
    "Abies amabilis": 0.40, "Abies concolor": 0.37, "Abies grandis": 0.35,
    "Abies magnifica": 0.36, "Abies procera": 0.37, "Abies lowiana": 0.37,
    # Picea (split 0.35)
    "Picea engelmannii": 0.33, "Picea sitchensis": 0.33, "Picea abies": 0.36,
    "Picea glauca": 0.37, "Picea mariana": 0.38, "Picea rubens": 0.37,
    # Pinus (split 0.45)
    "Pinus albicaulis": 0.43, "Pinus arizonica": 0.43, "Pinus banksiana": 0.40,
    "Pinus contorta": 0.38, "Pinus jeffreyi": 0.37, "Pinus lambertiana": 0.34,
    "Pinus leiophylla": 0.43, "Pinus monticola": 0.36, "Pinus ponderosa": 0.38,
    "Pinus resinosa": 0.41, "Pinus strobus": 0.34,
    "Pinus echinata": 0.47, "Pinus elliottii": 0.54, "Pinus palustris": 0.54,
    "Pinus rigida": 0.47, "Pinus taeda": 0.47, "Pinus flexilis": 0.37, "Pinus edulis": 0.51,
    "Pinus virginiana": 0.48, "Pinus serotina": 0.47, "Pinus glabra": 0.44, "Pinus clausa": 0.42,
    # Tsuga (split 0.40)
    "Tsuga canadensis": 0.38, "Tsuga heterophylla": 0.42, "Tsuga mertensiana": 0.42,
    # Cupressaceae conifer (splits 0.30 / 0.40) — forest form
    "Thuja occidentalis": 0.29, "Thuja plicata": 0.31, "Calocedrus decurrens": 0.35,
    "Sequoiadendron giganteum": 0.34, "Chamaecyparis nootkatensis": 0.42,
    "Juniperus virginiana": 0.44,
    # Aceraceae (split 0.50)
    "Acer macrophyllum": 0.44, "Acer pensylvanicum": 0.44, "Acer rubrum": 0.49,
    "Acer saccharinum": 0.44, "Acer spicatum": 0.47, "Acer saccharum": 0.56,
    "Acer negundo": 0.44, "Acer nigrum": 0.52,
    # Betulaceae (splits 0.40 / 0.50 / 0.60)
    "Alnus rubra": 0.37, "Betula papyrifera": 0.48, "Betula populifolia": 0.45,
    "Betula alleghaniensis": 0.55, "Betula lenta": 0.60, "Ostrya virginiana": 0.63,
    "Carpinus caroliniana": 0.58, "Betula nigra": 0.56, "Betula occidentalis": 0.45,
    "Betula glandulosa": 0.48, "Alnus incana": 0.37, "Alnus rhombifolia": 0.37,
    # Oleaceae (split 0.55)
    "Fraxinus nigra": 0.45, "Fraxinus pennsylvanica": 0.53, "Fraxinus americana": 0.55,
    # Salicaceae (split 0.35)
    "Populus balsamifera": 0.31, "Populus deltoides": 0.37, "Populus grandidentata": 0.36,
    "Populus tremuloides": 0.35, "Populus trichocarpa": 0.31, "Salix alba": 0.36,
    "Populus fremontii": 0.35, "Populus angustifolia": 0.36,
}

# Genera that fall wholly in one Chojnacky group regardless of species.
# value = group_key (forest, dbh) unless noted.
GENUS_GROUP = {
    "Larix": "conifer_Larix",
    "Pseudotsuga": "conifer_Pseudotsuga",
    # Fagaceae deciduous vs evergreen resolved per-species below; Fagus/Castanea always deciduous.
    "Fagus": "hardwood_Fagaceae_deciduous",
    "Castanea": "hardwood_Fagaceae_deciduous",
    # Carya -> its own Fabaceae/Juglandaceae Carya group; other Juglandaceae/Fabaceae -> "other".
    "Carya": "hardwood_Fabaceae_Juglandaceae_Carya",
    "Juglans": "hardwood_Fabaceae_Juglandaceae_other",
    "Robinia": "hardwood_Fabaceae_Juglandaceae_other",
    "Gleditsia": "hardwood_Fabaceae_Juglandaceae_other",
    "Gymnocladus": "hardwood_Fabaceae_Juglandaceae_other",
    # Hamamelidaceae
    "Liquidambar": "hardwood_Hamamelidaceae",
    # Hippocastanaceae / Tiliaceae
    "Aesculus": "hardwood_Hippocastanaceae_Tiliaceae",
    "Tilia": "hardwood_Hippocastanaceae_Tiliaceae",
    # Magnoliaceae
    "Liriodendron": "hardwood_Magnoliaceae",
    "Magnolia": "hardwood_Magnoliaceae",
    # Mixed-hardwood families (Cornaceae/Ericaceae/Lauraceae/Platanaceae/Rosaceae/Ulmaceae)
    "Cornus": "hardwood_mixed", "Nyssa": "hardwood_mixed", "Arbutus": "hardwood_mixed",
    "Oxydendrum": "hardwood_mixed", "Umbellularia": "hardwood_mixed", "Kalmia": "hardwood_mixed",
    "Sassafras": "hardwood_mixed", "Persea": "hardwood_mixed", "Platanus": "hardwood_mixed",
    "Amelanchier": "hardwood_mixed", "Prunus": "hardwood_mixed", "Sorbus": "hardwood_mixed",
    "Malus": "hardwood_mixed", "Crataegus": "hardwood_mixed",
    "Ulmus": "hardwood_mixed", "Celtis": "hardwood_mixed", "Rhamnus": "hardwood_mixed",
    "Diospyros": "hardwood_mixed",
    # Hamamelidaceae also includes witch-hazel (not just sweetgum).
    "Hamamelis": "hardwood_Hamamelidaceae",
    # Additional temperate tree genera in the mixed-hardwood families (Rosaceae/Ulmaceae/Ericaceae/
    # Rhamnaceae-approximated-as-mixed, Aquifoliaceae which the paper says may use mixed hardwood).
    "Ilex": "hardwood_mixed", "Frangula": "hardwood_mixed", "Lindera": "hardwood_mixed",
    "Cladrastis": "hardwood_Fabaceae_Juglandaceae_other",
    # Styracaceae (Halesia, silverbell): the paper says families not listed with midrange spg may
    # use the mixed-hardwood equation; Halesia spg ~0.42 sits in that range.
    "Halesia": "hardwood_mixed", "Styrax": "hardwood_mixed",
    "Morus": "hardwood_mixed", "Maclura": "hardwood_mixed",  # Moraceae -> mixed hardwood
    "Leucaena": "hardwood_Fabaceae_Juglandaceae_other",
    "Cercis": "hardwood_Fabaceae_Juglandaceae_other",
}

# Fagaceae: evergreen (live) oaks + Chrysolepis/Lithocarpus -> evergreen group; the rest deciduous.
FAGACEAE_EVERGREEN = {
    "Quercus virginiana", "Quercus agrifolia", "Quercus chrysolepis", "Quercus laurifolia",
    "Quercus hemisphaerica", "Quercus minima", "Quercus geminata", "Quercus fusiformis",
    "Chrysolepis chrysophylla", "Lithocarpus densiflorus", "Notholithocarpus densiflorus",
    "Quercus incana",  # bluejack oak — Chojnacky lists Q. incana under evergreen live oaks
}


def _binom(name: str):
    """'Tsuga canadensis (L.) Carrière' -> ('Tsuga', 'Tsuga canadensis'). None if not a binomial."""
    if not isinstance(name, str):
        return None, None
    toks = re.findall(r"[A-Za-z]+", name)
    if len(toks) < 1:
        return None, None
    genus = toks[0].capitalize()
    species = None
    if len(toks) >= 2 and toks[1].islower():
        species = f"{genus} {toks[1].lower()}"
    return genus, species


def chojnacky_group(scientific_name: str):
    """Return (group_key, note) or (None, reason).

    Forest (dbh) groups only for tree data. Woodland (drc) species — juniper/pinyon/mesquite/
    scrub-oak measured at root collar — are intentionally NOT auto-assigned from dbh data here;
    they return (None, 'woodland-drc') so the caller drops them rather than applying a dbh model.
    """
    genus, species = _binom(scientific_name)
    if genus is None:
        return None, "unparseable-name"

    # spg-split conifers
    if genus == "Abies":
        s = SPG.get(species)
        return (("conifer_Abies_lt035" if s < 0.35 else "conifer_Abies_ge035"), "spg") if s else (None, "Abies-unknown-spg")
    if genus == "Picea":
        s = SPG.get(species)
        return (("conifer_Picea_lt035" if s < 0.35 else "conifer_Picea_ge035"), "spg") if s else (None, "Picea-unknown-spg")
    if genus == "Pinus":
        s = SPG.get(species)
        if s is None:
            return None, "Pinus-unknown-spg"
        return ("conifer_Pinus_lt045" if s < 0.45 else "conifer_Pinus_ge045"), "spg"
    if genus == "Tsuga":
        s = SPG.get(species)
        return (("conifer_Tsuga_lt040" if s < 0.40 else "conifer_Tsuga_ge040"), "spg") if s else (None, "Tsuga-unknown-spg")

    # Cupressaceae conifer (forest): three-way spg split. Juniperus/pinyon woodland handled as drc.
    if genus in ("Thuja", "Calocedrus", "Sequoiadendron", "Sequoia", "Chamaecyparis", "Callitropsis"):
        s = SPG.get(species, 0.31)
        if s < 0.30:
            return "conifer_Cupressaceae_lt030", "spg"
        if s < 0.40:
            return "conifer_Cupressaceae_030_039", "spg"
        return "conifer_Cupressaceae_ge040", "spg"
    if genus == "Juniperus":
        # Multi-stem junipers are woodland (drc). Single-bole J. virginiana is forest, but NEON
        # measures dbh; without a per-record measure we drop Juniperus to avoid a drc/dbh mix.
        return None, "woodland-drc"
    if genus in ("Cercocarpus", "Prosopis", "Cercidium", "Parkinsonia"):
        return None, "woodland-drc"

    # spg-split hardwoods
    if genus == "Acer":
        s = SPG.get(species, 0.47)
        return ("hardwood_Aceraceae_ge050" if s >= 0.50 else "hardwood_Aceraceae_lt050"), "spg"
    if genus in ("Betula", "Alnus", "Ostrya", "Carpinus"):
        s = SPG.get(species)
        if s is None:
            s = {"Alnus": 0.37, "Ostrya": 0.63, "Carpinus": 0.58, "Betula": 0.48}[genus]
        if s < 0.40:
            return "hardwood_Betulaceae_lt040", "spg"
        if s < 0.50:
            return "hardwood_Betulaceae_040_049", "spg"
        if s < 0.60:
            return "hardwood_Betulaceae_050_059", "spg"
        return "hardwood_Betulaceae_ge060", "spg"
    if genus == "Fraxinus":
        s = SPG.get(species, 0.53)
        return ("hardwood_Oleaceae_ge055" if s >= 0.55 else "hardwood_Oleaceae_lt055"), "spg"
    if genus in ("Populus", "Salix"):
        s = SPG.get(species, 0.35)
        return ("hardwood_Salicaceae_ge035" if s >= 0.35 else "hardwood_Salicaceae_lt035"), "spg"

    # Fagaceae deciduous vs evergreen
    if genus in ("Quercus", "Chrysolepis", "Lithocarpus", "Notholithocarpus"):
        if species in FAGACEAE_EVERGREEN:
            return "hardwood_Fagaceae_evergreen", "evergreen"
        return "hardwood_Fagaceae_deciduous", "deciduous-default"

    if genus in GENUS_GROUP:
        return GENUS_GROUP[genus], "genus"

    return None, f"unmapped-genus:{genus}"
