# DRAFT_SKELETON — AAKG-M, CVPR 2027 主会（8 页双栏）

> 这份文件只回答一个问题：**正文每一段写什么、用哪个数、引哪张图**。所有数字都来自 `CLAIM_BRIEF.md`（已逐位复现，见 §8.8–§8.10），不再二次计算。
> 目标：8 页正文 + 参考文献。论文的卖点是**否证**，不是 SOTA——任何一句把它写成"我们提出了更好的融合方法"都会让审稿人用 tuned constant 打死它。

---

## 0. 一句话与标题

**Thesis（唯一一句）**：在官方 assay-held-out 协议下，一个只用预测值和 metadata、不看标签的 assay 条件化门控，能稳定赢过**固定**专家混合，但赢不过一个**在 held-out assay 上调过的常数**；把这条差距拆开，可以量化"条件化到底值多少"，并证明瓶颈是 context 与目标权重之间的表示失配，而不是优化。

**标题候选**
1. *Conditional Gating for Protein Fitness Prediction: Stable, Informative, and Worth 0.03%*（推荐：数字直接进标题，审稿人第一眼就知道这不是 SOTA 论文）
2. *What Assay-Conditional Gating Actually Buys: A Falsification Study on 217 ProteinGym Assays*
3. *Assay-Adaptive Kernel Gating for Protein Fitness Prediction*（最保守，但容易被认为是普通方法论文，不推荐）

> **2026-11-08 叙事已改写**：方法从"三专家 + 门控"变成"**四专家 + 四个常数，无门控**"（§8.53）。头条从 0.6879（打平）变成 **0.6963 ± 0.0004（单模型，主张层级）/ 0.6985（seed 集成，部署层级）**。`FINAL_ABSTRACT.md` 与 `INTRODUCTION.md` 已按新结果重写；`SECTION_5_1_5_2.md` 与 `SECTION_5_3_5_4.md` 已重写（新 §5.1 正面结果、§5.2 门控失败、§5.3 去相关与准确率的边界、§5.4 诊断），每份末尾附英文 camera-ready 段落。

**不要在 abstract 里写**：`state-of-the-art`、`outperforms`、`significantly better`、任何 "we improve" 的动词。

---

## 1. 页预算

| 节 | 页 | 字数 | 核心任务 |
|---|---:|---:|---|
| 1 Introduction | 1.0 | 700 | 把"结构先验总该加"当作被检验的默认假设 |
| 2 Related work | 0.6 | 400 | 只写三块：protein fitness 的融合、meta-learning/gating、负结果与 baseline 规范 |
| 3 Method | 1.4 | 950 | 三专家 + 17 维 context + 1,347 参数的门，符号干净 |
| 4 Experimental setup | 0.8 | 550 | 协议、指标、五个基线、复现性声明 |
| 5 Results | 2.4 | 1600 | 5.1 赢固定混合 / 5.2 输给调过的常数 / 5.3 换机制也不行 / 5.4 为什么 |
| 6 Analysis & Discussion | 1.0 | 650 | 表示失配 vs 优化失败；对领域的建议 |
| 7 Limitations & Conclusion | 0.4 | 250 | 单一 benchmark、ProteinGym 的 assay 结构 |
| References | 1.4 | — | — |

**Figure/Table 预算**：4 图 + 2 表。其余（fig2/3/4/6/8/9）进附录。这条要早定，CVPR 审稿人对"图太多"的容忍度很低。

---

## 2. 逐节骨架

### §1 Introduction（英文成稿见 `INTRODUCTION.md`，674 词 6 段）

1. **默认假设**：protein fitness 模型越来越多地把结构核拼进序列模型，DMS  benchmark 上"加了结构就好"几乎是共识。但没人问：**这个增益是不是只是把两个预测器平均了一下**？
2. **本文要检验的东西**：如果条件化（per-assay 选权重）真的有用，它必须赢过**在 held-out assay 上调过的常数**——这是最公平的对照，因为它和门一样不看标签。
3. **结论提前给**：赢了固定混合（+0.0047，16σ），**没赢**调过的常数（+0.0002，0.75σ）。然后把差距拆成可量化的部分：oracle 0.6935，捕获 3.6%，其中 49% 经得起 variant 级切分。
4. **贡献列表**（3 条，克制）：
   - 一个 label-free 的 assay 条件化门控，以及在官方协议下的完整负结果；
   - 一个可复用的**三层否证**流程（variant 级 split-half → 权重零模型 → context→权重回归），任何 conditional gating 方法都该做；
   - 逐位可复现的 OOF bundle 与全部脚本（56 个 run 重跑 max|Δ| = 0）。

