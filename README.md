# Data Center Site Intelligence Dashboard — Ontario, Canada

A production-grade dashboard that aggregates public data sources to identify and rank land parcels suitable for data center development in Ontario.

## Architecture

```
External Data Sources → ETL Pipelines → PostgreSQL/PostGIS → FastAPI → React/Leaflet
```

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, GeoAlchemy2
- **Database:** PostgreSQL 15 + PostGIS 3.3
- **Frontend:** React 18, Leaflet, Tailwind CSS, Vite
- **ETL:** Modular Python pipelines per data source
- **Scoring:** Weighted composite scoring (power, fiber, zoning, size, constraints)

## Quick Start

### Prerequisites
- Docker and Docker Compose

### Run with Docker Compose

```bash
docker compose up --build
```

This starts:
- **PostgreSQL/PostGIS** on port 5432
- **FastAPI backend** on port 8000
- **React frontend** on port 5173

### Load Mock Data

After services are running, seed the database with realistic Ontario mock data:

```bash
docker compose exec backend python -m etl.scheduler
```

### Access

- **Dashboard:** http://localhost:5173
- **API Docs:** http://localhost:8000/api/v1/docs
- **Health Check:** http://localhost:8000/health

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL/PostGIS is running on localhost:5432
# with database 'datacenters' and user 'postgres'

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Load Mock Data

```bash
cd backend
python -m etl.scheduler
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/parcels` | List parcels (GeoJSON) with filters |
| GET | `/api/v1/parcels/{id}` | Parcel detail with score breakdown |
| GET | `/api/v1/scores/top` | Top-scored parcels |
| GET | `/api/v1/scores/stats` | Score distribution statistics |
| POST | `/api/v1/scores/recompute` | Trigger score recomputation |
| GET | `/api/v1/substations` | Substations (GeoJSON) |
| GET | `/api/v1/transmission-lines` | Transmission lines (GeoJSON) |
| GET | `/api/v1/fiber-routes` | Fiber routes (GeoJSON) |

### Filter Parameters (parcels)

- `power_proximity_km` — Max distance to nearest substation (km)
- `min_area_acres` / `max_area_acres` — Parcel size range
- `zoning_types` — Comma-separated zoning codes (e.g., `M1,M2,M3`)
- `min_score` — Minimum overall score (0-100)
- `municipality` — Filter by municipality name

## Scoring Model

Each parcel receives a 0-100 composite score:

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| Power | 30% | Distance to substations, weighted by voltage tier |
| Fiber | 20% | Distance to fiber routes, provider redundancy |
| Zoning | 20% | Zoning compatibility (industrial = highest) |
| Size | 15% | Optimal range: 20-200 acres |
| Constraints | 15% | Environmental overlaps (floodplain, wetland) |

See [docs/PHASE3_SCORING_MODEL.md](docs/PHASE3_SCORING_MODEL.md) for full details.

## Project Structure

```
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── models.py          # SQLAlchemy + PostGIS models
│   │   ├── schemas.py         # Pydantic response schemas
│   │   ├── routers/           # API endpoint handlers
│   │   └── scoring/           # Scoring engine + weights
│   └── etl/                   # ETL pipelines per data source
│       ├── mock_data.py       # Realistic Ontario mock data
│       └── scheduler.py       # APScheduler configuration
├── frontend/
│   └── src/
│       ├── components/        # React UI components
│       ├── api/client.js      # API client
│       └── utils/colors.js    # Score color mapping
├── docs/                      # Design docs per phase
└── mock/                      # Exported mock GeoJSON files
```

## Documentation

- [Phase 1 — System Design](docs/PHASE1_DESIGN.md)
- [Phase 2 — Data Sources](docs/PHASE2_DATA_SOURCES.md)
- [Phase 3 — Scoring Model](docs/PHASE3_SCORING_MODEL.md)
- [Phase 7 — Enhancements](docs/PHASE7_ENHANCEMENTS.md)
