"""
Scraper: Analyst websites — Gartner public pages for AccelQ in the software
test automation category.

AccelQ has limited public analyst coverage compared to larger vendors; we
target Gartner Peer Insights and any publicly available mentions. Full
analyst reports are paywalled.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # Gartner Peer Insights — AccelQ vendor profile in Software Test Automation
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/accelq",
    # Gartner Peer Insights — broader Software Test Automation market
    "https://www.gartner.com/reviews/market/software-test-automation",
    # Forrester blog — any coverage of codeless/AI test automation
    "https://www.forrester.com/blogs/",
    # AccelQ case studies — analyst-adjacent social proof signals
    "https://www.accelq.com/case-studies/",
]


def run(output_dir: Path) -> dict:
    logger.info("[analyst] Starting analyst page scrape for AccelQ")
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
    run(Path("data/accelq"))
