"""
Scraper: Social media — Panaya LinkedIn, X/Twitter, and YouTube.

Panaya has ~24K LinkedIn followers and ~220 employees. Social content focuses
on SAP S/4HANA migration, self-healing automation, and ERP change intelligence.
YouTube channel hosts product demos and webinars.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple_with_rss

logger = logging.getLogger(__name__)

COMPETITOR = "panaya"

URLS = [
    # LinkedIn public company page
    "https://www.linkedin.com/company/panaya/",
    # X/Twitter
    "https://x.com/Panaya?lang=en",
]

RSS_URLS = [
    # YouTube RSS feed — Panaya channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCaCVGueKcvxnMjV1waiu5cA",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting Panaya social media scrape")
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
    run(Path("data/panaya"))
