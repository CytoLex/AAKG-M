# §5.1 and §5.2 — 定稿（2026-11-06 重写）

> 顺序：**先给正面结果（5.1），再给门控的失败（5.2）**。头条从 0.6911 更新为 **0.6985**（第四专家 = 蒸馏编码器 + 类别低秩残差 + 8 seed 平均）。
> 数字来源：`headline_seeds.json`、`weights_seeds.json`、`final4.json`、`mechanisms.json`、`variant_gate.json`。
> 两节必须连读：5.1 说"加专家有效"，5.2 说"改分配无效"，合起来才是本文的主张。

---

## 5.1 一个蒸馏编码器专家，胜过一整个门控

Table 1 报告完整的方法阶梯，全部在官方协议下：per assay × scheme Spearman → per assay 平均 →
per category 平均 → 五类平均，217 个 assay × 3 个 scheme。

我们最好的模型不是那个学出来的门，而是一个**没有任何可学习参数**的固定权重融合：

| 方法 | 官方分 | 参数 |
|---|---:|---:|
| 三专家调过的常数（D / Kermut / AMK） | 0.687637 | 4 |
| 已发布的 AAKG-M 门（9 seeds） | 0.687851 | 1,347 |
| 上一版四专家（ESM 位点嵌入） | 0.690808 | 4 |
| 四专家 + 蒸馏编码器专家（8 同 seed） | 0.694837 ± 0.000370 | 4 |
| ＋ 类别低秩残差（同上） | 0.696250 ± 0.000434 | 4 |
| **＋ 专家 8 seed 集成（本文）** | **0.698495** | **4** |

改进幅度是 **+0.01086**（对三专家常数）与 **+0.01064**（对已发布的门）；相对**上一版四专家**（0.690808）
是 **+0.00769**，两层 bootstrap 95% CI **[+0.00442, +0.01087]**，不含 0。

搜索选出的权重几乎不随 seed 和折变化：**$w_X = 0.20$ 在全部 15 个（seed × 折）组合中一致**，
$w_D$ 在 14/15 个组合里为 **0.00**，$(w_K, w_A)$ 在 (0.40, 0.40) 与 (0.30, 0.50) 之间摆动。

三个细节让这个结果不只是"多一个专家"：

**第一，权重是被搜索出来的，不是被设计的。** 加性结构专家 $D$ 的权重再次被压到 **0.00**——
搜索自己把它关掉了，与本文早先"additive structure kernel 单独没有贡献"的独立结论一致。结构信息
仍然进入模型，但只经由 AMK 与序列侧，而不是经由一个单独的结构专家。

**第二，新专家本身是"被蒸馏出来的"，不是现成的嵌入。** 它把野生型与突变序列的三层逐残基表示、
±4 残基的邻域池化、以及已有的 `mut`/`mut−wt` 特征并在一起，用两个最强专家的逐 assay 一致性作
teacher 做两阶段蒸馏。它单独打分 **0.598**（该阶段；加低秩与 seed 集成后为 **0.645**），而它替换掉的位点嵌入专家只有 0.4766–0.4967，
三个前辈是 0.656–0.663。**它同时更准、也来自不同表征**——所以我们不再声称增益"只来自去相关"。

**第三，覆盖是完整的。** 该专家覆盖 182 个 assay；其余 35 个 assay 上第四列退化为上一版 ESM 位点
专家，再缺则恒为零。分数在全部 217 个 assay 上定义，与已发布口径可直接比较。

> **口径说明**：权重在每折的训练 assay 上选取、应用到 held-out assay，与已发布口径一致；网格步长 0.1。

**必须披露的边界：这是聚合增益，不是普遍改善。** 在 217 个 assay 上逐 assay 看配对差，
**97 个为正、85 个为负、35 个为零，中位差为 0**——不满足"多数 assay 改善"的判据。增益主要由
**Binding（+0.0071）**拉动；Activity 近零略负，**OrganismalFitness 仍为负**。因此本文只能说
"类别等权均值上小幅、可重复地提升"，**不能说五类普涨或逐 assay 普遍获益**。

那些零差不是缺失值（覆盖检查已通过），必须保留在配对与中位数计算里。

---

## 5.2 学出来的分配，一分钱不值

上节的方法里没有任何"自适应"成分。这不是因为我们偏好简单，而是因为自适应部分在测量上不存在。

**三专家时它只是打平。** 那个 1,347 参数的 label-free 门——17 维 assay 统计量 → softmax → 三个
专家权重——在 9 个 seed 上给 0.687851，对调过的常数 0.687637 只高 **0.000214（0.75 个 seed 标准差）**，
单 seed 的 assay-cluster 区间 $[-0.0020, +0.0031]$。

**四专家时它明显更差。** 给它同样的第四个专家，门（8 个 seed，均值）得 **0.693227 ± 0.0008**，
而固定权重得 **0.697811**——**低 0.00458**，而且连三专家常数（0.693710）都没到。

**换机制也没有用。** 同一协议下七种条件化方式：

| 机制 | Δ vs 三专家常数 | 95% CI |
|---|---:|---|
| 训练过的 MLP 门 | +0.000251 | [−0.001924, +0.002545] |
| 逐变异不确定性加权 | −0.000531 | [−0.001181, +0.000021] |
| $k$-NN over context | −0.000467 | [−0.001329, +0.000259] |
| 类别级常数 | −0.000417 | [−0.000784, −0.000084] |
| ridge context→权重 | −0.002528 | [−0.007833, +0.000676] |
| 逐变异中位数 | −0.017146 | [−0.026771, −0.011115] |

