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

**Weighting has a ceiling, and the ceiling depends on what you measure.** An oracle that picks the best mixture
per assay using that assay's own labels reaches **+0.0051** over a constant fitted on the other assays, against
**+0.0122** for adding one expert: 42%, intervals disjoint. That bound is Spearman's. Under top-1% recall — what
a campaign actually experiences — the transferable headroom is **2.8 times larger**, and a rule that optimises
that recall and then shrinks beats weights a Spearman objective selects by **+0.0093** (CI [+0.0014, +0.0171]).
Fitted out of sample, per-assay weights gain +0.0047 on substitutions but *lose* 0.0032 on indels; shrinkage by
`λ = n/(n+k)` gains +0.0051 and +0.0021 instead.

**An expert is worth its disagreement, not its accuracy.** Across thirteen expert-into-pool pairs, marginal
value tracks disagreement at r = **+0.786** and not standalone score: **the weakest expert alone contributes the
most, and the strongest contributes almost nothing.** A noise column, a shuffled copy and a negated copy all
score exactly zero, so the measurement is not an artefact of enlarging the weight search. The objective is
residual disagreement subject to a competence floor, and the floor is measurable — the expert we build sits
within 0.0009 of it.

**That principle selects the representation.** A substitution is a difference between two sequences, so the view
that produces useful disagreement is the difference: reference-minus-mutant features in a ±4-residue
neighbourhood, distilled, with a functional-category residual. Fused at four fixed weights this reaches **0.694**
against **0.657** for Kermut, having first reproduced Kermut's published per-assay table on 217 of 217 assays to
mean absolute difference 0.0; the same representation wins six of seven FLIP2 splits.

**An aggregate score is not a deployment specification.** The model that reaches 0.694 scores 0.851 on stability assays and
0.642 on activity, and the top 5% of its ranking recovers 23.9% of the true top 5% — a **4.8x** lift that is 7.8x
on stability and 3.5x on activity. Those numbers let a laboratory decide how much of the ordering to
trust for its own property and assay size.

The levers are ordered, and so is what to do about each: measure the ceiling before tuning weights, spend on
experts that disagree rather than experts that score well, pool when you do weight, and optimise the metric you
will be judged by rather than the one that is convenient.

## Contributions

1. **A diagnostic protocol for fusion, and what it finds here.** Three numbers per pool — the oracle bound,
   the estimability of the weights, and the shrinkage that reaches it. Applied to
   seven gating mechanisms, three benchmarks and two expert pools it gives +0.0051 of allocatable headroom
   against +0.0122 for an expert change, and a shrinkage rule that recovers +0.0051 and +0.0021 where naive
   per-assay fitting loses. Applied to the deployment metric instead, the same protocol finds 2.8 times the
   headroom and yields a two-line rule that reaches all of it. The natural cross-pool comparison would have
   reported +0.0027 for the same quantity, an 85% error.
2. **An expert's value is its disagreement, not its accuracy**, measured at r = +0.786 across thirteen
   expert-into-pool pairs with noise, shuffle and negate controls at zero, and bounded by a competence floor we
   map. The representation follows from the principle rather than motivating it: the difference view carries
   +0.116 where stacking layers is negative, and a control arm shows the category structure is what the
   residual needs (+0.0214 against a shared branch with a fifth of the parameters).
3. **A utility characterisation that makes the ranking usable** — top-of-list recall by functional
   category, and the assay-size regime over which the advantage holds. It converts one aggregate number
   into the two facts a campaign needs: how much of the top of the list to trust, and for which property.
4. **A reproducible artifact**: per-mutant predictions for all 696,311 mutants and the code behind every reported
   number, supplied as anonymised supplementary material and released on publication, with the scope of what
   regenerates exactly stated in §6.

## 2 Related work

