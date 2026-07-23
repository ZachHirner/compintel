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
    # GitHub repo — stars, issues, contributor activity, README positioning
    "https://github.com/microsoft/playwright",
    # GitHub discussions — community pain points and feature requests
    "https://github.com/microsoft/playwright/discussions",
    # Microsoft LinkedIn — company-level promotion of Playwright
    "https://www.linkedin.com/company/microsoft/",
    # YouTube playlist — official Playwright demo and tutorial videos
    "https://www.youtube.com/@Playwrightdev",
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
