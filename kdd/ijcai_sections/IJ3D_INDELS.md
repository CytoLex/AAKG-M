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
