"""
Scraper: Review websites — PeerSpot, TrustRadius, and Gartner Peer Insights
customer reviews for Playwright.

Review sites surface real-world pain points, integration challenges, and
verbatim quotes usable in battle cards. G2 and Capterra are excluded due
to Cloudflare bot protection.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "playwright"

URLS = [
    # PeerSpot — Playwright reviews with detailed pros/cons
    "https://www.peerspot.com/products/playwright-reviews",
    # TrustRadius — Playwright user reviews
    "https://www.trustradius.com/products/playwright/reviews",
    # Gartner Peer Insights — Playwright reviews in Software Test Automation
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/microsoft/product/playwright",
]


def run(output_dir: Path) -> dict:
    logger.info("[review] Starting review site scrape for Playwright")
    raw = scrape_multiple(URLS)

    output = {
        "source_type": "review_websites",
        "competitor": COMPETITOR,
        "pages": [{"url": url, "content": content} for url, content in raw.items()],
    }

    out_path = output_dir / "review_raw.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("[review] Saved to %s", out_path)
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(Path("data/playwright"))
