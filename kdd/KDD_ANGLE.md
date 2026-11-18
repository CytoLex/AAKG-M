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

## The three measurements are done

None needed new training; all three are computations over the per-assay scores we already publish.

| question | answer | file |
|---|---|---|
| top-of-list utility | top 1% recall 0.119 vs 0.010 random (**11.8x**), top 5% **4.96x**, top 10% **3.50x**; best on Stability (7.7x), worst on Activity (3.4x) | `RESULTS_TOP_K.md` |
| which assays regress | **87 of 217**; Expression is the only category negative on average (−0.0018); the largest assay quartile gains **+0.00003** | `RESULTS_FAILURE_ANALYSIS.md` |
| coverage dependence | all +0.0038, encoder-covered +0.0047, fallback +0.0029 — the 35 are coupled through the nested weight search, not scored independently | `RESULTS_FAILURE_ANALYSIS.md` |

Two of these change the paper. The regression count is **87 negative / 130 positive / 0 unchanged**, not
the "85 / 97 / 35" the drafts carried, and the assay-size effect is a sharper limitation than any we
had written down: on the largest quartile the method is at parity with its predecessor.
