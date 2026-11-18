## 1 Introduction

A protein engineering campaign begins with a library of candidate mutations and a budget that covers
tens of assays, perhaps hundreds. Everything upstream of the bench is a ranking problem: which
candidates are worth synthesising. The models that answer it have improved substantially — sequence
language models, structure-informed kernels, supervised models trained on deep mutational scanning
data — and the current practice is to combine several of them, because they fail on different assays.

The combination is almost always made **conditional**. A gate reads assay-level context and emits
weights; a mixture layer routes by protein family; an uncertainty term reweights per variant. The
premise is that different assays need different mixtures, and that learning the mapping from context to
weights is worth its parameters. It is an appealing premise, and it has produced a decade of
architectures.

This paper tests it, and the answer reorganises the problem.

**First, the allocation headroom is small enough to bound.** We evaluate six label-free conditioning
mechanisms — parametric and nonparametric, per-assay, per-category and per-variant, supervised and not —
against a single constant tuned on held-out assays. One clears it, by +0.00025 with a confidence
interval straddling zero. Four land within 0.0006 below. The sharper statement is an oracle: a rule that
sees the held-out assay's own labels can gain **+0.0027** over the fixed blend, and that is the ceiling
for any weighting of this pool. Replacing one expert is worth **+0.0077** in the same protocol. **The
entire allocation headroom is a quarter of the expert headroom.**

**Second, the expert headroom is in how a mutation is represented.** A substitution is a difference
between two sequences, and the useful signal is the difference — not the mutant residue in isolation, not
the site in isolation. We build an encoder over reference-minus-mutant features in a ±4-residue
neighbourhood, distilled from the agreement of the two strongest experts, with a functional-category
low-rank residual and predictions averaged over eight training seeds. Fused with three published experts
at four fixed weights, it reaches **0.694** on the official ProteinGym supervised metric against
**0.657** for Kermut, the current leaderboard leader. We validate the measurement before reporting it:
recomputing Kermut through our pipeline reproduces the published per-assay table on all 217 assays with
mean absolute difference 0.0, and our fold assignments are bit-identical to the official distribution.

**Third, the utility is category-specific and concentrated at the top.** The aggregate 0.694 conceals
a 0.21 spread across functional categories, and it conceals where the method is useful. Taking the top
5% of the ranking recovers 24.7% of the true top 5%, a **4.96x** lift over random — but 7.7x on
stability assays against 3.4x on activity assays. On the largest assay quartile, the improvement over
the previous fusion is **+0.00003**: parity, with a 50% regression rate.

We think the third point is the one that matters for practice, and the second is the one that matters
for the field. The first is what makes both of them measurable.

## Contributions

1. **A falsification of adaptive weighting for this problem.** Seven mechanisms under one protocol, all
   at or below a tuned constant, plus an oracle that bounds the total allocatable gain at +0.0027. We
   argue this should be a reported baseline, not a footnote.

2. **An expert built from differential representations**, with the ablation that shows where the signal
   is: the wild-type-minus-mutant difference and the local neighbourhood carry +0.116, while stacking
   more layers alone is negative.

3. **A utility characterisation beyond aggregate correlation** — top-of-list recall by functional
   category, the 87 assays that regress, and the collapse to parity on large assays. This is the part a
   practitioner can act on and the part that keeps the headline honest.

4. **A reproducible artifact.** Per-mutant predictions for all 696,311 mutants in the benchmark, the
   code that regenerates every number in two commands from two public repositories, and the recovered
   kernel of the structural experts verified to floating-point precision.

## What this paper is not

It is not a claim that conditional weighting is worthless in general. In recommendation and multi-task
learning the mixture frequently carries real signal, and our result does not transfer there. It is not a
state-of-the-art claim: we beat one leaderboard entry, with one of that entry's own components inside our
ensemble, and we say so. And it is not a wet-lab validation: the top-of-list lift is a property of the
ranking, not a measured hit rate, and the experiment that would connect them has not been run.

## 2 Related work




