## 1 Introduction

A protein engineering campaign begins with a library of candidate mutations and a budget covering tens of
assays. Everything upstream of the bench is a ranking problem: which candidates are worth synthesising. The
models that answer it have improved — sequence language models \cite{esm2}, structure-informed kernels
\cite{kermut}, supervised models trained on deep mutational scanning data \cite{proteinnpt} — and practice
combines several, because they fail on different assays \cite{proteingym}.

The combination is almost always **conditional**: a gate reads assay-level context and emits per-assay
weights, a mixture layer routes by protein family \cite{jacobs1991,shazeer2017}, an uncertainty term
reweights per variant \cite{deepsong}. The premise is that different assays need different mixtures. This
paper asks how much that premise is worth, and answers with a measurement rather than another architecture.

**Weighting has a ceiling, and the ceiling is reachable.** An oracle that picks the best mixture for each
assay using that assay's own labels reaches **+0.0051** over a constant fitted on the other assays; adding
one expert to the same pool is worth **+0.0122**. The allocation headroom is 42% of the expert gain, and the
two intervals do not overlap. The bound is not the end of the story. Fitted on half an assay's variants and
evaluated on the other half, per-assay weights gain **+0.0047** on substitutions but *lose* 0.0032 on indels,
where assays are small; shrinking them toward the panel-wide constant by `λ = n/(n+k)` gains **+0.0051** and
**+0.0021** instead. Adapting weights is worth doing, at a scale the ceiling sets, and the estimator that
works is partial pooling.

**The expert's headroom is in how a mutation is represented.** A substitution is a difference between two
sequences, and the signal is the difference — not the mutant residue alone, not the site alone. We build an
encoder over reference-minus-mutant features in a ±4-residue neighbourhood, distilled from the two strongest
experts, with a functional-category low-rank residual and eight-seed averaging. Fused with three published
experts at four fixed weights it reaches **0.694** on the official metric against **0.657** for Kermut, the
leaderboard leader. We validate before reporting: recomputing Kermut through our pipeline reproduces the
published per-assay table on 217 of 217 assays with mean absolute difference 0.0, and the same representation
wins six of seven splits on FLIP2, an independently collected benchmark.

**An aggregate score is not a deployment specification.** The model that reaches 0.694 scores 0.851 on
stability assays and 0.642 on activity; the top 5% of its ranking recovers 24.7% of the true top 5%, a
**4.96x** lift over random that rises to 7.7x on stability and falls to 3.4x on activity; and on the largest
assay quartile the advantage over the previous fusion is **+0.00003**. Those three numbers are what let a
laboratory decide how much of the ordering to trust for its own property and its own assay size.

The levers are thus ordered, and so is what to do about each: measure the ceiling before tuning weights, put
the effort into experts, and pool when you do weight.

## Contributions

1. **A bounded, replicated and actionable account of weighting.** Seven mechanisms under one protocol, all
   at or below a tuned constant; an oracle bounding the allocatable gain at +0.0051 against +0.0122 for an
   expert change; and partial pooling, which recovers +0.0051 and +0.0021 where naive per-assay fitting
   loses and recovers less. We argue the oracle and the tuned constant belong in every baseline table.
2. **A measurement of where a mutation's signal lives.** Ablating the representation shows that the
   wild-type-minus-mutant difference and the local neighbourhood carry +0.116 while stacking more layers is
   negative, and a control arm shows the category structure is what the residual needs (+0.0214 against a
   shared branch with a fifth of the parameters). The expert is the vehicle; the finding is that the
   representation, not the capacity, is what moves the number.
3. **A utility characterisation that makes the ranking usable** — top-of-list recall by functional
   category, and the assay-size regime over which the advantage holds. It converts one aggregate number
   into the two facts a campaign needs: how much of the top of the list to trust, and for which property.
4. **A reproducible artifact**: per-mutant predictions for all 696,311 mutants and the code regenerating
   every number, supplied as anonymised supplementary material and released on publication.

## 2 Related work

