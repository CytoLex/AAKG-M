# The narrative, and why it changed

## What the paper now says

The spine is a **closed loop on one quantity**, not a list of findings:

```
ceiling      an oracle bounds what any weighting rule could reach      +0.0051
reachable    per-assay fitting gets +0.0047 on substitutions
             and loses 0.0032 on indels, where assays are small
captured     partial pooling gains +0.0051 and +0.0021                  <- the fix
lever        adding one expert is worth                                +0.0122
```

Read as one sentence: **weighting has a ceiling, the ceiling is less than half of what an expert change is
worth, naive per-assay fitting cannot reach even that, and partial pooling can.**

## Why it changed

The previous spine was "allocation is not the bottleneck, the expert is". That was a falsification with no
constructive half, and after the headroom correction it was also too absolute — 42% is not nothing.

The correction itself supplied the better story. Once the headroom is measured inside one pipeline, it stops
being a number to argue about and becomes a quantity with three separate measurements around it: what is
available, what is reachable, and what a specific estimator captures. A paper that reports all three says
something a reader can act on, and it is harder to dismiss than a negative result, because the negative half
is now a design constraint rather than a verdict.

## What was rewritten, and against the launch-writing principles

| position | original | problem | replacement | reasoning |
|---|---|---|---|---|
| §1 opening | "This paper tests it, and the answer reorganises the problem." | announces a test, not a result | "asks how much that premise is worth, and answers with a measurement rather than another architecture" | states what the paper delivers — a measurement — and positions it against the field's habit of adding architectures |
| §1 claim 1 | "the allocation headroom is small enough to bound", followed by the seven mechanism results | report-like ordering: the audit comes before the finding, and "small enough to bound" undersells | "**Weighting has a ceiling, and the ceiling is reachable**", then oracle, expert, ratio, and the pooling fix | leads with the result and closes the loop; the mechanism audit becomes supporting evidence rather than the opening move |
| §1 claim 1 | (absent) | the constructive result — pooling — appeared nowhere in the introduction | one sentence: per-assay fitting gains +0.0047 and loses 0.0032, pooling gains +0.0051 and +0.0021 | a paper whose best result is missing from its introduction is hiding its own contribution |
| §1 closing | "The second claim is what changes how the field builds these models; the third is what a user can act on today; the first is what makes both measurable rather than asserted." | a table of contents in prose; tells the reader how to rank our own claims | "measure the ceiling before tuning weights, put the effort into experts, and pool when you do weight" | converts self-description into instructions the reader can use |
| contributions 1 | "A falsification of adaptive weighting for this problem, replicated on a second benchmark." | names only the negative half | "A bounded, replicated and actionable account of weighting." | same evidence, but the entry now points at all three measurements |
| abstract | opened on the benchmark and the seven mechanisms | the first two sentences were method inventory; the reader learns the result fourth | opens "We measure what that combination is worth", then the oracle/expert ratio, then the pooling fix, then the expert and the utility profile | problem → gap → idea → hardest result, and the hardest result is the loop |
| abstract | (absent) | pooling, the constructive contribution, was missing | one sentence on λ = n/(n+k) and the two gains | if it is the thing a practitioner should do differently, it belongs in the abstract |

## What the principles forbade, and what was kept

Deleted: "small enough to bound", the self-ranking closing sentence, and the framing of contribution 1 as a
falsification. None of these were claims; they were hedges about how much to care.

Kept, deliberately: **every number, including the unfavourable ones** — the indels loss of 0.0032, the
+0.00003 on the largest quartile, the 3.4x top-of-list lift on activity. The rewrite changes where those
numbers sit and what they are attached to, not whether they appear. A limitation stated as a design
constraint ("pool when you do weight") is still a limitation; one stated as an apology is not.

Also kept: the exact scope conditions. "On substitutions / on indels / on the largest quartile" is the
comparison frame the numbers need, and dropping it would be overclaiming rather than streamlining.

## The title, and why it changed

The old title, "Allocation was never the bottleneck", was written when the ratio was believed to be a
quarter. At 42% with disjoint intervals it is still defensible, but it names only the negative half — a
paper titled after what does not matter is a paper that has buried its own constructive result.

The new title names both halves of the loop:

> **The Ceiling on Adaptive Weighting in Protein Fitness Prediction, and How to Reach It**

"There is a ceiling" is the bound; "and how to reach it" is partial pooling. It leads with the measurement
the paper is about rather than with a verdict, it keeps the domain in the title where the track needs it,
and it survives being read as a claim — both halves are backed by numbers, one by an oracle and one by two
benchmarks of out-of-sample gains.

Applied to all three builds (ACM, ICML, IJCAI). The ICML running header needed a short form and got
"The Ceiling on Adaptive Weighting". Page budgets re-verified after the change: ACM 8 content pages, ICML
8-page body, IJCAI 7-page body, all unchanged.
