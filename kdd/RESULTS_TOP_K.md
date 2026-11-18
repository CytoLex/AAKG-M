# Top-of-ranking utility

Spearman is a whole-list statistic. A wet lab assays tens of candidates out of thousands, so the
question that matters for practice is: if you take the top of our ranking, how much of the true top
do you actually get?

## Setup

For every assay × scheme unit, rank the variants by the published `fused` column, take the top
k ∈ {1%, 5%, 10%}, and count how many of them fall in the true top k by measured `DMS_score`. Scores
are then aggregated the official way: per assay over schemes, per UniProt id, per functional category,
mean over the five categories. 645 units contribute; ground truth is the official
`cv_folds_singles_substitutions` release.

## Result

| top of the list | recall of the true top | random expectation | lift |
|---|---:|---:|---:|
| 1% | **0.1192** | 0.0101 | **11.8x** |
| 5% | **0.2473** | 0.0499 | **4.96x** |
| 10% | **0.3504** | 0.1000 | **3.50x** |

A practitioner who orders the top 5% of candidates gets about a quarter of the true top 5% — roughly
five times what random ordering yields.

## Where it is trustworthy, and where it is not

Top 5%, by functional category:

| category | recall | random | lift |
|---|---:|---:|---:|
| Stability | **0.3837** | 0.0500 | 7.7x |
| Binding | 0.2435 | 0.0498 | 4.9x |
| OrganismalFitness | 0.2284 | 0.0500 | 4.6x |
| Expression | 0.2090 | 0.0498 | 4.2x |
| Activity | **0.1720** | 0.0499 | 3.4x |

The same ordering holds at the top 1%: Stability 0.2265, then Binding and Expression near 0.10,
OrganismalFitness 0.1008, Activity 0.0657.

**The ranker is roughly twice as good at prioritising stability mutants as activity mutants.** That is
the kind of statement a protein engineer can plan around, and it is invisible in the aggregate
Spearman.

## Reproduction

Scripts and the published per-mutant predictions are in `../submission/`. The computation needs only
`submission/predictions/fused_per_mutant.csv.gz` and the official DMS files; no training, no
proprietary tables.