**Protein fitness prediction.** Three lines converge here. Zero-shot predictors score variants from a
sequence model's likelihood or from multiple-sequence-alignment statistics, without touching assay labels
\cite{esm1v,tranception,msatransformer}. Supervised approaches train on deep mutational scanning data
\cite{fowler2014,yang2019}, either per assay or across a panel; the leaderboard leader is a composite
kernel regression of this kind. The fusion line, which this paper belongs to, combines predictors that
fail differently, and the combination is usually weighted per assay. Benchmarks for this comparison are
themselves a design choice \cite{flip}, and §5.1 therefore verifies the one we use end to end before
reporting any comparison on it.

**Adaptive weighting, and the combination puzzle.** Mixture-of-experts layers and context-conditioned gates are
standard across machine learning \cite{jacobs1991,shazeer2017}. Forecast combination has studied their limits for
longer: combining several forecasts by estimating weights is routinely no better than averaging them, a result
known as the forecast combination puzzle \cite{timmermann2006forecast}, with a theoretical explanation in which
weight-estimation error outweighs the benefit of weighting \cite{claeskens2016forecast}.
It has been argued partly an artefact of low-power tests \cite{frazier2023solving}, which is why our comparisons
carry assay-level intervals and a permutation null. \cite{qian2015forecast} separates combining *for improvement* from
combining *for adaptation* — this paper's expert and allocation levers — and our contribution is to measure both in
one domain and bound the adaptation side.

**Diversity and ensemble value.** Ensemble error decomposes into average member error minus an ambiguity term, first
for squared loss and then for any twice-differentiable loss \cite{audhkhasi2013generalized}, and diversity has since
been shown to be a hidden dimension of the bias-variance decomposition \cite{wood2023unified}. That literature is
explicit that diversity should be traded off against bias and variance rather than maximised, which is where this
paper arrives from the other direction: disagreement predicts an expert's marginal value (r = +0.63), but pushing
it further costs competence faster than it buys disagreement.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and a poor guide to
deployment: it ignores where in the ranking errors fall and averages over subpopulations a practitioner treats
separately. Our top-of-list analysis by category reports what a downstream experiment would experience.

## 3 What allocation is worth

This section asks how much of the mixture's gain is reachable, in three measurements: what a per-assay
oracle could extract, how much of that an assay's own data can estimate, and which estimator reaches it. Six
label-free conditioning mechanisms set the baseline for the first question, against the tuned constant they
all have to beat.

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

**A fusion result needs three numbers, not one**: how much any weighting of the pool could gain (an oracle),
how much of that an assay's own data can estimate (a split-half), and which estimator reaches it. Reporting
only the first invites a cross-pool comparison that is easy to make and wrong — that comparison reads +0.0027
for this paper's own allocation headroom, against **+0.0051** measured inside one pool, an 85% error.

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

One mechanism clears the constant by +0.00025 with an interval straddling zero; four land within 0.0006
below. **None is separated from the constant by more than the seed-to-seed spread of the models themselves.**

**And the constant is not separated from a parameter-free average either.** Averaging the experts' within-assay
ranks — no labels, no parameters — reaches **0.6942** against the tuned constant's **0.6952**, a paired difference of
**−0.0010** with a 95% CI of [−0.0031, +0.0011]. So nothing in this section separates from simple rank averaging,
tuned or learned: the comparison the mechanisms had to survive was itself only tied with a rule that requires no
fitting at all.

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

The gate itself behaves as intended — its per-assay weights reproduce across seeds at r = 0.92–0.97 — which
locates the shortfall in the objective, not the optimisation.

## 3.4 Estimating the weights is a separate, solvable problem

The bound says what weightings could reach. Whether an assay's own variants can *find* those weights is a
different question, and it has to be asked out of sample: weights fitted on half an assay's variants and
evaluated on the other half, with the reference constant fitted on the same half of the other assays.

| | substitutions | indels |
|---|---:|---:|
| per-assay weights, out of sample | +0.0047 | **−0.0032** |
| partial pooling, k tuned | +0.0051 | +0.0021 |
| **partial pooling, λ derived** | **+0.0051** | **+0.0022** |

