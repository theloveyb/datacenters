# GTA Commercial Real Estate Dashboard

Aggregated commercial real estate listings from 12 brokerages across the Greater Toronto Area, with a filterable React dashboard.

## Architecture

```
/gta-cre-dashboard
├── /scrapers          # Individual scraper modules (one per brokerage)
│   ├── base.py        # Common interface, normalization, utilities
│   ├── cbre.py        # CBRE Canada
│   ├── jll.py         # JLL Canada
│   ├── colliers.py    # Colliers Canada
│   ├── cushman.py     # Cushman & Wakefield
│   ├── avison_young.py # Avison Young
│   ├── newmark.py     # Newmark
│   ├── lee.py         # Lee & Associates Toronto
│   ├── lennard.py     # Lennard Commercial Realty
│   ├── behar.py       # The Behar Group
│   ├── intrust.py     # InTrust CRE
│   ├── spacelist.py   # Spacelist
│   └── icx.py         # ICX.ca
├── /backend
│   ├── main.py        # FastAPI server
│   └── database.py    # SQLite schema, queries, connection
├── /frontend          # React + Vite + Tailwind dashboard
├── run_scraper.py     # Orchestrator (cron-ready)
├── seed_brokerages.py # Pre-populate brokers table
├── requirements.txt
└── README.md
```

## Setup

### 1. Python dependencies

```bash
cd gta-cre-dashboard
pip install -r requirements.txt
playwright install chromium
```

### 2. Initialize database and seed brokerages

```bash
python seed_brokerages.py
```

### 3. Run scrapers

```bash
# Run all scrapers
python run_scraper.py

# Run only specific scrapers
python run_scraper.py --only cbre jll colliers

# Exclude specific scrapers
python run_scraper.py --exclude spacelist icx
```

### 4. Start the API server

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be at http://localhost:5173 with the API proxied to port 8000.

## Database

SQLite database (`gta_cre.db`) with three tables:

- **listings** — All scraped properties with address, asset type, pricing, broker info, and active/inactive tracking
- **brokers** — Broker directory (name, brokerage, email, phone, LinkedIn)
- **scrape_runs** — Audit log of each scrape execution

Deduplication is by `address + brokerage`. On each run, existing listings get their `date_last_seen` updated. Listings not found in the latest scrape are marked `is_active = false`.

## Dashboard Features

- Filterable table of active listings (asset type, listing type, brokerage, price range, sqft range, city)
- Full-text search across address and broker names
- Brokers tab with active listing counts, sortable
- New This Week / Delisted This Week tabs
- Bar chart of active listings by brokerage

## Cron Setup

Add to crontab for daily scraping:

```bash
0 6 * * * cd /path/to/gta-cre-dashboard && python run_scraper.py >> cron.log 2>&1
```

## Notes

- Scrapers use `requests + BeautifulSoup` for static sites and `Playwright` for JS-rendered sites
- Random delays (2-5s) between requests to be respectful
- Robots.txt is checked before scraping
- Some brokerage sites may block or change their structure — scrapers fail gracefully and log errors
- No authentication or multi-user support (local MVP)
