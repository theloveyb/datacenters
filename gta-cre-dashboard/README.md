# GTA Commercial Real Estate Dashboard

A dashboard that pulls commercial real estate listings from 12 brokerages across the GTA into one searchable, filterable view.

## How to Use

### Prerequisites (one-time installs)

You need two free programs installed. If you don't have them yet:

1. **Python** — Download from https://www.python.org/downloads/
   - Click the big yellow "Download Python" button
   - Run the installer
   - **Important (Windows):** Check the box that says "Add Python to PATH" before clicking Install

2. **Node.js** — Download from https://nodejs.org
   - Click the green "LTS" button
   - Run the installer, click Next through everything

### Starting the Dashboard

Open the `gta-cre-dashboard` folder and double-click:

- **Windows:** `Start Dashboard.bat`
- **Mac:** `Start Dashboard.command`

The first time it runs, it will install everything it needs automatically (~1 minute). After that it starts in a few seconds. Your browser will open to the dashboard.

**Leave the black window open** while you're using the dashboard. Close it when you're done.

### Getting Listings Into the Dashboard

The dashboard starts empty. To pull in listings from all 12 brokerage websites, double-click:

- **Windows:** `Scrape and Start.bat`
- **Mac:** `Scrape and Start.command`

This takes a few minutes since it's visiting 12 different websites. Once done, the dashboard opens with all the listings loaded. Run this whenever you want fresh data — old data is kept so you can track how long properties have been listed.

## What the Dashboard Shows

- **Active Listings** — All current listings in one filterable table. Filter by asset type (office, retail, industrial, etc.), sale vs. lease, brokerage, price range, square footage, and city. Search bar searches across addresses and broker names.
- **Brokers** — Directory of all brokers found, sortable by how many active listings they have.
- **New This Week** — Listings that appeared in the last 7 days.
- **Delisted This Week** — Listings that disappeared in the last 7 days.
- **Bar chart** — Visual breakdown of how many listings each brokerage has.

## Brokerages Covered

CBRE, JLL, Colliers, Cushman & Wakefield, Avison Young, Newmark, Lee & Associates, Lennard Commercial Realty, The Behar Group, InTrust CRE, Spacelist, ICX.ca

## Notes

- Some brokerage websites may block or change their layout, causing that scraper to return 0 results. The others will still work.
- This runs entirely on your computer. No data is sent anywhere.
- The listing data is stored in a file called `gta_cre.db` in this folder. Don't delete it unless you want to start fresh.

---

## Technical Details (for developers)

### Architecture

```
/gta-cre-dashboard
├── /scrapers          # One module per brokerage (requests + BeautifulSoup, Playwright fallback)
├── /backend           # FastAPI server + SQLite database layer
├── /frontend          # React + Vite + Tailwind CSS dashboard
├── start.py           # Launcher (installs deps, builds frontend, starts server)
├── run_scraper.py     # Scraper orchestrator (supports --only and --exclude flags)
├── seed_brokerages.py # Seeds the brokers table
└── requirements.txt   # Python dependencies
```

### Running from the command line

```bash
cd gta-cre-dashboard
python start.py              # Start dashboard
python start.py --scrape     # Scrape + start
python run_scraper.py        # Just scrape (no server)
python run_scraper.py --only cbre jll   # Scrape specific brokerages
```

### Automated daily scraping (cron)

```bash
0 6 * * * cd /path/to/gta-cre-dashboard && python run_scraper.py >> cron.log 2>&1
```

### Database

SQLite (`gta_cre.db`) with tables: `listings`, `brokers`, `scrape_runs`. Deduplication by address + brokerage. Tracks `date_first_seen`, `date_last_seen`, and `is_active` for market duration analysis.