Unregularised per-assay fitting gains on substitutions and **loses** on indels, where assays are small. Shrinking
each assay's weights toward the panel-wide constant, `w(λ) = (1−λ)·w_panel + λ·w_i`, gains on both — the figures
below are over the constant fitted in this out-of-sample protocol, not the §3.3 one.

**Shrinkage is the fix, and a single level is enough.** The strength has a closed form — `λ_i = τ²/(τ² + σ²_i)`,
with σ²_i the sampling variance of an assay's fitted weights from six half-splits and τ² the between-assay
variance — and on indels it reaches **+0.0022** against +0.0025 for a hand-tuned k with no search.

The control says what does the work: **permuting those coefficients across assays** changes the gain by at most
**+0.0005** on indels, inside the permutation's own spread, and is 0.0009 *better* on substitutions. **What matters is that the
estimate is shrunk at all, not how finely**: on indels a flat λ of 0.60 gains +0.0062 where the derived median of
0.41 gains +0.0052, so the closed form is, if anything, over-shrinking. We report the per-assay version for needing
no hand-chosen constant, not because its adaptivity earns anything.

**And it is predictable before you fit.** The oracle gain is not evenly spread across assays. It is explained by
the **ambiguity** of the pool on that assay — the variance of the experts' own scores, the term the ensemble
decomposition turns on \cite{audhkhasi2013generalized,wood2023unified} — and, negatively, by how much data the
assay has (r = −0.279). A leave-one-assay-out predictor from those two statistics reaches r = **+0.628** without fitting a per-assay
weight vector, so whether adapting the weights is worth attempting can be read off before any of it is done.

**And it is not spread evenly.** Ranking assays by pool ambiguity, the top quartile holds **57%** of the total
allocation headroom with a median gain of **+0.0117**; the bottom quartile is flat, at +0.0009 and 5%. Restricting
the oracle to the quarter the predictor ranks highest still captures **+0.0050** of the +0.0077 available. A
practitioner with a panel can therefore rank their own assays by ambiguity and know, before fitting anything,
which ones make adaptation worth the attempt.

Disagreement between the raw predictions is weaker, at r = +0.509, and skill-weighting it makes it weaker still
(+0.491): what helps is the spread of the experts' *scores*, not the correlation of their *predictions*. Consistent
with that literature we report this as a trade-off, not a maximand — pushing disagreement further by residualising
an expert against the pool collapsed its accuracy to −0.33 and bought nothing.

**This is the sharpest comparison in the paper.** The best of the seven designed mechanisms captures +0.00025 over
its tuned constant; a two-parameter shrinkage captures **+0.0051** in its own protocol — twenty times as much — and
stays positive where unregularised fitting loses. The estimation problem was a variance problem, and its fix need
not know the variance.

## 3.5 A second benchmark: the bound has two parts

We repeat both measurements on ProteinGym's **indel** benchmark — 66 assays, 287,207 variants, a
different mutation type, and a different expert pool: three published supervised indel models whose
out-of-fold predictions ship with the benchmark, so this half involves no training and the comparison is
exact.

| | substitutions | indels |
|---|---:|---:|
| oracle minus constant | +0.0051 | **+0.0084** |
| median variants | thousands | **154** |

The oracle gap is 1.6 times larger on indels, which on its own would say the headroom is substantial here. The
split test says otherwise: weights fitted on half an assay's variants **lose** 0.0032, where the same procedure
gains +0.0047 on substitutions. The difference is assay size — across indel quartiles the out-of-sample gain runs
−0.0053, −0.0023, −0.0002 and **+0.0044**, so only the largest, at a median of 490 variants, recovers any of it.

**The representation transfers too.** Our differential encoder is the strongest single expert on the indel
pool at **0.8858** against 0.8231 for the best published model, and lifts the three-expert blend from 0.8438
to **0.8934**. On a third, independently collected benchmark — FLIP2's seven usable splits — it beats a ridge
on mean-pooled ESM-2 embeddings on six of seven (mean test Spearman **0.43 against 0.26**), though not on the
features alone: a ridge on them scores 0.15, so the gain belongs to the view combined with a nonlinear head.

