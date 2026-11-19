# Second benchmark: ProteinGym DMS indels

The submission currently rests on one benchmark. This directory holds the first half of a second one,
computed entirely from published out-of-fold predictions — no training, so the numbers below are
reproducible from two downloads.

## What was downloaded

| file | size | contents |
|---|---:|---|
| `DMS_ProteinGym_indels.zip` | 6.7 MB | 66 indel assays, 287,207 variants, `mutated_sequence` + `DMS_score` |
| `DMS_supervised_indels_scores.zip` | 19 MB | per-variant **out-of-fold** predictions from three published supervised indel models, plus `normalized_targets` |
| `DMS_indels.csv` (reference) | — | `target_seq` per assay |

Source: `marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/`, the release the proteinGym README points at.

The three published models are `Embeddings_ESM1v_indels`, `Embeddings_MSA_Transformer_indels` and
`Embeddings_Tranception_indels`. Each variant carries exactly one prediction per model, so the scores are
out-of-fold — the same structure as the substitution benchmark's expert pool.

Only the `fold_random_5` scheme exists for indels; there is no modulo or contiguous scheme, so the
cross-scheme robustness axis the substitution benchmark provides is not available here.

## What was computed

**Allocation headroom.** A per-assay oracle (the best simplex blend for that assay, ≤0.1 grid) against a
single tuned constant, in the same spirit as §3 of the paper: if a weighting rule had real headroom, the
oracle would be far above the constant.

| quantity | indel benchmark | substitution benchmark (paper §3, 4-expert pool) |
|---|---:|---:|
| best single expert | 0.8351 | 0.6597 |
| equal-weight blend | 0.8425 | — |
| tuned constant | 0.8433 | 0.6876 |
| **per-assay oracle** | **0.8515** | 0.6935 |
| oracle − constant | **+0.0082** | **+0.0027** |

So the oracle gap is *larger* here than on substitutions. Taken alone that would read as evidence against
the paper's allocation claim, which is why the next measurement matters.

**Is that gap estimable?** Split each assay's variants into disjoint halves, select the per-assay optimal
weights on A, and evaluate them on B against the tuned constant — the same test §3.3 runs on
substitutions.

| | substitution benchmark | indel benchmark |
|---|---:|---:|
| oracle gain in place | +0.0083 | +0.0110 |
| the same weights on the held-out half | +0.0041 | **−0.0010** |
| fraction surviving | **49%** | **−9%** |

On substitutions, half the oracle gain is a stable property of the assay. On indels, none of it is: the
weights selected on half an assay *lose* to the constant on the other half.

The split by assay size explains why. Indel assays have a median of **154 variants**; substitution assays
have thousands.

| quartile of indel assay size | median n | in-place gain | transferred to the held-out half |
|---|---:|---:|---:|
| Q1 (smallest) | 104 | +0.0149 | −0.0053 |
| Q2 | 144 | +0.0096 | −0.0023 |
| Q3 | 175 | +0.0087 | −0.0002 |
| Q4 (largest) | 490 | +0.0108 | **+0.0044** |

Only the largest quartile transfers anything, and there it is 40% of the in-place gain.

## The claim this supports

The oracle is not one bound but two. A per-assay weighting rule is limited by how much the pool
disagrees — the oracle — and separately by how much of that disagreement can be *estimated* from the
assay's own variants. On substitutions the first bound is small (+0.0027) and half of it is estimable. On
indels the first bound is three times larger, but with a median of 154 variants per assay it is almost
entirely estimation noise, and a rule fitted on half the data loses to a constant on the other half.

That is a sharper statement than "allocation is exhausted", and it is the one a reader can use: the size
of the assay, not only the diversity of the pool, decides whether per-assay weighting is worth attempting.

## Caveats, stated plainly

- **This does not yet include our encoder.** The expert pool is the three published models. Adding a
  fourth expert built on the differential representation needs feature extraction for indels, which is
  the next piece of work; without it this benchmark tests the allocation claim but not the
  representation claim.
- **One scheme only** (`fold_random_5`), so no cross-scheme check.
- The split-half estimates are single-split; a multi-split average would tighten them, and the sign of the
  small-assay transfer is the quantity that most needs that tightening.
- 65 of 66 assays enter; one has fewer than 50 variants after dropping missing scores.
- The tuned constant is a single weight vector chosen on the whole panel. That is the optimistic choice
  for the constant, which makes the oracle gap an *optimistic* estimate of allocation headroom — the
  conclusion above therefore does not depend on under-tuning the baseline.

## Reproducing

```bash
python3 alloc_indels.py        # the allocation table
python3 split_half_v2.py      # the split-half table and its size breakdown
```

Both expect the two downloads unpacked in the working directory.
