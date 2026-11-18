# Limitations and Ethical Considerations

The KDD AI for Sciences track requires a separate section under this title. Draft below; every number
is taken from the analyses in this directory, and every limitation is one we measured rather than
anticipated.

---

## Draft

### Limitations

**The ranker is unreliable on most functional categories.** Top-of-list recall at 5% is 0.38 for
stability assays but 0.17 for activity assays — a 2.2x spread — and activity is what an
enzyme-engineering campaign most often cares about. Aggregate Spearman hides this; a user reading only
the headline will over-trust the method on function-oriented assays.

**The gain disappears on large assays.** Splitting the 217 assays into quartiles by mutant count, the
mean improvement over the previous fusion is +0.0073 on the smallest quartile and +0.00003 on the
largest, with a 50% regression rate on the largest. Assays with more measurements — the ones most
likely to be run at scale — are exactly where the method is at parity with its predecessor.

**A substantial minority of assays regress.** 87 of 217 assays (40%) score worse than the previous
four-expert fusion, with a median improvement across all assays of only +0.0016. The aggregate gain is
carried by a subset, and we do not have a feature that predicts in advance which subset.

**Coverage is partial, and the uncovered assays are coupled rather than independent.** The distilled
encoder requires a wild-type sequence and covers 182 of 217 assays; the remaining 35 fall back to an
older expert. Those 35 still show a mean improvement of +0.0029, but not because of their own
predictions: the nested weight search fits one weight vector per fold over *all* training assays, so
changes elsewhere move the weights applied to them. Reported per-assay deltas for those 35 should not
be read as evidence about their own representation.

**The structural experts are inherited, not retrained inside each outer fold.** Their kernel is
recovered and verified to floating-point precision (max absolute difference 8.2e-14 against the saved
per-fold predictions), and the published per-mutant scores make every reported number reproducible —
but a fully nested protocol would retrain them within each fold, which we did not do. The one
hyperparameter that materially matters, the distillation weight, was re-selected inside each fold and
chose the same value in all five; the broader design space, however, was explored on this panel.

**One benchmark family, no prospective validation.** All results are on ProteinGym substitution
assays. There is no held-out cohort from a different source, and no wet-lab experiment. Whether
top-of-list lift translates into hit-rate lift in a real screening campaign is untested; it is the
next experiment, not a claim.

### Ethical considerations

**Dual use.** Protein fitness predictors can be applied to gain-of-function engineering. Our method
ranks a user-supplied set of single-residue variants; it does not generate sequences, does not perform
design, and provides no structure-to-function capability beyond what the public ProteinGym baselines
already offer. We nevertheless note that ranking is the step that decides which candidates a laboratory
synthesises, and that this is the point at which such models are most directly useful. We release
predictions for the existing public assays only.

**Data.** All assays are previously published deep mutational scanning datasets distributed by
ProteinGym. No new experimental data, no human subjects, no clinical material, and no institutional
review was required. The wild-type sequences used for feature extraction are the ones distributed with
the public DMS files.

**Bias and domain shift.** The panel is skewed toward particular protein families, model organisms and
assay types, and our per-category results show that performance is not uniform across them. A
practitioner applying this to a protein family absent from ProteinGym should expect the large-assay
behaviour — parity, not improvement — rather than the headline.

**Released artifacts.** We publish per-mutant predictions for all 696,311 mutants, the code that
reproduces every reported number, and the recovered kernel for the structural experts. The expert
prediction tables remain research-use only, because they derive from third-party methods. We consider
the predictions themselves the artifact of record: they are what a reviewer or a practitioner needs,
and they are sufficient to re-derive every number in the paper.

**Use of generative AI.** The paper's prose and analysis scripts were developed with AI assistance.
Per the track's authorship policy this is disclosed in the submission form, and the authors take
responsibility for all content.

---

## Notes for the authors

**Specificity is the currency here.** A limitation that names a number ("+0.00003 on the largest
quartile") reads as measurement; one that says "performance may vary" reads as evasion. Keep the
numbers in.

**Do not add a "future work" paragraph to soften these.** The section should read as a boundary map,
not as an apology. The discussion in §7 is where the forward-looking material belongs.

**The dual-use paragraph is doing real work.** Reviewers on an AI-for-science track look for it. State
the capability precisely, state what we did and did not release, and do not overclaim the mitigation.

**Check the 2027 CFP for the exact section title.** KDD 2026 required "Limitations and Ethical
Considerations"; if the wording changes, the section heading must match it exactly — a desk-reject
criterion is formatting and required sections.
