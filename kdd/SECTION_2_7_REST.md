# §2 Related work and §7 Discussion

Camera-ready drafts, ~500 and ~350 words.

---

## 2 Related work

**Protein fitness prediction.** Three lines converge here. Zero-shot predictors score variants from a
sequence model's likelihood or from multiple-sequence-alignment statistics, without touching assay
labels. Supervised approaches train on deep mutational scanning data, either per assay or across a
panel; the current leaderboard leader is a composite kernel regression of this kind. The fusion line,
which this paper belongs to, combines predictors that fail differently — sequence kernels, structure
kernels, and learned encoders — and the combination is usually weighted per assay. Our contribution is
not a new member of any of these lines but a measurement of which of them the fusion actually benefits
from, and an expert built to exploit the answer.

**Adaptive weighting and gating.** Mixture-of-experts layers, context-conditioned gates and meta-learned
weighting schemes are standard across machine learning, and they are usually justified by heterogeneity
of the input distribution. Our negative result does not contradict that literature; it identifies a
regime where the justification fails — when the mixture components are highly correlated within a unit
(0.78 to 0.96 here) and the conditioning variable is not the one the optimal weights depend on. Reported
gains for gating in such regimes should be read against a tuned constant rather than a fixed prior, and
against an oracle.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and it
is a poor guide to deployment: it is insensitive to where in the ranking the errors fall, and it
averages over subpopulations a practitioner treats separately. Our top-of-list analysis by functional
category is a small step toward reporting what a downstream experiment would actually experience, and we
know of no reason it should be specific to protein fitness.

## 7 Discussion

**If you are building a fusion.** Report the oracle. It takes an afternoon and converts an open-ended
search for better gating into a bounded question: how much is left? When the answer is a quarter of what
a single expert change is worth, the search is over.

**If you are evaluating.** A ranker's aggregate correlation and its top-of-list recall can disagree in
significance — ours agree in direction but differ by a factor of two across categories — and the second
is closer to what the downstream experiment measures. The cheapest version of this discipline is to
report the oracle and the tuned constant alongside any learned weighting; the second cheapest is the
per-category breakdown instead of the mean.

**What would falsify us.** If a pool of experts were built to disagree — selected for low residual
correlation rather than high standalone score — the oracle over that pool would be larger, and adaptive
weighting might pay again. Our claim is about headroom under a pool built the usual way, and it should be
re-measured whenever the pool changes.

The experiment we would run next is prospective: generate a candidate list from the ranking, assay it
alongside a random control, and measure whether the top-of-list lift becomes a hit-rate lift at the
bench. Until then the honest claim is about rankings, not discoveries.
