# Attempt to reconstruct the structural-expert kernel

The submission does not need this — the scores are reproducible from the published prediction file —
but the question "can the kernel be rebuilt from its saved artifacts" came up, so here is what was
recovered and where it stopped.

## What the artifacts give you

`output/<assay>/<scheme>/fold<k>/` for every fold contains a complete record of one closed-form fit:

| artifact | content |
|---|---|
| `model.pt` | `alpha` (617, 1) kernel-ridge coefficients, `transforms.main` (10368) and `transforms.side` (9) with mean/std/active, `target_mean`, `target_std`, `train_indices`, `test_indices` |
| `inner_selection.pt` | `selected_lambda = 1e-4` and the inner-CV scores over six candidate values |
| `summary.json` | solver `Cholesky`, precision `float64`, `optimizer_steps = 0` — no gradient training |
| `predictions.csv` | per test variant: `target`, `prediction`, `prediction_normalized` |
| `side/<assay>.pt` | 9 hand-built side features per variant (LLR, MSA statistics), `target_access: false` |
| `features/esmc/<assay>/block_*.pt` | the 10,368-dim main features, 12 row-blocks of 64 x 10368 float32, backbone **ESM-C** |

So the model is kernel ridge regression, and every ingredient except the kernel function and the
callable feature pipeline is on disk in a readable form.

## What the reconstruction achieved

With feature blocks + side features + saved `alpha`, the test-set prediction under a kernel hypothesis
is `K(test, train) @ alpha`, compared against `prediction_normalized`:

| kernel | corr | RMSE |
|---|---:|---:|
| RBF on main, length scale 130 | 0.933 | 1.75 |
| RBF on side, length scale 2.7 | 0.725 | 1.14 |
| linear on main | 0.875 | — |
| **additive: 0.354 x RBF(main, 130) + 0.154 x RBF(side, 4)** | **0.936** | **0.345** |

The additive form with fitted amplitudes reaches **R^2 = 0.874** against the saved predictions.
The shape is right — the kernel is RBF-like over ESM-C block features with a smaller side component —
but 12.6% of the variance is unexplained, which is far from the exactness required to claim a
faithful reimplementation.

## Why it stopped there

1. **The kernel form is not fully identified.** Plausible remaining structure: a separate length
   scale per one of the 12 feature blocks, a Matern rather than Gaussian radial function, or an
   additional linear term. Each is a new experiment against the 145 saved predictions of one fold.
2. **The feature pipeline is not callable.** Features are computed at run time by the fitting code that
   is not on the compute share; only its cached outputs are. Those outputs are 430 MB per assay, so
   they cannot serve as the distribution format either.
3. **One fold is 145 test points.** That is enough to reject hypotheses, not enough to pin a dozen
   hyperparameters without overfitting the check.

## Conclusion

**Not reconstructed.** A reimplementation matching 87% of the variance would silently disagree with
the reported numbers, which is worse than not having one. The honest position is the one the
repository already takes: the structural experts are sealed, their scores are published per mutant,
and the reported benchmark numbers are reproducible from that publication.

If the fitting code is ever recovered, the recipe above is enough to verify a reimplementation
immediately: `K(test, train) @ alpha` must match `predictions.csv` to floating-point tolerance on
every fold.
