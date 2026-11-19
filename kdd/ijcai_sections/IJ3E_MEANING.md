## 3.6 What this means for the field
**Report against tuned constants, not fixed blends.** A gate beating a fixed 50/50 blend by +0.0047 is
commonly reported as evidence that conditioning works; against a constant tuned on held-out assays the
same gate is +0.0002, a statistical tie. The gain attributed to conditioning is mostly the gain from
*tuning at all*.

**A per-assay oracle should be a reported baseline.** It costs nothing to compute and converts "our gate
improves over the previous gate" into "our gate captures *x* percent of the available headroom", which is
the only number telling a reader whether the mechanism is worth its complexity. Here *x* is four percent.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0027, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: the oracle is a function of how much the experts disagree, so a pool
built to disagree might make gating worthwhile again — a different paper, and one that would have to
report the oracle too.
