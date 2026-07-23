"""
Scraper: Social media — UiPath LinkedIn, blog, and YouTube.

LinkedIn public company page surfaces follower growth and recent posts.
The UiPath blog signals which products and verticals they are pushing.

Note: Twitter/X requires a logged-in session; excluded from prototype.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "uipath"

URLS = [
    # LinkedIn public company page
    "https://www.linkedin.com/company/uipath/",
    # UiPath blog — content strategy signals product focus areas
    "https://www.uipath.com/blog",
    # Blog category: testing — most relevant posts for competitive intel
    "https://www.uipath.com/blog/testing",
    # YouTube channel — demo and product announcement videos
    "https://www.youtube.com/@UiPath",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting UiPath social media scrape")
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
    run(Path("data/uipath"))
