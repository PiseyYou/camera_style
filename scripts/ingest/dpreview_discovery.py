from bs4 import BeautifulSoup
import requests
from typing import List, Dict


# DPReview lens index URLs by brand
BRAND_INDEX_URLS = {
    "Canon": "https://www.dpreview.com/products/lenses/canon",
    "Nikon": "https://www.dpreview.com/products/lenses/nikon",
    "Sony": "https://www.dpreview.com/products/lenses/sony",
}


def fetch_url_simple(url: str) -> str:
    """
    Simple URL fetch without playwright (for discovery pages).

    Args:
        url: URL to fetch

    Returns:
        HTML content as string
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_lens_links(html: str, brand: str) -> list[dict]:
    """
    Extract lens product links from HTML content.

    Args:
        html: HTML content of the index page
        brand: Brand name (Canon, Nikon, Sony)

    Returns:
        List of dicts with keys: brand, title, url
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for anchor in soup.select("a"):
        href = anchor.get("href")
        title = anchor.get_text(" ", strip=True)
        if href and title and "/products/lenses/" in href:
            # Ensure URL is absolute
            if not href.startswith("http"):
                href = f"https://www.dpreview.com{href}" if href.startswith("/") else href
            items.append({"brand": brand, "title": title, "url": href})
    return items


def discover_lenses_for_brand(brand: str, limit: int = 20) -> list[dict]:
    """
    Discover lens product pages for a specific brand by fetching the index page.

    Args:
        brand: Brand name (Canon, Nikon, Sony)
        limit: Maximum number of lenses to return

    Returns:
        List of lens metadata dicts
    """
    if brand not in BRAND_INDEX_URLS:
        raise ValueError(f"Unsupported brand: {brand}. Supported: {list(BRAND_INDEX_URLS.keys())}")

    url = BRAND_INDEX_URLS[brand]
    html = fetch_url_simple(url)
    links = extract_lens_links(html, brand)
    return links[:limit]
