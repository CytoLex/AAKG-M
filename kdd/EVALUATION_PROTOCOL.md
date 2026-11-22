# Evaluation protocol for a fusion, and for an expert inside one

This is the working protocol distilled from the experiments behind the paper and the four follow-up pilots. It
exists because six of the mistakes recorded at the bottom were made *by us*, in this repository, with the
numbers to prove it. Anyone evaluating a new fusion, or deciding whether a new expert is worth building, can
run down this list and avoid all six.

The domain is protein fitness prediction; the protocol is not.

---

## 1. Report three numbers, not one

A single "our fusion reaches X" number cannot be interpreted, because it does not say how much was available.
Measure all three on the **same units, same aggregation, same pool**.

| number | what it answers | how |
|---|---|---|
| **Oracle bound** | how much could *any* weighting of this pool gain? | per-assay best weights using that assay's own labels; compare against a constant fitted on the other assays |
| **Estimability** | how much of that can an assay's own data actually find? | fit weights on half the variants, evaluate on the other half, with the constant fitted on the same half of the other assays |
| **Estimator** | what is the right way to do it? | see §3 |

Report the first without the second and you will overstate; report the second without the first and you cannot
tell whether the ceiling is worth reaching.

**Calibration anchors from this work** (ProteinGym substitutions, 182–217 assays):

```
oracle headroom over a tuned constant      +0.0051   (95% CI [0.0038, 0.0066])
same in an out-of-sample half-split        +0.0047     naive per-assay fitting
                                           +0.0051     with shrinkage
an expert change, same pipeline            +0.0122   (95% CI [0.0099, 0.0144])
```

---

## 2. Run the control battery before believing anything

Any protocol that searches over weights can manufacture value from extra dimensions. Before interpreting a
marginal gain, feed the search columns that carry **no signal** and confirm they score zero.

| control column | construction | must yield |
|---|---|---|
| noise | i.i.d. normal, standardised within assay×scheme | marginal gain 0 |
| shuffle | a permutation of the real expert's scores | marginal gain 0 |
| negate | −(real expert) | marginal gain 0 |

And each headline number needs its own null, not just the marginal-value one:

| claim | null control | what passing looks like |
|---|---|---|
| oracle headroom | give each assay the oracle weights of a **random other assay** | null ≈ 0 or below; measured here **−0.0064 [−0.0083, −0.0043]** against a real +0.0077 |
| predictability | permute the predictor across assays | null r ≈ 0; measured **+0.002 [−0.119, +0.144]** against a real +0.534 |
| any shrinkage | permute the shrinkage coefficients across assays | see the entry below — **a claim can pass on level and fail on alignment** |

**Measured here, and this is what a clean protocol looks like:**

```
pool baseline 0.6830
add noise    apparent marginal +0.0000
add shuffle  apparent marginal +0.0000
add negate   apparent marginal +0.0000     <- negative information is also worth nothing
add real     apparent marginal +0.0122
```

If a control scores materially above zero, nothing downstream is interpretable until that is fixed. Note the
negate column: a protocol that lets a bad expert be *used backwards* will show a large apparent gain from an
inverted expert, which is a bug, not a discovery.

---

## 3. The estimator has a closed form; prefer it to tuning

Shrinking an assay's fitted weights toward the panel-wide constant has an optimal strength that can be
*derived* rather than searched:

```
lambda_i = tau^2 / (tau^2 + sigma_i^2)

sigma_i^2   sampling variance of one fitted weight vector for assay i
            -> repeat the fit on R independent half-splits, take the variance ACROSS replicates
               (do not divide by R: the shrinkage acts on a single estimate, not on a mean)
tau^2       between-assay variance
            -> total variance of the fitted weights across assays, minus the mean sampling variance
```

**Calibration.** On ProteinGym indels the derived rule gives +0.0022 against +0.0025 for the best hand-tuned
k, implying k = 241 where tuning chose 300 — with no selection of k at all. On substitutions it matches to
three decimals.

A tuned k is not wrong, but it is a hyperparameter, and a derived one is a claim about the problem.

---

## 4. Statistical discipline

1. **Pair the comparison.** Score both rules on the *same* splits and take per-assay differences; assay-to-assay
   variance is an order of magnitude above the effects being measured.
2. **Use ≥5 independent splits** and report the across-split standard deviation alongside any single number.
3. **Bootstrap over assays, re-aggregating inside every resample.** If the metric groups assays (by protein
   identity, by functional category), resampling the assay list without redoing the grouping gives the wrong
   interval.
4. **Report the interval, not the point estimate.** See the learned-gate entry in §6.

---

## 5. Deciding whether to build a new expert: the objective is disagreement, not accuracy

