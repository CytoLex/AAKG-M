### Protocol and reproducibility

**Benchmark and aggregation.** ProteinGym's supervised substitution benchmark: 217 assays over 186
UniProt identifiers, each with the three official splits, giving 651 assay-by-split units. We use the
benchmark's own aggregation chain unmodified — per-unit Spearman, averaged over splits, grouped by
UniProt identifier and coarse functional category, then averaged over the five categories — and run its
published evaluation script on a score file we supply rather than reimplementing the metric. The grouping
step is the one most often skipped: several assays share a protein, and averaging before the category step
moves the result by about 0.005.

**Models.** Four experts: two frozen published predictions (Kermut, an assay-adaptive mixed structure
kernel), an additive structure kernel that receives weight 0.00 and does not affect scoring, and the
encoder of §4, refitted per assay and per split. Feature construction, the distillation loss, the
category residual and the seed averaging are specified in §4; α and the residual rank were re-selected by
inner selection on training assays only.

**Fusion.** Four weights per fold by step-0.1 simplex search on the training assays, applied to the
held-out ones — the same procedure the tuned-constant baseline uses, so the comparison is equal-compute.

**Baselines.** Five, in increasing strength: a fixed 50/50 blend of the two strongest experts; a fixed
D+Kermut blend; the tuned constant of §3; a nested constant with per-fold weights; and Kermut alone, which
is also the published leaderboard leader.

**Statistics.** Seed intervals from eight independent full-pipeline runs; assay intervals from a two-level
bootstrap resampling assays within category and seeds together, 4,000 replicates. Comparisons between two
configurations on the same assays use paired differences, because assay-to-assay variance is an order of
magnitude larger than the effect.

**Compute and reproduction.** One H200 GPU per encoder run, a few hours for a full panel with eight seeds;
the structural experts are frozen and cost nothing at scoring time. Two commands from two public
repositories regenerate every number here, and the control row of §5.1 is produced by the same command as
the headline, so a reader can check our aggregation before trusting any comparison built on it.
