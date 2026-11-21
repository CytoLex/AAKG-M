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

## The predictive criterion — now done

The gap recorded here earlier is closed. The per-assay oracle gain is not evenly spread, and both drivers are
measurable before any weight is fitted:

| | substitutions (182) | indels (65) |
|---|---:|---:|
| corr(oracle gain, expert disagreement) | **+0.534** | **+0.348** |
| corr(oracle gain, log variants) | −0.279 | −0.126 |
| leave-one-assay-out predictor from both | **+0.554** | **+0.258** |

So "how much could weighting gain here" is predictable from how much the experts disagree on an assay and how
much data it has — two statistics computable before fitting anything. That moves the paper from measuring the
allocation headroom to predicting *where* it is.

Stated precisely: the decision rule built on the predictor matches always-weighting (0.7027 against 0.7029 on
substitutions, 0.8534 against 0.8534 on indels) rather than beating it, which is expected since a per-assay
oracle cannot lose to the constant by construction. The value is diagnostic, not a gain: it tells a
practitioner whether the fitting exercise is worth starting.

The earlier failure was two bugs, both worth recording. The "constant" and the "oracle" were the same weight
vector, so every gain was zero and the correlation had no variance to explain. And the leave-one-out constant
was computed inside a per-assay loop, making the job O(n^2 * grid); it did not finish in an hour on a 4090 and
had to be rewritten around a single score matrix, after which it completes in minutes on an H100.

## The architecture experiment: gating on the variance axis — and why it does not hold up

The idea was to gate on a different variable. Every gating layer in this literature outputs a weight vector
over experts; the paper's own measurements say that axis is nearly exhausted and the binding constraint is
estimation error. So the gate here outputs the **shrinkage coefficient** instead:

```
lambda_i = gate(n_i, disagreement_i, expert-score spread, their interaction)
w(lam)   = (1 - lam) * w_panel + lam * w_i
```

Fitted leave-one-assay-out to each assay's own out-of-sample optimal lambda, then scored on five fresh splits
with a bootstrap over assays, re-aggregating inside every resample.

| rule | substitutions | indels |
|---|---:|---:|
| unregularised per-assay | **0.6993** | 0.8389 |
| tuned k = 300 | 0.6992 | 0.8436 |
| derived empirical Bayes | **0.6993** | 0.8427 |
| learned gate on lambda | 0.6991 | **0.8436** |

| comparison | substitutions | indels |
|---|---|---|
| gate − EB | **−0.0002** [−0.0004, +0.0000] | +0.0009 [+0.0003, +0.0016] |
| gate − tuned k=300 | −0.0001 [−0.0002, +0.0000] | +0.0001 [−0.0003, +0.0004] |

**The gate is not justified.** On substitutions it is *worse* than the closed form, with an interval that
excludes zero. On indels it does beat the closed form, but it is indistinguishable from a tuned constant
(+0.0001, P = 0.63). So the learned component adds nothing that tuning does not already capture.

An earlier single-split run reported +0.0003 and +0.0013 and looked like a win. Five splits and a bootstrap
turned one of those negative and the other into a tie with tuning. That is exactly what the interval was run
to find, and it is why the result was held back rather than written up.

**What this settles.** The paper's positioning as a measurement contribution is not a fallback — it is the
correct reading of the evidence. The variance axis is real (the closed form works, and per-assay fitting
fails), but building a learned layer on it buys nothing over the two-parameter version. A follow-up paper
would need a different idea, not this one.

## What still would

A genuinely new architecture was not attempted: inventing one, validating it on three benchmarks and writing
it up honestly does not fit inside a revision pass, and a half-validated new component would weaken the paper
rather than strengthen it.
