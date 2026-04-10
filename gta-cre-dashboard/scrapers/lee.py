"""Lee & Associates Toronto scraper.

Lee & Associates Toronto (leetoronto.com) - smaller regional brokerage.
Likely a simpler WordPress or static site with listing pages.
"""

import logging

from .base import BaseScraper, fetch_page, random_delay

logger = logging.getLogger(__name__)


class LeeScraper(BaseScraper):
    BROKERAGE_NAME = "Lee & Associates"
    BASE_URL = "https://www.leetoronto.com"

    def scrape(self) -> list[dict]:
        listings = []

        # Try common listing page URLs
        listing_urls = [
            f"{self.BASE_URL}/properties",
            f"{self.BASE_URL}/listings",
            f"{self.BASE_URL}/available-properties",
            f"{self.BASE_URL}/properties-for-lease",
            f"{self.BASE_URL}/properties-for-sale",
        ]

        for url in listing_urls:
            try:
                soup = fetch_page(url, self.session)
                if soup:
                    page_listings = self._parse_listings_page(soup, url)
                    if page_listings:
                        listings.extend(page_listings)
                        break  # Found the right URL
                random_delay()
            except Exception as e:
                self.logger.warning(f"Lee page {url} failed: {e}")
                continue

        # If no listings found from standard URLs, try scraping the homepage
        if not listings:
            try:
                soup = fetch_page(self.BASE_URL, self.session)
                if soup:
                    # Look for links to property pages
                    property_links = soup.select(
                        "a[href*='propert'], a[href*='listing'], "
                        "a[href*='available'], a[href*='lease'], a[href*='sale']"
                    )
                    for link in property_links[:5]:
                        href = link.get("href", "")
                        if href and not href.startswith("http"):
                            href = f"{self.BASE_URL}{href}"
                        if href:
                            random_delay()
                            page_soup = fetch_page(href, self.session)
                            if page_soup:
                                page_listings = self._parse_listings_page(page_soup, href)
                                listings.extend(page_listings)
            except Exception as e:
                self.logger.error(f"Lee homepage scrape failed: {e}")

        return listings

    def _parse_listings_page(self, soup, page_url: str) -> list[dict]:
        listings = []

        # Try common listing card selectors
        cards = soup.select(
            ".property-card, .listing-card, .property-item, "
            ".listing-item, .property, .listing, "
            "article.property, article.listing, "
            ".properties-list > div, .listings-grid > div, "
            ".entry-content .property, .wp-block-property"
        )

        # If no cards found, try looking for a table
        if not cards:
            rows = soup.select("table tr, .property-table tr")
            for row in rows[1:]:  # Skip header
                cells = row.select("td")
                if len(cells) >= 3:
                    try:
                        address = cells[0].get_text(strip=True)
                        if not address:
                            continue

                        listing = self.make_listing(
                            address=address,
                            city="Toronto",
                            asset_type=cells[1].get_text(strip=True) if len(cells) > 1 else None,
                            listing_type=cells[2].get_text(strip=True) if len(cells) > 2 else None,
                            asking_price=cells[3].get_text(strip=True) if len(cells) > 3 else None,
                            square_footage=cells[4].get_text(strip=True) if len(cells) > 4 else None,
                            listing_url=page_url,
                        )
                        listings.append(listing)
                    except Exception:
                        continue

        for card in cards:
            try:
                addr_el = card.select_one(
                    "h2, h3, h4, .property-title, .listing-title, .address, "
                    ".property-address, a"
                )
                address = addr_el.get_text(strip=True) if addr_el else ""
                if not address or len(address) < 5:
                    continue

                # Extract details
                text = card.get_text(" ", strip=True)

                type_el = card.select_one(".property-type, .type, .category")
                asset_type = type_el.get_text(strip=True) if type_el else None

                price_el = card.select_one(".price, .property-price, .asking-price")
                price_text = price_el.get_text(strip=True) if price_el else None

                size_el = card.select_one(".size, .sqft, .square-footage, .area")
                size_text = size_el.get_text(strip=True) if size_el else None

                link_el = card.select_one("a[href]")
                link = ""
                if link_el:
                    link = link_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"{self.BASE_URL}{link}"

                # Determine listing type from context
                lt = None
                if price_text:
                    lt = "Lease" if any(x in price_text.lower() for x in ["lease", "/sf", "psf", "net", "gross"]) else "Sale"
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
                    listing_url=link or page_url,
                )
                listings.append(listing)

            except Exception as e:
                self.logger.warning(f"Failed to parse Lee card: {e}")

        return listings


def scrape() -> list[dict]:
    return LeeScraper().scrape()
