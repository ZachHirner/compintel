"""
Delta detection: compares the current scrape run against the most recent previous run
and surfaces meaningful content changes for competitive intelligence.
"""
import difflib
import json
import hashlib
import logging
import os
from pathlib import Path

import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-5"

_FILE_MAP = {
    "competitor": "competitor_raw.json",
    "social_media": "social_media_raw.json",
    "analyst": "analyst_raw.json",
    "review": "review_raw.json",
}

_SIGNIFICANT_CHANGE_PCT = 5  # pages with >5% content change get an AI summary


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _find_previous_run(competitor_dir: Path, current_run_dir: Path) -> Path | None:
    """
    Return the most recent run from a different calendar date than current_run_dir.
    Falls back to any earlier run if no prior-date run exists.
    This prevents same-day test runs from being compared against each other.
    """
    current_date = current_run_dir.parent.name  # YYYY-MM-DD
    same_date_runs = []
    prior_date_runs = []

    for date_dir in competitor_dir.iterdir():
        if not date_dir.is_dir() or date_dir.name.startswith("."):
            continue
        for time_dir in date_dir.iterdir():
            if not time_dir.is_dir() or time_dir.resolve() == current_run_dir.resolve():
                continue
            key = f"{date_dir.name}/{time_dir.name}"
            current_key = f"{current_date}/{current_run_dir.name}"
            if key >= current_key:
                continue  # skip runs after the current one
            if date_dir.name == current_date:
                same_date_runs.append(time_dir)
            else:
                prior_date_runs.append(time_dir)

    # Prefer the latest run from a prior date; fall back to same-day if none
    for pool in (prior_date_runs, same_date_runs):
        if pool:
            pool.sort(key=lambda p: f"{p.parent.name}/{p.name}")
            return pool[-1]
    return None


def _load_pages(run_dir: Path, source_type: str) -> dict[str, str]:
    """Return {url: content} for a given source type in a run directory."""
    path = run_dir / _FILE_MAP[source_type]
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {p["url"]: p["content"] for p in data.get("pages", [])}


def _text_diff_excerpts(prev_text: str, curr_text: str, max_lines: int = 40) -> dict:
    """
    Return the added and removed lines from a unified diff of two text blocks.
    Splits on newlines; strips blank diff lines. Caps at max_lines per side.
    """
    prev_lines = prev_text.splitlines(keepends=True)
    curr_lines = curr_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(prev_lines, curr_lines, lineterm="", n=0))

    added = []
    removed = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            stripped = line[1:].strip()
            if stripped:
                added.append(stripped)
        elif line.startswith("-") and not line.startswith("---"):
            stripped = line[1:].strip()
            if stripped:
                removed.append(stripped)

    return {
        "added_lines": added[:max_lines],
        "removed_lines": removed[:max_lines],
    }


def _compare(current_run_dir: Path, previous_run_dir: Path) -> dict:
    changed = []
    new_pages = []
    removed_pages = []
    unchanged_count = 0

    for source_type in _FILE_MAP:
        curr = _load_pages(current_run_dir, source_type)
        prev = _load_pages(previous_run_dir, source_type)

        for url, curr_content in curr.items():
            if url not in prev:
                new_pages.append({"url": url, "source_type": source_type})
            elif _hash(curr_content) != _hash(prev[url]):
                prev_len = len(prev[url])
                curr_len = len(curr_content)
                excerpts = _text_diff_excerpts(prev[url], curr_content)
                changed.append({
                    "url": url,
                    "source_type": source_type,
                    "prev_length": prev_len,
                    "curr_length": curr_len,
                    "length_delta": curr_len - prev_len,
                    "change_pct": round(abs(curr_len - prev_len) / max(prev_len, 1) * 100, 1),
                    "added_lines": excerpts["added_lines"],
                    "removed_lines": excerpts["removed_lines"],
                })
            else:
                unchanged_count += 1

        for url in prev:
            if url not in curr:
                removed_pages.append({"url": url, "source_type": source_type})

    return {
        "changes_detected": bool(changed or new_pages),
        "changed_pages": changed,
        "new_pages": new_pages,
        "removed_pages": removed_pages,
        "unchanged_count": unchanged_count,
    }


def _ai_summarize_changes(
    changed: list,
    current_run_dir: Path,
    previous_run_dir: Path,
    competitor: str,
) -> list:
    """Add an ai_summary to changed pages where content shifted >_SIGNIFICANT_CHANGE_PCT%."""
    significant = [c for c in changed if c["change_pct"] > _SIGNIFICANT_CHANGE_PCT]
    if not significant:
        return changed

    client = anthropic.Anthropic()

    for change in significant:
        added = "\n".join(change.get("added_lines", []))[:2000]
        removed = "\n".join(change.get("removed_lines", []))[:2000]

        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": (
                        f"You are a competitive intelligence analyst tracking {competitor.upper()}.\n"
                        f"URL: {change['url']}\n\n"
                        "Below are the EXACT lines added and removed since the last scrape.\n"
                        "Identify any substantive competitive changes: new product names, "
                        "updated pricing or packaging, changed taglines or messaging, new feature "
                        "names, headcount or funding numbers, or newly announced partnerships.\n"
                        "Quote the specific changed text where possible. "
                        "If the diff only contains nav links, timestamps, cookie notices, or "
                        "formatting noise, say: 'No substantive changes — cosmetic/layout diff only.'\n\n"
                        f"LINES ADDED:\n{added or '(none)'}\n\n"
                        f"LINES REMOVED:\n{removed or '(none)'}"
                    ),
                }],
            )
            change["ai_summary"] = resp.content[0].text
        except Exception as exc:
            logger.warning("[delta] AI summary failed for %s: %s", change["url"], exc)

    return changed


def run(current_run_dir: Path, competitor: str, data_root: Path, report_date: str) -> dict | None:
    """
    Compare current run against the most recent previous run for the same competitor.
    Returns None if no previous run exists.
    Saves delta_report.json into current_run_dir.
    """
    competitor_dir = data_root / competitor
    previous_run_dir = _find_previous_run(competitor_dir, current_run_dir)

    if previous_run_dir is None:
        logger.info("[delta] No previous run found for %s — skipping", competitor)
        return None

    logger.info("[delta] Comparing %s vs %s", previous_run_dir, current_run_dir)
    delta = _compare(current_run_dir, previous_run_dir)

    if delta["changed_pages"] and os.environ.get("ANTHROPIC_API_KEY"):
        delta["changed_pages"] = _ai_summarize_changes(
            delta["changed_pages"], current_run_dir, previous_run_dir, competitor
        )

    report = {
        "competitor": competitor,
        "run_date": report_date,
        "previous_run_dir": str(previous_run_dir),
        **delta,
    }

    out_path = current_run_dir / "delta_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    logger.info(
        "[delta] %d changed, %d new, %d removed. Report saved to %s",
        len(delta["changed_pages"]),
        len(delta["new_pages"]),
        len(delta["removed_pages"]),
        out_path,
    )
    return report
