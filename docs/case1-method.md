# Case 1 method

## Frozen cohort

The audited snapshot is recovered from review tables embedded in the original Power BI file. This preserves the cohorts behind the published recommendation-rate charts rather than combining later desktop exports with older rates.

| Game | All reviews | Negative reviews | Positive reviews with 50h+ |
| --- | ---: | ---: | ---: |
| Apex Legends | 1,393 | 476 | 628 |
| Icarus | 1,445 | 288 | 899 |
| Path of Exile | 1,496 | 256 | 1,081 |

Private input filenames and SHA-256 hashes are in [the manifest](../data/case1_provenance.json). A hash identifies the exact CSV, not a collection date. The inputs inherit the original English-review selection. Apex and Icarus exploration also used an ASCII-letter/whitespace heuristic, which is not a reliable language classifier. No additional language filter was applied during reconciliation.

## Definitions

- Playtime is cumulative time at collection, `playtime_forever / 60`, not `playtime_at_review`.
- Intervals are `[0,10)`, `[10,50)`, `[50,100)`, `[100,300)`, `[300,1000)` and `[1000,infinity)`. Exactly 50h belongs to 50-100h.
- Reviews have equal weight; `weighted_vote_score` is not used.
- Negative rate = negative reviews / all reviews in the same game, snapshot and group.
- Negative theme rate = negative reviews mentioning a theme / all negative reviews in that group.
- The report's overall theme rate pools mention counts and denominators. `average_rate_pct` retains the unweighted stage average for compatibility; the report uses `overall_rate_pct`.
- Legacy `stayed_positive` columns mean positive reviews with 50+ cumulative hours. They do not track repeated recommendations or continued activity.

## Explicit dictionary v2

The original repository did not include the complete dictionaries that generated its theme exports. Some tables also used different snapshots and playtime definitions. Version 2 recalculates those tables with explicit rules rather than claiming to reproduce undocumented historical tags.

Complete rules are the `THEMES` and `ATTACHMENT` constants in [the rebuild script](../scripts/rebuild_case1_assets.py). Text is lowercased, hyphens and whitespace normalized, and terms matched at word boundaries. A review counts at most once per theme and can match multiple themes. Rules were not tuned to recover the old numbers.

Matches identify mentions. Negative reviews can praise a matched feature and positive reviews can criticise it. Negation, sarcasm and unmatched synonyms are not resolved. No manually labelled validation set was created, so classifier accuracy is unknown. Use flags to locate topics for qualitative reading, not to identify causes of dissatisfaction.

`signal_type` now states which comparison group has the higher mention rate, without labelling validated attachment/friction drivers. `active_stage_count` uses a descriptive 10% threshold, not a significance test. `positive_share` is the positive subset's share of combined mention counts, not a population recommendation rate.

## Validation and limits

Rebuilds require unique IDs, non-empty text, valid recommendation labels and finite non-negative playtime. The validator reconciles counts, rates, theme denominators and cohort totals. Unavailable denominators produce blank rates.

Self-selected reviewers do not represent the full player population. Groups contain different people and do not establish retention, churn, re-engagement or change in an individual's sentiment. Small groups, especially Icarus's six negative reviews at 1000h+, cannot support strong peak-stage claims. Product and marketing suggestions remain hypotheses.
