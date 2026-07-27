"""
Scraper: Competitor website — Keysight Eggplant test automation product pages.

Keysight acquired Eggplant in 2020. Targets Keysight's software testing and
Eggplant product pages to capture positioning around AI-driven, model-based
test automation.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple, zenrows_scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "keysight"

URLS = [
    # Keysight software solutions hub (updated URL after Eggplant rebrand)
    "https://www.keysight.com/us/en/solutions/software-test-and-simulation.html",
    # Eggplant DAI product page (current URL)
    "https://www.keysight.com/us/en/products/network-test/protocol-load-test/eggplant-digital-automation-intelligence.html",
    # Keysight software testing overview
    "https://www.keysight.com/us/en/home.html",
    # Eggplant blog — product updates and positioning
    "https://www.eggplantsoftware.com/blog",
    # Keysight newsroom (current URL)
    "https://www.keysight.com/us/en/about/newsroom/news-releases.html",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting Keysight/Eggplant product page scrape (via Zenrows)")
    raw = zenrows_scrape_multiple(URLS)

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
    run(Path("data/keysight"))
