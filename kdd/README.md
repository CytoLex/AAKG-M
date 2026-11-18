# KDD AI for Sciences retargeting

Working directory for the retarget from CVPR to the KDD AI for Sciences track.

| file | purpose |
|---|---|
| `KDD_PLAN.md` | the track's requirements, read from the KDD 2026 CFP, mapped against what we have |
| `KDD_ANGLE.md` | three candidate framings and the recommended spine/substance/vehicle split |
| `SKELETON_8P.md` | eight-page ACM double-column layout with word budgets and figure/table placement |
| `ABSTRACT_KDD.md` | 380-word abstract written to the track's three evaluation criteria |
| `LIMITATIONS_ETHICS.md` | the mandated *Limitations and Ethical Considerations* section, drafted |
| `RESULTS_TOP_K.md` | top-of-list utility: 11.8x lift at 1%, 4.96x at 5%, by category |
| `RESULTS_FAILURE_ANALYSIS.md` | the regression set, the assay-size effect, the coverage coupling |
| `SECTION_3_ALLOCATION.md` | §3 camera-ready: seven mechanisms, the oracle bound, the magnitude comparison |
| `SECTION_4_EXPERT.md` | §4 camera-ready: differential representation, distillation, category residual, seed averaging |
| `SECTION_1_INTRO.md` | §1 camera-ready: the domain problem, three claims, four contributions |
| `SECTION_2_7_REST.md` | §2 related work and §7 discussion |
| `SECTION_5_UTILITY.md` | §5 camera-ready: official metric, per category, top-of-list, the regressions |
| `figures/` | the two figure sources (`make_figs.py`) and the rendered PDFs |
| `latex/` | `make_tex.py`, `build.sh`, `paper.tex`, the compiled draft, and the measured page count |
| `VENUE_COMPARISON.md` | CCF-A alternatives with verified deadlines: ICML (Jan 22), IJCAI (Jan 11), ACL (Jan 4) |
| `SUBMISSION_CHECKLIST.md` | every CFP requirement against what we have, with the author-only items marked |
| `FIT_ASSESSMENT_2027.md` | the four 2027 evaluation criteria quoted, and the track recommendation |
| `records/` | the JSON records every number in the drafted sections points at |

## Status

**The paper compiles to 8 content pages plus 1 page of references**, with nine tables and two figures,
5,735 words, both mandated sections present, and 14 verified references carrying 11 citations. Every
number traces to `records/`. Build with `cd latex && ./build.sh`.

The writing is done. What remains is entirely on the authors: the track decision, a domain co-author if
AI4S is chosen, the author block, OpenReview profiles, and the reviewer nomination. See
`SUBMISSION_CHECKLIST.md`, which marks each one.


**Blocked on the authors:**

1. **Reviewer nomination.** The track requires each submission to nominate an author with three top
   AI/ML papers (KDD, NeurIPS, ICML, JMLR) or one Nature/Science/Cell paper. Without one, the CFP
   allows nominating the best-qualified author for the PC chairs to consider — a request, not a
   guarantee, and a desk-reject risk.
2. **Domain co-authorship.** The criteria expect co-authors from the studied domain with clear domain
   affiliations, and an explicit statement of what the work contributes to that domain. Our author list
   is computational.

Both are answered by the same conversation, and nothing else in the retarget depends on them.
