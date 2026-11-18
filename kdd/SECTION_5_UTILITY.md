# §5 What the ranker is worth

Camera-ready draft, English, ~1350 words. All numbers from the official performance script and the
analyses in this directory.

---

## 5.1 Measuring it the way the leaderboard measures it

Before any claim, the measurement itself has to be trustworthy. We run the official
`performance_DMS_supervised_benchmarks.py` unmodified on a score file containing our per-assay,
per-scheme correlations for the 217 assays — and, as a control, the same correlations recomputed from
Kermut's \cite{kermut} predictions through our pipeline. The control row reproduces the published
leaderboard entry on
all nine of its numbers: the average, the three cross-validation schemes, and the five functional
categories.

At the per-assay level the agreement is stronger still: our recomputed Kermut column matches the
published `DMS_substitutions_Spearman_DMS_level.csv` on **217 of 217 assays** with mean absolute
difference **0.0**. The numbers below are on the leaderboard's scale, computed by its own code.

## 5.2 The headline, and what it is a headline of

| model | official average | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| ProteinNPT (published rank 2) | 0.619 | | | |
| **Kermut \cite{kermut} (published rank 1)** | **0.657** | 0.745 | 0.633 | 0.593 |
| our fusion, single model | **0.691** | 0.782 | 0.671 | 0.624 |
| **our fusion, seed-averaged expert** | **0.694** | 0.784 | 0.674 | 0.625 |

**+0.037 over the published leader, +0.0085 over the previous four-expert fusion.**

The claim is a *fusion* claim and we state it plainly: Kermut is one of our four experts. The +0.037
measures what adding complementary experts on top of the strongest single model is worth, not what a new
standalone model achieves. A reader who wants the equal-compute statement should take the single-model
rung, which uses one trained expert rather than eight averaged ones.

## 5.3 The aggregate hides the category

Per functional category, official aggregation:

| category | ours | Kermut | delta |
|---|---:|---:|---:|
| Stability | **0.851** | 0.817 | +0.034 |
| Expression | 0.693 | 0.670 | +0.023 |
| Binding | 0.653 | 0.611 | +0.042 |
| Activity | **0.642** | 0.605 | +0.037 |
| OrganismalFitness | 0.632 | 0.582 | +0.050 |

Every category improves, which is the good news and also the least interesting part of the table. The
spread is what matters: the method sits at 0.851 on stability assays and 0.642 on activity assays — a
gap of 0.21 that the aggregate 0.694 conceals entirely. A practitioner applying this to an enzyme
engineering problem is working at the bottom of our range, not the top.

The aggregate and the top of the list do not rank categories identically: OrganismalFitness improves most
in global ordering (+0.050) but sits mid-table in top-of-list lift, its assays being the largest in the
panel and the most likely to regress (48%). We report both because neither alone is honest — the
aggregate would overstate the practical gain on that category, and top-of-list alone would understate a
real improvement in ordering.

## 5.4 The number a wet lab actually cares about

Spearman is a whole-list statistic. An engineering campaign has a library and can assay tens of
candidates; the question is whether the top of our ranking contains the top of the true ranking.

For each assay and split we rank variants by the published prediction, take the top *k* ∈ {1%, 5%, 10%},
and measure how many of them fall in the true top *k* by measured fitness. Aggregation is the official
one — per assay over schemes, per protein, per category, mean over categories.

| top of the list | recall of the true top | random | lift |
|---|---:|---:|---:|
| 1% | **0.119** | 0.010 | **11.8x** |
| 5% | **0.247** | 0.050 | **4.96x** |
| 10% | **0.350** | 0.100 | **3.50x** |

Ordering the top 5% of candidates recovers about a quarter of the true top 5% — roughly five times
random. That is the statement a protein engineer can plan around, and it is invisible in the aggregate
Spearman.

**It is also category-dependent, and in the direction §5.3 predicts.** At the top 5%:

| category | lift over random |
|---|---:|
| Stability | **7.7x** |
| Binding | 4.9x |
| OrganismalFitness | 4.6x |
| Expression | 4.2x |
| Activity | **3.4x** |

The same ordering holds at the top 1%, where stability reaches 0.226 and activity 0.066. **The ranker is
roughly twice as good at prioritising stability mutants as activity mutants**, and activity is what
function-oriented campaigns care about.

Ranking and ground truth are both computed within an assay-by-split unit on the released DMS files, so
the reference is independent of everything in §4, and aggregation follows the official chain. The lift,
not the raw recall, is the quantity to compare across categories, because categories differ in size and
in the base rate of top-*k* variants.

## 5.5 Where it fails

The improvement is not uniform, and a paper that reported only §5.2 would be misleading.

**87 of 217 assays regress** against the previous four-expert fusion, with a median improvement across
all assays of +0.0016 — roughly half the mean, so the gain is carried by a subset.

**Expression is the only category that regresses on average** (−0.0018). OrganismalFitness regresses in
48% of its assays but the surviving gains outweigh the losses.

**The effect disappears on large assays.** Splitting the panel into quartiles by mutant count:

| quartile | mean delta | regress rate |
|---|---:|---:|
| Q1 (smallest) | **+0.0073** | 0.255 |
| Q2 | +0.0017 | 0.444 |
| Q3 | +0.0024 | 0.407 |
| Q4 (largest) | **+0.00003** | 0.500 |

This is the sharpest honest limitation in the paper. The assays with the most measurements — the ones a
serious campaign is most likely to run — are exactly where the method is at parity with its predecessor
while regressing half the time. We do not have an explanation that survives scrutiny: it is not simply a
sample-size effect in the correlation estimate, since the *baseline* also has more data there.

**Coverage is partial and coupled.** The encoder requires a wild-type sequence and covers 182 of 217
assays; the other 35 fall back to an older expert. Those 35 still show +0.0029, but not because of their
own predictions: the nested weight search fits one weight vector per fold over *all* training assays, so
replacing the expert elsewhere moves the weights applied to them. Their delta is real for the system and
uninformative about the individual assay.
