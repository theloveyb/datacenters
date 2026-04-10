"""FastAPI backend for GTA CRE Dashboard."""

import os
import sys
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from backend.database import (
    get_connection,
    init_db,
    get_active_listings,
    get_new_this_week,
    get_delisted_this_week,
    get_brokers_with_counts,
    get_listing_counts_by_brokerage,
    get_filter_options,
)

app = FastAPI(title="GTA CRE Dashboard API", version="1.0.0")

# CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/listings")
def api_listings(
    asset_type: Optional[str] = Query(None),
    listing_type: Optional[str] = Query(None),
    brokerage: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_sqft: Optional[float] = Query(None),
    max_sqft: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
):
    conn = get_connection()
    try:
        listings = get_active_listings(
            conn,
            asset_type=asset_type,
            listing_type=listing_type,
            brokerage=brokerage,
            city=city,
            min_price=min_price,
            max_price=max_price,
            min_sqft=min_sqft,
            max_sqft=max_sqft,
            search=search,
        )
        return {"listings": listings, "count": len(listings)}
    finally:
        conn.close()


@app.get("/api/listings/new")
def api_new_listings():
    conn = get_connection()
    try:
        listings = get_new_this_week(conn)
        return {"listings": listings, "count": len(listings)}
    finally:
        conn.close()


@app.get("/api/listings/delisted")
def api_delisted_listings():
    conn = get_connection()
    try:
        listings = get_delisted_this_week(conn)
        return {"listings": listings, "count": len(listings)}
    finally:
        conn.close()


@app.get("/api/brokers")
def api_brokers():
    conn = get_connection()
    try:
        brokers = get_brokers_with_counts(conn)
        return {"brokers": brokers, "count": len(brokers)}
    finally:
        conn.close()


@app.get("/api/stats/by-brokerage")
def api_stats_by_brokerage():
    conn = get_connection()
    try:
        stats = get_listing_counts_by_brokerage(conn)
        return {"stats": stats}
    finally:
        conn.close()


@app.get("/api/filters")
def api_filters():
    conn = get_connection()
    try:
        return get_filter_options(conn)
    finally:
        conn.close()