Per-assay weighting is therefore limited twice: by how much the pool disagrees, which the oracle measures,
and by whether the assay carries enough variants to estimate the weights at all. Substitutions have a
small first bound and a partly estimable one; indels have a larger first bound that is almost entirely
estimation noise. **Assay size, not only pool diversity, decides whether adapting weights is worth attempting.**

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

**When the oracle is small, the pool is the problem**: the next +0.01 has to come from an expert that disagrees
usefully, which §4 builds.

The claim is bounded by the pool: a pool built to disagree more could make gating worthwhile again.

## 4 The expert

Allocation is bounded in the aggregate and larger under the deployment metric, but on neither measure is it the
lever: an expert change is worth more than twice as much. This section builds one from a different view of the
same information, then measures which of its design choices carry the gain and which are capacity in disguise.

## 4.1 A mechanism test decides the features

If a mutation's effect were a property of the mutant residue, the residue alone would predict it. We test that
instead of assuming a representation. Three ESM-2 650M layers \cite{esm2} (20, 30, 33) are extracted on both the
wild-type and the mutated sequence, and the question is what has to be passed to the head:

| representation | score | increment |
|---|---:|---:|
| site vector of the mutant (layer 33) | 0.467 | — |
| + three layers stacked | 0.464 | **−0.003** |
| + ±4-residue neighbourhood | 0.480 | +0.016 |
| **+ wild-type layers and difference terms** | **0.596** | **+0.116** |

The mutant's absolute state, even given its neighbourhood, is 0.129 below the differential view, and stacking
more layers on top of the absolute state *loses* ground. The effect is not a property of the mutant residue;
it is a property of the change, read in context. The features follow from that: 12,800 dimensions of `mut`, `wt` and `mut − wt` with mean-pooled ±4 windows.
**The representation is a conclusion about the problem, not a design choice asked of the reader.**

## 4.2 Distillation, and a residual per functional category

A 12,800-dimensional head trained on a few thousand variants per assay overfits before it learns, so we regularise
it with the two strongest experts: their per-assay z-scores give a teacher `t = 0.4·Kermut_z + 0.5·AMK_z`, and the
loss mixes the target with it at α = 0.9, re-selected inside each fold on training assays and chosen 0.9 in all
five. Distillation is worth +0.114 — the largest single step in the encoder's development.

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

Eight runs of the same architecture differ by about 0.004 in the official metric, so we average predictions per
variant rather than scores: +0.023 standalone but only +0.0022 in the fusion, which already averages four experts.

The fusion is four numbers, `0.00·D + 0.40·Kermut + 0.40·AMK + 0.20·X`, selected on the training assays
of each fold and applied to the held-out ones — exactly the protocol the tuned constant uses. The search drives the additive-structure weight to 0.00 in 14 of 15 seed-by-fold cells and the new expert to 0.20
in all 15. Under the official metric:

| configuration | official |
|---|---:|
| previous four-expert fusion | 0.685538 |
| + distilled encoder, category residual | 0.691130 |
| **+ eight-seed averaging** | **0.693311** |

against **0.657028** for Kermut \cite{kermut} — +0.0085 over the previous fusion, +0.037 over the leader.

## 4.4 What the ablation rules out

Two ablations agree: **co-distillation from the fusion** lifts the expert by +0.0136 but leaves the fusion at
−0.0002, and **a residual expert** trained on the fusion's own error receives weight zero in every fold.

**An expert's value is its disagreement, not its accuracy.** Measuring this directly: each of the five experts
in the bundle is added to the pool formed by the other four, under the nested-constant protocol, and its marginal
value compared with its standalone score and with its disagreement from that pool.