**Protein fitness prediction.** Three lines converge here. Zero-shot predictors score variants from a
sequence model's likelihood or from multiple-sequence-alignment statistics, without touching assay labels
\cite{esm1v,tranception,msatransformer}. Supervised approaches train on deep mutational scanning data
\cite{fowler2014,yang2019}, either per assay or across a panel; the leaderboard leader is a composite
kernel regression of this kind. The fusion line, which this paper belongs to, combines predictors that
fail differently, and the combination is usually weighted per assay. Benchmarks for this comparison are
themselves a design choice \cite{flip}, and §5.1 therefore verifies the one we use end to end before
reporting any comparison on it.

**Adaptive weighting and gating.** Mixture-of-experts layers and context-conditioned gates are standard
across machine learning, usually justified by heterogeneity of the input distribution. Our negative
result does not contradict that literature; it identifies a regime where the justification fails — the
mixture components are correlated at 0.78 to 0.96 within a unit, and the conditioning variable is not the
one the optimal weights depend on. Reported gains for gating in such regimes should be read against a
tuned constant rather than a fixed prior, and against an oracle.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and a poor
guide to deployment: it is insensitive to where in the ranking errors fall, and it averages over
subpopulations a practitioner treats separately. Our top-of-list analysis by functional category is a
step toward reporting what a downstream experiment would experience.

## 3 Allocation has no headroom

This section establishes that the mixture has nowhere to go. We first evaluate six label-free conditioning mechanisms against a tuned constant, then bound what *any* weighting rule could extract from this expert pool, then show that the bound is reproducible rather than an artefact of fitting
noise.

## 3.1 Protocol and reproducibility

**Benchmark and aggregation.** ProteinGym's supervised substitution benchmark: 217 assays over 186 UniProt
identifiers and the three official splits. We run the benchmark's own aggregation — per-unit Spearman,
averaged over splits, grouped by UniProt identity and coarse functional category, then averaged over the
five categories — and its published evaluation script on a score file we supply rather than reimplementing
the metric.





**Baselines.** Five, in increasing strength: a fixed 50/50 blend of the two strongest experts; a fixed
D+Kermut blend; the tuned constant of §3; a nested constant with per-fold weights; and Kermut alone, which
is also the published leaderboard leader.

**Statistics.** Seed intervals from eight independent full-pipeline runs; assay intervals from a two-level
bootstrap resampling assays within category and seeds together, 4,000 replicates. Comparisons between two
configurations on the same assays use paired differences, because assay-to-assay variance is an order of
magnitude larger than the effect.

## 3.2 Seven mechanisms, one protocol

We evaluate six label-free conditioning mechanisms plus the tuned constant they all must beat, on
ProteinGym \cite{proteingym}: 217 substitution assays, 651 assay-by-split units, official
category-balanced aggregation. Every mechanism is label-free with respect to the assay being scored —
its weights for assay *a* come from other assays or from no labels at all. A model is refitted per assay
on four of five published folds and predicts the fifth; our folds are bit-identical to the released
files, verified on all three schemes for a 9,576-variant assay.

| mechanism | official | Δ vs constant | 95% CI |
|---|---:|---:|---|
| tuned constant (0.05, 0.45, 0.50) | **0.687637** | — | — |
| MLP gate over 17 context statistics | 0.687888 | **+0.000251** | [−0.001924, +0.002545] |
| per-variant uncertainty weighting | 0.687106 | −0.000531 | [−0.001181, +0.000021] |
| k-NN over assay context | 0.687170 | −0.000467 | [−0.001329, +0.000259] |
| per-category constants | 0.687220 | −0.000417 | [−0.000784, −0.000084] |
| ridge context → weights | 0.685109 | −0.002528 | [−0.007833, +0.000676] |
| per-variant consensus (median) | 0.670492 | −0.017146 | [−0.026771, −0.011115] |

One mechanism clears the constant, by +0.00025, with a confidence interval straddling zero; four more
land within 0.0006 below it, the same magnitude on the other side. The two that fail badly do so
instructively — a context regressed onto weights scores below the constant, so the regression is actively
harmful, and a per-variant median discards the magnitude that separates a strong predictor from a weak
one. **No mechanism is separated from a tuned constant by more than the seed-to-seed spread of the models
themselves.**

