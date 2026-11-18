# Where the fusion helps, and where it hurts

Two questions a KDD AI4S reviewer will ask: which assays regress, and does the headline depend on the
35 assays that fall back to an older expert. Both are computed from the published per-assay scores.

## The regression set

Seed-averaged expert fusion versus the previous four-expert fusion, 217 assays:

| | count |
|---|---:|
| improves | **130** |
| regresses | **87** |
| unchanged | **0** |
| median delta | **+0.0016** |
| mean delta | +0.0029 |

So 40% of assays get worse, and the median gain is roughly half the mean — the improvement is
concentrated, not uniform.

> **This supersedes the "97 positive / 85 negative / 35 unchanged" figure in `paper/`.** That count came
> from an earlier arm pair under the looser protocol. The numbers above are from the current
> seed-averaged arm against the same run's baseline, which is the comparison the paper actually makes.

## Which categories regress

| category | n | regress | rate | mean delta |
|---|---:|---:|---:|---:|
| OrganismalFitness | 77 | 37 | **0.481** | +0.0012 |
| Expression | 18 | 8 | 0.444 | **−0.0018** |
| Activity | 43 | 18 | 0.419 | +0.0015 |
| Binding | 13 | 5 | 0.385 | +0.0131 |
| Stability | 66 | 19 | **0.288** | +0.0051 |

**Expression is the only category that regresses on average.** OrganismalFitness regresses almost half
the time but the surviving gains outweigh it. This is the same axis the top-k analysis found: the
ranker is strongest on stability, weakest on the function-flavoured categories.

## Assay size matters more than expected

| assay size quartile | n | mean delta | regress rate |
|---|---:|---:|---:|
| Q1 (smallest) | 55 | **+0.0073** | 0.255 |
| Q2 | 54 | +0.0017 | 0.444 |
| Q3 | 54 | +0.0024 | 0.407 |
| Q4 (largest) | 54 | **+0.00003** | 0.500 |

**The gain is essentially zero on the largest quartile and about seven times the average on the
smallest.** This is the sharpest honest limitation in the whole analysis: for the assays with the most
data — the ones an engineering campaign is most likely to run — the method is at parity with its
predecessor while regressing half the time.

## The 35 fallback assays are not zero

| subset | n | category-balanced mean delta |
|---|---:|---:|
| all assays | 217 | +0.0038 |
| encoder-covered | 182 | +0.0047 |
| fallback | 35 | **+0.0029** |

The fallback assays still move, even though the expert column is identical for them in both arms. The
cause is structural: the nested weight search fits one weight vector per fold on **all** training
assays, so replacing the expert on the other 182 assays changes the selected weights that are then
applied to the fallback assays. **The 35 are coupled to the rest through the weight search, not
predicted independently.**

That is worth stating in the paper rather than hiding: it means "182 assays covered" understates the
method's reach — the fallback assays inherit a fraction of the gain — but it also means their delta is
not evidence about their own predictions.

## Reproduction

`remote_ablation/kdd_analyses.py` in the working tree; inputs are `results_verify/ch_preds_savg.npy`,
`ch_old_preds_savg.npy`, and `ref_slim.csv`.
