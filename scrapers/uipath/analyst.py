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
    # Forrester blog — vendor profile and Wave coverage mentions
    "https://www.forrester.com/blogs/",
    # UiPath newsroom — press releases with analyst mentions
    "https://www.uipath.com/newsroom",
    # Capterra — UiPath reviews
    "https://www.capterra.com/p/155035/UiPath/",
    # SlashDot — UiPath reviews
    "https://slashdot.org/software/p/UiPath/",
    # IDC MarketScape mentions via UiPath blog
    "https://www.uipath.com/blog/automation/analyst-reports",
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