| expert | solo | marginal | disagr. |
|---|---:|---:|---:|
| encoder §4.1 | 0.6449 | **+0.0118** | **0.194** |
| Kermut | 0.6551 | +0.0062 | 0.143 |
| Kseq | 0.6364 | +0.0004 | 0.104 |
| D | 0.6561 | +0.0000 | 0.064 |
| AMK | **0.6651** | +0.0028 | 0.060 |

Marginal value tracks disagreement at r = **+0.786** across the thirteen pairs, and not accuracy: **the weakest
expert alone contributes the most, and the strongest almost nothing.** A noise column, a shuffled copy and a negated
copy each score **+0.0000**, so the measurement is not an artefact of enlarging the weight search.

That reframes what building an expert means: useful disagreement comes from a different *view* of the same
information — reference versus mutant, local versus global — not from a different optimiser, loss or bigger model.
The objective is to maximise residual disagreement subject to a competence floor, and **the floor is measurable**.
Degrading the expert's predictions with noise traces a clean frontier: marginal value peaks at a small degradation
(ε = 0.25 gains **+0.0086** against +0.0077 untouched) and then falls monotonically to +0.0063 at ε = 2. **The
expert sits within 0.0009 of the frontier** — a slightly less accurate version would contribute slightly more, and
the curve falls away steeply from there. The same sweep along a residualisation axis is not a frontier: its
isolated second peak comes from re-importing per-assay structure, the artefact §3.4 identifies. **The principle is not specific to proteins**: for any pool, an expert contributes what the pool cannot already
explain, and its accuracy alone is a poor guide.

## 5 What the ranker is worth

The preceding sections argue about where gain comes from. This one asks what the ranker is worth — on the
benchmark's own terms, on the terms a laboratory uses, and where it does not help.

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

Kermut is one of the four experts, so this is a fusion result and we report it as such: +0.037 is what adding two
complementary experts to the strongest published single model is worth. The equal-compute comparison is the
single-model rung, one trained expert rather than eight averaged, which still leads Kermut by 0.034.

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

| top of the list | recall of the true top | lift over random |
|---|---:|---:|
| 1% | **0.112** [0.099, 0.125] | **11.2x** [9.9x, 12.5x] |
| 5% | **0.239** [0.223, 0.255] | **4.78x** [4.46x, 5.10x] |
| 10% | **0.343** [0.329, 0.357] | **3.43x** [3.29x, 3.57x] |

Intervals are bootstrap over assays. These are the values the released scores regenerate under the fixed fusion of
§4.3; the per-fold weight search used for the headline score is not in the release, and reproduces them to within
0.01 rather than exactly.

Ordering the top 5% recovers about a quarter of the true top 5%, roughly five times random. It is also
category-dependent in the direction the table above predicts: **7.8x on Stability** [7.4, 8.1], 4.2x Binding
[3.1, 5.3], 4.1x Expression [3.4, 4.7], and **3.5x on Activity** [3.0, 3.9] — and activity is what
function-oriented campaigns care about. **The ranker is roughly twice as good at prioritising stability mutants as
activity mutants**, and the intervals separate.

Ranking and ground truth are computed within an assay-by-split unit on the released files, so the reference is
independent of §4; the lift, not the raw recall, is what compares across categories.

## 5.3 The operating range

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

**The operating range is specific and §5.3 measures it**: recall is twice as high on stability as on activity, and
the improvement reaches +0.00003 on the largest quartile. The aggregate is the centre of that range, not a property
of any one assay.

**The structural experts are inherited, not retrained inside each outer fold**, and every reported number is
reproducible from the published per-mutant scores except the per-fold fusion weights, which are summarised rather
than released — the utility figures in §5.2 therefore regenerate to within 0.01 under the fixed fusion rather than
exactly. A fully nested protocol would retrain the structural experts within each fold. The one hyperparameter that materially matters, the distillation weight, was re-selected inside each
fold and chose the same value in all five.

**Coverage and shift.** The panel is skewed toward particular families, organisms and assay types and performance
is not uniform across them; a family absent from it should be expected to behave like the large-assay regime.

