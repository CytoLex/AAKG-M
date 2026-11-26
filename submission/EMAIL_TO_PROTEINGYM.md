# Email to the ProteinGym maintainers

**To:** Pascal Notin `<pascal_notin@hms.harvard.edu>`
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

Against the requirements in your README for new baselines: the PR adds
`proteingym/baselines/cytomuta/compute_fitness.py` with a scoring script under `scripts/scoring_DMS_supervised/`, the
supervised analogue of the `scoring_DMS_zero_shot` example. All model scores are published: `raw_score_file.csv` is the
per-assay file your performance script reads directly, and `fused_per_mutant.csv.gz` covers every benchmarked mutant —
2,088,933 rows, 696,311 mutants across the three schemes and all 217 assays. Run on the per-assay file, your
evaluation script reports 0.694, +0.037 over Kermut.

The evaluation is checkable without taking our word for it: recomputing Kermut's predictions through the same pipeline
reproduces your published per-assay table on 217 of 217 assays, mean absolute difference 0.00026 and maximum 0.0005,
every residual inside the three-decimal rounding of the released file.

The weights and the structural-expert tables are research-use only under the repository's `LICENSE-WEIGHTS.md`, while
the code is Apache-2.0. The per-mutant scores are fully public, so the submission can be scored without any access
request, but if you would want to regenerate scores for new mutants we would need to arrange that explicitly — I am
happy to discuss what would make it workable.

If the format, file size, column naming, or a subset of assays would make review easier, I can reshape it quickly. And
if this is simply not something the repository is taking on right now, that is useful to know — a one-line reply is
enough.

Best,
Zane Tang
CytoLex · github.com/Zane12518

---

## Sending notes

- Send plain text, no attachments; the data is at a URL.
- The first attempt went to `pascal.notin@cs.ox.ac.uk`, the address printed in the 2023 PDF, and bounced: Oxford's
  redirect service forwards that alias to `scro3775@nexus.ox.ac.uk`, an account that no longer exists. Pascal has moved
  from Oxford to Harvard Medical School, so the working address is `pascal_notin@hms.harvard.edu` (note the
  underscore), which appears on three papers from December 2024, June 2025 and December 2025. `notin@hms.harvard.edu`
  also appears and is a reasonable second choice.
- The Cc to Daniel Ritter's Gmail produced no bounce, so the message may already have been seen by a co-first author
  who is also a repository committer.
- Pascal Notin is the measured choice: first author, most frequent author-committer (21 commits against 6 for the
  next), and the identity attached to the repository's merge commits. Aaron Kollasch, whom the repository name would
  suggest, does not appear in the commit history at all.
- Every figure in the body is traceable: 0.694 and +0.037 come from the benchmark's own script run on
  `submission/raw_score_file.csv` (output in `submission/official_outputs/`); 0.00026 / 0.0005 and 217 of 217 are the
  Kermut control recorded in `PR_DESCRIPTION.md`.
- The email describes `fused_per_mutant.csv.gz` by coverage only and does not claim it reproduces 0.694, because it
  does not: re-scoring it gives 0.692, with per-assay differences averaging 0.008. No stored file rebuilds the
  submitted predictions — the closest, eight-seed averaging, reaches mean r 0.7072 against the submission's 0.7123 —
  so if a maintainer asks for matching per-mutant scores, the honest answer is that it needs a retraining run.
- Do not follow up for two weeks, then once, in two sentences.
