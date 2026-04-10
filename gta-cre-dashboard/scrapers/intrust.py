"""InTrust CRE scraper.

InTrust CRE (intrustcre.com) is a Toronto-based commercial real estate brokerage.
Likely a smaller site with static or WordPress-based listing pages.
"""

import logging

from .base import BaseScraper, fetch_page, random_delay

logger = logging.getLogger(__name__)


class InTrustScraper(BaseScraper):
    BROKERAGE_NAME = "InTrust CRE"
    BASE_URL = "https://www.intrustcre.com"

    def scrape(self) -> list[dict]:
        listings = []

        listing_urls = [
            f"{self.BASE_URL}/properties",
            f"{self.BASE_URL}/listings",
            f"{self.BASE_URL}/available-properties",
            f"{self.BASE_URL}/our-listings",
            f"{self.BASE_URL}/search",
        ]

        for url in listing_urls:
            try:
                soup = fetch_page(url, self.session)
                if soup:
                    page_listings = self._parse_page(soup, url)
                    if page_listings:
                        listings.extend(page_listings)
                        break
                random_delay()
            except Exception as e:
                self.logger.warning(f"InTrust page {url} failed: {e}")

        if not listings:
            try:
                soup = fetch_page(self.BASE_URL, self.session)
                if soup:
                    nav_links = soup.select("nav a, .menu a, .nav a, header a")
                    for link in nav_links:
                        href = link.get("href", "")
                        text = link.get_text(strip=True).lower()
                        if any(kw in text for kw in ["propert", "listing", "available"]):
                            if href and not href.startswith("http"):
                                href = f"{self.BASE_URL}{href}"
                            if href:
                                random_delay()
                                page_soup = fetch_page(href, self.session)
                                if page_soup:
                                    listings.extend(self._parse_page(page_soup, href))
            except Exception as e:
                self.logger.error(f"InTrust homepage failed: {e}")

        return listings

    def _parse_page(self, soup, page_url: str) -> list[dict]:
        listings = []

        cards = soup.select(
            ".property-card, .listing-card, .property-item, "
            ".listing-item, article.property, article.listing, "
            ".properties-grid > div, .property-listing, "
            ".search-results .result, .property-box, .featured-property"
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

                if any(skip in address.lower() for skip in ["about", "contact", "team", "blog"]):
                    continue

                text = card.get_text(" ", strip=True)

                type_el = card.select_one(".property-type, .type, .category")
                price_el = card.select_one(".price, .property-price")
                size_el = card.select_one(".size, .sqft, .area")
                broker_el = card.select_one(".broker, .agent")

                price_text = price_el.get_text(strip=True) if price_el else None
                size_text = size_el.get_text(strip=True) if size_el else None
                asset_type = type_el.get_text(strip=True) if type_el else None
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
                elif "lease" in text.lower():
                    lt = "Lease"
                elif "sale" in text.lower():
                    lt = "Sale"

                listing = self.make_listing(
                    address=address,
                    city="Toronto",
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
                self.logger.warning(f"Failed to parse InTrust card: {e}")

        return listings


def scrape() -> list[dict]:
    return InTrustScraper().scrape()
