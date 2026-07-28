# Data-Access Request Materials — Restricted Forest-Biomass Reference Datasets

**Prepared for:** Gabriel(le) Sialelli — `gsialelli@ethz.ch`, ETH Zurich
**Use case:** Validation of a 10 m global above-ground biomass (AGB) map derived from AlphaEarth Foundations
satellite embeddings (years 2017–2025). Need: plot-level AGB with coordinates (or the finest aggregation the
data owner permits), field measurements ideally 2014–2025.

> **REQUEST SCOPE (updated 2026-07-23, per user):** We do **NOT** need tree-level / individual-stem data —
> **plot-aggregated AGB (per-plot Mg/ha at ≥0.25 ha support) plus the plot location** is sufficient and preferred.
> This deliberately narrows the ask to the less-restricted, faster-to-approve summary products. When sending each
> request below, state explicitly that only aggregated plot AGB + coordinates are required, not raw tree censuses.
> Caveat: aggregation removes the tree-vs-pixel noise but does NOT rescue datasets whose plot *location* is fuzzed
> or withheld (FIA, Italy INFC, coord-restricted EU NFIs) — those remain usable only at coarse aggregation.
**Compiled:** 2026-07-23. All URLs below were checked to resolve on this date. Where a specific personal contact
could not be confirmed, the official contact page is given instead — **no emails or DOIs have been invented.**

> **Coordinate-precision summary (read first)**
>
> | # | Dataset | Precise plot coordinates obtainable? | Practical validation mode |
> |---|---------|--------------------------------------|---------------------------|
> | 1 | ForestPlots.net | **Yes**, to approved collaborators under DUA (owner sets precision) | Plot-level |
> | 2 | ForestGEO | **Yes** — geolocated plots + within-plot stem maps | Plot-level (best case) |
> | 3 | GFBI | **Usually no** — contributors typically withhold/jitter coordinates | Mostly aggregate / degraded |
> | 4 | TmFO | **No** — raw inventories never leave site leaders; summary stats only | Aggregate-only |
> | 5 | ICP Forests Level II | **Partial** — coordinates released only if NFCs approve; often degraded | Plot-level *if* approved |
> | 6 | EU NFIs (SE/FI/CH/NO/IT/PL) | **Restricted, case-by-case** — exact coordinates are legally/administratively confidential in every one; see per-country notes | Mostly aggregate; precise coords only under bilateral agreement |
>
> **Legally/administratively coordinate-restricted (precise coords withheld by default):** GFBI, TmFO,
> and all six EU NFIs. For those, plan for aggregate or coordinate-degraded validation unless a bilateral
> data-use agreement is granted. ForestPlots.net and ForestGEO can release precise coordinates to approved users.
> ICP Forests Level II is intermediate (national veto per country).

---

## 1. ForestPlots.net (University of Leeds — RAINFOR / AfriTRON / T-FORCES)

- **(1) Where to start**
  - Register (free, non-commercial): <https://secure.forestplots.net/registration>
  - "Working with Data" (policy + collaboration route): <https://forestplots.net/en/join-forestplots/working-with-data>
  - Published open data packages (each with a DOI): <https://forestplots.net/en/publications#data>
  - Collaboration Committee reference doc: <https://forestplots.net/upload/Docs/ForestPlots.netCollaborationCommittee_March25.pdf>
- **(2) What to request** — Stem-level and plot-level census tables: plot metadata (location, area, census dates),
  per-tree DBH / height / species, and derived above-ground biomass (AGB, Mg/ha) computed with the network's
  allometries. For AGB-map validation, request **plot centroid coordinates and plot area** plus the plot-level AGB
  and most recent census date. Coordinate precision is set **per plot by the data owner**; some owners release full
  lat/lon to approved collaborators, others provide reduced precision. Ask explicitly for the finest coordinates the
  owner permits and the plot footprint (needed to match to a 10 m pixel window).