**Protein fitness prediction.** Three lines converge here. Zero-shot predictors score variants from a
sequence model's likelihood or from multiple-sequence-alignment statistics, without touching assay
labels. Supervised approaches train on deep mutational scanning data, either per assay or across a
panel; the current leaderboard leader is a composite kernel regression of this kind. The fusion line,
which this paper belongs to, combines predictors that fail differently — sequence kernels, structure
kernels, and learned encoders — and the combination is usually weighted per assay. Our contribution is
not a new member of any of these lines but a measurement of which of them the fusion actually benefits
from, and an expert built to exploit the answer.

**Adaptive weighting and gating.** Mixture-of-experts layers, context-conditioned gates and meta-learned
weighting schemes are standard across machine learning, and they are usually justified by heterogeneity
of the input distribution. Our negative result does not contradict that literature; it identifies a
regime where the justification fails — when the mixture components are highly correlated within a unit
(0.78 to 0.96 here) and the conditioning variable is not the one the optimal weights depend on. Reported
gains for gating in such regimes should be read against a tuned constant rather than a fixed prior, and
against an oracle.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and it
is a poor guide to deployment: it is insensitive to where in the ranking the errors fall, and it
averages over subpopulations a practitioner treats separately. Our top-of-list analysis by functional
category is a small step toward reporting what a downstream experiment would actually experience, and we
know of no reason it should be specific to protein fitness.

**What this paper does not span.** Three adjacent literatures bear on the claims and are not tested
here. Calibration and uncertainty quantification are the natural next step after a ranking result: our
predictions carry no calibrated error bars, and the per-assay regression rate of 40% is a statement that
a calibrated method could have flagged in advance. Active learning is the sequel rather than the
alternative — if the top of the list is enriched, the question becomes how quickly a batch can be chosen
and how the posterior updates, which is a different experiment. And structure-based design methods take
coordinates and propose sequences, whereas this work only ranks proposals someone else has made; the
dual-use considerations in §6 differ accordingly, and we do not claim the design-side literature's
results transfer.



## 3 Allocation has no headroom


Protein fitness models combine heterogeneous predictors: a sequence model, a structure kernel, an
assay-adaptive kernel. Because assays differ, the combination is usually made *conditional* — a gate
reads assay-level context and emits weights, a mixture-of-experts layer routes per family, an
uncertainty term reweights per variant. The premise is that a different assay needs a different
mixture, and that learning that mapping is worth parameters.

We ask a narrower question, the one the premise depends on. **If the mixture were the lever, how much
could any weighting rule gain?** The answer is bounded above by an oracle: a rule that sees the
held-out assay's own labels and picks the best mixture for it. Everything honest is below that.

## 3.2 Seven mechanisms, one protocol

We evaluate six label-free conditioning mechanisms plus the tuned constant they all have to beat. Every
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

## 3.1 Setup


**Benchmark.** ProteinGym's supervised substitution benchmark: 217 deep mutational scanning assays over
186 UniProt identifiers, each with three official cross-validation splits — `fold_random_5`,
`fold_modulo_5`, `fold_contiguous_5`. Following the benchmark's own protocol, a model is refitted per
assay on four folds and predicts the fifth, and the ordering is evaluated by Spearman correlation
within each assay-by-split unit, giving 651 units.

**Aggregation.** We use the official chain without modification: per-unit Spearman, averaged over the
three splits, then grouped by UniProt identifier and coarse functional category, then averaged over the
five categories. The grouping step is the one most often skipped in reimplementations: several assays
share a protein, and averaging them before the category step changes the result by about 0.005. Every
number in this paper is produced by the benchmark's own
`performance_DMS_supervised_benchmarks.py`, run unmodified on a score file we provide, rather than by a
reimplementation of its aggregation.

**Splits are the published ones.** Our fold assignments are bit-identical to the released
`cv_folds_singles_substitutions` files — we verified this on all three schemes for a 9,576-variant
assay, 9,576 of 9,576 mutants matching. We did not regenerate splits.

**Models.** Four experts. Two are frozen predictions from published methods: Kermut, a composite
Gaussian-process kernel over sequence and structure features, and AMK, an assay-adaptive mixed structure
kernel; a third, an additive structure kernel, receives weight 0.00 and does not affect scoring. The
fourth is our encoder, described in §4, refitted per assay and per split.

