"""
Scraper: Social media — Playwright GitHub, YouTube, and LinkedIn.

GitHub is the primary community hub for Playwright (open-source project).
LinkedIn and YouTube surface Microsoft's commercial promotion of Playwright.

Note: Twitter/X requires a logged-in session; excluded from prototype.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "playwright"

URLS = [
    # Microsoft LinkedIn company overview
    "https://www.linkedin.com/company/microsoft/",
    # Microsoft LinkedIn Jobs — signals hiring direction
    "https://www.linkedin.com/company/microsoft/jobs/",
    # Playwright YouTube channel
    "https://www.youtube.com/@Playwrightdev",
    # Playwright LinkedIn (community/product page)
    "https://www.linkedin.com/company/playwrightweb/",
    "https://x.com/playwrightweb?lang=en",
]


def run(output_dir: Path) -> dict:
    logger.info("[social_media] Starting Playwright social media scrape")
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
    run(Path("data/playwright"))
