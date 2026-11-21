## 3.5 A second benchmark: the bound has two parts

We repeat both measurements on ProteinGym's **indel** benchmark — 66 assays, 287,207 variants, a
different mutation type, and a different expert pool: three published supervised indel models whose
out-of-fold predictions ship with the benchmark, so this half involves no training and the comparison is
exact.

| | substitution benchmark | indel benchmark |
|---|---:|---:|
| per-assay oracle minus tuned constant | +0.0051 | **+0.0084** |
| median variants per assay | thousands | **154** |

The oracle gap is 1.6 times larger on indels, which on its own would say allocation headroom is
substantial here. The split test says otherwise: weights selected on half an assay's variants **lose** 0.0032 on the other
half, where the same procedure gains +0.0047 on substitutions. The difference is assay size. Across indel assay-size quartiles the out-of-sample gain is −0.0053,
−0.0023, −0.0002 and **+0.0044**; only the largest, at a median of 490 variants, recovers part of what an
oracle fitted in place suggests.

**The representation transfers too.** Our differential encoder is the strongest single expert on the indel
pool at **0.8858** against 0.8231 for the best published model, and lifts the three-expert blend from 0.8438
to **0.8934**. On a third, independently collected benchmark — FLIP2's seven usable splits — it beats a ridge
on mean-pooled ESM-2 embeddings on six of seven (mean test Spearman **0.43 against 0.26**), though not on the
features alone: a ridge on them scores 0.15, so the gain belongs to the view combined with a nonlinear head.

Per-assay weighting is therefore limited twice: by how much the pool disagrees, which the oracle measures,
and by whether the assay carries enough variants to estimate the weights at all. Substitutions have a
small first bound and a partly estimable one; indels have a larger first bound that is almost entirely
estimation noise. **Assay size, not only pool diversity, decides whether adapting weights is worth
attempting** — a rule that a practitioner can apply before fitting anything.
