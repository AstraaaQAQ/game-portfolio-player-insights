# Aggregate data

Review-level text is private. Public tables contain counts, rates and descriptive comparisons.

## Case 1

The [source manifest](case1_provenance.json) pins one frozen cohort per game. See the [method](../docs/case1-method.md) and [revision audit](../docs/data-audit.md).

- [lifecycle_risk_map_pct.csv](lifecycle_risk_map_pct.csv): review, negative and positive counts; `negative_rate` is a fraction (0.45652 means 45.652%). Counts and rates come from the same cohort.
- `*_theme_by_playtime.csv`: unique negative reviews mentioning each theme divided by negative reviews in the same stage. Fraction and percent columns are labelled separately. Legacy alias columns are retained for compatibility.
- `*_theme_pattern_summary.csv`: stage peaks and pooled rates. Use `overall_rate_pct` for a pooled percentage; `average_rate_pct` is an unweighted stage average.
- `*_attachment_vs_friction_signals.csv`: theme mentions in 50h+ positive versus all negative reviews. Legacy `stayed_positive` columns do not measure continued activity. Groups have different playtime eligibility.
- [complaint_portfolio_matrix.csv](complaint_portfolio_matrix.csv): historical exploratory export, excluded from corrected reports and not claimed to share their cohort.

Full theme dictionaries are versioned in [the rebuild script](../scripts/rebuild_case1_assets.py). Mentions are not manually coded feature sentiment or validated causal drivers.

## Case 2

- [narrative_overall_combined_1.csv](narrative_overall_combined_1.csv): narrative mention and recommendation-rate summaries.
- [narrative_vs_nonnarrative.csv](narrative_vs_nonnarrative.csv): recommendation-rate comparison. Rates use a 0-100 percentage scale.
- [narrative_lift_by_playtime.csv](narrative_lift_by_playtime.csv): all playtime groups, including small late groups for audit. Empty comparison denominators yield blank rates and gaps.
- [narrative_lift_by_playtime_stable.csv](narrative_lift_by_playtime_stable.csv): 10-50h, 50-100h and 100-300h, including subgroup counts. The legacy word `stable` denotes the display subset, not a formal stability test.
- [narrative_by_category_combined.csv](narrative_by_category_combined.csv): overlapping keyword categories and their rates.
- [compensation_flaw_combined.csv](compensation_flaw_combined.csv) and [compensation_flaw_wide.csv](compensation_flaw_wide.csv): narrative co-occurrence among reviews with potential gameplay-issue keywords. These do not demonstrate causal compensation.

[Input hashes](case2_provenance.json) identify the frozen files. Narrative lift is an association, not a retention, re-engagement or marketing effect. Historical YouTube summary exports are not used in either corrected report.
