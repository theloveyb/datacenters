"""SQLite database layer for GTA CRE Dashboard."""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.environ.get(
    "GTA_CRE_DB", os.path.join(os.path.dirname(__file__), "..", "gta_cre.db")
)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Optional[str] = None):
    """Initialize the database schema."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            city TEXT,
            neighbourhood TEXT,
            asset_type TEXT,
            listing_type TEXT,
            asking_price REAL,
            asking_rent REAL,
            square_footage REAL,
            broker_names TEXT,
            brokerage TEXT NOT NULL,
            listing_url TEXT,
            date_first_seen TEXT NOT NULL,
            date_last_seen TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(address, brokerage)
        );

        CREATE TABLE IF NOT EXISTS brokers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brokerage TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            linkedin_url TEXT,
            UNIQUE(name, brokerage)
        );

        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            brokerage TEXT NOT NULL,
            listings_found INTEGER NOT NULL DEFAULT 0,
            errors INTEGER NOT NULL DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_listings_active ON listings(is_active);
        CREATE INDEX IF NOT EXISTS idx_listings_brokerage ON listings(brokerage);
        CREATE INDEX IF NOT EXISTS idx_listings_asset_type ON listings(asset_type);
        CREATE INDEX IF NOT EXISTS idx_listings_listing_type ON listings(listing_type);
        CREATE INDEX IF NOT EXISTS idx_listings_city ON listings(city);
        CREATE INDEX IF NOT EXISTS idx_listings_date_first_seen ON listings(date_first_seen);
        CREATE INDEX IF NOT EXISTS idx_listings_date_last_seen ON listings(date_last_seen);
        CREATE INDEX IF NOT EXISTS idx_brokers_brokerage ON brokers(brokerage);
    """)

    conn.commit()
    conn.close()


def upsert_listing(conn: sqlite3.Connection, listing: dict) -> str:
    """Insert or update a listing. Returns 'new', 'updated', or 'error'."""
    today = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, is_active FROM listings WHERE address = ? AND brokerage = ?",
            (listing["address"], listing["brokerage"]),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """UPDATE listings
                   SET date_last_seen = ?, is_active = 1,
                       city = COALESCE(?, city),
                       neighbourhood = COALESCE(?, neighbourhood),
                       asset_type = COALESCE(?, asset_type),
                       listing_type = COALESCE(?, listing_type),
                       asking_price = COALESCE(?, asking_price),
                       asking_rent = COALESCE(?, asking_rent),
                       square_footage = COALESCE(?, square_footage),
                       broker_names = COALESCE(?, broker_names),
                       listing_url = COALESCE(?, listing_url)
                   WHERE id = ?""",
                (
                    today,
                    listing.get("city"),
                    listing.get("neighbourhood"),
                    listing.get("asset_type"),
                    listing.get("listing_type"),
                    listing.get("asking_price"),
                    listing.get("asking_rent"),
                    listing.get("square_footage"),
                    listing.get("broker_names"),
                    listing.get("listing_url"),
                    existing["id"],
                ),
            )
            return "updated"
        else:
            cursor.execute(
                """INSERT INTO listings
                   (address, city, neighbourhood, asset_type, listing_type,
                    asking_price, asking_rent, square_footage, broker_names,
                    brokerage, listing_url, date_first_seen, date_last_seen, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (
                    listing["address"],
                    listing.get("city"),
                    listing.get("neighbourhood"),
                    listing.get("asset_type"),
                    listing.get("listing_type"),
                    listing.get("asking_price"),
                    listing.get("asking_rent"),
                    listing.get("square_footage"),
                    listing.get("broker_names"),
                    listing["brokerage"],
                    listing.get("listing_url"),
                    today,
                    today,
                ),
            )
            return "new"
    except Exception:
        return "error"


def mark_delisted(conn: sqlite3.Connection, brokerage: str, active_addresses: set):
    """Mark listings as inactive if they weren't found in the latest scrape."""
    today = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, address FROM listings WHERE brokerage = ? AND is_active = 1",
        (brokerage,),
    )
    existing = cursor.fetchall()

    delisted = 0
    for row in existing:
        if row["address"] not in active_addresses:
            cursor.execute(
                "UPDATE listings SET is_active = 0, date_last_seen = ? WHERE id = ?",
                (today, row["id"]),
            )
            delisted += 1

    return delisted


def record_scrape_run(
    conn: sqlite3.Connection, brokerage: str, listings_found: int, errors: int
):
    """Record a scrape run in the scrape_runs table."""
    conn.execute(
        "INSERT INTO scrape_runs (timestamp, brokerage, listings_found, errors) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), brokerage, listings_found, errors),
    )


