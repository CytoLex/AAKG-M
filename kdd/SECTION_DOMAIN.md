# §7.1 What this contributes to protein engineering

The AI for Sciences criteria ask three things beyond a method result: what the work contributes to the
domain, which challenges it tackles with AI/ML, and which challenges arise from using AI/ML there. This
subsection answers them in the domain's terms.

---

**Contributions to the domain.** A protein engineer choosing mutations against an assay budget needs a
ranking they can act on, and the field's papers are not organised around that. Two deliverables follow.

The first is a *calibrated expectation*. Taking the top 5% of our ranking recovers 24.7% of the true top
5%, a five-fold lift over random — but 7.7-fold on stability assays and 3.4-fold on activity assays, and
no advantage at all on the largest assay quartiles. A laboratory can use that profile to decide how much
of the ordering to trust for the property it cares about. No previous protein-fitness paper makes this
statement, because aggregate Spearman cannot express it.

The second is the boundary in the negative direction: 87 of 217 assays regressing, the one category that
regresses on average, and the size regime where the method is at parity with its predecessor. For a
practitioner the boundary is worth more than the mean, because it is the difference between trusting a
ranking on a familiar assay family and being surprised by it on a new one.

**Challenges tackled with AI.** Three, in increasing difficulty. The ranking problem is small-data-per-task
learning — a few thousand variants per assay, often fewer — so the question is regularisation and
transfer, not capacity. It is a distribution-shift problem: assays differ in family, assay type and
dynamic range, which is exactly why the field reached for adaptive weighting and why we show that
weighting has no headroom. And it is a representation problem: the signal lives in the difference between
two sequences and in the local structural neighbourhood, which is what the encoder in §4 exploits.

**Challenges of using AI in this domain.** Wet-lab validation is the binding constraint and it is slow
and expensive, so the field reports against retrospective benchmarks and hopes the ranking transfers; we
have not closed that gap. Assay data is heterogeneous in ways metadata does not capture — two stability
assays on one protein can disagree in sign — so a category-averaged metric can look stable while
individual assays move sharply in both directions. And the benchmark ecosystem rewards leaderboard
improvement over characterisation: no venue asks where a model fails, yet that is what a domain user
needs most.

**On our use of ProteinGym.** The track prefers domain-specific data to existing benchmarks, so we state
what our use of ProteinGym adds rather than only takes. We verify it end to end — reproducing its
published per-assay values for a reference method on 217 of 217 assays and confirming its folds are
bit-identical to the released files — we publish per-mutant predictions for all 696,311 variants so the
evaluation is reproducible without our code, and we characterise its difficulty structure across
categories, sizes and splits. A reader can use that characterisation without adopting our method.

---

## Notes

**Placement.** §7.1, before the audience-specific paragraphs. Every sentence maps to a measured number:
a domain-contribution paragraph that gestures at "accelerating discovery" is what these criteria warn
against.

**What this does not fix.** A domain co-author. The CFP asks for domain-affiliated authors to write this
material, and a computational team writing it is second-best by construction. It closes the
*insufficient-discussion* objection, not the *absent-collaborator* one.
