"""
Scraper: Social media — AccelQ LinkedIn, blog, and YouTube.

LinkedIn public company page surfaces follower growth and recent posts.
The AccelQ blog signals product focus areas and go-to-market messaging.

Note: Twitter/X requires a logged-in session; excluded from prototype.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # LinkedIn public company page
    "https://www.linkedin.com/company/accelq/",
    # AccelQ blog — content strategy signals product direction
    "https://www.accelq.com/blog/",
    # YouTube channel — product demos and webinars
    "https://www.youtube.com/@accelq",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting AccelQ social media scrape")
    raw = scrape_multiple(URLS)

    output = {
        "source_type": "social_media",
        "competitor": COMPETITOR,
        "pages": [{"url": url, "content": content} for url, content in raw.items()],
    }

    out_path = output_dir / "social_media_raw.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("[social_media] Saved to %s", out_path)
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(Path("data/accelq"))
