from scripts.ingest.dpreview_discovery import extract_lens_links


def test_extract_lens_links_returns_title_brand_url_triplets():
    html = open("tests/fixtures/dpreview/index_canon.html", "r", encoding="utf-8").read()
    rows = extract_lens_links(html, brand="Canon")
    assert rows
    assert set(rows[0].keys()) == {"brand", "title", "url"}
    assert rows[0]["brand"] == "Canon"
