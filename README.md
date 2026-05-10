# Game Portfolio: Player Insights and Narrative Design

This repository contains selected public-facing materials from my game portfolio. It combines player sentiment analysis, Power BI dashboard walkthroughs, playable Twine prototypes, and branching narrative design documentation.

## Projects

### 1. Live-Service Sentiment Diagnostics

Steam review analysis of Apex Legends, Icarus, and Path of Exile, focused on where different live-service games lose player trust across the player lifecycle.

Key question:

> How do different live-service games lose player trust at different stages of the player lifecycle?

Main outputs:

- Power BI PDF walkthrough: `dashboards/Live-Service Sentiment Diagnostics.pdf`
- Python notebooks: `notebooks/*retention_analysis.ipynb`
- Aggregated lifecycle and theme tables: `data/lifecycle_risk_map_pct.csv`, `data/complaint_portfolio_matrix.csv`

### 2. Narrative as a Satisfaction Buffer

Steam review analysis of God of War, Red Dead Redemption 2, and The Witcher 3, focused on whether narrative-mentioning reviews show a higher positive-rate baseline and whether narrative assets still appear in positive reviews that also mention gameplay or mechanical friction.

Key questions:

> What is the positive-rate gap between narrative and non-narrative reviews?
>
> Among reviews that mention gameplay flaws, which narrative assets still appear in positive recommendations?

Terminology:

- Narrative lift: the positive-rate gap between narrative-mentioning reviews and non-narrative reviews.
- Compensation signal: among flaw-mentioning reviews, the narrative satisfaction drivers that still appear in positive reviews.

Main outputs:

- Power BI PDF walkthrough: `dashboards/Narrative as a Satisfaction Buffer.pdf`
- Python notebooks and rebuild script: `notebooks/*sentiment_analysis.ipynb`, `scripts/rebuild_case2_narrative_assets.py`
- Aggregated narrative lift tables: `data/narrative_vs_nonnarrative.csv`, `data/narrative_lift_by_playtime_stable.csv`
- Compensation signal tables: `data/compensation_flaw_combined.csv`, `data/compensation_flaw_wide.csv`

### 3. Narrative Design Demo: The Mine and The Moon

A branching narrative design demo adapted from my original fiction and worldbuilding project. It explores choice, class conflict, evidence, resistance, and love under unequal power.

Main outputs:

- Main route playable prototype: [The Mine - Main Route Twine Prototype](https://astraaaqaq.itch.io/the-mine)
- Side route playable prototype: [The Moon - Side Route Twine Prototype](https://astraaaqaq.itch.io/the-moon)
- Main route flowchart: `narrative/main-route-flowchart.png`
- Side route flowchart: `narrative/side-route-flowchart.png`
- Narrative artifact notes: `narrative/README.md`

## Analysis Pipeline

Steam reviews -> cleaning and filtering -> sentiment proxy from recommendation labels -> playtime grouping or theme tagging -> aggregated evidence tables -> Power BI dashboard -> portfolio insight writing.

## Reproducibility

Install the lightweight analysis dependencies with:

```bash
pip install -r requirements.txt
```

Raw review-level datasets are excluded from this public repository. The repository includes code, aggregated tables, dashboard PDFs, playable prototype links, and selected design artifacts so that the portfolio argument can be reviewed without republishing large volumes of user-generated review text.

Full interactive Power BI dashboards are available upon request.

## Tools

- Python
- Power BI
- Steam review data
- Keyword and phrase-based theme tagging
- Twine
- Notion portfolio writing
