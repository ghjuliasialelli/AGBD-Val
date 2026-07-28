# SOURCES — provenance for the AGB reference catalog

All metadata web-verified **2026-07-23** via three research passes (global plot networks; national
forest inventories; airborne-lidar AGB). This file records the primary source per dataset and flags
fields that still need confirmation before anyone *cites* them. Each dataset's `verified` field in the
catalog carries this date.

## Confidence & known gaps
- **DOIs left blank on purpose** (portal resolves, but the exact DOI string was not verified
  character-by-character — resolve on the guide page before citing):
  `sustainable-landscapes-brazil`, `cms-lidar-agb-tristate-rggi`, `tern-auscover-supersites`.
  Also blank where **no single dataset DOI exists**: `geo-trees`, `neon-veg-structure`,
  `tern-biomass-plot-library`, `swamp-mangrove`, and every NFI (cite the agency/portal instead).
- **Coordinate availability / precision unconfirmed**: `netherlands-nbi` (Probos DB — status unknown);
  `sweden-nfi` open RS-validation subset (coord precision undocumented). Marked `on-request` /
  `restricted` conservatively.
- **Units to double-check on ingest**: carbon products stored as `variable=AGC` (`gao-peru-carbon`,
  `gao-sabah-carbon`, `safe-borneo-lidar`, `drc-central-africa-lidar-agb`) — convert ÷≈0.47 to AGB.
- **`native_crs` for airborne rasters** is "UTM (region)" as a placeholder — read the actual EPSG from
  each GeoTIFF on download; do not trust this field for reprojection.

## Per-dataset primary sources

### In-situ plot networks
- **geo-trees** — https://data.geo-trees.org/ (data page /page/data); GEO program page. Predecessor FOS DOI 10.22022/ESM/03-2019.38.
- **forestplots-net** — https://forestplots.net/en/about ; DOI 10.1016/j.biocon.2020.108849 (ForestPlots.net et al. 2021); Lopez-Gonzalez et al. 2011 (J. Veg. Sci.).
- **forestgeo** — https://forestgeo.si.edu/explore-data ; data request http://ctfs.si.edu/ctfsrep/ ; DOI 10.1111/gcb.12712 (Anderson-Teixeira et al. 2015).
- **tmfo** — https://tmfo.org/sites-location/ ; DOI 10.1111/avsc.12125 (Sist et al. 2015).
- **gfbi** — https://www.gfbinitiative.org/data ; viewer https://ag.purdue.edu/facai/data/gfbi/ ; DOI 10.1038/s41597-020-00766-x; Liang et al. 2016 (Science).
- **neon-veg-structure** — https://data.neonscience.org/data-products/DP1.10098.001 ; versioned DOIs per release.
- **tern-biomass-plot-library** — https://portal.tern.org.au/metadata/fc4a7249-ebb2-4ada-8e06-b552bfb297a3 ; Field Data Portal https://field.jrsrp.com/ ; ausplotsR (CRAN).
- **swamp-mangrove** — https://data.cifor.org/dataverse/swamp (per-study DOIs).
- **icp-forests-level2** — https://www.icp-forests.org/ ; data requests via PCC (Thuenen).

