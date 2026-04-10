from bs4 import BeautifulSoup


def extract_lens_links(html: str, brand: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for anchor in soup.select("a"):
        href = anchor.get("href")
        title = anchor.get_text(" ", strip=True)
        if href and title and "/products/lenses/" in href:
            items.append({"brand": brand, "title": title, "url": href})
    return items
