Two things remain: what this work gives the domain it studies, and what would overturn it.

### What this contributes to protein engineering

A protein engineer choosing mutations against an assay budget needs a ranking they can act on, and the
field's papers are not organised around that. Two deliverables follow. The first is a **calibrated
expectation**: taking the top 5% recovers 24.7% of the true top 5%, but 7.7x on stability assays against
3.4x on activity, and no advantage on the largest assays — a laboratory can use that profile to decide
how much of the ordering to trust for the property it cares about, a statement aggregate Spearman cannot
express. The second is **the boundary**: 87 regressing assays, the category that regresses on average, and
the size regime at parity. For a practitioner the boundary is worth more than the mean, because it is the
difference between trusting a ranking on a familiar assay family and being surprised on a new one.

Three AI challenges are tackled. The ranking problem is small-data-per-task learning, so the question is
regularisation and transfer rather than capacity. It is a distribution-shift problem, which is exactly why
the field reached for adaptive weighting and why we show weighting has no headroom. And it is a
representation problem: the signal lives in the difference between two sequences and in the local
structural neighbourhood.

Three challenges arise from using AI here. Wet-lab validation is the binding constraint and it is slow and
expensive, so the field reports against retrospective benchmarks and hopes the ranking transfers; we have
not closed that gap. Assay data is heterogeneous in ways metadata does not capture — two stability assays
on one protein can disagree in sign — so a category-averaged metric can look stable while individual
assays move sharply both ways. And the benchmark ecosystem rewards leaderboard movement over
characterisation, while characterisation is what a domain user needs most.

On our use of ProteinGym: the track prefers domain-specific data to existing benchmarks, so we state what
this adds rather than only takes. We verify the benchmark end to end — reproducing its published
per-assay values for a reference method on 217 of 217 assays, confirming its folds are bit-identical — we
publish per-mutant predictions for all 696,311 variants so the evaluation is reproducible without our
code, and we characterise its difficulty structure across categories, sizes and splits. A reader can use
that characterisation without adopting our method.

### Implications, and what would falsify us

**If you are evaluating.** Report the oracle and the tuned constant alongside any learned weighting, and the
per-category breakdown instead of the mean: a ranker's aggregate correlation and its top-of-list recall can
disagree, and the second is closer to what the downstream experiment measures.



The experiment we would run next is prospective: generate a candidate list from the ranking, assay it
alongside a random control, and measure whether the top-of-list lift becomes a hit-rate lift at the bench.
Until then the honest claim is about rankings, not discoveries.
