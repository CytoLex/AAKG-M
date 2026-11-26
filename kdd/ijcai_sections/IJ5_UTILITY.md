The preceding sections argue about where gain comes from. This one asks what the ranker is worth — on the
benchmark's own terms, on the terms a laboratory uses, and where it does not help.

## 5.1 Measuring it the way the leaderboard measures it

We run the official `performance_DMS_supervised_benchmarks.py` unmodified on a score file of our
per-assay, per-scheme correlations, and as a control we run the same correlations recomputed from
Kermut's predictions. The control reproduces the published per-assay table on **217 of 217 assays** to the precision that table
is published at: mean absolute difference **0.00026**, maximum **0.0005**, every residual inside the
released file's three-decimal rounding. Our folds are bit-identical to the released distribution.

| model | official | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| Kermut (published rank 1) | 0.657 | 0.746 | 0.633 | 0.593 |
| our fusion | **0.692** | 0.778 | 0.671 | 0.626 |

Kermut is one of the four experts, so this is a fusion result and we report it as such: +0.035 is what adding
complementary experts to the strongest published single model is worth, and every scheme improves.

## 5.2 The aggregate hides the category, and the top of the list

Per functional category:

| category | ours | Kermut | delta |
|---|---:|---:|---:|
| Stability | **0.850** | 0.817 | +0.033 |
| Expression | 0.697 | 0.670 | +0.026 |
| Binding | 0.655 | 0.619 | +0.036 |
| Activity | **0.644** | 0.610 | +0.034 |
| OrganismalFitness | 0.636 | 0.597 | +0.040 |

Every category improves, and the spread is the part that matters downstream: 0.850 against 0.644 is a
0.21 gap, so a laboratory working on an activity assay is operating at the bottom of the range we report.

Spearman is a whole-list statistic. A campaign has a library and can assay tens of candidates, so the
question is whether the top of our ranking contains the top of the true ranking. For each assay and split
we take the top *k* ∈ {1%, 5%, 10%} and measure how many land in the true top *k*, aggregating the
official way:

| top of the list | recall of the true top | lift over random |
|---|---:|---:|
| 1% | **0.115** [0.104, 0.126] | **11.5x** [10.4x, 12.6x] |
| 5% | **0.241** [0.226, 0.254] | **4.82x** [4.52x, 5.08x] |
| 10% | **0.346** [0.333, 0.358] | **3.46x** [3.33x, 3.58x] |

Intervals are bootstrap over assays, and the values are computed from the same released per-mutant predictions as
§5.1: a reader re-running them gets these numbers.

Ordering the top 5% recovers about a quarter of the true top 5%, roughly five times random. It is also
category-dependent in the direction the table above predicts: **7.8x on Stability**, 4.3x OrganismalFitness, 4.3x
Expression, 4.2x Binding, and **3.4x on Activity** — and activity is what
function-oriented campaigns care about. **The ranker is roughly twice as good at prioritising stability mutants as
activity mutants**, and the intervals separate.

Ranking and ground truth are computed within an assay-by-split unit on the released files, so the reference is
independent of §4; the lift, not the raw recall, is what compares across categories.

## 5.3 The operating range

**87 of 217 assays regress** against the previous four-expert fusion, with a median improvement of
+0.0016 — roughly half the mean, so the gain is carried by a subset. **Expression is the only category
that regresses on average** (−0.0018).

**The effect disappears on large assays.**

| quartile of mutant count | mean delta | regression rate |
|---|---:|---:|
| smallest | **+0.0073** | 0.255 |
| second | +0.0017 | 0.444 |
| third | +0.0024 | 0.407 |
| **largest** | **+0.00003** | 0.500 |

The size regime is part of the method's specification, not a footnote: the gain is concentrated in assays with
fewer measurements and vanishes on the largest quartile. It is a property of the correlation estimate rather than
of the feature budget, since the baseline has more data there too.

**Coverage is partial and coupled.** The encoder needs a wild-type sequence and covers 182 of 217 assays; the other
35 fall back to an older expert and still show +0.0029, though not from their own predictions — the nested weight
search fits one vector per fold over all training assays, so replacing the expert elsewhere moves the weights
applied to them.
