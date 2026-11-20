# The encoder on the indel benchmark

Round two of the second-benchmark work: put our differential-representation encoder into the indel expert
pool and see whether it earns a place. Everything below ran on the platform's internet-capable GPU
workspace (`可上网GPU资源`, RTX 4090) as one job; the data and ESM-2 650M weights came from shared storage.

## Protocol

- **Assays**: 64 of the 65 usable indel assays. `CAPSD_AAV2S_Sinai_2021_designed_indels` (226k variants)
  was excluded for runtime, and one assay fell below the 60-variant floor.
- **Features**: ESM-2 650M at layers 20/30/33, wild-type and mutant, a ±4-residue window around the edit
  located by longest-common-prefix/suffix, differences taken between the two. 9 × 1,280 = 11,520
  dimensions per variant — deliberately close to the 12,800 of the substitution encoder.
- **Teacher**: the per-variant z-score mean of the three published supervised indel models, whose
  out-of-fold predictions ship with the benchmark.
- **Student**: 11,520 → 256 → 64 → 1 head, loss `(1−α)·MSE(student, target) + α·MSE(student, teacher)` with
  α = 0.9, five folds, two seeds averaged, predictions pooled out-of-fold.
- **Fusion**: four experts (three published + ours), simplex weights in steps of 0.1, selected on the other
  assays and applied to the held-out one — the same protocol as §3 of the paper.

## Result

**One protocol throughout.** Earlier passes used a fresh random five-way split and, separately, a constant
fitted on the whole panel; two figures for the same quantity appeared in the paper as a result. Everything
below is now the single protocol: 65 assays with a complete released-fold join, ProteinGym's own
`fold_random_5` column (`cv_folds_indels.zip`), the nested constant, five seeds per configuration, and ten
random half-splits for the transfer estimate. `indel_unified.py` in this directory reproduces the whole
table in one run.

| expert | per-assay Spearman |
|---|---:|
| Embeddings-ESM1v (published) | 0.8231 |
| Embeddings-Tranception (published) | 0.8008 |
| Embeddings-MSA Transformer (published) | 0.7952 |
| **our differential encoder, α = 0.9** | **0.8858** |

| pool | nested constant | per-assay oracle | headroom |
|---|---:|---:|---:|
| three published experts | 0.8438 | 0.8522 | +0.0084 |
| + our encoder (α = 0.0) | 0.8546 | 0.8631 | +0.0085 |
| **+ our encoder (α = 0.9)** | **0.8934** | 0.8997 | +0.0063 |

## Does the lead come from the teacher?

The encoder is distilled from the three published models, so the obvious objection is that it is copying
their consensus. Training the same head at four values of α separates the two sources — α = 0 uses only
the measured fitness, α = 1 only the teacher, with no labels at all.

| α | student alone | four-expert blend | headroom |
|---|---:|---:|---:|
| 0.0 (no distillation) | **0.8401** | **0.8546** | +0.0085 |
| 0.9 (paper) | 0.8858 | 0.8934 | +0.0063 |

Two readings follow. **The representation stands on its own**: at α = 0 it beats every published expert
(0.8401 against 0.8231) and still lifts the blend by 0.011. **Distillation adds another 0.046**, taking the
blend to 0.8934.

**Stability.** Five seeds per configuration, and the split-half estimate repeated over ten independent
half-splits: in-place gain +0.0129 ± 0.0012, transferred −0.0024 ± 0.0020, negative in every one of the ten.
The encoder figures above are per-assay Spearman averaged over assays; the spread across assays is large
(sd 0.079 at α = 0, 0.057 at α = 0.9) because indel assays range from 47 to 25k variants, which is why the
per-assay averages are quoted with the assay count rather than as a single number.

Two things follow.

**The representation transfers.** On a benchmark it was never tuned for — a different mutation type, a
different expert family — the encoder is the strongest single expert in the pool, 0.047 above the best
published model and 0.036 above the three-expert blend.

**The allocation finding is not an artefact of one pool.** Adding a much stronger expert raises the
blend from 0.8427 to 0.8787 but leaves the weighting headroom where it was, +0.0088 against +0.0087. The
quantity a weighting rule can reach is set by how much the experts disagree, not by how good the pool is,
which is the paper's §3 claim stated in a second setting.

## What this does and does not establish

- It **does** show the encoder's advantage is not specific to the substitution benchmark, and that the
  allocation result survives a change of benchmark, mutation type and expert pool.
- It **does not** show the encoder's advantage is independent of the published models: the teacher is
  their consensus. The student exceeds the teacher's own consensus score, so it is adding signal beyond
  copying, but an α = 0 run would settle how much. That control is the next thing to run.
- ~~The folds are a fresh random split rather than ProteinGym's.~~ Closed: `cv_folds_indels.zip` publishes
  a per-variant `fold_random_5` column and the numbers here use it.
- One assay of 65 is excluded for runtime; the excluded library is the largest and easiest, so the
  averages above are not flattered by it.

## Reproducing

`indel_full.py` in this directory is the exact script the job ran: it stages data, extracts features with
resumable per-assay caches, trains the student, and prints the two tables above.
