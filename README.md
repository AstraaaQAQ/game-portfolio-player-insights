# Game Portfolio: Player Insights and Narrative Design

This repository contains selected public-facing materials from my game portfolio. It combines player sentiment analysis, Power BI dashboard walkthroughs, playable Twine prototypes, and branching narrative design documentation.

## Projects

### 1. Steam Review Diagnostics by Playtime Stage

Steam review analysis of Apex Legends, Icarus, and Path of Exile, focused on how public player feedback changes across playtime stages and what keeps players attached despite friction. This case highlights early friction, entry into system depth, later-stage trust concerns, and the difference between attachment drivers and friction signals.

Key questions:

> Where does negative sentiment appear by playtime stage?
>
> Which complaint themes persist or intensify over time?
>
> What keeps stayed-positive players attached despite friction?

Main outputs:

- Power BI PDF walkthrough: `dashboards/Steam Review Diagnostics by Playtime Stage.pdf`
- Python notebooks: `notebooks/*retention_analysis.ipynb`
- Aggregated playtime-stage, theme, and attachment/friction tables: `data/lifecycle_risk_map_pct.csv`, `data/*_theme_by_playtime.csv`, `data/*_theme_pattern_summary.csv`, `data/*_attachment_vs_friction_signals.csv`

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
