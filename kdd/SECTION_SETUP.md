# §3.0 Experimental setup

Camera-ready draft, ~850 words. This is the subsection the skeleton reserves for the page the current
draft does not fill; it absorbs and replaces the compressed protocol paragraph currently at §3.1.

---

## Setup

**Benchmark.** ProteinGym's \cite{proteingym} supervised substitution benchmark: 217 deep mutational scanning assays over
186 UniProt identifiers, each with three official cross-validation splits — `fold_random_5`,
`fold_modulo_5`, `fold_contiguous_5`. Following the benchmark's own protocol, a model is refitted per
assay on four folds and predicts the fifth, and the ordering is evaluated by Spearman correlation
within each assay-by-split unit, giving 651 units.

**Aggregation.** We use the official chain without modification: per-unit Spearman, averaged over the
three splits, then grouped by UniProt identifier and coarse functional category, then averaged over the
five categories. The grouping step is the one most often skipped in reimplementations: several assays
share a protein, and averaging them before the category step changes the result by about 0.005. Every
number in this paper is produced by the benchmark's own
`performance_DMS_supervised_benchmarks.py`, run unmodified on a score file we provide, rather than by a
reimplementation of its aggregation.

**Splits are the published ones.** Our fold assignments are bit-identical to the released
`cv_folds_singles_substitutions` files — we verified this on all three schemes for a 9,576-variant
assay, 9,576 of 9,576 mutants matching. We did not regenerate splits.

**Models.** Four experts. Two are frozen predictions from published methods: Kermut, a composite
Gaussian-process kernel over sequence and structure features, and AMK, an assay-adaptive mixed structure
kernel; a third, an additive structure kernel, receives weight 0.00 and does not affect scoring. The
fourth is our encoder, described in §4, refitted per assay and per split.

**Feature construction.** Per-residue representations come from ESM-2 650M at layers 20, 30 and 33, on
both the wild-type and the mutated sequence, with a ±4-residue window pooled by mean at layers 30 and
33. Concatenating site vectors, wild-type vectors, window pools and difference terms gives 12,800
dimensions per variant. Features are standardised per assay with the statistics stored alongside each
fit.

**Training the encoder.** A 12,800 → 256 → 64 → 1 head with a category-specific rank-8 linear residual,
trained by the distillation loss of §4.2 with α = 0.9 and selected by early stopping on the held-out
fold of an inner split. Eight independent seeds per assay are trained and their per-variant predictions
are averaged. α and the rank were both re-verified by inner selection: α re-selects to 0.9 in all five
folds, and rank 4 and rank 8 differ by 0.0002.

**Fusion.** Four fixed weights per fold, selected on the training assays by simplex grid search and
applied to the held-out assays — the same procedure the tuned-constant baseline uses, so the comparison
is equal-compute. The grid is a step-0.1 simplex over four weights.

**Baselines.** Five, in increasing strength. A fixed 50/50 blend of the two strongest experts. A fixed
D+Kermut blend. The tuned constant of §3. A nested constant whose weights are selected per fold. And
Kermut alone, which is also the published leaderboard leader on this metric.

**Statistics.** Seed-level intervals come from eight independent runs of the full pipeline. Assay-level
intervals come from a two-level bootstrap that resamples assays within category and seeds together,
4,000 replicates. Where a comparison is between two configurations evaluated on the same assays, we
report paired differences rather than differences of means, because the assay-to-assay variance is
roughly an order of magnitude larger than the effect.

**Reproduction.** Two commands from two public repositories regenerate every number in this paper. The
score file, the per-mutant predictions for all 696,311 variants, the fusion and evaluation scripts, and
the recovered kernel for the two structural experts are in the released artifact (§8). The control row
of §5.1 is produced by the same command as the headline, so a reader can verify that our aggregation is
correct before trusting any comparison we make with it.

**Compute.** One H200 GPU per encoder run, a few hours for a full panel with eight seeds. The structural
experts are frozen, which is why their per-mutant predictions are published rather than left to be
regenerated.

---

## Note on placement

The skeleton put the protocol in a single paragraph of §3.1. Splitting it out is the better structure
for a data-mining venue: reviewers look for the aggregation chain and the statistics before they look at
the method, and burying the "we used their script unmodified" claim inside an argument section wastes
its rhetorical value.

This is also the material that fills the page the current draft is short. It is content a reviewer
would ask for anyway, which is the right way to use the space.