**引图**：Figure 1（概念图 + 基线阶梯）。

### §2 Related work（3 段，每段 ≤140 词）

1. **Protein fitness 与结构先验**：ProteinGym、序列模型、结构核（含 AMK 的来源）。落点：结构收益通常只在"加进去"的方向被报告。
2. **Conditional / meta 融合**：mixture-of-experts、per-task gating、meta-learning。落点：这些工作几乎都用固定混合或 in-domain 调参做基线。
3. **Baseline 规范与负结果**：tuned-constant 纪律、seed 研究、可复现性。落点：这正是本文的方法论立场。

**不写**：不要把 gating 文献列成清单；每一段最后一句必须落回本文。

### §3 Method（4 小节）

- **3.1 三个冻结专家**：D（additive structure kernel）、Kermut（sequence kernel）、AMK（assay-adaptive mixed structure kernel）。明确：**三者都不训练**，全部是 OOF 预测。
- **3.2 17 维 assay context**：12 数值 + 5 类别 one-hot，逐条列出（`log_n_z, D_std_z, K_std_z, A_std_z, D_K_corr_z, D_A_corr_z, K_A_corr_z, D_mean_z, K_mean_z, A_mean_z, seq_len_z, dms_z` + `cat_*`）。**必须写清 seq_len/dms 来自 metadata 而非标签**（这是 C1，也是审稿人第一个问题）。
- **3.3 门**：softmax over 3 logits，MLP-64，1,347 参数，**训练目标 = assay-balanced MSE on OOF**，5 折 assay-held-out。
- **3.4 部署：权重在 seed 上平均**：训练 9 个 seed，部署时用它们**权重**的平均（不是预测的平均）。全预算下 0.687937 → 0.688189；已发布 8 个 run 上为 0.687888。这是方差缩减而非新机制，但它是唯一稳定为正、且不需要额外训练的改动——写进方法，并在 Table 1 单列一行。
- **3.5 一个可选的简化**：`w_D` 钉死在调参最优点 0.05，门只在 K/A 间分配。Δ = −0.0001（95% CI [−0.0004, +0.0002]），**无成本但不提升**。正文一句话 + 附录表即可，不要包装成贡献。
- **3.6 为什么这是一个弱模型（有意为之）**：1,347 参数、无标签、只看预测统计量——如果连这个都能赚到，说明条件化本身有价值；赚不到，说明问题不在容量。

**引图**：Figure 1a（架构）。

### §4 Experimental setup

- 数据：ProteinGym 217 assays / 651 assay×scheme units / 5 categories（OrganismalFitness 77, Stability 66, Activity 43, Expression 18, Binding 13）。
- 指标：per assay×scheme Spearman → per assay 平均 → per category 平均 → 5 类平均。**必须写出这个三层聚合**，否则数字对不上。
- 三个 scheme：`fold_random_5`、`fold_modulo_5`、`fold_contiguous_5`；fold 分配 = 类别内洗牌后 `i % 5`。
- **六个基线**（Table 1）：raw D+K 0.683193、z-space D+K 0.681978、K+AMK 0.687322、门自己的平均常数 0.687585、**网格调参的常数 0.687637**、AAKG-L 0.687533。前两者是同一定义的两个空间，必须在表注里说清。
- 不确定性：两层 bootstrap（assay 在类别内 × seed），B=10,000；并说明**宽度由 assay 主导，不是 seed**（这是 §8.7 的发现，写在这里可以挡掉"你 seed 太少"的质疑）。
- 复现性一句话：8×H100 重跑 56 个 run，**40 对同 seed 配对 max|Δ| = 0.0e+00**。

**引表**：Table 1（基线阶梯）。**引图**：Figure 4（seed 噪声，放正文或附录看版面）。

