"""
Scraper: Competitor website — OpenText product & DevOps/quality pages.

Targets official product listings, DevOps/testing product pages, and
the pricing/contact page so we capture positioning and feature messaging.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "opentext"

URLS = [
    # Product catalogue
    "https://www.opentext.com/products/listing",
    # DevOps / Quality suite (ValueEdge, Micro Focus legacy)
    "https://www.opentext.com/products/devops-cloud",
    "https://www.opentext.com/products/valueedge",
    "https://www.opentext.com/products/application-quality-management",
    # Newsroom — press releases reveal positioning shifts
    "https://www.opentext.com/about/newsroom",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting OpenText product page scrape")
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
    run(Path("data/opentext"))