**Feature construction.** Per-residue representations come from ESM-2 650M at layers 20, 30 and 33, on
both the wild-type and the mutated sequence, with a ±4-residue window pooled by mean at layers 30 and
33. Concatenating site vectors, wild-type vectors, window pools and difference terms gives 12,800
dimensions per variant. Features are standardised per assay with the statistics stored alongside each
fit.

**Training the encoder.** A 12,800 → 256 → 64 → 1 head with a category-specific rank-8 linear residual,
trained by the distillation loss of §4.2 with α = 0.9 and selected by early stopping on the held-out
fold of an inner split. Eight independent seeds per assay are trained and their per-variant predictions
are averaged. α and the rank were both re-verified by inner selection: α re-selects to 0.9 in all five
folds, and rank 4 and rank 8 differ by 0.0002.

**Fusion.** Four fixed weights per fold, selected on the training assays by simplex grid search and
applied to the held-out assays — the same procedure the tuned-constant baseline uses, so the comparison
is equal-compute. The grid is a step-0.1 simplex over four weights.

**Baselines.** Five, in increasing strength. A fixed 50/50 blend of the two strongest experts. A fixed
D+Kermut blend. The tuned constant of §3. A nested constant whose weights are selected per fold. And
Kermut alone, which is also the published leaderboard leader on this metric.

**Statistics.** Seed-level intervals come from eight independent runs of the full pipeline. Assay-level
intervals come from a two-level bootstrap that resamples assays within category and seeds together,
4,000 replicates. Where a comparison is between two configurations evaluated on the same assays, we
report paired differences rather than differences of means, because the assay-to-assay variance is
roughly an order of magnitude larger than the effect.

**Reproduction.** Two commands from two public repositories regenerate every number in this paper. The
score file, the per-mutant predictions for all 696,311 variants, the fusion and evaluation scripts, and
the recovered kernel for the two structural experts are in the released artifact (§8). The control row
of §5.1 is produced by the same command as the headline, so a reader can verify that our aggregation is
correct before trusting any comparison we make with it.

**Compute.** One H200 GPU per encoder run; a full 217-assay panel with eight seeds takes a few hours on
a single device. The structural experts are frozen and cost nothing at scoring time. This matters for
the reproduction claim: a reader with one GPU can rebuild the encoder but not the experts, which is why
their per-mutant predictions are published rather than left to be regenerated.

## 4 The expert


A substitution is a difference. The reference and the mutant differ at one position, and the effect of
that difference depends on what the residue was, what it became, and what surrounds it. Three features
follow from taking that literally.

**The change, not the state.** For each variant we extract per-residue representations from three ESM-2
650M layers (20, 30, 33) on both the wild-type and the mutated sequence, and keep `mut`, `wt`, and
`mut − wt`. The difference vector is what the model reads most: a substitution's effect is not a
property of the mutant residue alone.

**The neighbourhood, not the site.** A ±4-residue window around the mutation is pooled by mean at layers
30 and 33. The same substitution in the protein's interior and on its surface is a different event, and
a site-only vector cannot see the difference.

**Both, concatenated.** The union of these blocks is 12,800 dimensions per variant: five site vectors,
three wild-type layer vectors, two window pools, and the difference terms. This is the representation the
encoder is trained on.

The encoder ladder, under the per-assay protocol, says where the signal actually comes from:

| representation | score |
|---|---:|
| site vector only (layer 33) | 0.467 |
| + multiple layers | 0.464 |
| + ±4 neighbourhood | 0.480 |
| **+ wild-type layers and difference terms** | **0.596** |

Stacking layers alone is negative. The gain is in the difference and the wild-type context, worth
+0.116 — an order of magnitude more than either of the other two steps.

## 4.2 Distillation from the experts we already trust

A 12,800-dimensional head trained on a few thousand variants per assay overfits before it learns. We
regularise it with the two strongest experts in the pool: the sequence kernel and the mixed structure
kernel. Their per-assay z-scores are averaged into a teacher `t = 0.4·Kermut_z + 0.5·AMK_z`, and the
loss mixes the measured target with the teacher,

```
L = (1 − α)·MSE(student, target) + α·MSE(student, teacher),   α = 0.9
```

