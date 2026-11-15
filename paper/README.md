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

## The headline, in one place

Both rungs are computed by running the official `performance_DMS_supervised_benchmarks.py` on our
score file, so they are on the same scale as the leaderboard:

| tier | number | delta | why it is written this way |
|---|---:|---|---|
| **claim** | **0.692** | **+0.035 over Kermut (0.657)** | single model, one seed: the equal-compute comparison |
| **deployed** | **0.694** | **+0.037 over Kermut** | expert averaged over eight training seeds |

Kermut is one of the four experts, so both deltas measure what complementary experts add on top of
the published leader, not a new single-model record. Per-scheme values: 0.782 / 0.671 / 0.624
(single) and 0.784 / 0.674 / 0.625 (seed-averaged).

An earlier set of drafts quoted 0.6963 / 0.6985 from a per-assay category-balanced protocol without
the UniProt grouping. Those are superseded; where they survive below they are labelled as the looser
protocol.

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
