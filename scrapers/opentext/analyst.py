"""
Scraper: Analyst websites — Gartner, Forrester, IDC public pages for OpenText.

Full analyst reports are paywalled; we target publicly visible summaries,
Magic Quadrant landing pages, Peer Insights overview pages, and press
releases that cite analyst rankings. These provide positioning signals
without requiring paid subscriptions.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "opentext"

URLS = [
    # Forrester search — OpenText mentions in the last 30 days
    "https://www.forrester.com/allSearch?query=OpenText&publishedSinceInDays=30",
    # Forrester blogs — free analyst commentary, no paywall
    "https://www.forrester.com/blogs/",
    # Gartner Peer Insights — OpenText software testing market reviews and ratings
    "https://www.gartner.com/reviews/market/software-testing-tools/vendor/opentext",
    # Gartner Peer Insights — OpenText application quality management
    "https://www.gartner.com/reviews/market/devops-platforms/vendor/opentext",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for OpenText")
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
    run(Path("data/opentext"))
