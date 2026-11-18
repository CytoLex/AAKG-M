# Retargeting to KDD AI for Sciences

Read from the KDD 2026 AI for Sciences track CFP (`kdd2026.kdd.org/ai4sciences-track-call-for-papers/`)
on 2026-11-18. KDD 2027 will restate these; the structural requirements below have been stable, but
every date and the reviewer clause should be re-checked against the 2027 page before submission.

## What the track demands

| requirement | detail | our status |
|---|---|---|
| **8 content pages** | ACM `sigconf,review`, double column, single PDF; references and an optional appendix outside the limit | drafts are CVPR single-column, ~3.5k English words total — a full rewrite, not a trim |
| **Mandatory section** | a separate section titled *Limitations and Ethical Considerations* | not present; we have scattered caveats |
| **Single-blind** | author names and affiliations listed | n/a, but removes the anonymisation work |
| **Second cycle only** | AI4S accepts submissions only in the February cycle | KDD 2026 was Feb 1 (abstract) / Feb 8 (paper); expect the same window for 2027 |
| **OpenReview** | every author needs a complete profile; institutional email avoids a 2-week moderation delay | needs action per author |
| **Qualified reviewer** | each submission must nominate ≥1 author with ≥3 top AI/ML papers (KDD/NeurIPS/ICML/JMLR) or ≥1 Nature/Science/Cell paper, or the best-qualified author if none qualifies | **unverified — see risks** |
| **Domain contribution** | reviewers expect co-authors from the studied domain and an explicit statement of what the work contributes *to that domain* | our authors are computational; framing is ML-first |
| **Unique data & analysis** | one of the three headline evaluation criteria | strong: 217-assay panel, 651 units, published per-mutant scores, falsification of a whole mechanism class |

## What changes in the story

The CVPR draft argues an ML-methodology point: *adaptive weighting buys nothing; expert construction
does*. That is a data-mining claim, and KDD's research track would accept it. The AI4S track asks a
different question: **what does this let a protein engineer do that they could not before?**

Three shifts are needed.

**1. From "the gate fails" to "allocation was never the bottleneck".** Same evidence, different
emphasis: the per-assay oracle sitting below the fixed blend is a statement about where headroom
lives in a scientific prediction problem — it tells the field not to spend effort on weighting.

**2. From "we get +0.037" to "rankings a wet lab can act on".** The product page already says this;
the paper should quantify it: agreement with measured fitness per functional category, what the
candidate ranking is worth at the top of the list (precision@k style), and where the ranking is
unreliable (the 85 assays that got worse).

**3. From caveats to a real Limitations and Ethical Considerations section.** Our material is unusually
well suited: we can state exactly where the method fails, and the ethics discussion is concrete —
these are fitness predictors for protein engineering, with dual-use relevance for gain-of-function
work.

## The one risk that is not ours to fix alone

The reviewer-nomination clause is a hard gate. If no author on the paper has three top-tier AI/ML
papers or one Nature/Science/Cell paper, the CFP allows nominating the best-qualified author "for
consideration by the PC chairs" — which is a request, not a guarantee, and a desk-reject risk. This
needs to be settled before writing anything else.

## Suggested sequence

1. **Settle the reviewer clause and the author list.** Everything downstream depends on it.
2. **Decide the paper's centre of gravity** — see `KDD_ANGLE.md` for the three candidate framings.
3. **Rebuild the drafts in ACM double-column**, 8 content pages, with the mandated section.
4. **Add the analysis that reviewers will ask for**: top-of-ranking utility, per-category behaviour,
   failure modes, and a wet-lab-facing statement of what changes in practice.
5. **Anchor the reproducibility claim** on what already exists: the GitHub repository, the published
   per-mutant scores, the two-command reproduction, and an Artifacts Available DOI.
