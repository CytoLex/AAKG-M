# Next-round worklist

Deadline: full paper **2027-01-11**; the separate abstract submission is **2027-01-04** and lands inside week 5.
Today is 2026-11-28, so there are six weeks and a two-day buffer. Nothing below assumes the current prose survives —
see the note on rewrites at the end.

## Decisions taken

1. **0.692 adopted.** The released per-mutant predictions are now the authority for every number in §5, under the
   benchmark's own aggregation: 0.692 against 0.657 for Kermut, +0.035. Per-scheme 0.778 / 0.671 / 0.626; category
   0.850 / 0.697 / 0.655 / 0.644 / 0.636; top-of-list 0.115 / 0.241 / 0.346 with lifts 11.5x / 4.82x / 3.46x. The
   submitted score file appears only in the limitations, as the thing that was replaced.
2. **The title changed** to *What Expert Fusion Can and Cannot Buy in Protein Fitness Prediction*.
3. **Prose rewrite** — see the scaffold document.
4. **Surpassing 0.700** — the attempt and its result are below.

## The finding that changes the goal

The second review named AutoScientists as a competitive neighbour. It is worse than a missing citation:

| method | contiguous | modulo | random | average |
|---|---:|---:|---:|---:|
| Kermut | 0.593 | 0.633 | 0.746 | 0.657 |
| AutoScientists-Kermut (arXiv:2605.28655, 2026) | 0.635 | 0.681 | 0.783 | **0.700** |
| this paper | 0.625 | 0.674 | 0.784 | 0.694 |

Verified by extracting Table 2 from their PDF: they report "improving the official average Spearman's ρ from 0.657 to
0.700, an absolute improvement of 0.043". So **the paper's best number is behind a 2026 result on the same 217 assays**,
and "beats the published leader" is no longer available as a claim.

§5.1 now says this explicitly and disclaims the ranking. That is the minimum. The strategic consequence is the one the
review already pointed to: **the contribution cannot be SOTA, so it has to be the measurement.** Everything below is
ordered by that.

## P0 — blocking, do before anything else

### P0.1 One authoritative prediction set

The reported 0.694 comes from a submitted per-assay score file; the released per-mutant file is a different run that
re-scores to 0.692, and none of the 651 units agree (mean |Δ| = 0.0083). Eight reconstruction recipes were tried
against the stored predictions; the closest, eight-seed averaging, reaches mean r 0.7072 against the submission's
0.7123, so the exact configuration is not recoverable from disk.

Two acceptable endings, and only two:

- **Find the run behind 0.694** and make the per-mutant file, the 651 unit scores, the aggregates, the top-list figures
  and every interval come from it.
- **Adopt 0.692 throughout** and say the released file is the authority.

Either is defensible. A paper whose headline cannot be re-derived from its own artifact is not, and this is a
measurement paper — its artifact is the measurement.

### P0.2 The oracle's wording

`+0.0051` is the in-sample best over a stated weight simplex, at fixed pool, with a fixed weight family. It is **not**
"any weighting" and does not bound per-variant gating, nonlinear fusion, or a different score transform. The abstract,
the Figure 1 caption and §3.3 all use the stronger phrasing today.

Rewrite as: *the empirical headroom of assay-level static reweighting over a fixed expert pool and a stated search
space.* The number keeps its value; the claim stops overreaching.

### P0.3 The oracle null does not exclude selection optimism

The random-other-assay control compares against −0.0064 while the real oracle is +0.0051, and the paper calls this
"not selection noise". It is not a matched null: it does not reproduce the step of taking a maximum over noisy local
estimates, and E[max ŵ] ≥ max E[ŵ] by Jensen.

Actions:
- Demote the null to what it shows — that local labels beat transferred weights.
- Promote the split-half result to the primary evidence, since it is the one that separates in-sample optimum from
  out-of-sample realisation.
- If a permutation test is kept, it must re-run the full search inside each permutation.

The indel result already carries the honest version of this: the oracle gap there is larger, and the unshrunk
adaptation still loses. Three quantities side by side say it better than one null does.

## P1 — the analyses that would raise the paper's ceiling

### P1.1 Replace the prediction target: oracle gain → held-out gain

This is the single highest-value item in the review, and it uses artifacts that already exist.

Today the paper predicts *where in-sample headroom exists*. That is not the same as *where adaptation pays*, and
small assays with high disagreement are exactly where the maximum is most optimistic. Re-target the leave-one-assay-out
predictor onto the held-out gain of the adaptation step, and check:

- does ambiguity plus sample size still predict it;
- does it hold on unseen UniProt entries;
- do selected assays beat random selection and size-only selection;
- same answer for plain adaptation and for shrinkage.

If it holds, the paper gains a transferable decision rule — "is fitting worth starting here" — which is a stronger
contribution than any of the current four. If it does not, the predictor stays a search-space diagnostic and the
application claim is dropped. Either outcome is publishable; only the current framing is not.

### P1.2 Separate what the last representation rung actually adds

The view ladder ends by adding wild-type layers *and* difference terms together, and the difference terms are a
deterministic function of inputs the model already has. So `+0.103` may be inductive bias rather than information.

Minimum grid, same head, same budget, reporting input dimensions and parameter counts for each row:

| representation | standalone | marginal in the same pool |
|---|---|---|
| mutant features | — | — |
| mutant + wild type | | |
| mutant + wild type + explicit difference | | |

Report both columns. A representation that helps alone but not in the pool, or the reverse, is a different claim.

### P1.3 Teacher leakage audit, and representation vs distillation

