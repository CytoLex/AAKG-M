# Where to send this, now that KDD's next AI4S cycle is three months out

Question: are there CCF-A venues with a nearer deadline that suit this paper better? Every date below
was read from the venue's own site on 2026-11-18, not recalled.

## The dates that are still open

| venue | CCF | abstract | full paper | notification | days from today |
|---|---|---|---:|---:|---:|
| **ACL 2027** (via ARR) | A | — | **Jan 4, 2027** | TBA | **47** |
| **IJCAI-27** (Kyoto) | A | Jan 4, 2027 | **Jan 11, 2027** | Apr 21, 2027 | **54** |
| **ICML 2027** | A | Jan 14, 2027 | **Jan 22, 2027** | first-stage Feb 23, 2027 | **65** |
| KDD 2027 Cycle 2 | A | not published | expected ~Feb 2027 | — | ~90 |

Already closed, for completeness: ICLR 2027 (paper Sep 25, 2026), CVPR 2027 (submission Nov 16, 2026 —
two days ago), NeurIPS 2026, AAAI-27.

## Which of these actually fits

**ICML 2027 — best fit, and the format already matches.** The CFP states: "8 pages for the main paper,
with unlimited pages for references, the impact statement, and appendices." That is exactly the shape
this paper already has: 8 content pages plus a reference page. ICML is also the venue that routinely
publishes analysis and negative results — "we tested a class of mechanisms and none of them work, here is
what does" is a recognised ICML genre, whereas it is an awkward fit for a track whose criteria
deprioritise papers that mainly build frameworks or mainly use existing benchmarks.

**IJCAI-27 — eleven days earlier, slightly worse fit.** Same content, general-AI audience. No format
advantage over ICML, and IJCAI's review culture is less sympathetic to a result whose contribution is a
falsification.

**ACL 2027 — earliest, wrong framing.** ARR would want this framed around protein language models. The
paper is not about language modelling; the encoder is one of four experts and the argument is about
allocation. Forcing that framing would weaken it.

**KDD 2027 Cycle 2 — furthest away and, on the 2027 criteria, the weakest fit.** See
`FIT_ASSESSMENT_2027.md`: two of the four criteria deprioritise exactly our profile, and the page itself
says methodology papers belong in the Research Track.

## What switching to ICML would cost

| item | change |
|---|---|
| Template | ICML's own style file instead of ACM `acmart`; LaTeX only. The section structure survives untouched. |
| Length | 8-page main body, unlimited references and appendix — **no rewriting** |
| Anonymity | **double-blind**, so the author block goes away entirely rather than being filled in |
| AI disclosure | ICML requires an "AI Disclosure Statement", placed at the end and excluded from the page limit — a relaxation of the KDD requirement, since it need not be a numbered section |
| Required sections | no mandated *Limitations* section, though ours stays as a strength |
| Deadline | abstract Jan 14, 2027; full paper Jan 22, 2027 |

The reformatting is a day of work, not a rewrite: the 8-page structure, the seven sections, the two
figures, the nine tables and the bibliography all carry over.

## Recommendation

**ICML 2027, with KDD Cycle 2 as the fallback if ICML is rejected** — notification for ICML comes in
February, before KDD's Cycle 2 would close, so the dates are compatible if the KDD CFP is confirmed in
time.

The exception is if a domain co-author joins in the next few weeks. That changes the calculus: the
clinical or protein-engineering framing that such a co-author would bring is worth more to an AI-for-
science track than to ICML, and the AI4S criteria reward exactly the thing they would add.
