# Restructure, and the scaffold for writing it in your own words

The narrative change the external review asked for, which the page limit also rewards. It is written as a skeleton —
each section reduced to the claims it must make and the numbers that carry them — so it can be worked through in
either direction: as an editing checklist against the current draft, or as the plan for a rebuild.

Either way, check every number against the paper before reusing it. Four of them changed in the last pass.

## The title

The current one is *What Moves a Protein-Fitness Predictor: Disagreement, Not Accuracy*. Two problems, and the
review is right about both:

- **"Not Accuracy" is refuted by the paper's own §4.4**, which measures a competence floor: degrade an expert's
  predictions with noise and its marginal value eventually falls. High disagreement from a bad expert is worthless,
  so disagreement is not a substitute for accuracy.
- The pair reads as a slogan where the contribution is a measurement.

Direction rather than a replacement, since the phrasing should be yours:

> **Predictive complementarity** as the organising concept, with disagreement as its measurable proxy, and the pool
> as the unit of analysis.

Something of the shape *"Predictive complementarity in protein fitness prediction: what expert fusion can and cannot
buy"* — but write the actual title yourself.

## The three contributions (was four)

| # | Claim | Evidence that carries it |
|---|---|---|
| 1 | **Diagnosis**: fusion gains decompose into what the pool allows and what a finite panel can estimate, and the first is small compared with changing the pool | oracle +0.0051 [0.0038, 0.0066] against the expert lever +0.0122 [0.0099, 0.0144]; oracle null −0.0064 [−0.0083, −0.0043]; seven mechanisms within ±0.00025 |
| 2 | **Mechanism**: an expert's marginal value tracks its disagreement with the pool rather than its standalone score, subject to a competence floor | r = +0.786 over 13 pairs; controls at +0.0000 each; noise sweep peaks at ε = 0.25 |
| 3 | **Validation**: the diagnosis and the mechanism hold across mutation types and under the metric a campaign uses, and the resulting predictor is competitive | indel bound +0.0084; metric dependence 2.8×; top-1% rule +0.0093 [+0.0014, +0.0171]; 0.694 against 0.657 |

The reproducibility artifact is the floor all three stand on, not a fourth contribution. Shrinkage is an estimator used
inside contribution 1, not a claim in its own right — the paper measures that shrinkage helps, not that its formula is
the right one.

## Section skeleton

Each entry lists what the section must establish and the numbers that establish it. Write the prose from these.

### 1 Introduction — five moves, no results in the first three

1. A campaign is a ranking problem under a fixed synthesis budget.
2. Several predictors exist and practice combines them because they fail differently.
3. The gap: **a model's standalone accuracy does not tell you what it adds to a pool, and existing work selects
   experts on standalone accuracy.** This is the sentence the paper exists to support.
4. The approach: measure what the pool allows, then measure what predicts an expert's contribution.
5. The three contributions, one sentence each.

Do not open with +0.0051. The review is right that the current opening reads as conclusions in search of a motive.

### 2 Related work — three paragraphs, not five

- Protein fitness prediction and what the benchmark measures.
- Ensemble construction: stacking, ensemble selection, and the forecast-combination result that adaptation is limited
  by estimation error, not by a shortage of methods.
- Diversity in ensembles: ambiguity and its trade-off, and why "maximise diversity" is not the objective.

### 3 Framework — the three quantities, stated once

- **Allocatable**: M(pool, oracle) − M(pool, constant), with the oracle defined as the in-sample best over a stated
  weight simplex, and its null defined as another assay's oracle weights.
- **Expert**: M(pool ∪ {e}, constant) − M(pool, constant).
- **Transferable**: M(pool, adapted) − M(pool, constant), fitted out of sample.
- State the aggregation, the label-access rules per stage, and that the oracle is a *diagnostic* — an in-sample
  quantity by construction, not an upper bound on what a method can achieve. The review asks for this to be explicit;
  it is a one-sentence fix that removes a whole class of objection.
- Report the paired difference between the two levers with its own interval, not by comparing two intervals.

### 4 Representation and integration

- The mechanism test: retrain each view, report 0.432 / 0.464 / 0.480 / 0.582 and the increments +0.032 / +0.016 /
  +0.103.
- **The confound the review identified, stated as a limitation and not as a claim**: the last rung adds wild-type
  features *and* difference terms together, and the difference terms are a deterministic function of inputs the model
  already has. The gain may come from inductive bias or optimisation rather than new information. Say that.
- The competence floor: a noise sweep shows marginal value falling once the expert degrades past ε = 0.25.
- Distillation: report +0.114 and state the open question the review raises — how much of the gain is the
  representation and how much is the teacher's predictions being recombined. If the teacher's out-of-fold predictions
  were generated outside the outer split, say how.

### 5 Experiments — five groups, in this order

| Group | Question | What must be shown |
|---|---|---|
| E1 | Is the model competitive? | 0.694 against 0.657 under the benchmark's own script, per-scheme and per-category breakdown, Kermut control at 217/217 |
| E2 | Where do fusion gains come from? | the two levers, their paired difference, the oracle null, the seven-mechanism range |
| E3 | What predicts an expert's contribution? | r = +0.786, the three controls, **and the leave-one-expert-out check** described below |
| E4 | What carries the representation's value? | the view ladder plus the confound statement |
| E5 | Where do the conclusions hold? | indel benchmark, metric dependence, the operating range, the assays that regress |

### 6 Limitations and discussion

- The structural experts are inherited rather than retrained inside each outer fold.
- The released per-mutant predictions are a re-run: re-scoring them gives 0.692, not 0.694. The submitted score file
  is what the claims rest on.
- Leave-one-assay-out is not leave-one-protein-out; state which one the reported numbers use.
- The thirteen points are observational. State plainly that a causal reading of disagreement is not established.

## The one new analysis the review demands before submission

**Leave-one-expert-out on the thirteen points.** The scatter has one expert contributing four of the thirteen points,
and those sit in the upper-right of the figure. If the correlation is carried by those four, the claim is about one
representation, not about disagreement in general.

This is already scripted: `headroom/review_checks.py` reports the correlation on all points, with that expert's rows
dropped, and split by whether a pool contains it, plus a partial correlation of disagreement given standalone accuracy.

Three outcomes and what each means:

- **r stays high without the encoder's rows** → the mechanism claim stands as written.
- **r falls materially** → narrow the claim to *this* representation, and say so in the title and the abstract.
- **the partial correlation vanishes given accuracy** → the honest claim is that disagreement and accuracy both matter,
  which is what the reviewer believes, and the paper should report that rather than the stronger version.

Do not write §5's complementarity subsection until that number exists.

## Order of work

1. Run `review_checks.py`; the result decides how contribution 2 is phrased. **Blocking.**
2. Write §3 and §5's E2 from the bullets above — these carry the paper and are the easiest to write cold.
3. Write §1 and §6 last, once the claim in §5 is fixed by step 1.
4. Rebuild and confirm `build.sh` prints `OK`. It now measures the body rather than asserting the split.

Page budget for the rebuild: 7 pages body. The current build is exactly at 7 after compressing §3.2's mechanism table
and trimming §3.6; this restructure should stay inside that if the seven-mechanism detail stays in one sentence.
