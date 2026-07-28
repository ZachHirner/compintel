"""
Scraper: Analyst websites — Gartner public pages for AccelQ in the software
test automation category.

AccelQ has limited public analyst coverage compared to larger vendors; we
target Gartner Peer Insights and any publicly available mentions. Full
analyst reports are paywalled.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # Forrester search — AccelQ mentions, last 30 days
    "https://www.forrester.com/allSearch?query=AccelQ&publishedSinceInDays=30",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for AccelQ")
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
    run(Path("data/accelq"))
