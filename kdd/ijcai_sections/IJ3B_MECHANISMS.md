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
**0.6830** for the constant fitted on the other assays: a headroom of **+0.0051** (95% CI [0.0038, 0.0066]).
That is the entire amount any weighting rule, supervised or not, per-assay or not, could ever extract from
this pool, and its interval is estimated by resampling assays and re-aggregating each resample.

**The expert lever.** Adding the distilled encoder to the same pool raises the nested constant from 0.6830
to **0.6952**, a gain of **+0.0122** (95% CI [0.0099, 0.0144]).

**The allocation headroom is 42% of the expert gain, and the intervals do not overlap.** Per-assay weighting
is therefore a real but secondary lever: everything a weighting rule could reach is less than half of what
one expert change delivers. The two quantities are easy to conflate: an oracle over one pool compared against a fixed blend of a
*different*, stronger pool understates the allocation side.

The gate itself behaves as intended — its per-assay weights reproduce across independent seeds at
r = 0.92–0.97 — which locates the shortfall in the objective rather than the optimisation.

## 3.4 The headroom is real, and it is not noise

A small oracle gain invites the objection that the oracle is fitting its own noise. Variants of each assay
are split into disjoint halves A and B; weights selected on A and evaluated on B transfer a gain of
**+0.0028 ± 0.0008** over ten independent splits, which is **44%** of the +0.0063 ± 0.0006 obtainable when
selection and evaluation share variants. Both halves are aggregated the same way as §3.3, so the two
quantities are comparable.

The per-assay optimum is therefore a stable property of the assay rather than an artefact of selection,
and what survives (+0.0028) is an order of magnitude above the best of the seven mechanisms (+0.00025) —
the headroom exists and is partly estimable, and it is not a function of the context statistics anyone
computes: a ridge \cite{rasmussen2006} from those statistics to the oracle weights reaches 0.6860, below the
constant, so the fitted direction is actively wrong.

