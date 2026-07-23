"""
Competitive Intelligence orchestrator.

Usage:
    python main.py                          # scrape all sources + generate report
    python main.py --scrape-only            # scrape only, skip analysis (no API key needed)
    python main.py --analyze-only           # skip scraping, re-analyze cached raw data
    python main.py --competitor opentext    # explicit competitor (default: opentext)

Supported competitors: opentext, playwright, uipath, accelq, keysight

Environment variables:
    ANTHROPIC_API_KEY  — required for the analysis step
"""
import argparse
import importlib
import json
import logging
import sys
from datetime import date
from pathlib import Path

from analysis import summarize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DATA_ROOT = Path("data")

SUPPORTED_COMPETITORS = ["opentext", "playwright", "uipath", "accelq", "keysight"]

RAW_FILE_MAP = {
    "competitor": "competitor_raw.json",
    "social_media": "social_media_raw.json",
    "analyst": "analyst_raw.json",
    "review": "review_raw.json",
}


def load_scraper_modules(competitor: str) -> dict:
    """Dynamically import the four scraper modules for the given competitor."""
    return {
        key: importlib.import_module(f"scrapers.{competitor}.{key}")
        for key in ["competitor", "social_media", "analyst", "review"]
    }


def run_scrapers(output_dir: Path, scraper_modules: dict) -> dict[str, dict]:
    results = {}
    for key, module in scraper_modules.items():
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
    parser.add_argument(
        "--competitor",
        default="opentext",
        choices=SUPPORTED_COMPETITORS,
        help=f"Competitor slug (default: opentext). One of: {', '.join(SUPPORTED_COMPETITORS)}",
    )
    parser.add_argument("--scrape-only", action="store_true", help="Scrape only; skip analysis (no API key needed)")
    parser.add_argument("--analyze-only", action="store_true", help="Skip scraping; use cached raw data")
    args = parser.parse_args()

    from datetime import datetime
    now = datetime.utcnow()
    report_date = now.strftime("%Y-%m-%d")
    run_timestamp = now.strftime("%H%M%S")

    # data/<competitor>/YYYY-MM-DD/HHMMSS/ — unique folder per run
    run_dir = DATA_ROOT / args.competitor / report_date / run_timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Latest symlink/alias dir for --analyze-only convenience
    output_dir = DATA_ROOT / args.competitor
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.analyze_only:
        logger.info("--analyze-only: loading cached raw data from %s", output_dir)
        scraped = load_cached_raw(output_dir)
    else:
        scraper_modules = load_scraper_modules(args.competitor)
        scraped = run_scrapers(run_dir, scraper_modules)
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
