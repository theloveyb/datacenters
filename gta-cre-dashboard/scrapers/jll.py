"""JLL Canada scraper.

JLL uses a JS-rendered property search. Their listings are loaded via API.
We try their property search API first, then fall back to Playwright.
"""

import asyncio
import logging

from .base import BaseScraper, random_delay, fetch_page_playwright

logger = logging.getLogger(__name__)

JLL_API_URL = "https://www.jll.ca/api/properties"
JLL_SEARCH_URL = "https://www.jll.ca/en/properties"


class JLLScraper(BaseScraper):
    BROKERAGE_NAME = "JLL"
    BASE_URL = "https://www.jll.ca"

    def scrape(self) -> list[dict]:
        listings = []

        # Try API approach
        try:
            listings = self._scrape_via_api()
            if listings:
                return listings
        except Exception as e:
            self.logger.warning(f"JLL API approach failed: {e}")

        # Fall back to Playwright
        try:
            listings = self._scrape_via_playwright()
        except Exception as e:
            self.logger.error(f"JLL Playwright approach failed: {e}")

        return listings

    def _scrape_via_api(self) -> list[dict]:
        """Try JLL property search API."""
        listings = []

        params = {
            "country": "CA",
            "state": "ON",
            "city": "Toronto",
            "radius": "50",
            "radiusUnit": "km",
            "pageSize": 100,
            "page": 1,
        }

        try:
            response = self.session.get(JLL_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            properties = data.get("properties", data.get("results", data.get("items", [])))
            if not properties and isinstance(data, list):
                properties = data

            for prop in properties:
                try:
                    addr = prop.get("address", "")
                    if isinstance(addr, dict):
                        addr = addr.get("line1", "") or addr.get("street", "")
                    if not addr:
                        continue

                    city = prop.get("city", "Toronto")
                    asset_type = prop.get("propertyType", "") or prop.get("type", "")
                    listing_type = prop.get("transactionType", "") or prop.get("listingType", "")

                    price = prop.get("price", prop.get("askingPrice"))
                    rent = prop.get("rent", prop.get("askingRent"))
                    sqft = prop.get("size", prop.get("area", prop.get("squareFeet")))

                    brokers = prop.get("contacts", prop.get("brokers", []))
                    broker_names = []
                    for b in (brokers if isinstance(brokers, list) else []):
                        if isinstance(b, dict):
                            name = b.get("name", "")
                            if not name:
                                name = f"{b.get('firstName', '')} {b.get('lastName', '')}".strip()
                            if name:
                                broker_names.append(name)

                    url = prop.get("url", prop.get("detailUrl", ""))
                    if url and not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"

                    listing = self.make_listing(
                        address=addr,
                        city=city if isinstance(city, str) else None,
                        asset_type=asset_type,
                        listing_type=listing_type,
                        asking_price=str(price) if price else None,
                        asking_rent=str(rent) if rent else None,
                        square_footage=str(sqft) if sqft else None,
                        broker_names=", ".join(broker_names) if broker_names else None,
                        listing_url=url,
                    )
                    listings.append(listing)

                except Exception as e:
                    self.logger.warning(f"Failed to parse JLL property: {e}")

        except Exception as e:
            self.logger.error(f"JLL API failed: {e}")
            raise

        return listings

    def _scrape_via_playwright(self) -> list[dict]:
        """Scrape JLL using Playwright for JS-rendered content."""
        listings = []
        url = f"{JLL_SEARCH_URL}?country=CA&state=ON&city=Toronto&radius=50km"

        try:
            loop = asyncio.new_event_loop()
            soup = loop.run_until_complete(
                fetch_page_playwright(url, wait_selector=".property-card, .listing-card")
            )
            loop.close()
        except Exception as e:
            self.logger.error(f"JLL Playwright failed: {e}")
            return listings

        if not soup:
            return listings

        cards = soup.select(
            ".property-card, .listing-card, .PropertyCard, "
            "[data-component='PropertyCard']"
        )

        for card in cards:
            try:
                addr_el = card.select_one("h3, h4, .property-address, .address")
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address:
                    continue

                type_el = card.select_one(".property-type, .type-label")
                asset_type = type_el.get_text(strip=True) if type_el else None

                price_el = card.select_one(".price, .property-price")
                price_text = price_el.get_text(strip=True) if price_el else ""

                size_el = card.select_one(".size, .property-size, .sqft")
                size_text = size_el.get_text(strip=True) if size_el else ""

                link_el = card.select_one("a[href]")
                link = link_el["href"] if link_el else ""
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL}{link}"

                lt = "Lease" if "lease" in price_text.lower() or "/sf" in price_text.lower() else "Sale"

                listing = self.make_listing(
                    address=address,
                    asset_type=asset_type,
                    listing_type=lt,
                    asking_price=price_text if lt == "Sale" else None,
                    asking_rent=price_text if lt == "Lease" else None,
                    square_footage=size_text,
                    listing_url=link,
                )
                listings.append(listing)

            except Exception as e:
                self.logger.warning(f"Failed to parse JLL card: {e}")

        return listings


def scrape() -> list[dict]:
    return JLLScraper().scrape()
