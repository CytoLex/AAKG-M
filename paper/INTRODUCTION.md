# §1 Introduction — 定稿（2026-11-06 修订）

> 现版 **744 词**，七段。论证顺序改为：**先立"公平基线"，再用它否掉门控，再用它找到专家池的价值**。
> 旧版的落点是"条件化不值钱"；新版落点是"**条件化不值钱，但专家池值钱，而后者的发现依赖前者的协议**"。

---

## 1. Introduction

Protein fitness prediction has settled into a recipe: take a sequence model, add a structure-derived
kernel, and combine the two. The combination is nearly always a fixed blend — equal weights, or
weights tuned once on the benchmark — and the evidence that it helps is a comparison against another
fixed blend. The practice has produced a steady supply of reported gains. It has also left one
question unasked. When a model fuses *per assay*, choosing different expert weights for different
assays, does the benefit come from the conditioning, or merely from having several predictors
instead of one? A fixed blend already supplies the second. What conditioning must add is a per-assay
choice that no single global choice could have made.

The obvious objection is leakage, and it points at the right baseline. A gate that sees the held-out
assay's labels would trivially beat any global blend. We therefore restrict the gate to label-free
inputs — the experts' own predictions and assay metadata, never the target — and compare it against
a baseline that is *also* label-free and *also* free to choose per assay: a constant fusion whose
weights are selected on the training assays and applied to held-out ones. That baseline has four
parameters, sees exactly the same information, and is the strongest honest competitor. Everything in
this paper is measured against it.

The gate loses. Our label-free gate, an MLP with 1,347 parameters that maps seventeen assay
statistics to three expert weights, matches the tuned constant to within 0.0002. Give it a fourth
expert and the gap widens against it: fixed weights score 0.6978, the gate 0.6932. Six further
conditioning mechanisms — per-category constants, $k$-nearest neighbours over the context, ridge
regression onto oracle weights, per-variant agreement rules, and a learned per-variant fusion trained
on 1.6 million variants — all land at or below the constant. The boundary of this failure is sharp
and reproducible; it is not a matter of tuning.

The same protocol then says what does work. The experts correlate 0.78 to 0.96 with each other: the
pool is diverse in name only. Adding one expert from a different representation raises a
fixed-weight fusion to **0.692** on the ProteinGym supervised benchmark, and averaging that expert
over eight training seeds lifts it to **0.694**, against **0.657** for Kermut, the published rank 1.
Both rungs are produced by running the official `performance_DMS_supervised_benchmarks.py` unmodified
on our score file, so they are on the leaderboard's scale; we report the single-model rung as the
equal-compute claim and the seed-averaged one as the deployed number. The newcomer is a distilled ESM-650 encoder that reads both wild-type
and mutant per-residue context, with neighbourhood pooling, a category-specific low-rank residual
(the control arm shows the gain needs category specialisation, not parameters), and seed averaging;
on its own it scores **0.645**, against **0.494** for the site-embedding expert it displaces. We therefore no longer attribute the gain to decorrelation alone:
the newcomer is both more accurate and the only expert from a different representation, and the
search silently sets the displaced expert's weight to zero. The fusion itself adds four numbers and
no model: the experts remain the same per-assay out-of-fold predictors used throughout, and the
additive-structure expert's weight is driven to zero by the search rather than by design.

Why the gate cannot buy the same improvement is itself measurable. The per-assay headroom is real —
a per-assay oracle reaches 0.6935, and 49% of that gain survives a variant-level split — but no
label-free descriptor we can compute predicts it: seventeen hand-built statistics, a 768-dimensional
visual assay embedding, and per-residue structure features all give cross-validated $R^2 \le 0$ for
the weights that would help, while the same features predict the gate's own weights at
$R^2$ = 0.52–0.67. The context is informative about what the gate does and uninformative about what
would help. Reaching the headroom costs labels instead: with $k$ labelled variants per assay the
advantage of conditioning turns positive at roughly $k = 215$ and reaches half the oracle headroom by
$k = 500$.

Our contributions are three. **First**, a controlled demonstration that learned per-assay weighting
adds nothing over a tuned constant, across seven mechanisms, four granularities and two orders of
magnitude of training data — and that the comparison which reveals this, a constant tuned on held-out
assays, is missing from the standard evaluation of this literature. **Second**, a positive method
result that follows from taking the negative one seriously: a distilled encoder expert raises the
fusion to 0.692 on a four-parameter weighting, +0.035 over the published leader and +0.037 once the
expert is averaged over its eight training seeds. **Third**, a diagnostic that separates "there is no headroom" from "there is headroom we
cannot reach", with the measurements — oracle capture, variant-level split, weight-level nulls,
context-to-weight regression, and a label-budget curve — that make the distinction checkable. We
release the frozen out-of-fold bundle and code under which every number reproduces bit-for-bit.

We are not claiming that adaptive fusion is impossible, nor that a richer context could not close the
gap. We are claiming that with label-free prediction statistics, on this benchmark, adaptive
weighting is worth less than the precision of the measurement — while expert diversity is worth more
than either, and can be bought without any learned machinery at all.

---

## 段落 → 证据映射

| ¶ | 论点 | 证据 |
|---|---|---|
| 1 | 融合对着固定混合验证 | §5.1 / `reconciled.json` |
| 2 | 公平基线 = label-free 且 per-assay | nested 常数构造 §5.2 |
| 3 | 门控输：+0.0002；四专家下 −0.0046；六机制 ≤ 常数 | §8.26 / `final4.json`、`mechanisms.json` |
| 4 | 专家池赢：单模型 **0.692**、集成 **0.694**（官方脚本），对 Kermut +0.035/+0.037；覆盖 696,311 个突变 | 官方脚本 / `submission/` |
| 5 | 为什么：headroom 真但不可测；R²≤0；k≈215 | §5.4、§8.15、§8.17、§8.21 |
| 6 | 三条贡献 | — |
| 7 | hedge | — |

## 三个不能写错的点

1. **"0.6978 vs 0.6932"** 是四专家面板上的比较（§8.26），**不是**已发布口径的 0.6876。段里必须紧跟一句说明面板差异，否则读者会以为是同一组数。
2. **两个层级不能混**：`0.692` 是主张层级（单模型、同算力），`0.694` 是部署层级（8 seed 集成）。
   两者都由官方脚本产出，都**没有**可配对的 seed 区间——"8/8 seed 为正"属于更早的宽松口径实验，不能挂到这两个数上。
3. **四个 delta 来源不同**：单模型层 `+0.0054`（对上一版四专家）、`+0.0084`（对门控）；
   部署层 `+0.0077`、`+0.0106`、`+0.0109`（对三专家常数）。不能混用。
4. **不要写"增益来自去相关而非准确率"**：新专家单独 0.645，被它替换的旧专家 0.494，两者同时变好，这个因果已被自己的数据推翻。

## 与旧版的差异

| | 旧版 | 新版 |
|---|---|---|
| 结论 | 条件化不值钱 | 条件化不值钱 + **专家池值钱** |
| 贡献 | 一条负结果 | 负结果 + **正面方法结果** + 诊断 |
| 落点 | "should be reported against tuned constants" | "expert diversity can be bought without learned machinery" |