### National Forest Inventories
- **usa-fia** — https://apps.fs.usda.gov/fia/datamart/datamart.html ; exact coords: https://research.fs.usda.gov/programs/fia/sds (Spatial Data Services).
- **france-ign-nfi** — https://inventaire-forestier.ign.fr/dataifn/?lang=en ; Etalab Open Licence v2.0.
- **spain-ifn** — https://www.miteco.gob.es/en/biodiversidad/temas/inventarios-nacionales/inventario-forestal-nacional.html ; datos.gob.es catalog a10002983.
- **sweden-nfi** — https://www.slu.se/en/environment/statistics-and-environmental-data/search-for-open-environmental-data/swedish-national-forest-inventory-sample-plot-data/ ; PXWeb API.
- **finland-nfi** — https://kartta.luke.fi/index-en.html ; raster archive https://pta.data.lit.fmi.fi/mvmi/index.html ; CC-BY-4.0 (MS-NFI).
- **germany-bwi** — https://bwi.info/ ; download https://bwi.info/download/de/ ; Web-API.
- **switzerland-lfi** — https://www.lfi.ch/en ; https://opendata.swiss/en/dataset?q=lfi ; Schadauer et al. 2024 (New Phytologist) on guarded coords.
- **norway-nfi** — https://www.nibio.no/en/about-eng/our-divisions/division-of-forest-and-forest-resources/national-forest-inventory ; stats https://www.ssb.no/en/jord-skog-jakt-og-fiskeri/skogbruk/statistikk/landsskogtakseringen.
- **italy-infc** — https://www.inventarioforestale.org/en/ (registration to download; license forbids reuse for producing Italian forest statistics).
- **uk-nfi** — https://www.forestresearch.gov.uk/tools-and-resources/national-forest-inventory/ ; woodland map https://data-forestry.opendata.arcgis.com/ (OGL).
- **canada-nfi** — https://open.canada.ca/data/en/dataset/824e684b-4114-4a05-a490-aa56332b57f4 ; exact coords https://nfi.nfis.org/en/datarequestform ; MAGPlot dataset 1a73441d.
- **poland-wisl** — https://www.bdl.lasy.gov.pl/portal/en ; https://buligl.pl/pl/web/buligl-en/w/national-forest-inventory.
- **netherlands-nbi** — https://www.wur.nl/en/research/environmental/dutch-national-forest-inventory (DB hosted by Probos; coord status UNCONFIRMED).

### Airborne-lidar AGB
- **sustainable-landscapes-brazil** — https://daac.ornl.gov/CMS/guides/LiDAR_Forest_Inventory_Brazil.html ; EMBRAPA WebGIS https://www.paisagenslidar.cnptia.embrapa.br/webgis/ (DOI UNCONFIRMED).
- **afrisar-agb-maps-ornl1681** — https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=1681 ; DOI 10.3334/ORNLDAAC/1681.
- **afrisar-lvis-gridded-ornl1775** — https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=1775 ; DOI 10.3334/ORNLDAAC/1775.
- **neon-aop** — https://data.neonscience.org (DP3.30015.001 CHM; DP1.30003 point cloud); GEE projects/neon-prod-earthengine/assets/CHM/001.
- **g-liht** — https://gliht.gsfc.nasa.gov/ ; https://glihtdata.gsfc.nasa.gov/ ; DOI 10.5067/COMMUNITY/GLIHT/GLLIDARPC.001 ; Cook et al. 2013 (10.3390/rs5084045).
- **cms-lidar-agb-california-ornl1537** — https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=1537 ; DOI 10.3334/ORNLDAAC/1537.
- **cms-lidar-biomass-sonoma-ornl1523** — https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=1523 ; DOI 10.3334/ORNLDAAC/1523 (note separate "improved high-biomass" Sonoma product).
- **cms-forest-agb-nw-usa-ornl2443** — https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=2443 ; DOI 10.3334/ORNLDAAC/2443 (V1 1766).
- **cms-lidar-agb-tristate-rggi** — https://daac.ornl.gov/CMS/guides/CMS_LiDAR_Biomass_MD_PA_DE.html ; https://daac.ornl.gov/CMS/guides/AGB_Carbon_Sequestration_RGGI.html (DOIs UNCONFIRMED).
- **gao-peru-carbon** — https://zenodo.org/records/4626309 ; DOI 10.5281/zenodo.4626309 ; Asner et al. 2014 (PNAS).
- **gao-sabah-carbon** — https://zenodo.org/records/4549461 ; DOI 10.5281/zenodo.4549461 ; Asner et al. 2018 (Biol. Conserv.).
- **safe-borneo-lidar** — https://zenodo.org/records/4549461 (GAO Sabah); oil-palm ACD via NERC EDS record 6e18121c; Jucker et al. 2018.
- **paracou-french-guiana-als** — https://catalogue.ceda.ac.uk/uuid/1d554ff41c104491ac3661c6f6f52aab/ ; DOI 10.5285/1d554ff41c104491ac3661c6f6f52aab ; CHM 10.5281/zenodo.10908679.
- **tern-auscover-supersites** — https://portal.tern.org.au/ ; geonetwork.tern.org.au (per-site DOIs NOT individually verified).
- **drc-central-africa-lidar-agb** — https://www.nature.com/articles/s41597-024-03162-x (ref maps, 10.1038/s41597-024-03162-x) ; DRC map https://www.nature.com/articles/s41598-017-15050-z (10.1038/s41598-017-15050-z) ; databasin.org.
