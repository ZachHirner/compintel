"""
Scraper: Social media — AccelQ LinkedIn, blog, YouTube RSS, and X/Twitter.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple_with_rss

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # LinkedIn public company page
    "https://www.linkedin.com/company/accelq/",
    # AccelQ blog
    "https://www.accelq.com/blog/",
    # X/Twitter
    "https://x.com/ACCELQ?lang=en",
]

RSS_URLS = [
    # YouTube RSS feed — channel ID UCW8CbXDMJ7nHW8pFDDuPkVA
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCW8CbXDMJ7nHW8pFDDuPkVA",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting AccelQ social media scrape")
    raw = scrape_multiple_with_rss(URLS, rss_urls=RSS_URLS)

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
