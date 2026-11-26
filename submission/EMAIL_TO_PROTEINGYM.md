# Email to the ProteinGym maintainers

**To:** Pascal Notin `<pascal.notin@cs.ox.ac.uk>`
**Cc:** Daniel Ritter `<danieldritter1@gmail.com>`
**Subject:** ProteinGym supervised baseline — materials ready (issue #129 / PR #130)

---

Pascal,

I opened issue #129 and PR #130 on 16 November adding cytomuta-preview as a supervised substitution baseline; the PR
was marked ready for review on the 18th. It is a new model rather than a fix, so it needs a judgement call from
someone with merge rights, and the repository has picked up a backlog — I wanted to put the materials in front of you
directly rather than leave a notification buried.

Everything the submission checklist asks for is public:

- Per-mutant scores: `submission/predictions/fused_per_mutant.csv.gz` in `CytoLex/AAKG-M` — 2,088,933 rows, which is
  696,311 mutants × 3 fold schemes across all 217 substitution assays.
- The score file is in ProteinGym's expected format, so the official evaluation script runs on it unmodified.
- As a control, the same pipeline reproduces Kermut's released per-assay table on **217 of 217 assays** with a mean
  absolute difference of 0.0, so the numbers can be checked without taking ours on trust.

The model is frozen and its scores are final; I am not asking for review of a moving target. If the format, the file
size, a column naming convention, or a subset of assays would make the review easier, I can reshape it quickly —
whatever is least work for you.

If the answer is simply that this is not something the repository is taking on right now, that is a useful thing to
know too, and a one-line reply is enough.

Best,
[Your name]
[Affiliation]
[GitHub handle: Zane12518]

---

## Sending notes

- Send plain text, no attachments — the data is already at a URL.
- Do not follow up before two weeks pass, and then only once, with no more than two sentences.
- The addresses come from the `∗Correspondence` line of the NeurIPS 2023 PDF, so they are the paper's own publication
  contacts rather than addresses inferred from lab websites.
- Pascal Notin is the right first recipient because he is the first author, the most frequent author-committer (21
  commits against 6 for the next), and the identity attached to the repository's merge commits — that is, the person
  who has actually been merging contributions.
