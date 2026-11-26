# Verification ledger

Which numbers in the paper reproduce from released artifacts, which do not, and what each would need. This exists
because three separate discrepancies were found by checking rather than by reading, and the first two were only
visible once a *control* number was checked against the same pipeline.

## Reproduces from the official script run (`submission/official_outputs/`)

These are ProteinGym's own evaluation script run on `submission/raw_score_file.csv`, so they are the benchmark's numbers
rather than a reimplementation of them.

| number | where | value | status |
|---|---|---|---|
| our fusion, official | §4.3, §5.1 | 0.694 | reproduces |
| Kermut, official | §4.3, §5.1 | 0.657 | reproduces |
| per-scheme breakdown | §5.1 | 0.784 / 0.674 / 0.625 | reproduces |
| per-category scores | §5.2 | 0.851 … 0.642 | reproduces |

## Does not reproduce: the released per-mutant predictions

The file in `submission/predictions/fused_per_mutant.csv.gz` is **a different run** from the score file that produced
the numbers above. Across all 651 assay-by-scheme units, **none** agree, and the mean absolute difference is 0.0083;
re-scoring it gives 0.692 rather than 0.694, and 0.115 / 0.241 / 0.346 for the top-of-list figures rather than
0.119 / 0.247 / 0.350.

This is a defect in the release, not in the paper: the claims rest on the submitted score file, which is included, and
the paper's limitations now say so. The proper repair would be to publish the predictions that generated that file,
which cannot be reconstructed from what remains on disk.

## Reproduces from the expert bundle (`submission/oof/`)

| number | where | value | status |
|---|---|---|---|
| allocation headroom | §3.3 | +0.0051 [0.0038, 0.0066] | reproduces |
| its null | §3.3 | −0.0064 [−0.0083, −0.0043] | reproduces |
| expert lever | §3.3 | +0.0122 [0.0099, 0.0144] | reproduces |
| rank-average baseline | §3.2 | 0.6942 vs 0.6952, [−0.0031, +0.0011] | reproduces |
| out-of-sample estimability and shrinkage | §3.4 | +0.0047 → +0.0051 etc. | reproduces |
| predictor and its permutation null | §3.4 | +0.628 vs +0.002 | reproduces |
| thirteen expert-into-pool points, r = +0.786 | §4.4, Fig. 1 | +0.786 | reproduces |
| the noise / shuffle / negate controls | §3.2, §4.4 | +0.0000 each | reproduces |

## Reproduces from the indel bundle

| number | where | value | status |
|---|---|---|---|
| indel oracle minus constant | §3.5 | +0.0084 | reproduces (oracle 0.8534, constant 0.8450) |

## Reproduces from the ablation score tables (`submission/oof/ablation_scores.tar.gz`)

Eighty per-unit tables plus the official score of each run. Aggregating a table the official way returns the
reported number.

| number | where | value | status |
|---|---|---|---|
| representation ladder | §4.1 | 0.4318 / 0.4641 / 0.4796 / 0.5823 | reproduces |
| distillation, category residual, shared-branch control | §4.2 | +0.114, +0.024, +0.0214 | reproduces |
| co-distillation and residual expert | §4.4 | +0.0136, weight 0 | reproduces |

## Reproduces from the indel score files

| number | where | value | status |
|---|---|---|---|
| encoder on indels | §3.5 | 0.88576 | reproduces (`unified.json`) |
| three-expert blend | §3.5 | 0.89339 | reproduces |
| pooled experts, nested and oracle | §3.5 | 0.84379 / 0.85217 | reproduces |

## The last item: regenerated, but under a different convention

The per-fold fusion weights were the only unreleased input. They are not missing after all — `headline_seeds.py`
reproduces the ladder from the eight per-seed prediction files:

```
previous fusion (D, Kermut, AMK, the older expert)   0.690808
new fusion, eight seeds averaged                     0.694984
gain +0.004175   95% CI [+0.002234, +0.006376]
```

Two things keep this out of the paper as the headline. It uses **category-mean** aggregation, while the headline
figure of 0.6917 uses **UniProt then category** — the convention that reproduces Kermut's 0.657028 exactly. And the
ladder that was originally reported (0.685538 / 0.691130 / 0.693311) matches neither this regeneration nor the
released artifact, so it cannot be restored as written.

So the item is resolved as *understood* rather than *published*: nothing is unreleased, one number was convention-
dependent, and §4.3 stays on the released artifact because that is the convention a reader can check against Kermut.

## A bug found in the project's own script

`headline_seeds.py` defaults `PREFIX` to `preds_union_s` and then appends `_s{s}`, so it looks for
`preds_union_s_s1.csv` and silently skips all eight seeds, printing only the previous fusion's score. Running it with
`PREFIX=preds_union` reproduces the full ladder. The default should have been `preds_union`; anyone regenerating this
number from the repository would have got eight "no predictions" lines and no explanation.

## A correction this pass forced

The representation ladder had never been checked against its own score tables. Two of its four rungs were right
(0.4641 and 0.4796 against the reported 0.464 and 0.480); the endpoints were not, and the reported 0.467 made the
"stacking more layers is negative" claim true. Retrained values give site 0.4318 to layers 0.4641, which is
**positive**, and the differential step is 0.5823 − 0.4796 = +0.103 rather than +0.116. Section 4.1 and contribution
2 now carry the reproduced values and the corrected reading: stacking helps a little, context helps a little, and the
change carries three times either.

## What this ledger got wrong, and why it is recorded here

Three "corrections" in earlier drafts of this file were themselves wrong, and they are kept as a record rather than
deleted:

1. **"The headline compares two populations."** It does not. The 0.694 came from ProteinGym's script on the submitted
   score file; the 0.6917 came from re-scoring the released per-mutant file, which is a different run.
2. **"The utility table came from a reconstruction."** It came from the submitted model. Recomputing from the release
   gives different figures because the release is not the submitted model.
3. **"Section 5.2's 0.119 / 0.247 / 0.350 were never reproducible."** They are reproducible from the submitted file;
   they are not reproducible from the release.

All three share one root cause: treating the released per-mutant predictions as the model the paper reports. That
assumption was never checked, and it is wrong — none of the 651 assay-by-scheme units agree between the two, with a
mean absolute difference of 0.0083.

The check that settles it takes one command and the file was in the submission the whole time:
`submission/official_outputs/Summary_performance_DMS_substitutions_Spearman.csv` is the benchmark script's own output
and carries 0.694 and 0.657 directly.

The lesson is narrower than "verify numbers": **verify that the artefact you are verifying against is the artefact the
claim came from.** Two files, both plausible, both about the same model, one of which is a re-run.

## The representation ladder remains corrected

That one stands on its own evidence — the per-unit tables each run writes alongside its scores — and is unaffected by
the above. Site vector 0.4318 to 0.4641 with three layers is positive, the differential step is +0.103, and §4.1 and
contribution 2 carry those values.
