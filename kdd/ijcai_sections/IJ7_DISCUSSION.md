Two things remain: what this work gives the domain it studies, and what would overturn it.

### What this contributes to protein engineering

A protein engineer choosing mutations against an assay budget needs a ranking they can act on, and the field's
papers are not organised around that. Two deliverables follow. The first is a **calibrated expectation**: the top 5% recovers
23.9% of the true top 5%, 7.8x on stability assays against 3.5x on activity, and no advantage on the largest — a profile that lets a laboratory decide how much of the ordering to trust for its own property, which
aggregate Spearman cannot express. The second is **the boundary** — the regressing assays, the category that regresses on average, and the size
regime at parity. For a practitioner the boundary is worth more than the mean: it is the difference between
trusting a ranking on a familiar assay family and being surprised on a new one.

Three AI challenges are tackled: small-data-per-task learning, so the question is regularisation rather than
capacity; distribution shift, which is why the field reached for adaptive weighting and why that lever is 42% of an
expert change; and representation, where the signal lives in the difference between two sequences.

Three challenges arise from using AI here. Wet-lab validation is the field's binding constraint, and this paper
places its claims at the ranking rather than the bench. Assay data is heterogeneous in ways metadata does not
capture — two stability assays on one protein can disagree in sign — so a category-averaged metric can look stable
while individual assays move sharply both ways. And the ecosystem rewards leaderboard movement over
characterisation, which is what a domain user needs most.

On our use of ProteinGym: rather than only taking from a public benchmark we verify it end to end, publish
per-mutant predictions for all 696,311 variants so the evaluation stands without our code, and characterise its
difficulty structure across categories, sizes and splits. A reader can use that characterisation without adopting
our method.

### What this work gives, and what would overturn it





The experiment we would run next is prospective: generate a candidate list from the ranking, assay it
alongside a random control, and measure whether the top-of-list lift becomes a hit-rate lift at the bench.
Until then the honest claim is about rankings, not discoveries.

**What would overturn this.** Three developments would move the conclusion, and each is measurable with the
protocol of §3. A pool whose experts disagree more than this one's — the oracle is a function of
disagreement, r = +0.534 — would raise the ceiling. An assay regime with many more variants per assay would
make the weights estimable where they are not, shifting the bound from "small" to "large enough to matter". A
gating mechanism that beats a tuned constant by more than the seed-to-seed spread would break the claim that
none does. Any of the three would be reported by the same three numbers this paper reports.
