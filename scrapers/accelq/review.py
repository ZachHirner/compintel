"""
Scraper: Review websites — PeerSpot and TrustRadius customer reviews for AccelQ.

PeerSpot and TrustRadius are preferred over G2/Capterra (Cloudflare-blocked).
Gartner Peer Insights is included where an AccelQ product profile exists.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # PeerSpot — AccelQ reviews with detailed pros/cons
    "https://www.peerspot.com/products/accelq-reviews",
    # TrustRadius — AccelQ user reviews
    "https://www.trustradius.com/products/accelq/reviews",
    # Gartner Peer Insights — AccelQ reviews in Software Test Automation
    "https://www.gartner.com/reviews/market/software-test-automation/vendor/accelq",
]


def run(output_dir: Path) -> dict:
    logger.info("[review] Starting review site scrape for AccelQ")
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
    run(Path("data/accelq"))
