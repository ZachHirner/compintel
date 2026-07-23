"""
Scraper: Analyst websites — Gartner and Forrester public pages for UiPath
in the test automation and RPA categories.

Full analyst reports are paywalled; we target publicly visible Gartner Peer
Insights vendor profiles and Forrester blog posts mentioning UiPath.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "uipath"

URLS = [
    # Gartner Peer Insights — UiPath in Software Test Automation market
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/uipath",
    # Gartner Peer Insights — UiPath in Robotic Process Automation market (adjacent)
    "https://www.gartner.com/reviews/market/robotic-process-automation/vendor/uipath",
    # Forrester blog — vendor profile and Wave coverage mentions
    "https://www.forrester.com/blogs/",
    # UiPath analyst relations page — links to public analyst recognitions
    "https://www.uipath.com/company/analyst-recognition",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for UiPath")
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
    run(Path("data/uipath"))
