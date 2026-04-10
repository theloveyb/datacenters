"""ICX.ca scraper.

ICX (icx.ca) is a Canadian commercial real estate listing platform.
They have property search with GTA filtering.
"""

import asyncio
import logging

from .base import BaseScraper, fetch_page, random_delay, fetch_page_playwright

logger = logging.getLogger(__name__)


class ICXScraper(BaseScraper):
    BROKERAGE_NAME = "ICX"
    BASE_URL = "https://www.icx.ca"

    def scrape(self) -> list[dict]:
        listings = []

        # Try static scraping first
        try:
            listings = self._scrape_static()
            if listings:
                return listings
        except Exception as e:
            self.logger.warning(f"ICX static scrape failed: {e}")

        # Fall back to Playwright
        try:
            listings = self._scrape_playwright()
        except Exception as e:
            self.logger.error(f"ICX Playwright failed: {e}")

        return listings

    def _scrape_static(self) -> list[dict]:
        listings = []

        search_urls = [
            f"{self.BASE_URL}/search?city=Toronto&province=ON",
            f"{self.BASE_URL}/properties?city=Toronto&province=ON",
            f"{self.BASE_URL}/listings?location=Toronto",
            f"{self.BASE_URL}/search?location=GTA",
            f"{self.BASE_URL}/toronto",
        ]

        for url in search_urls:
            try:
                soup = fetch_page(url, self.session)
                if not soup:
                    continue

                page_listings = self._parse_page(soup, url)
                if page_listings:
                    listings.extend(page_listings)

                    # Pagination
                    page = 2
                    while page <= 10:
                        sep = "&" if "?" in url else "?"
                        next_url = f"{url}{sep}page={page}"
                        random_delay()
                        next_soup = fetch_page(next_url, self.session)
                        if not next_soup:
                            break
                        next_listings = self._parse_page(next_soup, next_url)
                        if not next_listings:
                            break
                        listings.extend(next_listings)
                        page += 1

                    break

                random_delay()
            except Exception as e:
                self.logger.warning(f"ICX URL {url} failed: {e}")

        return listings

    def _scrape_playwright(self) -> list[dict]:
        listings = []
        url = f"{self.BASE_URL}/search?city=Toronto&province=ON"

        try:
            loop = asyncio.new_event_loop()
            soup = loop.run_until_complete(
                fetch_page_playwright(url, wait_selector=".listing-card, .property-card")
            )
            loop.close()
        except Exception as e:
            self.logger.error(f"ICX Playwright failed: {e}")
            return listings

        if soup:
            listings = self._parse_page(soup, url)

        return listings

    def _parse_page(self, soup, page_url: str) -> list[dict]:
        listings = []

        cards = soup.select(
            ".listing-card, .property-card, .search-result, "
            ".listing-item, .property-item, .listing, "
            "[data-listing], .listing-row, .result-card, "
            ".property-listing"
        )

        for card in cards:
            try:
                addr_el = card.select_one(
                    "h2, h3, h4, .listing-title, .property-title, "
                    ".address, .listing-address"
                )
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address or len(address) < 5:
                    continue

                text = card.get_text(" ", strip=True)

                type_el = card.select_one(".property-type, .type, .category")
                price_el = card.select_one(".price, .listing-price, .property-price")
                size_el = card.select_one(".size, .sqft, .area")
                city_el = card.select_one(".city, .location")
                broker_el = card.select_one(".broker, .agent, .listed-by")

                price_text = price_el.get_text(strip=True) if price_el else None
                size_text = size_el.get_text(strip=True) if size_el else None
                asset_type = type_el.get_text(strip=True) if type_el else None
                city = city_el.get_text(strip=True) if city_el else "Toronto"
                broker_name = broker_el.get_text(strip=True) if broker_el else None

                link_el = card.select_one("a[href]")
                link = ""
                if link_el:
                    link = link_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"{self.BASE_URL}{link}"

                lt = None
                if price_text:
                    lt = "Lease" if any(x in price_text.lower() for x in ["lease", "/sf", "psf"]) else "Sale"
                elif "lease" in text.lower() or "rent" in text.lower():
                    lt = "Lease"
                elif "sale" in text.lower():
                    lt = "Sale"

                listing = self.make_listing(
                    address=address,
                    city=city,
                    asset_type=asset_type,
                    listing_type=lt,
                    asking_price=price_text if lt == "Sale" else None,
                    asking_rent=price_text if lt == "Lease" else None,
                    square_footage=size_text,
                    broker_names=broker_name,
                    listing_url=link or page_url,
                )
                listings.append(listing)

            except Exception as e:
                self.logger.warning(f"Failed to parse ICX card: {e}")

        return listings


def scrape() -> list[dict]:
    return ICXScraper().scrape()
