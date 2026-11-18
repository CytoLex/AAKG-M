# Submission checklist against the KDD 2027 AI4S CFP

Every line is a requirement quoted from
`kdd2027.kdd.org/ai4sciences-track-call-for-papers/` (read 2026-11-18), with what we have and what is
still needed. Items marked **YOU** cannot be done by anyone but the authors.

## Format and structure

| requirement | status |
|---|---|
| English, double-column, ACM template, `\documentclass[sigconf,review]{acmart}` | **done** — `latex/paper.tex` |
| Single PDF, **8 content pages**, then References and optional Appendix | **done** — content compiles to exactly 8; references add page 9, which the CFP allows |
| Required section *Limitations and Ethical Considerations* | **done** — §6, title matched verbatim |
| Required section *Generative AI Usage* | **done** — §6.1 |
| Author names and affiliations in the PDF (single-blind; missing author info is desk-rejected) | **YOU** — the block currently holds two placeholders |
| No placeholder or dummy abstract | **done** — abstract is final prose, 380 words of it in `ABSTRACT_KDD.md` |

## Content and claims

| requirement | status |
|---|---|
| "Unique data & analysis" | partly — we use ProteinGym but verify it end to end and publish per-mutant scores; §7.1 argues the case explicitly |
| "Clear, detailed descriptions of how data was collected, preprocessed, managed, analysed" | **done** — §3.1 Setup |
| "Focus of studies... advancing the science within the targeted discipline" | weakest link — the strategy is `FIT_ASSESSMENT_2027.md`, and it needs a decision |
| "Co-authored by experts from domains relevant to the studies" | **YOU** — no domain co-author at present |
| "Key contributions of the work to their domain" | **done** — §7.1 |
| "Challenges tackled by AI/ML" and "challenges with using AI/ML in their domain" | **done** — §7.1 |
| Ethics, data privacy, consent, bias, misuse, limitations | **done** — §6, seven measured limitations and four ethical points |

## Process

| requirement | status |
|---|---|
| Every author has a complete OpenReview profile | **YOU** — each needs current and past affiliation (5 years), homepage, DBLP, ORCID, advisors, recent publications. Institutional email avoids a two-week moderation delay |
| Nominate a qualified reviewer (≥3 papers at KDD or related conferences), or the best-qualified author if none qualifies | **YOU** — form link is in the CFP; the nomination form is sent after the abstract deadline |
| ≤4 submissions per author per cycle | **YOU** — check against the author list |
| Author list final at the paper deadline; no additions or reordering after | **YOU** |
| Deadlines strict, no extensions | **YOU** — Cycle 2 dates unpublished; 2026's second cycle opened in February |

## Before pressing submit

1. Decide track: AI4S or Research Track (`FIT_ASSESSMENT_2027.md`). **This changes the paper's framing,
   not its content.**
2. Fill the author block, and record each author's OpenReview readiness.
3. Nominate the reviewer.
4. Re-read `latex/README.md` for the build and the two known-cosmetic issues (about a hundred overfull
   boxes, all under 10pt).
5. Refresh the CFP page — Cycle 2 is not published yet, and the 2027 wording may have been edited since
   this file was written.
