# compintel

Competitive intelligence scraping and analysis pipeline for Tricentis.

Scrapes four source types per competitor, then synthesizes a structured CI report
using the Claude API — including a battle card section tailored for Tricentis AEs.

## Architecture

```
compintel/
├── scrapers/
│   ├── base.py           # shared headless Chrome driver (undetected_chromedriver)
│   ├── competitor.py     # official product pages, newsroom
│   ├── social_media.py   # LinkedIn, blog, YouTube
│   ├── analyst.py        # Gartner, Forrester, IDC public pages
│   └── review.py         # G2, TrustRadius, Gartner Peer Insights
├── analysis/
│   └── summarize.py      # Claude API — synthesizes all sources into CI report JSON
├── data/
│   └── opentext/         # raw + analyzed output per competitor
├── main.py               # orchestrator CLI
├── requirements.txt
└── .claude/skills/
    └── competitive-intel.md  # Claude Code skill definition
```

## Quick start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here

# Full scrape + analysis
python main.py --competitor opentext

# Re-analyze cached data (no browser)
python main.py --competitor opentext --analyze-only
```

## Output

`data/opentext/ci_report.json` — structured report with:
- Executive summary
- Key products & positioning themes
- Strengths / weaknesses
- Recent moves (newsroom signals)
- Analyst standing (Gartner, Forrester)
- Customer sentiment (G2/TrustRadius reviews)
- Battle card notes for Tricentis AEs

## Prototype scope

Tier 1 competitor: **OpenText** (ValueEdge, UFT One, ALM Quality Center)

## Requirements

- Python 3.11+
- Chrome 150 (matches `version_main=150` in `scrapers/base.py` — update if runner upgrades)
- `ANTHROPIC_API_KEY` environment variable