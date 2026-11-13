# Paper drafts

Working drafts for the method paper. The prose is in Chinese with English camera-ready blocks at
the end of each section file; the English blocks are what would be submitted.

| file | content |
|---|---|
| `FINAL_ABSTRACT.md` | abstract, three lengths (195 / 120 / 34 words) plus an evidence table |
| `INTRODUCTION.md` | introduction, seven paragraphs, plus a contributions table |
| `SECTION_5_1_5_2.md` | §5.1 the positive result and §5.2 the gate's failure, with English blocks |
| `SECTION_5_3_5_4.md` | §5.3 why the expert pays and §5.4 the headroom diagnostic, with English blocks |
| `DRAFT_SKELETON.md` | full-paper skeleton: section order, figure assignments, forbidden phrasings |
| `PROPOSAL_METHOD.md` | the same method written up as a thesis-proposal chapter (technical route + plan) |

## The two-tier headline, in one place

Every file uses the same convention, and it must not drift:

| tier | number | delta | why it is written this way |
|---|---:|---|---|
| **claim** | **0.6963 ± 0.0004** | +0.0054 over the previous four-expert fusion (95% CI [+0.0035, +0.0076]); +0.0084 over the published gate | single model, eight seeds: the only tier with a seed-level interval and an equal-compute comparison |
| **deployed** | **0.6985** | +0.0077 and +0.0106 respectively | adds seed averaging (eight models); reported as a deployment step, like the gate repository's weight-averaged variant |

The sentence "positive in all eight seeds" belongs to the **claim** tier only. The deployed tier has
no seed dimension.

## What `§8.x` means

Cross-references like `§8.53` or `§8.90` point at an internal experiment log that is not distributed
with this repository. It records, for every number quoted here, the script that produced it, the
seed range, and the paired statistics. Everything it supports is reproducible from `expert/` plus
the numbers in the main README; the log is available from the authors on request.

## Status

These are **drafts**, not a submitted manuscript. No venue has been chosen and nothing here has been
through peer review. Where the drafts state a limitation, the limitation is real and is repeated in
the main README's caveat list (coverage is 182 of 217 assays, hyperparameters were not nested, the
gain is aggregate rather than universal).
