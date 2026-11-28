Allocation is bounded in the aggregate and larger under the deployment metric, but on neither measure is it the
lever: an expert change is worth more than twice as much. This section builds one from a different view of the
same information, then measures which of its design choices carry the gain and which are capacity in disguise.

## 4.1 A mechanism test decides the features

If a mutation's effect were a property of the mutant residue, the residue alone would predict it. We test that
instead of assuming a representation. Three ESM-2 650M layers \cite{esm2} (20, 30, 33) are extracted on both the
wild-type and the mutated sequence, and the question is what has to be passed to the head:

Each view is retrained from scratch; the per-assay scores behind every entry are released.

| representation | score | increment |
|---|---:|---:|
| site vector of the mutant (layer 33) | 0.432 | — |
| + three layers stacked | 0.464 | +0.032 |
| + ±4-residue neighbourhood | 0.480 | +0.016 |
| **+ wild-type layers and difference terms** | **0.582** | **+0.103** |

The mutant's absolute state, even with its neighbourhood, is **0.102** below the differential view, and the
difference is three times the next largest step. Stacking layers helps a little and local context helps a little; the
change is what carries the signal. The effect is not a property of the mutant residue but of the change, read in
context, and the features follow: 12,800 dimensions of `mut`, `wt` and `mut − wt` with mean-pooled ±4 windows.
**The representation is a conclusion about the problem, not a design choice asked of the reader.**

## 4.2 Distillation, and a residual per functional category

A 12,800-dimensional head trained on a few thousand variants per assay overfits before it learns, so we regularise it by distillation \cite{hinton2015distilling} from the two strongest experts: their per-assay z-scores give a teacher `t = 0.4·Kermut_z + 0.5·AMK_z`, and the
loss mixes the target with it at α = 0.9, re-selected inside each fold on training assays and chosen 0.9 in all
five. Distillation is worth +0.114 — the largest single step in the encoder's development.

Assays fall into five categories that behave differently, so we add a low-rank correction to the head:
`y = MLP(x) + U_c V_cᵀ x`, with `U_c` zero-initialised and rank 8, `c` the assay's category — a low-rank
adaptation in the sense of \cite{hu2022lora}. The branch is
worth **+0.024** standalone and **+0.0014** in the fusion — the gap is the decorrelation argument in
miniature, since a residual that makes an expert better can make it less useful to a pool already holding
what it learned.

**The control that decides the interpretation.** A shared branch with the same rank has one fifth of the
parameters and is indistinguishable from no branch (−0.0008, 2/4 seeds); the per-category branch beats it
by **+0.0214** standalone with every seed positive, on a matched per-branch comparison. **The gain needs
the category structure, not the parameters.** Rank 4 and rank 8 differ by 0.0002, so the branch is
saturated far below what memorising a category would require.

## 4.3 Variance, and four fixed weights

Eight runs of the same architecture differ by about 0.004 in the official metric, so we average predictions per
variant rather than scores — the deep-ensemble recipe \cite{lakshminarayanan2017deep}: +0.023 standalone but only +0.0022 in the fusion, which already averages four experts.

The pool is four experts: Kermut \cite{kermut}; the site-wise structural expert we call `D`; an assay-level sequence model we call `AMK`; and `X`, the encoder of §4.1. The fusion is four numbers, `0.00·D + 0.40·Kermut + 0.40·AMK + 0.20·X`, selected on the training assays
of each fold and applied to the held-out ones — exactly the protocol the tuned constant uses. The search drives the additive-structure weight to 0.00 in 14 of 15 seed-by-fold cells and the new expert to 0.20
in all 15. Under the official metric:

Run on our submitted score file, the benchmark's own evaluation script reports **0.694** for the fusion against
**0.657** for Kermut \cite{kermut} — a lead of **+0.037** — with 0.784 / 0.674 / 0.625 across the three fold schemes.
That output is included with the submission, so the number is the benchmark's rather than ours.

## 4.4 What the ablation rules out

Two ablations agree: **co-distillation from the fusion** lifts the expert by +0.0136 but leaves the fusion at
−0.0002, and **a residual expert** trained on the fusion's own error receives weight zero in every fold.

**An expert's value is its disagreement, not its accuracy.** Measuring this directly: each of the five experts
in the bundle is added to the pool formed by the other four, under the nested-constant protocol, and its marginal
value compared with its standalone score and with its disagreement from that pool.

Figure 1 (right) shows all thirteen. A signal that indicates generalisation need not select models \cite{nagarsekar2026generalisation}; here
marginal value tracks disagreement at r = **+0.786**, and standalone accuracy does not predict it at all: across the five experts r = **−0.200**, and the weakest alone contributes the most — the
encoder at 0.6449, adding +0.0118 — while the strongest contributes +0.0028 at 0.6651. The correlation's *magnitude*
is not robust to which experts enter it: dropping the encoder's four points gives +0.500, and the seven points
contributed by the published experts alone give +0.929. We report the full set and the split rather than the headline
alone. A noise column, a shuffled copy and a negated copy each score **+0.0000**, so the measurement is not an
artefact of enlarging the weight search.

That reframes what building an expert means: useful disagreement comes from a different *view* of the same
information, not from a different optimiser, loss or bigger model. The objective is to maximise residual disagreement subject to a competence floor, and **the floor is measurable**.
Degrading the expert's predictions with noise traces a clean frontier: marginal value peaks at a small degradation
(ε = 0.25 gains **+0.0086** against +0.0077 untouched) and then falls monotonically to +0.0063 at ε = 2. **The
expert sits within 0.0009 of the frontier** — a slightly less accurate version would contribute slightly more, and
the curve falls away steeply from there. The same sweep along a residualisation axis is not a frontier: its
isolated second peak comes from re-importing per-assay structure, the artefact §3.4 identifies. **The principle is not specific to proteins**: for any pool, an expert contributes what the pool cannot already
explain, and its accuracy alone is a poor guide.
