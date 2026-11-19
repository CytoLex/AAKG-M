This section establishes that the mixture has nowhere to go. We first evaluate six label-free conditioning mechanisms against a tuned constant, then bound what *any* weighting rule could extract from this expert pool, then show that the bound is reproducible rather than an artefact of fitting
noise.

## 3.1 Seven mechanisms, one protocol

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

## 3.2 The bound is small

The oracle over the same expert pool reaches **0.693544**, against **0.690808** for the fixed blend — a
headroom of **+0.0027**. That is the entire amount any weighting rule, supervised or not, per-assay or
not, could ever extract from this pool. For comparison, the same protocol attributes **+0.0077** to
replacing a single expert.

**The allocation headroom is a quarter of the expert headroom.** This is the paper's central magnitude
comparison, and it is worth being precise about what it does and does not say. It does not say the gate
is broken: its per-assay weights reproduce across independent seeds at r = 0.92–0.97, and shuffling them
within category costs 0.0017. It says the object being learned is nearly irrelevant to the objective,
because the pool does not contain enough disagreement for the choice to matter. The tuned optimum places
weight 0.05 on the additive-structure expert, and deleting that expert entirely costs nothing measurable.

## 3.3 The headroom is real, and it is not noise

A small oracle gain invites the objection that the oracle is fitting its own noise. Variants of each
assay are split into disjoint halves A and B; weights selected on A and evaluated on B transfer a gain of
**+0.0041**, which is **49%** of the +0.0083 obtainable when selection and evaluation share variants. Half
the oracle gain survives contact with unseen variants, so the per-assay optimum is a stable property of
the assay rather than an artefact of selection.

That half-surviving gain is still three times what any mechanism captures, which sharpens the diagnosis:
the headroom exists, it is reproducible, and it is not a function of the context statistics anyone
computes. A ridge \cite{rasmussen2006} from the same 17 statistics to the oracle weights, with leave-one-out
protection, reaches 0.6860 — below the constant, meaning the fitted direction is actively wrong.

## 3.4 What this means for the field

**Report against tuned constants, not fixed blends.** A gate beating a fixed 50/50 blend by +0.0047 is
commonly reported as evidence that conditioning works; against a constant tuned on held-out assays the
same gate is +0.0002, a statistical tie. The gain attributed to conditioning is mostly the gain from
*tuning at all*.

**A per-assay oracle should be a reported baseline.** It costs nothing to compute and converts "our gate
improves over the previous gate" into "our gate captures *x* percent of the available headroom", which is
the only number telling a reader whether the mechanism is worth its complexity. Here *x* is four percent.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0027, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: the oracle is a function of how much the experts disagree, so a pool
built to disagree might make gating worthwhile again — a different paper, and one that would have to
report the oracle too.
