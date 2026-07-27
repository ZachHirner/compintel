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
    # Forrester blog — AI-driven and model-based test automation coverage
    "https://www.forrester.com/blogs/",
    # Keysight newsroom — press releases with analyst mentions
    "https://www.keysight.com/us/en/about/newsroom/press-releases.html",
    # Capterra — Eggplant reviews
    "https://www.capterra.com/p/131233/Eggplant/",
    # SlashDot — Eggplant reviews
    "https://slashdot.org/software/p/Eggplant/",
    # Eggplant resources — whitepapers and analyst-adjacent content
    "https://www.eggplantsoftware.com/resources",
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
