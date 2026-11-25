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

61,209 variants over 65 assays, with the three published indel experts whose out-of-fold predictions ship with
ProteinGym-indels.

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

## What is not here, and what that means

Two sets of numbers in the paper do not reproduce from these files alone, and the paper says so where they appear:

- **The per-fold fusion weights** behind the ablation ladder in §4.3. The ladder was removed for this reason; §4.3
  quotes only the released fusion's score.
- **The representation ladder in §4.1** (0.467 / 0.464 / 0.480 / 0.596) comes from the training pipeline's view
  ablations. Regenerating it means retraining each view. It is not claimed as reproducible from the release.

## Verifying a number

```bash
export AAKG_DATA=/path/to/these/files          # directory holding the two bundles and the ref tables
python3 kdd/headroom/one_pipeline.py           # §3.3: +0.0051 against +0.0122
python3 kdd/headroom/consistent.py             # §3.4: estimability and shrinkage
python3 kdd/headroom/baselines.py              # §3.2: the rank-average baseline
python3 kdd/headroom/pilotB.py                 # §4.4: the thirteen points, r = +0.786
```

Each script reads `AAKG_DATA` and writes its numbers to stdout; none needs a GPU.
