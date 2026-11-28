## 3.2 Seven mechanisms, one protocol

**A fusion result needs three numbers, not one**: how much any weighting of the pool could gain (an oracle),
how much of that an assay's own data can estimate (a split-half), and which estimator reaches it. Reporting
only the first invites a cross-pool comparison that is easy to make and wrong — that comparison reads +0.0027
for this paper's own allocation headroom, against **+0.0051** measured inside one pool -- it captures just over half, and the gap is the point.

We evaluate six label-free conditioning mechanisms plus the tuned constant they all must beat, on
ProteinGym \cite{proteingym}: 217 substitution assays, 651 assay-by-split units, official
category-balanced aggregation. Every mechanism is label-free with respect to the assay being scored —
its weights for assay *a* come from other assays or from no labels at all. A model is refitted per assay
on four of five published folds and predicts the fifth; our folds are bit-identical to the released
files, verified on all three schemes for a 9,576-variant assay.

The six mechanisms land between **−0.00053 and +0.00025** against it, every interval straddling or barely
excluding zero; the full table is in the released analysis.

One mechanism clears the constant by +0.00025 with an interval straddling zero; four land within 0.0006
below. **None is separated from the constant by more than the seed-to-seed spread of the models themselves.**

Stacking \cite{wolpert1992stacked} and ensemble selection \cite{caruana2004ensemble} are the standard answers to
this; the mechanisms below are their conditional variants, and the tuned constant is what unconditional combination
amounts to.

**And the constant is not separated from a parameter-free average either.** Averaging the experts' within-assay
ranks — no labels, no parameters — reaches **0.6922** against the tuned constant's **0.6952**, a paired difference of
**−0.0010** with a 95% CI of [−0.0031, +0.0011]. So nothing in this section separates from simple rank averaging,
tuned or learned: the comparison the mechanisms had to survive was itself only tied with a rule that requires no
fitting at all.

## 3.3 The bound, measured against the expert lever

Two quantities decide where the effort belongs, and they have to be measured in one pipeline or the
comparison is meaningless. Both below use the same aggregation — per-split Spearman, mean over schemes,
grouped by UniProt identity then by functional category — on the 182 assays where the distilled expert
covers the panel, so that both pools are evaluated on the same units.

**The allocation bound.** Inside the three-expert pool, a per-assay oracle reaches **0.6881** against
**0.6830** for the constant fitted on the other assays: **+0.0051** (95% CI [0.0038, 0.0066]), estimated by
resampling assays and re-aggregating each resample \cite{efron1993bootstrap}. **The expert lever.** Adding the distilled encoder to the
same pool raises that constant to **0.6952**, a gain of **+0.0122** (95% CI [0.0099, 0.0144]).

**The headroom is not selection noise.** Replacing each assay's oracle weights with those of a *random other* assay
— matched per-assay selection, zero information — gives **−0.0064** [−0.0083, −0.0043]: below the constant, as random
per-assay weights should be. The real oracle sits **0.0115** above that null — 0.6881 against 0.6766.

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

Unregularised per-assay fitting gains on substitutions and **loses** on indels, where assays are small. Shrinking
each assay's weights toward the panel-wide constant, `w(λ) = (1−λ)·w_panel + λ·w_i`, gains on both — the figures
below are over the constant fitted in this out-of-sample protocol, not the §3.3 one.

**Shrinkage is the fix, and a single level is enough.** This is the classical variance-reduction argument: shrink toward a pooled
value by the ratio of between- to within-group variance \cite{james1961stein}. The strength has a closed form — `λ_i = τ²/(τ² + σ²_i)`,
with σ²_i the sampling variance of an assay's fitted weights from six half-splits and τ² the between-assay
variance — and on indels it reaches **+0.0022** against +0.0025 for a hand-tuned k with no search.

The control says what does the work: **permuting those coefficients across assays** changes the gain by at most
**+0.0005** on indels, inside its own spread, and is 0.0009 *better* on substitutions. **What matters is that the estimate is shrunk, not how finely**: on indels a flat λ of 0.60 gains +0.0062 where the
derived median of 0.41 gains +0.0052, so the closed form is if anything over-shrinking. We report the per-assay form
because it needs no hand-chosen constant, not because its adaptivity earns anything.

**And it is predictable before you fit.** The oracle gain is not evenly spread across assays. It is explained by
the **ambiguity** of the pool on that assay — the variance of the experts' own scores, the term the ensemble
decomposition turns on \cite{audhkhasi2013generalized,wood2023unified} — and, negatively, by how much data the
assay has (r = −0.279). A leave-one-assay-out predictor from those two statistics reaches r = **+0.628** without fitting a per-assay weight
vector, against **+0.002** for a permuted predictor, so whether adapting the weights is worth attempting can be read
off before any of it is done.

**And it is not spread evenly.** Ranking assays by pool ambiguity, the top quartile holds **57%** of the total
allocation headroom with a median gain of **+0.0117**; the bottom quartile is flat, at +0.0009 and 5%. Restricting
the oracle to the quarter the predictor ranks highest still captures **+0.0050** of the +0.0077 available. A
practitioner with a panel can therefore rank their own assays by ambiguity and know, before fitting anything,
which ones make adaptation worth the attempt.

Disagreement between the raw predictions is weaker, at r = +0.509, and skill-weighting it weaker still: what helps
is the spread of the experts' *scores*, not the correlation of their *predictions*. Consistent
with that literature we report this as a trade-off, not a maximand — pushing disagreement further by residualising
an expert against the pool collapsed its accuracy to −0.33 and bought nothing.

