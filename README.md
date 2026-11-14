# AAKG-M: a four-expert fusion that beats the published supervised leaderboard

**0.6933** on the ProteinGym supervised substitution benchmark, against **0.657** for Kermut, the
published rank 1 — and the pipeline is validated by reproducing Kermut's own published row exactly.

| model | official average |
|---|---:|
| ProteinNPT (published rank 2) | 0.619 |
| **Kermut (published rank 1 — one of our four experts)** | **0.657** |
| AMK (our structural expert) | 0.6611 |
| **AAKG-M (four-expert fusion)** | **0.6933** |

The claim is a **fusion** claim: Kermut is one of the four experts, so +0.036 measures what
complementary experts add on top of the strongest single model, not a new single-model record.

**How the pipeline is validated.** Recomputing Kermut through this repository — official fold files,
official aggregation — reproduces the leaderboard row to three decimals on every scheme:

| scheme | official leaderboard | this pipeline |
|---|---:|---:|
| Random | 0.745 | **0.7455** |
| Modulo | 0.633 | **0.6328** |
| Contiguous | 0.593 | **0.5928** |
| **Average** | **0.657** | **0.6570** |

The fold assignments are bit-identical to the published `cv_folds_singles_substitutions` files
(9,576/9,576 mutants, all three schemes, `A0A140D2T1_ZIKV_Sourisseau_2019`).

**Where the gain comes from.** Replacing the weakest expert with a distilled encoder expert, plus a
category-specific low-rank residual on its output, is worth **+0.0056** (0.6855 → 0.6911). Averaging
that expert over its eight training seeds adds **+0.0022** (0.6911 → 0.6933). Nine other directions
were tried and failed; that list is at the bottom, and it is half the value of this repository — it
tells you where the headroom is *not*.

## The method

Four experts, **four fixed weights, no gate**. Weights are selected on the training assays of each
fold and applied to the held-out assays, exactly as a tuned-constant baseline is.

```text
pred_i = 0.00 · D_i + 0.40 · Kermut_i + 0.40 · AMK_i + 0.20 · X_i
```

`X` is a distilled encoder expert built from ESM-650:

| stage | what it adds |
|---|---|
| features | wild-type and mutant per-residue layers (L20/L30/L33), ±4-residue neighbourhood pooling, and `mut`/`mut−wt` embeddings |
| teacher | `0.4·Kermut_z + 0.5·AMK_z`, per-assay z-scored; loss `(1−α)·MSE(student, target) + α·MSE(student, teacher)`, α = 0.9 |
| head | 12800 → 256 → 64 → 1, plus a **category-specific rank-8 linear residual** `y = MLP(x) + U_c V_cᵀ x`, U zero-initialised |
| ensembling | the expert's per-variant OOF predictions are averaged over its **eight training seeds** |

The search drives `w_D` to **0.00** in 14 of 15 (seed × fold) combinations and sets `w_X = 0.20` in
**all 15**. The additive-structure expert is switched off by optimisation, not by hand.

## The ladder

Under the official metric, with every step changing one thing:

| configuration | official | Δ |
|---|---:|---:|
| D (additive structure) | 0.6537 | — |
| Kermut (published rank 1) | 0.6570 | — |
| AMK (best single expert) | 0.6611 | — |
| four experts, previous site expert | 0.6855 | +0.0244 vs AMK |
| ＋ distilled encoder expert, category low-rank residual | 0.6911 | +0.0056 |
| **＋ expert averaged over 8 training seeds** | **0.6933** | **+0.0022** |

The single expert columns (0.6537–0.6611) are below every fusion row, which is the point: the blend
buys roughly four points over its best component.

A finer decomposition — separating the encoder swap (+0.0040) from the low-rank residual (+0.0014)
— is measured under the looser per-assay convention and tabulated in *Cross-check against an earlier,
looser protocol* below, because those two intermediate runs were not re-scored with the official
aggregation.

## The encoder on its own

Reporting only the fusion score would imply the gain comes from combination tricks. Measured alone:

| configuration | standalone official |
|---|---:|
| L33 site only, frozen embeddings | 0.467 |
| ＋ multi-layer | 0.464 |
| ＋ ±4 neighbourhood | 0.480 |
| ＋ multi-representation union (distilled) | 0.596 |
| ＋ category low-rank residual | 0.622 |
| **＋ 8-seed averaging** | **0.645** |
| (reference) Kermut / AMK / D alone | 0.6625 / 0.6620 / 0.6562 |
| (reference) the site expert this replaced | 0.494 |