The single most useful result from the pilots. Across 13 real (expert-into-pool) pairs:

| expert | solo Spearman | marginal value to the pool | disagreement with the pool |
|---|---:|---:|---:|
| encoder (differential view) | 0.6449 | **+0.0118** | **0.194** |
| Kermut | 0.6551 | +0.0062 | 0.143 |
| Kseq | 0.6364 | +0.0004 | 0.104 |
| D | 0.6561 | +0.0000 | 0.064 |
| AMK | 0.6651 | +0.0028 | 0.060 |

corr(marginal value, disagreement) = **+0.786**. The expert with the *lowest* standalone accuracy contributes
the most; the highest-accuracy expert contributes almost nothing.

**So state the design objective as:** maximise residual disagreement with the existing pool, subject to a
competence floor. Do **not** distil toward the pool — measured, co-distillation raised the expert by +0.0136
but moved the fusion by −0.0002, because it removed the disagreement that gave the expert its value.

**Practical expectations before building anything:** if a candidate's disagreement is at or below the pool's
current maximum, expect little. If its solo score is far below the pool members, the competence floor binds and
the disagreement is noise.

---

## 6. Failure modes, with the numbers

Every one of these was encountered here. The measured size of the error is the reason to take them seriously.

**Cross-pool comparison.** Comparing an oracle over one pool against a fixed blend of a *different*, stronger
pool gave +0.0027 for a quantity that measures +0.0051 inside one pool — an **85% error** in the number the
conclusion rested on. Always compare within one pool, or state the pools are different and give both numbers.

**Cross-protocol ratio.** A ratio whose numerator came from one protocol and denominator from another ("the
gate captures four percent of the headroom") was silently wrong twice over. Never divide quantities measured
differently; recompute both under one protocol or drop the ratio.

**Single-split optimism.** A learned gate looked like a win at +0.0003 and +0.0013 on one split. Under five
splits with a bootstrap, one became **−0.0002 with an interval excluding zero** and the other became a tie with
tuning. A result that improves on a rerun is not yet a result.

**Grid expansion — suspected, then tested and absent.** We expected that enlarging a weight simplex would let a
useless column show positive value. The control battery showed exactly +0.0000. Suspicion is not evidence in
either direction: test it.

**Discretisation — suspected, then tested and absent.** An apparent +0.0013 from a residualised column survived
a 6× finer grid. Testing cost one job and removed a wrong explanation.

**Signed weights — tested, constraint not binding.** The natural follow-up was that the non-negative simplex
constraint bound the fusion. An unconstrained fit returned all-positive weights summing to 1.01 and scored
0.6953 against the simplex's 0.6952. The convexity constraint was not the issue; the residualised column was
re-importing per-assay structure through the assay-specific weights it subtracted.

**A shrinkage claim can pass on level and fail on alignment.** The derived per-assay shrinkage gained +0.0064
over the constant, while the *same coefficients permuted across assays* gained +0.0073 [+0.0070, +0.0076]. The
formula's per-assay alignment contributed nothing; the fact that lambda < 1 somewhere did all the work. That is
not a refutation of shrinkage — it is a refutation of the story that the *assay-specific* strength matters, and
it only shows up when the control is run. Check the median lambda first: if it sits near 1 there is no room for
alignment to matter, and the claim has to be restricted to the regime where shrinkage is heavy.

The heavy-shrinkage regime was then checked too, and the alignment still did not earn anything. On indels, median
lambda 0.41, the derived rule gains +0.0052 against a permuted null of +0.0047 [0.0042, 0.0054] -- a difference of
+0.0005 inside the null's own spread -- and a flat lambda of 0.60 gains +0.0062, beating the derived rule
outright. So the finding is not regime-specific: **the level is what works.**

**Cost of a leave-one-out constant.** Computing it inside a per-assay loop is O(n² × grid) and did not finish
in an hour on a 4090. Build the score matrix S[grid, assay] once, then derive both the oracle and the
leave-one-out constant from it: O(grid × n), minutes on one GPU.

---

## 7. Checklist

Before reporting any fusion or expert result:

- [ ] Oracle bound, estimability, and estimator reported, all on identical units
- [ ] Control battery run: noise, shuffle, negate all score 0
- [ ] Paired comparisons on the same splits, ≥5 splits, across-split sd reported
- [ ] Assay-level bootstrap with the metric's grouping re-applied inside each resample
- [ ] Intervals reported for every claim of improvement
- [ ] No ratio computed across two protocols
- [ ] Any tuned hyperparameter either reported as tuned, or replaced by a derived value
- [ ] New expert justified by marginal value, not standalone accuracy
- [ ] Disagreement of the new expert measured and compared against the pool's existing maximum