## 3.3 The bound, measured against the expert lever

Two quantities decide where the effort belongs, and they have to be measured in one pipeline or the
comparison is meaningless. Both below use the same aggregation — per-split Spearman, mean over schemes,
grouped by UniProt identity then by functional category — on the 182 assays where the distilled expert
covers the panel, so that both pools are evaluated on the same units.

**The allocation bound.** Inside the three-expert pool, a per-assay oracle reaches **0.6881** against
**0.6830** for the constant fitted on the other assays: **+0.0051** (95% CI [0.0038, 0.0066]), estimated by
resampling assays and re-aggregating each resample. **The expert lever.** Adding the distilled encoder to the
same pool raises that constant to **0.6952**, a gain of **+0.0122** (95% CI [0.0099, 0.0144]).

**The allocation headroom is 42% of the expert gain, and the intervals do not overlap.** Per-assay weighting
is therefore a real but secondary lever: everything a weighting rule could reach is less than half of what
one expert change delivers. The two quantities are easy to conflate: an oracle over one pool compared against a fixed blend of a
*different*, stronger pool understates the allocation side.

The gate itself behaves as intended — its per-assay weights reproduce across independent seeds at
r = 0.92–0.97 — which locates the shortfall in the objective rather than the optimisation.

## 3.4 Estimating the weights is a separate, solvable problem

The bound says what weightings could reach. Whether an assay's own variants can *find* those weights is a
different question, and it has to be asked out of sample: weights fitted on half an assay's variants and
evaluated on the other half, with the reference constant fitted on the same half of the other assays.

| | substitutions | indels |
|---|---:|---:|
| per-assay weights, out of sample | **+0.0047** | **−0.0032** |
| partial pooling, `λ = n/(n+k)` | **+0.0051** | **+0.0021** |

Unregularised per-assay fitting gains on substitutions and **loses** on indels, where assays are small.
Shrinking each assay's weights toward the panel-wide constant, `w(λ) = (1−λ)·w_panel + λ·w_i` with
`λ = n_i/(n_i+k)` and k selected on the panel and never on the held-out half, gains on both: it matches the
per-assay rule where estimation is feasible and turns a loss into a gain where it is not.

**This is the sharpest comparison in the paper.** The seven mechanisms of §3.2 are the designed answer to
this problem; the best of them captures **+0.00025** over its tuned constant. A two-parameter shrinkage rule
captures **+0.0051** over the constant in its own out-of-sample protocol — twenty times as much, and at the
level the in-sample oracle says is available — and it keeps a positive gain on indels, where unregularised
fitting loses. On this problem the estimation problem was a variance problem rather than a modelling one,
and it has a two-line fix.

## 3.5 A second benchmark: the bound has two parts

We repeat both measurements on ProteinGym's **indel** benchmark — 66 assays, 287,207 variants, a
different mutation type, and a different expert pool: three published supervised indel models whose
out-of-fold predictions ship with the benchmark, so this half involves no training and the comparison is
exact.

| | substitution benchmark | indel benchmark |
|---|---:|---:|
| per-assay oracle minus tuned constant | +0.0051 | **+0.0084** |
| per-assay weights, fitted on half the variants | +0.0047 | **−0.0032** |
| median variants per assay | thousands | **154** |

The oracle gap is 1.6 times larger on indels, which on its own would say allocation headroom is
substantial here. The split test says otherwise: weights selected on half an assay's variants **lose** 0.0032 on the other
half, where the same procedure gains +0.0047 on substitutions. The difference is assay size. Across indel assay-size quartiles the out-of-sample gain is −0.0053,
−0.0023, −0.0002 and **+0.0044**; only the largest, at a median of 490 variants, recovers part of what an
oracle fitted in place suggests.

