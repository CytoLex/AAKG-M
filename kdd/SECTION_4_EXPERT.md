# §4 The expert: differential representations

Camera-ready draft, English, ~1350 words. Fusion numbers are from the official
`performance_DMS_supervised_benchmarks.py`; the encoder ladder is under the per-assay protocol and is
labelled as such.

---

## 4.1 What a mutation is, as a signal

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

## 4.6 What the ablation rules out

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
