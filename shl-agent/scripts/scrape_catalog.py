"""First-party scraper for the SHL product catalog.

IMPORTANT: This sandbox environment cannot reach www.shl.com directly
(network egress is restricted to a small allowlist that doesn't include
it), so `data/catalog.json` in this repo was bootstrapped from a
community-scraped dataset (see APPROACH.md for full disclosure) rather
than run from this script. Please run this script yourself from a
machine with normal internet access before final submission, diff the
output against data/catalog.json, and use whichever you trust more -
ideally this one, since it hits the live site directly.

Usage:
    pip install requests beautifulsoup4
    python scripts/scrape_catalog.py > data/catalog_fresh.json

The SHL catalog page paginates via `start=N` and separates the two
top-level categories via `type=1` (Individual Test Solutions) vs
`type=2` (Pre-packaged Job Solutions) query params. Each row in the
results table carries a `data-entity-id` attribute plus columns for
Remote Testing / Adaptive-IRT support (shown as filled/empty circle
icons) and one-or-more Test Type badge letters (A/B/C/D/E/K/P/S).

The selectors below are based on the page structure as documented by
several public scrapers of this same catalog; please verify them
against the live DOM (they can drift if SHL changes their markup) and
adjust before relying on this for scoring.
"""
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://www.shl.com/solutions/products/product-catalog/"
PAGE_SIZE = 12  # observed pagination step size
TYPE_INDIVIDUAL = 1  # "Individual Test Solutions" tab


def fetch_page(start: int, session: requests.Session) -> BeautifulSoup:
    params = {
        "start": start,
        "type": TYPE_INDIVIDUAL,
    }
    resp = session.get(BASE, params=params, timeout=20, headers={
        "User-Agent": "Mozilla/5.0 (compatible; SHLCatalogResearchBot/1.0)"
    })
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_rows(soup: BeautifulSoup):
    rows = soup.select("[data-entity-id]")
    for row in rows:
        entity_id = row.get("data-entity-id")
        link = row.select_one("a[href*='/product-catalog/view/']")
        if not link:
            continue
        name = link.get_text(strip=True)
        url = link.get("href")
        if url and url.startswith("/"):
            url = "https://www.shl.com" + url

        # Remote Testing / Adaptive-IRT are typically rendered as a filled
        # vs. outline circle icon in a specific column - adjust the
        # selector below to match what you see in the live DOM.
        remote = bool(row.select_one(".catalogue__circle.-yes, .remote-testing.yes"))
        adaptive = bool(row.select_one(".catalogue__circle.-yes ~ .catalogue__circle.-yes, .adaptive.yes"))

        type_badges = [b.get_text(strip=True) for b in row.select(".product-catalogue__key, .test-type-badge")]
        test_type = type_badges[0] if type_badges else None

        duration_text = row.get_text(" ", strip=True)
        m = re.search(r"(\d+)\s*min", duration_text)
        duration = int(m.group(1)) if m else None

        yield {
            "id": entity_id,
            "name": name,
            "url": url,
            "remote_testing": remote,
            "adaptive_irt": adaptive,
            "test_type": test_type,
            "duration_minutes": duration,
        }


def scrape_all():
    session = requests.Session()
    start = 0
    seen_ids = set()
    results = []
    while True:
        soup = fetch_page(start, session)
        page_rows = list(parse_rows(soup))
        new_rows = [r for r in page_rows if r["id"] not in seen_ids]
        if not new_rows:
            break
        for r in new_rows:
            seen_ids.add(r["id"])
            results.append(r)
        start += PAGE_SIZE
        time.sleep(0.5)  # be polite
        if start > 2000:  # safety valve against infinite loop
            break
    return results


if __name__ == "__main__":
    data = scrape_all()
    json.dump(data, sys.stdout, indent=2)
    print(f"\nScraped {len(data)} items", file=sys.stderr)
