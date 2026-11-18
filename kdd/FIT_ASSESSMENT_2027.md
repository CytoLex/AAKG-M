# Fit against the KDD 2027 criteria

Read from `kdd2027.kdd.org/ai4sciences-track-call-for-papers/` on 2026-11-18. This matters because the
2027 criteria are **stricter about domain contribution than the 2026 ones** this project was written
against, in ways that bear directly on whether this paper belongs in the track at all.

## The four criteria, quoted, and where we stand

**"Submissions that directly use existing benchmark datasets without special considerations are less
preferred."**

We use ProteinGym directly. Our contribution to the benchmark is real — we validate it down to the
per-assay level and publish per-mutant scores — but we did not *collect* data. This is the paper's
weakest point against the 2027 wording.

**"Submissions that mainly focus on building complex technical frameworks are less preferred."**

Our contribution is four fixed weights and a two-hundred-parameter head; the opposite of a complex
framework. This one we pass comfortably, and it is worth making explicit in the introduction because a
reviewer scanning the abstract may assume otherwise.

**"We expect submissions co-authored by experts from domains relevant to the studies... Submissions
solely authored by AI/ML experts are less preferred."**

Currently unmet; the author list is computational. Note the wording is *less preferred*, not
desk-reject — softer than the reviewer clause, and softer than I stated in earlier rounds.

**"The studies should focus on advancing the science within the targeted discipline(s)."**

Partly. We measure how a ranker behaves rather than discovering biology. The downstream claim — that
top-of-list lift becomes wet-lab hit-rate lift — is explicitly untested.

## What this means for the choice of track

The same CFP says: **"Papers focusing on methodology development should consider the Research Track."**
On a literal reading our paper is method-focused: a falsification of adaptive weighting, plus an expert
construction, plus a characterisation of a ranker. Under the 2027 criteria that is a Research Track
paper wearing AI4S clothes.

The two viable routes:

| route | what it needs | risk |
|---|---|---|
| **AI4S** | a domain co-author, and a paragraph that states the biological contribution in the domain's terms | the two "less preferred" clauses are both live |
| **Research Track** | nothing new; it is a data-mining methodology result and the venue is the natural home | weaker story for "AI for science" positioning |

There is a third: **Datasets & Benchmarks**. We publish per-mutant scores for 696,311 mutants, a
two-command reproduction, and the recovered kernel. That is a genuine benchmark artifact. But the
paper's argument is not about the dataset, so this would require reframing rather than retargeting.

## Recommendation

**Settle the domain co-author first.** If one joins, AI4S becomes viable and the paper improves, because
the domain framing is currently the thinnest part of the argument. If none does, the Research Track is
the honest choice and essentially no rewriting is needed — the methodology content stands on its own.

Everything else in this directory is track-agnostic: the analyses, the figures, the claims, and the
eight-page structure survive the switch.

## Deadlines

KDD 2027 Cycle 1 has already closed (abstract July 19, 2026; paper July 26, 2026; notification
November 14, 2026). Cycle 2 dates are **not yet published**; on the 2026 pattern it should land around
February 2027, which is the realistic target and leaves roughly three months. Verify the dates before
planning anything around them.
