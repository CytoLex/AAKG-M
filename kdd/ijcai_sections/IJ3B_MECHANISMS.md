## 3.2 Seven mechanisms, one protocol

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

One mechanism clears the constant, by +0.00025, with a confidence interval straddling zero; four more
land within 0.0006 below it, the same magnitude on the other side. The two that fail badly do so
instructively — a context regressed onto weights scores below the constant, so the regression is actively
harmful, and a per-variant median discards the magnitude that separates a strong predictor from a weak
one. **No mechanism is separated from a tuned constant by more than the seed-to-seed spread of the models
themselves.**

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

**The shrinkage is derived, not tuned.** If an assay's fitted weight vector has sampling variance σ²_i around
a true weight whose variance across assays is τ², the optimal shrink is `λ_i = τ²/(τ² + σ²_i)`. Both
components are estimable here: σ²_i from repeating the fit on six independent half-splits, τ² as the total
variance of the fitted weights minus the mean sampling variance. On indels this yields τ² = 0.0113 against
σ̄² = 0.0195, a median λ of 0.39, and **+0.0022** — within 12% of the +0.0025 that the best hand-tuned k
reaches, with an implied k of 241 against the tuned 300 — **without ever selecting k**. On substitutions the
same rule gives +0.0051 against a tuned +0.0056, on a loss surface flat from k = 30 to k = 300. The
shrinkage strength follows from how much the weights actually move between assays and how much they move
between refits of the same assay; it does not need a search.

**And it is predictable before you fit.** The oracle gain is not evenly spread across assays: it is
explained by how much the experts disagree on that assay (r = **+0.534** on substitutions, **+0.348** on
indels) and, negatively, by how much data the assay has (r = −0.279). A linear predictor of the gain from
those two statistics, fitted leave-one-assay-out, reaches r = **+0.554** without ever fitting a per-assay
weight vector. Whether adapting the weights is worth attempting is therefore a property of the assay that can
be read off before any of it is done.

**This is the sharpest comparison in the paper.** The seven mechanisms of §3.2 are the designed answer to
this problem; the best captures **+0.00025** over its tuned constant. A two-parameter shrinkage captures
**+0.0051** over the constant in its own out-of-sample protocol — twenty times as much — and stays positive
on indels, where unregularised fitting loses. Here the estimation problem was a variance problem, and it has
a two-line fix.

