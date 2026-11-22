# Survey: where this paper actually sits in the literature, and what that buys

Searched arXiv by API (web search was unavailable). Five clusters matter; each one either threatens a claim or
strengthens it. Venue metadata is not verified here — arXiv ids only — and every citation must be checked
against the published version before it enters the bibliography.

## A. The forecast combination puzzle — our closest theoretical home

| id | title | what it establishes |
|---|---|---|
| 1505.00475 | On the Forecast Combination Puzzle | simple averages often beat optimally-weighted combinations; causes are estimation error, invalid weighting formulas, and **model screening**; introduces the distinction **combining for adaptation vs combining for improvement** |
| 2308.05263 | Solving the Forecast Combination Puzzle | argues the puzzle is partly an artefact of low-power tests; with efficient estimation the naive approach's advantage can vanish |
| 2109.13801 | No-Regret Forecasting with Egalitarian Committees | exploits the puzzle deliberately |
| 2208.00139 | Another look at forecast trimming | robustness/accuracy/diversity trade-off in combination |

**This is what our §3.2 and §3.4 are.** Seven gating mechanisms failing to beat a tuned constant, and shrinkage
toward the panel constant working where they do not, is the forecast combination puzzle appearing in protein
fitness prediction. And 1505.00475's "adaptation vs improvement" is *exactly* our allocation-versus-expert split,
named twenty years earlier.

**What it buys:** the negative result stops being ours alone. Instead of "gating does not work here", the paper
says "gating does not work here, for the reason it does not work in forecasting" — a known phenomenon, newly
located in a domain where nobody has measured it, with a bound attached.

**What it costs:** the citation 2308.05263 argues the puzzle can be a testing artefact. Our paper uses assay-level
bootstrap intervals and a permutation null, so we are on the defensible side — but the paper should say so
explicitly rather than invite the objection.

## B. Ambiguity and diversity decomposition — our r = +0.786

| source | result |
|---|---|
| Krogh & Vedelsby (1995) | ensemble error = average member error − ambiguity |
| 1312.7463 Generalized Ambiguity Decomposition | the same decomposition for any twice-differentiable loss and any convex ensemble |
| 2301.03962 A Unified Theory of Diversity in Ensemble Learning | diversity is a **hidden dimension of the bias-variance decomposition**; concludes *"we should not be maximising diversity as so many works aim to do — instead, we have a bias/variance/diversity trade-off to manage"* |
| 1910.13631 When does Diversity Help Generalization | diversity helps conditionally, not unconditionally |

**Our +0.786 is the ambiguity term measured on 13 real (expert, pool) pairs.** That is a quantification, not a
discovery, and the paper should present it that way.

**Critically, 2301.03962 is a warning we already obey without knowing it.** A naive reading of "disagreement
drives marginal value" is "maximise disagreement", which that paper explicitly argues against. Our own
residualisation experiment is the counter-evidence: pushing disagreement further dropped standalone accuracy to
−0.33 and bought nothing. So the correct statement is a trade-off with a competence floor, which is already the
language in `EVALUATION_PROTOCOL.md` §5.

**Action:** cite it, and phrase the design rule as *"maximise residual disagreement subject to a competence
floor"*, explicitly as a trade-off rather than a maximisation.

## C. Accuracy-adjusted diversity predicts better than raw diversity

2607.17384 (Quantifying Diversity of Thought, 2026) derives an exact decomposition of ensemble lift into rescue
and damage masses and reports a sharp empirical fact: **raw correctness correlation has almost no predictive
power (R² ≤ 0.09), while the accuracy-adjusted version reaches R² = 0.67.**

**Our predictability result uses raw disagreement** (1 − mean pairwise |Spearman| between experts), giving
r = +0.554 from a leave-one-assay-out linear predictor. That is squarely in the regime this paper says is weak.

**This is a concrete, cheap, testable upgrade:** build an accuracy-adjusted disagreement — weighting the
pairwise correlation by each expert's own residual skill, the analogue of their φ_adj — and rerun the
leave-one-assay-out predictor. If r rises above +0.554, §3.4's predictability paragraph gets stronger and gains a
direct comparison to a 2026 result. If it does not, we report that the adjustment does not transfer to rank
metrics, which is itself a finding.

## D. Stacking and non-negative weights

Breiman's stacked regressions and the ensemble-selection line use non-negativity and ridge precisely because
unconstrained weight estimation is unstable. Our finding that the simplex constraint is *not* binding (an
unconstrained fit returns all-positive weights summing to 1.01, scoring 0.6953 against the simplex's 0.6952) is
a small but citable data point in that practice — it says the constraint is not the binding limitation here,
which is the opposite of the usual worry.

## E. The protein side

Kermut (2407.00002), ProteinGym, FLIP, ProteinNPT, and the FLIP2 splits. The survey found no paper that treats
gating/fusion for protein fitness as the object of study with an oracle bound — which is the paper's opening.

---

# Ranked actions

**1. Add the forecast-combination framing to §2 and §3.6.** Highest value per word. It converts both flagged
weaknesses at once: the negative result becomes a known phenomenon measured in a new domain, and the method no
longer looks like an assembly with no scholarly context. Roughly 80 words in §2, one sentence in §3.6.

**2. Test the accuracy-adjusted disagreement predictor.** One job. Directly tests this paper's predictability
claim against 2607.17384's finding that raw diversity is a poor predictor. Either outcome is publishable.

**3. Rephrase the disagreement result as a trade-off, citing 2301.03962.** Protects against the strongest
available objection to the paper's own mechanism language.

**4. Cite the ambiguity decomposition for r = +0.786.** Turns "we observed correlation" into "we measured the
ambiguity term".

**5. Say explicitly why the puzzle is not a testing artefact here** (assayed bootstrap + permutation null),
citing 2308.05263. Pre-empts a reviewer who knows that literature.

**Do not** claim the gating-fails result as novel in general — it is a 20-year-old puzzle. Claim the domain
instance, the bound, and the estimator.
