# Eight-page skeleton for KDD AI for Sciences

ACM `sigconf,review`, double column, single PDF. Eight **content** pages, then references and an
optional appendix outside the limit. The first eight pages must be self-contained.

Double-column ACM holds roughly 9000 words when there are two or three figures; assume **8500** as the
budget and let the tables eat the rest.

## Title candidates

1. **Allocation was never the bottleneck: what actually moves a protein-fitness ranker**
2. *Beyond adaptive weighting: differential representations for protein fitness prediction*
3. *What a protein engineer can act on: characterising a fitness ranker beyond aggregate Spearman*

(1) is recommended: it puts the falsification in the title, which is what distinguishes this from the
several benchmark-improvement submissions the track will receive.

## Page budget

| § | pages | words | job |
|---|---:|---:|---|
| 1 Introduction | 1.0 | 850 | the domain problem: candidate prioritisation; the field optimises allocation; our three claims |
| 2 Related work | 0.6 | 500 | protein-fitness fusion; adaptive weighting / gating; evaluation practice in the domain |
| 3 Allocation has no headroom | 1.6 | 1350 | seven mechanisms, the oracle bound, what it implies |
| 4 The expert: differential representations | 1.6 | 1350 | encoder, distillation, category low-rank residual, seed averaging, fixed-weight fusion |
| 5 What the ranker is worth | 1.6 | 1350 | official metric, per category, top-of-list utility, the regression set |
| 6 Limitations and ethical considerations | 1.0 | 850 | **mandated section**; see `LIMITATIONS_ETHICS.md` |
| 7 Discussion and conclusion | 0.4 | 350 | what changes in practice; what we would measure next |
| References + appendix | — | — | outside the 8 |

Two figures and three tables. That is the limit a data-mining reviewer will tolerate on eight pages.

## Section-by-section

### §1 Introduction (850 w)

Open on the practice, not the benchmark: an engineering campaign has a library and can assay tens of
candidates. Everything upstream of the assay is a ranking problem. Then the observation that the
field optimises the *mixture* of predictors — gates, context networks, uncertainty weighting — and the
question we ask: if the mixture were the lever, a per-assay oracle would beat a fixed blend by a
large margin. It does not.

Three claims, in order:
1. **Allocation is exhausted.** Seven adaptive mechanisms tie a tuned constant; the per-assay oracle
   sits below the fixed blend once a stronger expert is added.
2. **The expert is the lever.** Replacing one expert moves the official metric by +0.0056 on the
   single model and +0.0078 with seed averaging, against 0.694 vs 0.657 for the published leader.
3. **The ranker is useful in a specific, bounded way.** Top 5% of the ranking recovers 24.7% of the
   true top 5% (4.96x random); on the largest assay quartile the method is at parity with its
   predecessor.

Contribution list, four items, each one sentence. End with the reproducibility fact: published
per-mutant scores for 696,311 mutants, two commands to regenerate every number.

**Figure 1**: the allocation-versus-expert axis — oracle bound, fixed blend, gate, and the expert swap
on one number line. This is the paper's whole argument in one picture.

### §2 Related work (500 w)

Three paragraphs, 170 words each.
- Protein fitness: zero-shot predictors, supervised DMS-trained models, the fusion line.
- Adaptive weighting outside this domain: mixture-of-experts, gating, meta-learning; what the negative
  result says to that literature.
- Evaluation practice: aggregate Spearman versus what practitioners need; link to our top-k analysis.

### §3 Allocation has no headroom (1350 w)

- The protocol: 217 assays, 651 assay-by-split units, official aggregation.
- Seven mechanisms and their measured effect against a tuned constant (one table).
- The oracle bound: 0.6935 against 0.6908 for the fixed blend — **+0.0027 of total allocation
  headroom**, against +0.0077 for the expert swap in the same protocol. This inequality is the
  load-bearing result; state it as a comparison of magnitudes, not as "the oracle is below X".
- Why it happens: the tuned optimum already puts weight 0.05 on the additive-structure expert, and
  deleting that expert costs nothing.
- What it implies for anyone building a gating layer on this problem.

**Table 1**: the seven mechanisms, their delta against the tuned constant, seeds positive.

### §4 The expert (1350 w)

- The differential representation: reference-minus-mutant features over a ±4 neighbourhood, three
  ESM layers, plus neighbourhood-mean pooling.
- Distillation from the agreement of the two strongest experts.
- Category-specific rank-8 low-rank residual on the output.
- Seed averaging.
- Fixed four weights, selected per fold; `w_D` collapses to 0.00 in 14 of 15 seed-by-fold cells.

**Table 2**: the ladder under the official metric — 0.6855 previous four-expert, 0.6911 single model,
0.694 seed-averaged.

### §5 What the ranker is worth (1350 w)

- Official metric validation: recomputing Kermut reproduces the published per-assay table on 217/217
  assays, mean absolute difference 0.0.
- Per-category agreement: Stability 0.851, Activity 0.642.
- **Top-of-list utility**: 11.8x at 1%, 4.96x at 5%, 3.50x at 10%; Stability 7.7x versus Activity 3.4x.
- The regression set: 87 of 217 assays regress; Expression is the only category negative on average.
- Assay size: largest quartile gains +0.00003.

**Figure 2**: top-k lift by category — the actionable half of the result.
**Table 3**: the regression breakdown by category and by size quartile.

### §6 Limitations and ethical considerations (850 w)

Mandated. Drafted in `LIMITATIONS_ETHICS.md`. Six limitations, four ethical points, no hedging
language — reviewers reward specificity here and punish vagueness.

### §7 Discussion and conclusion (350 w)

What a practitioner should do differently (order stability candidates with more confidence than
activity ones; expect nothing on large assays). What we would measure next (a prospective wet-lab
batch, which is the only way to test whether top-k lift becomes hit-rate lift). One-sentence close on
the allocation result.

## Measured state

All seven sections are drafted. Word counts as written:

| § | words | target | file |
|---|---:|---:|---|
| 1 Introduction | 678 | 850 | `SECTION_1_INTRO.md` |
| 2 Related work | 386 | 500 | `SECTION_2_7_REST.md` |
| 3 Allocation | 935 | 1350 | `SECTION_3_ALLOCATION.md` |
| 4 The expert | 919 | 1350 | `SECTION_4_EXPERT.md` |
| 5 Utility | 1039 | 1350 | `SECTION_5_UTILITY.md` |
| 6 Limitations & ethics | 683 | 850 | `LIMITATIONS_ETHICS.md` |
| 7 Discussion | 311 | 350 | `SECTION_2_7_REST.md` |
| **total** | **4951** | 6600 | |

My 8,500-word budget was a guess. At ACM sigconf density — roughly 1,200 words per full page of pure
text — 4,951 words plus two figures, three tables and a references section lands at about **7 pages**,
not 8. The gap is roughly one page.

**Do not pad.** One page of genuine content is available and should be spent on a dedicated
*Experimental setup* subsection (protocol, splits, baselines, the exact aggregation chain, and the
reproduction commands), which §3.1 currently compresses into a paragraph. Everything else is at its
natural length, and the honest move is to typeset and measure rather than to invent material.

## Writing constraints

- No `state-of-the-art`, no `outperforms`, no `significantly`.
- Every claimed gain carries its protocol.
- Every limitation appears in §6, not only as a clause elsewhere.
- The word "we" is fine — the track is single-blind.
