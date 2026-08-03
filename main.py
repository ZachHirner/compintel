"""
Competitive Intelligence orchestrator.

Usage:
    python main.py                          # scrape all sources + generate report (opentext)
    python main.py --all                    # run all tracked competitors in sequence
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
import os
import sys
from datetime import datetime
from pathlib import Path
import zoneinfo

from analysis import summarize, delta as delta_mod

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


def _print_delta(delta_report: dict | None) -> None:
    if delta_report:
        n_changed = len(delta_report.get("changed_pages", []))
        n_new = len(delta_report.get("new_pages", []))
        print(f"  Delta vs previous run: {n_changed} page(s) changed, {n_new} new page(s)")


def run_competitor(competitor: str, report_date: str, run_timestamp: str, args: argparse.Namespace) -> None:
    """Run the full pipeline for a single competitor."""
    print(f"\n{'=' * 60}")
    print(f"COMPETITOR: {competitor.upper()}")
    print(f"{'=' * 60}")

    run_dir = DATA_ROOT / competitor / report_date / run_timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    output_dir = DATA_ROOT / competitor
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.analyze_only:
        logger.info("--analyze-only: loading cached raw data from %s", output_dir)
        scraped = load_cached_raw(output_dir)
    else:
        scraper_modules = load_scraper_modules(competitor)
        scraped = run_scrapers(run_dir, scraper_modules)
        for key, filename in RAW_FILE_MAP.items():
            src = run_dir / filename
            if src.exists():
                (output_dir / filename).write_bytes(src.read_bytes())

    delta_report = None
    if not args.analyze_only:
        logger.info("=== Running delta detection ===")
        delta_report = delta_mod.run(run_dir, competitor, DATA_ROOT, report_date)

    if args.scrape_only:
        print(f"Scrape complete. Raw data saved to: {run_dir}")
        for key, filename in RAW_FILE_MAP.items():
            path = run_dir / filename
            if path.exists():
                pages = json.loads(path.read_text()).get("pages", [])
                ok = sum(1 for p in pages if not p["content"].startswith("ERROR"))
                print(f"  {key}: {ok}/{len(pages)} pages scraped successfully")
        _print_delta(delta_report)
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("ANTHROPIC_API_KEY not set — skipping analysis, scrape data saved.")
        print(f"Scrape complete (analysis skipped — no ANTHROPIC_API_KEY). Raw data saved to: {run_dir}")
        _print_delta(delta_report)
        return

    logger.info("=== Running analysis (date: %s) ===", report_date)
    report = summarize.run(output_dir, scraped, report_date, competitor=args.competitor)

    if delta_report:
        report["delta"] = {
            "previous_run_dir": delta_report.get("previous_run_dir"),
            "changes_detected": delta_report.get("changes_detected"),
            "changed_pages": delta_report.get("changed_pages", []),
            "new_pages": delta_report.get("new_pages", []),
        }
        out_path = output_dir / "ci_report.json"
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(json.dumps(report, indent=2))
    print(f"\nFull report saved to: {output_dir / 'ci_report.json'}")


def main():
    parser = argparse.ArgumentParser(description="Competitive Intelligence runner")
    parser.add_argument(
        "--competitor",
        default="opentext",
        choices=SUPPORTED_COMPETITORS,
        help=f"Competitor slug (default: opentext). One of: {', '.join(SUPPORTED_COMPETITORS)}",
    )
    parser.add_argument("--all", action="store_true", help="Run all tracked competitors in sequence")
    parser.add_argument("--scrape-only", action="store_true", help="Scrape only; skip analysis (no API key needed)")
    parser.add_argument("--analyze-only", action="store_true", help="Skip scraping; use cached raw data")
    args = parser.parse_args()

    now = datetime.now(tz=zoneinfo.ZoneInfo("America/Chicago"))
    report_date = now.strftime("%Y-%m-%d")
    run_timestamp = now.strftime("%H-%M-%S")

    competitors = SUPPORTED_COMPETITORS if args.all else [args.competitor]

    for competitor in competitors:
        try:
            run_competitor(competitor, report_date, run_timestamp, args)
        except Exception as exc:
            logger.error("Pipeline failed for %s: %s", competitor, exc)
            if not args.all:
                sys.exit(1)


if __name__ == "__main__":
    main()
