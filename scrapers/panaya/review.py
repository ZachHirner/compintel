"""
Scraper: Review websites — PeerSpot and TrustRadius customer reviews for Panaya.

Panaya Test Dynamix has an active review presence on PeerSpot. TrustRadius
also carries verified reviews. G2 and Capterra are excluded (Cloudflare-blocked).
Key signals to watch: SAP migration satisfaction, support quality, integration
complaints (no SSO, limited connectors), and comparisons to Tricentis.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "panaya"

URLS = [
    # PeerSpot — Panaya Test Dynamix reviews
    "https://www.peerspot.com/products/panaya-test-dynamix-reviews",
    # PeerSpot — Panaya vendor page
    "https://www.peerspot.com/vendors/panaya",
    # TrustRadius — Panaya Test Dynamix reviews
    "https://www.trustradius.com/products/panaya-test-dynamix/reviews",
]


def run(output_dir: Path) -> dict:
    logger.info("[review] Starting review site scrape for Panaya")
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
    run(Path("data/panaya"))
