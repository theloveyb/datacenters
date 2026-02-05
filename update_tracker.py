#!/usr/bin/env python3
"""
Ontario & Toronto AI Data Center Tracker — Auto-Updater
========================================================

Searches for new Ontario/Toronto data-center developments and
updates both tracker_data.json and the embedded data in tracker.html.

Usage:
    python update_tracker.py                  # search + update
    python update_tracker.py --rebuild-html   # just re-embed JSON into HTML

Requires: pip install requests beautifulsoup4
(Optional: set GOOGLE_API_KEY and GOOGLE_CSE_ID env vars for Google search,
 otherwise falls back to scraping Google News RSS.)
"""

import argparse
import datetime
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
import ssl
import time
from html.parser import HTMLParser

# ── paths ───────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH    = os.path.join(SCRIPT_DIR, "tracker_data.json")
HTML_PATH    = os.path.join(SCRIPT_DIR, "tracker.html")

# ── search config ───────────────────────────────────────────────────────
SEARCH_QUERIES = [
    "Ontario data center new project announcement",
    "Toronto data center investment megawatt",
    "Ontario Bill 40 data centre grid connection regulation",
    "IESO Ontario electricity data center demand",
    "Ontario data centre legislation policy 2025 2026",
    "Toronto hyperscale data center construction",
    "Canada AI data center Ontario investment",
]

CATEGORY_KEYWORDS = {
    "legislation": [
        "bill", "legislation", "regulation", "regulatory", "act", "law",
        "policy", "government", "minister", "consultation", "royal assent",
        "zoning", "bylaw", "approval process", "environmental registry",
    ],
    "investment": [
        "investment", "invest", "billion", "million", "funding", "capital",
        "financing", "budget", "commit", "pledge", "acquisition",
    ],
    "project": [
        "data center", "data centre", "groundbreaking", "construction",
        "facility", "campus", "operational", "megawatt", "mw", "build",
        "launch", "expansion", "phase", "broke ground",
    ],
    "grid": [
        "grid", "electricity", "power", "ieso", "hydro", "energy",
        "reliability", "capacity", "generation", "transmission",
        "peak demand", "twh",
    ],
    "market": [
        "market", "report", "analysis", "forecast", "outlook",
        "vacancy", "pipeline", "cbre", "mordor", "research",
    ],
}

# ── HTML text extraction ────────────────────────────────────────────────
class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        return " ".join(self._parts)


def html_to_text(html_str):
    p = _TextExtractor()
    p.feed(html_str)
    return p.get_text()


# ── web helpers ─────────────────────────────────────────────────────────
def _urlopen(url, timeout=15):
    """Fetch a URL with a permissive SSL context."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DataCenterTracker/1.0)"
    })
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def google_news_rss(query, num=10):
    """Search Google News RSS for articles matching `query`."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-CA&gl=CA&ceid=CA:en"
    results = []
    try:
        resp = _urlopen(url)
        body = resp.read().decode("utf-8", errors="replace")
        # Quick XML parse — pull <item> blocks
        items = re.findall(r"<item>(.*?)</item>", body, re.DOTALL)
        for item in items[:num]:
            title = re.search(r"<title>(.*?)</title>", item)
            link  = re.search(r"<link/>\s*(https?://\S+)", item)
            if not link:
                link = re.search(r"<link>(.*?)</link>", item)
            pub   = re.search(r"<pubDate>(.*?)</pubDate>", item)
            desc  = re.search(r"<description>(.*?)</description>", item, re.DOTALL)
            if title and link:
                results.append({
                    "title": html_to_text(title.group(1)).strip(),
                    "url":   link.group(1).strip(),
                    "date":  pub.group(1).strip() if pub else "",
                    "snippet": html_to_text(desc.group(1)).strip() if desc else "",
                })
    except Exception as e:
        print(f"  [warn] RSS search failed for '{query}': {e}")
    return results


def fetch_article_text(url, max_chars=3000):
    """Best-effort fetch and extract text from a URL."""
    try:
        resp = _urlopen(url, timeout=10)
        raw = resp.read()
        text = raw.decode("utf-8", errors="replace")
        plain = html_to_text(text)
        # Collapse whitespace
        plain = re.sub(r"\s+", " ", plain).strip()
        return plain[:max_chars]
    except Exception:
        return ""


