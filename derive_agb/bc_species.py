"""BC Ministry of Forests 2-letter tree species codes -> scientific name.

Only codes that can be attributed with confidence are mapped; anything uncertain is left OUT so it
falls through to 'unmapped' (dropped + reported), never mis-allometried. The scientific name is then
resolved to a Chojnacky-2014 group by chojnacky_taxonomy.chojnacky_group() (shared with NEON) — the
BC conifer flora (Tsuga/Pseudotsuga/Pinus/Picea/Abies/Thuja/Larix) overlaps NEON's, so the wood
specific-gravity table already covers most species. Codes deliberately NOT mapped: TW (Taxus – no
Chojnacky Taxaceae group), JR (Juniperus – woodland drc, not dbh), and rare/ambiguous maple/misc
codes (MR, MS, DM, GP, KC, VB, WS, UP, EW, V, XC) — together <1% of stems.
"""

BC_CODE_TO_SCINAME = {
    # conifers
    "HW": "Tsuga heterophylla",
    "HM": "Tsuga mertensiana",
    "FD": "Pseudotsuga menziesii",
    "PL": "Pinus contorta",
    "PW": "Pinus monticola",
    "PY": "Pinus ponderosa",
    "PA": "Pinus albicaulis",
    "PJ": "Pinus banksiana",
    "SW": "Picea glauca",
    "SS": "Picea sitchensis",
    "SB": "Picea mariana",
    "SE": "Picea engelmannii",
    "BL": "Abies lasiocarpa",
    "BA": "Abies amabilis",
    "BG": "Abies grandis",
    "LW": "Larix occidentalis",
    "LT": "Larix laricina",
    "CW": "Thuja plicata",           # Cupressaceae (dbh group by spg)
    "YC": "Callitropsis nootkatensis",  # yellow-cedar, Cupressaceae
    # hardwoods
    "AT": "Populus tremuloides",
    "AC": "Populus balsamifera",      # black cottonwood complex
    "DR": "Alnus rubra",
    "EP": "Betula papyrifera",
    "MB": "Acer macrophyllum",
    "MV": "Acer circinatum",
    "DG": "Cornus nuttallii",         # Pacific dogwood -> hardwood_mixed (Cornaceae)
    "W":  "Salix sp",
}
