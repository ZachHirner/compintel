"""
Scraper: Review websites — PeerSpot, TrustRadius, and Gartner Peer Insights
customer reviews for UiPath Test Suite.

Review sites surface real-world pain points, competitor comparisons, and
verbatim quotes usable in battle cards. G2 and Capterra are excluded due
to Cloudflare bot protection.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "uipath"

URLS = [
    # PeerSpot — UiPath Test Suite reviews with detailed pros/cons
    "https://www.peerspot.com/products/uipath-test-suite-reviews",
    # PeerSpot — UiPath platform reviews (broader, more volume)
    "https://www.peerspot.com/products/uipath-reviews",
    # TrustRadius — UiPath reviews
    "https://www.trustradius.com/products/uipath/reviews",
    # Gartner Peer Insights — UiPath Test Suite reviews
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/uipath/product/uipath-test-suite",
]


def run(output_dir: Path) -> dict:
    logger.info("[review] Starting review site scrape for UiPath")
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
    run(Path("data/uipath"))
