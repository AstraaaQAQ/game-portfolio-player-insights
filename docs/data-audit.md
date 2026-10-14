# Data reconciliation - 14 October 2026

## Case 1

The Apex 0-10h row combined **128 reviews** from an older export with **45.65%** from a different snapshot. The old backup has 70 negative reviews out of 128 (54.6875%). The Power BI report's embedded review table has **63 negative reviews out of 138**, or **45.6521739%**.

The embedded review tables were recovered and grouped independently. The corrected public table now includes negative and positive counts alongside each rate.

| Item | Previous presentation | Correction |
| --- | --- | --- |
| Apex 0-10h | n=128, 45.65% | n=138, negative=63, 45.65% |
| Apex total | Counts totalled 1,386; rates came from another cohort | Counts and rates from 1,393 frozen reviews |
| Icarus recommendation table | 1,445 reviews | Reproduced from the same cohort |
| PoE total | Counts totalled 1,494; rates used a 1,496-review cohort | Rebuilt from 1,496 reviews |
| PoE exact-50h boundary | One review in 10-50h | Shared lower-inclusive convention moves it to 50-100h; the rates become 14.40% and 13.76% |
| Playtime wording | "Playtime at review" | Cumulative playtime at collection |
| Theme/comparison tables | Mixed versions and incomplete rule provenance | Explicit dictionary v2 and one cohort per game |

Some theme rates and peak stages change. This is a documented reanalysis, not a claim to recover missing historical rules. The report, tables and script now share definitions.

## Case 2

The three frozen inputs each have 5,000 unique reviews meeting the 10-hour and 20-word minimums. An offline run reproduced the six existing aggregate tables within their stored rounding. The displayed early-to-mid table is now regenerated too.

One numerical edge case was fixed: God of War's 1000h+ group has three narrative reviews and **zero** non-narrative reviews. Its old 0% non-narrative rate and 100 pp gap were undefined. Both are now blank. This group was already excluded from the main chart.

The report now states that narrative mentions **were associated with higher positive recommendation rates**. Retention, re-engagement and story-beat timing claims were replaced by observed associations and proposed content tests. The offline option fails on missing inputs instead of silently collecting new reviews.

## Notebooks, navigation and artifact status

Six notebooks now have consistent method notes, no saved outputs and null execution counts. The homepage has direct report links, previews, playable entries and project delivery notes.

The current PDFs are static Python-rendered walkthroughs of the audited data, retaining 11 pages for Case 1 and five for Case 2. They are not presented as newly exported live Power BI reports. Original PBIX and private source files remain historical originals; editing CSVs/PDFs does not update their embedded models. See [Power BI refresh notes](../dashboards/README.md).

The separate Notion pages and itch.io builds were not edited in this repository repair.
