# New Zealand Data & APIs

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](CONTRIBUTING.md)

A list of New Zealand data sources and APIs. Pull requests are very welcome :smile:.

## Browse the site

This list is also published as a searchable website at
<https://olitreadwell.github.io/new-zealand-data/>, generated from this README
by `scripts/build_site.py` and deployed to GitHub Pages by
[`.github/workflows/pages.yml`](.github/workflows/pages.yml). To deploy your own
copy, enable Pages for the repository (Settings → Pages → Source: GitHub
Actions).

## Legend

Every entry is tagged with what it is, what it costs you to use, and whether it
is still the current tool for that data.

- Type: `API` (a programmatic interface), `Data` (datasets you download or
  query), `Portal` (a site you search across many datasets), `Register` (an
  official register you look records up in), `Docs` (documentation or metadata
  with no data of its own).
- Access: `Open` (no key and no account needed), `Key` (API key or developer
  registration), `Login` (user account), `Paid`.
- Status: `Legacy` (still online, but superseded) or `Archived` (frozen
  snapshot). No status tag means current.

Tags sit between the link and the description:

```
- [Name](https://example.govt.nz/) - Data - Open - what it holds
```

Entries are checked weekly by
[`.github/workflows/linkcheck.yml`](.github/workflows/linkcheck.yml). Links that
move, or that stop pointing at data, get repointed or dropped.

## Start here

These cover most requests. Each one is listed in full under its publisher below.

- data.govt.nz - the catalogue of government datasets
- Stats NZ - Aotearoa Data Explorer for statistics, Datafinder for boundaries
- LINZ Data Service - topographic, title, address and aerial data
- Koordinates - geospatial data from many publishers
- MBIE business API portal - company, NZBN, IPONZ and PPSR registers
- DigitalNZ - heritage collections from libraries and museums
- GeoNet - earthquakes, volcanoes and tsunami
- Metlink and Auckland Transport - public transport feeds

### Central government and agencies