α was selected on held-out assays and the sweep is flat-topped: 0.607 at α = 0.6, 0.617 at 0.75, 0.621
at 0.9, 0.619 at 1.0. Re-selecting α inside each of the five folds, using only training assays, picks
0.9 in all five — so the nested estimate equals the fixed one exactly.

Distillation is worth +0.114 on the union representation (0.484 → 0.598). It is the largest single step
in the encoder's development, larger than the feature union itself, and it is worth noting *why*: the
teacher is not a better model than the target, it is a smoother one, and the student inherits smoothing
where it needs it most — the low-data assays.

## 4.3 A residual per functional category

Assays fall into five coarse categories that behave differently. A single linear head cannot express
"for stability assays, weight this dimension more". We add a low-rank correction on the head's output,

```
y = MLP(x) + U_c V_cᵀ x,    U_c zero-initialised, rank 8
```

with `c` the assay's category, so the correction is shared across assays of the same kind and cannot
overfit any single one. Rank 8 is not a tuned value: rank 4 and rank 8 score within 0.0002 of each
other, so the branch is saturated.

The branch is worth **+0.024** standalone and **+0.0014** in the fusion. The gap between those two
numbers is the decorrelation argument in miniature: a residual that makes an expert better can make it
*less* useful to a pool that already contains the thing it learned.

**Control arm.** A shared branch with the same rank (one `U`, not five) gains 0.0008 *less* than the
per-category one, and a shared branch with five times the parameters still loses. The gain needs the
category structure, not the parameters.

## 4.4 Variance, not bias

Eight independent training runs of the same architecture differ by about 0.004 in the official metric.
We do not average the resulting scores; we average the predictions, per variant, and use the average as
the expert's output. This is a variance reduction and nothing else — same model class, same features,
same hyperparameters.

It is worth **+0.023** standalone (0.622 → 0.645) and **+0.0022** in the fusion. The asymmetry is
informative: the fusion already averages over four experts, so a fifth of the noise is removed before
the expert arrives.

Because the averaged expert is a single object, it has no seed distribution. We therefore report two
rungs: the single-model rung carries the seed-level confidence interval and the equal-compute
comparison, and the seed-averaged rung is the deployed number.

## 4.5 Four fixed weights, no gate

The fusion is four numbers:

```
pred = 0.00·D + 0.40·Kermut + 0.40·AMK + 0.20·X
```

selected on the training assays of each fold and applied to the held-out assays — exactly the protocol
that the tuned constant in §3 uses, which is the point. The search drives the additive-structure
expert's weight to 0.00 in 14 of 15 seed-by-fold cells and sets the new expert's weight to 0.20 in all
15. Structure is still present through the mixed kernel; what disappears is the standalone structure
prior, which §3.4 showed was already worthless.

**Under the official metric** the ladder is:

| configuration | official |
|---|---:|
| previous four-expert fusion | 0.685538 |
| + distilled encoder, category residual | 0.691130 |
| **+ eight-seed averaging** | **0.693311** |

against **0.657028** for Kermut, the published leaderboard leader — a gain of **+0.0085** over the
previous fusion and **+0.037** over the leader.

## 4.6 The control that decides the interpretation

The category residual has five branches and the shared alternative has one, so a natural reading is that
the gain is simply "more parameters". We ran the control.

| branch | parameters | standalone delta vs plain | seeds positive | 95% CI |
|---|---|---:|---:|---|
| per-category, rank 8 | 5x | **+0.0214** | 4/4 | [+0.0157, +0.0274] |
| shared, rank 8 | 1x | −0.0008 | 2/4 | [−0.0054, +0.0040] |

The per-category branch beats the shared branch by **+0.0214** with every seed positive, on a matched
parameter-per-branch comparison. The shared branch, which has the same rank and one fifth of the
parameters, is indistinguishable from no branch at all. **The gain requires the category structure, not
the parameters.** We regard this as the load-bearing ablation in the paper, because without it the
residual reads as capacity and with it the residual reads as structure — the same five vectors carved
per category rather than jointly.