**The representation transfers, and it carries its own weight.** We build our differential encoder for
indels — the same wild-type/mutant difference and ±4 neighbourhood, with the edit site located by longest
common prefix and suffix — and train it under ProteinGym's released per-variant fold assignment, so our
out-of-fold predictions sit on the same split as the published models. The 226k-variant AAV library is
excluded for runtime, leaving 65 assays.

On measured fitness alone, with no distillation, it scores **0.8401** against 0.8231 for the best published
model and lifts the three-expert blend from 0.8438 to **0.8546**. Distilling from the three published models
then adds a further 0.046, reaching **0.8858** and a four-expert blend of **0.8934**. The weighting headroom
is unchanged throughout — between +0.006 and +0.009 across every pool we trained, against +0.0084 for the
three published models alone. A much stronger pool moves the level, not the allocation bound.

**A third source, outside the ProteinGym suite.** FLIP2 collects its own data and publishes sixteen
predefined splits. Its fixed-length substitution libraries leave seven splits with enough training rows to
fit a head — amylase, ired and trpb — and on those the encoder beats a ridge on mean-pooled ESM-2
embeddings on six of the seven, at a mean test Spearman of **0.43 against 0.26**. The differential features
are not by themselves better: a ridge on them scores 0.15, so the gain is the view combined with a
nonlinear head, which is what the feature ablation of §4.1 shows from the other direction. FLIP2 offers
seven splits rather than hundreds of assays, so it carries the representation claim and cannot carry the
allocation one.

Per-assay weighting is therefore limited twice: by how much the pool disagrees, which the oracle measures,
and by whether the assay carries enough variants to estimate the weights at all. Substitutions have a
small first bound and a partly estimable one; indels have a larger first bound that is almost entirely
estimation noise. **Assay size, not only pool diversity, decides whether adapting weights is worth
attempting** — a rule that a practitioner can apply before fitting anything.

## 3.6 What this means for the field
**Report against tuned constants, not fixed blends.** A gate beating a fixed 50/50 blend by +0.0047 is
commonly reported as evidence that conditioning works; against a constant tuned on held-out assays the
same gate is +0.0002, a statistical tie. The gain attributed to conditioning is mostly the gain from
*tuning at all*.

**A per-assay oracle should be a reported baseline.** It costs nothing to compute and converts "our gate
improves over the previous gate" into "our gate captures *x* percent of the available headroom", which is
the only number telling a reader whether the mechanism is worth its complexity. Here *x* is four percent.

**When the oracle is small, the pool is the problem.** If no weighting of these experts can gain more
than +0.0051, the next +0.01 has to come from an expert that disagrees usefully. §4 builds one.

The claim is bounded by the pool: the oracle is a function of how much the experts disagree, so a pool
built to disagree might make gating worthwhile again — a different paper, and one that would have to
report the oracle too.

## 4 The expert

If allocation is exhausted, the headroom has to be in the experts. This section builds one from a different view of the same information, and then asks which of its design choices actually carry the
gain — including one that looks like capacity and turns out to be structure.

## 4.1 What a mutation is, as a signal

A substitution is a difference. We extract per-residue representations from three ESM-2 650M layers
\cite{esm2} (20, 30, 33) on both the wild-type and the mutated sequence, keep `mut`, `wt` and `mut − wt`,
and pool a ±4-residue window by mean at layers 30 and 33. The union is 12,800 dimensions per variant. The
ladder under the per-assay protocol says where the signal comes from:

| representation | score |
|---|---:|
| site vector only (layer 33) | 0.467 |
| + multiple layers | 0.464 |
| + ±4 neighbourhood | 0.480 |
| **+ wild-type layers and difference terms** | **0.596** |

Stacking layers alone is negative; the gain is in the difference and the wild-type context, worth +0.116,
an order of magnitude more than either other step.

## 4.2 Distillation, and a residual per functional category