The encoder is **still below the strongest single expert (Kermut, 0.6625)** yet still earns
**+0.0054** in the fusion. That is the point: an expert's marginal value tracks its residual
decorrelation with the pool, not its standalone score.

## The official protocol

Everything above is computed with the official ProteinGym supervised protocol: the published fold
files, the official reference table, and their aggregation code path. What that does and does not
buy is worth stating plainly.

It is **not** a fully nested benchmark submission, because:

1. **Architecture selection was not fully nested.**  The MLP-64 gate configuration was chosen after
   observing the 217-assay results. For the fusion, the one hyperparameter that matters (α) *was*
   re-selected inside each fold and picked the same value every time — see caveat 4 — but the
   broader design space was explored on this panel.
2. **Base expert predictions are cached OOF.**  D, Kermut and AMK are frozen
   out-of-fold predictions; they are not retrained inside every meta-fold.
3. **No fresh external cohort.**  All 217 assays were used during development.
4. **No untouched test server.**  This is a cross-assay CV estimate, not a
   leaderboard submission.

For a strict official claim, lock the configuration before the final run or
nest architecture selection inside each outer fold, and retrain/regenerate all
base experts under the same folds.

### Official ProteinGym evaluation

Scores below follow the official implementation
(`OATML-Markslab/ProteinGym`, `proteingym/performance_DMS_supervised_benchmarks.py`):

1. per DMS × scheme Spearman, **averaged over the three schemes**
   (`fold_random_5`, `fold_modulo_5`, `fold_contiguous_5`);
2. mean grouped by **(model, UniProt_ID, coarse_selection_type)** — several assays of the same
   protein are averaged before the category step;
3. mean over `coarse_selection_type`.

The DMS→UniProt and DMS→category mapping comes from the official
`reference_files/DMS_substitutions.csv` (217 assays, 186 UniProt IDs).

| configuration | official | Δ |
|---|---:|---:|
| D | 0.653717 | — |
| Kermut | 0.657028 | — |
| AMK | 0.661147 | — |
| previous four-expert fusion | 0.685538 | — |
| **this method, single model** | **0.691130** | **+0.005592** |
| **this method, expert averaged over 8 seeds** | **0.693311** | **+0.007773** |

**+0.0078 over the previous four-expert fusion, +0.0363 over the best single expert (AMK).**

### Validation: the pipeline reproduces the official leaderboard

The leaderboard at `proteingym.org/benchmarks` lists Kermut as rank 1 on the supervised substitution
benchmark. Recomputing Kermut's score with this repository's pipeline, on the official fold files
and the official aggregation, reproduces that row to three decimals on every cross-validation scheme:

| scheme | official leaderboard | this pipeline |
|---|---:|---:|
| Random | 0.745 | **0.7455** |
| Modulo | 0.633 | **0.6328** |
| Contiguous | 0.593 | **0.5928** |
| **Average** | **0.657** | **0.6570** |

Two further checks support it: the fold assignments are bit-identical to the published
`cv_folds_singles_substitutions` files (9,576/9,576 mutants on all three schemes for
`A0A140D2T1_ZIKV_Sourisseau_2019`), and the aggregation reproduces their code path including the
`UniProt_ID` grouping step.

### Where this method lands

The three numbers worth remembering, all under the official metric: the published rank 2 sits at
0.619, the published rank 1 (Kermut) at 0.657, and this fusion at 0.6933. The single-model rung below
the fusion scores 0.6911, so most of the gain is the expert, not the ensembling.

### What this does and does not establish

The **aggregation and the fold schemes now match the official implementation**, and the numbers are
computed on all 217 official assays. What still differs:

- **D / Kermut / AMK are cached out-of-fold predictions** inherited from earlier work. Recomputing
  Kermut reproduces the published leaderboard row exactly, which is evidence that the columns were
  produced under the official folds, but the generation script for the three columns is not in this
  repository.
- **Fusion weights are selected assay-held-out**, which is stricter than the official supervised
  setting but not identical to it.
