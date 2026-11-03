# AAKG-M: Assay-Adaptive Kernel Gate

**Fixed-configuration empirical result, not a fully nested official benchmark.**

AAKG-M learns a **label-free assay-context gate** over three frozen protein-
fitness experts:

- `D`: additive structure kernel;
- `Kermut`: sequence/kernel expert;
- `AMK`: assay-adaptive mixed structure kernel.

For each assay, the gate maps a 17-dimensional context vector (assay size,
expert means/stds/correlations, sequence length, DMS number, category) to a
softmax weight over the three experts:

```text
g_a = softmax(MLP(c_a))
pred_i = g_{a,D} z(D_i) + g_{a,K} z(Kermut_i) + g_{a,A} z(AMK_i)
```

The gate sees **no target labels from the held-out assay**.  At meta-test time,
only the assay context and the frozen expert predictions are used.

## Headline result

651 assay × scheme units, 217 assays, official-valid category-balanced
aggregation (per-unit Spearman → mean per `coarse_selection_type` → mean over
the five categories):

| Method | Score |
|---|---:|
| AMK | 0.662033 |
| D | 0.656215 |
| Kermut | 0.662540 |
| fixed D+Kermut Blend | 0.683193 |
| nested contextual meta | 0.687426 |
| AAKG-L (linear gate) | 0.687533 |
| **AAKG-M (MLP-64, 3-seed mean)** | **0.688024 ± 0.000027** |

Seed details:

| seed | official |
|---|---:|
| 20261029 | 0.687994 |
| 1 | 0.688046 |
| 2 | 0.688034 |

Paired assay-cluster bootstrap (AAKG-M seed 1):

| contrast | point | 95% CI |
|---|---:|---:|
| AAKG-M − Blend | +0.003911 | [+0.002340, +0.005198] |
| AAKG-M − Kermut | +0.027001 | [+0.023501, +0.030335] |
| AAKG-M − AMK | +0.021241 | [+0.016275, +0.027845] |
| AAKG-M − AAKG-L | −0.000054 | [−0.001070, +0.001029] |

The gain over the fixed blend is small but supported.  The gain over AAKG-L is
a statistical tie, and **Contiguous is a tie with Blend** (+0.0003).  Do not
claim SOTA.

## What “official” means here

This repository reports an **official-metric, assay-held-out estimate for a
fixed AAKG-M configuration**.  That is enough for an empirical methods paper
if the caveats are disclosed.

It is **not** a fully nested official benchmark number, because:

1. **Architecture selection was not nested.**  The MLP-64 configuration was
   chosen after observing the 217-assay results.  The 5-fold estimate is nested
   over assay holdout, not over architecture/hyperparameter search.
2. **Base expert predictions are cached OOF.**  D, Kermut and AMK are frozen
   out-of-fold predictions; they are not retrained inside every meta-fold.
3. **No fresh external cohort.**  All 217 assays were used during development.
4. **No untouched test server.**  This is a cross-assay CV estimate, not a
   leaderboard submission.

For a strict official claim, lock the configuration before the final run or
nest architecture selection inside each outer fold, and retrain/regenerate all
base experts under the same folds.

## Protocol

- 5-fold **assay-held-out** CV, stratified by `coarse_selection_type`.
- The gate for a held-out assay is trained only on the other assays.
- Assay-balanced MSE: each assay contributes equally regardless of variant count.
- Context features and prediction z-scores use **no target labels**.
- No per-assay kernel selection at meta-test time.
- Official aggregation over 3 schemes; no cross-scheme reuse.

## Reproduce

The base OOF tables and contract are **not redistributed** (size and upstream
licenses).  Put them under `data/` or set `AAKG_ROOT`.

Expected layout:

```text
data/
  oof_predictions.csv
  kseq_oof_predictions.csv
  contract.json
  dev20_units/<assay>/<scheme>/oof.csv
  amk197_units/<assay>/<scheme>/oof.csv
```

`oof_predictions.csv` columns:

```text
assay, scheme, variant, fold, target_common_std,
D_common_std, Kermut_common_std
```

`kseq_oof_predictions.csv` columns:

```text
assay, scheme, variant, fold, K_feature_common_std
```

Each `oof.csv` under the unit roots needs:

```text
variant_id, fold, AMK_common
```

Run the headline configuration:

```bash
export AAKG_ROOT=$PWD
python aakg_m.py \
  --model mlp --hidden 64 --dropout 0.1 \
  --ctx ext --sched cosine --lr 1e-3 --epochs 100 \
  --seed 1 --out results/run
```

`--seed 1` reproduces the seed-1 score `0.688046`; the headline `0.688024` is
the mean over the three seeds above.

## Files

```text
aakg_m.py                 gate training + official aggregation
meta_stack.py             OOF loading, features, context, metrics
AAKG_M_REPORT.md          full method report, ablations, limitations
aakg_m_217.png            summary figure
results/result.json       seed-1 metrics and category/scheme breakdown
results/per_unit.csv      per assay × scheme × category scores
results/assay_weights.csv mean gate weights per assay
results/history.json      training history
requirements.txt
```

## Caveats

1. **Kermut-dependent.**  Kermut is one of the three experts.  This is not a
   Kermut-free method.
2. **Not a pure two-expert fusion.**  It is a three-expert gated ensemble.
3. **Small effect.**  +0.0048 over Blend; Contiguous is a tie.
4. **Architecture selected on the same 217 assays.**  The headline number is
   selection-optimistic relative to a fully nested protocol.
5. **No trained weights included.**  The gate has 1,347 parameters and is
   retrained by `aakg_m.py`.
6. **No fresh cohort.**  External validation is still missing.

## License

No license is granted for this private research release.  Contact the CytoLex
organization before reuse or redistribution.
