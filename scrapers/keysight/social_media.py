"""
Scraper: Social media — Keysight/Eggplant LinkedIn, blog, and YouTube.

LinkedIn surfaces company-level signals. The Eggplant/Keysight blog and
YouTube channel show which use cases and verticals they are pushing.

Note: Twitter/X requires a logged-in session; excluded from prototype.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "keysight"

URLS = [
    # LinkedIn — Keysight Technologies company page (Eggplant is a product line)
    "https://www.linkedin.com/company/keysight-technologies/",
    # Eggplant blog — content strategy for the software testing product line
    "https://www.eggplantsoftware.com/blog",
    # Keysight software testing blog
    "https://www.keysight.com/us/en/about/keysight-blog.html",
    # YouTube — Keysight software testing demos and webinars
    "https://www.youtube.com/@KeysightTech",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting Keysight social media scrape")
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
    run(Path("data/keysight"))
