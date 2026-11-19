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