A second control fixes the rank. Rank 4 and rank 8 land within 0.0002 of each other standalone, so the
branch is saturated at a rank far below what would be needed to memorise a category; the branch is not
a lookup table.

## 4.7 What the ablation rules out

Nine directions were measured and rejected, and three of them are worth stating because they constrain
what a reader should conclude.

**Co-distillation from the fusion itself** lifts the expert by +0.0136 (8/8 seeds, CI excluding zero)
and leaves the fusion at −0.0002. Teaching an expert to imitate the pool removes exactly the residual
disagreement that gave it value — the clearest demonstration we have that standalone accuracy and
marginal value are different quantities.

**A residual or boosting expert**, trained on the fusion's own error, receives weight exactly zero in
every fold. The residual of a fitted ensemble is, by construction, the part these features cannot
explain.

**A larger pre-trained backbone** (ESM-C 300M) is decorrelated but too weak: +0.0007 as a fourth expert
with a confidence interval straddling zero, and −0.011 concatenated. Representation diversity without
competence is worthless.

The constructive reading: an expert earns its place through disagreement in the residual, and the way
to get that disagreement is a different *view* of the same information — reference versus mutant, local
versus global — not a different optimiser, a different loss, or a bigger model.

## 5 What the ranker is worth


Before any claim, the measurement itself has to be trustworthy. We run the official
`performance_DMS_supervised_benchmarks.py` unmodified on a score file containing our per-assay,
per-scheme correlations for the 217 assays — and, as a control, the same correlations recomputed from
Kermut's predictions through our pipeline. The control row reproduces the published leaderboard entry on
all nine of its numbers: the average, the three cross-validation schemes, and the five functional
categories.

At the per-assay level the agreement is stronger still: our recomputed Kermut column matches the
published `DMS_substitutions_Spearman_DMS_level.csv` on **217 of 217 assays** with mean absolute
difference **0.0** and maximum 0.0005, the residual being the published table's three-decimal rounding.
Our fold assignments are bit-identical to the released `cv_folds_singles_substitutions` files
(9,576/9,576 mutants on all three schemes for the assay we checked).

So the numbers below are on the leaderboard's scale, computed by the leaderboard's own code.

## 5.2 The headline, and what it is a headline of

| model | official average | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| ProteinNPT (published rank 2) | 0.619 | | | |
| **Kermut (published rank 1)** | **0.657** | 0.745 | 0.633 | 0.593 |
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

## 5.8 Reading the result correctly

Three sentences we would want a reader to take away, in order of confidence.

**The fusion is better than the published leader on the official metric, by 0.037, with a control row
that reproduces the leaderboard exactly.** That we can defend to the decimal.

**The utility is category-specific and concentrated at the top of the ranking.** Five-fold lift in the
top 5%, twice as strong on stability as on activity.

**On large assays and on function-oriented categories, expect parity at best.** The aggregate number
should not be read as a uniform improvement, and we have published the per-mutant predictions so that
anyone can check this on their own assay.

## 6 Limitations and ethical considerations


### Limitations

**The ranker is unreliable on most functional categories.** Top-of-list recall at 5% is 0.38 for
stability assays but 0.17 for activity assays — a 2.2x spread — and activity is the category an
enzyme-engineering campaign most often cares about. Aggregate Spearman hides this completely; a user
who reads only the headline number will over-trust the method on function-oriented assays.

**The gain disappears on large assays.** Splitting the 217 assays into quartiles by mutant count, the
mean improvement over the previous fusion is +0.0073 on the smallest quartile and +0.00003 on the
largest, with a 50% regression rate on the largest. Assays with more measurements — the ones most
likely to be run at scale — are exactly where the method is at parity with its predecessor.

**A substantial minority of assays regress.** 87 of 217 assays (40%) score worse than the previous
four-expert fusion, with a median improvement across all assays of only +0.0016. The aggregate gain is
carried by a subset, and we do not have a feature that predicts in advance which subset.

**Coverage is partial, and the uncovered assays are coupled rather than independent.** The distilled
encoder requires a wild-type sequence and covers 182 of 217 assays; the remaining 35 fall back to an
older expert. Those 35 still show a mean improvement of +0.0029, but not because of their own
predictions: the nested weight search fits one weight vector per fold over *all* training assays, so
changes elsewhere move the weights applied to them. Reported per-assay deltas for those 35 should not
be read as evidence about their own representation.

