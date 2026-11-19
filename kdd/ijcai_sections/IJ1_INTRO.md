A protein engineering campaign begins with a library of candidate mutations and a budget covering tens
of assays, perhaps hundreds. Everything upstream of the bench is a ranking problem: which candidates are
worth synthesising. The models that answer it have improved substantially — sequence language models
\cite{esm2}, structure-informed kernels \cite{kermut}, supervised models trained on deep mutational
scanning data \cite{proteinnpt} — and the practice is to combine several, because they fail on different
assays \cite{proteingym}.

The combination is almost always **conditional**: a gate reads assay-level context and emits weights, a
mixture layer routes by protein family \cite{jacobs1991,shazeer2017}, an uncertainty term reweights per
variant \cite{deepsong}. The premise is that different assays need different mixtures, and that learning
the mapping from context to weights is worth its parameters. It has produced a decade of architectures.

This paper tests it, and the answer reorganises the problem.

**First, the allocation headroom is small enough to bound.** We evaluate six label-free conditioning
mechanisms — parametric and nonparametric, per-assay, per-category and per-variant, supervised and not —
against a single constant tuned on held-out assays. One clears it, by +0.00025 with a confidence interval
straddling zero; four land within 0.0006 below. The sharper statement is an oracle: a rule that sees the
held-out assay's own labels can gain **+0.0027** over the fixed blend, and that is the ceiling for any
weighting of this pool. Replacing one expert is worth **+0.0077** in the same protocol. **The entire
allocation headroom is a quarter of the expert headroom.**

**Second, the expert headroom is in how a mutation is represented.** A substitution is a difference
between two sequences, and the useful signal is the difference — not the mutant residue in isolation, not
the site in isolation. We build an encoder over reference-minus-mutant features in a ±4-residue
neighbourhood, distilled from the agreement of the two strongest experts, with a functional-category
low-rank residual and predictions averaged over eight seeds. Fused with three published experts at four
fixed weights, it reaches **0.694** on the official ProteinGym metric against **0.657** for Kermut, the
leaderboard leader. We validate the measurement before reporting it: recomputing Kermut through our
pipeline reproduces the published per-assay table on all 217 assays with mean absolute difference 0.0.

**Third, an aggregate score is not a deployment specification, and we report the one that is.** The same
model that reaches 0.694 overall scores 0.851 on stability assays and 0.642 on activity assays, and the
ordering it produces is uneven in the same way: the top 5% of the ranking recovers 24.7% of the true top
5%, a **4.96x** lift over random, which rises to 7.7x on stability and falls to 3.4x on activity. The
advantage also has a size regime — largest on small assays, and at parity with the previous fusion
(+0.00003) on the largest quartile of mutant counts. Those two numbers are what let a laboratory decide
how much of the ordering to trust for its own property and its own assay size.

The second claim is what changes how the field builds these models; the third is what a user can act on
today; the first is what makes both measurable rather than asserted.

## Contributions

1. **A falsification of adaptive weighting for this problem.** Seven mechanisms under one protocol, all
   at or below a tuned constant, plus an oracle bounding the total allocatable gain at +0.0027. We argue
   this should be a reported baseline, not a footnote.
2. **An expert built from differential representations**, with the ablation that shows where the signal
   is: the wild-type-minus-mutant difference and the local neighbourhood carry +0.116, while stacking
   more layers alone is negative.
3. **A utility characterisation that makes the ranking usable** — top-of-list recall by functional
   category, and the assay-size regime over which the advantage holds. It converts one aggregate number
   into the two facts a campaign needs: how much of the top of the list to trust, and for which property.
4. **A reproducible artifact**: per-mutant predictions for all 696,311 mutants and the code that
   regenerates every number in two commands from two public repositories, supplied with this submission
   as anonymised supplementary material and released publicly on publication.
