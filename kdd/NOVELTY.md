# Where the novelty actually is, and what was done about it

The user's question was whether the method is novel enough. Honest answer before any work: **as an
architecture, no.** Each component — differential ESM features, distillation from stronger models, a
low-rank residual, seed averaging — is a known technique, and a reviewer will say so.

What the paper does have is a measurement argument. The work below was to give that argument a formal spine
so the novelty sits somewhere defensible.

## What changed

**The shrinkage went from tuned to derived.** The pooling rule `λ = n/(n+k)` carried a k selected on the
panel, which is a hyperparameter and reads as a heuristic. It now has a closed form:

```
λ_i = τ² / (τ² + σ²_i)
```

where σ²_i is the sampling variance of an assay's fitted weight vector — estimated by repeating the fit on
six independent half-splits — and τ² is the between-assay variance, estimated as the total variance of the
fitted weights minus the mean sampling variance. No search.

The derivation reproduces the tuning:

| | indels | substitutions |
|---|---:|---:|
| per-assay weights, out of sample | −0.0032 | +0.0047 |
| pooling, k tuned | +0.0021 | +0.0051 |
| **pooling, λ derived** | **+0.0022** | **+0.0051** |
| implied k | 241 | 497 |
| tuned k | 300 | 10 |

On indels — the hard case, where per-assay fitting loses — the derived rule lands within 12% of the best
tuned value and implies a k of 241 against a tuned 300. On substitutions it matches exactly; the tuned k
there is 10 but the loss surface is flat from k = 30 to 300, so the disagreement does not cost anything.

**Contribution 2 was reframed** from "an expert built from differential representations" to "a measurement
of where a mutation's signal lives". The evidence — a +0.116 feature ablation and a +0.0214 control arm —
locates signal; presenting it as an architecture overstates the machinery and understates the evidence.

**The closing comparison was made explicit**: the best of seven designed mechanisms captures +0.00025 of a
+0.0051 ceiling; a two-parameter shrinkage captures +0.0051.

## What this buys, and what it does not

It buys a method section that says something a reader can derive rather than tune: the shrinkage strength is
a function of how much weights move between assays and how much they move between refits of the same assay.
That is a claim about the problem, not about our implementation.

It does not buy architectural novelty, and the paper should not claim any. The honest framing is a
measurement paper with a derived estimator, which is what the title, the introduction and the contributions
now say.

## What would raise novelty further, and why it was not done

A **predictive criterion** — "apply per-assay weighting iff a computable statistic exceeds a threshold" —
would move the paper from measurement to prediction. The attempt is in `headroom/eb.py`: it relates the
per-assay oracle gain to expert disagreement. That run returned NaN on both benchmarks because of a
degenerate correlation in the disagreement estimator, and the fix was not completed in this session. The
code path is there and the numbers would be a one-job follow-up.

A genuinely new architecture was not attempted: inventing one, validating it on three benchmarks and writing
it up is not something that can be done honestly inside a revision pass, and a half-validated new component
would weaken the paper rather than strengthen it.
