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

## Status in one line

The science and the packaging are ready; three things need a decision by the repository owners
before a PR can be opened: the licence (the repo currently grants inspection only, while ProteinGym
requires the model to be open source), whether the upstream kernel code can be published, and who
holds the GitHub credentials to open the PR with multi-gigabyte score files attached.