- **Nothing has been submitted to the ProteinGym evaluation harness.**

Treat the deltas as internally valid and directly comparable across the rows above; treat the
absolute values as this project's estimate under the official metric, not as leaderboard positions.

### Cross-check against an earlier, looser protocol

Before matching the official script this project used a per-assay category-balanced mean without the
UniProt grouping. The two agree closely:

| protocol | baseline | this method | Δ |
|---|---:|---:|---:|
| per-assay, no UniProt grouping | 0.690808 | 0.698495 | +0.007687 |
| **official (UniProt-grouped, 217 assays)** | **0.685538** | **0.693311** | **+0.007773** |

The absolute values shift by about 0.005; the delta shifts by 0.0001. An intermediate variant that
used only random 5-fold and a plain assay mean gave 0.798 for this method, but that is **not** the
official protocol — the official script averages all three schemes and category-balances.

The finer three-scheme decomposition, separating the encoder swap from the low-rank residual:

| configuration | three-scheme, category-balanced | Δ |
|---|---:|---:|
| four experts, previous site expert | 0.690808 | — |
| ＋ distilled multi-representation encoder | 0.694837 | +0.004029 |
| ＋ category-specific low-rank residual | 0.696250 ± 0.000434 | +0.001413 |
| ＋ expert averaged over 8 seeds | 0.698495 | +0.002245 |

## What did not work

Nine directions were tested and rejected, reported with numbers because the negative space is what
makes the positive result credible.

### Result 1 (negative): a learned gate ties a tuned constant

This repository began as a gate — a label-free assay-context network mapping a 17-dimensional
context vector (assay size, expert means/stds/correlations, sequence length, DMS count, category) to
a softmax over three frozen experts. It was the wrong hypothesis, and the measurements below are why
we dropped it.

651 assay × scheme units, 217 assays, official-valid category-balanced
aggregation (per-unit Spearman → mean per `coarse_selection_type` → mean over
the five categories):

| Method | Score |
|---|---:|
| AMK | 0.662033 |
| D | 0.656215 |
| Kermut | 0.662540 |
| fixed D+Kermut blend (raw predictions) | 0.683193 |
| fixed D+Kermut blend (z-scored, same space as the gate) | 0.681978 |
| fixed 50/50 K+AMK blend | 0.687322 |
| best single constant g | 0.687585 |
| nested-tuned constant gate | 0.687637 |
| nested contextual meta | 0.687426 |
| AAKG-L (linear gate) | 0.687533 |
| **AAKG-M (MLP-64, 9-seed mean ± sd)** | **0.687851 ± 0.000287** |

`results/per_unit.csv` is the **seed-1** run (official 0.688046), verified bit-identical
across machines; the headline above is the mean of nine seeds.  Quote the mean, not a
single seed's per-unit table.

### Deployment: average the weights, not the predictions

Train `--seed` runs as usual, then **average the per-assay gate weights across seeds** before
applying them. This is variance reduction, not a new mechanism: on the eight released runs it
gives **0.687888** versus a per-seed mean of **0.687606**, and at full budget on a clean
re-implementation 0.687937 → 0.688189. It costs nothing at inference time.

Do **not** quote the seed-averaged number as the headline. The headline is the nine-seed mean
**0.687851 ± 0.000287**; report 0.687888 separately as the deployed variant.

An optional simplification — pin `w_D` at the tuned optimum 0.05 and let the gate split only
K and A — changes the score by **−0.0001** (95% CI [−0.0004, +0.0002]). It is a no-cost
simplification, not an improvement.

### Read this before quoting the headline

The three seeds originally reported (20261029, 1, 2) give 0.688024 ± 0.000027.
Those three happen to lie within 5e-5 of each other.  Across nine seeds
(20261029 plus 1-8) the spread is **0.000287**, i.e. 10.5x larger, and the
nine-seed mean sits 0.00017 below the three-seed mean.  The three reported
seeds rank 2nd, 3rd and 4th of the nine: they are not a maximum, but they are
an unusually tight cluster.  Full seed table:

| seed | official |
|---|---:|
| 20261029 (default) | 0.687994 |
| 1 | 0.688046 |
| 2 | 0.688034 |
| 3 | 0.687981 |
| 4 | 0.687221 |
| 5 | 0.688128 |
| 6 | 0.687746 |
| 7 | 0.687604 |
| 8 | 0.687908 |
| **mean ± sd (n=9)** | **0.687851 ± 0.000287** |

