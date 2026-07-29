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
    # Agentic Testing — new AI-driven testing positioning
    "https://www.uipath.com/platform/agentic-automation/agentic-ai",
    # Product overview
    "https://www.uipath.com/product",
    # Agentic Automation — broader platform pitch
    "https://www.uipath.com/platform/agentic-automation",
    # Studio — authoring environment
    "https://www.uipath.com/product/studio",
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