- **(3) Governance** — **Collaboration / data-use agreement with contribution expectation.** Publicly-released
  packages are CC BY-NC-SA 4.0. Non-public records require a collaboration request reviewed by the
  **Collaboration and Data Request Committee**; use of non-public data in publications requires explicit consent of
  the principal researcher / grant holder / field lead. Global-North / well-funded institutions (ETH qualifies) are
  asked to **contribute financially** toward database maintenance and field-training costs. Data may not be
  re-stored, redistributed, or shared with third parties without permission.
- **(4) Draft request email** (to `admin@forestplots.net`, requesting the collaboration form):

  > Subject: Collaboration request — plot AGB for validating a 10 m global biomass map (ETH Zurich)
  >
  > Dear ForestPlots.net Collaboration and Data Request Committee,
  > I am a researcher at ETH Zurich (gsialelli@ethz.ch) validating a new 10 m global above-ground biomass map
  > derived from AlphaEarth Foundations satellite embeddings (2017–2025). I would like to request access to
  > plot-level AGB estimates (Mg/ha), plot area, census dates, and plot-centroid coordinates at the finest
  > precision the data owners permit, for plots measured from roughly 2014 onward, to use as independent
  > ground reference. Please could you send me the "request to collaborate" form and advise on the contribution
  > expected from an ETH-based project. I am glad to offer co-authorship or acknowledgment as the contributing
  > PIs prefer, and I will not redistribute or re-store any non-public data. Thank you for your time.
  > Kind regards, [Name], ETH Zurich.
- **(5) Turnaround / cost** — Committee review **up to ~8 weeks**. Expect a **financial contribution** request
  (amount negotiated; scaled to institution). Progress report/publication expected within 2 years of collaboration.

---

## 2. Smithsonian ForestGEO

- **(1) Where to start**
  - Explore Data overview: <https://forestgeo.si.edu/explore-data>
  - Data request portal (register / request per plot): <https://ctfs.si.edu/datarequest/>
  - Portal main / login: <https://ctfs.si.edu/datarequest/index.php/main>
