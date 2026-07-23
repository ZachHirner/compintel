"""
Scraper: Competitor website — Playwright (Microsoft) product & docs pages.

Targets the official Playwright website, docs, and feature pages to capture
positioning, supported languages, and integration messaging.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "playwright"

URLS = [
    # Homepage — headline positioning and key value props
    "https://playwright.dev/",
    # Docs landing — feature overview and supported languages
    "https://playwright.dev/docs/intro",
    # Feature highlights: auto-waits, traces, parallel execution
    "https://playwright.dev/docs/test-runners",
    # Supported browsers and platforms
    "https://playwright.dev/docs/browsers",
    # GitHub releases page — cadence and recent changes
    "https://github.com/microsoft/playwright/releases",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting Playwright product page scrape")
    raw = scrape_multiple(URLS)

    output = {
        "source_type": "competitor_website",
        "competitor": COMPETITOR,
        "pages": [{"url": url, "content": content} for url, content in raw.items()],
    }

    out_path = output_dir / "competitor_raw.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("[competitor] Saved to %s", out_path)
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(Path("data/playwright"))
