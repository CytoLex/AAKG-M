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

The gate itself behaves as intended — its per-assay weights reproduce across independent seeds at
r = 0.92–0.97 — which locates the shortfall in the objective rather than the optimisation.

#**Having the weights and being able to estimate them are different problems, and the second is fixable.**
In an out-of-sample protocol — weights fitted on half an assay's variants and evaluated on the other half —
the per-assay rule gains **+0.0047** on substitutions but *loses* **0.0032** on indels, where assays are
small. Pooling each assay's weights toward the panel-wide constant — `w(λ) = (1−λ)·w_panel + λ·w_i` with
`λ = n_i/(n_i+k)` and k selected on the panel, never on the held-out half — gains **+0.0051** and
**+0.0021** respectively: partial pooling matches the per-assay rule where estimation is feasible and turns
a loss into a gain where it is not.
Partial pooling is therefore the right way to adapt weights on this problem — not because it finds new
headroom, but because it is the only version that survives small assays.

# 3.4 The headroom is real, and it is not noise

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

