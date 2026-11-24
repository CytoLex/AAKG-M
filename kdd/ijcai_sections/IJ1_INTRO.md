A protein engineering campaign begins with a library of candidate mutations and a budget covering tens of
assays. Everything upstream of the bench is a ranking problem: which candidates are worth synthesising. The
models that answer it have improved — sequence language models \cite{esm2}, structure-informed kernels
\cite{kermut}, supervised models trained on deep mutational scanning data \cite{proteinnpt} — and practice
combines several, because they fail on different assays \cite{proteingym}.

The combination is almost always **conditional**: a gate reads assay-level context and emits per-assay
weights, a mixture layer routes by protein family \cite{jacobs1991,shazeer2017}, an uncertainty term
reweights per variant \cite{deepsong}. The premise is that different assays need different mixtures. This
paper asks how much that premise is worth, and answers with a measurement rather than another architecture.

**Weighting has a ceiling, and the ceiling depends on what you measure.** An oracle that picks the best mixture
per assay using that assay's own labels reaches **+0.0051** over a constant fitted on the other assays, against
**+0.0122** for adding one expert: 42%, intervals disjoint. That bound is Spearman's. Under top-1% recall — what
a campaign actually experiences — the transferable headroom is **2.8 times larger**, and a rule that optimises
that recall and then shrinks beats weights a Spearman objective selects by **+0.0093** (CI [+0.0014, +0.0171]).
Fitted out of sample, per-assay weights gain +0.0047 on substitutions but *lose* 0.0032 on indels; shrinkage by
`λ = n/(n+k)` gains +0.0051 and +0.0021 instead.

**An expert is worth its disagreement, not its accuracy.** Across thirteen expert-into-pool pairs, marginal
value tracks disagreement at r = **+0.786** and not standalone score: **the weakest expert alone contributes the
most, and the strongest contributes almost nothing.** A noise column, a shuffled copy and a negated copy all
score exactly zero, so the measurement is not an artefact of enlarging the weight search. The objective is
residual disagreement subject to a competence floor, and the floor is measurable — the expert we build sits
within 0.0009 of it.

**That principle selects the representation.** A substitution is a difference between two sequences, so the view
that produces useful disagreement is the difference: reference-minus-mutant features in a ±4-residue
neighbourhood, distilled, with a functional-category residual. Fused at four fixed weights this reaches **0.694**
against **0.657** for Kermut, having first reproduced Kermut's published per-assay table on 217 of 217 assays to
mean absolute difference 0.0; the same representation wins six of seven FLIP2 splits.

**An aggregate score is not a deployment specification.** The model that reaches 0.694 scores 0.851 on stability assays and
0.642 on activity, and the top 5% of its ranking recovers 23.9% of the true top 5% — a **4.8x** lift that is 7.8x
on stability and 3.5x on activity. Those numbers let a laboratory decide how much of the ordering to
trust for its own property and assay size.

The levers are ordered, and so is what to do about each: measure the ceiling before tuning weights, spend on
experts that disagree rather than experts that score well, pool when you do weight, and optimise the metric you
will be judged by rather than the one that is convenient.

## Contributions

1. **A diagnostic protocol for fusion, and what it finds here.** Three numbers per pool — the oracle bound,
   the estimability of the weights, and the shrinkage that reaches it. Applied to
   seven gating mechanisms, three benchmarks and two expert pools it gives +0.0051 of allocatable headroom
   against +0.0122 for an expert change, and a shrinkage rule that recovers +0.0051 and +0.0021 where naive
   per-assay fitting loses. Applied to the deployment metric instead, the same protocol finds 2.8 times the
   headroom and yields a two-line rule that reaches all of it. The natural cross-pool comparison would have
   reported +0.0027 for the same quantity, an 85% error.
2. **An expert's value is its disagreement, not its accuracy**, measured at r = +0.786 across thirteen
   expert-into-pool pairs with noise, shuffle and negate controls at zero, and bounded by a competence floor we
   map. The representation follows from the principle rather than motivating it: the difference view carries
   +0.116 where stacking layers is negative, and a control arm shows the category structure is what the
   residual needs (+0.0214 against a shared branch with a fifth of the parameters).
3. **A utility characterisation that makes the ranking usable** — top-of-list recall by functional
   category, and the assay-size regime over which the advantage holds. It converts one aggregate number
   into the two facts a campaign needs: how much of the top of the list to trust, and for which property.
4. **A reproducible artifact**: per-mutant predictions for all 696,311 mutants and the code regenerating
   every number, supplied as anonymised supplementary material and released on publication.
