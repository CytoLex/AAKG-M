# Submission-day operations sheet — IJCAI 2027 AI4Science

Everything here assumes the build in `latex_ijcai/` and the assumptions recorded in
`SUBMISSION_CHECKLIST_IJCAI.md`. Work through it in order; nothing below needs the paper to be rewritten.

**State of play.** The paper is complete and verified. All three author-only decisions are resolved — the
fee is payable, a qualified reciprocal reviewer is available, and in-person attendance is confirmed. The
only thing still outstanding is the AI4Science track's own call for papers, which IJCAI has not published;
section 2 lists the five items it could change and what each would cost. Apart from those, nothing blocks a
submission.

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

The body is at **7 of 7 pages and the whole document at 9 of 9**, so any added requirement means removing an equal amount — there is no slack left at either level. In order of what costs the paper least. **Re-measured against the current build. The previous list had all five items already used, and one of them
recommended cutting a paragraph that is now load-bearing — do not use an older copy of this table.**

| cut | words | why it is the cheapest |
|---|---:|---|
| §4.4 the "reframes what building an expert means" tail | 141 | the principle is stated above it, in the figure caption, and in the contributions |
| §6 the inherited-experts limitation | 69 | the reproducibility scope is repeated in the §5.2 table caption |
| §2 the evaluation-practice paragraph | 44 | §5.2 makes the same argument with numbers |
| §7 the three-challenges list | 38 | the challenges are evident from §2 and §3 |
| §5.2 the per-category prose | 32 | the category table carries the same comparison |

They are measured word counts from the current text, not estimates. The first three together — 254 words — buy
roughly half a page without touching a claim or an interval.

**Do not cut, in this order of severity:** the §7 falsification paragraph (it is the paper's answer to "what would
change your mind" and a reviewer will look for it), the §3.2 rank-average baseline (it is the objection a reader in
this literature asks first), the oracle null in §3.3 (it is what makes +0.0051 more than selection noise), and any
interval.

## 4. The three author-only decisions — **all resolved**

Status as of this writing: in-person attendance confirmed; the fee is payable (or the paper qualifies as
primary); a qualified author is available to designate as reciprocal reviewer. The mechanics below are kept
so the commitments are on record rather than in memory.

1. **USD 100 fee — confirmed payable.** It is waived only for a *primary paper*, defined verbatim as
   "papers for which none of the authors appear as an author on any **other** submission to IJCAI 2027",
   so the waiver applies only if this is the team's sole covered submission; a second one sharing any
   author makes both payable. Since the fee is acceptable, the waiver is now an optimisation rather than a
   dependency. Excluded from the initiative and therefore harmless: Senior Researchers' Position Talks,
   Journal Track, Sister Conferences Track, Early Career Highlights, Competitions, Demos, Doctoral
   Consortium. Non-primary payment deadline: **January 18, 2027**.
2. **Reciprocal reviewer — confirmed available; designation is mandatory.** One of the paper's own
   authors must be recorded as the reciprocal reviewer by the full-paper deadline. Qualification, verbatim
   from the Reciprocal Review Policy: "at least **five full papers in total** across the following venues:
   IJCAI, AAAI, ECAI, AAMAS, KR, NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, ICCV, ECCV, UAI, AISTATS, COLT,
   ICAPS, KDD, and AIJ"; serving IJCAI 2027 as PC, SPC or Area Chair also qualifies, and for those the
   existing duties count instead of new assignments.

   **Because a qualified author exists, an exemption is not available.** An unqualified designation is a
   desk reject, and a designated reviewer who does not complete Phase 1 or Phase 2 takes every submission
   that named them down with them. Eligibility is assessed against what the submission system records at
   the deadline, so the designation cannot be settled afterwards.

   (An earlier version of this file said "three papers in KDD or related conferences" — that is KDD's
   rule, not IJCAI's.)
3. **In-person presentation** at Kyoto or Hengqin — **confirmed by the authors**. Papers not presented are
   excluded from the proceedings unless IJCAI grants prior approval for exceptional circumstances.

## 5. Final build check

```bash
cd kdd/figures && python3 make_figs_ijcai.py     # the IJCAI-scaled figures
cd ../latex_ijcai && ./build.sh
```

Expected output: `AAKG_IJCAI_draft.pdf: 9 pages (7 body + 2 references)`. Then confirm by hand:

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
