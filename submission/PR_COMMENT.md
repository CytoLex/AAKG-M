# Comment for PR #130 — posted

**Posted 2026-11-27 10:03 UTC** as comment `7215431262`, https://github.com/OATML-Markslab/ProteinGym/pull/130#issuecomment-7215431262

Post on the pull request rather than the issue: the PR is where a merge decision is made, and a comment there puts the
notification where the action is.

It tags `@pascalnotin` and `@danieldritter`, both verified as repository committers from the commit history, and both
co-first authors on the ProteinGym paper. Two mentions on a stalled PR with two active maintainers is proportionate;
tagging more people would not be.

---

@pascalnotin @danieldritter — flagging this for review. It has been open since 16 November and marked ready on the
18th, and it needs a call from someone with merge rights rather than anything further from me.

**What it adds.** `cytomuta-preview` as a supervised substitution baseline: the scoring script under
`proteingym/baselines/cytomuta/` and the shell script under `scripts/scoring_DMS_supervised/`, the supervised analogue
of the `scoring_DMS_zero_shot` example.

**What can be checked.**

- `submission/raw_score_file.csv` — per-assay scores in the format your performance script reads directly. Run on it,
  the script reports **0.694**, which is +0.037 over Kermut.
- `submission/predictions/fused_per_mutant.csv.gz` — per-mutant scores covering every benchmarked mutant: 2,088,933
  rows, 696,311 mutants across the three schemes and all 217 assays.
- As a control, recomputing Kermut's predictions through the same pipeline reproduces your published per-assay table
  on **217 of 217** assays, mean absolute difference 0.00026 and maximum 0.0005, every residual inside the
  three-decimal rounding of the released file.

**If it helps.** I can reshape the format, file size, column naming, or a subset of assays — whichever makes review
least work. And if this is simply not something the repository is taking on right now, a one-line reply is enough.

---

## Notes

- The comment carries no reference to email. Two attempts bounced, one at Oxford's broken redirect and one at Harvard
  with "user unknown", and telling the thread about that would make the comment about our delivery problems instead of
  the submission.
- The figure 0.694 is attached explicitly to `raw_score_file.csv`, the per-assay file the script consumes. The
  per-mutant file is described by coverage only, for the reason recorded in `EMAIL_TO_PROTEINGYM.md`: it is a
  different run and re-scores to 0.692.
- The licence split is not repeated here because `## Reproducibility and licence` in the PR body already states it, and
  a comment that recaps the body reads as padding.
- If nothing comes back, the next step is not another comment. The submission is complete and public; the thread is
  where a maintainer will look when the repository resumes.

## Outcome

Posted successfully as `Zane12518`. The rendered thread shows the two mentions resolving to the right accounts, and
the comment sits directly under "marked this pull request as ready for review November 18, 2026 06:29", which is the
right place for a maintainer scanning the thread.

Nothing further to do on delivery. The submission is complete and public; the thread is where a maintainer will look
when the repository resumes, and that is now the only outstanding dependency.
