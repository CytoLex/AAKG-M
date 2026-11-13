# §5.3 and §5.4 — 定稿（2026-11-08 修订）

> 5.3 解释**为什么加专家有效**（去相关，不是单独分）；5.4 解释**为什么门控无效**（headroom 真但不可测）。
> 这两节合起来是本文的解释层：一个正面、一个负面，共用同一套诊断工具。
> **2026-11-08 修订**：第四专家换成蒸馏编码器（单独 0.598），§5.3 的对比表与论证已随之重写；
> §5.4 增加一段说明 oracle 只对"旧专家池的权重单纯形"成立。
> 数字来源：`five_expert.json`、`final4.json`、`headline_seeds.json`、`headroom_split.json`、`struct_screen.json`、`visual_emb_screen.json`、`few_shot.json`、`few_shot_active.json`。

---

## 5.3 收益来自"和池子不相关"，不是来自单独分

专家单独分与彼此相关（unit 内秩相关均值）：

| 专家 | 单独分 | 与池子的相关 |
|---|---:|---|
| Kermut | 0.6625 | 0.78–0.84 |
| AMK | 0.6620 | 0.83–0.96 |
| D | 0.6562 | 0.84–0.96 |
| Kseq | 0.6391 | 0.78–0.92 |
| 旧 ESM 位点嵌入（$E_{\text{old}}$） | 0.4942 | 显著更低（不同表征） |
| **蒸馏编码器（$X$，本文）** | **0.5980** | **同样来自不同表征** |

现有专家彼此相关 **0.78–0.96**：这个池子在名义上多样，实际上几乎共线。

**关键对比：单独分更低的那一个，贡献反而更大。**

| 加入的专家 | 单独分 | 对三专家融合的贡献 | 基准 |
|---|---:|---:|---|
| $E_{\text{old}}$ | 0.4942 | **+0.00317** | 0.687637 → 0.690808 |
| **$X$（本文，仅 union 阶段）** | **0.5980** | **+0.00720** | 0.687637 → 0.694837 |
| Kseq | **0.6391** | **+0.00090** | 0.690808 → 0.691708（四专家基准） |

$X$ 的单独分（0.5980）比 Kseq（0.6391）**低 0.041**，但它的贡献**是 Kseq 的 8 倍**；而它与池子的
相关显著更低。**一个专家的边际价值，看起来取决于它和已有专家的相关，而不取决于它自己的分数。**
（注意：这条规律的直接证据只有 **5 个候选**，其中 2 个是合成对照；它是描述性的、探索性的观察，
不足以支撑"普遍机制"或因果表述。要作为机制论证，需要扩大候选集并预注册分析。）
Kseq 拿到 0.1 权重后几乎全部是从 AMK 的 0.5 匀过来的（两者相关 0.92）。

这个规律在两个方向上同时成立：它是 $X$ 能赚到的原因，也是继续往池子里加同源专家赚不到的原因。

**一个必须说清的边界。** 新专家相对旧专家**既更准（0.598 vs 0.494）又更不相关**，两个因素同时变了，
所以**我们不能声称这次的增益"只来自去相关"**。上文支持的是更弱的命题：在单独分相近的区间里
（Kseq 0.639 vs $X$ 0.598），相关性的差别足以造成 8 倍的边际价值差。要把"准确率"和"去相关"完全
分离，需要一个单独分相同但相关性不同的对照——本文没有做，留作限制。

一个直接的方法学推论：

> 改进这类融合系统的**可能**方向是找不同表征的专家，而不是找更聪明的分配机制。前者在我们的
> 数据上，换专家这条线最终给出 **+0.0054（单模型，主张层级）／+0.0077（部署层级）**（仅 union 阶段为 +0.0072），改分配给出 **−0.0046**——但采购准则本身只有 5 个候选，这是提示而非定律。

---

## 5.4 门控为什么学不到：headroom 是真的，但不可观测

**headroom 是真实的。** 一个 per-assay oracle 在 231 点单纯形上达到 **0.693544**，与三专家常数
（0.687637）相距 **0.0057**。

> **口径提醒（2026-11-08 加）**：这个 oracle 是在**旧专家池**的权重单纯形上算的（单协议、未按 seed 对齐）。
> 本文最终的固定权重融合达到 **0.698495**，**超过了这个 oracle**。这不矛盾——oracle 度量的是"在同一组专家内部重新
> 分配权重还能拿多少"，而不是方法的天花板；换一个更强的专家，天花板本身就被抬高了。§5.4 的结论因此
> 应读作**关于权重分配机制的**，不是关于模型上限的。这个差距不是选择噪声：把每个 (assay, scheme) 的变异随机分成两半
$A$/$B$，在 $A$ 上选权重、在 $B$ 上评分，$A$ 上选的权重仍然比 $A$ 上选的常数高 **+0.0041**，即
就地可得增益（+0.0083）的 **49%**。per-assay 最优权重是 assay 的稳定属性。

**但没有任何 label-free 描述子能预测它。** 用同一套特征预测门自己的权重，交叉验证
$R^2 = 0.52 / 0.43 / 0.67$；预测 oracle 权重，同一回归器给 **$R^2 = -0.13 / -0.10 / 0.08$**。
换成更强的表征也一样：

| 上下文 | → 门权重 $R^2$ | → oracle 权重 $R^2$ |
|---|---|---|
| 17 维手写统计量 | 0.52–0.67 | $-0.13$ – $+0.08$ |
| 768 维视觉 assay 嵌入 | — | $\approx 0$（raw 与 PCA 5/20/40 全部） |
| 14 个逐残基结构特征 | — | 把 ridge 从 $-0.12$ 拉到 $0.00$ |

