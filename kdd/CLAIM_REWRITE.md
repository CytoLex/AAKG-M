# Claim rewrite — diagnosis and replacements

Applying the paper-launch-writing principles: organise around the strongest evidenced advantage, delete
self-undermining phrasing, state each result with its comparison condition, and turn limitations into
operating range rather than apology. Every number is preserved; only the framing changed.

**Organising claim.** The paper's strongest asset is not the 0.694 but the *inequality*: allocation
headroom +0.0027 against expert headroom +0.0077. That is a bound, and bounds are what let a paper say
something about a field rather than about one model. Everything else is arranged to make that bound
usable: the expert construction shows where the headroom actually is, and the utility analysis shows what
the resulting ranker is worth in the units a laboratory spends money in.

## Diagnosis

| position | original | problem | replacement | reasoning |
|---|---|---|---|---|
| §1, third claim | "The aggregate 0.694 conceals a 0.21 spread … and it conceals where the method is useful." | Two sentences built on "conceals": the paper describing its own headline as a veil. | "an aggregate score is not a deployment specification, and we report the one that is" | States the contribution positively and claims the deployment-facing analysis as the deliverable, which is what it is. |
| §1, third claim | "On the largest assay quartile the improvement … is +0.00003: parity, with a 50% regression rate." | Leads the reader's first encounter with the method into its weakest cell. | "The advantage also has a size regime — largest on small assays, and at parity … on the largest quartile." | Same fact, now a measurable operating range with the direction stated, so a reader learns where the gain lives. |
| §1, closing | "We think the third point is the one that matters for practice…" | "We think" hedges the paper's own editorial judgement; the three claims are not tied to distinct jobs. | "The second claim is what changes how the field builds these models; the third is what a user can act on today; the first is what makes both measurable rather than asserted." | Gives each claim a job and asserts the judgement instead of apologising for having one. |
| Contributions 3 | "…the part that keeps the headline honest." | The contribution list auditing the paper's honesty — defensive by construction. | "It converts one aggregate number into the two facts a campaign needs: how much of the top of the list to trust, and for which property." | Names the two deliverables a reader can actually take away. |
| §5.1 | "The claim is a fusion claim and we state it plainly… not what a new standalone model achieves." | Pre-emptive defence against an objection that the following sentence already settles. | "Kermut is one of the four experts, so this is a fusion result and we report it as such… The equal-compute comparison is the single-model rung above … which still leads Kermut by 0.034." | Same disclosure, but stated once as a condition and immediately paired with the stricter comparison it implies, including its margin. |
| §5.2 | "Every category improves, which is the least interesting part." | Dismisses our own positive result as uninteresting. | "Every category improves, and the spread is the part that matters downstream…" | Keeps the fact, redirects attention to what changes a decision. |
| §5.3 | "This is the sharpest honest limitation: …" | Self-flagellation; the reader is told how to feel before seeing the number's use. | "The size regime is therefore part of the method's specification rather than a footnote … it tells a reader which assays to expect an improvement on." | Scope condition with operational meaning; the negative control about the baseline is retained verbatim. |
| §3.2 | "It does not say the gate is broken: …" | Opens the key comparison by denying a claim nobody made. | "The gate itself does what its designers would want — … — which locates the problem in the objective rather than in the optimisation." | Converts the same evidence into a positive diagnosis, which is the stronger reading. |
| §6 opening | "The measurements bound this method more narrowly than the headline suggests" | The limitations section apologising before listing anything. | "The method's operating range is specific, and §5.3 measures it" | Scope, with a pointer to where it is measured. |
| §2 | "which is why §5.1 verifies the one we use rather than trusting it" | "Rather than trusting" implies the benchmark would otherwise be taken on faith. | "and §5.1 therefore verifies the one we use end to end before reporting any comparison on it" | States the action taken, not the suspicion avoided. |

## What was deliberately kept

- **Every number**, including the ones that are unflattering: 87 of 217 regressing, +0.00003 on the
  largest quartile, 3.4x top-of-list lift on activity. The rewrite changes where and how they are framed,
  not whether they appear.
- **The negative control** on the quartile effect ("since the baseline has more data there too"), because
  it is a real control and removing it would overstate the explanation.
- **The fusion disclosure** that Kermut is one of the experts, because concealing it would be a factual
  failure rather than a rhetorical one.
- The limitations section itself, which a track may require and which reviewers read for specificity.

## Open: the fourth claim the user asked for

The user asked for a benchmark addition as well as this rewrite. That is a separate, compute-bearing
change and is not in this file; see the plan in the conversation and the data reconnaissance recorded
with it.
