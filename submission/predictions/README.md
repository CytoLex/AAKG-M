# Per-mutant predictions

`fused_per_mutant.csv.gz` — the fused prediction for **every mutant in the ProteinGym supervised
substitution benchmark**.

| column | meaning |
|---|---|
| `assay` | ProteinGym `DMS_id` |
| `scheme` | one of `fold_random_5`, `fold_modulo_5`, `fold_contiguous_5` |
| `variant_id` | mutation string, e.g. `I291A` |
| `fused` | `0.40·Kermut_z + 0.40·AMK_z + 0.20·X_z`, z-scored within each assay × scheme, clipped to ±8 |

**Coverage:** 2,088,933 rows = 696,311 mutants × 3 schemes, over all 217 assays. Every official
mutant receives a prediction; the 35 assays outside the distilled encoder's reach are scored by the
older site expert, exactly as in the fusion used for the reported numbers.

## What it is for

ProteinGym asks a submitter to provide all model scores for all mutants. This file is that artifact.
Spearman is rank-based within each assay × scheme, so the z-scored `fused` column can be ranked
directly.

## How it was produced

`expert/` trains the distilled encoder; the two structural experts come from the research-use tables
described in `../data/README.md`; the weights are the fixed `(0, 0.40, 0.40, 0.20)` selected per fold.
The aggregation that turns per-assay Spearman into the reported 0.694 is the official
`performance_DMS_supervised_benchmarks.py`, run by `../reproduce_official.sh`.
