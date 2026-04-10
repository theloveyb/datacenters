"""Lennard Commercial Realty scraper.

Lennard (lennard.com) is a GTA-focused commercial brokerage.
Likely a simpler site with static or lightly dynamic listing pages.
"""

import logging

from .base import BaseScraper, fetch_page, random_delay

logger = logging.getLogger(__name__)


class LennardScraper(BaseScraper):
    BROKERAGE_NAME = "Lennard Commercial Realty"
    BASE_URL = "https://www.lennard.com"

    def scrape(self) -> list[dict]:
        listings = []

        listing_urls = [
            f"{self.BASE_URL}/properties",
            f"{self.BASE_URL}/listings",
            f"{self.BASE_URL}/available-properties",
            f"{self.BASE_URL}/search",
            f"{self.BASE_URL}/properties/search",
        ]

        for url in listing_urls:
            try:
                soup = fetch_page(url, self.session)
                if soup:
                    page_listings = self._parse_page(soup, url)
                    if page_listings:
                        listings.extend(page_listings)
                        # Check for pagination
                        listings.extend(self._handle_pagination(soup, url))
                        break
                random_delay()
            except Exception as e:
                self.logger.warning(f"Lennard page {url} failed: {e}")

        # Try homepage for property links if nothing found
        if not listings:
            try:
                soup = fetch_page(self.BASE_URL, self.session)
                if soup:
                    links = soup.select(
                        "a[href*='propert'], a[href*='listing'], "
                        "a[href*='available'], a[href*='search']"
                    )
                    seen = set()
                    for link in links[:5]:
                        href = link.get("href", "")
                        if href and not href.startswith("http"):
                            href = f"{self.BASE_URL}{href}"
                        if href and href not in seen:
                            seen.add(href)
                            random_delay()
                            page_soup = fetch_page(href, self.session)
                            if page_soup:
                                listings.extend(self._parse_page(page_soup, href))
            except Exception as e:
                self.logger.error(f"Lennard homepage failed: {e}")

        return listings

    def _handle_pagination(self, soup, base_url: str) -> list[dict]:
        """Follow pagination links."""
        listings = []
        next_link = soup.select_one(
            "a.next, a[rel='next'], .pagination a:last-child, "
            ".next-page a, a[aria-label='Next']"
        )

        pages_followed = 0
        while next_link and pages_followed < 10:
            href = next_link.get("href", "")
            if not href:
                break
            if not href.startswith("http"):
                href = f"{self.BASE_URL}{href}"

            random_delay()
            soup = fetch_page(href, self.session)
            if not soup:
                break

            page_listings = self._parse_page(soup, href)
            if not page_listings:
                break

            listings.extend(page_listings)
            pages_followed += 1

            next_link = soup.select_one(
                "a.next, a[rel='next'], .pagination a:last-child, "
                ".next-page a, a[aria-label='Next']"
            )

        return listings

    def _parse_page(self, soup, page_url: str) -> list[dict]:
        listings = []

        cards = soup.select(
            ".property-card, .listing-card, .property-item, "
            ".listing-item, article.property, "
            ".properties-grid > div, .property-listing, "
            ".search-results .result, .property-box"
        )

        for card in cards:
            try:
                addr_el = card.select_one(
                    "h2, h3, h4, .property-title, .listing-title, "
                    ".address, .property-address"
                )
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address or len(address) < 5:
                    continue

                text = card.get_text(" ", strip=True)

                type_el = card.select_one(".property-type, .type, .category, .asset-type")
                price_el = card.select_one(".price, .property-price, .rent, .asking")
                size_el = card.select_one(".size, .sqft, .square-footage, .area")

                price_text = price_el.get_text(strip=True) if price_el else None
                size_text = size_el.get_text(strip=True) if size_el else None
                asset_type = type_el.get_text(strip=True) if type_el else None

                link_el = card.select_one("a[href]")
                link = ""
                if link_el:
                    link = link_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"{self.BASE_URL}{link}"

                # Extract broker from card
                broker_el = card.select_one(".broker, .agent, .contact-name")
                broker_name = broker_el.get_text(strip=True) if broker_el else None

                # Determine listing type
                lt = None
                if price_text:
                    lt = "Lease" if any(x in price_text.lower() for x in ["lease", "/sf", "psf", "net", "gross"]) else "Sale"
                elif "lease" in text.lower():
                    lt = "Lease"
                elif "sale" in text.lower():
                    lt = "Sale"

                # Detect city from text
                city = None
                city_el = card.select_one(".city, .location, .neighbourhood")
                if city_el:
                    city = city_el.get_text(strip=True)

                listing = self.make_listing(
                    address=address,
                    city=city or "Toronto",
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
                self.logger.warning(f"Failed to parse Lennard card: {e}")

        return listings


def scrape() -> list[dict]:
    return LennardScraper().scrape()
