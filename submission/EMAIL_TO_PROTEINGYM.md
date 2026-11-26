# Email to the ProteinGym maintainers

**To:** Pascal Notin `<pascal.notin@cs.ox.ac.uk>`
**Cc:** Daniel Ritter `<danieldritter1@gmail.com>`
**Subject:** cytomuta-preview — supervised baseline submitted (issue #129, PR #130)

---

Pascal,

I opened issue #129 and PR #130 adding cytomuta-preview as a supervised substitution baseline, marked ready for
review on 18 November. It is a new model rather than a fix, so it needs someone with merge rights to make a call, and
I know the queue is long — I am writing so that the materials are in front of you rather than sitting in a
notification.

- Issue: https://github.com/OATML-Markslab/ProteinGym/issues/129
- Pull request: https://github.com/OATML-Markslab/ProteinGym/pull/130

Against the requirements in your README for new baselines: the PR adds `proteingym/baselines/cytomuta/compute_fitness.py`
together with the scoring script under `scripts/scoring_DMS_supervised/`, and all model scores for all mutants are
published — 2,088,933 rows, 696,311 mutants across the three fold schemes, all 217 assays, in the format your
performance script reads unmodified. On your aggregation it reports 0.6917, which is +0.035 over Kermut.

The evaluation is checkable without taking our word for it: recomputing Kermut's predictions through the same pipeline
reproduces your published per-assay table on 217 of 217 assays, mean absolute difference 0.00026 and maximum 0.0005,
every residual inside the three-decimal rounding of the released file.

One thing I should flag rather than let you find: the weights and the structural-expert tables are research-use only
under the repository's `LICENSE-WEIGHTS.md`, while the code is Apache-2.0. The per-mutant scores are fully public, so
your script can score the submission as-is, but if you would want to regenerate scores for new mutants we would need
to arrange access explicitly — I am happy to discuss what would make that workable.

If the format, file size, column naming, or a subset of assays would make review easier, I can reshape it quickly.
And if this is simply not something the repository is taking on right now, that is useful to know — a one-line reply
is enough.

Best,
Zane Tang
CytoLex
GitHub: Zane12518

---

## Sending notes

- Send plain text with no attachments; the data is at a URL.
- The addresses are the `∗Correspondence` line of the NeurIPS 2023 PDF, not addresses inferred from lab pages.
- Pascal Notin is the measured choice: first author, most frequent author-committer (21 commits against 6 for the
  next), and the identity attached to the repository's merge commits. Aaron Kollasch, who the repository name would
  suggest, does not appear in the commit history at all.
- Do not follow up for two weeks, and then once, in two sentences.
- Before sending, the PR body must say 0.6917 rather than 0.6933: the maintainers' own script corrects for the biases
  their README describes, so a reviewer running it would otherwise find a number 0.0016 below what we claim.
