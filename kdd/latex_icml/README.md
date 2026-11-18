# ICML 2027 variant

Same research, retargeted to ICML's template. `make_tex.py` assembles the markdown sections in the parent
directory; `build.sh` compiles with the official `icml2027` style, which is in this directory along with
`icml2027.bst` and the ancillary packages.

```bash
./build.sh     # writes AAKG_ICML_draft.pdf
```

## Measured state

**8-page main body**, plus 4 pages of appendix and references — 12 total. ICML's CFP: "8 pages for the
main paper, with unlimited pages for references, the impact statement, and appendices", so this is
compliant with room to spare.

Verified by compiling the main body alone, with the appendix cut at `\appendix` and the bibliography
disabled: that build is exactly 8 pages.

## The thing I got wrong first

I told the user the switch would be a formatting exercise. It is not, and the measurement says so: the
same 5,735-word draft that fits 8 content pages in ACM's `sigconf` (9pt) runs to **9 pages of main body
and 12 total** under ICML (10pt). The typographic density differs by about 22%, so a same-length paper
does not carry over.

What made it work was ICML's unlimited appendix, which lets material move rather than be deleted:

| moved out of the main body | size |
|---|---|
| §3.1 Experimental setup | 561 words |
| §7.1 What this contributes to protein engineering | 436 words |
| five supporting tables (representation ladder, configuration ladder, control arm, per-category, quartile) | ~1.5 pages |

Nothing was cut. The main body keeps the argument and its four central tables; the appendix holds the
protocol detail and the supporting evidence, and the paper is self-contained for a reader who stops at
page 8.

## Differences from the ACM/KDD build

| | ACM (KDD AI4S) | ICML |
|---|---|---|
| class | `acmart` `sigconf,review,nonacm` | `article` + `icml2027` |
| anonymity | single-blind, author block required | **double-blind**, author block auto-removed |
| required sections | *Limitations and Ethical Considerations* **and** *Generative AI Usage*, both numbered | **none required** |
| AI disclosure | a numbered section (§6.1) | a non-numbered statement at the end, outside the page limit |
| length | 8 content pages + refs | 8-page main body + unlimited appendix |

The Limitations and Generative AI sections are kept in the ICML build. They are not required there, but
they cost nothing now that the supporting material has moved, and reviewers reward them.

## Not done

- **The abstract deadline is 2027-01-14 and the paper deadline 2027-01-22.** Nothing here is submitted.
- The author block in `make_tex.py` is an anonymous placeholder; the style removes it unless `[accepted]`
  is passed, so no edit is needed before submission — only after acceptance.
- Figure fonts and the ~100 overfull boxes from the pandoc conversion are unchanged from the ACM build.
