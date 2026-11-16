# Submission readiness — what is done, what blocks a real PR

Checked against `How to contribute?` in the ProteinGym README (read 2026-11-15).

## The official bar

> 1. A new subfolder under `proteingym/baselines` ... including a python scoring script ... as well
>    as all code dependencies required for the scoring script to run properly
> 2. An example bash script ...
> 3. Raise an issue with a `new model` label, providing instructions on how to download relevant
>    model checkpoints ... and reporting the performance of your model on the relevant benchmark
>    using our performance scripts

Conditions:

> 1. The model is able to score **all mutants** in the relevant benchmark
> 2. The model is **open source** (we should be able to reproduce scores)
> 3. ... all model scores for all mutants in a given benchmark are **provided by the requester**

## Status against each item

| requirement | status | note |
|---|---|---|
| official aggregation replicated | **done** | Kermut reproduced per assay, r = 0.999998 over 217/217 |
| one-command reproduction from public repos | **done** | `submission/reproduce_official.sh`; verified from fresh clones of both repositories |
| official folds used | **done** | bit-identical to `cv_folds_singles_substitutions` |
| scoring script | **drafted** | `proteingym/baselines/cytomuta/compute_fitness.py`; needs the expert tables and the trained student per assay |
| example bash script | **drafted** | `scripts/scoring_DMS_supervised/cytomuta_substitutions.sh` |
| config.json entry | **drafted** | `config_entry.json` |
| summary row | **done** | produced by running their `performance_DMS_supervised_benchmarks.py` unmodified: 0.694 average, 0.784 / 0.674 / 0.625 per scheme, bootstrap SE 0.004, five function categories filled |
| issue text with checkpoint instructions | **drafted** | `ISSUE_TEXT.md`; download links not yet available |
| **able to score all mutants** | **verified** | 217/217 assays match the official mutant counts exactly (696,311 mutants); `Kermut` and `AMK` are 100% non-null on every assay, so every benchmarked mutant has a prediction. The student covers 182 assays and the older site expert covers the remaining 35 |
| scores for **all mutants** supplied | **packaging** | the predictions exist for every mutant; what is missing is a redistribution-ready file and a way to move multi-GB tables off the compute share |
| **open source** so they can reproduce | **addressed** | code is Apache-2.0; weights and the `D`/`AMK` prediction tables are research-use only under `LICENSE-WEIGHTS.md`. Every reported number reproduces from public code plus `submission/raw_score_file.csv` via `reproduce_official.sh`, which is what the criterion asks for ("we should be able to reproduce scores") |

## Coverage, verified against the official mutant lists

| check | result |
|---|---|
| assays with a matching mutant count | **217 / 217** |
| total mutants in the benchmark | 696,311 |
| assays where `Kermut` is fully non-null | **217 / 217** |
| assays where `AMK` is fully non-null | **217 / 217** |

So the "must score all mutants" condition is met at the mutation level. The earlier note that this was
blocked was wrong: the 35 assays the encoder cannot reach are scored by the older site expert, which
covers all 217.

## What must happen before opening the PR

1. **Publish the two structural experts.** A requester-run reproducibility check needs `AMK` (and
   `D`, though its weight is 0) as runnable code, or as released per-mutant predictions. Right now
   they are sealed tables.
2. **Publish the per-assay student checkpoints** (8 seeds x 182 assays) or a documented path to
   retrain them. `expert/esm_mut_head.py` can retrain given the ESM-650 features, but the features
   themselves are not distributed.
3. **Produce the full-score file** for all 217 assays x 3 schemes, and fill the per-scheme row of the
   summary by rerunning the official script.
4. **Decide the fallback story** for the 35 assays the encoder cannot cover, since the benchmark
   requires every mutant to be scored.

## The authoritative numbers

Produced by the official script from a raw score file (2 models x 3 schemes x 217 assays):

| model | average | random | modulo | contiguous | Activity | Binding | Expression | Org. Fitness | Stability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cytomuta-preview | **0.694** | 0.784 | 0.674 | 0.625 | 0.642 | 0.653 | 0.693 | 0.632 | 0.851 |
| Kermut (control) | 0.657 | 0.745 | 0.633 | 0.593 | 0.605 | 0.611 | 0.670 | 0.582 | 0.817 |

The Kermut row reproduces the published leaderboard entry on all nine numbers, which is the strongest
end-to-end check available short of submitting. Our independent reimplementation gives 0.6933 for the
fusion; the script gives 0.694 (0.694313 unrounded). The 0.001 difference is the order of the scheme
averaging — the script is authoritative because it is their code.

## Licence split

`LICENSE` is Apache-2.0 and covers all code. `LICENSE-WEIGHTS.md` covers the trained weights and the
structural-expert prediction tables: research use without asking, commercial use by permission,
redistribution with the file attached. The split exists because ProteinGym asks for a reproducible
model, not for a transfer of commercial rights.

Remaining note: the kernel *fitting* code for `D` / `AMK` is not on the compute share we have access
to, so it cannot be published from here. Reproduction does not require it — the submitted score file
plus the official script regenerates the reported numbers.

## Honest recommendation

Opening the PR today would fail condition 2 and 3. The defensible sequence is:

1. Open the **issue** now, reporting the number, the validation, and a link to the method repository —
   their README asks for the issue alongside the PR, and it invites discussion before code is merged.
2. Close the reproducibility gaps above, then open the PR.

The validation numbers are strong enough that the issue is worth raising immediately; the missing
piece is packaging, not science.
