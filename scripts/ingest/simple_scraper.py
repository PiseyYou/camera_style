#!/usr/bin/env python3
"""
Simple scraper without playwright - uses requests only.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from pathlib import Path
from datetime import datetime
import time
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.ingest.dpreview_parser import parse_lens_detail

# Brand index URLs
BRAND_URLS = {
    "Canon": "https://www.dpreview.com/products/lenses/canon",
    "Nikon": "https://www.dpreview.com/products/lenses/nikon",
    "Sony": "https://www.dpreview.com/products/lenses/sony",
}

def fetch_simple(url):
    """Simple HTTP fetch with requests."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def discover_lenses(brand, limit=50):
    """Discover lens URLs from brand index page."""
    print(f"\n🔍 Discovering {brand} lenses...")

    url = BRAND_URLS.get(brand)
    if not url:
        print(f"Unknown brand: {brand}")
        return []

    html = fetch_simple(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    lens_links = []

    # Find all product links
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/products/lenses/' in href and brand.lower() in href.lower():
            full_url = f"https://www.dpreview.com{href}" if href.startswith('/') else href
            title = link.get_text(strip=True)

            if full_url not in [l['url'] for l in lens_links]:
                lens_links.append({
                    'brand': brand,
                    'title': title,
                    'url': full_url
                })

                if len(lens_links) >= limit:
                    break

    print(f"  Found {len(lens_links)} lens URLs")
    return lens_links[:limit]

def scrape_lens(lens_info):
    """Scrape a single lens page."""
    url = lens_info['url']
    print(f"  Scraping: {lens_info['title']}")

    html = fetch_simple(url)
    if not html:
        return None

    try:
        lens_data = parse_lens_detail(html, url)
        return lens_data
    except Exception as e:
        print(f"    Error parsing: {e}")
        return None

def save_data(lenses, brand):
    """Save scraped data."""
    if not lenses:
        return

    # Save JSON
    json_dir = project_root / 'data' / 'parsed' / 'dpreview'
    json_dir.mkdir(parents=True, exist_ok=True)

    for lens in lenses:
        filename = lens['model_name'].lower().replace(' ', '-').replace('/', '-')
        json_path = json_dir / f"{brand.lower()}-{filename}.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(lens, f, ensure_ascii=False, indent=2)

    # Update CSV
    csv_path = json_dir / 'summary.csv'

    # Read existing data
    existing_lenses = []
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_lenses = list(reader)

    # Add new lenses (avoid duplicates)
    existing_urls = {l.get('source_url') for l in existing_lenses}
    for lens in lenses:
        if lens.get('source_url') not in existing_urls:
            existing_lenses.append(lens)

    # Write CSV
    if existing_lenses:
        fieldnames = existing_lenses[0].keys()
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_lenses)

    print(f"\n✓ Saved {len(lenses)} lenses")
    print(f"  Total in database: {len(existing_lenses)}")

def main():
    """Main scraping function."""
    import argparse

    parser = argparse.ArgumentParser(description='Simple lens scraper')
    parser.add_argument('--brand', required=True, choices=['Canon', 'Nikon', 'Sony'])
    parser.add_argument('--limit', type=int, default=30)

    args = parser.parse_args()

    print(f"=== Simple Lens Scraper ===")
    print(f"Brand: {args.brand}")
    print(f"Limit: {args.limit}")

    # Discover lenses
    lens_links = discover_lenses(args.brand, args.limit)

    if not lens_links:
        print("No lenses found!")
        return

    # Scrape each lens
    print(f"\n📥 Scraping {len(lens_links)} lenses...")
    scraped_lenses = []

    for i, lens_info in enumerate(lens_links, 1):
        print(f"\n[{i}/{len(lens_links)}]", end=" ")
        lens_data = scrape_lens(lens_info)

        if lens_data:
            scraped_lenses.append(lens_data)

        # Be polite - wait between requests
        if i < len(lens_links):
            time.sleep(2)

    # Save data
    save_data(scraped_lenses, args.brand)

    print(f"\n✅ Scraping complete!")
    print(f"   Successfully scraped: {len(scraped_lenses)}/{len(lens_links)}")

if __name__ == '__main__':
    main()
