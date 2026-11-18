# LaTeX build

`make_tex.py` assembles the markdown sections in the parent directory into `paper.tex`, and `build.sh`
compiles it with the ACM `acmart` class (`sigconf,review,nonacm`). Tectonic fetches the class from the
TeX bundle on first run, so no local TeX installation is needed — only pandoc and a tectonic binary.

```bash
./build.sh          # writes AAKG_KDD_draft.pdf and prints the page count
```

## Measured state

**8 content pages + 1 page of references = 9 pages in the compiled PDF.**

That is the ACM allowance, not a violation: the CFP specifies "8 content pages as main paper, followed
by References and an optional Appendix that has no page limits". Verified by rebuilding with the
bibliography disabled — the content alone is 8 pages — and by counting `/Type /Page` objects in the
decompressed object streams.

I got this wrong twice before noticing. Two earlier rounds cut 370 and then 230 words chasing an 8-page
*total*, when the limit applies to content only. The cuts that removed redundancy were worth making
anyway; the one that removed a real ablation (ESM-C as a fourth expert) has been restored.

Current: 5,735 words, 9 tables, 2 figures, 8 content pages, 9 pages total.

## Figures

`figures/make_figs.py` regenerates both. They are vector PDFs, embedded directly:

- `fig1_allocation_vs_expert` — the shaded allocation band (constant to oracle, +0.0027) against the
  expert arrow (fixed blend to final, +0.0077), on one axis in one protocol.
- `fig2_topk_by_category` — top-of-list recall by functional category at k = 1%, 5%, 10%, with the
  random expectation marked.

## What is still missing before submission

- **Author block.** Placeholders. The track is single-blind, and the list must be final at the deadline.
- **Bibliography.** 14 entries, each verified against the venue's own index or a Crossref DOI lookup
  rather than typed from memory; 11 `\cite` commands appear in the text. Twelve carry full metadata
  including a DOI where one exists; the five NeurIPS/ICML entries are verified by their proceedings
  pages, which do not mint DOIs; `shazeer2017` carries its ICLR venue plus an arXiv locator. The
  verification caught two errors — a wrong paper title and a DOI that resolved to an unrelated letter —
  both recorded in `REFERENCES_TODO.md`.
- **Required section title.** Rendered "Limitations and ethical considerations". KDD 2026 used
  "Limitations and Ethical Considerations" — match the 2027 CFP verbatim, since required-section wording
  is a desk-reject criterion.
- **Overfull boxes.** About a hundred, almost all under 10pt, from pandoc's literal conversion and long
  URLs. Cosmetic; clean them after the content is frozen.
