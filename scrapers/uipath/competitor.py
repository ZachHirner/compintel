"""
Scraper: Competitor website — UiPath Test Suite product pages.

Targets UiPath's test automation product pages, pricing signals, and
newsroom to capture positioning in the RPA + test automation space.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "uipath"

URLS = [
    # Test Suite product landing page
    "https://www.uipath.com/product/test-suite",
    # Test Manager — test management component
    "https://www.uipath.com/product/test-suite/test-manager",
    # Studio — authoring environment for test automation
    "https://www.uipath.com/product/studio",
    # Platform overview — positions UiPath beyond RPA into end-to-end automation
    "https://www.uipath.com/platform",
    # Newsroom — press releases reveal positioning and partnership shifts
    "https://www.uipath.com/newsroom",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting UiPath product page scrape")
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
    run(Path("data/uipath"))
