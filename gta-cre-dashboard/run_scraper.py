#!/usr/bin/env python3
"""Orchestrator script that runs all scrapers, writes results to the database,
and outputs a summary. Designed to be run as a cron job.

Usage:
    python run_scraper.py              # Run all scrapers
    python run_scraper.py --only cbre  # Run only CBRE scraper
    python run_scraper.py --exclude jll colliers  # Skip specific scrapers
"""

import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import (
    get_connection,
    init_db,
    upsert_listing,
    mark_delisted,
    record_scrape_run,
    upsert_broker,
)
from scrapers import cbre, jll, colliers, cushman, avison_young, newmark
from scrapers import lee, lennard, behar, intrust, spacelist, icx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraper.log")
        ),
    ],
)
logger = logging.getLogger("orchestrator")

# Registry of all scrapers
SCRAPERS = {
    "cbre": ("CBRE", cbre.scrape),
    "jll": ("JLL", jll.scrape),
    "colliers": ("Colliers", colliers.scrape),
    "cushman": ("Cushman & Wakefield", cushman.scrape),
    "avison_young": ("Avison Young", avison_young.scrape),
    "newmark": ("Newmark", newmark.scrape),
    "lee": ("Lee & Associates", lee.scrape),
    "lennard": ("Lennard Commercial Realty", lennard.scrape),
    "behar": ("The Behar Group", behar.scrape),
    "intrust": ("InTrust CRE", intrust.scrape),
    "spacelist": ("Spacelist", spacelist.scrape),
    "icx": ("ICX", icx.scrape),
}


def run_all_scrapers(only: list[str] = None, exclude: list[str] = None):
    """Run scrapers and write results to the database."""
    init_db()
    conn = get_connection()

    summary = {
        "total_new": 0,
        "total_updated": 0,
        "total_delisted": 0,
        "total_errors": 0,
        "by_brokerage": {},
    }

    scrapers_to_run = SCRAPERS.items()
    if only:
        scrapers_to_run = [(k, v) for k, v in scrapers_to_run if k in only]
    if exclude:
        scrapers_to_run = [(k, v) for k, v in scrapers_to_run if k not in exclude]

    for key, (brokerage_name, scrape_fn) in scrapers_to_run:
        logger.info(f"--- Running scraper: {brokerage_name} ---")

        new_count = 0
        updated_count = 0
        error_count = 0

        try:
            listings = scrape_fn()
            logger.info(f"{brokerage_name}: Found {len(listings)} listings")

            active_addresses = set()

            for listing in listings:
                if not listing.get("address"):
                    continue

                result = upsert_listing(conn, listing)
                active_addresses.add(listing["address"])

                if result == "new":
                    new_count += 1
                elif result == "updated":
                    updated_count += 1
                elif result == "error":
                    error_count += 1

                # Extract and upsert brokers
                if listing.get("broker_names"):
                    for broker_name in listing["broker_names"].split(","):
                        broker_name = broker_name.strip()
                        if broker_name:
                            upsert_broker(conn, broker_name, brokerage_name)

            # Mark listings not found in this run as delisted
            delisted_count = mark_delisted(conn, brokerage_name, active_addresses)

            record_scrape_run(conn, brokerage_name, len(listings), error_count)
            conn.commit()

            brokerage_summary = {
                "new": new_count,
                "updated": updated_count,
                "delisted": delisted_count,
                "errors": error_count,
                "total_found": len(listings),
            }
            summary["by_brokerage"][brokerage_name] = brokerage_summary
            summary["total_new"] += new_count
            summary["total_updated"] += updated_count
            summary["total_delisted"] += delisted_count
            summary["total_errors"] += error_count

            logger.info(
                f"{brokerage_name}: {new_count} new, {updated_count} updated, "
                f"{delisted_count} delisted, {error_count} errors"
            )

        except Exception as e:
            logger.error(f"{brokerage_name}: Scraper failed with error: {e}")
            error_count += 1
            summary["total_errors"] += 1
            record_scrape_run(conn, brokerage_name, 0, 1)
            conn.commit()
            summary["by_brokerage"][brokerage_name] = {
                "new": 0,
                "updated": 0,
                "delisted": 0,
                "errors": 1,
                "total_found": 0,
            }

    conn.close()
    return summary


def print_summary(summary: dict):
    """Print a formatted summary of the scrape run."""
    print("\n" + "=" * 60)
    print("GTA CRE SCRAPER RUN SUMMARY")
    print("=" * 60)
    print(f"\nTotal new listings:      {summary['total_new']}")
    print(f"Total updated listings:  {summary['total_updated']}")
    print(f"Total delisted:          {summary['total_delisted']}")
    print(f"Total errors:            {summary['total_errors']}")
    print("\n--- By Brokerage ---")

    for brokerage, stats in summary["by_brokerage"].items():
        print(f"\n  {brokerage}:")
        print(f"    Found: {stats['total_found']}")
        print(f"    New: {stats['new']} | Updated: {stats['updated']} | "
              f"Delisted: {stats['delisted']} | Errors: {stats['errors']}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="GTA CRE Listing Scraper")
    parser.add_argument(
        "--only",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        help="Only run specific scrapers",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        help="Exclude specific scrapers",
    )
    args = parser.parse_args()

    logger.info("Starting GTA CRE scraper run...")
    summary = run_all_scrapers(only=args.only, exclude=args.exclude)
    print_summary(summary)
    logger.info("Scraper run complete.")


if __name__ == "__main__":
    main()
