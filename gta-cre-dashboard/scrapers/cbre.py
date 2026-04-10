"""CBRE Canada scraper.

CBRE uses a JS-rendered property search at cbre.ca/en/properties.
Their listings are loaded dynamically via API calls.
We attempt to hit their search API directly; fall back to Playwright if needed.
"""

import logging

from .base import BaseScraper, random_delay, parse_price, parse_sqft, normalize_asset_type

logger = logging.getLogger(__name__)

# CBRE's property search API endpoint (discovered from network inspection)
CBRE_API_URL = "https://www.cbre.ca/api/properties/search"

CBRE_SEARCH_PARAMS = {
    "location": "Toronto, ON, Canada",
    "radius": "50km",
    "pageSize": 100,
    "page": 1,
}


class CBREScraper(BaseScraper):
    BROKERAGE_NAME = "CBRE"
    BASE_URL = "https://www.cbre.ca"

    def scrape(self) -> list[dict]:
        listings = []

        # Try API approach first
        try:
            listings = self._scrape_via_api()
            if listings:
                return listings
        except Exception as e:
            self.logger.warning(f"CBRE API approach failed: {e}")

        # Fall back to Playwright
        try:
            listings = self._scrape_via_playwright()
        except Exception as e:
            self.logger.error(f"CBRE Playwright approach failed: {e}")

        return listings

    def _scrape_via_api(self) -> list[dict]:
        """Try to scrape via CBRE's internal property search API."""
        listings = []

        try:
            response = self.session.get(
                CBRE_API_URL,
                params=CBRE_SEARCH_PARAMS,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            properties = data.get("properties", data.get("results", []))
            if not properties and isinstance(data, list):
                properties = data

            for prop in properties:
                try:
                    address = prop.get("address", {})
                    if isinstance(address, dict):
                        addr_str = address.get("line1", "") or address.get("streetAddress", "")
                        city = address.get("city", "")
                    else:
                        addr_str = str(address)
                        city = prop.get("city", "")

                    if not addr_str:
                        continue

                    listing_type_raw = prop.get("transactionType", "") or prop.get("listingType", "")
                    asset_type_raw = prop.get("propertyType", "") or prop.get("type", "")

                    price = prop.get("price", prop.get("askingPrice"))
                    rent = prop.get("rent", prop.get("askingRent"))
                    sqft = prop.get("size", prop.get("totalSize", prop.get("squareFeet")))

                    brokers = prop.get("contacts", prop.get("brokers", []))
                    broker_names = []
                    if isinstance(brokers, list):
                        for b in brokers:
                            if isinstance(b, dict):
                                name = b.get("name", "") or f"{b.get('firstName', '')} {b.get('lastName', '')}".strip()
                                if name:
                                    broker_names.append(name)
                            elif isinstance(b, str):
                                broker_names.append(b)

                    listing_url = prop.get("url", prop.get("detailUrl", ""))
                    if listing_url and not listing_url.startswith("http"):
                        listing_url = f"{self.BASE_URL}{listing_url}"

                    listing = self.make_listing(
                        address=addr_str,
                        city=city,
                        asset_type=asset_type_raw,
                        listing_type=listing_type_raw,
                        asking_price=str(price) if price and "sale" in str(listing_type_raw).lower() else None,
                        asking_rent=str(rent) if rent else (str(price) if price and "lease" in str(listing_type_raw).lower() else None),
                        square_footage=str(sqft) if sqft else None,
                        broker_names=", ".join(broker_names) if broker_names else None,
                        listing_url=listing_url,
                    )
                    listings.append(listing)
                    random_delay(0.1, 0.3)

                except Exception as e:
                    self.logger.warning(f"Failed to parse CBRE property: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"CBRE API request failed: {e}")
            raise

        return listings

    def _scrape_via_playwright(self) -> list[dict]:
        """Fall back to Playwright for JS-rendered content."""
        import asyncio
        from .base import fetch_page_playwright

        listings = []
        url = f"{self.BASE_URL}/en/properties?location=Toronto%2C+ON&radius=50km"

        async def _fetch():
            soup = await fetch_page_playwright(url, wait_selector=".property-card")
            return soup

        soup = asyncio.get_event_loop().run_until_complete(_fetch()) if True else None

        try:
            loop = asyncio.new_event_loop()
            soup = loop.run_until_complete(_fetch())
            loop.close()
        except Exception as e:
            self.logger.error(f"CBRE Playwright failed: {e}")
            return listings

        if not soup:
            return listings

        cards = soup.select(".property-card, .PropertyCard, [data-testid='property-card']")
        for card in cards:
            try:
                addr_el = card.select_one(".property-address, .address, h3, h4")
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address:
                    continue

                type_el = card.select_one(".property-type, .type")
                asset_type = type_el.get_text(strip=True) if type_el else None

                price_el = card.select_one(".property-price, .price")
                price_text = price_el.get_text(strip=True) if price_el else ""

                sqft_el = card.select_one(".property-size, .size, .sqft")
                sqft_text = sqft_el.get_text(strip=True) if sqft_el else ""

                link_el = card.select_one("a[href]")
                link = link_el["href"] if link_el else ""
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL}{link}"

                listing_type = "Lease" if "lease" in price_text.lower() else "Sale"

                listing = self.make_listing(
                    address=address,
                    asset_type=asset_type,
                    listing_type=listing_type,
                    asking_price=price_text if listing_type == "Sale" else None,
                    asking_rent=price_text if listing_type == "Lease" else None,
                    square_footage=sqft_text,
                    listing_url=link,
                )
                listings.append(listing)

            except Exception as e:
                self.logger.warning(f"Failed to parse CBRE card: {e}")
                continue

        return listings


def scrape() -> list[dict]:
    """Module-level scrape function."""
    return CBREScraper().scrape()