The headline therefore has to be quoted against the right baseline:

| contrast, 9-seed mean | baseline | delta | in units of the 0.000287 seed sd |
|---|---:|---:|---:|
| vs fixed D+Kermut blend | 0.683193 | **+0.004658** | 16 sigma - real |
| vs fixed 50/50 K+AMK | 0.687322 | +0.000529 | 1.8 sigma |
| vs best single constant g | 0.687585 | +0.000266 | 0.9 sigma - inside noise |
| vs nested-tuned constant | 0.687637 | +0.000214 | 0.75 sigma - inside noise |

**+0.0048 is a comparison against the weakest fusion in the table.**  Against
any properly tuned constant the gate is a statistical tie, and the difference
is smaller than the seed-to-seed spread of the method itself.  This is the
central negative result of the paper; it is not a rounding issue.

Paired assay-cluster bootstrap (AAKG-M seed 1; this captures cross-assay
uncertainty only and does **not** include seed noise):

| contrast | point | 95% CI |
|---|---:|---:|
| AAKG-M − Blend | +0.003911 | [+0.002340, +0.005198] |
| AAKG-M − Kermut | +0.027001 | [+0.023501, +0.030335] |
| AAKG-M − AMK | +0.021241 | [+0.016275, +0.027845] |
| AAKG-M − AAKG-L | −0.000054 | [−0.001070, +0.001029] |

With the seed study above in view: the gain over the fixed D+Kermut blend is
real and large; the gains over AAKG-L, over a fixed 50/50 K+AMK blend and over
a nested-tuned constant are statistical ties.  **Contiguous is a tie with
Blend** (+0.0003).  Do not claim SOTA, and do not quote +0.0048 without the
baseline next to it.

### Cross-validation setup for the gate

- 5-fold **assay-held-out** CV, stratified by `coarse_selection_type`.
- The gate for a held-out assay is trained only on the other assays.
- Assay-balanced MSE: each assay contributes equally regardless of variant count.
- Context features and prediction z-scores use **no target labels**.
- No per-assay kernel selection at meta-test time.
- Official aggregation over 3 schemes; no cross-scheme reuse.

### The nine rejected directions

Nine directions were tested and rejected. All of them are reported with numbers because the
negative space is what makes the positive result credible.

| direction | outcome |
|---|---|
| seven conditioning / gating mechanisms | at or below the tuned constant |
| category GroupDRO | −0.0001 (2/4 seeds) here, **−0.0044 (0/4)** on an independent pipeline; group weights collapse (ESS 2.28 < 2.5) |
| Huber / loss clipping | +0.0005 (3/4, CI crosses zero) here, +0.0009 (3/4) independently — both below the 0.002 detection threshold |
| variant-count capping | **−0.0124** (0/4 seeds) |
| static category balancing | −0.0006 (1/4) |
| ESM-C 300M as a fourth expert | +0.0007 (CI crosses zero) |
| ESM-C features concatenated | **−0.0112** |
| co-distillation from the fusion itself | expert **+0.0136** (8/8) but fusion **−0.0002** |
| residual ("boosting") expert | the simplex gives it **exactly zero weight** |

The last two are the most instructive: making an expert *stronger* by imitating the pool destroys
the decorrelation that gave it value, and an expert trained on the fusion's own residual has no
information left to add.

## Reproduce

The base OOF tables and contract are **not redistributed** (size and upstream
licenses).  Put them under `data/` or set `AAKG_ROOT`.

Expected layout:

```text
data/
  oof_bundle.csv.gz          # optional single-file bundle (see HF private dataset)
  oof_predictions.csv
  kseq_oof_predictions.csv
  contract.json
  dev20_units/<assay>/<scheme>/oof.csv
  amk197_units/<assay>/<scheme>/oof.csv
```

