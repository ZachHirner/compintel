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
    # Gartner Peer Insights — OpenText vendor profile (public)
    "https://www.gartner.com/reviews/market/devops-platforms/vendor/opentext",
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/opentext",
    # Forrester vendor profile page
    "https://www.forrester.com/vendor-profile/opentext-corp--VID1152",
    # IDC vendor page
    "https://www.idc.com/vendor/opentext",
    # OpenText's own analyst-relations page (reveals which quadrants they cite)
    "https://www.opentext.com/about/analyst-relations",
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
