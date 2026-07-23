"""
Scraper: Social media — OpenText LinkedIn company page and blog.

LinkedIn's public company page is accessible without login and surfaces
recent posts, employee count, and follower growth signals. The OpenText
blog doubles as a content/social signal for product focus areas.

Note: Twitter/X requires a logged-in session; excluded from prototype.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "opentext"

URLS = [
    # LinkedIn public company page (no login required for basic info)
    "https://www.linkedin.com/company/opentext/",
    # OpenText blog — content strategy signals which products they're pushing
    "https://blogs.opentext.com/",
    "https://blogs.opentext.com/category/devops/",
    # OpenText YouTube channel page (public metadata)
    "https://www.youtube.com/@OpenText",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting OpenText social media scrape")
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
    run(Path("data/opentext"))
