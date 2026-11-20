## 3.5 A second benchmark: the bound has two parts

We repeat both measurements on ProteinGym's **indel** benchmark — 66 assays, 287,207 variants, a
different mutation type, and a different expert pool: three published supervised indel models whose
out-of-fold predictions ship with the benchmark, so this half involves no training and the comparison is
exact.

| | substitution benchmark | indel benchmark |
|---|---:|---:|
| per-assay oracle minus tuned constant | +0.0027 | **+0.0084** |
| share of that gap surviving a held-out-variant split | 49% | **−19%** |
| median variants per assay | thousands | **154** |

The oracle gap is three times larger on indels, which on its own would say allocation headroom is
substantial here. The split test says otherwise: weights selected on half an assay's variants **lose** to
the constant by 0.0024 on the other half — negative in all ten random splits we drew (±0.0020) — where the
same procedure on substitutions transfers 49% of the in-place gain. The difference is assay size. Across indel assay-size quartiles the transfer is −0.0053,
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

Per-assay weighting is therefore limited twice: by how much the pool disagrees, which the oracle measures,
and by whether the assay carries enough variants to estimate the weights at all. Substitutions have a
small first bound and a partly estimable one; indels have a larger first bound that is almost entirely
estimation noise. **Assay size, not only pool diversity, decides whether adapting weights is worth
attempting** — a rule that a practitioner can apply before fitting anything.
