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
with a scoring script under `scripts/scoring_DMS_supervised/`, the supervised analogue of the `scoring_DMS_zero_shot`
example. All model scores are published: `raw_score_file.csv` is the per-assay file your performance script reads
directly, and `fused_per_mutant.csv.gz` covers every benchmarked mutant — 2,088,933 rows, 696,311 mutants across the
three schemes and all 217 assays. Run on the per-assay file, your evaluation script reports 0.694, +0.037 over Kermut.

One thing I would rather flag than let you find: the per-mutant file is a re-run, not the run behind that 0.694.
Re-scoring it gives 0.692, with per-assay differences averaging 0.008. The per-assay file is what our reported number
rests on and is the one your script's aggregation matches; if you need the per-mutant predictions to agree with it
exactly, I can tell you what regenerating them from the submitted configuration would take.

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
- The figure quoted is 0.694 because that is what the benchmark's own script returns on
  `submission/raw_score_file.csv`; the output is in `submission/official_outputs/`. The email says explicitly that the
  released per-mutant file is a separate re-run and re-scores to 0.692, because a maintainer running it will find that
  and should hear it from us.
- Regenerating per-mutant predictions that match the submission was attempted and is not possible from what remains
  on disk. Best reconstructions against the 651 submitted units: 0.4 Kermut + 0.4 AMK + 0.2 encoder gives mean r
  0.7054 (per-unit difference 0.0116), the rank-space blend 0.7058, eight-seed averaging 0.7072; the submitted file is
  0.7123. No single stored prediction file comes closer than 0.0618. The exact configuration is not recoverable, so
  the honest framing is the one in the email rather than a claim that the release reproduces the submission.