A 12,800-dimensional head trained on a few thousand variants per assay overfits before it learns. We
regularise it with the two strongest experts: their per-assay z-scores give a teacher
`t = 0.4·Kermut_z + 0.5·AMK_z`, and the loss is `(1 − α)·MSE(student, target) + α·MSE(student, teacher)`
with α = 0.9. Re-selecting α inside each of the five folds, using only training assays, picks 0.9 in all
five. Distillation is worth +0.114 on the union representation — the largest single step in the encoder's
development, larger than the feature union itself.

Assays fall into five categories that behave differently, so we add a low-rank correction to the head:
`y = MLP(x) + U_c V_cᵀ x`, with `U_c` zero-initialised and rank 8, `c` the assay's category. The branch is
worth **+0.024** standalone and **+0.0014** in the fusion — the gap is the decorrelation argument in
miniature, since a residual that makes an expert better can make it less useful to a pool already holding
what it learned.

**The control that decides the interpretation.** A shared branch with the same rank has one fifth of the
parameters and is indistinguishable from no branch (−0.0008, 2/4 seeds); the per-category branch beats it
by **+0.0214** standalone with every seed positive, on a matched per-branch comparison. **The gain needs
the category structure, not the parameters.** Rank 4 and rank 8 differ by 0.0002, so the branch is
saturated far below what memorising a category would require.

## 4.3 Variance, and four fixed weights

Eight independent runs of the same architecture differ by about 0.004 in the official metric. We average
the predictions per variant rather than the scores: +0.023 standalone, +0.0022 in the fusion, the
asymmetry being that the fusion already averages four experts.

The fusion is four numbers, `0.00·D + 0.40·Kermut + 0.40·AMK + 0.20·X`, selected on the training assays
of each fold and applied to the held-out ones — exactly the protocol the tuned constant uses. The search
drives the additive-structure weight to 0.00 in 14 of 15 seed-by-fold cells and sets the new expert to
0.20 in all 15. Under the official metric:

| configuration | official |
|---|---:|
| previous four-expert fusion | 0.685538 |
| + distilled encoder, category residual | 0.691130 |
| **+ eight-seed averaging** | **0.693311** |

against **0.657028** for Kermut \cite{kermut} — +0.0085 over the previous fusion, +0.037 over the leader.

## 4.4 What the ablation rules out

**Co-distillation from the fusion itself** lifts the expert by +0.0136 (8/8 seeds) and leaves the fusion
at −0.0002: teaching an expert to imitate the pool removes the residual disagreement that gave it value.
**A residual expert** trained on the fusion's own error receives weight exactly zero in every fold — the
residual of a fitted ensemble is what these features cannot explain. Representation diversity without competence buys nothing.

The constructive reading: an expert earns its place through disagreement in the residual, and the way to
get that disagreement is a different *view* of the same information — reference versus mutant, local
versus global — not a different optimiser, loss, or a bigger model.

## 5 What the ranker is worth

The preceding sections argue about where gain comes from. This one asks what the resulting ranker is worth: first on the benchmark's own terms, then on the terms a laboratory actually uses, and finally where it does
not help — which is the part most papers leave out.

## 5.1 Measuring it the way the leaderboard measures it

We run the official `performance_DMS_supervised_benchmarks.py` unmodified on a score file of our
per-assay, per-scheme correlations, and as a control we run the same correlations recomputed from
Kermut's predictions. The control reproduces the published per-assay table on **217 of 217 assays** with
mean absolute difference **0.0**, the residual being the published table's three-decimal rounding, and
our folds are bit-identical to the released distribution.

| model | official | random | modulo | contiguous |
|---|---:|---:|---:|---:|
| Kermut (published rank 1) | 0.657 | 0.745 | 0.633 | 0.593 |
| our fusion, single model | **0.691** | 0.782 | 0.671 | 0.624 |
| our fusion, seed-averaged | **0.694** | 0.784 | 0.674 | 0.625 |

Kermut is one of the four experts, so this is a fusion result and we report it as such: +0.037 is what
adding two complementary experts to the strongest published single model is worth. The equal-compute
comparison is the single-model rung above — one trained expert instead of eight averaged ones — which
still leads Kermut by 0.034.

## 5.2 The aggregate hides the category, and the top of the list

