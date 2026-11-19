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

The claim is a *fusion* claim and we state it plainly: Kermut is one of our four experts. The +0.037
measures what adding complementary experts on top of the strongest single model is worth, not what a new
standalone model achieves. A reader wanting the equal-compute statement should take the single-model rung.

## 5.2 The aggregate hides the category, and the top of the list

Per functional category, our fusion scores 0.851 on Stability, 0.693 on Expression, 0.653 on Binding,
0.642 on Activity and 0.632 on OrganismalFitness, against 0.817, 0.670, 0.611, 0.605 and 0.582 for
Kermut. Every category improves, which is the least interesting part. The spread matters: 0.851 against
0.642 is a gap of 0.21 that the aggregate conceals entirely.

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
category-dependent, in the direction §5.2 predicts: 7.7x on Stability, 4.9x Binding, 4.6x
OrganismalFitness, 4.2x Expression, and **3.4x on Activity** — and activity is what function-oriented
campaigns care about. **The ranker is roughly twice as good at prioritising stability mutants as
activity mutants.**

Ranking and ground truth are both computed within an assay-by-split unit on the released DMS files, so
the reference is independent of §4, and the lift rather than the raw recall is the quantity to compare
across categories.

## 5.3 Where it fails

**87 of 217 assays regress** against the previous four-expert fusion, with a median improvement of
+0.0016 — roughly half the mean, so the gain is carried by a subset. **Expression is the only category
that regresses on average** (−0.0018).

**The effect disappears on large assays.** By quartile of mutant count, the mean delta is +0.0073 on the
smallest, +0.0017, +0.0024, and **+0.00003 on the largest**, with a 50% regression rate there. This is
the sharpest honest limitation: the assays with the most measurements — the ones a serious campaign is
most likely to run — are exactly where the method is at parity with its predecessor. It is not simply a
sample-size effect in the correlation estimate, since the baseline has more data there too.

**Coverage is partial and coupled.** The encoder needs a wild-type sequence and covers 182 of 217 assays;
the other 35 fall back to an older expert, and still show +0.0029 — but not because of their own
predictions: the nested weight search fits one vector per fold over all training assays, so replacing the
expert elsewhere moves the weights applied to them.