- **(2) What to request** — Per-plot **tree data** (stem tag, species, DBH per census, status, and **within-plot
  x,y stem coordinates** — ForestGEO plots are fully stem-mapped, typically on a local grid), plus **dendrometer**
  and **trait** data where present. For AGB validation request the tree table plus the **plot's absolute geographic
  reference** (corner/origin lat-lon and grid orientation) so the stem map can be georeferenced, and either
  ForestGEO-computed AGB or the species DBH needed to apply allometries. This is the **best-georeferenced** of the
  six datasets: precise within-plot positions plus a public plot location. Note only **~30 of ~78 sites** are in
  the portal; for others contact the plot **Principal Investigators** directly (contacts on each site's page under
  <https://forestgeo.si.edu/explore-data>).
- **(3) Governance** — **Per-plot data-use agreement, PI-approved.** Public datasets grant automatic access;
  non-public datasets require the plot's Principal Investigators to approve a request that includes a project
  description and planned analyses. Site-specific terms & conditions apply; **co-authorship/acknowledgment of plot
  PIs is the expected norm**, especially for unpublished census data.
- **(4) Draft request** (submitted through the portal form at <https://ctfs.si.edu/datarequest/> per plot):

  > Project title: Independent validation of a 10 m global AGB map (AlphaEarth embeddings, 2017–2025).
  > Requester: [Name], ETH Zurich (gsialelli@ethz.ch). I request tree-census tables (species, DBH, stem status,
  > within-plot x,y coordinates) and the plot's absolute geolocation/origin for the most recent censuses (ideally
  > 2014 onward) at [plot name]. Planned analysis: aggregate stem-level biomass to plot AGB (Mg/ha) using standard
  > allometries and compare against my map's predictions over the co-located pixel window; no redistribution of raw
  > data. I would be glad to include the plot Principal Investigators as co-authors or to acknowledge them as they
  > prefer. Please advise on any site-specific conditions.
- **(5) Turnaround / cost** — No fee. Turnaround varies by PI (days to several weeks; longer for the ~48 non-portal
  sites requiring direct PI correspondence). Budget extra time to contact multiple PIs if you need many sites.

---

## 3. GFBI — Global Forest Biodiversity Initiative

- **(1) Where to start**
  - Data page (routes requests through Science-i): <https://www.gfbinitiative.org/data>
  - Science-i collaboration platform (register / submit proposal): <https://science-i.org/>
  - Data viewer (see plot coverage, not download): <https://ag.purdue.edu/facai/data/gfbi/>
- **(2) What to request** — GFBI is collated ground-sourced **forest-inventory** data (~777,000 permanent plots
  globally): per-plot stem measurements and derived stand attributes including biomass/growing stock. For validation
  you would request plot-level AGB (or stand volume + wood density to derive it), measurement year, and **plot
  coordinates at the finest precision each contributor allows**. In practice **contributors commonly withhold or
  spatially jitter coordinates**, so be explicit that coordinate precision is your binding constraint and ask, per
  contributor, whether exact coordinates can be released under agreement or only degraded/aggregate.
- **(3) Governance** — **Per-project proposal + per-contributor permission, co-authorship-oriented.** Data users
  (GFB-U) submit a formal research proposal via Science-i and must obtain permission from each data contributor
  (GFB-C) for that specific project. Users agree to GFB policy and each owner's policy, and are **strongly
  encouraged to offer contributors co-authorship and/or acknowledgment.** Membership is free (GFBI reserves the
  right to change terms). This is effectively a collaboration model, not open data.
- **(4) Draft request** (email `GFBinitiative@gmail.com` and/or open an account and proposal at <https://science-i.org/>):

  > Subject: GFBI/Science-i data proposal — validating a 10 m global AGB map (ETH Zurich)
  >
  > Dear GFBI team, I am a researcher at ETH Zurich (gsialelli@ethz.ch) producing a 10 m global above-ground
  > biomass map from AlphaEarth Foundations embeddings (2017–2025) and I would like to submit a Science-i proposal
  > to use GFBI plots as independent ground reference. I need plot-level AGB (or volume + wood density), measurement
  > year (ideally 2014 onward), and plot coordinates at the finest precision contributors permit; where exact
  > coordinates cannot be shared, please advise whether coordinate-degraded or aggregated validation is possible.
  > I will follow GFBI and each contributor's policy and am glad to offer co-authorship or acknowledgment to
  > contributing data owners. Could you point me to the current proposal template and registration on Science-i?
  > Thank you, [Name], ETH Zurich.
- **(5) Turnaround / cost** — Free of charge. Turnaround depends on proposal review **and** on collecting
  per-contributor consent for many owners — realistically **weeks to a few months**. **Flag:** precise coordinates
  are frequently unavailable; plan for degraded/aggregate validation unless specific contributors agree otherwise.

---

## 4. TmFO — Tropical managed Forests Observatory (coordinated by CIRAD)

- **(1) Where to start**
  - Network site: <https://tmfo.org/>
  - Data management & policy: <https://tmfo.org/Data/>
  - Data policy (full text): <https://tmfo.org/Data/data%20policy>
- **(2) What to request** — Realistically, only **summary statistics** computed per site to a common protocol
  (e.g. stand-level AGB/carbon, dynamics after logging). **Raw forest inventories with plot coordinates are
  explicitly not shared** — they reside solely with each site leader and remain the IP of that leader's institution.
  A study using plot-level georeferenced data would have to be arranged **directly and bilaterally with individual
  site leaders**, plot by plot, as a research collaboration — not via a central download.
- **(3) Governance** — **Collaboration / co-authorship model with strict IP protection.** Research questions,
  protocols and analyses are agreed collectively at regional workshops (participatory decision-making). Site leaders
  retain IP and authorship and may publish independently. There is no open request portal.
- **(4) Draft request** (email `contact@tmfo.org`; verify the current network coordinator via <https://tmfo.org/>
  and the CIRAD Forests & Societies unit page <https://ur-forets-societes.cirad.fr/en/worldwide/observatories>):

  > Subject: Collaboration enquiry — tropical managed-forest plots to validate a 10 m AGB map (ETH Zurich)
  >
  > Dear TmFO coordination, I am a researcher at ETH Zurich (gsialelli@ethz.ch) validating a 10 m global
  > above-ground biomass map from AlphaEarth Foundations embeddings (2017–2025), and I am seeking independent
  > tropical reference data. I understand TmFO shares summary statistics rather than raw inventories; I would like
  > to ask (a) whether site-level AGB summaries with an approximate location could support map validation, and
  > (b) whether you could introduce me to individual site leaders open to a bilateral collaboration involving
  > georeferenced plot AGB. I will fully respect each institution's IP and offer co-authorship or acknowledgment as
  > site leaders prefer. Could you advise on the appropriate contact(s)? Thank you, [Name], ETH Zurich.
- **(5) Turnaround / cost** — No published fee. Because access is relationship-based and per-site, expect **weeks
  to months** and multiple separate agreements. **Flag: coordinate-restricted — aggregate/summary validation only,
  unless a per-site collaboration is separately negotiated.**

---

## 5. ICP Forests — Level II (intensive monitoring)

- **(1) Where to start**
  - Data requests page: <https://www.icp-forests.net/data-maps/data-requests>
  - Open-data downloads (subset): <https://icp-forests.org/data> and Level II open data: <https://icp-forests.org/open_data/level_ii/index.html>
  - Application form (PDF): `https://www.icp-forests.net/fileadmin/icp_forests/Dateien/Data_Access/ICPF_data_application_form.pdf`
    (if the direct link 404s, the current form is linked from the Data Requests page above)
- **(2) What to request** — Level II is the network of intensive monitoring plots. Request the tree-growth /
  biomass-relevant surveys: **tree data (DBH, height, species) and any growth/biomass increment tables**, plus plot
  metadata and **plot coordinates**. Coordinate release is **not guaranteed** — the Programme Co-ordinating Centre
  (PCC) forwards each request to the National Focal Centres (NFCs), which may **withhold or degrade coordinates**
  per national rules; state clearly you need the finest coordinates permitted and the plot footprint for pixel-level
  matching, and ask which countries can release them. Note the number of Level II plots is modest (a few hundred
  across Europe), so coverage per country is sparse.
- **(3) Governance** — **Signed data-use agreement + national approval.** You submit the signed application form
  and a ~1-page project description to the PCC (`pcc-icpforests@thuenen.de`); the request goes to all collaborating
  countries' NFCs, each of which can approve or refuse for its data. Governed by the ICP Forests Intellectual
  Property and Publication Policy (acknowledgment / possible co-authorship of data providers).
- **(4) Draft request** (cover email accompanying the signed form to `pcc-icpforests@thuenen.de`):

  > Subject: ICP Forests Level II data application — 10 m global AGB map validation (ETH Zurich)
  >
  > Dear Programme Co-ordinating Centre, please find attached the signed data application form and a one-page
  > project description. I am a researcher at ETH Zurich (gsialelli@ethz.ch) validating a 10 m global above-ground
  > biomass map derived from AlphaEarth Foundations embeddings (2017–2025). I request Level II tree/biomass survey
  > data (DBH, height, species, growth/increment) with plot metadata and plot coordinates at the finest precision
  > each National Focal Centre permits, for surveys from about 2014 onward. Where exact coordinates cannot be
  > released, please indicate which countries can provide degraded coordinates sufficient for ~100 m-scale matching.
  > I will comply with the ICP Forests IP and Publication Policy and acknowledge/involve data providers as required.
  > Thank you, [Name], ETH Zurich.
- **(5) Turnaround / cost** — PCC decision typically **~2–4 weeks** after the NFC circulation; no fee stated.
  **Flag: coordinate release is per-country and often degraded — plot-level validation is possible only for the
  countries whose NFCs approve full coordinates.**

---

## 6. Coordinate-restricted EU National Forest Inventories (as a group)

**General rule:** In all six countries the **exact plot coordinates are confidential** (plots must remain
undisturbed and unidentifiable), and public products are aggregated or coordinate-degraded. Precise coordinates,
where obtainable at all, come **only** under a signed confidentiality/data-use agreement negotiated directly with
the inventory institute, and a foreign (non-national) researcher is **not guaranteed** access. Approach each as a
bilateral research collaboration. Below is the single best entry point per country and a realistic read on feasibility.

### 6a. Sweden — SLU (Riksskogstaxeringen)
- **Contact / URL:** Dept. of Forest Resource Management NFI page — <https://www.slu.se/en/about-slu/organisation/departments/forest-resource-management/miljoanalys/nfi/>
  (official statistics/data contacts listed there; I could **not** confirm a specific personal email from public
  pages — use the NFI/department contact on that page rather than an invented address).
- **Coordinates:** Exact plot coordinates (SWEREF 99 TM) are **confidential**; public/microdata releases discretize
  environmental variables specifically to prevent plot localization. Exact coordinates can be requested directly from
  the Swedish NFI but require agreement and are not routinely given to external parties.
- **Feasible for a foreign researcher?** Possibly, under a data-use agreement; **not** as an open download.

### 6b. Finland — Luke (Natural Resources Institute Finland)
- **Contact / URL:** Luke NFI / data services — start at <https://www.luke.fi/en> (forest resources / NFI), and the
  Luke open-data geoportal <https://kartta.luke.fi/index-en.html> for the wall-to-wall MS-NFI rasters. For plot
  microdata use Luke's general research-data contact on luke.fi (no specific personal email confirmed — do not invent one).
- **Coordinates:** Public products are the **16 m multi-source NFI raster maps** (modelled, not field plots). Exact
  field-plot coordinates are confidential; plot-level microdata with coordinates is available only via a Luke research
  agreement.
- **Feasible for a foreign researcher?** Case-by-case under agreement; the raster MS-NFI is openly available but is a
  modelled product, not independent ground reference.

### 6c. Switzerland — WSL / LFI (Swiss NFI)
- **Contact / URL:** LFI info service <https://www.lfi.ch/en> and WSL Scientific Service NFI —
  <https://www.wsl.ch/en/about-wsl/organisation/research-units/forest-resources-and-management/head-and-research-groups/scientific-service-nfi.html>
  (the Scientific Service NFI is the formal channel for data/collaboration requests).
- **Coordinates:** Exact plot coordinates are **kept secret** by policy (even location-revealing photos are withheld).
  Access to precise coordinates is essentially only through a formal WSL research collaboration.
- **Feasible for a foreign researcher?** Only via WSL/LFI Scientific Service collaboration; **not** an open release.
  (Being ETH Zurich, a Swiss-domestic collaboration with WSL is the most tractable of the six — worth prioritizing.)

### 6d. Norway — NIBIO (Landsskogtakseringen)
- **Contact / URL:** NIBIO National Forest Inventory —
  <https://www.nibio.no/en/about-eng/our-divisions/division-of-forest-and-forest-resources/national-forest-inventory>
  (custom estimates service: <https://www.nibio.no/en/services/estimates-based-on-norway-s-national-forest-inventory-nfi>).
  Use the division contact on that page (no specific personal email confirmed).
- **Coordinates:** Plots are permanent, tree-level georeferenced (250 m² plots, 3×3 km grid), but exact plot
  coordinates are confidential. NIBIO offers **custom aggregated estimates** as the standard external service;
  plot-level coordinates require a research agreement.
- **Feasible for a foreign researcher?** Aggregated estimates readily; precise coordinates only under agreement.

### 6e. Italy — INFC (CREA / Carabinieri Forestali)
- **Contact / URL:** INFC portal (register to download): <https://www.inventarioforestale.org/en/> ; institutional
  host CREA Forestry & Wood: <https://www.crea.gov.it/en/web/foreste-e-legno>.
- **Coordinates:** INFC is the **most open** of the six — after free registration you can download raw stem-level data
  (INFC2005: ~230,000 living stems over 7,272 plots). **However, published plot coordinates are deliberately
  perturbed/approximate** for confidentiality, so they support only coarse (not 10 m pixel-exact) matching. Exact
  coordinates would need a separate request to CREA/INFC.
- **Feasible for a foreign researcher?** Yes for the coordinate-degraded raw data (open registration); exact
  coordinates only on special request.

### 6f. Poland — WISL / BDL (BULiGL, State Forests)
- **Contact / URL:** Forest Data Bank (Bank Danych o Lasach) WISL data: <https://www.bdl.lasy.gov.pl/portal/wisl-en>
  and <https://www.bdl.lasy.gov.pl/portal/dane-wisl> ; WISL project (BULiGL): <https://wisl.pl/en/>.
- **Coordinates:** Aggregated WISL results are public via BDL on a 4×4 km grid; **exact sample-plot coordinates are
  not published.** Plot-level data with coordinates would require a request to BULiGL / State Forests.
- **Feasible for a foreign researcher?** Aggregated results openly; precise plot coordinates only on request to BULiGL,
  feasibility uncertain.

**Group draft request** (adapt the salutation/URL per institute; send to the NFI/data contact on each page above):

> Subject: Data-use enquiry — plot-level NFI data for validating a 10 m global AGB map (ETH Zurich)
>
> Dear [Institute] National Forest Inventory team, I am a researcher at ETH Zurich (gsialelli@ethz.ch) validating a
> 10 m global above-ground biomass map derived from AlphaEarth Foundations satellite embeddings (2017–2025). I would
> like to ask whether it is possible, under a data-use/confidentiality agreement, to obtain plot-level AGB (or
> volume + wood density) with plot coordinates at the finest precision your rules permit, for field surveys from
> about 2014 onward, for use as independent ground reference. I understand exact plot coordinates are protected; if
> they cannot be released, please advise whether coordinate-degraded or small-area-aggregated estimates could be
> provided instead, and what agreement and any cost would apply. I will treat all coordinates as confidential and
> not redistribute them. Thank you for your guidance. Kind regards, [Name], ETH Zurich.

**Turnaround / cost (EU NFIs):** Highly variable — from immediate (INFC open registration; BDL/Luke public
aggregated products) to **weeks–months** for a negotiated agreement; custom aggregated estimates (Norway, Poland)
may carry a service fee. **Flag: exact coordinates are legally/administratively withheld in all six; assume
aggregate or coordinate-degraded validation unless a bilateral agreement is granted.** ETH's Swiss base makes the
WSL/LFI route the most promising for precise domestic data.

---

## Verification notes / caveats
- URLs above resolved on 2026-07-23. Portal sub-paths (e.g. the ICP Forests application-form PDF and ForestGEO
  per-plot request pages) can change; always start from the top-level page given and follow the current link.
- **No emails or DOIs were fabricated.** Confirmed contacts used: `admin@forestplots.net`, ForestGEO portal form,
  `GFBinitiative@gmail.com` / Science-i, `contact@tmfo.org`, `pcc-icpforests@thuenen.de`. For the six NFIs I could
  **not** confirm specific personal emails from public pages and have pointed to the official institutional NFI/data
  contact page in each case — obtain the current named contact there.
- Coordinate-precision statements reflect each program's stated confidentiality policy; the *actual* precision
  released is set at agreement time by the data owner/NFC and should be confirmed in writing before you rely on it
  for 10 m pixel-level matching.

---

# Priority NFIs — verified contacts (added 2026-07-27)

Contacts below were web-verified 2026-07-27; **nothing is fabricated** — where no email could be confirmed, the
statutory/portal channel is given instead. Ranked by whether TRUE ~10 m coordinates are actually obtainable, which
is the binding constraint. Supersedes the coordinate-status notes in §6 (Sweden/Finland/Switzerland) with confirmed
detail.

> **Coordinate reality (send effort here first):**
> - **True ~10 m coords under agreement:** **Estonia (documented YES)**, **Sweden (YES)**, Canada NFI (conditional, DUA), USA FIA (in principle, but PAUSED).
> - **Coordinate-blind / bespoke:** Switzerland, Finland (they extract at their side, may not hand over coords).
> - **Restricted by law / offset:** Mexico (LSNIEG Art. 37). **Hard ±100 m cap → unusable at 10 m:** Chile.
> - **No verified contact:** Argentina (use RTI Ley 27.275), Alberta PSP/GYPSY (custodian).

## A. Estonia — SMI (Keskkonnaagentuur) — TOP request, coords confirmed YES
- **To:** `klienditugi@envir.ee` (customer service; ask to forward to Metsaosakond / head Janika Laht — her direct
  email unverified). Landing: <https://keskkonnaagentuur.ee/keskkonnaagentuuri-tegevusvaldkonnad/mets/smi>
- **Must include:** signed *andmete kasutamise leping* (data-use agreement) — research objective, named authorised
  persons, transfer/processing procedure, data-protection + deletion-after-project clauses.
- **Coords:** **YES** — documented policy of releasing SMI permanent-plot coordinates to bona-fide scientists under
  the agreement. Annual panel, in-window. This is the single best gated source; prioritise.
- **Draft:**
  > Subject: SMI plot data + coordinates for validating a 10 m biomass map (ETH Zurich)
  >
  > Dear Keskkonnaagentuur, I am a researcher at ETH Zurich (gsialelli@ethz.ch) validating a 10 m above-ground
  > biomass map from AlphaEarth satellite embeddings. I would like to request SMI permanent-plot data — per-plot
  > AGB (or dbh+species to derive it), measurement year, and plot coordinates — for measurements from ~2014 on, as
  > independent ground reference. I understand coordinates are released to researchers under a data-use agreement; I
  > will treat them as confidential, not redistribute, and delete them at project end. Could you send me the
  > agreement template and advise on scope? Kind regards, [Name], ETH Zurich.

## B. Sweden — Riksskogstaxeringen (SLU) — coords confirmed YES
- **To:** `Riksskogstaxeringen@slu.se` (open-data contact Anna-Lena Axelsson; Head of Programme Cornelia Roberge,
  `cornelia.roberge@slu.se`). Policy: <https://www.slu.se/forskning/kunskapsbanken/s/sa-jobbar-riksskogstaxeringen-med-oppna-data>
- **Must include:** description of intended use / study plan + a signed confidentiality agreement (precondition for
  exact coords). Public coords are deliberately offset 200–1000 m; **exact coords released to external researchers**
  who sign. Possible extraction fee (unverified).
- **Draft:** (as §A, addressed to SLU; explicitly request the exact plot coordinates and state you will sign the
  confidentiality agreement and not redistribute.)

## C. Switzerland — LFI4/5 (WSL) — coordinate-blind by default
- **To:** `lfi@wsl.ch` (contacts Christoph Fischer, Barbara Allgaier Leuch). <https://www.lfi.ch/en/services/data-supply>
- **Must include:** email for a consultation + written quote → signed *Nutzungsvereinbarung*. Practical gate: study
  area ≈5,000–15,000 ha forest for ±10% accuracy; likely a **fee**. Default deliverable is an area-aggregated
  special evaluation, **not** raw ~10 m coords — negotiate explicitly; true-coord release unconfirmed. ETH being
  Swiss-domestic makes this the most tractable EU collaboration despite the coordinate limitation.
- **Precedent:** Gessler et al. 2024, New Phytol. 242(2):344, doi:10.1111/nph.19466.

## D. Finland — VMI (Luke) — coordinate-blind extraction
- **To:** `kirjaamo@luke.fi` (records office). <https://www.luke.fi/fi/tietoa-lukesta/asiakirjajulkisuus-ja-tietopyynnot>
- **Must include:** contact details; data description (database, period, geographic scope); purpose (scientific
  research is the legal basis, coords being personal data); delivery format. Standard info requests answered in
  2 weeks–1 month; a microdata agreement takes longer. Luke commonly runs a **coordinate-blind extraction** (they
  match plots to your rasters without revealing coords) — whether they release raw coords is negotiable.

## E. Argentina — INBN2 (MAyDS) — no verified email; use RTI
- **Channel:** *Solicitud de Acceso a la Información Pública* under **Ley 27.275**, filed via **TAD (Trámites a
  Distancia)** to Dirección Nacional de Bosques. Pages: <https://www.argentina.gob.ar/ambiente/bosques/segundo-inventario-nacional-bosques-nativos>
- **Must include:** requester identity; precise description (georeferenced conglomerado coords + tree/biomass
  measurements, INBN2 ~2015–2023); format. Statutory ~15 working days (+15). ~4,158 georef plots, best-in-window
  Latin-American NFI. Coordinate-release policy unverified — ask directly in the request.

## F. Mexico — INFyS (CONAFOR/INEGI) — coords restricted by law
- **To:** `conafor@conafor.gob.mx`; named INFyS contact **José Armando Alanís de la Rosa, `jalanis@conafor.gob.mx`**
  (from INEGI catalog 772: <https://www.inegi.org.mx/rnm/index.php/catalog/772>). Also PNT transparency channel.
- **Must include:** purpose + acceptance of restrictive use terms (statistical/non-commercial). **Exact coords are
  the confidential element under LSNIEG Art. 37 — NO by default**; true coords need a bespoke CONAFOR agreement.
  4 cycles incl. 2015–2020; richest content in Latin America if coords can be negotiated.

## G. Chile — IFN (INFOR) — ±100 m cap, likely unusable at 10 m
- **Channel:** *solicitud simple* / OIRS via <https://ifn.infor.cl> (Contacto email JS-obfuscated, unverified).
  Governing doc: "Protocolo Traspaso de Datos Biofísicos del IFN" (2021). Level-1 tree data needs a *carta
  compromiso de confidencialidad*. **Coords degraded to ±100 m (verbatim)** — record but treat as Tier-B only.

## H. Canada — NFI + Alberta — conditional YES via DUA
- **NFI:** online **Data Request Form** <https://nfi.nfis.org/en/datarequestform> (prelim `nfisupport@nfis.org`).
  Public coords randomized within 5 km; **exact ground-plot coords via request + signed DUA** (± jurisdiction
  sign-off). **Alberta PSP/GYPSY:** no verified channel — pursue via <https://open.alberta.ca> (search "permanent
  sample plot"/"GYPSY") + Alberta Forestry and Parks; likely converges with the NFI form.

## I. USA — FIA Spatial Data Services — PAUSED, monitor
- **Status (confirmed):** *"Due to the recent reduction of the federal workforce, we cannot process requests for
  confidential information at this time."* — <https://research.fs.usda.gov/programs/fia/sds>. Monitor for this line
  to disappear.
- **Form (for when it reopens):** wo-FIA SDS Request Form 2023 → regional SDS coordinator (e.g. PNW John Chase
  `john.chase@usda.gov`; National `SM.FS.FIANATLDR@usda.gov`). Needs a **sponsoring FIA scientist**, study plan,
  data-security plan, signed NDAs, and an MTA. Public data are fuzzed ~½ mile + private-plot swapped. Route returns
  predicted-vs-observed pairs, **never coordinates** — so plan a whole-region hold-out (PNW westside / SE pine),
  not a plot-level one.
