# LaTeX build

`make_tex.py` assembles the markdown sections in the parent directory into `paper.tex`, and `build.sh`
compiles it with the ACM `acmart` class (`sigconf,review,nonacm`). Tectonic fetches the class from the
TeX bundle on first run, so no local TeX installation is needed — only pandoc and a tectonic binary.

```bash
./build.sh          # writes AAKG_KDD_draft.pdf and prints the page count
```

## Measured state

**8 pages**, with nine tables and two figures. Verified twice: macOS metadata and by decompressing the
PDF object streams and counting `/Type /Page` objects.

That is the target, and it was reached by cutting rather than by compressing. The intermediate state is
worth recording because it inverted my earlier estimate:

| state | words | figures | pages |
|---|---:|---:|---:|
| sections drafted, estimated from word count | 4,951 | — | ~7 (guess) |
| first compile, no figures | 6,100 | 0 | **8** |
| + two figures, no cuts | 6,100 | 2 | 9 |
| + bibliography and 11 in-text citations | 5,656 | 2 | 9 |
| **after also cutting §5.8** | **5,656** | **2** | **8** |

Final state: 8 pages including the reference list, which fits on the last page rather than needing a
ninth. Verified twice: macOS metadata and by counting `/Type /Page` objects in the decompressed object
streams, and confirmed by rebuilding with the bibliography disabled — the content alone is also 8.

The estimate was wrong in the direction that mattered: the draft was already full, not short. Adding the
planned figures pushed it to nine pages, so roughly 370 words had to go before they could stay. What
went: §3.7 "Scope of the claim" (its content survives as one sentence in §3.5), §5.6 on top-of-list
methodology (three sentences folded into §5.4), and §5.7 on aggregate-versus-top-k ranking (merged into
§5.3). All three restated material already carried elsewhere.

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
