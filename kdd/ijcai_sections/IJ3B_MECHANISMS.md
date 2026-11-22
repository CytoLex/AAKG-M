## 3.2 Seven mechanisms, one protocol

**A fusion result needs three numbers, not one**: how much any weighting of the pool could gain (an oracle),
how much of that an assay's own data can estimate (a split-half), and which estimator reaches it. Reporting
only the first invites a cross-pool comparison that is easy to make and wrong — that comparison reads +0.0027
for this paper's own allocation headroom, against **+0.0051** measured inside one pool, an 85% error.

We evaluate six label-free conditioning mechanisms plus the tuned constant they all must beat, on
ProteinGym \cite{proteingym}: 217 substitution assays, 651 assay-by-split units, official
category-balanced aggregation. Every mechanism is label-free with respect to the assay being scored —
its weights for assay *a* come from other assays or from no labels at all. A model is refitted per assay
on four of five published folds and predicts the fifth; our folds are bit-identical to the released
files, verified on all three schemes for a 9,576-variant assay.

| mechanism | official | Δ vs constant | 95% CI |
|---|---:|---:|---|
| tuned constant (0.05, 0.45, 0.50) | **0.687637** | — | — |
| MLP gate over 17 context statistics | 0.687888 | **+0.000251** | [−0.001924, +0.002545] |
| per-variant uncertainty weighting | 0.687106 | −0.000531 | [−0.001181, +0.000021] |
| k-NN over assay context | 0.687170 | −0.000467 | [−0.001329, +0.000259] |
| per-category constants | 0.687220 | −0.000417 | [−0.000784, −0.000084] |
| ridge context → weights | 0.685109 | −0.002528 | [−0.007833, +0.000676] |
| per-variant consensus (median) | 0.670492 | −0.017146 | [−0.026771, −0.011115] |

One mechanism clears the constant by +0.00025 with an interval straddling zero; four land within 0.0006
below. **None is separated from the constant by more than the seed-to-seed spread of the models themselves.**

## 3.3 The bound, measured against the expert lever

Two quantities decide where the effort belongs, and they have to be measured in one pipeline or the
comparison is meaningless. Both below use the same aggregation — per-split Spearman, mean over schemes,
grouped by UniProt identity then by functional category — on the 182 assays where the distilled expert
covers the panel, so that both pools are evaluated on the same units.

**The allocation bound.** Inside the three-expert pool, a per-assay oracle reaches **0.6881** against
**0.6830** for the constant fitted on the other assays: **+0.0051** (95% CI [0.0038, 0.0066]), estimated by
resampling assays and re-aggregating each resample. **The expert lever.** Adding the distilled encoder to the
same pool raises that constant to **0.6952**, a gain of **+0.0122** (95% CI [0.0099, 0.0144]).

**The allocation headroom is 42% of the expert gain, and the intervals do not overlap.** Per-assay weighting
is therefore a real but secondary lever: everything a weighting rule could reach is less than half of what
one expert change delivers. The two quantities are easy to conflate: an oracle over one pool compared against a fixed blend of a
*different*, stronger pool understates the allocation side.

The gate itself behaves as intended — its per-assay weights reproduce across seeds at r = 0.92–0.97 — which
locates the shortfall in the objective, not the optimisation.

## 3.4 Estimating the weights is a separate, solvable problem

The bound says what weightings could reach. Whether an assay's own variants can *find* those weights is a
different question, and it has to be asked out of sample: weights fitted on half an assay's variants and
evaluated on the other half, with the reference constant fitted on the same half of the other assays.

| | substitutions | indels |
|---|---:|---:|
| per-assay weights, out of sample | +0.0047 | **−0.0032** |
| partial pooling, k tuned | +0.0051 | +0.0021 |
| **partial pooling, λ derived** | **+0.0051** | **+0.0022** |

Unregularised per-assay fitting gains on substitutions and **loses** on indels, where assays are small.
Shrinking each assay's weights toward the panel-wide constant, `w(λ) = (1−λ)·w_panel + λ·w_i`, gains on both.

**Shrinkage is the fix, and a single level is enough.** The strength has a closed form — `λ_i = τ²/(τ² + σ²_i)`,
with σ²_i the sampling variance of an assay's fitted weights from six half-splits and τ² the between-assay
variance — and on indels it reaches **+0.0022** against +0.0025 for a hand-tuned k with no search.

The control says what does the work: **permuting those coefficients across assays** changes the gain by at most
**+0.0005** on indels, inside the permutation's own spread, and is 0.0009 *better* on substitutions. **What matters is that the
estimate is shrunk at all, not how finely**: on indels a flat λ of 0.60 gains +0.0062 where the derived median of
0.41 gains +0.0052, so the closed form is, if anything, over-shrinking. We report the per-assay version for needing
no hand-chosen constant, not because its adaptivity earns anything.

**And it is predictable before you fit.** The oracle gain is not evenly spread across assays. It is explained by
the **ambiguity** of the pool on that assay — the variance of the experts' own scores, the term the ensemble
decomposition turns on \cite{audhkhasi2013generalized,wood2023unified} — and, negatively, by how much data the
assay has (r = −0.279). A leave-one-assay-out linear predictor of the gain from those two statistics reaches
r = **+0.628** without ever fitting a per-assay weight vector. Whether adapting the weights is worth attempting
is therefore a property of the assay that can be read off before any of it is done.

**And it is not spread evenly.** Ranking assays by pool ambiguity, the top quartile holds **57%** of the total
allocation headroom with a median gain of **+0.0117**; the bottom quartile is flat, at +0.0009 and 5%. Restricting
the oracle to the quarter the predictor ranks highest still captures **+0.0050** of the +0.0077 available. A
practitioner with a panel can therefore rank their own assays by ambiguity and know, before fitting anything,
which ones make adaptation worth the attempt.

Disagreement between the raw predictions is the weaker signal: it predicts the gain at r = +0.509, and a
skill-weighted version of it at +0.491. Adjusting correlation for how good the experts are does not help here;
what helps is measuring the spread of their *scores* rather than the correlation of their *predictions*. Consistent
with that literature, we report these as a trade-off rather than a maximand: the gain rises with disagreement, but
pushing disagreement further by residualising an expert against the pool collapsed its standalone accuracy to
−0.33 and bought nothing.

**This is the sharpest comparison in the paper.** The seven mechanisms of §3.2 are the designed answer to
this problem; the best captures **+0.00025** over its tuned constant. A two-parameter shrinkage captures
**+0.0051** over the constant in its own out-of-sample protocol — twenty times as much — and stays positive on
indels, where unregularised fitting loses. Here the estimation problem was a variance problem, and its fix does
not need to know the variance: shrinking toward the pool by any reasonable amount recovers most of it.

