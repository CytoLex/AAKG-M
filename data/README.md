# Data layout and expert provenance

The repository does not redistribute the large prediction tables. This file describes exactly what
they are and how `meta_stack.py` loads them, so the numbers can be audited and the inputs rebuilt.

## What the four experts are, and where each column comes from

| column in `oof_bundle.csv.gz` | source file | source column | produced by |
|---|---|---|---|
| `D` | `oof_predictions.csv` | `D_common_std` | additive-structure kernel, fitted per assay and per fold |
| `Kermut` | `oof_predictions.csv` | `Kermut_common_std` | Kermut GP (Groth et al., 2024) |
| `Kseq` | `kseq_oof_predictions.csv` | `K_feature_common_std` | sequence kernel; not used in the final fusion |
| `AMK` | `{dev20_units,amk197_units}/<assay>/<scheme>/oof.csv` | `AMK_common` | assay-adaptive mixed structure kernel |
| `target` | `oof_predictions.csv` | `target_common_std` | the DMS score, standardised |

## Why these columns are out-of-fold

Two things establish it, one structural and one numerical.

**Structural.** `meta_stack.py` joins the expert tables on
`(assay, scheme, variant_id, fold)` with `validate="one_to_one"`, and raises if the merge changes the
row count or if the AMK keys are duplicated. A prediction that had been fitted on the full assay
could not be carried on a per-fold key without collision — the key itself asserts that each row's
prediction belongs to a specific held-out fold.

**Numerical.** Recomputing Kermut from its column reproduces the published ProteinGym supervised
row to three decimals on all three cross-validation schemes (0.7455 / 0.6328 / 0.5928 against
0.745 / 0.633 / 0.593). An in-sample fit would not land on the published out-of-fold numbers.

## What is not here

The upstream kernel fitting code lives in a separate project directory
(`cytolex-kernel-full217`, `cytolex-kernel-readout`), whose per-assay outputs are organised as
`<assay>/<fold_scheme>/`, consistent with the per-fold keys above. That pipeline is not
redistributed in this repository, and neither are the prediction tables themselves (they are
multi-gigabyte). Both are available from the authors on request, and both are research-use only under
[LICENSE-WEIGHTS.md](../LICENSE-WEIGHTS.md) — the Apache-2.0 licence covers the code, not the tables.

## Rebuilding the bundle

```bash
export AAKG_ROOT=$PWD
python meta_stack.py           # writes data/oof_bundle.csv.gz from the tables above
```

The bundle is what every script in `expert/` and the gate code read, so once it exists the whole
pipeline is reproducible from this repository plus the two prediction tables.
