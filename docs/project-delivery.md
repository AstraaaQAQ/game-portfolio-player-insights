# Project delivery notes

These are independent portfolio projects. The notes describe work evidenced in the artifacts, without claiming a client engagement, team-management role, production deployment or measured commercial impact.

## Case 1 - Steam review diagnostics

**Goal:** turn public review language and recommendation labels into specific player-experience questions.

**Scope:** three games, six cumulative-playtime groups, rule-based themes and 50h+ positive versus negative review comparisons. Internal retention and campaign outcomes are outside the data.

**Contribution and outputs:** Python aggregation, dashboard interpretation, aggregate CSVs, an 11-page report, method documentation and an offline rebuild.

**Key decisions:** measure recommendation labels; preserve fixed cohorts; show numerators and denominators; separate findings from product hypotheses; keep review-level text private.

**Revision process:** an impossible count/rate pair was traced to mixed exports. Embedded review snapshots were recovered, group boundaries standardized, explicit theme rules published and dependent figures rebuilt. Validation connects stage rates, theme denominators and cohort totals.

## Case 2 - Narrative associations

**Goal:** investigate narrative mentions and their association with recommendation labels.

**Scope:** 5,000 eligible reviews each for God of War, RDR2 and The Witcher 3; five narrative categories; overall and playtime-group comparisons. Gameplay-issue keywords are not manually validated complaints.

**Contribution and outputs:** filtering/tagging code, subgroup comparisons, aggregate tables, a five-page report and hypotheses for future content testing.

**Key decisions:** require 10+ cumulative hours and 20+ English words; show separate baselines; keep small late-playtime groups out of the main chart; define lift as a percentage-point association.

**Revision process:** frozen-input rebuilding reproduced main results. Retention and re-engagement wording was removed, empty-group rates marked unavailable, and missing offline inputs made explicit errors.

## The Mine and The Moon

**Goal:** turn original fiction into playable choices whose consequences reflect what characters value under pressure.

**Scope:** two Twine narrative slices, documented routes and endings, and Figma flowcharts. This is a prototype scope, not a commercial release.

**Contribution and outputs:** original worldbuilding and writing, choice/consequence logic, hidden alignment variables, two browser-playable prototypes and design documentation.

**Key decisions:** connect earlier actions to the final appeal through Leverage, Spark and Solidarity in The Mine; use Mara's perspective to explore possession, release and rebellion in The Moon.

**Revision process:** repository history records revised A/B ending directions, added side-route framing and removal of duplicate ending text. These clarify consequences and the route through the design. No external playtest results are claimed.

[Return to the finished work](../README.md)
