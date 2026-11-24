# Rebuttal evidence pack

Every number in the paper, with the protocol it was measured under and the control or interval behind it, plus the
objections worth answering and the ones worth conceding outright. Built so that a rebuttal can be written from fact
rather than memory.

Protocols are named because the same quantity measured two ways is how three of this project's own errors started.

---

## 1. The claims, with their support

| # | claim | number | protocol | what backs it |
|---|---|---|---|---|
| 1 | allocation headroom | **+0.0051** [0.0038, 0.0066] | one pipeline, 182 assays, constant fitted LOO on full data | assay bootstrap, re-aggregating inside each resample |
| 2 | expert lever | **+0.0122** [0.0099, 0.0144] | same pipeline, same units | intervals disjoint from claim 1 |
| 3 | their ratio | **42%** | — | — |
| 4 | oracle headroom is not selection noise | null **−0.0064** [−0.0083, −0.0043] | each assay given a *random other* assay's oracle weights | real oracle is 0.0141 above its null |
| 5 | seven mechanisms fail | best **+0.00025** [−0.0019, +0.0025] | per-assay refit, released folds, official aggregation | intervals straddle zero for five of seven |
| 6 | a parameter-free rank average ties the tuned constant | **0.6942** vs **0.6952**, diff **−0.0010** [−0.0031, +0.0011] | same units | paired bootstrap over assays |
| 7 | shrinkage is what fixes estimation | +0.0047 naive → **+0.0051** shrunk (subs); −0.0032 → **+0.0022** (indels) | half-split, constant fitted on the same half of other assays | across-assay bootstrap |
| 8 | shrinkage level matters, per-assay alignment does not | permuting λ changes gain by at most **+0.0005** (inside its own spread), and is 0.0009 *better* on substitutions; flat λ 0.60 gives +0.0062 vs derived 0.41's +0.0052 | permutation control | stated openly |
| 9 | the gain is predictable before fitting | **r = +0.628** LOO from ambiguity + log n | leave-one-assay-out linear predictor | raw disagreement +0.509, skill-weighted +0.491, permuted null **+0.002** [−0.119, +0.144] |
| 10 | headroom is concentrated | top ambiguity quartile holds **57%**, median gain **+0.0117**; bottom quartile +0.0009 | quartile sort by pool ambiguity | — |
| 11 | an expert's value is its disagreement | **r = +0.786** over 13 expert-into-pool pairs | nested constant, same units | noise / shuffle / negate columns each score **+0.0000** |
| 12 | the weakest expert contributes most | X solo **0.6449** → marginal **+0.0118**; AMK solo **0.6651** → **+0.0028** | same | the counterintuitive core of the title |
| 13 | the competence floor is measurable | peak at ε = 0.25: **+0.0086** vs +0.0077 untouched; expert within **0.0009** | noise-degradation sweep, 17 steps | residualisation axis shown to be a trap, not a frontier |
| 14 | the bound is metric-dependent | top-k transferable headroom **+0.0130** vs Spearman's **+0.0046** (2.8×); Spearman-optimal weights capture **10.4%** | half-split, 5 splits averaged | — |
| 15 | a rule reaches the deployment headroom | **0.1239** vs **0.1146**, **+0.0093** [+0.0014, +0.0171] at top-1% | per-assay weights fitted on half to maximise top-k, then shrunk | paired bootstrap; **not detectable at 5%** (+0.0029 [−0.0028, +0.0085]) or 10% |
| 16 | the expert itself | **0.694** vs **0.657** Kermut | official metric, official script | Kermut recomputed through our pipeline: 217/217 assays, MAD **0.0** |
| 17 | the representation transfers | FLIP2: 6 of 7 splits, mean **0.43 vs 0.26**; ridge on the same features only 0.15 | independent benchmark | the gain is the view *plus* a nonlinear head |
| 18 | utility profile | top-5% recall **0.239** [0.223, 0.255], lift **4.78x**; Stability **7.8x** [7.4, 8.1] vs Activity **3.5x** [3.0, 3.9] | fixed fusion, bootstrap over assays | intervals separate across categories |
| 19 | size regime | smallest quartile **+0.0073**, largest **+0.00003** | same units | stated as specification, not footnote |

## 2. Objections worth answering

**"Gating works elsewhere; this is a null result."**
It is a bounded regime, and we measure the bound rather than asserting it: the oracle says no weighting of this pool
can gain more than +0.0051, and that bound is itself 0.0141 above the null that would be expected from per-assay
selection alone. We also give the mechanism — expert correlations of 0.78–0.96 within a unit, and a conditioning
variable that is not the one the optimal weights depend on. The rank-average control sharpens it: the tuned constant
is indistinguishable from averaging, so there is little headroom for *any* rule.

**"Your baseline is a tuned constant, which is generous to you."**
It is generous, and that is the point: even so, nothing beats it. And the constant itself is tied with a rank
average that uses no labels and has no parameters.

**"The encoder is standard components."**
Agreed, and the paper does not claim otherwise — contribution 2 is a measurement of where an expert's value comes
from (r = +0.786, disagreement not accuracy), and the encoder is its instance. The transferable part is the
protocol and the principle, not the architecture.

**"You only optimise Spearman."**
We report the deployment metric explicitly: under top-1% recall the transferable headroom is 2.8 times larger,
Spearman-selected weights capture about a tenth of it, and a shrunk top-k rule beats them by +0.0093 with an
interval excluding zero.

**"The top-k rule fails on indels."**
Correct, and stated in the paper. 5% of a 154-variant assay is eight variants, so the counting statistic is not
estimable there — the same estimability constraint as §3.4, applied to a noisier statistic.

**"Reproducibility."**
Every number regenerates from the released per-mutant scores except the per-fold fusion weights, which are
summarised rather than released; the utility figures therefore reproduce to within 0.01 under the fixed fusion. That
scope is stated in the limitations and the table caption, and the table itself carries the values the release does
regenerate.

## 3. Objections to concede immediately

Conceding these costs nothing and buys credibility; arguing them costs the review.

- **Architectural novelty is low.** The encoder is an assembly of known ingredients. The paper says so by framing the
  contribution as measurement and by showing four natural upgrades that failed.
- **No wet-lab validation.** The claims stop at the ranking, by design, and §6 says where.
- **The top-k advantage does not generalise to small assays**, and is undetectable at 5% and 10% on the benchmark
  where it does work.
- **The per-fold fusion weights are not released**, so one table reproduces to 0.01 rather than exactly.
- **A previously reported +0.0106 at top-5% did not survive an interval.** If a reviewer has seen an earlier version,
  the corrected number is +0.0029 [−0.0028, +0.0085] and only the top-1% result survives.

## 4. Numbers never to quote in a rebuttal without their qualifier

- **+0.0051** — two quantities: the oracle headroom (§3.3) and the shrinkage gain in the out-of-sample protocol
  (§3.4). Always say which.
- **+0.0077** — the oracle headroom of the *four*-expert pool, not the three-expert +0.0051.
- **2.8×** — ratio of transferable headroom between metrics at top-1%; it is not a ratio of the headline 42%.
- **42%** — allocation vs expert lever under Spearman. Under the deployment metric that ratio does not hold and the
  paper says so.
- **0.6942 vs 0.6952** — both on the substitute benchmark's units; the published 0.694 headline is from the per-fold
  fusion and is not the same quantity as either.
