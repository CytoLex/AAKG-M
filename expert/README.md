# Expert pipeline (result 2)

These three scripts produce the encoder expert and the 217-assay fusion score reported in the
main README under *Result 2*.

## Environment variables

Nothing is hard-coded; point these at your own copies.

| variable | used by | meaning |
|---|---|---|
| `AAKG_DATA` | `esm_mut_head.py` | directory holding the per-assay feature archives |
| `AAKG_BUNDLE` | `esm_mut_head.py`, `headline_seeds.py` | path to `oof_bundle.csv.gz` (per-variant rows with fold columns) |
| `AAKG_WORK` | `headline_seeds.py` | working directory holding the bundle and the cached expert predictions |
| `AAKG_RUNS` | `make_seedavg.py` | directory holding `preds_*_s{1..8}.csv` |
| `PREFIX` | `headline_seeds.py` | filename prefix of the prediction set to evaluate |

## Order of operations

```bash
# 1. train the encoder expert (one seed per run)
python esm_mut_head.py --variant union --src esm650 --alpha 0.9 --lowrank 8 \
    --seed 1 --out runs/e1.json --units runs/u1.csv --preds runs/p1.csv

# 2. repeat for seeds 2..8, then average the per-variant predictions
python make_seedavg.py            # writes preds_savg_s1.csv

# 3. nested four-expert fusion on the 217-assay panel
PREFIX=preds_savg python headline_seeds.py
```

## What each script needs

| script | inputs | notes |
|---|---|---|
| `esm_mut_head.py` | OOF bundle (`assay, scheme, variant_id, target, category, folds`) + per-assay feature npz files | builds union features, runs distillation, trains the head and the category low-rank residual |
| `make_seedavg.py` | `preds_*_s{1..8}.csv` | averages the eight seeds; **the average is over z-scored per-assay predictions** |
| `extract_mutant_layers.py` | ESM-650 weights + per-assay `probability.pt` (wild-type sequence) | builds the mutant-sequence features: L20/L30/L33 site vectors plus ±4-residue neighbourhood means |
| `esm650_map.py` | `esm650_merged.bin` | maps the published ESM-650 state dict onto the `esm` package's `ESM2` module layout |
| `headline_seeds.py` | bundle + `preds_*_s*.csv` + cached expert predictions | nested simplex fusion, per-unit Spearman, category-balanced aggregate, two-level bootstrap |

## Reproducing the headline number

`headline_seeds.py` prints, per seed, the nested fusion score, and then a two-level bootstrap CI for
the delta against the fixed old-expert baseline. With the averaged expert there is a single
"seed", so the CI it prints is **assay-level only** — the seed-level spread has to be read off the
eight single-seed runs instead.

## Flags that matter

| flag | meaning |
|---|---|
| `--variant union` | full feature set (mutant layers + WT layers + neighbourhood + `mut`/`mut−wt`) |
| `--src esm650` | use the ESM-650 features (the ESM-C variants were tested and rejected) |
| `--alpha 0.9` | distillation weight; 0 disables it |
| `--lowrank 8` | category-specific rank-8 residual branch; **rank 4 gives the same score** |
| `--teacher-csv` | override the teacher (used by the co-distillation experiment, which did not help) |
| `--target-csv` | override the regression target (used by the residual-expert experiment, which got zero weight) |

## Not included

The feature extraction itself (`extract_mutant_layers.py`) and the ESM-650 checkpoint loader are not
in this repository: the former needs the wild-type sequences, which are not redistributable, and the
latter needs the 2.6 GB ESM-650 weights. The per-assay feature archives are available from the
authors on request.
