# Technical note for reviewers

This accompanies the manuscript *What Moves a Protein-Fitness Predictor: Disagreement, Not Accuracy*. It states what
the paper claims, how each claim is checked, what is known not to reproduce, and which extensions have already been
tested and failed. The last section says where comments would be most useful.

## What the paper claims

1. **A bound on what combining can buy.** On a fixed pool of four protein-fitness experts, a per-assay oracle — the
   best weighting chosen with hindsight for each assay — captures **+0.0051** [0.0038, 0.0066] Spearman over a
   constant fitted on the other assays. Adding one expert to the pool is worth **+0.0122** [0.0099, 0.0144]. So
   allocation is **42%** of the expert lever, not the whole of it.
2. **The bound understates the practical loss.** Under top-of-list recall, the metric an experimental campaign
   actually experiences, transferable headroom is **2.8 times** larger than under Spearman, and standard weights
   capture about a tenth of it.
3. **The loss is repairable and concentrated.** Shrinking each assay's weights toward the panel constant recovers the
   headroom with no per-assay tuning, using a closed form rather than a tuned strength. The gain is concentrated:
   the top ambiguity quartile holds **57%** of it.
4. **Expert value is disagreement, not accuracy.** Across thirteen expert-into-pool pairs, marginal contribution
   tracks disagreement with the pool at **r = +0.786**, while the weakest expert alone contributes the most
   (+0.0118) and the strongest almost nothing (+0.0000).

## How each claim is checked

| claim | check | outcome |
|---|---|---|
| the bound is real, not selection noise | oracle versus randomly drawn other-assay weights | null **−0.0064** [−0.0083, −0.0043]; the measured bound sits 0.0141 above it |
| allocation is worth less than adding an expert | both levers measured on the same panel, same aggregation | intervals do not overlap |
| the bound generalises beyond substitutions | same protocol on the indel benchmark (65 assays, 61,209 variants) | **+0.0084**, same direction |
| the shrinkage is derived, not tuned | closed form λ = τ²/(τ²+σ²) against the best tuned constant | matches within 12% on indels, exactly on substitutions |
| disagreement drives expert value | noise, shuffled and negated columns fed to the same search | each scores **+0.0000** |
| the aggregate is not the whole story | per-category breakdown plus top-1/5/10% recall | stability 0.851 against activity 0.642 |
| the model number is the benchmark's | ProteinGym's own evaluation script on our submitted score file | **0.694** against 0.657 for the published leader |

Intervals throughout are bootstrap over assays, re-aggregating inside every resample.

## What is known not to reproduce

**The released per-mutant predictions are a different run from the score file the reported numbers come from.**
Across all 651 assay-by-scheme units, none of the Spearman values agree, and the mean absolute difference is 0.0083.
Re-scoring the released file gives 0.692 rather than 0.694.

The reported numbers rest on the submitted score file, which is included in the submission and whose official-script
output ships with it. The released predictions are offered as a convenience. This is a defect in what was packaged,
not in the measurement, and the manuscript's limitations section says so. It is flagged here because a reader who
tries to re-derive 0.694 from the release will not get it, and should know that before concluding the work is wrong.

## Why this is a measurement paper rather than an architecture paper

Every component of the fused model — differential language-model features, distillation, a low-rank residual, seed
averaging — is an established technique, and the paper does not claim otherwise. What is new is the measurement
apparatus and one derived estimator:

- a three-number protocol (oracle bound, estimability, shrinkage) that transfers to any expert pool;
- a closed-form shrinkage strength that follows from how much weights move between assays versus between refits of
  the same assay, with no hyperparameter;
- a quantitative account of *why* expert value is disagreement, with controls that show the search cannot manufacture
  value from extra dimensions.

## Extensions already tested and refuted

These were tried and did not survive, and are recorded so that review effort is not spent re-suggesting them:

1. **A learned gate on the shrinkage coefficient.** Worse than the closed form on substitutions (−0.0002
   [−0.0004, 0.0000]) and statistically indistinguishable from a tuned constant on indels (+0.0001, P = 0.63).
2. **Residualising the new expert against the pool.** Apparent gain disappears when unchecked: the fit finds all
   positive weights, so convexity is not binding, and what the residualised column re-imports is per-assay structure
   — the allocation headroom arriving by another route.
3. **Interpolating the expert toward the pool.** The gain falls monotonically to zero; the optimum is at the boundary,
   so there is no interior configuration to find.
4. **Shrinking weight *alignment* rather than weight *level*.** Only level helps; the alignment version sits inside
   the permutation spread.
5. **A top-of-list rule at 5% and 10%.** Only the top-1% version survives its interval (+0.0093 [+0.0014, +0.0171]);
   the 5% version is +0.0029 [−0.0028, +0.0085], which is why the paper is careful about the threshold it operates at.

## Where comments would help most

- **Section 3.3 argues the bound is a property of the pool, not of our measurement.** If there is a flaw in the
  construction of the oracle or its null, everything downstream weakens. This is the highest-leverage place to push.
- **Section 3.4 claims the shrinkage is derivable.** The half-split variance estimate assumes refits of the same
  assay are exchangeable. If that assumption is wrong for a class of assays, the closed form should fail where it
  currently does not.
- **Section 4.4 claims expert value is disagreement.** The thirteen points are observational, not interventional:
  they show value and disagreement covary across pools, not that one causes the other. An argument that this is
  confounded would be substantive.
- **Section 5.2's top-of-list figures** depend on how ties and near-ties at the threshold are handled. The paper's
  handling is stated; a different convention would move the numbers by a few thousandths.
