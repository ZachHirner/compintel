"""
Scraper: Analyst websites — Forrester and Gartner public coverage for Panaya.

Panaya appears in Gartner Peer Insights under Application Development and
receives periodic Forrester mentions in ERP testing and change intelligence
research. Full reports are paywalled; public search results are captured.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "panaya"

URLS = [
    # Forrester search — Panaya mentions, last 30 days
    "https://www.forrester.com/allSearch?query=Panaya&publishedSinceInDays=30&activeTab=All",
    # Gartner Peer Insights — Panaya vendor profile (Application Development)
    "https://www.gartner.com/reviews/market/application-development/vendor/panaya",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for Panaya")
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
    run(Path("data/panaya"))
