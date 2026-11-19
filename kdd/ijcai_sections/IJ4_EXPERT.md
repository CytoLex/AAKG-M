## 4.1 What a mutation is, as a signal

A substitution is a difference. We extract per-residue representations from three ESM-2 650M layers
\cite{esm2} (20, 30, 33) on both the wild-type and the mutated sequence, keep `mut`, `wt` and `mut − wt`,
and pool a ±4-residue window by mean at layers 30 and 33. The union is 12,800 dimensions per variant. The
ladder under the per-assay protocol says where the signal comes from:

| representation | score |
|---|---:|
| site vector only (layer 33) | 0.467 |
| + multiple layers | 0.464 |
| + ±4 neighbourhood | 0.480 |
| **+ wild-type layers and difference terms** | **0.596** |

Stacking layers alone is negative; the gain is in the difference and the wild-type context, worth +0.116,
an order of magnitude more than either other step.

## 4.2 Distillation, and a residual per functional category

A 12,800-dimensional head trained on a few thousand variants per assay overfits before it learns. We
regularise it with the two strongest experts: their per-assay z-scores give a teacher
`t = 0.4·Kermut_z + 0.5·AMK_z`, and the loss is `(1 − α)·MSE(student, target) + α·MSE(student, teacher)`
with α = 0.9. Re-selecting α inside each of the five folds, using only training assays, picks 0.9 in all
five. Distillation is worth +0.114 on the union representation — the largest single step in the encoder's
development, larger than the feature union itself.

Assays fall into five categories that behave differently, so we add a low-rank correction to the head:
`y = MLP(x) + U_c V_cᵀ x`, with `U_c` zero-initialised and rank 8, `c` the assay's category. The branch is
worth **+0.024** standalone and **+0.0014** in the fusion — the gap is the decorrelation argument in
miniature, since a residual that makes an expert better can make it less useful to a pool already holding
what it learned.

**The control that decides the interpretation.** A shared branch with the same rank has one fifth of the
parameters and is indistinguishable from no branch (−0.0008, 2/4 seeds); the per-category branch beats it
by **+0.0214** standalone with every seed positive, on a matched per-branch comparison. **The gain needs
the category structure, not the parameters.** Rank 4 and rank 8 differ by 0.0002, so the branch is
saturated far below what memorising a category would require.

## 4.3 Variance, and four fixed weights

Eight independent runs of the same architecture differ by about 0.004 in the official metric. We average
the predictions per variant rather than the scores: +0.023 standalone, +0.0022 in the fusion, the
asymmetry being that the fusion already averages four experts.

The fusion is four numbers, `0.00·D + 0.40·Kermut + 0.40·AMK + 0.20·X`, selected on the training assays
of each fold and applied to the held-out ones — exactly the protocol the tuned constant uses. The search
drives the additive-structure weight to 0.00 in 14 of 15 seed-by-fold cells and sets the new expert to
0.20 in all 15. Under the official metric:

| configuration | official |
|---|---:|
| previous four-expert fusion | 0.685538 |
| + distilled encoder, category residual | 0.691130 |
| **+ eight-seed averaging** | **0.693311** |

against **0.657028** for Kermut \cite{kermut} — +0.0085 over the previous fusion, +0.037 over the leader.

## 4.4 What the ablation rules out

**Co-distillation from the fusion itself** lifts the expert by +0.0136 (8/8 seeds) and leaves the fusion
at −0.0002: teaching an expert to imitate the pool removes the residual disagreement that gave it value.
**A residual expert** trained on the fusion's own error receives weight exactly zero in every fold — the
residual of a fitted ensemble is what these features cannot explain. **A larger backbone** (ESM-C 300M)
is decorrelated but too weak: +0.0007 as a fourth expert with an interval straddling zero, and −0.011
concatenated. Representation diversity without competence buys nothing.

The constructive reading: an expert earns its place through disagreement in the residual, and the way to
get that disagreement is a different *view* of the same information — reference versus mutant, local
versus global — not a different optimiser, loss, or a bigger model.