Distillation is the largest single gain (+0.114) and the teachers are themselves pool members. The question the review
raises is unavoidable: **how much of the expert's value is the representation, and how much is the teacher's
predictions being recombined?**

Needs: how teacher out-of-fold predictions were generated relative to the student's outer split; whether any teacher saw
labels from the fold it is scoring; and one comparison of representations under an identical distillation setup.

### P1.4 Capacity-matched control for the category branch, or demote it

The shared-branch control holds per-branch width at one fifth of the category branches, which does not hold total
capacity fixed. Either add a capacity-matched control and a category-identity-shuffled control, or move the branch into
the implementation section. Its measured contribution to the fusion is +0.0014, so demotion is defensible and buys
space.

### P1.5 FLIP2 with a matched head

The missing cell is the decisive one: mean-pooled ESM-2 with the *same nonlinear head* as the current representation.
Without it, 0.43 against 0.26 cannot be split between representation and head.

Also needed: which seven splits, why the others are excluded, and the compatibility rule — stated before the results,
not after. FLIP2 is now cited (Didi et al., ICML 2026 Spotlight).

### P1.6 Strong baselines in the top-list table

Top-5% recall of 24.7% currently compares against random. It should also compare against Kermut, rank averaging over
the same pool, and the tuned constant, all on the same prediction file. This is buildable from existing artifacts.

## P2 — do only if time allows

- **Competence floor, honestly.** The noise sweep never reaches a zero-contribution point, so it measures sensitivity to
  one perturbation direction, not a floor and not a frontier. Rename it, or extend it until contribution crosses zero
  and report a paired interval at each ε.
- **13-point table instead of a correlation.** The full table (expert, pool, pool performance, solo score, disagreement
  definition, held-out marginal) is more persuasive than any single r. It also fixes the units mismatch the review
  identified: disagreement is measured over 13 expert–pool rows, accuracy over 5 experts, and the two are quoted side
  by side.
- **Tie and rounding rules** for the top-1/5/10% statistics, in the paper rather than only in code: how m is rounded,
  how ties are broken, whether metrics are computed within the official fold or on concatenated OOF, and how the random
  baseline and lift are aggregated.
- **Drop the 2.8× cross-metric ratio** from the abstract and contributions. Transform Spearman as (ρ+1)/2 and it
  becomes 5.6× with nothing else changed; the ratio is not a utility comparison. Keep the same-metric comparison
  (0.1239 against 0.1146 at top-1%), which needs no rescaling.

## Fixed this round, for the record

Nine items from the review's last section were applied and verified: internal bookkeeping notes removed from the
bibliography; Qian et al. corrected to its published form (Econometrics 7(3):39, 2019) and its distinction no longer
equated with the paper's two levers; the Hsu citation corrected to what that paper does; the top-list table given its
fourth column label; "85% error" replaced by the arithmetic that gives just over half; r = +0.63 aligned to +0.786;
mutant-minus-reference used consistently; the four pool members named where the fusion is defined.

## References

Five 2026 entries were added, all verified against primary metadata, because the bibliography had nothing after 2024:

| key | why it belongs |
|---|---|
| `gao2026autoscientists` | the current best number on this panel; §5.1 now disclaims the ranking against it |
| `didi2026flip2` | FLIP2 was named four times and never cited; verified from the project site as ICML 2026 Spotlight |
| `tan2026harness` | foundation-model fitness prediction harnesses, cited with the benchmark-design sentence |
| `ma2026linear` | representation structure used for sample-efficient directed evolution, same sentence |
| `nagarsekar2026generalisation` | a signal indicating generalisation need not select models — the same failure this paper measures |

## Sequencing

| week | dates | work | gate |
|---|---|---|---|
| 1 | Nov 28 – Dec 5 | P0.1 authority, P0.2 wording, P0.3 null | every headline number re-derivable |
| 2 | Dec 5 – Dec 12 | P1.1 held-out-gain predictor | rule works on unseen UniProt or claim is dropped |
| 3 | Dec 12 – Dec 19 | P1.2 representation split, P1.3 teacher audit | increments attributable |
| 4 | Dec 19 – Dec 26 | P1.5 FLIP2 matched head, P1.6 top-list baselines | external validation real |
| **5** | **Dec 26 – Jan 2** | **write; abstract ready** | **abstract submitted by Jan 4** |
| 6 | Jan 2 – Jan 9 | P2 items, figures, page compliance | build prints OK |
| buffer | Jan 9 – Jan 11 | final checks | submit |

Two deadlines sit inside this: **Jan 4 abstract**, **Jan 11 full paper**. The abstract must be final while week 5 is
still writing, so it should be drafted at the end of week 4 from results that are already in.

## Decisions only you can make

1. **0.694 or 0.692.** Pick one authority; I cannot recover the former.
2. **Whether to claim SOTA at all.** AutoScientists has 0.700. If the paper keeps a performance table it must include
   them, and the honest framing is "competitive with, not ahead of".
3. **The title.** "Disagreement, Not Accuracy" is not supported: the competence floor shows a degraded expert
   disagrees plenty and adds nothing. Predictive complementarity is the concept the evidence carries.
4. **Whether to rewrite the prose.** The AI statement has been removed at your direction; the underlying question of
   whose sentences these are is not something I can settle by editing.

## What I would not spend time on

More gates, more shrinkage variants, more seeds for a higher leaderboard position, larger ablation matrices, or
tuning experts until the disagreement correlation looks better. The paper's problem is inference, not inventory.
