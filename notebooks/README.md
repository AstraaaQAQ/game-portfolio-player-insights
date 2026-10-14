# Notebooks

All six notebooks have empty saved outputs and null execution counts. Every notebook opens with a method note covering question, source, filters, playtime definition, outputs, rebuild command and limitations.

## Historical exploration and the published snapshot

The notebooks preserve exploratory code. Some cells call Steam or YouTube, use older matching rules, or assume a local folder. Running all cells can produce a new dataset. The opening notes describe the **current report method** and link to its canonical offline script; they do not claim every historical cell reproduces current tables.

Use a separate private folder for historical cells. Do not commit generated review-level files.

| Case | Historical notebooks | Canonical rebuild |
| --- | --- | --- |
| 1 | [Apex](APEX_retention_analysis.ipynb), [Icarus](Icarus_retention_analysis.ipynb), [PoE](PoE_retention_analysis.ipynb) | [Case 1 script](../scripts/rebuild_case1_assets.py) |
| 2 | [God of War](GoW_sentiment_analysis.ipynb), [RDR2](RD2_sentiment_analysis.ipynb), [The Witcher 3](Witcher3_sentiment_analysis.ipynb) | [Case 2 script](../scripts/rebuild_case2_narrative_assets.py) |

The Case 1 filenames retain `retention_analysis` for link compatibility. The measured outcome is a review recommendation label, not retention.

See [aggregate definitions](../data/README.md), [Case 1 methodology](../docs/case1-method.md) and the [audit](../docs/data-audit.md).
