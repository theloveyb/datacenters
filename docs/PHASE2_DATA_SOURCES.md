# Phase 2 — Data Sources

## 1. Power Grid Infrastructure

### 1.1 Hydro One Transmission Stations
- **Source:** Ontario GeoHub / LIO Open Data
- **URL:** `https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/LIO_OPEN_DATA/LIO_Open01/MapServer/17/query`
- **Format:** ArcGIS REST → GeoJSON (via `f=geojson`)
- **Update Frequency:** Quarterly
- **Key Fields:** STATION_NAME, VOLTAGE_KV, CAPACITY_MVA, OWNER, geometry (Point)
- **Ingestion:** HTTP GET with `where=1=1&outFields=*&outSR=4326&f=geojson`
- **Notes:** Layer 17 is Transmission Stations. Layer numbers may change; query the MapServer root to verify.

### 1.2 Transmission Lines
- **Source:** Ontario GeoHub / LIO Open Data
- **URL:** `https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/LIO_OPEN_DATA/LIO_Open01/MapServer/16/query`
- **Format:** ArcGIS REST → GeoJSON
- **Update Frequency:** Quarterly
- **Key Fields:** LINE_NAME, VOLTAGE_KV, OWNER, geometry (LineString)
- **Ingestion:** Same pattern as substations
- **Notes:** Use `resultRecordCount=5000` and pagination for large datasets.

### 1.3 IESO Generation / Capacity Data
- **Source:** IESO Open Data
- **URL:** `https://www.ieso.ca/en/Power-Data/Data-Directory`
- **Format:** CSV reports
- **Update Frequency:** Daily (real-time generation), Monthly (planning)
- **Key Fields:** Zone, capacity MW, demand MW, surplus/deficit
- **Ingestion:** CSV download + pandas parsing
- **Notes:** Useful for understanding which regions have available capacity vs. constrained.

## 2. Fiber / Telecom Backbone

### 2.1 CRTC Broadband Availability
- **Source:** CRTC Open Data
- **URL:** `https://open.canada.ca/data/en/dataset/00a331db-121b-445d-b119-35dbbe3eedd9`
- **Format:** CSV (large, ~500MB)
- **Update Frequency:** Annual
- **Key Fields:** Provider, technology, max speed, latitude, longitude, FSA
- **Ingestion:** Bulk CSV download, filter for Ontario (province = ON)
- **Notes:** Provides coverage areas per provider, not exact routes. Useful for identifying multi-provider zones.

### 2.2 Known Backbone Routes (Derived)
- **Source:** Public carrier filings + infrastructure maps
- **Format:** Manually curated GeoJSON (mock data initially)
- **Key Fields:** Provider name, route type (backbone/metro), coordinates
- **Notes:** Exact fiber routes are proprietary. We approximate major corridors (Highway 401, 407, rail corridors) based on public filings.

## 3. Land Parcels / Cadastral

### 3.1 Ontario Parcel Register (MPAC)
- **Source:** Ontario GeoHub
- **URL:** `https://geohub.lio.gov.on.ca/datasets/ontario-parcel-boundaries`
- **Format:** Shapefile / GeoJSON via ArcGIS REST
- **Update Frequency:** Semi-annually
- **Key Fields:** PIN, ARN, municipality, area, geometry (Polygon)
- **Ingestion:** ArcGIS REST query with pagination
- **Limitations:** Full province dataset is very large (~12M parcels). Filter by municipality or bounding box.

### 3.2 Assessment Roll Data (MPAC)
- **Source:** Municipal Property Assessment Corporation
- **URL:** Available through individual municipalities or MPAC data products
- **Format:** CSV / database export
- **Key Fields:** Property type, assessed value, land use code
- **Notes:** Not freely open. Some municipalities publish assessment data in open data portals.

## 4. Zoning / Municipal Planning

### 4.1 Toronto Zoning By-law
- **Source:** Toronto Open Data
- **URL:** `https://open.toronto.ca/dataset/zoning-by-law/`
- **Format:** GeoJSON / Shapefile
- **Update Frequency:** As amended (quarterly approx.)
- **Key Fields:** Zone code (M1, M2, M3, etc.), zone description, geometry

### 4.2 York Region / Durham Region / Peel Region
- **Source:** Regional open data portals
- **Format:** Shapefile / GeoJSON
- **Notes:** Each municipality has its own portal and schema. Key municipalities:
  - Markham: `https://data-markham.opendata.arcgis.com/`
  - Vaughan: `https://data.vaughan.ca/`
  - Pickering: Available through Durham Region GIS

### 4.3 Ontario Official Plans
- **Source:** Ministry of Municipal Affairs
- **Format:** PDF (text extraction required) or GIS where available
- **Notes:** Official plans indicate future growth areas and employment lands. Useful for identifying expansion zones.

## 5. Environmental Constraints

### 5.1 Floodplain Mapping
- **Source:** Ontario GeoHub / Conservation Authorities
- **URL:** LIO Open Data floodplain layers
- **Format:** ArcGIS REST → GeoJSON
- **Key Fields:** Flood type (floodway/fringe), regulation limit, authority

### 5.2 Wetlands
- **Source:** Ontario GeoHub
- **URL:** LIO Open Data wetland layers
- **Format:** ArcGIS REST → GeoJSON
- **Key Fields:** Wetland type, evaluation status, significance (PSW/non-PSW)

### 5.3 Areas of Natural and Scientific Interest (ANSI)
- **Source:** Ontario GeoHub
- **Format:** ArcGIS REST
- **Key Fields:** ANSI type (life science/earth science), significance

### 5.4 Endangered Species Habitat
- **Source:** Ontario Ministry of Natural Resources
- **Format:** Varies (some available through GeoHub)
- **Notes:** Sensitive data; general habitat areas available, specific locations restricted.

## 6. Real Estate / Land Transactions (Optional)

### 6.1 Ontario Land Registry (Teranet)
- **Source:** Teranet / Ontario Land Registry
- **Format:** Proprietary database
- **Notes:** Not freely accessible. Transaction history available through paid GeoWarehouse service.

### 6.2 Commercial Real Estate Listings
- **Source:** Various (CoStar, LoopNet, Realtor.ca commercial)
- **Format:** Web scraping / API (where available)
- **Notes:** Useful for price validation but not critical for scoring.

## Data Pipeline Summary

| Source | Format | Frequency | Priority | Status |
|--------|--------|-----------|----------|--------|
| Hydro One Substations | GeoJSON/REST | Quarterly | Critical | Mock + Live |
| Transmission Lines | GeoJSON/REST | Quarterly | Critical | Mock + Live |
| IESO Capacity | CSV | Monthly | High | Mock |
| CRTC Broadband | CSV | Annual | High | Mock |
| Fiber Routes | GeoJSON | Manual | High | Mock |
| Ontario Parcels | GeoJSON/REST | Semi-annual | Critical | Mock + Live |
| Zoning (Toronto) | GeoJSON | Quarterly | High | Mock + Live |
| Zoning (Other) | Various | Varies | Medium | Mock |
| Floodplains | GeoJSON/REST | Annual | Medium | Mock + Live |
| Wetlands | GeoJSON/REST | Annual | Medium | Mock + Live |
