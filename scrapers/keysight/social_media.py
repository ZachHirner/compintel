"""
Scraper: Social media — Keysight LinkedIn, blog, YouTube RSS, and X/Twitter.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple_with_rss

logger = logging.getLogger(__name__)

COMPETITOR = "keysight"

URLS = [
    # LinkedIn company overview
    "https://www.linkedin.com/company/keysight-technologies?trk=nav_type_overview",
    # Blog (bot-verified — kept for monitoring, may return thin content)
    "https://www.keysight.com/blogs/en/",
    # X/Twitter
    "https://x.com/Keysight?lang=en",
]

RSS_URLS = [
    # YouTube RSS feed — channel ID UCsUQ4q-woGsK3VaAQynptbg
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCsUQ4q-woGsK3VaAQynptbg",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting Keysight social media scrape")
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
    run(Path("data/keysight"))
