"""
Scraper: Competitor website — AccelQ AI-powered codeless test automation.

Targets AccelQ's product and features pages to capture positioning around
codeless automation, AI testing, and enterprise integrations.
"""
import json
import logging
from pathlib import Path
from scrapers.base import scrape_multiple

logger = logging.getLogger(__name__)

COMPETITOR = "accelq"

URLS = [
    # Homepage — headline positioning and key value props
    "https://www.accelq.com/",
    # Product overview — codeless AI-powered automation pitch
    "https://www.accelq.com/platform/",
    # Features page — detailed capability listing
    "https://www.accelq.com/features/",
    # Integrations — CI/CD and tool ecosystem signals
    "https://www.accelq.com/integrations/",
    # Resources / newsroom — recent announcements and positioning shifts
    "https://www.accelq.com/resources/",
]


def run(output_dir: Path) -> dict:
    logger.info("[competitor] Starting AccelQ product page scrape")
    raw = scrape_multiple(URLS)

    output = {
        "source_type": "competitor_website",
        "competitor": COMPETITOR,
        "pages": [{"url": url, "content": content} for url, content in raw.items()],
    }

    out_path = output_dir / "competitor_raw.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("[competitor] Saved to %s", out_path)
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(Path("data/accelq"))
