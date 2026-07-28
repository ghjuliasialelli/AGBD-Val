"""Quebec MFFP PEP essence codes -> scientific name (from DICTIONNAIRE_PLACETTE.xlsx 'ESSENCES').

Tree species only; shrubs / unknown / non-commercial codes are left OUT so they drop to 'unmapped'
(reported, never mis-allometried). Scientific name -> Chojnacky-2014 group via chojnacky_taxonomy
(shared with NEON/BC; the NE-temperate flora is covered).

ETAT (tree state) live codes, from the dictionary 'ETAT' sheet — NOTE 14/44 = DEAD ('mort sur pied'),
a real trap; only the 'vivant'/'recrue vivante'/'renuméroté vivant'/'oublié vivant' codes are live.
"""

QC_LIVE_ETAT = {"10", "12", "30", "32", "40", "42", "50", "52"}
# 10 vivant sur pied, 12 vivant chablis, 30/32 oublié vivant, 40/42 recrue vivante, 50/52 renuméroté vivant

QC_ESSENCE_TO_SCINAME = {
    # conifers
    "SAB": "Abies balsamea",
    "EPN": "Picea mariana",
    "EPB": "Picea glauca",
    "EPR": "Picea rubens",
    "EPO": "Picea abies",
    "PIG": "Pinus banksiana",
    "PIB": "Pinus strobus",
    "PIR": "Pinus resinosa",
    "PIS": "Pinus sylvestris",
    "PID": "Pinus rigida",
    "MEL": "Larix laricina",
    "THO": "Thuja occidentalis",
    "PRU": "Tsuga canadensis",
    # hardwoods
    "BOP": "Betula papyrifera",
    "BOJ": "Betula alleghaniensis",
    "BOG": "Betula populifolia",
    "OSV": "Ostrya virginiana",
    "AUR": "Alnus incana",
    "ERS": "Acer saccharum",
    "ERR": "Acer rubrum",
    "ERA": "Acer saccharinum",
    "ERP": "Acer pensylvanicum",
    "ERE": "Acer spicatum",
    "PET": "Populus tremuloides",
    "PEG": "Populus grandidentata",
    "PEB": "Populus balsamifera",
    "SAL": "Salix sp",
    "HEG": "Fagus grandifolia",
    "CHR": "Quercus rubra",
    "CHB": "Quercus alba",
    "CHE": "Quercus bicolor",
    "CHG": "Quercus macrocarpa",
    "FRA": "Fraxinus americana",
    "FRN": "Fraxinus nigra",
    "FRP": "Fraxinus pennsylvanica",
    "TIL": "Tilia americana",
    "ORA": "Ulmus americana",
    "ORR": "Ulmus rubra",
    "CAC": "Carya cordiformis",
    "NOC": "Juglans cinerea",
    "PRP": "Prunus pensylvanica",
    "CET": "Prunus serotina",
    "PRV": "Prunus virginiana",
    "SOA": "Sorbus americana",
    "SOD": "Sorbus decora",
    "MAS": "Malus sp",
    "AME": "Amelanchier sp",
}
