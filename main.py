"""
Competitive Intelligence orchestrator.

Usage:
    python main.py                     # scrape all sources + generate report
    python main.py --scrape-only       # scrape only, skip analysis (no API key needed)
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
    parser.add_argument("--scrape-only", action="store_true", help="Scrape only; skip analysis (no API key needed)")
    parser.add_argument("--analyze-only", action="store_true", help="Skip scraping; use cached raw data")
    args = parser.parse_args()

    report_date = date.today().isoformat()

    # Datestamped subdirectory preserves each run's raw data historically
    run_dir = DATA_ROOT / args.competitor / report_date
    run_dir.mkdir(parents=True, exist_ok=True)

    # Latest symlink/alias dir for --analyze-only convenience
    output_dir = DATA_ROOT / args.competitor
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.analyze_only:
        logger.info("--analyze-only: loading cached raw data from %s", output_dir)
        scraped = load_cached_raw(output_dir)
    else:
        scraped = run_scrapers(run_dir)
        # Also write to the flat competitor dir so --analyze-only always finds latest
        for key, filename in RAW_FILE_MAP.items():
            src = run_dir / filename
            if src.exists():
                (output_dir / filename).write_bytes(src.read_bytes())

    if args.scrape_only:
        print("\nScrape complete. Raw data saved to:", run_dir)
        for key, filename in RAW_FILE_MAP.items():
            path = run_dir / filename
            if path.exists():
                pages = json.loads(path.read_text()).get("pages", [])
                ok = sum(1 for p in pages if not p["content"].startswith("ERROR"))
                print(f"  {key}: {ok}/{len(pages)} pages scraped successfully")
        return
    logger.info("=== Running analysis (date: %s) ===", report_date)
    report = summarize.run(output_dir, scraped, report_date)

    print("\n" + "=" * 60)
    print(f"COMPETITIVE INTELLIGENCE REPORT — {args.competitor.upper()}")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print("\nFull report saved to:", output_dir / "ci_report.json")


if __name__ == "__main__":
    main()
