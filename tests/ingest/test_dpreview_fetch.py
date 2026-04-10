from scripts.ingest.dpreview_fetch import choose_fetch_mode


def test_choose_fetch_mode_falls_back_to_browser_after_403():
    assert choose_fetch_mode(status_code=403) == "browser"
    assert choose_fetch_mode(status_code=200) == "http"
