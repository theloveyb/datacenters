"""Base scraper module with common interface and utilities."""

import logging
import random
import re
import time
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Common headers
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# GTA cities and neighbourhoods for filtering
GTA_CITIES = {
    "toronto",
    "mississauga",
    "brampton",
    "vaughan",
    "markham",
    "richmond hill",
    "oakville",
    "burlington",
    "milton",
    "pickering",
    "ajax",
    "whitby",
    "oshawa",
    "newmarket",
    "aurora",
    "king",
    "caledon",
    "halton hills",
    "east gwillimbury",
    "georgina",
    "clarington",
    "scugog",
    "uxbridge",
    "brock",
    "north york",
    "scarborough",
    "etobicoke",
    "york",
    "east york",
}

# Asset type normalization mapping
ASSET_TYPE_MAP = {
    "office": "Office",
    "retail": "Retail",
    "industrial": "Industrial",
    "warehouse": "Industrial",
    "manufacturing": "Industrial",
    "logistics": "Industrial",
    "distribution": "Industrial",
    "multifamily": "Multifamily",
    "multi-family": "Multifamily",
    "apartment": "Multifamily",
    "residential": "Multifamily",
    "land": "Land",
    "development": "Land",
    "dev site": "Land",
    "mixed-use": "Mixed-Use",
    "mixed use": "Mixed-Use",
    "flex": "Mixed-Use",
    "special purpose": "Mixed-Use",
    "hospitality": "Mixed-Use",
    "hotel": "Mixed-Use",
}

# Street suffix normalization
STREET_SUFFIXES = {
    "st": "St",
    "st.": "St",
    "street": "St",
    "ave": "Ave",
    "ave.": "Ave",
    "avenue": "Ave",
    "blvd": "Blvd",
    "blvd.": "Blvd",
    "boulevard": "Blvd",
    "dr": "Dr",
    "dr.": "Dr",
    "drive": "Dr",
    "rd": "Rd",
    "rd.": "Rd",
    "road": "Rd",
    "cres": "Cres",
    "cres.": "Cres",
    "crescent": "Cres",
    "ct": "Ct",
    "ct.": "Ct",
    "court": "Ct",
    "pl": "Pl",
    "pl.": "Pl",
    "place": "Pl",
    "ln": "Ln",
    "ln.": "Ln",
    "lane": "Ln",
    "way": "Way",
    "cir": "Cir",
    "cir.": "Cir",
    "circle": "Cir",
    "terr": "Terr",
    "terr.": "Terr",
    "terrace": "Terr",
    "pkwy": "Pkwy",
    "parkway": "Pkwy",
    "hwy": "Hwy",
    "highway": "Hwy",
    "trail": "Trail",
    "trl": "Trail",
}


def normalize_address(address: str) -> str:
    """Normalize an address for deduplication.

    - Strip unit/suite numbers
    - Standardize street suffixes
    - Normalize whitespace and casing
    """
    if not address:
        return ""

    addr = address.strip()

    # Remove unit/suite numbers (e.g., "Unit 5", "Suite 200", "#3", "Apt 4")
    addr = re.sub(
        r"\b(unit|suite|ste|apt|apartment|#)\s*[\w-]+",
        "",
        addr,
        flags=re.IGNORECASE,
    )

    # Remove floor references
    addr = re.sub(
        r"\b\d+(st|nd|rd|th)\s*floor\b", "", addr, flags=re.IGNORECASE
    )

    # Remove leading/trailing commas and dashes left after stripping
    addr = re.sub(r"^[\s,\-]+", "", addr)
    addr = re.sub(r"[\s,\-]+$", "", addr)

    # Normalize whitespace
    addr = re.sub(r"\s+", " ", addr).strip()

    # Standardize street suffixes
    words = addr.split()
    normalized_words = []
    for word in words:
        lower = word.lower().rstrip(".,")
        if lower in STREET_SUFFIXES:
            normalized_words.append(STREET_SUFFIXES[lower])
        else:
            normalized_words.append(word)

    addr = " ".join(normalized_words)

    # Title case
    addr = addr.title()

    return addr


