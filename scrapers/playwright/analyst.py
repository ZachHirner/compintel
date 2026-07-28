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
    # Forrester search — Playwright mentions, last 30 days, reports tab
    "https://www.forrester.com/allSearch?query=Playwright&activeTab=Reports&publishedSinceInDays=30",
    # Playwright release notes — cadence and strategic direction signals
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
