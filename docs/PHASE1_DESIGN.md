# Phase 1 — System Design

## Architecture

```
External Data Sources → ETL Pipelines → PostgreSQL/PostGIS → FastAPI → React/Leaflet
```

### Layers

1. **Ingestion Layer** — Python ETL scripts per data source. Fetch, parse, validate, load.
2. **Storage Layer** — PostgreSQL 15 + PostGIS 3.3. Spatial indexes on all geometry columns.
3. **Scoring Layer** — Batch computation after each ETL run. Pre-computed scores stored in `parcel_scores`.
4. **API Layer** — FastAPI serving GeoJSON. Spatial filtering via PostGIS queries.
5. **Presentation Layer** — React + Leaflet. Map-based UI with filter panel and detail views.

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | Python 3.11 + FastAPI | Async, geo library ecosystem, auto-docs |
| Database | PostgreSQL 15 + PostGIS | Industry standard geospatial DB |
| ORM | SQLAlchemy + GeoAlchemy2 | Mature PostGIS integration |
| Frontend | React 18 + Leaflet | Free OSM tiles, native GeoJSON support |
| Styling | Tailwind CSS | Rapid dashboard UI development |
| Build | Vite | Fast HMR, simple config |
| Container | Docker Compose | One-command local setup |

## Key Design Decisions

1. **Pre-computed scores** — Scoring runs as batch after ETL, not on every API request.
2. **GeoJSON interchange** — API returns GeoJSON, Leaflet consumes it natively.
3. **Mock data first** — Validate pipeline before wiring real sources.
4. **Monorepo** — Backend, frontend, ETL in one repo at this scale.
5. **PostGIS for all spatial logic** — Distance calculations, intersections, containment.