def upsert_broker(conn: sqlite3.Connection, name: str, brokerage: str):
    """Insert a broker if not already present."""
    try:
        conn.execute(
            "INSERT OR IGNORE INTO brokers (name, brokerage) VALUES (?, ?)",
            (name, brokerage),
        )
    except Exception:
        pass


# --- Query functions for the API ---


def get_active_listings(
    conn: sqlite3.Connection,
    asset_type: Optional[str] = None,
    listing_type: Optional[str] = None,
    brokerage: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_sqft: Optional[float] = None,
    max_sqft: Optional[float] = None,
    search: Optional[str] = None,
) -> list:
    """Get active listings with optional filters."""
    query = """
        SELECT *, julianday('now') - julianday(date_first_seen) AS days_on_market
        FROM listings WHERE is_active = 1
    """
    params = []

    if asset_type:
        query += " AND asset_type = ?"
        params.append(asset_type)
    if listing_type:
        query += " AND listing_type = ?"
        params.append(listing_type)
    if brokerage:
        query += " AND brokerage = ?"
        params.append(brokerage)
    if city:
        query += " AND city = ?"
        params.append(city)
    if min_price is not None:
        query += " AND (asking_price >= ? OR asking_rent >= ?)"
        params.extend([min_price, min_price])
    if max_price is not None:
        query += " AND (asking_price <= ? OR asking_rent <= ?)"
        params.extend([max_price, max_price])
    if min_sqft is not None:
        query += " AND square_footage >= ?"
        params.append(min_sqft)
    if max_sqft is not None:
        query += " AND square_footage <= ?"
        params.append(max_sqft)
    if search:
        query += " AND (address LIKE ? OR broker_names LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY date_first_seen DESC"
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_new_this_week(conn: sqlite3.Connection) -> list:
    """Get listings first seen in the last 7 days."""
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = """
        SELECT *, julianday('now') - julianday(date_first_seen) AS days_on_market
        FROM listings WHERE date_first_seen >= ? AND is_active = 1
        ORDER BY date_first_seen DESC
    """
    return [dict(row) for row in conn.execute(query, (week_ago,)).fetchall()]


def get_delisted_this_week(conn: sqlite3.Connection) -> list:
    """Get listings that went inactive in the last 7 days."""
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = """
        SELECT *, julianday(date_last_seen) - julianday(date_first_seen) AS days_on_market
        FROM listings WHERE is_active = 0 AND date_last_seen >= ?
        ORDER BY date_last_seen DESC
    """
    return [dict(row) for row in conn.execute(query, (week_ago,)).fetchall()]


def get_brokers_with_counts(conn: sqlite3.Connection) -> list:
    """Get all brokers with their active listing counts."""
    query = """
        SELECT b.id, b.name, b.brokerage, b.email, b.phone, b.linkedin_url,
               COUNT(CASE WHEN l.is_active = 1 THEN 1 END) AS active_listings
        FROM brokers b
        LEFT JOIN listings l ON l.brokerage = b.brokerage
            AND l.broker_names LIKE '%' || b.name || '%'
        GROUP BY b.id
        ORDER BY active_listings DESC
    """
    return [dict(row) for row in conn.execute(query).fetchall()]


def get_listing_counts_by_brokerage(conn: sqlite3.Connection) -> list:
    """Get active listing counts grouped by brokerage."""
    query = """
        SELECT brokerage, COUNT(*) as count
        FROM listings WHERE is_active = 1
        GROUP BY brokerage
        ORDER BY count DESC
    """
    return [dict(row) for row in conn.execute(query).fetchall()]


def get_filter_options(conn: sqlite3.Connection) -> dict:
    """Get distinct values for filter dropdowns."""
    asset_types = [
        row["asset_type"]
        for row in conn.execute(
            "SELECT DISTINCT asset_type FROM listings WHERE asset_type IS NOT NULL ORDER BY asset_type"
        ).fetchall()
    ]
    listing_types = [
        row["listing_type"]
        for row in conn.execute(
            "SELECT DISTINCT listing_type FROM listings WHERE listing_type IS NOT NULL ORDER BY listing_type"
        ).fetchall()
    ]
    brokerages = [
        row["brokerage"]
        for row in conn.execute(
            "SELECT DISTINCT brokerage FROM listings ORDER BY brokerage"
        ).fetchall()
    ]
    cities = [
        row["city"]
        for row in conn.execute(
            "SELECT DISTINCT city FROM listings WHERE city IS NOT NULL ORDER BY city"
        ).fetchall()
    ]
    return {
        "asset_types": asset_types,
        "listing_types": listing_types,
        "brokerages": brokerages,
        "cities": cities,
    }
