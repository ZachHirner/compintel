# competitive-intel

Generate a competitive intelligence report for a named competitor by orchestrating
four web scrapers (competitor site, social media, analyst coverage, customer reviews)
and synthesizing the results with Claude.

## Trigger phrases
"competitive intel", "CI report", "battle card research", "scrape competitor",
"analyze [competitor name]", "what's [competitor] up to", "competitor research",
"run CI on [competitor]"

## What this skill does

1. Runs `scrapers/competitor.py` — official product pages, pricing, newsroom
2. Runs `scrapers/social_media.py` — LinkedIn, blog, YouTube
3. Runs `scrapers/analyst.py` — Gartner, Forrester, IDC public pages
4. Runs `scrapers/review.py` — G2, TrustRadius, Gartner Peer Insights reviews
5. Passes all raw text to `analysis/summarize.py` which calls the Claude API
6. Outputs a structured JSON report at `data/<competitor>/ci_report.json`

## Instructions

When invoked, follow these steps:

### Step 1 — Confirm scope
Ask the user: "Which competitor? (default: opentext)" and whether they want a
full scrape or just re-analysis of cached data (`--analyze-only`).

### Step 2 — Install dependencies if needed
```bash
pip install -r requirements.txt
```

### Step 3 — Run the orchestrator
Full scrape + analysis:
```bash
python main.py --competitor opentext
```

Re-analyze cached data only (faster, no browser required):
```bash
python main.py --competitor opentext --analyze-only
```

### Step 4 — Present results
Read `data/opentext/ci_report.json` and present the findings in this order:
1. **Executive Summary** — paste verbatim
2. **Key Products** — table with name / description / target segment
3. **Strengths vs. Weaknesses** — two-column comparison
4. **Recent Moves** — bulleted list
5. **Customer Sentiment** — overall rating + top complaints + top praise
6. **Battle Card Notes** — where we win, where they win, landmines, talk tracks

### Step 5 — Save or share
Offer to:
- Export the report as a Markdown battle card
- Save a timestamped copy to `data/opentext/ci_report_<date>.json`

## Competitor tier list (prototype: Tier 1)

| Tier | Competitors |
|------|-------------|
| 1    | OpenText (ValueEdge, UFT One, ALM QC) |
| 2    | Micro Focus (legacy — now OpenText), IBM, Broadcom |
| 3    | Parasoft, SmartBear, Keysight |

## Output schema reference

The CI report JSON has these top-level keys:
- `executive_summary`
- `key_products[]`
- `positioning_themes[]`
- `strengths[]`
- `weaknesses[]`
- `recent_moves[]`
- `analyst_standing` — `{gartner, forrester}`
- `customer_sentiment` — `{overall, top_complaints[], top_praise[]}`
- `tricentis_battlecard_notes` — `{where_we_win[], where_they_win[], key_differentiators[], landmines[], suggested_talk_tracks[]}`
- `data_quality_notes`

## Required environment variable
`ANTHROPIC_API_KEY` must be set for the analysis step.
