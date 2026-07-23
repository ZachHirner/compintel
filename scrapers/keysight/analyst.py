"""
Scraper: Analyst websites — Gartner and Forrester public pages for Keysight
Eggplant in the software test automation category.

Full analyst reports are paywalled; we target publicly visible Gartner Peer
Insights vendor profiles, Magic Quadrant landing pages, and Forrester blog
posts mentioning Eggplant or Keysight software testing.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "keysight"

URLS = [
    # Gartner Peer Insights — Keysight (Eggplant) in Software Test Automation
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/keysight",
    # Gartner Peer Insights — Eggplant product profile
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/keysight/product/eggplant-test",
    # Forrester blog — any coverage of AI-driven or model-based test automation
    "https://www.forrester.com/blogs/",
    # Keysight analyst relations — links to public recognitions
    "https://www.keysight.com/us/en/about/analyst-relations.html",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for Keysight")
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
    run(Path("data/keysight"))
