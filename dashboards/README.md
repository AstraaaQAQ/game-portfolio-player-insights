# Reports and Power BI source status

- [Case 1 report](Steam%20Review%20Diagnostics%20by%20Playtime%20Stage.pdf)
- [Case 2 report](Narrative%20as%20a%20Satisfaction%20Buffer.pdf)

Current static PDFs are generated from reconciled tables by [render_reports.py](../scripts/render_reports.py). Original Power BI files were inspected as historical sources; their embedded models have not been refreshed.

## Refreshing Power BI later

Use copies of original PBIX files and preserve the originals.

1. Point Case 1 review queries to the corresponding frozen files in `private_data/case1`. Expected totals: Apex 1,393; Icarus 1,445; PoE 1,496. Do not mix later desktop exports into this snapshot.
2. Point aggregate queries to corrected `data/` files. Map query `lifecycle_risk_map_pct_1` to `lifecycle_risk_map_pct.csv`. Update explicit CSV column-count and type steps for added columns.
3. Group cumulative `playtime_hours` using `<10`, `<50`, `<100`, `<300`, `<1000` consistently. Do not label this playtime at review.
4. Use `overall_rate_pct` for pooled theme bars. Label `average_rate_pct` explicitly if retaining an unweighted stage average. Replace old attachment/friction quadrant interpretations with descriptive group comparisons.
5. Use revised report text and limitations. Case 2 needs regenerated timing tables and blank rates for empty comparison groups.
6. Refresh and verify counts, denominators, exact-50h boundaries and all chart labels before exporting. Native Power BI refresh has not been tested in this repair.
