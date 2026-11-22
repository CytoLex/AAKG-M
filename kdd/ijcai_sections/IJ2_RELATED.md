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
known as the forecast combination puzzle, and the standard explanation is weight-estimation error \cite{qian2015forecast}.
The puzzle has been argued to be partly an artefact of low-power tests \cite{frazier2023solving}, which is why we
report assay-level intervals and a permutation null rather than a point comparison. \cite{qian2015forecast} also
separates combining *for improvement* from combining *for adaptation*; that is precisely this paper's split between
the expert lever and the allocation lever, and our contribution is to measure both in one domain and bound the
adaptation side.

**Diversity and ensemble value.** Ensemble error decomposes into average member error minus an ambiguity term, first
for squared loss and then for any twice-differentiable loss \cite{audhkhasi2013generalized}, and diversity has since
been shown to be a hidden dimension of the bias-variance decomposition \cite{wood2023unified}. That literature is
explicit that diversity should be traded off against bias and variance rather than maximised, which is the position
this paper reaches from the other direction: the disagreement between our experts predicts their marginal value
(r = +0.63), but pushing it further costs competence faster than it buys disagreement. Our negative result about
gating does not contradict the gating literature; it locates a regime where the justification fails, because the
mixture components are correlated at 0.78 to 0.96 within a unit and the conditioning variable is not the one the
optimal weights depend on.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and a poor
guide to deployment: it is insensitive to where in the ranking errors fall, and it averages over
subpopulations a practitioner treats separately. Our top-of-list analysis by functional category is a
step toward reporting what a downstream experiment would experience.