768 维、视觉来源、与 17 维完全不同构造的信息，给出同一个答案。**这不是"特征不够多"，是
"assay 级描述子里没有这个信息"。**

**代价是标签，而不是架构。** 给每个 held-out assay $k$ 个**有标签**的变异（与评测集不重叠），
在 $k$ 上选权重再评其余：

| $k$ | k-shot | 常数 | Δ |
|---:|---:|---:|---:|
| 16 | 0.6934 | 0.7024 | −0.0090 |
| 64 | 0.6983 | 0.7023 | −0.0040 |
| 128 | 0.7011 | 0.7023 | −0.0012 |
| **256** | 0.7026 | 0.7020 | **+0.00056** |
| **512** | 0.7039 | 0.7020 | **+0.00186** |

符号翻转在 **$k \approx 215$**，到 $k = 512$ 时吃到 oracle headroom 的 **50%**。而且这个阈值
**降不下来**：四种无标签的标注选择策略里，随机抽样最好；按专家分歧挑选在每一个 $k$ 上都更差
（−0.0087 到 −0.0098），因为有偏子样本的偏差不随样本量消失。

**为什么这些是"零"而不是"功效不足"。** 217 个 assay 在类别内重采样，聚合差的配对 95% 区间半宽
约 **0.0014**，即效应需达到约 **0.002** 才能在 80% 功效下被判为真实。§5.2 的六种机制全部落在常数
0.0005 以内——是阈值的四分之一。加 seed 不改变这一点，因为区间由 assay 异质性主导。

---

## 数字索引

| 论断 | 值 | 来源 |
|---|---|---|
| 专家单独分与相关 | 0.5980–0.6625；0.78–0.96 | `five_expert.json`、`union.json` |
| $X$ 的贡献 / Kseq 的贡献 | +0.00720 / +0.00090 | `headline_seeds.json`、`five_expert.json` |
| 旧 $E$ 的贡献 | +0.00317 | `final4.json` |
| oracle / headroom（旧池） | 0.693544 / 0.0057（**低于本文最终 0.698495**） | `oracle_local.json` |
| split-half 存活 | +0.0041（占 +0.0083 的 49%） | `headroom_split.json` |
| context→门 / →oracle $R^2$ | 0.52–0.67 / ≤0.08 | `context_recovers_weights.json` |
| 768 维视觉嵌入 $R^2$ | ≈0 | `visual_emb_screen.json` |
| 结构特征把 $R^2$ 从 −0.12 拉到 0.00 | −0.019/0.008/−0.012 | `struct_screen.json` |
| k-shot 阈值 | ≈215；k=512 时 +0.00186 | `few_shot.json` |
| 主动选择劣于随机 | 四种策略对比 | `few_shot_active.json` |
| 检测阈 | ±0.0014 → 0.002 | `verify_matrix.json` |

## 不能写错的三处

1. **"49% 存活"** 是就地增益的比例，不是相对常数的绝对提升；绝对存活增量是 +0.0041（在 $B$ 上）。
2. **oracle 0.693544 是旧专家池、单协议的**，本文最终 0.698495 已超过它——不能写成"我们接近了 oracle"，
   也不能让读者以为是"我们超过了 oracle"；正确说法是 oracle 只回答权重分配问题。
3. **"$R^2 \le 0$"** 说的是 label-free 预测 oracle 权重；不要扩大成"context 没有信息"——它对门
   自己的权重 $R^2$ 高达 0.67，这正是"稳定但方向错"的证据。

---

## English camera-ready text

### 5.3 The gain tracks decorrelation, not standalone accuracy

The experts in the pool are nearly collinear: their within-unit rank correlations range from 0.78 to
0.96, and the strongest of them, Kermut at 0.6625, correlates 0.83 with AMK and 0.84 with D. The
contrast that matters is between two experts from different representations. A distilled ESM-650
encoder scoring **0.5980** on its own lifts the three-expert fusion to **0.694837** (the union stage,
before the low-rank branch and seed averaging), a contribution of
**+0.00720**; the correlated Kseq expert, scoring **0.6391** — 0.041 *higher* — contributes only
**+0.00090**. What appears to earn an expert its place is its residual correlation with the pool rather
than its standalone score; with five candidates (two of them synthetic controls) this remains a
descriptive observation, not an established mechanism. We stop short of the stronger claim: the new expert is both more accurate than the
site-embedding expert it replaces (0.5980 versus 0.4942) and less correlated, so accuracy and
decorrelation are not separated here, and we report the weaker, supported statement. The corollary is tentative for the same reason: the evidence is consistent with searching for
experts from new representations rather than for cleverer weighting rules — +0.0054 (single model) versus −0.0046
here — but five candidates cannot establish it as a rule.

### 5.4 The headroom is real and unobservable

A per-assay oracle over the simplex of the *original* expert pool reaches 0.693544, 0.0057 above the
tuned constant. That oracle is a statement about re-weighting a fixed pool under one protocol, not about the ceiling of
the method: the final fixed-weight fusion reaches 0.698495 and therefore
already exceeds it, because swapping in a stronger expert raises the ceiling itself. Within that pool, the gap is not selection
noise: choosing weights on one half of each unit's variants and scoring the other
half still beats the constant by +0.0041, 49% of the gain available in-sample. Yet no label-free
descriptor we can compute predicts it. The seventeen statistics predict the gate's own weights at
$R^2$ = 0.52–0.67 but the oracle weights at $R^2 \le 0.08$; a 768-dimensional visual assay embedding
and fourteen per-residue structure features give $R^2 \approx 0$ as well. The price of the headroom is
labels: with $k$ labelled variants per assay the advantage of conditioning turns positive at
$k \approx 215$ and reaches half the oracle headroom at $k = 500$, and no label-free sampling rule we
tried lowers that threshold — random selection was the best of four.
