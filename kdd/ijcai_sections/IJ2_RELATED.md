**Protein fitness prediction.** Three lines converge here. Zero-shot predictors score variants from a
sequence model's likelihood or from multiple-sequence-alignment statistics, without touching assay labels
\cite{esm1v,rives2021esm1b,tranception,msatransformer}. Supervised approaches train on deep mutational scanning data
\cite{fowler2014,yang2019}, either per assay or across a panel; the leaderboard leader is a composite
kernel regression of this kind. The fusion line, which this paper belongs to, combines predictors that
fail differently, and the combination is usually weighted per assay. Benchmarks for this comparison are
themselves a design choice \cite{flip}, and §5.1 therefore verifies the one we use end to end before
reporting any comparison on it.

**Adaptive weighting, and the combination puzzle.** Mixture-of-experts layers and context-conditioned gates are
standard across machine learning \cite{jacobs1991,shazeer2017,fedus2022switch}. Forecast combination has studied their limits for
longer: combining several forecasts by estimating weights is routinely no better than averaging them, a result
known as the forecast combination puzzle \cite{timmermann2006forecast}, with a theoretical explanation in which
weight-estimation error outweighs the benefit of weighting \cite{claeskens2016forecast}.
It has been argued partly an artefact of low-power tests \cite{frazier2023solving}, which is why our comparisons
carry assay-level intervals and a permutation null. \cite{qian2019forecast} separates combination that merely reaches the best member from
combination that exceeds all of them, a distinction our two levers are easily conflated with: changing the pool
changes what can be reached, reweighting it does not. We measure both levers in one domain and bound the second.

**Diversity and ensemble value.** Ensemble error decomposes into average member error minus an ambiguity term, first
for squared loss and then for any twice-differentiable loss \cite{audhkhasi2013generalized}, and diversity has since
been shown to be a hidden dimension of the bias-variance decomposition \cite{wood2023unified}. That literature is
explicit that diversity should be traded off against bias and variance rather than maximised, which is where this
paper arrives from the other direction: disagreement predicts an expert's marginal value (r = +0.786 over thirteen pairs), but pushing
it further costs competence faster than it buys disagreement.

**Evaluation practice in AI for science.** Aggregate correlation is the standard reporting unit and a poor guide to
deployment: it ignores where in the ranking errors fall and averages over subpopulations a practitioner treats
separately. Our top-of-list analysis by category reports what a downstream experiment would experience.
