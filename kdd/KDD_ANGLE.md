# Three candidate framings for the AI4S submission

All three use the same evidence. They differ in what the paper asks the reader to believe, and in
which reviewers decide its fate.

## A. "Allocation was never the bottleneck" — a negative result with a constructive tail

**Claim.** The field spends its effort on the wrong object. We test an entire class of adaptive
weighting mechanisms on a 217-assay protein-fitness panel and show every one of them ties a single
tuned constant; the per-assay oracle itself sits *below* a fixed blend, so there is no allocation
headroom left to find. The headroom is in the experts.

**Evidence we have.** Seven mechanisms measured, a four-expert gate that falls 0.0046 behind the
constant once a fourth expert enters, and the oracle bound.

**Risk.** AI4S reviewers may read a null result as "no science was accelerated". The constructive half
has to carry equal weight, and the committee composition (data mining plus life sciences) is the one
that can appreciate a falsification.

## B. "A protein-fitness ranker built from differential representations"

**Claim.** Predicting which mutations a wet lab should assay is a ranking problem, and the useful
signal is the difference between the reference and the mutant in a local three-dimensional
neighbourhood. We build that encoder, fuse it with structure-aware experts, and reach 0.694 on the
official ProteinGym supervised benchmark against 0.657 for the published leader.

**Evidence we have.** The encoder ladder (0.467 → 0.645 standalone), the fusion gain decomposition, the
per-mutant predictions, the full official-metric validation down to the per-assay level.

**Risk.** This is a benchmark-chasing paper. The AI4S criteria ask for *unique data and analysis* and
for a domain contribution; "we are 0.037 better" answers neither on its own.

## C. "What a protein engineer can act on, and where the model lies"

**Claim.** We characterise a state-of-the-art fitness ranker the way a practitioner needs it: how much
of the top of the ranking is right per functional category, which assay types the method helps and
which it actively harms (85 of 217 assays got worse), and where the ceiling is (35 assays outside the
encoder's coverage, structural fallbacks).

**Evidence we have.** Per-assay paired differences, per-category breakdowns, the coverage boundary, the
oracle bound, and the published per-mutant scores that let anyone re-derive all of it.

**Risk.** Least novel-sounding. Needs the fusion result in front of it or it reads as an audit.

## Recommendation

**A as the spine, C as the substance, B as the vehicle.** The narrative runs: the field optimises
allocation, we show allocation is exhausted, so we optimise the expert, and here is what the resulting
ranker is and is not good for. That gives the AI4S track a methodological claim, a domain-facing
deliverable, and an honest boundary — which is exactly its three stated criteria.

Concretely, the 8 pages would be:

| pages | content |
|---|---|
| 1 | abstract, introduction, the domain problem (candidate prioritisation in protein engineering) |
| 2–3 | the allocation falsification: mechanisms, oracle bound, what it implies for the field |
| 4–5 | the expert: differential encoder, category low-rank residual, seed averaging, the fusion |
| 6 | what the ranker is worth: per-category agreement, top-of-list utility, the 85 assays that regress |
| 7 | limitations and ethical considerations (mandated) |
| 8 | related work, and a reproducibility statement pointing at the published scores |

## What must be measured before B or C can be written

- **Top-of-ranking utility.** Spearman is a whole-list statistic; a wet lab assays tens of candidates,
  not thousands. Precision in the top 1%, 5%, 10% per assay, aggregated the official way.
- **The regression set.** The 85 assays where the fusion loses: is it a category pattern, a variant-count
  effect, or noise? We have the per-assay table to answer this.
- **Coverage effect.** How much of the aggregate gain survives if the 35 fallback assays are excluded —
  a reviewer will ask whether the headline depends on them.

None of these need new training runs; all three are computations over the per-assay scores we already
publish.