> 5.1 与 5.2 的英文成稿见 `SECTION_5_1_5_2.md`；5.3 与 5.4 见 `SECTION_5_3_5_4.md`。两节必须连读——**先给 16σ 的余量，下一段就收回**，顺序不能换。

### §5 Results（四小节，全文的重心）

#### 5.1 赢固定混合（Figure 1b / Table 1）
- 0.687851 vs **raw** D+K 0.683193 → **+0.004658 = 16× seed sd**。
- 同空间对照：z-space D+K 0.681978 → **+0.005873**。
- **写法**：把 raw 的 0.683193 当头条（对手更强、更保守），在表注里给 z-space 一行并说明空间差异。**不要**只报 z-space 那个更大的数。

#### 5.2 输给调过的常数（Table 1 / Figure 4）
- nested-tuned constant **0.687637**：用 AAKG-M 自己的 5 折划分，在每折训练 assay 上从 231 个单纯形权重里选。
- **五个折独立选出同一组权重 (0.05, 0.45, 0.50)** → nested = oracle，基线极稳。
- Δ = **+0.000214 = 0.75× seed sd**，单 seed CI [−0.0020, +0.0031]。
- **写法**：不要写 "is zero"，写 **"not distinguishable from zero"**；也不要写 "significantly better than fixed blends" 之后又淡化后者——两句要放同一段，让读者看到完整阶梯。

#### 5.3 不是我们这个门的问题（Fig. 5 / Table 2）
七种机制、同一协议：训练过的 MLP 门 +0.00025（CI 跨 0），另外六种全部 ≤ 常数，其中类别级和不确定性加权**显著更差**。一句话：**换机制不解决问题**。

#### 5.4 为什么（三个否证，Figure 5 + Figure 7）
1. **headroom 是稳定的，不是噪声**：assay 级 oracle 0.693544，headroom **0.0057**（= 0.693544 − 0.687851），捕获 3.6%（权重去噪后 4.3%）。**variant 级 split-half**：在 A 上选的最优权重拿到没见过的 B 上仍领先常数 **+0.0041**，是就地增益（+0.0083）的 **49%**。→ 不是 oracle 在拟合自己的噪声。
2. **但 context 里没有这个映射**：同一套 17 维 context，预测**门自己**的权重 R² = 0.52 / 0.43 / 0.67；预测**oracle** 权重 R² = **−0.13 / −0.10 / 0.08**。用 ridge 直接回归 oracle 权重只得 0.686030，**低于常数**。→ 表示失配。
3. **门本身不退化**：跨 seed split-half 权重相关 r = 0.92 / 0.96 / 0.97，ICC 0.75 / 0.84 / 0.88；类别内打乱权重掉 **0.0017**（500 次置换，sd 0.00075）。→ 它学到一个稳定的函数，只是方向不对。

**合起来的一句**：*稳定、有信息、worth 0.00025——这是表示失败，不是优化失败。*

**引图**：Figure 5（阶梯 + split-half）、Figure 7（两个 R²）。

### §6 Analysis & Discussion

- **6.1 结构到底从哪进来**：nested 最优 `w_D = 0.05`，门平均给 D 0.142（系统性高估 ~3×）；删掉 D 专家 Δ = −0.0001（跨 0）。→ 结构收益在 **AMK** 里，不在 additive kernel。这是对"结构先验总该加"的直接反驳。
- **6.2 为什么 context 不够**（可写的推测，标为 hypothesis）：17 维统计量描述的是"专家之间像不像"，而 oracle 权重取决于"哪个专家在这个 assay 的**标签分布**上更好"——后者需要标签信息，label-free 原理上拿不到。这句话是本文最值得被引用的一句。
- **6.3 给领域的建议**：conditional gating 的论文应报告 ① tuned constant（held-out 上调）、② oracle 上界与捕获率、③ 权重零模型、④ 至少一个**别家机制**的复现。**四者缺一，结论就可能反过来。**

**引图**：Figure 6（权重零模型）。

### §7 Limitations & Conclusion

