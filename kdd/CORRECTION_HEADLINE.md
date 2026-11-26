# Correction of the correction: the headline is 0.694, and it was right the first time

## What I got wrong

For two rounds this file recorded that the paper's headline of 0.694 was inflated, that the correct figure was
0.6917, and that the paper had compared two different populations. All three of those conclusions were wrong, and
they were wrong for one reason: I assumed the released per-mutant predictions were the model that the paper reports.

They are not. They are a different run.

## How it was settled

The submission contains `official_outputs/Summary_performance_DMS_substitutions_Spearman.csv`, the output of
ProteinGym's own `performance_DMS_supervised_benchmarks.py` run on `submission/raw_score_file.csv`:

```
cytomuta-preview  0.694  0.784 0.674 0.625  |  0.642 0.653 0.693 0.632 0.851
Kermut            0.657  0.745 0.633 0.593  |  0.605 0.611 0.670 0.582 0.817
```

Those are the paper's original numbers, to the digit. The benchmark's own code, on the submitted file, is the
authority, and it says 0.694 against 0.657 — a lead of 0.037, not 0.0347.

The two sets are not the same run. Comparing per-assay, per-scheme Spearman across all 651 units, **0 of 651 agree**
and the mean absolute difference is 0.0083; the submitted scores average 0.7123 against 0.7087 for the release.

## How the mistake happened, in order

1. I recomputed the aggregation from the released predictions and got 0.6917, and treated that as the truth.
2. Kermut recomputed to 0.657028 under the same code and matched the published 0.657, which I took as proof the
   pipeline was right — but agreement to three decimals on one model does not validate a reimplementation of a
   bias-corrected aggregate. It only shows the two happen to round the same.
3. Seeing 0.6917 sit nearer the 182-assay figure, I diagnosed a population mix-up and "corrected" the paper.
4. The diagnosis survived because it was internally coherent. It was still built on step 1.

The check that would have prevented it: `official_outputs/` is in the submission and contains the answer directly.

## What the paper says now

Restored: 0.694 against 0.657 in §4.3 and the introduction, the script's per-scheme figures in §5.1, and the script's
category table in §5.2. The §4.3 wording now says the number came from the benchmark's script rather than from our
reaggregation, and the output ships with the submission.

The limitations carry the gap that this episode did expose, and it is real: **the released per-mutant predictions are
not the submitted score file.** They differ on every one of the 651 units, by 0.008 on average, and re-scoring them
gives 0.692 rather than 0.694. The submitted score file is what the claims rest on; the per-mutant file is offered as
a convenience and is now labelled as such. That is a genuine defect in the release, and the correct repair is to
publish the predictions that generated the submitted scores, which is not possible from what remains on disk.
