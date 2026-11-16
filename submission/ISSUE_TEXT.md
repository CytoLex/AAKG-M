# [new model] cytomuta-preview — supervised substitutions

**Model name:** cytomuta-preview
**Benchmark:** supervised substitutions
**Average Spearman (official aggregation):** 0.694  (single-model rung: 0.692)

## Method

Four experts with fixed weights: `0.40 Kermut + 0.40 AMK + 0.20 X`, where `X` is a distilled
ESM-650 encoder trained per assay on the assay's fold column, with a category-specific rank-8 linear
residual, and its predictions averaged over eight training seeds. The additive-structure expert gets
weight 0.00 in 14 of 15 (seed x fold) combinations and is not required at scoring time.

## Validation performed before submitting

- Recomputing Kermut through our pipeline reproduces `DMS_substitutions_Spearman_DMS_level.csv` on
  217/217 assays: Pearson r = 0.999998, mean |diff| = 0.00026, max |diff| = 0.0005.
- Fold columns are bit-identical to `cv_folds_singles_substitutions` (9,576/9,576 mutants, three
  schemes, `A0A140D2T1_ZIKV_Sourisseau_2019`).
- Aggregation follows `performance_DMS_supervised_benchmarks.py` including the `UniProt_ID` grouping.

## Checkpoints and code

Method code is Apache-2.0; the expert prediction tables are research-use only under the repository's
`LICENSE-WEIGHTS.md`. Reproduction of every number requires only the public code plus the score file
in `submission/`, not the tables.

Method code, expert provenance and evaluation records: https://github.com/CytoLex/AAKG-M
Project page: https://cytolex.com/cytomuta-preview/en/

## Coverage

Every mutant in the benchmark is scored: 217/217 assays match the official mutant counts exactly
(696,311 mutants), and the two frozen experts are fully non-null on all 217 assays. The distilled
encoder covers 182 assays; the remaining 35 are scored by an older site expert.

## Disclosure

Kermut is one of the fused experts, so the +0.037 over it is a fusion gain rather than an independent
single-model result.
