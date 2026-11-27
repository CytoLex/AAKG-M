# IJCAI 2027 submission sheet

Target: AI4Science Special Track. Abstract deadline **2027-01-04**, full paper **2027-01-11**, both 23:59 AoE.

Everything below is filled except the author block, which needs the real names and affiliations.

## Confirmed requirements (from the IJCAI 2027 site)

| item | requirement | our state |
|---|---|---|
| Length | **9 pages total: 7 body + 2 references** | exactly 7 + 2 ✓ |
| Anonymity | double-blind, enforced by desk rejection | anonymous build ✓ |
| Abstract | separate submission on **4 January 2027** | text below, ready |
| Full paper | 11 January 2027 | built, verified |
| Notification | 21 April 2027 | — |
| Camera-ready | 24 May 2027 | — |

Note that the abstract deadline is a real, separate step seven days before the full paper. The AI4Science track page
still says the full call "will be published here soon", so the main-track rules above are what we are building to.

## Title

What Moves a Protein-Fitness Predictor: Disagreement, Not Accuracy

## Abstract (plain text, 255 words, 1,780 characters)

> Protein engineering screens rank candidate mutations, and the field's models combine several predictors, each new
> one added because it scores well on its own. Both habits are worth less than they look. We measure the two levers
> directly on ProteinGym. A per-assay oracle bounds what any weighting of a fixed expert pool can capture at +0.0051
> over a constant fitted on the other assays, against +0.0122 for adding one expert: allocation is 42% of the expert
> lever, the intervals do not overlap, and the bound replicates on the indel benchmark. It is a bound under Spearman:
> under top-of-list recall, the metric a campaign experiences, the transferable headroom is 2.8 times larger and
> standard weights capture a tenth of it; at top-1%, a threshold a campaign actually operates at, a rule that
> optimises that recall and then shrinks beats them by +0.0093. That loss is repairable — shrinkage toward the panel
> constant recovers the headroom without per-assay tuning — and it is concentrated: the top ambiguity quartile holds
> 57% of it. The expert lever is disagreement, not accuracy. Across thirteen expert-into-pool pairs, marginal value
> tracks disagreement at r = +0.786 while the weakest expert alone contributes the most and the strongest almost
> nothing, a measurement whose noise and shuffle controls each score zero. An encoder built on that principle —
> reference-minus-mutant features in a local neighbourhood, distilled and fused at four fixed weights — reaches 0.694
> on the official metric against 0.657 for the published leader. For the domain we report where the ranking can be
> trusted: the top 5% recovers 24.7% of the true top 5%, 7.7x on stability against 3.4x on activity, and parity on
> the largest quartile. We release per-mutant predictions for all 696,311 mutants.

No LaTeX markup survives in this version, so it can be pasted into a form field as-is.

## Suggested subject areas and keywords

IJCAI submission forms ask for subject areas from a list. If the AI4Science track supplies its own list, use it; if it
falls back to the main-track list, the closest are **Machine Learning: Ensemble Methods**, **Machine Learning:
Applications**, and **AI for Science**.

Keywords: protein fitness prediction, ensemble combination, deep mutational scanning, Spearman allocation bound,
shrinkage estimation, uncertainty in model selection

## Still needed from you

1. **Authors and affiliations** in submission order, with the corresponding author marked.
2. **Author conflicts** for the CMT/OpenReview form.
3. Confirmation that no co-author has submitted the same work elsewhere — IJCAI and ICML both forbid parallel
   submission, and ICML's deadline on 22 January falls inside the IJCAI review period.

## What I will not do without you

Upload, register, or enter the author block. Everything else on this sheet is final.

## One structural warning

The paper is at exactly 9 of 9 pages. Any change requested between now and 11 January needs an equal cut, and the
measured cut list in `SUBMISSION_DAY.md` is the place to take it from — the first three items total 254 words.
