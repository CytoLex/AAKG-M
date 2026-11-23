The preceding sections argue about where gain comes from. This one asks what the ranker is worth — on the
benchmark's own terms, on the terms a laboratory uses, and where it does not help.

## 5.1 Measuring it the way the leaderboard measures it

We run the official `performance_DMS_supervised_benchmarks.py` unmodified on a score file of our
per-assay, per-scheme correlations, and as a control we run the same correlations recomputed from
Kermut's predictions. The control reproduces the published per-assay table on **217 of 217 assays** with
mean absolute difference **0.0**, the residual being the published table's three-decimal rounding, and
our folds are bit-identical to the released distribution.

| model | official | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| Kermut (published rank 1) | 0.657 | 0.745 | 0.633 | 0.593 |
| our fusion, single model | **0.691** | 0.782 | 0.671 | 0.624 |
| our fusion, seed-averaged | **0.694** | 0.784 | 0.674 | 0.625 |

Kermut is one of the four experts, so this is a fusion result and we report it as such: +0.037 is what
adding two complementary experts to the strongest published single model is worth. The equal-compute
comparison is the single-model rung above — one trained expert instead of eight averaged ones — which
still leads Kermut by 0.034.

## 5.2 The aggregate hides the category, and the top of the list

Per functional category:

| category | ours | Kermut | delta |
|---|---:|---:|---:|
| Stability | **0.851** | 0.817 | +0.034 |
| Expression | 0.693 | 0.670 | +0.023 |
| Binding | 0.653 | 0.611 | +0.042 |
| Activity | **0.642** | 0.605 | +0.037 |
| OrganismalFitness | 0.632 | 0.582 | +0.050 |

Every category improves, and the spread is the part that matters downstream: 0.851 against 0.642 is a
0.21 gap, so a laboratory working on an activity assay is operating at the bottom of the range we report.

Spearman is a whole-list statistic. A campaign has a library and can assay tens of candidates, so the
question is whether the top of our ranking contains the top of the true ranking. For each assay and split
we take the top *k* ∈ {1%, 5%, 10%} and measure how many land in the true top *k*, aggregating the
official way:

| top of the list | recall of the true top | random | lift |
|---|---:|---:|---:|
| 1% | **0.119** | 0.010 | **11.8x** |
| 5% | **0.247** | 0.050 | **4.96x** |
| 10% | **0.350** | 0.100 | **3.50x** |

Ordering the top 5% recovers about a quarter of the true top 5%, roughly five times random. It is also
category-dependent, in the direction the category table above predicts: 7.7x on Stability, 4.9x Binding, 4.6x
OrganismalFitness, 4.2x Expression, and **3.4x on Activity** — and activity is what function-oriented
campaigns care about. **The ranker is roughly twice as good at prioritising stability mutants as
activity mutants.**

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

The size regime is therefore part of the method's specification rather than a footnote: the gain is
concentrated in assays with fewer measurements, and on the largest quartile the fusion matches its
predecessor. This is a property of the correlation estimate rather than of the feature budget, since the
baseline has more data there too, and it tells a reader which assays to expect an improvement on.

**Coverage is partial and coupled.** The encoder needs a wild-type sequence and covers 182 of 217 assays;
the other 35 fall back to an older expert, and still show +0.0029 — but not because of their own
predictions: the nested weight search fits one vector per fold over all training assays, so replacing the
expert elsewhere moves the weights applied to them.
