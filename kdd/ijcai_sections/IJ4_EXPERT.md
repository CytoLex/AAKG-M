Allocation is bounded in the aggregate and larger under the deployment metric, but on neither measure is it the
lever: an expert change is worth more than twice as much. This section builds one from a different view of the
same information, then measures which of its design choices carry the gain and which are capacity in disguise.

## 4.1 A mechanism test decides the features

If a mutation's effect were a property of the mutant residue, the residue alone would predict it. We test that
instead of assuming a representation. Three ESM-2 650M layers \cite{esm2} (20, 30, 33) are extracted on both the
wild-type and the mutated sequence, and the question is what has to be passed to the head:

| representation | score | increment |
|---|---:|---:|
| site vector of the mutant (layer 33) | 0.467 | — |
| + three layers stacked | 0.464 | **−0.003** |
| + ±4-residue neighbourhood | 0.480 | +0.016 |
| **+ wild-type layers and difference terms** | **0.596** | **+0.116** |

The mutant's absolute state, even given its neighbourhood, is 0.129 below the differential view, and stacking
more layers on top of the absolute state *loses* ground. The effect is not a property of the mutant residue;
it is a property of the change, read in context. The features follow from that: 12,800 dimensions of `mut`, `wt` and `mut − wt` with mean-pooled ±4 windows.
**The representation is a conclusion about the problem, not a design choice asked of the reader.**

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

Two ablations agree: **co-distillation from the fusion** lifts the expert by +0.0136 but leaves the fusion at
−0.0002, and **a residual expert** trained on the fusion's own error receives weight zero in every fold.

**An expert's value is its disagreement, not its accuracy.** Measuring this directly: each of the five experts
in the bundle is added to the pool formed by the other four, under the nested-constant protocol, and its marginal
value compared with its standalone score and with its disagreement from that pool.

| expert | solo | marginal | disagr. |
|---|---:|---:|---:|
| encoder §4.1 | 0.6449 | **+0.0118** | **0.194** |
| Kermut | 0.6551 | +0.0062 | 0.143 |
| Kseq | 0.6364 | +0.0004 | 0.104 |
| D | 0.6561 | +0.0000 | 0.064 |
| AMK | **0.6651** | +0.0028 | 0.060 |

Marginal value tracks disagreement at r = **+0.786** across the thirteen pairs, and not accuracy: **the weakest
expert alone contributes the most, and the strongest almost nothing.** A noise column, a shuffled copy and a negated
copy each score **+0.0000**, so the measurement is not an artefact of enlarging the weight search.

That reframes what building an expert means: useful disagreement comes from a different *view* of the same
information — reference versus mutant, local versus global — not from a different optimiser, loss or bigger model.
The objective is to maximise residual disagreement subject to a competence floor, and **the floor is measurable**.
Degrading the expert's predictions with noise traces a clean frontier: marginal value peaks at a small degradation
(ε = 0.25 gains **+0.0086** against +0.0077 untouched) and then falls monotonically to +0.0063 at ε = 2. **The
expert sits within 0.0009 of the frontier** — a slightly less accurate version would contribute slightly more, and
the curve falls away steeply from there. The same sweep along a residualisation axis is not a frontier: its
isolated second peak comes from re-importing per-assay structure, the artefact §3.4 identifies. **The principle is not specific to proteins**: for any pool, an expert contributes what the pool cannot already
explain, and its accuracy alone is a poor guide.
