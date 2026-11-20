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
