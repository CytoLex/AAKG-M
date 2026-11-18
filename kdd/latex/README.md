# LaTeX build

`paper.tex` is generated from the markdown sources in the parent directory, then compiled with the ACM
`acmart` class (`sigconf,review,nonacm`). Run `./build.sh` to rebuild; tectonic fetches `acmart` from
the TeX bundle on first run, so no local TeX installation is needed.

## Measured state

**8 pages**, compiled on 2026-11-18, with **nine tables and no figures**.

That number carries a warning worth reading before anyone touches the layout. The skeleton planned two
figures; the draft as it stands fills all eight content pages with text and tables alone. Adding the two
figures would push it to roughly nine and a half pages, so the revision has to cut **600–800 words**
before those figures can go in. The obvious candidates are §3.6 and §5.6, which restate material that
§3.3 and §5.4 already carry.

Overfull boxes: 104 warnings, almost all under 10pt, from pandoc's literal conversion of the markdown
tables and from long repository URLs. They are cosmetic and should be cleaned during the layout pass,
not before the content is settled.

## What is not in this build

- **Figures.** None. The two planned figures — the allocation-versus-expert number line (§3), and
  top-of-list lift by category (§5) — are specified in `../SKELETON_8P.md` but not drawn. Both are
  single-axis plots that need no new computation.
- **Author block.** Placeholders. The track is single-blind, so real names and affiliations go here
  before submission, and the author list has to be final at the deadline.
- **References.** The bibliography is empty; `../SECTION_2_7_REST.md` names the literatures but does not
  cite specific works. This is the largest remaining writing task after the figures.
- **The mandated section title.** Rendered as "Limitations and ethical considerations". The KDD 2026 CFP
  used exactly "Limitations and Ethical Considerations" — capitalisation should be matched verbatim to
  whatever the 2027 CFP says, since required-section wording is a desk-reject criterion.

## Reproducing the page count

```bash
./build.sh
mdls -name kMDItemNumberOfPages AAKG_KDD_draft.pdf
```
