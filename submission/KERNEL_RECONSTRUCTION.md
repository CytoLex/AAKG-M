# The structural-expert kernel: recovered and verified

**Status: reconstructed.** `submission/kernel.py` implements the kernel, and running it against the
saved artifacts reproduces the stored predictions to floating-point precision.

## What the artifacts expose

Every fold directory (`output/<assay>/<scheme>/fold<k>/`) records a complete closed-form fit:

| artifact | content |
|---|---|
| `model.pt` | `alpha` (617, 1), `transforms.main` (10368) and `.side` (9) with mean/std/active, `target_mean`, `target_std`, `train_indices`, `test_indices` |
| `inner_selection.pt` | `selected_lambda = 1e-4` plus the inner-CV scores over six candidates |
| `summary.json` | solver `Cholesky`, precision `float64`, `optimizer_steps = 0` — no gradient training |
| `predictions.csv` | per test variant: `target`, `prediction`, `prediction_normalized` |
| `side/<assay>.pt` | 9 side features plus `wt` and `mut` per variant, `target_access: false` |
| `features/esmc/<assay>/block_*.pt` | the main features: 12 row-blocks of 64 x 10368 float32, backbone ESM-C |

So everything except the kernel function was on disk, readable, including `alpha` and a set of saved
predictions to check against.

## The kernel

Found in `kernel_readout_v1.py` of the fitting project:

```python
def kernel(left, right):
    out = None
    for key in ("main", "side"):
        d2 = ||x||^2 + ||y||^2 - 2xy            # squared euclidean distance
        block = exp(-0.5 * d2 / x.shape[1])     # length scale^2 == block dimension
        out = block if out is None else out + block
    for key in ("wt", "mut"):
        out = out + 1[wt equal] + 1[mut equal]  # identity indicators
    return out / 4
```

The squared length scale of each block is that block's own dimension — 10368 for `main`, 9 for
`side` — and two identity indicators carry the rest. Both blocks are standardised with the per-block
`mean`/`std` from `transforms`, inactive coordinates zeroed.

## Verification

`K(test, train) @ alpha` for `MAFG_MOUSE_Tsuboyama_2023_1K1V` / `fold_random_5` / `fold0`, against
`predictions.csv`:

| quantity | value |
|---|---:|
| correlation | **1.0** |
| RMSE | **2.4e-14** |
| max absolute difference | **8.2e-14** |

Floating-point exact over all 145 test variants.

## Why a hypothesis search had stalled first

Fitting a kernel family against those 145 predictions reached R^2 = 0.874 with free amplitudes and a
grid over length scales. It could not have done better: `exp(-0.5 d^2 / 10368)` and
`exp(-0.5 d^2 / 130^2)` differ by about 3% in effective length scale, which at n = 145 is far inside
the noise, and the missing pieces were structural — the two identity indicators and the `/4`
normalisation — not a hyperparameter.

The artifacts were never the bottleneck. The source was, and it was on the user home volume
(`/inspire/hdd/global_user/.../cytolex-mutation-context-v02-preparation-20260930/`) rather than under
the project share that the benchmark outputs live on.

## What this changes for the submission

Nothing about the published numbers, but it removes the last unknown: the structural experts are no
longer sealed. Given the cached feature blocks, `submission/kernel.py` plus the per-fold `alpha`
reproduces their predictions exactly.

The per-mutant prediction file remains the recommended distribution path — it needs no features and
no 430 MB per-assay caches — but anyone who wants to rescore new mutants now has the kernel.
