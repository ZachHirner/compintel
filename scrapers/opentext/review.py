"""
Scraper: Review websites — G2, TrustRadius, and Gartner Peer Insights
customer reviews for OpenText DevOps/Quality products.

Review sites are goldmines for: real customer pain points, feature gaps
vs. competitors, and verbatim quotes usable in battle cards. We target
the most trafficked review pages for OpenText's key products in the
DevOps/testing space.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "opentext"

URLS = [
    # PeerSpot — OpenText vendor overview page
    "https://www.peerspot.com/vendors/opentext",
    # Gartner Peer Insights — OpenText software testing reviews
    "https://www.gartner.com/reviews/market/software-testing-tools/vendor/opentext",
    # PeerSpot — OpenText Functional Testing reviews
    "https://www.peerspot.com/products/opentext-functional-testing-reviews",
    # PeerSpot — Application Quality Management reviews
    "https://www.peerspot.com/products/opentext-application-quality-management-reviews",
    # PeerSpot — OpenText vendor Q&A
    "https://www.peerspot.com/vendors/opentext/questions",
]


def run(output_dir: Path) -> dict:
    logger.info("[review] Starting review site scrape for OpenText")
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
    run(Path("data/opentext"))
