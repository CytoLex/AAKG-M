# §1 Introduction

Camera-ready draft, English, ~850 words.

---

A protein engineering campaign begins with a library of candidate mutations and a budget that covers
tens of assays, perhaps hundreds. Everything upstream of the bench is a ranking problem: which
candidates are worth synthesising. The models that answer it have improved substantially — sequence
language models \cite{esm2}, structure-informed kernels \cite{kermut}, supervised models trained on deep
mutational scanning data \cite{proteinnpt} — and the current practice is to combine several of them,
because they fail on different assays \cite{proteingym}.

The combination is almost always made **conditional**. A gate reads assay-level context and emits
weights; a mixture layer routes by protein family \cite{jacobs1991,shazeer2017}; an uncertainty
term reweights per variant \cite{deepsong}. The
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