# ── classification ──────────────────────────────────────────────────────
def classify_category(title, snippet):
    """Classify an article into a tracker category."""
    combined = (title + " " + snippet).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        scores[cat] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "market"
    return best


def classify_impact(title, snippet):
    """Heuristic impact classification."""
    combined = (title + " " + snippet).lower()
    high_signals = [
        "billion", "royal assent", "law", "legislation", "regulation",
        "hyperscale", "multi-billion", "record", "landmark",
        "ieso", "grid connection", "6500", "6,500",
    ]
    low_signals = [
        "minor", "small", "boutique", "update",
    ]
    if any(s in combined for s in high_signals):
        return "high"
    if any(s in combined for s in low_signals):
        return "low"
    return "medium"


def parse_date(date_str):
    """Try to parse a date string into YYYY-MM-DD."""
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %Z",  # RSS format
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
    ]:
        try:
            dt = datetime.datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.date.today().isoformat()


def extract_entities(title, snippet):
    """Extract likely entity names from text."""
    known = [
        "Microsoft", "Google", "Google Cloud", "Amazon", "AWS",
        "Amazon Web Services", "Meta", "Oracle", "QScale", "Yondr",
        "STACK Infrastructure", "Cologix", "Equinix", "Digital Realty",
        "CPP Investments", "Cohere", "Bell Canada", "Hydro One",
        "Toronto Hydro", "IESO", "Ontario Government",
        "Government of Canada", "Torys LLP", "Brookfield",
    ]
    combined = title + " " + snippet
    found = [e for e in known if e.lower() in combined.lower()]
    return found


def extract_location(title, snippet):
    """Extract Ontario/Toronto location from text."""
    combined = (title + " " + snippet).lower()
    locations = [
        ("Greater Toronto Area", ["greater toronto", "gta"]),
        ("Toronto", ["toronto"]),
        ("Markham, Ontario", ["markham"]),
        ("Cambridge, Ontario", ["cambridge, on", "cambridge, ontario"]),
        ("Mississauga, Ontario", ["mississauga"]),
        ("Ontario", ["ontario"]),
        ("Canada-wide", ["canada", "canadian"]),
    ]
    for name, keywords in locations:
        if any(kw in combined for kw in keywords):
            return name
    return "Ontario"


def extract_mw(text):
    """Try to extract a MW capacity figure."""
    m = re.search(r"(\d[\d,]*)\s*(?:MW|megawatt)", text, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


def extract_investment(text):
    """Try to extract a C$ investment figure."""
    # Match patterns like C$19B, $7.5 billion, C$225M, $225 million
    m = re.search(
        r"[C$]*\$\s*([\d.]+)\s*(billion|million|B|M)\b",
        text, re.IGNORECASE,
    )
    if m:
        num = float(m.group(1))
        unit = m.group(2).lower()
        if unit in ("billion", "b"):
            return int(num * 1_000_000_000)
        elif unit in ("million", "m"):
            return int(num * 1_000_000)
    return None


# ── core logic ──────────────────────────────────────────────────────────
def load_existing():
    """Load existing tracker entries."""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(entries):
    """Save entries to tracker_data.json."""
    entries.sort(key=lambda e: e["date"], reverse=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(entries)} entries to {DATA_PATH}")


def rebuild_html(entries):
    """Re-embed the entry data into tracker.html."""
    if not os.path.exists(HTML_PATH):
        print(f"[error] {HTML_PATH} not found — skipping HTML rebuild.")
        return False

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Find the EMBEDDED_DATA block and replace it
    pattern = r"(let EMBEDDED_DATA = )\[.*?\];$"
    json_str = json.dumps(entries, indent=2, ensure_ascii=False)
    replacement = r"\g<1>" + json_str + ";"

    new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL | re.MULTILINE)
    if count == 0:
        print("[error] Could not find EMBEDDED_DATA block in tracker.html")
        return False

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"Rebuilt {HTML_PATH} with {len(entries)} embedded entries.")
    return True


