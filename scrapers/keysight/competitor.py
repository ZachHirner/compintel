"""
Scraper: Competitor website — Keysight Eggplant test automation product pages.

Keysight acquired Eggplant in 2020. Targets Keysight's software testing and
Eggplant product pages to capture positioning around AI-driven, model-based
test automation.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "keysight"

URLS = [
    # Eggplant product landing page (Keysight Software Testing)
    "https://www.keysight.com/us/en/products/software-testing.html",
    # Eggplant DAI — Digital Automation Intelligence (flagship product)
    "https://www.keysight.com/us/en/products/software-testing/eggplant-test.html",
    # Eggplant Manager — test management component
    "https://www.keysight.com/us/en/products/software-testing/eggplant-manager.html",
    # Software testing overview / hub page
    "https://www.eggplantsoftware.com/",
    # Newsroom — press releases and analyst recognition
    "https://www.keysight.com/us/en/about/newsroom.html",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting Keysight/Eggplant product page scrape")
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
    run(Path("data/keysight"))
