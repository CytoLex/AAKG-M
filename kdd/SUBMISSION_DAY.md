# Submission-day operations sheet — IJCAI 2027 AI4Science

Everything here assumes the build in `latex_ijcai/` and the assumptions recorded in
`SUBMISSION_CHECKLIST_IJCAI.md`. Work through it in order; nothing below needs the paper to be rewritten.

## 1. Confirm the two dates

| | |
|---|---|
| Full paper + author information | **January 11, 2027**, 23:59 AoE |
| Abstract (main-track date, assumed to apply) | January 4, 2027 |
| Notification | April 21, 2027 |

The AI4Science track page lists the full-paper deadline itself; the abstract date is the main-track one and
is an assumption until the track CFP appears.

## 2. Read the track CFP when it appears

Reconcile five items, all recorded in the checklist: page limit, anonymity, required sections,
purchasable pages, and the fee. If the track turns out to be **non-anonymous**, add the author block:

```python
# latex_ijcai/make_tex.py, replace the empty \author{}
\author{Name One\and Name Two\\ Affiliation}
```

That is the only edit needed; nothing else in the document identifies the authors.

## 3. If a new required section appears, here is where to cut

The body is at **7 of 7 pages**, so any added requirement means removing an equal amount. In order of what
costs the paper least:

| cut | words | why it is the cheapest |
|---|---:|---|
| §3.5 Compute and reproduction paragraph | 111 | the numbers are all in the artifact |
| §7 "What would falsify us" paragraph | 47 | good faith, not load-bearing |
| §6 "Bias and domain shift" merged into Limitations | 46 | overlap |
| §3.5 Statistics paragraph | 44 | conventional, recoverable from the code |
| §4.4 the ESM-C sentence | 24 | second-order ablation |

Those are measured word counts, not estimates. The first three together — 204 words — buy about a third
of a page without touching a claim; all five buy roughly half a page.

## 4. The three decisions only the authors can make

1. **USD 100 fee**, waived only if no author appears on another IJCAI 2027 submission in any track covered
   by the Primary Paper Initiative.
2. **Reciprocal reviewer**: designate one author who qualifies — the 2027 main-track wording is "at least
   three papers in KDD or other related conferences". Failing to comply, or a designated reviewer not
   doing the work, is grounds for rejection.
3. **In-person presentation** at Kyoto or Hengqin; papers not presented are excluded from the proceedings
   unless prior approval is granted.

## 5. Final build check

```bash
cd kdd/figures && python3 make_figs_ijcai.py     # the IJCAI-scaled figures
cd ../latex_ijcai && ./build.sh
```

Expected output: `AAKG_IJCAI_draft.pdf: 7 pages`. Then confirm by hand:

- [ ] body ends by page 7, references within 9
- [ ] no author names, affiliations, acknowledgements, or repository URLs anywhere in the PDF
- [ ] `/BaseFont` entries show a Times family, not Latin Modern
- [ ] both figures present
- [ ] title in Title Case
- [ ] line numbers on
- [ ] references render author-year (`named` style), not numeric

## 6. What is frozen and what is not

**Frozen**: the analysis, every number, the claims, the figures. Nothing in this package depends on the
missing CFP — only the five assumptions in step 2 do.

**Not frozen**: the paragraphs listed in the step-3 cut table, the author block, and the closing
availability sentence in §6 if the track CFP asks for different wording.
