"""
Shared browser driver and scraping utilities for all CI scrapers.
Uses Selenium with stealth patches to avoid bot detection.
"""
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

logger = logging.getLogger(__name__)

_DEFAULT_WAIT = 6
_DEFAULT_CHAR_LIMIT = 25_000


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


def scrape_site(url: str, wait: int = _DEFAULT_WAIT, char_limit: int = _DEFAULT_CHAR_LIMIT) -> str:
    """
    Load *url* in a Chrome instance with stealth patches applied,
    wait for JS to render, strip scripts/styles, and return plain text.
    """
    driver = _build_driver()
    try:
        logger.info("Fetching %s", url)
        driver.get(url)
        time.sleep(wait)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:char_limit]
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
                driver.get(url)
                time.sleep(wait)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                for tag in soup(["script", "style", "noscript", "svg"]):
                    tag.decompose()

                text = soup.get_text(separator="\n", strip=True)
                results[url] = text[:char_limit]
            except Exception as exc:
                logger.warning("Failed to scrape %s: %s", url, exc)
                results[url] = f"ERROR: {exc}"
    finally:
        driver.quit()
    return results
