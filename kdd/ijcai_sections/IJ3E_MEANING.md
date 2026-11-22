## 3.6 What this means for the field
This is the forecast combination puzzle \cite{claeskens2016forecast}, measured in a domain where it had not been: weight
estimation error, not a shortage of mechanisms, is what caps the adaptation lever.

**The bound is a function of the metric, and we should say so.** Every oracle in this paper maximises Spearman,
including the +0.0051 that sets the headline. Recomputing the same bound under the metric §5 argues a campaign
actually experiences — top-of-list recall — changes its size: out of sample, the transferable headroom is **+0.0130**
at top-5% recall against **+0.0046** for Spearman, a factor of 2.8, and the weights a Spearman objective selects
capture only **10.4%** of it. So the lever is small in the aggregate and roughly three times larger in the
deployment metric, with no standard rule reaching the latter: +0.0051 bounds Spearman at fixed pool and per-assay
weights, and is not a claim that weighting is worthless under a ranking objective.

**The rule that reaches it is two lines.** Fit each assay's weights to maximise top-5% recall on half its variants,
then shrink toward the panel constant. Unshrunk, the noisy counting statistic is worthless — 0.2403, exactly the
constant's own 0.2403 — which is why the field does not do this. Shrunk, it reaches **0.2533**, the full transferable
headroom, against **0.2427** for weights a Spearman objective selects. The shrinkage is what makes the deployment
metric usable, exactly as it was for the aggregate in §3.4; smooth surrogates for the counting statistic did not
help (0.2401), so the noisy objective plus shrinkage beats the smooth objective without it.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0051, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: the oracle is a function of how much the experts disagree, so a pool built to
disagree could make gating worthwhile again — a different paper that would have to report the oracle too.