Per functional category:

| category | ours | Kermut | delta |
|---|---:|---:|---:|
| Stability | **0.851** | 0.817 | +0.034 |
| Expression | 0.693 | 0.670 | +0.023 |
| Binding | 0.653 | 0.611 | +0.042 |
| Activity | **0.642** | 0.605 | +0.037 |
| OrganismalFitness | 0.632 | 0.582 | +0.050 |

Every category improves, and the spread is the part that matters downstream: 0.851 against 0.642 is a
0.21 gap, so a laboratory working on an activity assay is operating at the bottom of the range we report.

Spearman is a whole-list statistic. A campaign has a library and can assay tens of candidates, so the
question is whether the top of our ranking contains the top of the true ranking. For each assay and split
we take the top *k* ∈ {1%, 5%, 10%} and measure how many land in the true top *k*, aggregating the
official way:

| top of the list | recall of the true top | random | lift |
|---|---:|---:|---:|
| 1% | **0.119** | 0.010 | **11.8x** |
| 5% | **0.247** | 0.050 | **4.96x** |
| 10% | **0.350** | 0.100 | **3.50x** |

Ordering the top 5% recovers about a quarter of the true top 5%, roughly five times random. It is also
category-dependent, in the direction the category table above predicts: 7.7x on Stability, 4.9x Binding, 4.6x
OrganismalFitness, 4.2x Expression, and **3.4x on Activity** — and activity is what function-oriented
campaigns care about. **The ranker is roughly twice as good at prioritising stability mutants as
activity mutants.**

Ranking and ground truth are both computed within an assay-by-split unit on the released DMS files, so
the reference is independent of §4, and the lift rather than the raw recall is the quantity to compare
across categories.

## 5.3 Where it fails

**87 of 217 assays regress** against the previous four-expert fusion, with a median improvement of
+0.0016 — roughly half the mean, so the gain is carried by a subset. **Expression is the only category
that regresses on average** (−0.0018).

**The effect disappears on large assays.**

| quartile of mutant count | mean delta | regression rate |
|---|---:|---:|
| smallest | **+0.0073** | 0.255 |
| second | +0.0017 | 0.444 |
| third | +0.0024 | 0.407 |
| **largest** | **+0.00003** | 0.500 |

The size regime is therefore part of the method's specification rather than a footnote: the gain is
concentrated in assays with fewer measurements, and on the largest quartile the fusion matches its
predecessor. This is a property of the correlation estimate rather than of the feature budget, since the
baseline has more data there too, and it tells a reader which assays to expect an improvement on.

**Coverage is partial and coupled.** The encoder needs a wild-type sequence and covers 182 of 217 assays;
the other 35 fall back to an older expert, and still show +0.0029 — but not because of their own
predictions: the nested weight search fits one vector per fold over all training assays, so replacing the
expert elsewhere moves the weights applied to them.

## 6 Limitations and Ethical Considerations

### Limitations

**The method's operating range is specific, and §5.3 measures it**: top-of-list recall is roughly twice
as high on stability assays as on activity assays, the improvement over the previous fusion reaches
+0.00003 on the largest assay quartile, and the aggregate is an average over a population that contains
both regimes rather than a property of any particular assay. A practitioner should read the aggregate as
the centre of that range and the per-category numbers as the part that applies to their assay.

**The structural experts are inherited, not retrained inside each outer fold.** Their kernel is recovered
and verified to floating-point precision against the saved per-fold predictions, and every reported number
is reproducible from the published per-mutant scores — but a fully nested protocol would retrain them
within each fold. The one hyperparameter that materially matters, the distillation weight, was re-selected
inside each fold and chose the same value in all five; the broader design space, however, was explored on
this panel.

**Coverage and shift.** The panel is skewed toward particular protein families, organisms and assay types,
and performance is not uniform across them; applying this to a family absent from the benchmark should be
expected to behave like the large-assay regime. There is also no prospective validation. All results are on ProteinGym substitution assays.
There is no held-out cohort from a different source and no wet-lab experiment. Whether top-of-list lift
becomes hit-rate lift in a real screening campaign is untested; it is the next experiment, not a claim.

