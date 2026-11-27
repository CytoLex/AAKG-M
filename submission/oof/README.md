# Analysis inputs

Every number in sections 3 and 4 of the paper is computed from the files listed here. They are not in this
repository because of their size; include them in the supplementary upload from the locations given, or regenerate
the indel bundle with the script below.

## substitution bundle

```
oof_bundle.csv.gz          86 MB
```

Per-variant out-of-fold predictions for the five experts on ProteinGym's supervised substitution benchmark.

| column | meaning |
|---|---|
| `assay` | ProteinGym `DMS_id` |
| `scheme` | `fold_random_5` / `fold_modulo_5` / `fold_contiguous_5` |
| `variant_id` | mutation string |
| `fold` | which of the five published folds the variant belongs to |
| `category` | functional category |
| `target` | measured fitness (renamed `y` by the analysis scripts) |
| `D`, `Kermut`, `Kseq`, `AMK` | per-expert predictions, z-scored within assay × scheme |

2,088,933 rows. Plus `ref_slim.csv` (16 KB): UniProt identity and coarse functional category per assay, which the
aggregation groups by.

**What it reproduces.** The oracle bound and its null (§3.3), the out-of-sample estimability and shrinkage results
(§3.4), the predictor and its permutation null (§3.4), the rank-average baseline (§3.2), and the thirteen
expert-into-pool points behind Figure 1 (§4.4). Every script in `kdd/headroom/` reads this file.

Note that the released `fused_per_mutant.csv.gz` in `submission/predictions/` is the *fused* prediction, which is what
sections 4.3, 5.1 and 5.2 use. It is not a substitute for this bundle: the bundle holds the individual experts, which
is what the allocation analysis needs.

## indel bundle

```
indel_bundle.csv.gz        1.9 MB
```

61,209 variants over 69 assays' worth of prediction files, of which 65 join cleanly to fold metadata, with the three
published indel experts whose out-of-fold predictions ship with ProteinGym-indels.

**This is a subset, not the whole benchmark.** ProteinGym's indel benchmark is 66 assays and 287,207 variants; the
compact file here keeps only variants that have both a finite measurement and a fold assignment in the released fold
files. The analysis that produces the paper's +0.0084 therefore runs on 65 assays and 61,209 variants, which is what
the paper's indel section should say. A reader comparing the two counts is seeing a subset plus a join filter, not a
discrepancy.

| column | meaning |
|---|---|
| `assay` | ProteinGym `DMS_id` |
| `variant_id` | mutated sequence |
| `y` | measured fitness |
| `expert0`, `expert1`, `expert2` | the three published experts |

**What it reproduces.** The indel oracle bound of +0.0084 and the per-assay constant of 0.8450 that carry §3.5.
Verified against the paper's own figure: oracle 0.8534, constant 0.8450, headroom **+0.0084**.

Regenerate it from the public ProteinGym indel release with `kdd/indel_benchmark/` scripts; the compact form above is
what those scripts consume.

## ablation scores

```
ablation_scores.tar.gz     0.68 MB
ablation_scores.json
```

Eighty per-unit score tables, one per ablation run, each holding `variant, seed, alpha, dim, assay, scheme,
category, r`. Aggregating any of them the official way returns the number the paper reports, and the JSON file
records the official score of every run so a reader can match a table to a claim without re-deriving it.

**What it reproduces.** The representation ladder of §4.1 — site vector 0.4318, three layers 0.4641, ±4
neighbourhood 0.4796, plus reference-minus-mutant terms 0.5823 — the feature and control-arm ablations of §4.2
(distillation, the per-category residual, the shared-branch control), and the co-distillation and residual-expert
results of §4.4. Regenerating these by retraining each view is possible but unnecessary: the per-unit scores are what
the aggregates are computed from.

## indel scores

The four JSON files in `kdd/indel_benchmark/` (`unified.json`, `official_folds.json`, `ablation.json`, `ref3.json`)
carry the indel numbers: `alpha_0.9/student_mean` = 0.88576 and `alpha_0.9/nested` = 0.89339 are the 0.8858 and 0.8934
of §3.5, and `three_expert/nested` = 0.84379 with `oracle` = 0.85217 are the pooled figures.

## The fusion ladder

Not released as weights, but regenerable: `headline_seeds.py` recomputes the ladder from the eight `preds_union_s*.csv`
files, giving 0.690808 for the previous fusion and 0.694984 for the eight-seed average, a gain of +0.004175 with a
95% CI of [+0.002234, +0.006376]. Note that this script aggregates by category mean, while the headline figure
reproduces under UniProt-then-category; the two conventions differ by about 0.004 on this panel, which is why §4.3
quotes the released artifact rather than the ladder.

Run it with `PREFIX=preds_union` — the default in the script appends a second `_s` to the prefix and silently finds no
per-seed files.

## Verifying a number

```bash
export AAKG_DATA=/path/to/these/files          # directory holding the two bundles and the ref tables
python3 kdd/headroom/one_pipeline.py           # §3.3: +0.0051 against +0.0122
python3 kdd/headroom/consistent.py             # §3.4: estimability and shrinkage
python3 kdd/headroom/baselines.py              # §3.2: the rank-average baseline
python3 kdd/headroom/pilotB.py                 # §4.4: the thirteen points, r = +0.786
```

Each script reads `AAKG_DATA` and writes its numbers to stdout; none needs a GPU.
