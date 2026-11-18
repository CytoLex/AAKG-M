# Abstract draft for KDD AI for Sciences

Written to the track's three stated criteria: unique data and analysis, an explicit domain
contribution, and an honest boundary. 8-page ACM double-column target, so this is longer than an
abstract needs to be at submission — it is the whole argument compressed to what the introduction will
expand.

---

## Draft

Protein engineering screens rank candidate mutations, but the field optimises the wrong object: the
*fusion* of sequence and structure models. A decade of work has produced learned gates, context
networks, and uncertainty-aware weighting schemes that adapt per assay, on the premise that a
different assay needs a different mixture. We test that premise on the ProteinGym substitution
benchmark, 217 assays and 651 assay-by-split units, and find that every one of seven adaptive weighting
mechanisms we measured ties a single constant tuned on held-out assays. The bound is sharper than that: a per-assay
oracle, free to choose the best mixture for every assay, reaches 0.6935 against 0.6908 for the fixed
blend — **the entire headroom any weighting rule could ever capture is +0.0027**, and replacing a
single expert is worth +0.0077. **Allocation is not where the headroom is; it is an order of magnitude
too small.**

We then show where it is. Replacing an expert changes the result by an order of magnitude more than
re-allocating among experts. Our contribution is an encoder that reads the *difference* between
reference and mutant representations in a local three-dimensional neighbourhood, distilled from the
agreement of the strongest experts, with a category-specific low-rank residual on its output and its
predictions averaged over eight training seeds. Fused as four fixed weights with three published
experts, it reaches **0.694** on the official ProteinGym supervised metric, against **0.657** for
Kermut, the current leaderboard leader. We validate the measurement before reporting it: recomputing
Kermut through the same pipeline reproduces the published per-assay table on all 217 assays with mean
absolute difference 0.0, and our fold assignments are bit-identical to the official distribution.

For the domain, the result is not the two-thousandths of aggregate gain but the shape of the ranking.
We report where the ranker is trustworthy — agreement by functional category, and how much of the top
of the list a wet lab would actually sample correctly — and where it is not: 85 of the 217 assays
regress, 35 sit outside the encoder's coverage and fall back to an older expert, and the aggregate
improvement is driven by one category. We release the per-mutant predictions for all 696,311 mutants
and the code that reproduces every number, so that the boundary can be re-derived rather than taken on
trust. The practical claim is narrow and, we think, more useful than a leaderboard position: effort
spent on adaptive weighting is misdirected, and a ranker built from differential representations buys
a better first batch of candidates while remaining unreliable on a substantial subset of assay types.

---

## Notes on choices

**"Allocation is not where the headroom is"** is the sentence the paper turns on. It is supported by
the oracle bound, which is the strongest single piece of evidence we own, and it is a statement about
the *field* rather than about our method — which is what a methodology track rewards.

**The 0.6935 / 0.6908 / +0.0077 numbers** all come from the looser per-assay protocol where they were
measured together; the +0.0077 is the expert swap's gain in that same convention. The official-metric
numbers (0.694, +0.0085 over the previous fusion) appear separately in the results section. Mixing the
two conventions inside one sentence would be the fastest way to lose a reviewer.

**The comparison was initially written backwards** — "oracle below the fixed blend" — because 0.6935
and 0.6908 are close enough to misread at a glance. The oracle is *above* the fixed blend; what makes
the argument work is that the allocation headroom (+0.0027) is smaller than the expert-swap gain
(+0.0077), not that the oracle is below anything.

**The domain paragraph deliberately leads with failure.** "85 assays regress, 35 fall back" is the kind
of statement a life-sciences reviewer trusts, and the AI4S criteria explicitly ask for limitations.
Leading with it also makes the contribution look measured rather than promotional.

**No "state of the art".** We beat one leaderboard entry, with one of that entry's own components
inside our ensemble. Claiming SOTA would be both unsupported and, given the fusion setup, easy to
demolish in review.
