"""
Shared browser driver and scraping utilities for all CI scrapers.
Uses Selenium with stealth patches to avoid bot detection.
RSS feeds are fetched directly without a browser.
"""
import time
import logging
import urllib.request
from xml.etree import ElementTree
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


def fetch_rss(url: str, max_items: int = 10) -> str:
    """
    Fetch a YouTube RSS feed and return a plain-text summary of the latest videos.
    Returns title, published date, and description for each entry — no browser needed.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml = resp.read()
        root = ElementTree.fromstring(xml)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "media": "http://search.yahoo.com/mrss/",
            "yt": "http://www.youtube.com/xml/schemas/2015",
        }
        entries = root.findall("atom:entry", ns)[:max_items]
        lines = []
        for entry in entries:
            title = entry.findtext("atom:title", default="", namespaces=ns)
            published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
            description = ""
            group = entry.find("media:group", ns)
            if group is not None:
                desc_el = group.find("media:description", ns)
                if desc_el is not None and desc_el.text:
                    description = desc_el.text[:300].replace("\n", " ")
            link_el = entry.find("atom:link", ns)
            link = link_el.get("href", "") if link_el is not None else ""
            lines.append(f"[{published}] {title}\n{description}\n{link}")
        return "\n\n".join(lines) if lines else "No videos found."
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", url, exc)
        return f"ERROR: {exc}"


def scrape_multiple_with_rss(
    urls: list[str],
    rss_urls: list[str] | None = None,
    wait: int = _DEFAULT_WAIT,
    char_limit: int = _DEFAULT_CHAR_LIMIT,
) -> dict[str, str]:
    """
    Scrape regular URLs via Selenium and fetch RSS URLs directly.
    Returns {url: text_content} for all URLs combined.
    """
    results: dict[str, str] = {}
    if rss_urls:
        for url in rss_urls:
            logger.info("Fetching RSS %s", url)
            results[url] = fetch_rss(url)
    if urls:
        browser_results = scrape_multiple(urls, wait=wait, char_limit=char_limit)
        results.update(browser_results)
    return results


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
