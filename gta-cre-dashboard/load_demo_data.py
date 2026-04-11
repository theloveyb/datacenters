#!/usr/bin/env python3
"""Load realistic demo listings so you can see the dashboard working
immediately, without needing to scrape live websites.

Run: python load_demo_data.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.database import init_db, get_connection, upsert_broker

init_db()
conn = get_connection()

today = datetime.now()

DEMO_LISTINGS = [
    # CBRE listings
    {"address": "100 King Street West", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 32.50, "square_footage": 15000, "broker_names": "Michael Chen", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 45},
    {"address": "2200 Yonge Street", "city": "Toronto", "neighbourhood": "Yonge-Eglinton", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 28.00, "square_footage": 8500, "broker_names": "Sarah Williams", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 12},
    {"address": "5500 Explorer Drive", "city": "Mississauga", "neighbourhood": "Meadowvale", "asset_type": "Industrial", "listing_type": "Sale", "asking_price": 12500000, "square_footage": 45000, "broker_names": "Michael Chen, David Park", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 30},
    {"address": "250 Dundas Street West", "city": "Toronto", "neighbourhood": "Dundas Square", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 85.00, "square_footage": 3200, "broker_names": "Sarah Williams", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 60},
    {"address": "7100 Woodbine Avenue", "city": "Markham", "neighbourhood": "Markham", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 18.50, "square_footage": 12000, "broker_names": "David Park", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 8},

    # JLL listings
    {"address": "77 King Street West", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 42.00, "square_footage": 22000, "broker_names": "Amanda Foster", "brokerage": "JLL", "listing_url": "https://www.jll.ca/en/properties", "days_ago": 20},
    {"address": "1 Dundas Street West", "city": "Toronto", "neighbourhood": "Dundas Square", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 125.00, "square_footage": 5800, "broker_names": "Amanda Foster, Rob Taylor", "brokerage": "JLL", "listing_url": "https://www.jll.ca/en/properties", "days_ago": 90},
    {"address": "2300 Meadowpine Boulevard", "city": "Mississauga", "neighbourhood": "Meadowvale", "asset_type": "Industrial", "listing_type": "Lease", "asking_rent": 14.75, "square_footage": 62000, "broker_names": "Rob Taylor", "brokerage": "JLL", "listing_url": "https://www.jll.ca/en/properties", "days_ago": 5},
    {"address": "130 Adelaide Street West", "city": "Toronto", "neighbourhood": "Entertainment District", "asset_type": "Office", "listing_type": "Sublease", "asking_rent": 22.00, "square_footage": 4500, "broker_names": "Amanda Foster", "brokerage": "JLL", "listing_url": "https://www.jll.ca/en/properties", "days_ago": 3},

    # Colliers listings
    {"address": "181 Bay Street", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 38.00, "square_footage": 18500, "broker_names": "James Robertson", "brokerage": "Colliers", "listing_url": "https://www.colliers.com/en-ca/properties", "days_ago": 15},
    {"address": "3500 Steeles Avenue East", "city": "Markham", "neighbourhood": "Markham", "asset_type": "Industrial", "listing_type": "Sale", "asking_price": 8900000, "square_footage": 32000, "broker_names": "James Robertson, Lisa Chang", "brokerage": "Colliers", "listing_url": "https://www.colliers.com/en-ca/properties", "days_ago": 55},
    {"address": "1200 Sheppard Avenue East", "city": "Toronto", "neighbourhood": "North York", "asset_type": "Mixed-Use", "listing_type": "Sale", "asking_price": 15000000, "square_footage": 28000, "broker_names": "Lisa Chang", "brokerage": "Colliers", "listing_url": "https://www.colliers.com/en-ca/properties", "days_ago": 22},
    {"address": "2800 Skymark Avenue", "city": "Mississauga", "neighbourhood": "Airport Corporate Centre", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 21.00, "square_footage": 9800, "broker_names": "James Robertson", "brokerage": "Colliers", "listing_url": "https://www.colliers.com/en-ca/properties", "days_ago": 7},

    # Cushman & Wakefield listings
    {"address": "40 University Avenue", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 35.00, "square_footage": 25000, "broker_names": "Karen Mitchell", "brokerage": "Cushman & Wakefield", "listing_url": "https://www.cushmanwakefield.com", "days_ago": 35},
    {"address": "6733 Mississauga Road", "city": "Mississauga", "neighbourhood": "Meadowvale", "asset_type": "Industrial", "listing_type": "Lease", "asking_rent": 16.50, "square_footage": 55000, "broker_names": "Karen Mitchell, Tom Nguyen", "brokerage": "Cushman & Wakefield", "listing_url": "https://www.cushmanwakefield.com", "days_ago": 18},
    {"address": "3300 Highway 7", "city": "Vaughan", "neighbourhood": "Vaughan Metropolitan Centre", "asset_type": "Land", "listing_type": "Sale", "asking_price": 22000000, "square_footage": 120000, "broker_names": "Tom Nguyen", "brokerage": "Cushman & Wakefield", "listing_url": "https://www.cushmanwakefield.com", "days_ago": 42},
    {"address": "200 Front Street West", "city": "Toronto", "neighbourhood": "Entertainment District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 30.00, "square_footage": 7200, "broker_names": "Karen Mitchell", "brokerage": "Cushman & Wakefield", "listing_url": "https://www.cushmanwakefield.com", "days_ago": 2},

    # Avison Young listings
    {"address": "18 York Street", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 45.00, "square_footage": 30000, "broker_names": "Patricia Hayes", "brokerage": "Avison Young", "listing_url": "https://www.avisonyoung.com", "days_ago": 28},
    {"address": "5055 Satellite Drive", "city": "Mississauga", "neighbourhood": "Airport Corporate Centre", "asset_type": "Office", "listing_type": "Sale", "asking_price": 6500000, "square_footage": 14000, "broker_names": "Mark Davidson", "brokerage": "Avison Young", "listing_url": "https://www.avisonyoung.com", "days_ago": 65},
    {"address": "1550 Kingston Road", "city": "Toronto", "neighbourhood": "Scarborough", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 22.00, "square_footage": 4800, "broker_names": "Patricia Hayes, Mark Davidson", "brokerage": "Avison Young", "listing_url": "https://www.avisonyoung.com", "days_ago": 10},

    # Newmark listings
    {"address": "161 Bay Street", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 40.00, "square_footage": 20000, "broker_names": "Chris Anderson", "brokerage": "Newmark", "listing_url": "https://www.nmrk.com", "days_ago": 33},
    {"address": "4711 Yonge Street", "city": "Toronto", "neighbourhood": "North York", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 24.00, "square_footage": 11000, "broker_names": "Chris Anderson", "brokerage": "Newmark", "listing_url": "https://www.nmrk.com", "days_ago": 6},
    {"address": "1 City Centre Drive", "city": "Mississauga", "neighbourhood": "City Centre", "asset_type": "Office", "listing_type": "Sale", "asking_price": 18500000, "square_footage": 42000, "broker_names": "Emily Watson", "brokerage": "Newmark", "listing_url": "https://www.nmrk.com", "days_ago": 50},

    # Lee & Associates listings
    {"address": "45 Sheppard Avenue East", "city": "Toronto", "neighbourhood": "North York", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 20.00, "square_footage": 6500, "broker_names": "George Kim", "brokerage": "Lee & Associates", "listing_url": "https://www.leetoronto.com", "days_ago": 14},
    {"address": "880 Lady Ellen Place", "city": "Toronto", "neighbourhood": "Etobicoke", "asset_type": "Industrial", "listing_type": "Lease", "asking_rent": 13.50, "square_footage": 28000, "broker_names": "George Kim, Natalie Russo", "brokerage": "Lee & Associates", "listing_url": "https://www.leetoronto.com", "days_ago": 40},

    # Lennard Commercial Realty listings
    {"address": "3080 Yonge Street", "city": "Toronto", "neighbourhood": "Lawrence Park", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 45.00, "square_footage": 2800, "broker_names": "Daniel Gurevich", "brokerage": "Lennard Commercial Realty", "listing_url": "https://www.lennard.com", "days_ago": 25},
    {"address": "1243 Islington Avenue", "city": "Toronto", "neighbourhood": "Etobicoke", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 28.00, "square_footage": 1800, "broker_names": "Daniel Gurevich", "brokerage": "Lennard Commercial Realty", "listing_url": "https://www.lennard.com", "days_ago": 4},
    {"address": "300 Borough Drive", "city": "Toronto", "neighbourhood": "Scarborough", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 16.00, "square_footage": 5200, "broker_names": "Rachel Stone", "brokerage": "Lennard Commercial Realty", "listing_url": "https://www.lennard.com", "days_ago": 38},

    # The Behar Group listings
    {"address": "3401 Dufferin Street", "city": "Toronto", "neighbourhood": "Downsview", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 32.00, "square_footage": 3500, "broker_names": "Morry Behar", "brokerage": "The Behar Group", "listing_url": "https://www.behargroup.com", "days_ago": 52},
    {"address": "1920 Ellesmere Road", "city": "Toronto", "neighbourhood": "Scarborough", "asset_type": "Industrial", "listing_type": "Sale", "asking_price": 4200000, "square_footage": 18000, "broker_names": "Morry Behar", "brokerage": "The Behar Group", "listing_url": "https://www.behargroup.com", "days_ago": 9},

    # InTrust CRE listings
    {"address": "260 Spadina Avenue", "city": "Toronto", "neighbourhood": "Chinatown", "asset_type": "Mixed-Use", "listing_type": "Sale", "asking_price": 5800000, "square_footage": 8500, "broker_names": "Alex Peralta", "brokerage": "InTrust CRE", "listing_url": "https://www.intrustcre.com", "days_ago": 19},
    {"address": "1600 Steeles Avenue West", "city": "Vaughan", "neighbourhood": "Concord", "asset_type": "Industrial", "listing_type": "Lease", "asking_rent": 15.00, "square_footage": 35000, "broker_names": "Alex Peralta", "brokerage": "InTrust CRE", "listing_url": "https://www.intrustcre.com", "days_ago": 1},

    # Spacelist listings
    {"address": "439 University Avenue", "city": "Toronto", "neighbourhood": "Discovery District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 29.00, "square_footage": 7500, "broker_names": "Listed on Spacelist", "brokerage": "Spacelist", "listing_url": "https://www.spacelist.ca", "days_ago": 11},
    {"address": "55 Town Centre Court", "city": "Toronto", "neighbourhood": "Scarborough", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 17.50, "square_footage": 4200, "broker_names": "Listed on Spacelist", "brokerage": "Spacelist", "listing_url": "https://www.spacelist.ca", "days_ago": 32},
    {"address": "2900 Steeles Avenue East", "city": "Markham", "neighbourhood": "Markham", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 35.00, "square_footage": 2200, "broker_names": "Listed on Spacelist", "brokerage": "Spacelist", "listing_url": "https://www.spacelist.ca", "days_ago": 5},

    # ICX listings
    {"address": "350 Bay Street", "city": "Toronto", "neighbourhood": "Financial District", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 36.00, "square_footage": 16000, "broker_names": "Listed on ICX", "brokerage": "ICX", "listing_url": "https://www.icx.ca", "days_ago": 23},
    {"address": "7030 Woodbine Avenue", "city": "Markham", "neighbourhood": "Markham", "asset_type": "Industrial", "listing_type": "Sale", "asking_price": 7800000, "square_footage": 26000, "broker_names": "Listed on ICX", "brokerage": "ICX", "listing_url": "https://www.icx.ca", "days_ago": 44},
]

# Also add some recently delisted listings
DELISTED_LISTINGS = [
    {"address": "150 Bloor Street West", "city": "Toronto", "neighbourhood": "Yorkville", "asset_type": "Retail", "listing_type": "Lease", "asking_rent": 95.00, "square_footage": 4000, "broker_names": "Sarah Williams", "brokerage": "CBRE", "listing_url": "https://www.cbre.ca/properties", "days_ago": 80, "delisted_days_ago": 2},
    {"address": "2001 Sheppard Avenue East", "city": "Toronto", "neighbourhood": "North York", "asset_type": "Office", "listing_type": "Lease", "asking_rent": 19.00, "square_footage": 6000, "broker_names": "James Robertson", "brokerage": "Colliers", "listing_url": "https://www.colliers.com", "days_ago": 60, "delisted_days_ago": 4},
    {"address": "4120 Yonge Street", "city": "Toronto", "neighbourhood": "North York", "asset_type": "Retail", "listing_type": "Sale", "asking_price": 3200000, "square_footage": 5500, "broker_names": "Morry Behar", "brokerage": "The Behar Group", "listing_url": "https://www.behargroup.com", "days_ago": 120, "delisted_days_ago": 1},
    {"address": "890 Dixon Road", "city": "Toronto", "neighbourhood": "Etobicoke", "asset_type": "Industrial", "listing_type": "Lease", "asking_rent": 12.00, "square_footage": 40000, "broker_names": "Tom Nguyen", "brokerage": "Cushman & Wakefield", "listing_url": "https://www.cushmanwakefield.com", "days_ago": 95, "delisted_days_ago": 3},
]


def load_demo():
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM listings")
    cursor.execute("DELETE FROM brokers")
    conn.commit()

    print("Loading demo listings...")

    # Insert active listings
    for item in DEMO_LISTINGS:
        first_seen = (today - timedelta(days=item["days_ago"])).strftime("%Y-%m-%d")
        last_seen = today.strftime("%Y-%m-%d")

        cursor.execute(
            """INSERT OR REPLACE INTO listings
               (address, city, neighbourhood, asset_type, listing_type,
                asking_price, asking_rent, square_footage, broker_names,
                brokerage, listing_url, date_first_seen, date_last_seen, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                item["address"], item["city"], item.get("neighbourhood"),
                item["asset_type"], item["listing_type"],
                item.get("asking_price"), item.get("asking_rent"),
                item["square_footage"], item["broker_names"],
                item["brokerage"], item["listing_url"],
                first_seen, last_seen,
            ),
        )

    # Insert delisted listings
    for item in DELISTED_LISTINGS:
        first_seen = (today - timedelta(days=item["days_ago"])).strftime("%Y-%m-%d")
        last_seen = (today - timedelta(days=item["delisted_days_ago"])).strftime("%Y-%m-%d")

        cursor.execute(
            """INSERT OR REPLACE INTO listings
               (address, city, neighbourhood, asset_type, listing_type,
                asking_price, asking_rent, square_footage, broker_names,
                brokerage, listing_url, date_first_seen, date_last_seen, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                item["address"], item["city"], item.get("neighbourhood"),
                item["asset_type"], item["listing_type"],
                item.get("asking_price"), item.get("asking_rent"),
                item["square_footage"], item["broker_names"],
                item["brokerage"], item["listing_url"],
                first_seen, last_seen,
            ),
        )

    # Insert brokers extracted from listings
    all_listings = DEMO_LISTINGS + DELISTED_LISTINGS
    seen_brokers = set()
    for item in all_listings:
        for name in item["broker_names"].split(","):
            name = name.strip()
            key = (name, item["brokerage"])
            if key not in seen_brokers and not name.startswith("Listed on"):
                seen_brokers.add(key)
                cursor.execute(
                    "INSERT OR IGNORE INTO brokers (name, brokerage) VALUES (?, ?)",
                    (name, item["brokerage"]),
                )

    conn.commit()

    active = cursor.execute("SELECT COUNT(*) as c FROM listings WHERE is_active = 1").fetchone()["c"]
    delisted = cursor.execute("SELECT COUNT(*) as c FROM listings WHERE is_active = 0").fetchone()["c"]
    brokers = cursor.execute("SELECT COUNT(*) as c FROM brokers").fetchone()["c"]

    print(f"\nDemo data loaded:")
    print(f"  {active} active listings")
    print(f"  {delisted} recently delisted listings")
    print(f"  {brokers} brokers")
    print(f"\nNow run: python start.py")


if __name__ == "__main__":
    load_demo()

conn.close()
