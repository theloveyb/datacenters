#!/usr/bin/env python3
"""Seed the brokers table with brokerage names so you can manually add
contact info later."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_connection, init_db

BROKERAGES = [
    {
        "brokerage": "CBRE",
        "brokers": [
            "CBRE Toronto Office",
        ],
    },
    {
        "brokerage": "JLL",
        "brokers": [
            "JLL Toronto Office",
        ],
    },
    {
        "brokerage": "Colliers",
        "brokers": [
            "Colliers Toronto Office",
        ],
    },
    {
        "brokerage": "Cushman & Wakefield",
        "brokers": [
            "Cushman & Wakefield Toronto Office",
        ],
    },
    {
        "brokerage": "Avison Young",
        "brokers": [
            "Avison Young Toronto Office",
        ],
    },
    {
        "brokerage": "Newmark",
        "brokers": [
            "Newmark Toronto Office",
        ],
    },
    {
        "brokerage": "Lee & Associates",
        "brokers": [
            "Lee & Associates Toronto Office",
        ],
    },
    {
        "brokerage": "Lennard Commercial Realty",
        "brokers": [
            "Lennard Commercial Realty Office",
        ],
    },
    {
        "brokerage": "The Behar Group",
        "brokers": [
            "The Behar Group Office",
        ],
    },
    {
        "brokerage": "InTrust CRE",
        "brokers": [
            "InTrust CRE Office",
        ],
    },
    {
        "brokerage": "Spacelist",
        "brokers": [
            "Spacelist Platform",
        ],
    },
    {
        "brokerage": "ICX",
        "brokers": [
            "ICX Platform",
        ],
    },
]


def seed():
    init_db()
    conn = get_connection()

    count = 0
    for entry in BROKERAGES:
        brokerage = entry["brokerage"]
        for broker_name in entry["brokers"]:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO brokers (name, brokerage) VALUES (?, ?)",
                    (broker_name, brokerage),
                )
                count += 1
            except Exception as e:
                print(f"Error seeding {broker_name} @ {brokerage}: {e}")

    conn.commit()
    conn.close()
    print(f"Seeded {count} broker entries across {len(BROKERAGES)} brokerages.")
    print("You can now manually add email, phone, and LinkedIn URLs via SQLite.")
    print(f"Database: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gta_cre.db')}")


if __name__ == "__main__":
    seed()
