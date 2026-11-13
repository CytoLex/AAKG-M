# FINAL_ABSTRACT — 定稿（2026-11-08 修订）

> **这一版按 §8.53/§8.90 重写**：第四专家换成蒸馏编码器 + 类别低秩残差。**主张挂在单模型层级 0.6963 ± 0.0004（8 seed 均值）**，seed 集成后的 0.6985 作为部署数字紧随其后。
> 原 §8.27–8.28 版（0.6911，ESM 位点专家）作废；更早的"gate 打平常数"版也作废。
> 主张没变：**不是门控赢了，是把门控删掉、换了一个更强的专家**——但"增益只来自去相关"这句已被自己的数据推翻，见下方"五处必须小心"。
> 主版本 195 词（CVPR 上限 200）；短版 120 词；一句话 34 词。词数为实测。
> **不要**出现 "state-of-the-art"、"outperform"、"significantly"。

---

## 主版本（195 词，投稿用）

Protein fitness models fuse sequence and structure experts, validated almost always against another
fixed blend. We ask what a tuned baseline leaves, against a constant tuned on held-out assays.
First, the learned part does not help. A label-free gate over frozen experts matches that constant
to 0.0002 and falls 0.0046 behind once a fourth expert enters; six further mechanisms also fail.
Second, the expert pool does help. Adding a distilled ESM-650 expert with a category-specific
low-rank residual raises a fixed-weight fusion from 0.6876 to **0.6963 ± 0.0004** over eight seeds:
**+0.0054** against the previous four-expert fusion (95% CI [+0.0035, +0.0076]) and **+0.0084**
against the published gate, positive in all eight. Averaging that expert over the same eight seeds
lifts it to **0.6985**. The original experts correlate 0.78 to 0.96; the newcomer is the only one
from a different representation — but it is also more accurate than the one it replaces (0.645
versus 0.494), so decorrelation alone does not explain it. The gain is aggregate, not universal (97
assays improve, 85 decline, 35 unchanged). The gate's failure is diagnosable: per-assay headroom is
real, 49% surviving a variant-level split, but no label-free descriptor predicts it ($R^2 \le 0$).

---

## 短版本（120 词，workshop / 短报告）

Assay-conditional fusion of protein fitness experts is usually validated against a fixed blend. We
validate it against a constant tuned on held-out assays, and find the learned gate is worth nothing:
it matches a three-expert constant to 0.0002 and falls 0.0046 behind once a fourth expert is added.
The expert pool, by contrast, is worth something: a distilled ESM-650 encoder expert with a
category-specific low-rank residual lifts a fixed-weight fusion from 0.6876 to 0.6963 ± 0.0004 over
eight seeds, +0.0054 against the previous fusion and +0.0084 against the published gate; averaging
the expert over those seeds gives 0.6985. The newcomer is both decorrelated and more accurate than
the expert it replaces. Improving the experts pays; improving the weighting mechanism does not.

---

## 一句话版（34 词）

A learned gate over protein fitness experts adds nothing once the baseline is tuned; a distilled
encoder expert raises a fixed-weight fusion from 0.6876 to 0.6963. The gain is the expert, not
adaptive weighting.

---

## 句子 → 证据映射

| 摘要句 | 证据 | 位置 |
|---|---|---|
| **0.6963 ± 0.0004, eight seeds**（**主张所在层级**） | lr8 单 seed，8 次独立训练 | §8.53 / `headline_seeds.json` |
| **+0.0054 [+0.0035, +0.0076] vs 上一版四专家** | 同 seed 配对，8/8 为正 | §8.53 |
| **+0.0084 vs 已发表门控** | 0.6963 − 0.687851 | §8.53 |
| 0.6985（**部署层级**） | 同一专家 8 seed 预测平均 | §8.90 / `seed_avg.json` |
| +0.0109 vs 三专家常数（部署） | 0.6985 − 0.687637 | §8.90 |
| +0.0106 vs 已发表门控（部署） | 0.6985 − 0.687851 | §8.90 |
| gate falls 0.0046 behind with four experts | 8-seed gate mean 0.693227 vs constant 0.697811 | §8.26 / `final4.json` |
| six mechanisms at or below the constant | mechanism spectrum | §8.12 / `mechanisms.json` |
| newcomer scores 0.645 alone | lr8 + 8 seed 平均，182 assay | `standalone_scores.json` |
| the replaced expert scored 0.494 | official 0.4766–0.4967 across three feature sets | §8.24 / `esm_expert.json` |
| experts correlate 0.78–0.96 | within-unit rank correlation | §8.29 / `five_expert.json` |
| 49% of headroom survives a split | split-half A→B | §5.4 / `headroom_split.json` |
| $R^2 \le 0$ | context→oracle weights, ridge and RF, 17 and 768 dims | §5.4 / `struct_screen.json` |

## 五处必须小心

1. **两个层级不能混**：`0.6963` 是**主张层级**（单模型、8 seed、有 ±、可配对检验），`0.6985` 是**部署层级**（8 seed 预测平均、无 ±）。
   摘要里"8/8 seed 为正"这句**只能挂在 0.6963 上**，0.6985 没有 seed 维度。
2. **四个 delta 来源各不相同**：单模型层 `+0.0054`（对上一版四专家，CI [+0.0035, +0.0076]）、`+0.0084`（对已发表门控）；
   部署层 `+0.0077`（对上一版四专家）、`+0.0106`（对门控）、`+0.0109`（对三专家常数）。
3. **0.645 是 newcomer 单独的官方分**（lr8，8 seed 平均）；被它替换的旧 ESM 专家是 0.4942。两者都要给，否则"去相关"的说法站不住。
4. **不要再写"增益来自去相关而不是准确率"**——新专家同时更准（**0.645** vs 旧专家的 **0.494**），这个因果已被自己的数据推翻。
5. **必须写"聚合增益、非普遍改善"**：217 个 assay 里 97 正 / 85 负 / 35 零，中位差 0，增益主要由 Binding 拉动。
   任何"五类普涨"或"逐 assay 受益"的表述都不被证据支持。

## 与旧版的差异（供对照）

| | 旧版 | 新版 |
|---|---|---|
| 头条 | 0.6879（9 seed 门控） | **0.6963 ± 0.0004（单模型）/ 0.6985（seed 集成部署）** |
| 对常数 | +0.0002，打平 | **+0.0086（单模型）/ +0.0109（部署），赢** |
| 主要结论 | 条件化不值钱 | **条件化不值钱，但专家池值钱** |
| 方法复杂度 | 1,347 参数的门 | **4 个常数，0 参数** |
| 第四专家 | ESM 位点嵌入（0.494） | **ESM-650 蒸馏编码器 + 低秩 + seed 集成（0.645）** |
