"""
Analysis layer: takes raw scraped JSON from all four source types and
produces a structured competitive intelligence report via the Claude API.
"""
import json
import logging
from pathlib import Path
import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a senior competitive intelligence analyst at Tricentis, a software testing company.
Tricentis competes directly with OpenText in the DevOps quality / software testing market.
Your job is to synthesize raw web-scraped data into actionable CI reports for the Tricentis sales and product teams."""

ANALYSIS_PROMPT_TEMPLATE = """Below is raw text scraped from four source types about OpenText.
Analyze all sources and produce a structured competitive intelligence report in JSON.

---
## SOURCE 1: Competitor Website (product pages, messaging, newsroom)
{competitor_content}

---
## SOURCE 2: Social Media (LinkedIn, blog, YouTube)
{social_content}

---
## SOURCE 3: Analyst Coverage (Gartner, Forrester, IDC)
{analyst_content}

---
## SOURCE 4: Customer Reviews (G2, TrustRadius, Gartner Peer Insights)
{review_content}

---

Produce a JSON object with exactly these keys:

{{
  "competitor": "OpenText",
  "report_date": "{report_date}",
  "executive_summary": "3-4 sentence overview of OpenText's current competitive position in DevOps/quality testing",
  "key_products": [
    {{"name": "...", "description": "...", "target_segment": "..."}}
  ],
  "positioning_themes": ["list of 3-5 core messaging themes OpenText uses"],
  "strengths": ["list of genuine strengths from product pages + analyst data"],
  "weaknesses": ["list of weaknesses surfaced in customer reviews and analyst commentary"],
  "recent_moves": ["list of notable recent announcements, acquisitions, or pivots from newsroom/blog"],
  "analyst_standing": {{
    "gartner": "brief summary of Gartner positioning if available, else null",
    "forrester": "brief summary of Forrester positioning if available, else null"
  }},
  "customer_sentiment": {{
    "overall": "positive | mixed | negative",
    "top_complaints": ["top 3 complaints from reviews"],
    "top_praise": ["top 3 praised aspects from reviews"]
  }},
  "tricentis_battlecard_notes": {{
    "where_we_win": ["situations or deal types where Tricentis beats OpenText"],
    "where_they_win": ["situations or deal types where OpenText beats Tricentis"],
    "key_differentiators": ["Tricentis advantages to emphasize in competitive deals"],
    "landmines": ["OpenText weaknesses to probe during discovery"],
    "suggested_talk_tracks": ["1-2 sentence talk tracks for AEs"]
  }},
  "data_quality_notes": "Brief note on which sources had useful data vs. blocked/empty pages"
}}

Return only the JSON object, no markdown fences."""


def _extract_text(scraped_data: dict) -> str:
    """Flatten a scraped data dict into a single text block for the prompt."""
    parts = []
    for page in scraped_data.get("pages", []):
        url = page.get("url", "unknown")
        content = page.get("content", "")
        parts.append(f"[{url}]\n{content[:4000]}")  # cap per-page to keep prompt manageable
    return "\n\n".join(parts) if parts else "No data available."


def run(output_dir: Path, scraped_data: dict[str, dict], report_date: str) -> dict:
    """
    scraped_data: {
        "competitor": <dict from competitor.run()>,
        "social_media": <dict from social_media.run()>,
        "analyst": <dict from analyst.run()>,
        "review": <dict from review.run()>,
    }
    """
    logger.info("[analysis] Building CI report via Claude API")

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        competitor_content=_extract_text(scraped_data.get("competitor", {})),
        social_content=_extract_text(scraped_data.get("social_media", {})),
        analyst_content=_extract_text(scraped_data.get("analyst", {})),
        review_content=_extract_text(scraped_data.get("review", {})),
        report_date=report_date,
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_response = message.content[0].text
    logger.info("[analysis] Received %d chars from Claude", len(raw_response))

    try:
        report = json.loads(raw_response)
    except json.JSONDecodeError:
        logger.warning("[analysis] Response was not valid JSON; storing raw text")
        report = {"raw_response": raw_response, "parse_error": True}

    out_path = output_dir / "ci_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    logger.info("[analysis] CI report saved to %s", out_path)
    return report


def load_existing(output_dir: Path) -> dict | None:
    """Load a previously generated report without re-scraping."""
    path = output_dir / "ci_report.json"
    if path.exists():
        return json.loads(path.read_text())
    return None
