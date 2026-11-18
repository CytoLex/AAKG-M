# Retargeting to KDD AI for Sciences

**Updated against the KDD 2027 CFP** (`kdd2027.kdd.org/ai4sciences-track-call-for-papers/`), read
2026-11-18. The earlier version of this file was written against the 2026 page; three things changed and
they matter:

1. **A second required section.** Beyond *Limitations and Ethical Considerations*, the 2027 CFP requires
   a separate section titled **Generative AI Usage**. Drafted in `SECTION_6B_GENAI.md`.
2. **Stricter fit criteria.** Two of the four criteria now explicitly deprioritise papers that use
   existing benchmarks directly and papers that build complex technical frameworks. See
   `FIT_ASSESSMENT_2027.md`, which recommends deciding between this track and the Research Track before
   any further writing.
3. **A softer reviewer clause.** 2027 asks for "at least three papers in KDD **or other related
   conferences**", where 2026 demanded three top AI/ML papers or one Nature/Science/Cell paper. Still a
   requirement, materially easier to meet.

## What the track demands

| requirement | detail | our status |
|---|---|---|
| **8 content pages** | ACM `sigconf,review`, double column, single PDF; references and optional appendix outside the limit | **compiled at 8 pages**, 5,600 words, 9 tables, 2 figures |
| **Mandatory section** | *Limitations and Ethical Considerations* | **drafted**, §6 of the built paper |
| **Mandatory section** | *Generative AI Usage* (new in 2027) | **drafted**, §6.1 of the built paper |
| **Single-blind** | author names and affiliations listed | n/a, but removes the anonymisation work |
| **Cycle** | KDD 2027 Cycle 1 closed on 2026-07-19 (abstract) / 2026-07-26 (paper), notification 2026-11-14. Cycle 2 dates are unpublished; the 2026 pattern implies ~February 2027 | **next realistic target, ~3 months out** |
| **Generative AI Usage section** | required separately from Limitations, new in 2027 | drafted in `SECTION_6B_GENAI.md`, wired into the build |
| **OpenReview** | every author needs a complete profile; institutional email avoids a 2-week moderation delay | needs action per author |
| **Qualified reviewer** | 2027 wording: "at least three papers in KDD or other related conferences", or nominate the best-qualified author for the PC chairs | **unverified — the author list is still the open question** |
| **Domain contribution** | "we expect submissions co-authored by experts from domains relevant to the studies... solely authored by AI/ML experts are less preferred" | our authors are computational; framing is ML-first. See `FIT_ASSESSMENT_2027.md` |
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
