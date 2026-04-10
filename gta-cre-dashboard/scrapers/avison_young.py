"""Avison Young scraper.

Avison Young has a property search at avisonyoung.com/properties.
JS-rendered listings loaded via API.
"""

import asyncio
import logging

from .base import BaseScraper, random_delay, fetch_page_playwright

logger = logging.getLogger(__name__)

AY_API_URL = "https://www.avisonyoung.com/api/properties/search"


class AvisonYoungScraper(BaseScraper):
    BROKERAGE_NAME = "Avison Young"
    BASE_URL = "https://www.avisonyoung.com"

    def scrape(self) -> list[dict]:
        listings = []

        # Try API
        try:
            listings = self._scrape_via_api()
            if listings:
                return listings
        except Exception as e:
            self.logger.warning(f"AY API failed: {e}")

        # Fall back to Playwright
        try:
            listings = self._scrape_via_playwright()
        except Exception as e:
            self.logger.error(f"AY Playwright failed: {e}")

        return listings

    def _scrape_via_api(self) -> list[dict]:
        listings = []

        params = {
            "location": "Toronto, ON, Canada",
            "radius": "50",
            "radiusUnit": "km",
            "country": "CA",
            "province": "ON",
            "pageSize": 100,
        }

        try:
            response = self.session.get(AY_API_URL, params=params, timeout=30)
            if response.status_code != 200:
                response = self.session.post(AY_API_URL, json=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            properties = data if isinstance(data, list) else data.get("results", data.get("properties", []))

            for prop in properties:
                try:
                    addr = prop.get("address", "")
                    if isinstance(addr, dict):
                        addr = addr.get("line1", "") or addr.get("street", "")
                    if not addr:
                        continue

                    city = prop.get("city", "")
                    if isinstance(city, dict):
                        city = city.get("name", "")

                    brokers = prop.get("contacts", prop.get("brokers", []))
                    broker_names = []
                    for b in (brokers if isinstance(brokers, list) else []):
                        if isinstance(b, dict):
                            name = b.get("name", "") or f"{b.get('firstName', '')} {b.get('lastName', '')}".strip()
                            if name:
                                broker_names.append(name)

                    url = prop.get("url", prop.get("detailUrl", ""))
                    if url and not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"

                    listing = self.make_listing(
                        address=addr,
                        city=city,
                        neighbourhood=prop.get("neighbourhood", prop.get("submarket")),
                        asset_type=prop.get("propertyType", ""),
                        listing_type=prop.get("transactionType", ""),
                        asking_price=str(prop.get("price", "")) or None,
                        asking_rent=str(prop.get("rent", "")) or None,
                        square_footage=str(prop.get("size", "")) or None,
                        broker_names=", ".join(broker_names) if broker_names else None,
                        listing_url=url,
                    )
                    listings.append(listing)

                except Exception as e:
                    self.logger.warning(f"Failed to parse AY property: {e}")

        except Exception as e:
            raise

        return listings

    def _scrape_via_playwright(self) -> list[dict]:
        listings = []
        url = f"{self.BASE_URL}/properties?location=Toronto%2C+ON&radius=50km"

        try:
            loop = asyncio.new_event_loop()
            soup = loop.run_until_complete(
                fetch_page_playwright(url, wait_selector=".property-card, .listing-card")
            )
            loop.close()
        except Exception as e:
            self.logger.error(f"AY Playwright failed: {e}")
            return listings

        if not soup:
            return listings

        cards = soup.select(".property-card, .listing-card, .property-item, .search-result")
        for card in cards:
            try:
                addr_el = card.select_one("h3, h4, .address, .property-address")
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address:
                    continue

                type_el = card.select_one(".property-type, .type")
                price_el = card.select_one(".price, .property-price")
                size_el = card.select_one(".size, .sqft")
                link_el = card.select_one("a[href]")

                price_text = price_el.get_text(strip=True) if price_el else ""
                lt = "Lease" if any(x in price_text.lower() for x in ["lease", "/sf", "psf"]) else "Sale"
                link = link_el["href"] if link_el else ""
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL}{link}"

                listing = self.make_listing(
                    address=address,
                    asset_type=type_el.get_text(strip=True) if type_el else None,
                    listing_type=lt,
                    asking_price=price_text if lt == "Sale" else None,
                    asking_rent=price_text if lt == "Lease" else None,
                    square_footage=size_el.get_text(strip=True) if size_el else None,
                    listing_url=link,
                )
                listings.append(listing)

            except Exception as e:
                self.logger.warning(f"Failed to parse AY card: {e}")

        return listings


def scrape() -> list[dict]:
    return AvisonYoungScraper().scrape()