def is_duplicate(existing, title, url):
    """Check if an article is already in the tracker."""
    title_lower = title.lower().strip()
    for entry in existing:
        # URL match
        if entry.get("source_url", "").rstrip("/") == url.rstrip("/"):
            return True
        # Fuzzy title match: >60% word overlap
        existing_words = set(entry["title"].lower().split())
        new_words = set(title_lower.split())
        if len(existing_words) > 0 and len(new_words) > 0:
            overlap = len(existing_words & new_words) / max(len(existing_words), len(new_words))
            if overlap > 0.6:
                return True
    return False


def is_relevant(title, snippet):
    """Check if an article is relevant to Ontario/Toronto data centers."""
    combined = (title + " " + snippet).lower()
    # Must mention data cent(er/re)
    has_dc = ("data cent" in combined or "datacent" in combined
              or "hyperscale" in combined or "data hall" in combined)
    # Must mention Ontario/Toronto/Canada
    has_location = any(loc in combined for loc in [
        "ontario", "toronto", "markham", "mississauga", "cambridge",
        "gta", "greater toronto", "canada", "canadian",
    ])
    return has_dc and has_location


def search_new_articles():
    """Search for new data-center articles and return candidates."""
    all_results = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        print(f"  Searching: {query}")
        results = google_news_rss(query, num=8)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)
        time.sleep(1)  # polite delay

    print(f"  Found {len(all_results)} total articles across {len(SEARCH_QUERIES)} queries.")
    return all_results


def process_articles(raw_articles, existing):
    """Filter, classify, and format new articles into tracker entries."""
    next_id = max(
        (int(e["id"].split("-")[1]) for e in existing if e["id"].startswith("ev-")),
        default=0,
    ) + 1

    new_entries = []

    for article in raw_articles:
        title = article["title"]
        url = article["url"]
        snippet = article.get("snippet", "")

        # Skip duplicates
        if is_duplicate(existing + new_entries, title, url):
            continue

        # Skip irrelevant
        if not is_relevant(title, snippet):
            continue

        # Optionally fetch more context
        body_text = ""
        if len(snippet) < 100:
            body_text = fetch_article_text(url)
            if body_text:
                snippet = body_text[:500]

        full_text = title + " " + snippet

        entry = {
            "id": f"ev-{next_id:03d}",
            "date": parse_date(article.get("date", "")),
            "category": classify_category(title, snippet),
            "subcategory": "news",
            "title": title,
            "summary": snippet[:400].strip(),
            "entities": extract_entities(title, snippet),
            "location": extract_location(title, snippet),
            "capacity_mw": extract_mw(full_text),
            "investment_cad": extract_investment(full_text),
            "source_url": url,
            "source_name": urllib.parse.urlparse(url).netloc.replace("www.", ""),
            "impact": classify_impact(title, snippet),
        }

        new_entries.append(entry)
        next_id += 1
        print(f"  + [{entry['category']}] {title[:80]}")

    return new_entries


# ── main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Update the Ontario AI Data Center Tracker"
    )
    parser.add_argument(
        "--rebuild-html", action="store_true",
        help="Only rebuild the HTML from existing tracker_data.json (no search)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Search and show candidates but don't write files",
    )
    args = parser.parse_args()

    existing = load_existing()
    print(f"Loaded {len(existing)} existing entries.")

    if args.rebuild_html:
        existing.sort(key=lambda e: e["date"], reverse=True)
        rebuild_html(existing)
        return

    print("Searching for new articles...")
    raw = search_new_articles()

    new_entries = process_articles(raw, existing)
    print(f"\nFound {len(new_entries)} new entries.")

    if not new_entries:
        print("Nothing new to add.")
        # Still rebuild HTML in case JSON was updated manually
        rebuild_html(existing)
        return

    if args.dry_run:
        print("\n[dry-run] Would add:")
        for e in new_entries:
            print(f"  {e['date']} [{e['category']}] {e['title'][:70]}")
        return

    # Merge and save
    all_entries = existing + new_entries
    save_data(all_entries)
    rebuild_html(all_entries)
    print(f"\nDone. Total entries: {len(all_entries)}")


if __name__ == "__main__":
    main()