def normalize_asset_type(raw_type: str) -> Optional[str]:
    """Normalize asset type to standard categories."""
    if not raw_type:
        return None

    lower = raw_type.lower().strip()
    for key, value in ASSET_TYPE_MAP.items():
        if key in lower:
            return value

    return raw_type.title()


def normalize_listing_type(raw_type: str) -> Optional[str]:
    """Normalize listing type to 'Sale' or 'Lease'."""
    if not raw_type:
        return None

    lower = raw_type.lower().strip()
    if "sale" in lower or "buy" in lower or "purchase" in lower:
        return "Sale"
    if "lease" in lower or "rent" in lower or "let" in lower:
        return "Lease"

    return raw_type.title()


def parse_price(price_str: str) -> Optional[float]:
    """Parse a price string into a float."""
    if not price_str:
        return None

    # Remove currency symbols, commas, whitespace
    cleaned = re.sub(r"[^\d.]", "", price_str)

    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def parse_sqft(sqft_str: str) -> Optional[float]:
    """Parse a square footage string into a float."""
    if not sqft_str:
        return None

    cleaned = re.sub(r"[^\d.]", "", sqft_str)

    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def is_gta_location(city: str) -> bool:
    """Check if a city/location is in the GTA."""
    if not city:
        return False
    return city.lower().strip() in GTA_CITIES


def random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """Sleep for a random duration between min and max seconds."""
    time.sleep(random.uniform(min_seconds, max_seconds))


def check_robots_txt(base_url: str, path: str = "/") -> bool:
    """Check if scraping is allowed by robots.txt."""
    try:
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(DEFAULT_HEADERS["User-Agent"], f"{base_url}{path}")
    except Exception:
        # If we can't read robots.txt, proceed with caution
        return True


def fetch_page(url: str, session: Optional[requests.Session] = None) -> Optional[BeautifulSoup]:
    """Fetch a page and return a BeautifulSoup object."""
    s = session or requests.Session()
    try:
        response = s.get(url, headers=DEFAULT_HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


async def fetch_page_playwright(url: str, wait_selector: Optional[str] = None):
    """Fetch a JS-rendered page using Playwright. Returns HTML string."""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent=DEFAULT_HEADERS["User-Agent"]
            )
            await page.goto(url, wait_until="networkidle", timeout=60000)

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=15000)

            content = await page.content()
            await browser.close()
            return BeautifulSoup(content, "html.parser")
    except Exception as e:
        logger.error(f"Playwright failed for {url}: {e}")
        return None


class BaseScraper(ABC):
    """Base class for all CRE listing scrapers."""

    BROKERAGE_NAME: str = ""
    BASE_URL: str = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Scrape listings and return a list of standardized listing dicts.

        Each dict should have:
            - address: str (normalized)
            - city: str | None
            - neighbourhood: str | None
            - asset_type: str | None (Office, Retail, Industrial, Multifamily, Land, Mixed-Use)
            - listing_type: str | None (Sale or Lease)
            - asking_price: float | None
            - asking_rent: float | None
            - square_footage: float | None
            - broker_names: str | None (comma-separated)
            - brokerage: str
            - listing_url: str | None
        """
        pass

    def make_listing(
        self,
        address: str,
        city: Optional[str] = None,
        neighbourhood: Optional[str] = None,
        asset_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        asking_price: Optional[str] = None,
        asking_rent: Optional[str] = None,
        square_footage: Optional[str] = None,
        broker_names: Optional[str] = None,
        listing_url: Optional[str] = None,
    ) -> dict:
        """Create a standardized listing dict with normalization applied."""
        return {
            "address": normalize_address(address),
            "city": city.strip().title() if city else None,
            "neighbourhood": neighbourhood.strip().title() if neighbourhood else None,
            "asset_type": normalize_asset_type(asset_type) if asset_type else None,
            "listing_type": normalize_listing_type(listing_type) if listing_type else None,
            "asking_price": parse_price(str(asking_price)) if asking_price else None,
            "asking_rent": parse_price(str(asking_rent)) if asking_rent else None,
            "square_footage": parse_sqft(str(square_footage)) if square_footage else None,
            "broker_names": broker_names.strip() if broker_names else None,
            "brokerage": self.BROKERAGE_NAME,
            "listing_url": listing_url,
        }