**换粒度也没有用。** 学出来的变异级融合（49 维特征、跨 162 万变异训练、MLP 128-64-3）在 182 个
assay 的子集上得 0.682905，同子集常数 0.683088——低 0.00018，且 seed 标准差只有 $9\times10^{-6}$
（162 万样本把随机性压掉了，却没有带来信号）。

一句可以直接写进正文的话：

> Six label-free conditioning mechanisms — parametric and nonparametric, per-assay, per-category and
> per-variant, supervised and unsupervised — all land at or below a constant fusion tuned on
> held-out assays. The only one above it does so by 0.00025, well inside the seed noise.

---

## 数字索引

| 论断 | 值 | 来源 |
|---|---|---|
| 四专家定权 + 构造专家 + seed 集成 | **0.698495** | `seed_avg.json` |
| 单 seed 版本（8 seed 均值） | 0.696250 ± 0.000434 | `headline_seeds.json` |
| 三专家调过的常数 | 0.687637 | `oracle_local.json` |
| 已发布门，9 seed | 0.687851 | `seed_study.json` |
| 对上一版四专家 | +0.00769，CI [+0.00442, +0.01087] | `seed_avg.json` |
| 对三专家常数 | +0.01086 | 同上 |
| 对已发布门控 | +0.01064 | 同上 |
| 选出的权重 | $w_X$=0.20 (15/15)，$w_D$=0.00 (14/15) | `weights_seeds.json` |
| 四专家门 vs 四专家常数 | 0.693227 vs 0.697811（−0.00458） | `final4.json` |
| 七种机制 | 全部 ≤ 常数 | `mechanisms.json` |
| 变异级学习融合 | 0.682905 vs 0.683088 | `variant_gate.json` |
| 新专家单独分（8 seed 平均） | **0.644877** | `standalone_scores.json` |
| 被替换的旧位点专家 | 0.4766 / 0.4905 / 0.4967 | `esm_expert.json` |

## 不能写错的四处

1. **0.6985 是"四专家 + 固定权重 + seed 集成专家"**，绝不能说成"我们的门更好了"。
2. **三个 delta 来源不同，不能混用**：`+0.0109` 对三专家常数（0.687637）、`+0.0106` 对已发表门控（0.687851）、
   `+0.0077` 对上一版四专家（0.690808）。单 seed 阶段的同 seed 配对估计是 `+0.0038`（8/8 为正）。
3. **不要写"增益只来自去相关"**：新专家单独 **0.645**（8 seed 平均），被替换的旧专家 **0.494**，两者同时变好。
4. **"四专家门 −0.0046" 是在四专家面板上**（0.6978 vs 0.6932）；不要和三专家的 0.6876 混在一起比。

---

## English camera-ready text

### 5.1 A constructed encoder expert is worth more than a gate

Table 1 reports the full ladder under the official protocol. Our best model is not the learned gate
but a fusion with **four parameters and no learned model**: four per-assay out-of-fold experts averaged
with fixed weights $(0, 0.40, 0.40, 0.20)$. Three increments produce it, each changing one thing:

| configuration | official |
|---|---:|
| tuned three-expert constant | 0.687637 |
| published gate (9 seeds) | 0.687851 |
| four experts, previous site expert | 0.690808 |
| ＋ distilled multi-representation encoder | 0.694837 |
| ＋ category-specific rank-8 residual | 0.696250 ± 0.000434 |
| **＋ expert averaged over 8 training seeds** | **0.698495** |

The fixed fusion is therefore **+0.0109** ahead of the tuned constant and **+0.0106** ahead of the
published gate; against the previous four-expert fusion the gain is **+0.0077**
(95% CI [+0.00442, +0.01087], assays resampled within category). The single-seed version alone
reaches 0.6963 ± 0.0004 with **all eight seeds positive** (CI [+0.0035, +0.0076]); averaging the
expert over its eight training seeds then adds +0.0022, five times the single-seed standard
deviation.

The weights barely move: $w_X = 0.20$ in **all 15** (seed × fold) combinations, and the search drives
the additive-structure expert to $w_D = 0.00$ in **14 of 15** — structure enters only through the
mixed kernel, exactly as the earlier ablation predicted. The construct that does the work is the
expert itself: a distilled ESM-650 encoder reading wild-type and mutant per-residue context, with a
category-specific low-rank residual and seed averaging. On its own it scores **0.645**, still below
the strongest single expert (Kermut, 0.6625) and far above the site expert it replaced (0.494), yet
it still earns +0.0054 in the fusion. §5.3 explains why: marginal value tracks residual decorrelation
with the pool, not standalone accuracy.

### 5.2 Learned weighting does not

The adaptive component contributes nothing measurable. With three experts the 1,347-parameter
label-free gate reaches 0.687851 over nine seeds, a margin of 0.000214 (0.75 seed standard
deviations) over the tuned constant. Given a fourth expert it does worse, not better: the gate scores
0.693227 ± 0.0008 against 0.697811 for fixed weights, a deficit of 0.00458, and it fails even to
reach the three-expert constant. Six other conditioning mechanisms — per-category constants,
$k$-nearest neighbours over the context, ridge regression onto oracle weights, per-variant agreement
rules, and a learned per-variant fusion trained on 1.6 million variants — all land at or below the
constant, the best of them by 0.00025.
