# Add cytomuta-preview as a supervised substitution baseline

## What this adds

`cytomuta-preview` is a four-expert fusion with fixed weights, evaluated on the ProteinGym supervised
substitution benchmark under the official protocol.

| model | official average Spearman |
|---|---:|
| cytomuta-preview | **0.6917** |
| Kermut (current rank 1) | 0.6570 |
| ProteinNPT | 0.619 |
| MSA Transformer Embeddings | 0.581 |

## Why the number is trustworthy

Before submitting, the evaluation pipeline was validated against the published per-assay table:
recomputing Kermut's score from our tables reproduces `DMS_substitutions_Spearman_DMS_level.csv`
on **all 217 assays** with Pearson r = 0.999998, mean absolute difference 0.00026, max 0.0005
(the residual is the three-decimal rounding in the published CSV).

We also verified that our fold assignments are bit-identical to the published
`cv_folds_singles_substitutions` files (9,576/9,576 mutants on all three schemes for
`A0A140D2T1_ZIKV_Sourisseau_2019`).

## What is in the PR

- `proteingym/baselines/cytomuta/compute_fitness.py` — assembles the fused prediction from the
  per-assay student model and the two structural experts.
- `scripts/scoring_DMS_supervised/cytomuta_substitutions.sh` — end-to-end scoring plus the official
  performance script.

## Scope and disclosure

The method **fuses Kermut and AMK** (weights 0.40 each) with a distilled encoder (0.20); the additive
structure expert receives weight 0.00 and is not needed at scoring time. Kermut is therefore both a
component and a baseline, and the +0.035 over it measures what complementary experts add on top of
the strongest single model, not an independent single-model result.

The distilled encoder covers 182 of the 217 assays (it requires a wild-type sequence); the remaining
35 are scored by the older site expert. The aggregate is computed over all 217 under the official
aggregation.

## Coverage

217/217 assays match the official mutant counts exactly (696,311 mutants); every benchmarked mutant
receives a prediction. The distilled encoder covers 182 assays and the older site expert covers the
remaining 35.

## Reproducibility and licence

Method code is **Apache-2.0**. Weights and the structural-expert prediction tables are research-use
only under `LICENSE-WEIGHTS.md`; the code needed to reproduce every reported number is open, and
`submission/reproduce_official.sh` regenerates the leaderboard figures from two public repositories
plus `submission/raw_score_file.csv`.

Method code and evaluation records: https://github.com/CytoLex/AAKG-M
Project page: https://cytolex.com/cytomuta-preview/en/
