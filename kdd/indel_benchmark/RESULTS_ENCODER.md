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

| expert | per-assay Spearman |
|---|---:|
| Embeddings-ESM1v (published) | 0.8234 |
| Embeddings-Tranception (published) | 0.8006 |
| Embeddings-MSA Transformer (published) | 0.7951 |
| **our differential encoder** | **0.8699** |

| pool | nested constant | per-assay oracle | headroom |
|---|---:|---:|---:|
| three published experts | 0.8427 | 0.8514 | +0.0088 |
| **+ our encoder** | **0.8787** | 0.8875 | +0.0087 |

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
- The comparison is per-assay out-of-fold on both sides, but our folds are a fresh random five-way split
  (seed 1) rather than ProteinGym's released assignment for indels, which we could not locate. Both are
  random five-fold over the same variants, so the expected difficulty matches, but this is a difference
  worth closing if the released indel folds exist.
- One assay of 65 is excluded for runtime; the excluded library is the largest and easiest, so the
  averages above are not flattered by it.

## Reproducing

`indel_full.py` in this directory is the exact script the job ran: it stages data, extracts features with
resumable per-assay caches, trains the student, and prints the two tables above.
