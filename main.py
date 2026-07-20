"""
Competitive Intelligence orchestrator.

Usage:
    python main.py                     # scrape all sources + generate report
    python main.py --analyze-only      # skip scraping, re-analyze cached raw data
    python main.py --competitor opentext  # explicit competitor (default: opentext)

Environment variables:
    ANTHROPIC_API_KEY  — required for the analysis step
"""
import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

from scrapers import competitor, social_media, analyst, review
from analysis import summarize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DATA_ROOT = Path("data")

SCRAPER_MAP = {
    "competitor": competitor,
    "social_media": social_media,
    "analyst": analyst,
    "review": review,
}

RAW_FILE_MAP = {
    "competitor": "competitor_raw.json",
    "social_media": "social_media_raw.json",
    "analyst": "analyst_raw.json",
    "review": "review_raw.json",
}


def run_scrapers(output_dir: Path) -> dict[str, dict]:
    results = {}
    for key, module in SCRAPER_MAP.items():
        logger.info("=== Running %s scraper ===", key)
        try:
            results[key] = module.run(output_dir)
        except Exception as exc:
            logger.error("Scraper %s failed: %s", key, exc)
            results[key] = {"pages": [], "error": str(exc)}
    return results


def load_cached_raw(output_dir: Path) -> dict[str, dict]:
    results = {}
    for key, filename in RAW_FILE_MAP.items():
        path = output_dir / filename
        if path.exists():
            results[key] = json.loads(path.read_text())
            logger.info("Loaded cached %s from %s", key, path)
        else:
            logger.warning("No cached data for %s at %s", key, path)
            results[key] = {"pages": []}
    return results


def main():
    parser = argparse.ArgumentParser(description="Competitive Intelligence runner")
    parser.add_argument("--competitor", default="opentext", help="Competitor slug (default: opentext)")
    parser.add_argument("--analyze-only", action="store_true", help="Skip scraping; use cached raw data")
    args = parser.parse_args()

    output_dir = DATA_ROOT / args.competitor
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.analyze_only:
        logger.info("--analyze-only: loading cached raw data")
        scraped = load_cached_raw(output_dir)
    else:
        scraped = run_scrapers(output_dir)

    report_date = date.today().isoformat()
    logger.info("=== Running analysis (date: %s) ===", report_date)
    report = summarize.run(output_dir, scraped, report_date)

    print("\n" + "=" * 60)
    print("COMPETITIVE INTELLIGENCE REPORT — OpenText")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print("\nFull report saved to:", output_dir / "ci_report.json")


if __name__ == "__main__":
    main()
