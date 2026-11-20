# Correction: the allocation headroom is 42% of the expert gain, not a quarter

## What was wrong

The paper's central inequality compared two quantities measured on **different pools**:

```
+0.0027  =  three-expert per-assay oracle (0.693544)
          − four-expert fixed blend      (0.690808)
```

The four-expert blend is a different, stronger pool, so the subtraction does not give a within-pool
allocation headroom. The same source table the number came from records the oracle's gain over **its own**
pool's tuned constant as **+0.0059**, and a fresh measurement under the paper's own aggregation puts it at
**+0.0051**.

The consequence is that the ratio was overstated by roughly a factor of two and a half.

## What it is now

Everything below is computed in **one pipeline** — per (assay, scheme) Spearman, mean over schemes, grouped
by UniProt identity then by functional category — on the **182 assays** where the distilled expert covers
the panel, so both pools are scored on identical units.

| quantity | value | 95% CI |
|---|---:|---|
| pool A constant (D, Kermut, AMK) | 0.6830 | |
| pool A per-assay oracle | 0.6881 | |
| **allocation headroom** | **+0.0051** | **[+0.0038, +0.0066]** |
| pool B constant (+ distilled encoder) | 0.6952 | |
| **expert gain** | **+0.0122** | **[+0.0099, +0.0144]** |
| **ratio** | **0.42** | intervals do not overlap |

**The qualitative claim survives and is stronger for being correct**: the entire allocation headroom is less
than half of what one expert change delivers, and the two confidence intervals are disjoint. The word
"quarter" is replaced by "42%", and every place that carried the old number is updated.

The variant-level split-half was recomputed in the same aggregation: in-place **+0.0063 ± 0.0006**,
transferred **+0.0028 ± 0.0008**, survival **44%** over ten independent splits. The earlier figure was 49%
under the old aggregation, so that conclusion is robust to the change.

## Why this happened, and what it costs

The +0.0027 predates the paper: it was inherited from an internal claim table where the oracle and the
"fixed blend" happened to be quoted next to each other, and the subtraction was never re-derived when the
claim moved into the manuscript. It is the kind of error that survives precisely because both inputs are
individually correct and the resulting number is in the right direction — only the comparison is wrong.

Three things follow that a reader should know:

- **The title still holds.** "The Ceiling on Adaptive Weighting in Protein Fitness Prediction, and How to Reach It" says allocation is not the main lever;
  42% against an expert change, with disjoint intervals, supports that. It would not support "allocation is
  worth nothing", which the paper does not claim.
- **§3.5's cross-benchmark comparison changed scale.** Substitutions +0.0051 against indels +0.0084 is
  1.6x, not the 3x the old pairing implied.
- **The absolute levels shifted** because the join with the encoder's predictions restricts the panel to 182
  assays. That is stated in the text rather than left for a reader to discover.

## Reproducing

`one_pipeline.py` and `splithalf_pipeline.py` in `kdd/headroom/` are the exact scripts the platform jobs
ran. They read the out-of-fold bundle, the encoder's per-variant predictions, and the reference table, and
print the two tables above.
