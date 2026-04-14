import time
from playwright.sync_api import sync_playwright, Page, Browser


def choose_fetch_mode(status_code: int) -> str:
    return "browser" if status_code == 403 else "http"


def fetch_with_playwright(url: str, wait_seconds: int = 3) -> str:
    """
    Fetch webpage content using Playwright with browser automation.
    This bypasses 403 errors by simulating a real browser.

    Args:
        url: The URL to fetch
        wait_seconds: Seconds to wait for page to load

    Returns:
        HTML content as string
    """
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page: Page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(wait_seconds)
            html = page.content()
            return html
        finally:
            context.close()
            browser.close()


def fetch_url(url: str, mode: str = "browser", delay: int = 3) -> dict:
    """
    Fetch URL with specified mode.

    Args:
        url: URL to fetch
        mode: "browser" (Playwright) or "http" (requests)
        delay: Delay in seconds between requests

    Returns:
        dict with keys: html (str), status_code (int), mode (str)
    """
    if mode == "browser":
        try:
            html = fetch_with_playwright(url, wait_seconds=delay)
            return {"html": html, "status_code": 200, "mode": "browser"}
        except Exception as e:
            return {"html": "", "status_code": 500, "mode": "browser", "error": str(e)}
    else:
        # HTTP mode not implemented yet, always use browser
        return fetch_url(url, mode="browser", delay=delay)