### Ethical considerations

**Dual use.** Protein fitness predictors can be applied to gain-of-function engineering. Our method ranks
a user-supplied set of single-residue variants; it does not generate sequences, does not perform design,
and offers no capability beyond what public ProteinGym baselines already provide. Ranking is nevertheless
the step deciding which candidates a laboratory synthesises. We release predictions for existing public
assays only.





**Data and released artifacts.** All assays are previously published deep-mutational-scanning datasets distributed by ProteinGym: no new experimental data, no human subjects, no clinical material. The submission includes, as anonymised supplementary material, per-mutant
predictions for all 696,311 mutants, the code reproducing every reported number, and the recovered kernel
for the structural experts; all of it is released publicly on publication. The code is under a permissive
licence, while the expert prediction tables remain research-use only because they derive from third-party
methods — so a reader can re-run our evaluation but cannot redistribute those tables commercially.

**Generative AI usage.** Analysis scripts, evaluation harnesses and LaTeX assembly were written and
revised with an AI coding assistant; the prose was drafted with the same assistant and then reviewed,
corrected and rewritten by the authors. Reference metadata was resolved programmatically against the
NeurIPS and ICML proceedings indexes and the Crossref API rather than recalled, and that verification
caught a wrong paper title and a DOI belonging to a different article. No result reported here was
generated by a model, no AI system is listed as an author, and the authors take full responsibility.

## 7 Discussion

Two things remain: what this work gives the domain it studies, and what would overturn it.

### What this contributes to protein engineering

A protein engineer choosing mutations against an assay budget needs a ranking they can act on, and the
field's papers are not organised around that. Two deliverables follow. The first is a **calibrated
expectation**: taking the top 5% recovers 24.7% of the true top 5%, but 7.7x on stability assays against
3.4x on activity, and no advantage on the largest assays — a laboratory can use that profile to decide
how much of the ordering to trust for the property it cares about, a statement aggregate Spearman cannot
express. The second is **the boundary**: 87 regressing assays, the category that regresses on average, and
the size regime at parity. For a practitioner the boundary is worth more than the mean, because it is the
difference between trusting a ranking on a familiar assay family and being surprised on a new one.

Three AI challenges are tackled. The ranking problem is small-data-per-task learning, so the question is
regularisation and transfer rather than capacity. It is a distribution-shift problem, which is exactly why
the field reached for adaptive weighting and why we show weighting has no headroom. And it is a
representation problem: the signal lives in the difference between two sequences and in the local
structural neighbourhood.

Three challenges arise from using AI here. Wet-lab validation is the binding constraint and it is slow and
expensive, so the field reports against retrospective benchmarks and hopes the ranking transfers; we have
not closed that gap. Assay data is heterogeneous in ways metadata does not capture — two stability assays
on one protein can disagree in sign — so a category-averaged metric can look stable while individual
assays move sharply both ways. And the benchmark ecosystem rewards leaderboard movement over
characterisation, while characterisation is what a domain user needs most.

On our use of ProteinGym: the track prefers domain-specific data to existing benchmarks, so we state what
this adds rather than only takes. We verify the benchmark end to end — reproducing its published
per-assay values for a reference method on 217 of 217 assays, confirming its folds are bit-identical — we
publish per-mutant predictions for all 696,311 variants so the evaluation is reproducible without our
code, and we characterise its difficulty structure across categories, sizes and splits. A reader can use
that characterisation without adopting our method.

### Implications, and what would falsify us

**If you are evaluating.** Report the oracle and the tuned constant alongside any learned weighting, and the
per-category breakdown instead of the mean: a ranker's aggregate correlation and its top-of-list recall can
disagree, and the second is closer to what the downstream experiment measures.



The experiment we would run next is prospective: generate a candidate list from the ranking, assay it
alongside a random control, and measure whether the top-of-list lift becomes a hit-rate lift at the bench.
Until then the honest claim is about rankings, not discoveries.