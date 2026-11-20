# Third source: FLIP2

The two benchmarks in the paper so far — ProteinGym substitutions and ProteinGym indels — come from one
suite, which is the last objection a reviewer can raise against the evidence. FLIP2 is an independent
benchmark with its own collectors, its own splits and its own baseline family. This directory records what
it can and cannot carry.

## What FLIP2 is

Seven datasets over sixteen predefined splits (`flip.protein.properties`, data on Zenodo, DOI
`10.5281/zenodo.18433203`). Files are gzipped CSV with a four-column schema — `sequence`, `target`, `set`,
`validation` — plus a parallel FASTA format carrying the same metadata in the header.

**There is no wild-type column and no published per-variant prediction.** Baselines exist only as research
code with experiment-specific paths; the repository says so explicitly and points at the paper for the
official numbers.

## What is usable, and why it is only part of it

Of the sixteen splits, the fixed-length substitution libraries with a fitted train set:

| dataset | splits | rows | train / test | length | target |
|---|---:|---:|---|---:|---|
| amylase | 4 | 3,706 | 1,426–2,574 / 488–1,924 | 425 | −0.010 … 0.212 |
| ired | 1 | 8,586 | 3,746 / 4,178 | 290 | −4.841 … 4.764 |
| trpb | 2 of 3 | 228,298 | 8,633 / 31,557 | 389 | −0.801 … 2.451 |

Excluded and why: `hydro` (5 splits), `pdz3`, `rhomax` are **variable length**, so there is no wild type to
difference against; `nucb` has a **binned target** (0–3, 48k test rows) and is a classification task;
`trpb/one_to_many` has **304 training rows**, too few to fit an 11,520-dimensional head.

**The wild type is inferred** as the per-position modal residue. The reconnaissance measured this to be
safe: modal support 0.99 and a median distance of 2–4 residues from the inferred wild type, which is what
these libraries contain.

## The limitation that matters

FLIP2 gives **seven usable splits**, not hundreds of independent assays. The paper's allocation claim is a
statement about a *population* of units: it fits one constant on the other units and reports what a
per-unit oracle would add. Seven units cannot support that — the oracle would be pure noise.

So FLIP2 **can carry claim 2** (the representation) and **cannot carry claim 1** (allocation). The
three-source statement below holds for the representation claim only, and the paper says so rather than
implying three sources for everything.

## What is being measured

Three models per split, trained on the released train set, evaluated once on the released test set:

| arm | what it isolates |
|---|---|
| ridge on mean-pooled ESM-2 embeddings of the mutant | a standard FLIP-style baseline |
| ridge on the differential features | the features without the neural head |
| MLP encoder on the differential features | the paper's model |

The comparison that matters is arm 1 against arms 2–3: if the differential view is worth what the paper
claims, it should beat a mean-pooled embedding baseline **on a benchmark it was not developed against**.

## Caveats to state in the paper

- The wild type is inferred rather than published, and the inference is validated only by its own
  stability (modal support, distance distribution) — not against a ground-truth reference.
- `trpb` contributes two splits that share one underlying library, so its three arms are measured twice on
  overlapping sequences; the splits are counted separately but that is not three independent datasets.
- No distillation is used on FLIP2 because there are no published per-variant predictions to distil from,
  so the arm is the α = 0 configuration. That is the weaker of the two the paper reports, which makes the
  comparison conservative.

## Result

Seven splits, three arms, released train and test partitions, evaluated once on test:

| split | train | test | ridge on mean-pooled ESM-2 | ridge on differential | MLP on differential |
|---|---:|---:|---:|---:|---:|
| amylase / one_to_many | 2,574 | 488 | +0.5901 | +0.4906 | **+0.6990** |
| amylase / close_to_far | 1,426 | 1,924 | +0.0116 | −0.1020 | **+0.4712** |
| amylase / far_to_close | 1,539 | 1,782 | +0.1107 | +0.0429 | **+0.2713** |
| amylase / by_mutation | 2,403 | 702 | +0.4476 | +0.2444 | **+0.6659** |
| ired / two_to_many | 3,746 | 4,178 | **+0.1738** | +0.0623 | +0.1631 |
| trpb / two_to_many | 8,633 | 217,507 | +0.2388 | +0.0925 | **+0.4473** |
| trpb / by_position | 31,557 | 188,852 | +0.2650 | +0.2239 | **+0.3095** |
| **mean** | | | **+0.2625** | **+0.1507** | **+0.4325** |

The encoder wins six of seven splits and loses one by 0.011, lifting the mean from 0.26 to 0.43 on a
benchmark it was not developed against.

**The differential features alone are worse, and the paper says so.** A ridge on the same features scores
0.15, below the mean-pooled baseline. The advantage belongs to the view *combined with* a nonlinear head,
not to the view on its own — which is the same conclusion the substitution-side feature ablation reaches
from the other direction, where the difference terms are worth +0.116 but only inside the trained encoder.

## What this buys and what it does not

It buys the **representation claim** a third, independently collected benchmark, so that result no longer
rests on one suite.

It does not buy the **allocation claim** a third source. That claim is about a population of units — fit
one constant on the others, ask what a per-unit oracle adds — and FLIP2 supplies seven units. Seven is not
a population. The paper therefore says three sources for the representation result and two for allocation,
rather than claiming three for everything.
