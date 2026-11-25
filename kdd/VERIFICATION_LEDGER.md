# Verification ledger

Which numbers in the paper reproduce from released artifacts, which do not, and what each would need. This exists
because three separate discrepancies were found by checking rather than by reading, and the first two were only
visible once a *control* number was checked against the same pipeline.

## Reproduces from `submission/predictions/fused_per_mutant.csv.gz`

These were recomputed from the released fusion under the benchmark's own aggregation, and each was compared against
the value in the paper.

| number | where | value | status |
|---|---|---|---|
| our fusion, all 217 assays | §4.3, §5.1 | 0.6917 | reproduces |
| our fusion, 182 covered assays | §4.3 | 0.6931 | reproduces |
| Kermut, all 217 assays | §5.1 | 0.6570 | reproduces to six decimals |
| per-scheme breakdown | §5.1 | 0.778 / 0.671 / 0.626 | reproduces |
| per-category scores | §5.2 | 0.850 … 0.644 | reproduces |
| top-1/5/10% recall and lifts | §5.2 | 0.115 / 0.241 / 0.346 | reproduces |

## Reproduces from the expert bundle (`submission/oof/`)

| number | where | value | status |
|---|---|---|---|
| allocation headroom | §3.3 | +0.0051 [0.0038, 0.0066] | reproduces |
| its null | §3.3 | −0.0064 [−0.0083, −0.0043] | reproduces |
| expert lever | §3.3 | +0.0122 [0.0099, 0.0144] | reproduces |
| rank-average baseline | §3.2 | 0.6942 vs 0.6952, [−0.0031, +0.0011] | reproduces |
| out-of-sample estimability and shrinkage | §3.4 | +0.0047 → +0.0051 etc. | reproduces |
| predictor and its permutation null | §3.4 | +0.628 vs +0.002 | reproduces |
| thirteen expert-into-pool points, r = +0.786 | §4.4, Fig. 1 | +0.786 | reproduces |
| the noise / shuffle / negate controls | §3.2, §4.4 | +0.0000 each | reproduces |

## Reproduces from the indel bundle

| number | where | value | status |
|---|---|---|---|
| indel oracle minus constant | §3.5 | +0.0084 | reproduces (oracle 0.8534, constant 0.8450) |

## Does not reproduce from the release, and the paper says so

| number | where | why |
|---|---|---|
| the ablation ladder 0.685538 → 0.691130 → 0.693311 | was §4.3 | the per-fold fusion weights are summarised, not released. **Removed** rather than quoted unverifiably |
| the representation ladder 0.467 / 0.464 / 0.480 / 0.596 | §4.1 | needs each view retrained; now labelled as measured, not regenerable |
| the encoder's indel score 0.8858 and blend 0.8934 | §3.5 | the encoder's indel predictions are not in the released bundle |
| the feature/control ablations +0.116, +0.0214, +0.114 | §4.1, §4.2, §4.4 | same reason: they are view-level retrainings |

## The three discrepancies this ledger found

1. **The headline was 0.694 against Kermut's 0.657 — two different populations** (182 covered assays against 217).
   Corrected to 0.6917 against 0.6570, +0.0347, with the 182-assay figure given separately.
2. **The utility table came from a fixed-fusion reconstruction**, not from the release. Recomputed: 0.115 / 0.241 /
   0.346 with lifts 11.5x / 4.82x / 3.46x.
3. **Section 5.2's earlier numbers** (0.119 / 0.247 / 0.350) were never reproducible from anything released.

Each was found by checking a number against the artifact that was supposed to produce it. None would have been found
by reading the paper.