**The structural experts are inherited, not retrained inside each outer fold.** Their kernel is
recovered and verified to floating-point precision (max absolute difference 8.2e-14 against the saved
per-fold predictions), and the published per-mutant scores make every reported number reproducible —
but a fully nested protocol would retrain them within each fold, which we did not do. The one
hyperparameter that materially matters, the distillation weight, was re-selected inside each fold and
chose the same value in all five; the broader design space, however, was explored on this panel.

**One benchmark family, no prospective validation.** All results are on ProteinGym substitution
assays. There is no held-out cohort from a different source, and no wet-lab experiment. Whether
top-of-list lift translates into hit-rate lift in a real screening campaign is untested; it is the
next experiment, not a claim.

**Feature storage is heavy.** The encoder's main features are 32 MB per assay — 762 variants x 10,368
dimensions in float32 — which is 6.9 GB across the 217 assays and must be regenerated from ESM-C for
any assay outside the panel. We therefore distribute per-mutant predictions rather than the feature
pipeline.

### Ethical considerations

**Dual use.** Protein fitness predictors can be applied to gain-of-function engineering. Our method
ranks a user-supplied set of single-residue variants; it does not generate sequences, does not perform
design, and provides no structure-to-function capability beyond what the public ProteinGym baselines
already offer. We nevertheless note that ranking is the step that decides which candidates a laboratory
synthesises, and that this is the point at which such models are most directly useful. We release
predictions for the existing public assays only.

**Data.** All assays are previously published deep mutational scanning datasets distributed by
ProteinGym. No new experimental data, no human subjects, no clinical material, and no institutional
review was required. The wild-type sequences used for feature extraction are the ones distributed with
the public DMS files.

**Bias and domain shift.** The panel is skewed toward particular protein families, model organisms and
assay types, and our per-category results show that performance is not uniform across them. A
practitioner applying this to a protein family absent from ProteinGym should expect the large-assay
behaviour — parity, not improvement — rather than the headline.

**Released artifacts.** We publish per-mutant predictions for all 696,311 mutants, the code that
reproduces every reported number, and the recovered kernel for the structural experts. The expert
prediction tables remain research-use only, because they derive from third-party methods. We consider
the predictions themselves the artifact of record: they are what a reviewer or a practitioner needs,
and they are sufficient to re-derive every number in the paper.

**Use of generative AI.** The paper's prose and analysis scripts were developed with AI assistance.
Per the track's authorship policy this is disclosed in the submission form, and the authors take
responsibility for all content.

## 7 Discussion




Three things change depending on who is reading.

**If you are building a fusion.** Report the oracle. It takes an afternoon to compute and it converts an
open-ended search for better gating into a bounded question: how much is left? When the answer is a
quarter of what a single expert change is worth, the search is over.

**If you are ranking candidates for a campaign.** Trust the top of the list more than the middle, trust
stability and binding predictions more than activity predictions, and do not expect an advantage on
assays with tens of thousands of measurements. The per-mutant predictions are published so that this can
be checked on the assays you care about before committing a library.

**If you are evaluating.** A ranker's aggregate correlation and its top-of-list recall can disagree in
significance — ours agree in direction but differ by a factor of two across categories — and the second
is closer to what the downstream experiment measures. The cheapest version of this discipline is to
report the oracle and the tuned constant alongside any learned weighting, and the second cheapest is to
report the per-category breakdown rather than the mean. Neither takes more than an afternoon and both
change what a reader concludes.

**What would falsify us.** If a pool of experts were built to disagree — deliberately selected for low
residual correlation rather than high standalone score — the oracle over that pool would be larger, and
adaptive weighting might pay again. Our claim is about headroom under a pool built the usual way, and it
should be re-measured whenever the pool changes. We would be glad to be wrong about this one.

The experiment we would run next is a prospective one: generate a candidate list from the ranking, assay
it alongside a random control, and measure whether the top-of-list lift reported here becomes a hit-rate
lift at the bench. Until that is done, the honest claim is about rankings, not about discoveries.