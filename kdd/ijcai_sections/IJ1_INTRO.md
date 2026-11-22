A protein engineering campaign begins with a library of candidate mutations and a budget covering tens of
assays. Everything upstream of the bench is a ranking problem: which candidates are worth synthesising. The
models that answer it have improved — sequence language models \cite{esm2}, structure-informed kernels
\cite{kermut}, supervised models trained on deep mutational scanning data \cite{proteinnpt} — and practice
combines several, because they fail on different assays \cite{proteingym}.

The combination is almost always **conditional**: a gate reads assay-level context and emits per-assay
weights, a mixture layer routes by protein family \cite{jacobs1991,shazeer2017}, an uncertainty term
reweights per variant \cite{deepsong}. The premise is that different assays need different mixtures. This
paper asks how much that premise is worth, and answers with a measurement rather than another architecture.

**Weighting has a ceiling, and the ceiling is reachable.** An oracle that picks the best mixture for each
assay using that assay's own labels reaches **+0.0051** over a constant fitted on the other assays; adding
one expert to the same pool is worth **+0.0122**. The allocation headroom is 42% of the expert gain, and the
two intervals do not overlap. The bound is not the end of the story. Fitted on half an assay's variants and
evaluated on the other half, per-assay weights gain **+0.0047** on substitutions but *lose* 0.0032 on indels,
where assays are small; shrinking them toward the panel-wide constant by `λ = n/(n+k)` gains **+0.0051** and
**+0.0021** instead. Adapting weights is worth doing, at a scale the ceiling sets, and the estimator that
works is partial pooling.

**The expert's headroom is in how a mutation is represented.** A substitution is a difference between two
sequences, and the signal is the difference — not the mutant residue alone, not the site alone. We build an
encoder over reference-minus-mutant features in a ±4-residue neighbourhood, distilled from the two strongest
experts, with a functional-category low-rank residual and eight-seed averaging. Fused with three published
experts at four fixed weights it reaches **0.694** on the official metric against **0.657** for Kermut, the
leaderboard leader. We validate before reporting: recomputing Kermut through our pipeline reproduces the
published per-assay table on 217 of 217 assays with mean absolute difference 0.0, and the same representation
wins six of seven splits on FLIP2, an independently collected benchmark.

**An aggregate score is not a deployment specification.** The model that reaches 0.694 scores 0.851 on
stability assays and 0.642 on activity; the top 5% of its ranking recovers 24.7% of the true top 5%, a
**4.96x** lift over random that rises to 7.7x on stability and falls to 3.4x on activity; and on the largest
assay quartile the advantage over the previous fusion is **+0.00003**. Those three numbers are what let a
laboratory decide how much of the ordering to trust for its own property and its own assay size.

The levers are thus ordered, and so is what to do about each: measure the ceiling before tuning weights, put
the effort into experts, and pool when you do weight.

## Contributions

1. **A diagnostic protocol for fusion, and what it finds here.** Three numbers per pool — the oracle bound,
   the estimability of the weights, and the shrinkage that reaches it. Applied to
   seven gating mechanisms, three benchmarks and two expert pools it gives +0.0051 of allocatable headroom
   against +0.0122 for an expert change, and a shrinkage rule that recovers +0.0051 and +0.0021 where naive
   per-assay fitting loses. The protocol is the transferable part: the natural cross-pool comparison would
   have reported +0.0027 for the same quantity, an 85% error.
2. **A measurement of where a mutation's signal lives.** Ablating the representation shows that the
   wild-type-minus-mutant difference and the local neighbourhood carry +0.116 while stacking more layers is
   negative, and a control arm shows the category structure is what the residual needs (+0.0214 against a
   shared branch with a fifth of the parameters). The expert is the vehicle; the finding is that the
   representation, not the capacity, is what moves the number.
3. **A utility characterisation that makes the ranking usable** — top-of-list recall by functional
   category, and the assay-size regime over which the advantage holds. It converts one aggregate number
   into the two facts a campaign needs: how much of the top of the list to trust, and for which property.
4. **A reproducible artifact**: per-mutant predictions for all 696,311 mutants and the code regenerating
   every number, supplied as anonymised supplementary material and released on publication.
