"""
B&H Photo scraper for lens data.
"""

import re
from bs4 import BeautifulSoup
from scripts.ingest.base_scraper import BaseScraper, LensData
from scripts.ingest.dpreview_fetch import fetch_url


BRAND_URLS = {
    "Canon": "https://www.bhphotovideo.com/c/browse/Lenses/ci/15492/N/4288584247",
    "Nikon": "https://www.bhphotovideo.com/c/browse/Lenses/ci/15492/N/4288584248",
    "Sony": "https://www.bhphotovideo.com/c/browse/Lenses/ci/15492/N/4288584249",
}


class BHPhotoScraper(BaseScraper):
    """Scraper for B&H Photo website."""

    def __init__(self):
        super().__init__("bhphoto")

    def discover_lenses(self, brand: str, limit: int = 20) -> list[dict]:
        """Discover lens products from B&H Photo."""
        if brand not in BRAND_URLS:
            raise ValueError(f"Unsupported brand: {brand}")

        url = BRAND_URLS[brand]
        result = fetch_url(url, mode="browser", delay=3)

        if result["status_code"] != 200:
            raise RuntimeError(f"Failed to fetch {url}: {result['status_code']}")

        soup = BeautifulSoup(result["html"], "html.parser")
        items = []

        # B&H uses data-selenium attributes for product links
        for product in soup.select('[data-selenium="miniProductPage"]')[:limit]:
            link = product.select_one('a[data-selenium="miniProductPageProductNameLink"]')
            if not link:
                continue

            href = link.get('href', '')
            title = link.get_text(strip=True)

            if href and title:
                full_url = f"https://www.bhphotovideo.com{href}" if href.startswith('/') else href
                items.append({
                    'brand': brand,
                    'title': title,
                    'url': full_url
                })

        return items

    def fetch_page(self, url: str) -> str:
        """Fetch page HTML using Playwright."""
        result = fetch_url(url, mode="browser", delay=3)
        if result["status_code"] != 200:
            raise RuntimeError(f"Failed to fetch {url}")
        return result["html"]

    def parse_lens_detail(self, html: str) -> LensData:
        """Parse lens details from B&H Photo page."""
        soup = BeautifulSoup(html, "html.parser")

        # Initialize with empty data
        data = LensData(
            brand="",
            model_name="",
            source="bhphoto",
            source_url=""
        )

        # Extract title
        title_elem = soup.select_one('h1[data-selenium="productTitle"]')
        if title_elem:
            full_title = title_elem.get_text(strip=True)
            data.model_name = full_title

            # Extract brand from title
            for brand in ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus"]:
                if brand.lower() in full_title.lower():
                    data.brand = brand
                    break

        # Extract price
        price_elem = soup.select_one('[data-selenium="uppedDecimalPriceFirst"]')
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace(',', '').replace('$', '')
            try:
                data.current_price = float(price_text)
                data.currency = "USD"
            except ValueError:
                pass

        # Extract specifications from the specs table
        spec_rows = soup.select('.specs_table tr')
        for row in spec_rows:
            label_elem = row.select_one('td:first-child')
            value_elem = row.select_one('td:last-child')

            if not label_elem or not value_elem:
                continue

            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)

            # Parse different spec types
            if 'mount' in label or 'lens mount' in label:
                data.mount = value

            elif 'focal length' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    if len(numbers) == 1:
                        data.focal_length_min = float(numbers[0])
                        data.focal_length_max = float(numbers[0])
                        data.prime_or_zoom = "Prime"
                    else:
                        data.focal_length_min = float(numbers[0])
                        data.focal_length_max = float(numbers[1])
                        data.prime_or_zoom = "Zoom"

            elif 'maximum aperture' in label or 'max aperture' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    data.max_aperture_wide = float(numbers[0])
                    if len(numbers) > 1:
                        data.max_aperture_tele = float(numbers[1])
                    else:
                        data.max_aperture_tele = data.max_aperture_wide

            elif 'minimum aperture' in label or 'min aperture' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    data.min_aperture = float(numbers[0])

            elif 'weight' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    weight = float(numbers[0])
                    # Convert to grams if in pounds/ounces
                    if 'lb' in value.lower() or 'pound' in value.lower():
                        weight = weight * 453.592
                    elif 'oz' in value.lower() and 'ounce' in value.lower():
                        weight = weight * 28.3495
                    data.weight = weight

            elif 'diameter' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    data.diameter = float(numbers[0])

            elif 'length' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    data.length = float(numbers[0])

            elif 'filter' in label and 'thread' in label:
                numbers = re.findall(r'\d+', value)
                if numbers:
                    data.filter_thread = float(numbers[0])

            elif 'minimum focus' in label or 'close focus' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    distance = float(numbers[0])
                    # Convert to meters if in feet/inches
                    if 'ft' in value.lower() or 'feet' in value.lower():
                        distance = distance * 0.3048
                    elif 'in' in value.lower() and 'inch' in value.lower():
                        distance = distance * 0.0254
                    data.min_focus_distance = distance

            elif 'magnification' in label:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    data.max_magnification = float(numbers[0])

            elif 'image stabilization' in label or 'vibration reduction' in label:
                data.image_stabilization = 'yes' in value.lower()

            elif 'autofocus' in label or 'af' in label:
                data.autofocus = 'yes' in value.lower() or 'af' in value.lower()

            elif 'weather' in label and 'seal' in label:
                data.weather_sealing = 'yes' in value.lower()

        return data


def main():
    """Test the B&H Photo scraper."""
    scraper = BHPhotoScraper()

    print("Testing B&H Photo scraper...")
    print("Discovering Canon lenses...")

    try:
        lenses = scraper.discover_lenses("Canon", limit=3)
        print(f"Found {len(lenses)} lenses")

        if lenses:
            print(f"\nScraping first lens: {lenses[0]['title']}")
            lens_data = scraper.scrape_lens(
                url=lenses[0]['url'],
                title=lenses[0]['title'],
                brand=lenses[0]['brand']
            )
            print(f"Model: {lens_data.model_name}")
            print(f"Price: ${lens_data.current_price}")
            print(f"Mount: {lens_data.mount}")
            print(f"Focal Length: {lens_data.focal_length_min}-{lens_data.focal_length_max}mm")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