- Statistics New Zealand
    - [Aotearoa Data Explorer](https://explore.data.stats.govt.nz/) - Data - Open - the current Stats NZ data tool, replaced NZ.Stat for most official statistics
    - [Infoshare](https://infoshare.stats.govt.nz/) - Data - Open - Legacy - time series data, being retired in favour of the Aotearoa Data Explorer
    - [Stats NZ website](https://www.stats.govt.nz/) - Portal - Open - statistical releases, methods and tools
    - [Stats NZ Geographic Data Service](https://datafinder.stats.govt.nz/) - Data - Open - geographic boundary files and other spatial data
- Ministry of Social Development (MSD)
    - [Statistics Page](https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/statistics/index.html) - Portal - Open
    - [Benefits Data Tables](https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/statistics/benefit/index.html#Datatables6) - Data - Open
    - [Housing Register](https://www.msd.govt.nz/about-msd-and-our-work/publications-resources/statistics/housing/housing-register.html) - Data - Open - social housing register, published quarterly
- Ministry of Justice (MoJ)
    - [Justice research and data](https://www.justice.govt.nz/justice-sector-policy/research-data/) - Data - Open - conviction and justice sector data, the successor to DataLab
- Ministry of Health (MoH)
    - [Statistics and data sets](https://www.health.govt.nz/monitoring-statistics/statistics-and-data-sets) - Data - Open - health survey results and published datasets
- Ministry of Transport (MoT)
    - [Statistics and insights](https://www.transport.govt.nz/statistics-and-insights) - Data - Open - transport statistics, replacing the Transport Monitoring Indicator Framework
- Ministry for the Environment (MoE)
    - [GIS Data & APIs](https://data.mfe.govt.nz/) - Data - Open
- Department of Conservation (DoC)
    - [Maps and data](https://www.doc.govt.nz/our-work/maps-and-data/) - Data - Open - DOC datasets, maps and geospatial services
- Department of Internal Affairs (DIA) (+ DigitalNZ)
    - [Digital NZ API](https://digitalnz.org/developers) - API - Key - search across NZ heritage collections
    - [Data.govt.nz](https://www.data.govt.nz/) - Portal - Open - government dataset catalogue
    - [Government A-Z directory](https://www.govt.nz/organisations/) - Register - Open - every government organisation and what it does
    - [New Zealand Gazette](http://www.digitalnz.org/developers/govhack-infopack#gazette) - Data - Open
    - [Papers Past](http://natlib.govt.nz/about-us/open-data/papers-past-metadata) - Data - Open
    - [Turnbull Unpublished Collections](http://natlib.govt.nz/about-us/open-data/turnbull-unpublished-collections-metadata) - Data - Open
    - [WWI related data](http://www.digitalnz.org/developers/wwi-api-examples) - Data - Open
    - [Publications New Zealand](http://natlib.govt.nz/about-us/open-data/publications-nz-metadata) - Data - Open
    - [Index New Zealand](http://natlib.govt.nz/about-us/open-data/innz-metadata) - Data - Open
    - [Free Alexander Turnbull Library Image Downloads](http://natlib.govt.nz/photos?il%5batl_free_download%5d=true) - Data - Open
- Inland Revenue (IRD)
    - [Tax Statistics](https://www.ird.govt.nz/about-us/tax-statistics) - Data - Open
- Land Information New Zealand (LINZ)
    - [LINZ Data Service](https://data.linz.govt.nz/) - Data - Open - authoritative topographic, hydrographic, survey, title, street address, crown pastoral land, aerial imagery and geodetic data
- Education Counts
    - [National data collections](https://www.educationcounts.govt.nz/data-services/national) - Data - Open
    - [Statistics](https://www.educationcounts.govt.nz/statistics) - Data - Open
- Herenga ā Nuku Aotearoa (Walking Access Commission)
    - [Public Access Areas](https://data.govt.nz/dataset/show/3630) - Data - Open
    - [Public Access Areas (REST API)](http://wams.org.nz/arcgis/rest/services/WEBSERVICE/WEBSERVICE_Public_Access_Areas/MapServer) - API - Open
    - [Outdoor access maps](https://www.herengaanuku.govt.nz/maps/outdoor-access-maps) - Portal - Open - downloadable maps and trail data
- New Zealand Police
    - [Crime Statistics](https://www.police.govt.nz/about-us/publications-statistics/data-and-statistics) - Data - Open
- New Zealand Qualifications Authority (NZQA)
    - [Secondary School Statistics](https://www2.nzqa.govt.nz/ncea/understanding-secondary-quals/secondary-school-stats/) - Data - Open
- New Zealand Transport Agency (NZTA)
    - [NZTA InfoConnect](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/) - API - Key - traffic and travel APIs, registration required
        - [Auckland Traffic](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/auckland-traffic-api/) - API - Key
        - [Christchurch Traffic](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/christchurchy-traffic-api/) - API - Key
        - [Highway Information](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/highway-information-api/) - API - Key
        - [Location Referencing](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/location-referencing-api/) - API - Key
        - [SSDF Segment Manager](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/ssdf-segment-manager-api/) - API - Key
        - [Traffic Cameras](https://www.nzta.govt.nz/traffic-and-travel-information/infoconnect-section-page/about-the-apis/traffic-cameras/) - API - Key
    - [Crash Analysis System (CAS)](https://www.nzta.govt.nz/resources/crash-analysis-system-data/index.html) - Data - Open
    - [Aerial Imagery](https://koordinates.com/from/nzta/data/) - Data - Open
- Ministry of Business, Innovation and Employment (MBIE)
    - [Business API portal](https://portal.api.business.govt.nz/) - Portal - Key - MBIE register APIs, subscription required
        - [Companies Register](https://portal.api.business.govt.nz/api/companies-register) - API - Key
        - [Intellectual Property Office (IPONZ)](https://portal.api.business.govt.nz/api/iponz) - API - Key
        - [Insolvency Register](https://portal.api.business.govt.nz/api/insolvency-register) - API - Key
        - [Licensed Building Practitioners (LBP)](https://portal.api.business.govt.nz/api/lbp) - API - Key
        - [Motor Vehicle Traders Register (MVTR)](https://portal.api.business.govt.nz/api/motor-vehicle-traders-register) - API - Key
        - [New Zealand Business Number (NZBN)](https://portal.api.business.govt.nz/api/nzbn) - API - Key
        - [Personal Property Securities Register (PPSR)](https://portal.api.business.govt.nz/api/ppsr) - API - Key
        - [Radio Spectrum Management (RSM)](https://portal.api.business.govt.nz/api/radiospectrum-management) - API - Key
        - [Tenancy Bond](https://portal.api.business.govt.nz/api/tenancy-bond) - API - Key
        - [Petroleum and Minerals (NZPAM)](https://www.nzpam.govt.nz/) - Register - Open - the NZPAM API is not in the MBIE portal, so use the register
- Department of Corrections
    - [Research](https://www.corrections.govt.nz/resources/research) - Data - Open - prison population and corrections statistics
- Immigration New Zealand
    - [Research and statistics](https://www.immigration.govt.nz/about-us/research-and-statistics/) - Data - Open - visa and migration statistics
- Parliamentary Counsel Office
    - [New Zealand Legislation](https://www.legislation.govt.nz/) - Register - Open - official Acts, regulations and Bills

### Tourism and economic data

- [Regional Tourism Estimates](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/previous-tourism-data-releases/regional-tourism-estimates) - Data - Open - annual visitor spend by region
- [Monthly Regional Tourism Estimates](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/monthly-regional-tourism-estimates) - Data - Open - monthly visitor spend by region
- [Tourism data releases](https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases) - Portal - Open - forecasts and other tourism releases
- Reserve Bank of New Zealand
    - [Statistics](http://www.rbnz.govt.nz/statistics/) - Data - Open
- New Zealand Institute of Economic Research
    - [Data1850](https://www.nzier.org.nz/data-1850) - Data - Open - long-term economic data

### Regional councils

- Environment Canterbury & Partners (ECAN)
    - [Canterbury Maps open data](https://opendata.canterburymaps.govt.nz/) - Data - Open
- Greater Wellington Regional Council (GWRC)
    - [GIS Data & APIs](https://koordinates.com/from/gwrc/data/) - Data - Open

### City and district councils

- Auckland Council
    - [Auckland Open Data](https://aucklandopendata-aucklandcouncil.opendata.arcgis.com/) - Portal - Open
    - [Auckland Transport API](https://dev-portal.at.govt.nz/) - API - Key
    - [Auckland Transport Open GIS Data](https://data-atgis.opendata.arcgis.com/) - Data - Open
- Wellington City Council (WCC)
    - [GIS Data](https://data-wcc.opendata.arcgis.com/) - Data - Open
    - [Metlink Open Data](https://opendata.metlink.org.nz/) - Data - Key - GTFS timetables and realtime feeds, registration required
- Christchurch City Council
    - [Open Data Portal](https://opendata-christchurchcity.hub.arcgis.com/) - Portal - Open - council datasets across transport, land and services
- Whanganui District Council
    - [Whanganui GeoSpatial](https://geonode.whanganui.govt.nz/) - Data - Open - council GIS datasets
    - [Open data on Koordinates](https://koordinates.com/from/whanganui-district-council/data/) - Data - Open
    - [Cemetery Search](https://www.whanganui.govt.nz/Services/Cemeteries-and-Crematorium/Cemetery-Search) - Register - Open
    - [Property and Rating Search](https://www.whanganui.govt.nz/Property-and-Rates/Rates/Property-Rating-Search) - Register - Open
    - [Food Safety](https://www.whanganui.govt.nz/Business/Food-Safety) - Docs - Open - food business registration; grading searches for all councils are on the MPI food register
- Porirua City Council
    - [GIS Data & APIs](https://koordinates.com/from/porirua-city-council/data/) - Data - Open

### Crown Research Institutes (CRIs)

- NIWA
    - [DataHub](https://data.niwa.co.nz/) - Portal - Open - NIWA's open data platform
    - [CliFlo Climate Database](https://data.niwa.co.nz/pages/clidb-on-datahub) - Data - Open - climate observations, now hosted on DataHub
    - [River Environment Classification (REC) v2.0 (OGC WMS)](https://geoserver.niwa.co.nz/rec/wms) - API - Open
    - [Tide forecasts](https://developer.niwa.co.nz/docs/tide-api/1/overview) - API - Key
    - [UV forecasts](https://developer.niwa.co.nz/docs/uv-api/1/overview) - API - Key
    - [SolarView](https://developer.niwa.co.nz/docs/solarview-api/1/overview) - API - Key
- GNS Science
    - [GeoNet API](https://api.geonet.org.nz/) - API - Open - earthquake, volcano and tsunami data
- Landcare Research | Manaaki Whenua
    - [LRIS Portal - Science/Land GIS Data & APIs](https://lris.scinfo.org.nz/) - Portal - Open
    - [Topographic basemaps (OGC WMS)](http://maps.scinfo.org.nz/basemaps/wms?) - API - Open

### Non-Government Organisations (NGOs)

- Land Air Water Aotearoa (LAWA)
    - [Natural resources data](http://www.lawa.org.nz/) - Data - Open
- New Zealand Organisms Register
    - [Organism Register](http://data.nzor.org.nz/) - Data - Open
- Figure NZ (formally Wiki New Zealand)
    - [Charts and data](https://figure.nz/) - Data - Open - curated charts built from official sources; the old public API has been withdrawn

### Companies

- New Zealand Electricity Industry
    - [Market Info](http://www.electricityinfo.co.nz/comitFta/ftapage.main) - Data - Open
- NZ Post
    - [Developer Centre](https://www.nzpost.co.nz/business/ecommerce/developer-resource-centre) - API - Key - address and parcel APIs
- Zenbu
    - [NZ places listings](https://www.zenbu.co.nz/browse) - Data - Open
- Carjam
    - [Vehicle information API](https://www.carjam.co.nz/dev:page?t=getting-started) - API - Key
- Koordinates
    - [Geospatial data & APIs](https://koordinates.com/) - Portal - Open
- Eventfinda
    - [Event API](https://www.eventfinda.co.nz/api/index) - API - Key
- TradeMe
    - [API](https://developer.trademe.co.nz/) - API - Key
- Xero
    - [API](https://developer.xero.com/documentation/getting-started/getting-started-guide/) - API - Key
- Vend (now Lightspeed)
    - [API documentation](https://developers.retail.lightspeed.app/documentation) - API - Key
- Psoda
    - [Web Services API](https://www.psoda.com/download/PsodaWebServicesReference.pdf) - Docs - Open
- ASB
    - [API](https://developer.asb.co.nz/) - API - Key

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to suggest or add links.
Pull requests are very welcome :smile:.

## How it's maintained

- Links are checked automatically every week by
  [`.github/workflows/linkcheck.yml`](.github/workflows/linkcheck.yml); a
  tracking issue opens on genuine dead links and closes when they recover.
- The site is rebuilt from this README whenever it changes, so the two never
  drift apart.

#### Help wanted
Hi there, if you're interested in helping out I'd love a PR with new links, if you've never created a Pull Request before get in touch and I'll help you out.

Tags are checked by `scripts/validate_readme.py`, so if you add an entry, give it a type, an access level and (if it is no longer the current tool) a status. See the legend above.

#### References and Attributions
- [Govhack 2015](https://www.govhack.org.nz/) - Portal - Open - the event this list started from
- [Open NZ Wiki APIs](https://web.archive.org/web/20180129103726/https://wiki.open.org.nz/wiki/spaces/main/pages/589878/New+Zealand+APIs) - Docs - Open - Archived - where this list originally came from
- [Open NZ datasets](https://web.archive.org/web/20180129035232/http://cat.open.org.nz/category/dataset/) - Data - Open - Archived - catalogue of datasets from the same era
