## 3.6 What this means for the field
This is the forecast combination puzzle \cite{claeskens2016forecast}, measured in a domain where it had not been: weight
estimation error, not a shortage of mechanisms, is what caps the adaptation lever.

**Report against tuned constants, not fixed blends.** A gate beating a fixed 50/50 blend by +0.0047 is commonly
reported as evidence that conditioning works; against a tuned constant the same gate is +0.0002. The gain
attributed to conditioning is mostly the gain from *tuning at all*.

**A per-assay oracle should be a reported baseline.** It costs nothing to compute and converts "our gate
improves over the previous gate" into "our gate captures *x* percent of the available headroom", which is
the only number telling a reader whether the mechanism is worth its complexity. Here *x* is the fraction that
a tuned constant leaves on the table.

**The bound is a function of the metric, and we should say so.** Every oracle in this paper maximises Spearman,
including the +0.0051 that sets the headline. Recomputing the same bound under the metric §5 argues a campaign
actually experiences — top-of-list recall — changes its size: out of sample, the transferable headroom is **+0.0130**
at top-5% recall against **+0.0046** for Spearman, a factor of 2.8, and the weights a Spearman objective selects
capture only **10.4%** of it. So the lever is small in the aggregate and roughly three times larger in the deployment metric, with no standard
rule reaching the latter: +0.0051 bounds Spearman at fixed pool and per-assay weights, and is not a claim that
weighting is worthless under a ranking objective.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0051, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: the oracle is a function of how much the experts disagree, so a pool
built to disagree might make gating worthwhile again — a different paper, and one that would have to
report the oracle too.
