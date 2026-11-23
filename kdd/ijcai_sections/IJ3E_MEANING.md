## 3.6 What this means for the field
This is the forecast combination puzzle \cite{claeskens2016forecast}, measured in a domain where it had not been: weight
estimation error, not a shortage of mechanisms, is what caps the adaptation lever.

**The bound is a function of the metric, and we should say so.** Every oracle in this paper maximises Spearman,
including the +0.0051 that sets the headline. Recomputing the same bound under the metric §5 argues a campaign
actually experiences — top-of-list recall — changes its size: out of sample, the transferable headroom is **+0.0130**
at top-5% recall against **+0.0046** for Spearman, a factor of 2.8, and the weights a Spearman objective selects
capture only **10.4%** of it. So +0.0051 bounds Spearman at fixed pool and per-assay weights; it is not a claim that weighting is
worthless under a ranking objective, where the lever is three times larger.

**The rule that reaches it works at the threshold a campaign operates at.** Fit each assay's weights to maximise
top-of-list recall on half its variants, then shrink toward the panel constant — the shrinkage the unshrunk
counting statistic needs, since it otherwise lands on the constant to four decimals. At top-1%, the tightest and
operationally closest threshold, this reaches **0.1239** against **0.1146** for weights a Spearman objective
selects: **+0.0093**, 95% CI [+0.0014, +0.0171], and +0.0143 over the constant. **The advantage is not detectable
at 5%** (+0.0029, CI [−0.0028, +0.0085]) **or 10%** (+0.0014), and on the indel benchmark the same rule is the
*worst* of the four candidates. Both failures have the same cause: 5% of a 154-variant assay is eight variants, so
the counting statistic is not estimable there. The rule is real where a campaign operates and where the assay is large enough to
estimate it — the estimability story of §3.4 applied to a noisier statistic.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0051, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: a pool built to disagree more could make gating worthwhile again.
