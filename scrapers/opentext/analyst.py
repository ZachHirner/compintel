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
    # Gartner Peer Insights — OpenText vendor profiles (public)
    "https://www.gartner.com/reviews/market/devops-platforms/vendor/opentext",
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/opentext",
    # Forrester public blog — vendor profile pages are login-walled
    "https://www.forrester.com/blogs/",
    # OpenText leadership page — signals strategic direction when IDC/analyst pages are paywalled
    "https://www.opentext.com/about/leadership",
    # OpenText newsroom — press releases citing analyst recognition (replaces 404 analyst-reports page)
    "https://www.opentext.com/about/news",
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
