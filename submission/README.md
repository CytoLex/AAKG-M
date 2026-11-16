# ProteinGym submission package

Everything needed to submit cytomuta-preview to the ProteinGym supervised substitution benchmark,
plus an honest statement of what is still missing.

| file | what it is |
|---|---|
| `proteingym/baselines/cytomuta/compute_fitness.py` | the scoring script the PR would add |
| `scripts/scoring_DMS_supervised/cytomuta_substitutions.sh` | the example bash script the PR would add |
| `config_entry.json` | the `config.json` entry for the supervised model list |
| `summary_row.csv` | the row produced by running the official performance script |
| `PR_DESCRIPTION.md` | ready-to-paste pull-request text |
| `ISSUE_TEXT.md` | ready-to-paste "new model" issue text |
| `SUBMISSION_READINESS.md` | item-by-item status against the official requirements |
| `raw_score_file.csv` | 1,302 rows: per-assay, per-scheme Spearman for cytomuta-preview **and** Kermut, the exact input to the official script |
| `reproduce_official.sh` | clones ProteinGym and re-runs their script on that file — no GPU, no cluster, no proprietary tables |
| `test_scoring.py` | smoke test: checks the scoring script really computes `0.4·K_z + 0.4·A_z + 0.2·X_z` |
| `official_outputs/` | what the script writes: the DMS-level tables (overall and per scheme) and the summary row, i.e. the exact files a merged PR would carry |

## The numbers, as their own script reports them

Produced by running `proteingym/performance_DMS_supervised_benchmarks.py` unmodified on a raw score
file of 2 models × 3 schemes × 217 assays:

| model | average | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| cytomuta-preview (8-seed expert) | **0.694** | 0.784 | 0.674 | 0.625 |
| cytomuta-single (one seed) | **0.692** | 0.782 | 0.671 | 0.624 |
| Kermut (control) | 0.657 | 0.745 | 0.633 | 0.593 |

The control row reproduces the published Kermut entry on all nine numbers (average, three schemes,
five function categories), which is the strongest available check short of submitting.

## Reproducing the number from scratch

```bash
cd submission && python test_scoring.py      # the fusion arithmetic
cd submission && ./reproduce_official.sh     # the headline number
```

The script clones the official repository, runs `performance_DMS_supervised_benchmarks.py` unmodified
on `raw_score_file.csv`, and prints the summary. Because Kermut's column is in the same file, the run
also exercises the control row.

**Verified end to end** from a fresh clone of this repository plus a fresh clone of ProteinGym:

```text
Model_rank,Model_name,Model type,Average_Spearman,...,random,modulo,contiguous
1,cytomuta-preview,,0.694,...,0.784,0.674,0.625
2,Kermut,Structure & sequence embedding,0.657,...,0.745,0.633,0.593
```

The Kermut row reproduces the published leaderboard entry, including its model type string, which
only appears when the official `constants.json` is used rather than a stub. That is the check that
makes the reproduction meaningful: if our aggregation were wrong, the control row would move.

## The output files a merged PR would carry

`official_outputs/` holds the script's own outputs, unedited:

| file | content |
|---|---|
| `DMS_substitutions_Spearman_DMS_level.csv` | 217 rows: per-assay score for cytomuta-preview and Kermut |
| `..._fold_random_5.csv`, `..._fold_modulo_5.csv`, `..._fold_contiguous_5.csv` | the same split by scheme |
| `Summary_performance_DMS_substitutions_Spearman.csv` | the one-row summary that would be appended to the leaderboard table |

Cross-check: our generated Kermut column is **identical to the published
`benchmarks/DMS_supervised/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv` on 217 of
217 assays** (mean absolute difference 0.0, three-decimal table). Running the pipeline end to end
therefore reproduces the published per-assay values, not just the aggregate.

## Submission status

**Issue opened:** https://github.com/OATML-Markslab/ProteinGym/issues/129 —
`[new model] cytomuta-preview — supervised substitutions`, posted 2026-11-16.

The label could not be attached: GitHub only lets repository maintainers set labels, so the
`[new model]` prefix in the title carries that information instead.

The pull request is prepared but not opened. Their README asks for the PR and the issue together, but
the scoring script cannot run without the expert prediction tables, and those are research-use only.
Whether a score-file reproduction is enough is exactly what the issue asks.

## Status in one line

The science and the packaging are ready; three things need a decision by the repository owners
before a PR can be opened: the licence (the repo currently grants inspection only, while ProteinGym
requires the model to be open source), whether the upstream kernel code can be published, and who
holds the GitHub credentials to open the PR with multi-gigabyte score files attached.
