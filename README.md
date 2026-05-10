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

Steam review analysis of God of War, Red Dead Redemption 2, and The Witcher 3, focused on whether narrative elements help players remain positive when they also mention gameplay friction.

Key question:

> Can narrative elements act as a satisfaction buffer when players also mention gameplay friction?

Main outputs:

- Power BI PDF walkthrough: `dashboards/Narrative as a Satisfaction Buffer.pdf`
- Python notebooks and rebuild script: `notebooks/*sentiment_analysis.ipynb`, `scripts/rebuild_case2_narrative_assets.py`
- Aggregated narrative and compensation tables: `data/narrative_*.csv`, `data/compensation_flaw_combined.csv`

### 3. Narrative Design Demo: The Mine and The Moon

A branching narrative design demo adapted from my original fiction and worldbuilding project. It explores choice, class conflict, evidence, resistance, and love under unequal power.

Main outputs:

- Main route playable prototype: [The Mine - Main Route Twine Prototype](https://astraaaqaq.itch.io/the-mine)
- Side route playable prototype: [The Moon - Side Route Twine Prototype](https://astraaaqaq.itch.io/the-moon)
- Main route flowchart: `narrative/Main-Route-Flowchart.png`
- Side route flowchart: `narrative/Side-Route-Flowchart.png`

## Analysis Pipeline

Steam reviews -> cleaning and filtering -> sentiment proxy from recommendation labels -> playtime grouping or theme tagging -> aggregated evidence tables -> Power BI dashboard -> portfolio insight writing.

## Public Data Note

This repository intentionally includes only code, aggregated tables, dashboard PDFs, playable prototype links, and selected design artifacts. Raw review datasets are excluded from the public repository to keep the portfolio clean and avoid republishing large volumes of user-generated review text.

Full interactive Power BI dashboards are available upon request.

## Tools

- Python
- Power BI
- Steam review data
- Keyword and phrase-based theme tagging
- Twine
- Notion portfolio writing
