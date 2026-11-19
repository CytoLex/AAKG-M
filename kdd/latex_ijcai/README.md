# IJCAI 2027 AI4Science submission

Built against the IJCAI 2027 author kit (`ijcai27.sty`, `named.bst`, fetched from
`ijcai.org/authors_kit`), using condensed section sources in `../ijcai_sections/`.

```bash
./build.sh      # writes AAKG_IJCAI_draft.pdf
```

## Measured state

**7-page body + 1 page of references = 8 pages.** The limit is 9 (7 body + up to 2 for references,
acknowledgements, contribution statement or ethics statement), so there is a page in hand.

Verified by compiling with the bibliography disabled and counting `/Type /Page` objects in the
decompressed PDF streams: the body alone is exactly 7.

## Why this is a rewrite, not a reformat

The same research is 8 content pages under ACM's `sigconf` at 9pt and 10 pages under IJCAI's 10pt. The
IJCAI limit is 7 body pages with **no unlimited appendix** — unlike ICML, which lets material move rather
than be cut. So the paper was condensed to 3,415 words from 5,735, and from 9 tables to 5.

What survived and what did not:

| | ACM/ICML build | IJCAI build |
|---|---:|---:|
| words | 5,735 | **3,415** |
| tables | 9 | **5** |
| figures | 2 | 2 |
| body pages | 8 | **7** |

Cut: the standalone experimental-setup section (its essentials are now inside §3.1), the separate
*Generative AI Usage* section (folded into the ethics section as one paragraph, which is what IJCAI's
optional ethics statement invites), the mechanism "type" column, and the per-category and quartile tables
(their numbers are in the prose). Nothing was dropped that carries a claim; the appendix-only material of
the other builds is simply gone.

## Anonymity

The **Author's Kit** says anonymity is track-dependent: "For the main track and some of the special
tracks, submissions must be anonymous; for other special tracks they must be non-anonymous… please check
the track-specific instructions."

The AI4Science track's CFP has not been published, so this build is **anonymous**: no author block, no
institutional references, no repository URLs naming the group. If the track turns out to be
non-anonymous, adding the author block is a two-line change in `make_tex.py`.

## Format details taken from the kit

- `\documentclass{article}` with `\pdfpagewidth=8.5in`, `\pdfpageheight=11in`
- Times font, `\usepackage[small]{caption}`, `\usepackage{times}`
- **`\linenumbers` enabled** — the template keeps it on for submissions and comments it out for
  camera-ready
- `\bibliographystyle{named}` — IJCAI's author-year style, so references render as names, not numbers
- **Title in Title Case.** The kit states: "The title must be capitalized using Title Case." The earlier
  sentence-case title was a formatting violation and is fixed.
- `\tightlist` is defined locally, because pandoc emits it but the IJCAI preamble does not provide it.

## Figures are redrawn for IJCAI's column

IJCAI's column is (7.0 − 0.25)/2 = **3.375 in** and the build includes figures at 0.86 of that, 2.902 in.
The ACM/ICML figures are authored 3.4 in wide, so including them there scales by 0.85 and an 8pt label
renders at **6.8pt** — too small next to 10pt body text.

`../figures/make_figs_ijcai.py` authors them at **2.90 in**, so the scale factor is 1.00 and an 8.5pt
label renders at 8.5pt. Both figures carry the same data as the other builds; only the drawing size and
label sizes changed.

## Still unknown until the track CFP appears

| item | assumption made here |
|---|---|
| page limit for this track | 7 body + 2 references, from the main-track rule and the 2026 special tracks |
| anonymity | anonymous |
| required sections | none specific; ethics statement optional and placed at the end |
| whether extra pages can be purchased | assumed not |
| submission fee | USD 100 under the Primary Paper Initiative unless the paper is a primary submission |

All five are recorded in `../SUBMISSION_CHECKLIST_IJCAI.md`.
