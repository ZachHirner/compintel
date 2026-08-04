"""
Shared browser driver and scraping utilities for all CI scrapers.
Uses Selenium with stealth patches to avoid bot detection.
"""
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

logger = logging.getLogger(__name__)

_DEFAULT_WAIT = 6
_DEFAULT_CHAR_LIMIT = 50_000

# Minimum characters of visible body text before we consider the page usefully loaded.
# Pages that only render a banner/overlay/cookie wall tend to stay below this.
_MIN_CONTENT_CHARS = 500


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver


def _wait_for_content(driver: webdriver.Chrome, timeout: int = 20) -> None:
    """
    Wait until the page body contains at least _MIN_CONTENT_CHARS of visible text.
    This catches JS-heavy pages where readyState fires before the main content
    hydrates — e.g. countdown banners or overlays that render first and block
    the rest of the page from appearing until their JS bundle finishes.
    Falls back gracefully after timeout rather than raising.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(
                BeautifulSoup(d.page_source, "html.parser")
                .get_text(separator=" ", strip=True)
            ) >= _MIN_CONTENT_CHARS
        )
    except Exception:
        # Page didn't reach threshold — proceed anyway and capture what's there
        logger.debug("Content threshold not reached within %ds — proceeding", timeout)


def _load_and_scroll(driver: webdriver.Chrome, url: str, wait: int) -> None:
    """Load url, wait for meaningful content to appear, then scroll to trigger lazy-loaded content."""
    driver.get(url)
    # Phase 1: wait for DOM ready
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    # Phase 2: wait for actual content to hydrate (handles JS overlays / countdown banners)
    _wait_for_content(driver)
    time.sleep(wait)
    # Phase 3: scroll incrementally to trigger lazy-load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


def _extract_text(driver: webdriver.Chrome, char_limit: int) -> str:
    """Extract main content text from the current page, stripping nav/layout noise."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()
    # Prefer semantic content containers; fall back to full body
    content = soup.find("main") or soup.find("article") or soup.find("body") or soup
    text = content.get_text(separator="\n", strip=True)
    return text[:char_limit]


def scrape_site(url: str, wait: int = _DEFAULT_WAIT, char_limit: int = _DEFAULT_CHAR_LIMIT) -> str:
    """
    Load *url* in a Chrome instance with stealth patches applied,
    wait for JS to render, strip scripts/styles, and return plain text.
    """
    driver = _build_driver()
    try:
        logger.info("Fetching %s", url)
        _load_and_scroll(driver, url, wait)
        return _extract_text(driver, char_limit)
    finally:
        driver.quit()


def scrape_multiple(urls: list[str], wait: int = _DEFAULT_WAIT, char_limit: int = _DEFAULT_CHAR_LIMIT) -> dict[str, str]:
    """
    Scrape a list of URLs, reusing a single driver session.
    Returns {url: text_content}.
    """
    driver = _build_driver()
    results: dict[str, str] = {}
    try:
        for url in urls:
            try:
                logger.info("Fetching %s", url)
                _load_and_scroll(driver, url, wait)
                results[url] = _extract_text(driver, char_limit)
            except Exception as exc:
                logger.warning("Failed to scrape %s: %s", url, exc)
                results[url] = f"ERROR: {exc}"
    finally:
        driver.quit()
    return results
