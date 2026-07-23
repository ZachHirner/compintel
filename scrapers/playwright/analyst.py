"""
Scraper: Analyst websites — Gartner public pages for Playwright in the
software test automation category.

Full analyst reports are paywalled; we target publicly visible Gartner Peer
Insights vendor profiles and the Forrester blog for any Playwright mentions.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "playwright"

URLS = [
    # Gartner Peer Insights — Playwright vendor profile in Software Test Automation
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/microsoft/product/playwright",
    # Gartner Peer Insights — broader Software Test Automation market overview
    "https://www.gartner.com/reviews/market/software-test-automation",
    # Forrester blog — search for any Playwright or open-source test automation coverage
    "https://www.forrester.com/blogs/",
    # Playwright changelog / announcements — signals strategic direction
    "https://playwright.dev/docs/release-notes",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for Playwright")
    raw = scrape_multiple(URLS)

    output = {
        "source_type": "analyst_websites",
        "competitor": COMPETITOR,
        "pages": [{"url": url, "content": content} for url, content in raw.items()],
    }

    out_path = output_dir / "analyst_raw.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("[analyst] Saved to %s", out_path)
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(Path("data/playwright"))
