"""
Scraper: Competitor website — Panaya AI-powered ERP test automation and change intelligence.

Panaya (acquired by Infosys in 2015) targets SAP, Oracle EBS, and Salesforce
customers with codeless test automation, change impact analysis, and an
S/4HANA migration accelerator. Captures positioning, product pages, and blog.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "panaya"

URLS = [
    # Homepage — core value proposition and messaging
    "https://www.panaya.com/",
    # Testing platform overview
    "https://www.panaya.com/testing/",
    # SAP testing — primary product page
    "https://www.panaya.com/testing/sap-testing/",
    # SAP change intelligence hub
    "https://www.panaya.com/sap/",
    # Press releases and announcements
    "https://www.panaya.com/press/",
    # Testing blog — recent content and messaging themes
    "https://www.panaya.com/blog/testing/",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting Panaya product page scrape")
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
    run(Path("data/panaya"))