- 单一 benchmark（ProteinGym）；assay 结构固定为 217×3；oracle 是 assay 级而非 mutation 级（后者不可复现，已弃用）；"context 不含该映射"只对**给定的 17 维**成立，不是对所有可能的 metadata 成立。
- 结论段回到 thesis：**能赢固定混合，赢不了调过的常数；差距稳定、可量化、且不在我们能算的 context 里。**

---

## 3. 图表清单（正文只留这些）

| 编号 | 内容 | 源文件 | 位置 |
|---|---|---|---|
| Fig. 1 | (a) 架构 (b) 基线阶梯：固定混合 → 调过常数 → 门 → oracle | `fig1_conditional_use.pdf`, `fig1b_baseline_ladder.pdf` | §1 / §5.1 |
| Fig. 2 | headroom 阶梯与 3.6% 捕获 + split-half 迁移 | `fig5_headroom.pdf` | §5.3 |
| Fig. 3 | 同一 context 预测门（R² 0.52–0.67）vs 预测 oracle（−0.13–0.08） | `fig7_context_recovers.pdf` | §5.3 |
| Fig. 4 | 权重零模型：split-half 散点 + 四种权重方案 | `fig6_weight_null.pdf` | §6.2 |
| Table 1 | 全部基线与 Δ（含 CI、seed sd 倍数） | 手写 | §4–§5 |
| Fig. 5 | **机制谱系**：七种条件化方式的分数与 Δ | `fig11_mechanisms.pdf` | §5.3 |
| Table 2 | 七种机制的分值与 95% CI（Fig. 5 的数字表） | `mechanisms.json` | §5.3 |
| Table 3 | 消融：drop D / drop D+stats / context none/cat-only/shuffle，8 seeds + 两层 CI | `verify_matrix.json` | §6.1 |

**进附录**：fig2（τ/α 曲线）、fig3（结构消融）、fig4（seed 噪声）、fig8（#3 四臂）、fig9（森林图）、fig10（粒度谱系）。

---

## 4. Appendix 映射（brief → 附录字母）

| 附录 | 内容 | 来源 |
|---|---|---|
| A | 17 维 context 的完整定义与来源，label-free 论证 | §3.2 / C1 |
| B | 17 维中最关键的 2 维需契约，故离线只能重建 15 维的说明 | §8 备注 |
| C | 全部消融的逐 seed 表与两层 bootstrap | §8.7 / §8.8 |
| D | 温度与 α 扫描（负结果） | §8.2 / fig2 |
| E | seed 研究：9 个 seed、sd 0.000287、已发布 3 seed 的偶然性 | §8.3 / fig4 |
| F | 权重零模型与 ICC | §8.5 / fig6 |
| G | context→权重的 ridge/RF 细节 | §8.6 / fig7 |
| H | 复现性：56 run、40 对配对、0.0e+00 | §8.8 |
| I | 基线口径：raw vs z-space 的 D+K，per_unit 为 seed 1 | §8.10 / §3 注 |

---

## 5. 交稿前必须核对的 6 个数

1. 头条 **0.687851 ± 0.000287**（9 seeds），不是 0.6879937（seed 20261029 单个），也不是 0.688046（seed 1）。
2. 对 D+K **+0.004658（raw）/ +0.005873（z）**，两者都要在表注出现。
3. 对 nested 常数 **+0.000214 = 0.75σ**，措辞 "not distinguishable from zero"。
4. 捕获率 **3.6%**（去噪 4.3%），headroom **0.0057**，split-half 存活 **+0.0041（49%）**。
5. 打乱权重的代价 **0.0017**（不是 0.0021——那是旧的一次性置换）。
6. 消融 P 值：shuffle 0.004、cat-only 0.009、none 0.257、drop-D 0.417。

## 6. 禁止表述清单

- ❌ "outperforms a tuned constant" / "significantly better than constants"
- ❌ "the gate learns to route"（有效专家数 2.44/3，是 soft reweighting）
- ❌ "structure always helps" / 任何把 AMK 的收益归给 additive kernel 的说法
- ❌ 把 0.692611 或 0.695550 当上界（前者不可复现，后者是 per-mutation）
- ❌ "8.9% headroom"（旧数，现值 3.6%）
- ❌ 用 seed 1 的 per_unit.csv 复核得出 0.688046 然后当成 headline