**Scope of the evaluation.** Every result is on ProteinGym substitutions, ProteinGym indels, or FLIP2's
published splits, and the top-of-list analysis characterises a *ranking*. Turning an enriched ranking into a
measured hit rate is a prospective study against a wet-lab readout — a different experiment with a different
design. The claims here stop at the ranking.

### Ethical considerations

**Dual use.** Protein fitness predictors can be applied to gain-of-function engineering. Our method ranks
a user-supplied set of single-residue variants; it does not generate sequences, does not perform design,
and offers no capability beyond what public ProteinGym baselines already provide. Ranking is nevertheless
the step deciding which candidates a laboratory synthesises. We release predictions for existing public
assays only.





**Data and released artifacts.** All assays are previously published deep-mutational-scanning datasets distributed
by ProteinGym: no new experimental data, no human subjects, no clinical material. The submission includes, as
anonymised supplementary material, per-mutant predictions for all 696,311 mutants, the code behind every reported
number, and the recovered kernel for the structural experts. The code is permissively licensed; the expert prediction tables are research-use only because they derive from
third-party methods.

**Generative AI usage.** Analysis scripts, evaluation harnesses and LaTeX assembly were written and
revised with an AI coding assistant; the prose was drafted with the same assistant and then reviewed,
corrected and rewritten by the authors. Reference metadata was resolved programmatically against the
NeurIPS and ICML proceedings indexes and the Crossref API rather than recalled, and that verification
caught a wrong paper title and a DOI belonging to a different article. No result reported here was
generated by a model, no AI system is listed as an author, and the authors take full responsibility.

## 7 Discussion

Two things remain: what this work gives the domain it studies, and what would overturn it.

### What this contributes to protein engineering

A protein engineer choosing mutations against an assay budget needs a ranking they can act on, and the field's
papers are not organised around that. Two deliverables follow. The first is a **calibrated expectation**: the top 5% recovers
23.9% of the true top 5%, 7.8x on stability assays against 3.5x on activity, and no advantage on the largest — a profile that lets a laboratory decide how much of the ordering to trust for its own property, which
aggregate Spearman cannot express. The second is **the boundary** — the regressing assays, the category that regresses on average, and the size
regime at parity. For a practitioner the boundary is worth more than the mean: it is the difference between
trusting a ranking on a familiar assay family and being surprised on a new one.

Three AI challenges are tackled. The ranking problem is small-data-per-task learning, so the question is
regularisation rather than capacity. It is a distribution-shift problem, which is why the field reached for
adaptive weighting and why the reachable part of that lever is 42% of an expert change. And it is a representation
problem: the signal lives in the difference between two sequences, read in its local context.

Three challenges arise from using AI here. Wet-lab validation is the field's binding constraint, and this paper
places its claims at the ranking rather than the bench. Assay data is heterogeneous in ways metadata does not
capture — two stability assays on one protein can disagree in sign — so a category-averaged metric can look stable
while individual assays move sharply both ways. And the ecosystem rewards leaderboard movement over
characterisation, which is what a domain user needs most.

On our use of ProteinGym: rather than only taking from a public benchmark we verify it end to end, publish
per-mutant predictions for all 696,311 variants so the evaluation stands without our code, and characterise its
difficulty structure across categories, sizes and splits. A reader can use that characterisation without adopting
our method.

### What this work gives, and what would overturn it





The experiment we would run next is prospective: generate a candidate list from the ranking, assay it
alongside a random control, and measure whether the top-of-list lift becomes a hit-rate lift at the bench.
Until then the honest claim is about rankings, not discoveries.

**What would overturn this.** Three developments would move the conclusion, and each is measurable with the
protocol of §3. A pool whose experts disagree more than this one's — the oracle is a function of
disagreement, r = +0.534 — would raise the ceiling. An assay regime with many more variants per assay would
make the weights estimable where they are not, shifting the bound from "small" to "large enough to matter". A
gating mechanism that beats a tuned constant by more than the seed-to-seed spread would break the claim that
none does. Any of the three would be reported by the same three numbers this paper reports.