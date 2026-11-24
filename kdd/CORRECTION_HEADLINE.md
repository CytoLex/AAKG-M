# Correction: the headline number, and a comparison across two populations

## What was wrong

Two things, and the second is worse than the first.

**The headline did not reproduce.** The paper reported **0.694** (and 0.693311 in the ablation ladder). Recomputing
from the published `fused_per_mutant.csv.gz` — 2,088,933 rows, 217 assays, the benchmark's own aggregation — gives
**0.6917**.

**The comparison mixed populations.** Kermut's 0.657 is the score over all 217 assays; the paper's 0.694 was the
score over the 182 assays the encoder covers. Measured on identical units:

| population | ours | Kermut | lead |
|---|---:|---:|---:|
| all 217 assays | **0.6917** | 0.6570 | **+0.0347** |
| 182 assays the encoder covers | 0.6931 | 0.6551 | +0.0380 |

The paper quoted 0.694 against 0.657, a lead of +0.037 — a figure that corresponds to neither row.

## How it was found

Kermut's row turned out to be the control that settled it. Recomputing Kermut through the same pipeline returns
**0.657028**, matching the paper to six decimals, so the aggregation chain was never in doubt: the same chain was
being applied to two different populations.

## What the paper says now

Section 4.3 quotes **0.6917 against 0.6570 on all 217 assays (+0.0347)** and **0.6931 against 0.6551 on the 182
covered assays (+0.0380)**, both of which the released predictions reproduce. The ablation ladder that carried
0.685538 / 0.691130 / 0.693311 is gone: those rungs come from the training pipeline and the release does not support
them, so quoting them would have made the paper's reproducibility claim false for its own headline.

The section 5.1 table now carries one verified row for our fusion instead of two unverifiable ones, and the section
5.2 category table was recomputed: values move by up to 0.004 and one delta by 0.010, and every category still
improves (+0.026 to +0.040).

## Follow-on: the utility numbers now come from the same artifact

Section 5.2's top-of-list figures had been computed from a fixed-fusion reconstruction rather than from the release,
which left the paper with two pipelines again at a smaller scale. Recomputed from the released predictions:

| top-k | was (fixed fusion) | now (released) |
|---|---|---|
| 1% | 0.112, 11.2x | **0.115** [0.104, 0.126], **11.5x** |
| 5% | 0.239, 4.78x | **0.241** [0.226, 0.254], **4.82x** |
| 10% | 0.343, 3.43x | **0.346** [0.333, 0.358], **3.46x** |

The category ordering is unchanged — Stability 7.8x against Activity 3.4x — and the caveat that used to sit under the
table ("regenerates to within 0.01 under the fixed fusion") is gone, because it no longer applies. Every number in
the headline, the category breakdown and the top-of-list analysis now derives from one released artifact.

## What did not change

The conclusion. The lead over the published leader is +0.035 rather than +0.037, the category ordering is the same
(Stability 0.850 highest, Activity 0.644 lowest), and every supporting claim in sections 3 and 4 was computed from
the out-of-fold bundle rather than from this pipeline.

## Why this is the right repair rather than a defence

The unverifiable numbers were not wrong in the sense of being fabricated — they came from a real run. They were
wrong in the sense that matters for a paper whose contribution includes reproducibility: **a reader executing the
released artifact would not have reproduced them.** The choice was to republish the artifact that matches them, or to
publish the numbers the existing artifact gives. The original pipeline was not available, so the second.

If the training pipeline is recovered later, the ladder can be restored — with its population stated, which it
should have had from the start.
