# IJCAI 2027 AI4Science submission checklist

Sources read on 2026-11-19: the IJCAI 2027 main-track CFP, the AI4Science special-track page, and the
official author kit (`FormattingGuidelines-IJCAI-27.zip`, containing `ijcai27.sty` and `named.bst`).
The AI4Science track's **own CFP is still unpublished** — it says "will be published here soon" — so
anything below marked *assumed* is inferred from the main-track rules and from the 2026 special tracks.

## Confirmed from the 2027 pages

| requirement | status |
|---|---|
| Paper deadline **January 11, 2027**, 23:59 AoE | noted; abstract deadline for the main track is Jan 4 and is assumed to apply |
| Notification April 21, 2027; camera-ready May 21, 2027 | noted |
| **Double-blind** from the authors' perspective (main track) | **done** — no author block, no institutional strings |
| IJCAI style enforced; margins and font sizes must not be altered | **done** — `ijcai27.sty` used unmodified |
| Overlength papers rejected without review | **done** — 7 body pages, 8 total |
| Ethics statement optional, placeable in body or reference pages | **done** — §6 covers limitations and ethics |
| USD 100 submission fee under the Primary Paper Initiative, waived for primary papers | **YOU** — decide whether to pay or to submit as a sole IJCAI submission |
| Reciprocal reviewing: one qualified author must be designated | **YOU** |
| At least one author must attend in person (Kyoto or Hengqin) | **YOU** |
| No dual submission while under review — which spans every other AI/ML deadline in this window | **YOU** — this forecloses ICML and KDD for the same paper |

## Assumed until the AI4Science CFP appears

| item | assumption | risk if wrong |
|---|---|---|
| Page limit | 7 body + up to 2 for references/ethics | if it is 9 body pages we have slack; if 7 total we must cut one page |
| Anonymity | anonymous | if non-anonymous, add the author block (two lines) |
| Track-specific required sections | none | may require something the main track does not |
| Extra pages for purchase | not available | if available, this is relief, not risk |

## Format decisions taken from the kit

- Times font, `[small]` captions, `\pdfpagewidth=8.5in` / `\pdfpageheight=11in`
- **`\linenumbers` enabled**, as the kit keeps it on for submission and comments it out for camera-ready
- `\bibliographystyle{named}` — author-year references, so 14 verified entries render as names

## Before submitting

1. Re-read the AI4Science CFP when it appears; reconcile the table above.
2. Decide the fee/primary-paper question and designate the reciprocal reviewer.
3. Add the author block **only if** the track is non-anonymous.
4. Rebuild with `cd latex_ijcai && ./build.sh` and confirm 8 pages.