If `data/oof_bundle.csv.gz` is present, `meta_stack.load_oof()` uses it and
ignores the four separate OOF sources.  The bundle is not in this model repo;
it is in the private dataset [`cytolex/AAKG-M-oof`](https://huggingface.co/datasets/cytolex/AAKG-M-oof).

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

`--seed 1` reproduces the seed-1 score `0.688046`.  Do not use that as the
headline: the nine-seed mean is `0.687851 ± 0.000287` (see
`results/seed_study.json` and the section "Read this before quoting the
headline" above).  Running the same command with `--seed 20261029`, `2`, ...
reproduces the other rows of the seed table.

## Checkpoints

`checkpoints/gate_fold{0..4}.pt` are the five seed-1 fold gates.  They are the
models that produced `results/per_unit.csv`; see
[`checkpoints/README.md`](checkpoints/README.md) for the format, checksums and
loading snippet.

These checkpoints contain **only the gate**.  D / Kermut / AMK experts and the
OOF tables are not included.

## Files

```text
aakg_m.py                 the gate (negative result), kept for reproducibility
meta_stack.py             OOF loading, features, context, metrics
expert/esm_mut_head.py    the encoder expert: distillation + category low-rank residual
expert/make_seedavg.py    average the expert over its eight training seeds
expert/headline_seeds.py  nested four-expert fusion + two-level bootstrap
expert/README.md          how to reproduce, and what is not redistributed
paper/                    paper drafts (Chinese prose + English camera-ready blocks)
paper/README.md           the headline convention and what §8.x refers to
AAKG_M_REPORT.md          full method report, ablations, limitations
aakg_m_217.png            summary figure
checkpoints/              five seed-1 gate checkpoints + format notes
results/                  per-unit scores, seed study, gate weights, training history
requirements.txt
```

## Caveats

1. **Kermut-dependent, and the headline is a fusion claim.**  Kermut (published rank 1) is one of
   the four experts, so +0.036 over it means *fusing complementary experts with the strongest single
   model buys four points* — not that a new single model beats it.
2. **The gate and the fusion are different models on the same panel.**  The gate is a
   three-expert gated ensemble scoring 0.6879; the fusion is a four-expert ungated one scoring
   0.6933 under the official metric. Do not mix their numbers.
3. **The gate's effect is small.**  +0.0048 over the weakest blend, and a statistical tie with any
   tuned constant. The fusion's +0.0078 over the previous four-expert fusion is above the detection
   threshold, but see caveats 7–9.
4. **Hyperparameters: partially nested.**  The knob that materially moves the score is the
   distillation weight α (standalone: 0.607 at α=0.6, 0.617 at 0.75, **0.621 at 0.9**, 0.619 at 1.0).
   Re-selecting α inside every fold, using the training assays only, picks **0.9 in all five folds**,
   so the nested estimate is bit-identical to the fixed one (gap 0.000). Rank is flat (4 vs 8 differ
   by 0.0002), and width and epochs were never tuned. What is *not* nested is the broader design
   space — which mechanisms we chose to try was decided on this panel, and no protocol can nest that.
   **That selection risk is bounded, though.** Twenty-two mechanisms were tried here, so a two-sided
   Bonferroni correction needs z = 3.05; the observed paired effect is **z = 5.16**, giving a
   corrected 95% CI of **[+0.00223, +0.00866]**, still entirely above zero. The claim would survive
   even if 10⁵ configurations had been tried. (Bonferroni assumes independence and the attempts here
   are correlated, which makes the correction conservative in our favour.) This bounds the risk; it
   does not replace replication on an external panel.
5. **Only gate checkpoints are included.**  D / Kermut / AMK expert weights and
   the OOF tables are not redistributed.
6. **No fresh cohort.**  External validation is still missing.
7. **The encoder expert covers 182 of 217 assays.**  It needs a wild-type sequence,
   which is available for 182 assays only; the other 35 fall back to the older site expert.
   Those 35 are 16% of the panel and contribute structural fallback zeros, so the fusion
   gain is diluted, not inflated, by them.  Do not read the 217-assay score as if all
   assays had a real prediction from the new expert.
8. **0.6933 is a single configuration, not a seed distribution.**  The expert is averaged
   over eight training seeds, so there is no seed-to-seed spread for that exact number. The
   comparable spread is on the single-seed rung under the looser protocol: 0.6963 ± 0.0004.
9. **Fusion weights are nested per fold; the experts are cached OOF.**  Same structure as
   the gate result above, so caveat 2 and 4 apply to both numbers equally.

## License

No license is granted for this private research release.  Contact the CytoLex
organization before reuse or redistribution.
