# §3 Allocation has no headroom

Camera-ready draft, English, ~1350 words. Protocol note: the mechanism table and the oracle bound are
measured under the per-assay category-balanced protocol; the fusion numbers in §4–§5 come from the
official performance script. The two conventions are stated wherever a number appears.

---

## 3.1 What the field optimises

Protein fitness models combine heterogeneous predictors: a sequence model, a structure kernel, an
assay-adaptive kernel. Because assays differ, the combination is usually made *conditional* — a gate
reads assay-level context and emits weights, a mixture-of-experts layer routes per family, an
uncertainty term reweights per variant. The premise is that a different assay needs a different
mixture, and that learning that mapping is worth parameters.

We ask a narrower question, the one the premise depends on. **If the mixture were the lever, how much
could any weighting rule gain?** The answer is bounded above by an oracle: a rule that sees the
held-out assay's own labels and picks the best mixture for it. Everything honest is below that.

## 3.2 Seven mechanisms, one protocol

We evaluate six label-free conditioning mechanisms plus the tuned constant they all have to beat, on
ProteinGym \cite{proteingym}. Every
mechanism is label-free with respect to the assay being scored: its weights for assay *a* come either
from other assays or from no labels at all. All are measured on the 217 ProteinGym substitution assays,
651 assay-by-split units, under the official category-balanced aggregation.

| mechanism | official | Δ vs constant | 95% CI | type |
|---|---:|---:|---|---|
| tuned constant (0.05, 0.45, 0.50) | **0.687637** | — | — | none |
| MLP gate over 17 context statistics | 0.687888 | **+0.000251** | [−0.001924, +0.002545] | parametric, per-assay |
| per-variant uncertainty weighting | 0.687106 | −0.000531 | [−0.001181, +0.000021] | unsupervised, per-variant |
| k-NN over assay context | 0.687170 | −0.000467 | [−0.001329, +0.000259] | nonparametric, per-assay |
| per-category constants | 0.687220 | −0.000417 | [−0.000784, −0.000084] | parametric, per-category |
| ridge regression context → weights | 0.685109 | −0.002528 | [−0.007833, +0.000676] | linear, per-assay |
| per-variant consensus (median) | 0.670492 | −0.017146 | [−0.026771, −0.011115] | unsupervised, per-variant |

One mechanism clears the constant, by +0.00025, with a confidence interval straddling zero. Four more
land within 0.0006 *below* it — the same magnitude, on the other side. The two that fail badly do so for
instructive reasons: a ridge on context cannot beat a constant because the context does not predict the
optimal weights (it scores below the constant, so the regression is actively harmful), and a per-variant
median discards the magnitude information that separates a strong predictor from a weak one.

The spread of the six is 0.017, and all of it is on the losing side. **Not one of them is separated from
a tuned constant by more than the seed-to-seed spread of the models themselves.**

## 3.3 The bound is small

The oracle over the same expert pool reaches **0.693544**, against **0.690808** for the fixed blend — a
headroom of **+0.0027**. That is the entire amount any weighting rule, supervised or not, per-assay or
not, could ever extract from this pool. For comparison, the same protocol attributes **+0.0077** to
replacing a single expert in that pool.

**The allocation headroom is a quarter of the expert gain.** This is the paper's central magnitude
comparison, and it is worth being precise about what it does and does not say. It does not say the gate
is broken; the MLP gate is stable across seeds and its per-assay weights agree at r = 0.92–0.97 between
independent halves, and shuffling them within category costs 0.0017. It says the object being learned
is nearly irrelevant to the objective, because the pool does not contain enough disagreement for the
choice to matter.

## 3.4 Why the pool has no disagreement

The tuned optimum places weight 0.05 on the additive-structure expert. Deleting that expert entirely
costs nothing measurable. Structure enters through the mixed kernel, not as a standalone prior, and once
it does, the remaining experts are correlated at 0.78 to 0.96 within a unit — the diversity that a gate
would exploit is largely nominal.

A gate that is stable, informative, and worth four percent of what per-assay weights could deliver is
not a failure of optimisation. It is evidence that the conditioning variable — 17 label-free context
statistics — is not the variable the optimal weights depend on. We verified the direction of that
mismatch directly: regressing the oracle weights on the same context statistics, with leave-one-out
protection, scores **below the constant**.

## 3.5 What this means for the field

Three implications, ordered by how confident we are.

**Report against tuned constants, not fixed blends.** A gate that beats a fixed 50/50 blend by +0.0047
is commonly reported as evidence that conditioning works. Against a constant tuned on held-out assays
the same gate is +0.0002, a statistical tie. The gain attributed to conditioning is mostly the gain from
*tuning at all*, and the literature's comparison point is often the wrong one.

**A per-assay oracle should be a reported baseline.** It costs nothing to compute and it converts "our
gate improves over the previous gate" into "our gate captures *x* percent of the available headroom",
which is the only number that tells a reader whether the mechanism is worth its complexity. Here *x* is
four percent.

**When the oracle is small, the pool is the problem.** The constructive half of this paper follows
directly: if no weighting of these experts can gain more than +0.0027, the next +0.01 has to come from
an expert that disagrees with the others in a useful way. §4 builds one.

## 3.6 The headroom is real, and it is not noise

A small oracle gain invites the objection that the oracle is fitting its own noise: choose per-assay
weights on a set of variants, and part of the apparent advantage is selection on those particular
variants. We tested that directly with a split-half design.

Variants of each assay are split into two disjoint halves A and B. We select the per-assay optimal
weights on A and evaluate on B, against the constant. The transferred gain is **+0.0041**, which is
**49%** of the +0.0083 obtainable when the weights are selected and evaluated on the same variants.
Half of the oracle gain survives contact with unseen variants, so the per-assay optimum is a stable
property of the assay rather than an artefact of selection.

That half-surviving gain is still three times what the gate captures, which sharpens the diagnosis
rather than softening it. The headroom exists, it is reproducible, and it is simply not a function of
the context statistics anyone computes.

**Three independent checks agree on the mechanism.** (i) The gate is not degenerate: split across
independent seeds, its per-assay weights agree at r = 0.92–0.97, and shuffling them within category
costs 0.0017. (ii) The context does not contain the mapping: a ridge from the same 17 statistics to the
oracle weights, with leave-one-out protection, reaches 0.6860 — below the constant, meaning the fitted
direction is actively wrong rather than merely weak. (iii) The gate captures 3.6% of the oracle gain.
A stable, informative function that recovers four percent of the available headroom is a representation
failure, not an optimisation one.
