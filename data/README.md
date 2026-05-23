# Aggregated Data Tables

This folder contains selected aggregate tables used by the dashboard walkthroughs.

Raw review-level datasets are not included in this public portfolio repository.

## Steam Review Diagnostics by Playtime Stage

- `lifecycle_risk_map_pct.csv`: negative review rate by game and playtime group. Values are stored as rates, so `0.5966` means `59.66%`.
- `apex_theme_by_playtime.csv`, `icarus_theme_by_playtime.csv`, `poe_theme_by_playtime.csv`: negative theme mention rates by playtime stage.
- `apex_theme_pattern_summary.csv`, `icarus_theme_pattern_summary.csv`, `poe_theme_pattern_summary.csv`: peak-stage and persistence summaries for negative themes.
- `apex_attachment_vs_friction_signals.csv`, `icarus_attachment_vs_friction_signals.csv`, `poe_attachment_vs_friction_signals.csv`: stayed-positive versus negative theme mention rates used to separate attachment drivers, contested high-importance themes, friction drivers, and secondary signals.
- `complaint_portfolio_matrix.csv`: earlier positive and negative theme-count matrix kept for audit/reference.

## Narrative as a Satisfaction Buffer

- `narrative_overall_combined_1.csv`: narrative mention and positive-rate summary by game.
- `narrative_vs_nonnarrative.csv`: positive-rate comparison for narrative and non-narrative reviews. This table supports the narrative lift reading.
- `narrative_lift_by_playtime.csv`: full playtime-stage narrative lift table, including late groups kept for audit/reference.
- `narrative_lift_by_playtime_stable.csv`: stable playtime-stage narrative lift table used for portfolio conclusions. It keeps only `10-50h`, `50-100h`, and `100-300h` because later groups have small samples.
- `narrative_by_category_combined.csv`: post-play narrative satisfaction drivers by game: story/quest engagement, character attachment, world/genre immersion, emotional payoff, and theme/meaning.
- `compensation_flaw_combined.csv`: narrative satisfaction driver presence in positive versus negative flaw-mentioning reviews. This table supports the compensation signal reading.
- `compensation_flaw_wide.csv`: wide-format version of the same compensation signal comparison.
