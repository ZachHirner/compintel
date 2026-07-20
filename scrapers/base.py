"""
Shared browser driver and scraping utilities for all CI scrapers.
"""
import time
import logging
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

_DEFAULT_WAIT = 6
_DEFAULT_CHAR_LIMIT = 25_000


def _build_driver() -> uc.Chrome:
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # version_main must match the Chrome binary on the runner (currently 150)
    return uc.Chrome(options=options, use_subprocess=True, version_main=150)


def scrape_site(url: str, wait: int = _DEFAULT_WAIT, char_limit: int = _DEFAULT_CHAR_LIMIT) -> str:
    """
    Load *url* in a headless Chrome instance, wait for JS to render,
    strip scripts/styles, and return plain text up to *char_limit* chars.
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
