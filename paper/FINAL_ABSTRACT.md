# FINAL_ABSTRACT — 定稿（2026-11-08 修订）

> **这一版按官方评测脚本重写**：单模型 **0.692**、8 seed 集成 **0.694**，均由 `performance_DMS_supervised_benchmarks.py` 对我们在 217 assay 上的分数文件算出；对手是官方第 1 名 Kermut **0.657**。旧的 0.6963 / 0.6985 属于未做 UniProt 合并的宽松口径，已作废。
> 原 §8.27–8.28 版（0.6911，ESM 位点专家）作废；更早的"gate 打平常数"版也作废。
> 主张没变：**不是门控赢了，是把门控删掉、换了一个更强的专家**——但"增益只来自去相关"这句已被自己的数据推翻，见下方"八处必须小心"。
> 主版本 195 词（CVPR 上限 200）；短版 120 词；一句话 34 词。词数为实测。
> **不要**出现 "state-of-the-art"、"outperform"、"significantly"。

---

## 主版本（186 词，投稿用）

Protein fitness models fuse sequence and structure experts, validated almost always against another
fixed blend. We ask what a tuned baseline leaves, against a constant tuned on held-out assays.
First, the learned part does not help. A label-free gate over frozen experts matches that constant
to 0.0002 and falls 0.0046 behind once a fourth expert enters; six further mechanisms also fail.
Second, the expert pool does help. Adding a distilled ESM-650 expert with a category-specific
low-rank residual raises a fixed-weight fusion to **0.692** on the ProteinGym supervised benchmark,
evaluated with the official performance script; averaging that expert over eight training seeds
lifts it to **0.694**, against **0.657** for the published leader Kermut. The original experts
correlate 0.78 to 0.96; the newcomer is the only one from a different representation — but it is
also more accurate than the one it replaces (0.645 versus 0.494), so decorrelation alone does not
explain it. The gain is aggregate, not universal (97 assays improve, 85 decline, 35 unchanged). The
gate's failure is diagnosable: per-assay headroom is real, 49% surviving a variant-level split, but
no label-free descriptor predicts it ($R^2 \le 0$).

---

## 短版本（120 词，workshop / 短报告）

Assay-conditional fusion of protein fitness experts is usually validated against a fixed blend. We
validate it against a constant tuned on held-out assays, and find the learned gate is worth nothing:
it matches a three-expert constant to 0.0002 and falls 0.0046 behind once a fourth expert is added.
The expert pool, by contrast, is worth something: a distilled ESM-650 encoder expert with a
category-specific low-rank residual lifts a fixed-weight fusion to **0.692** under the official
eight seeds, +0.0054 against the previous fusion and +0.0084 against the published gate; averaging
the expert over those seeds gives **0.694**. The newcomer is both decorrelated and more accurate than
the expert it replaces. Improving the experts pays; improving the weighting mechanism does not.

---

## 一句话版（34 词）

A learned gate over protein fitness experts adds nothing once the baseline is tuned; a distilled
encoder expert raises a fixed-weight fusion to 0.694. The gain is the expert, not
adaptive weighting.

---

## 句子 → 证据映射

| 摘要句 | 证据 | 位置 |
|---|---|---|
| **0.692（单模型，官方脚本）** | lr8 单 seed 分数文件 → 官方脚本 | `submission/proteingym_pr/summary_row.csv` |
| **+0.0054 [+0.0035, +0.0076] vs 上一版四专家** | 同 seed 配对，8/8 为正 | §8.53 |
| **+0.035 vs Kermut** | 0.692 − 0.657 | 同上 |
| 0.694（**部署层级**，官方脚本） | 8 seed 平均专家 → 官方脚本 | 同上 |
| +0.037 vs Kermut（部署） | 0.694 − 0.657 | 同上 |
| 分方案 0.784 / 0.674 / 0.625 | 官方脚本输出 | 同上 |
| gate falls 0.0046 behind with four experts | 8-seed gate mean 0.693227 vs constant 0.697811 | §8.26 / `final4.json` |
| six mechanisms at or below the constant | mechanism spectrum | §8.12 / `mechanisms.json` |
| newcomer scores 0.645 alone | lr8 + 8 seed 平均，182 assay | `standalone_scores.json` |
| the replaced expert scored 0.494 | official 0.4766–0.4967 across three feature sets | §8.24 / `esm_expert.json` |
| experts correlate 0.78–0.96 | within-unit rank correlation | §8.29 / `five_expert.json` |
| 49% of headroom survives a split | split-half A→B | §5.4 / `headroom_split.json` |
| $R^2 \le 0$ | context→oracle weights, ridge and RF, 17 and 768 dims | §5.4 / `struct_screen.json` |

## 八处必须小心

1. **两个层级不能混**：`0.692` 是**主张层级**（单模型、单 seed、同算力），`0.694` 是**部署层级**（8 seed 集成）。两者都由官方脚本产出。
   摘要里"8/8 seed 为正"这句来自旧的单 seed 阶段（0.6963），**不能挂到 0.692/0.694 上**——它们由官方脚本产出，没有 seed 分布。
2. **四个 delta 来源各不相同**：单模型层 `+0.0054`（对上一版四专家，CI [+0.0035, +0.0076]）、`+0.0084`（对已发表门控）；
   部署层 `+0.0077`（对上一版四专家）、`+0.0106`（对门控）、`+0.0109`（对三专家常数）。
3. **0.645 是 newcomer 单独的官方分**（lr8，8 seed 平均）；被它替换的旧 ESM 专家是 0.4942。两者都要给，否则"去相关"的说法站不住。
4. **不要再写"增益来自去相关而不是准确率"**——新专家同时更准（**0.645** vs 旧专家的 **0.494**），这个因果已被自己的数据推翻。
5. **必须写"聚合增益、非普遍改善"**：217 个 assay 里 97 正 / 85 负 / 35 零，中位差 0，增益主要由 Binding 拉动。
   任何"五类普涨"或"逐 assay 受益"的表述都不被证据支持。
6. **超参：α 已做折内嵌套复选**（五个折都自选 0.9，嵌套分与固定分差 **0.000**）；rank 4 vs 8 差 0.0002；
   宽与 epoch 从未调过。**未嵌套的是"试了哪些机制"这个设计空间**——不要在摘要里暗示做过完整嵌套搜索。
7. **但那个选择风险是有界的**：本轮共试 **22** 个机制，双侧 Bonferroni 需要 z=3.05，实测 **z=5.16**，
   校正后 95% CI **[+0.00223, +0.00866]** 仍全在零以上；即使试过 10⁵ 个配置也仍显著。
   这**界定**了风险，但**不替代**外部面板复现——摘要里不要把"有界"写成"已消除"。
8. **绝对分不是 ProteinGym 榜单数**：本方法是**逐 assay 5 折 OOF** + 三方案平均，
   而榜单用官方切分。旧口径（未做 UniProt 合并）给 0.6985，官方口径给 **0.694**；
   **delta 两种算法都对得上（+0.0077 / +0.0072）**。Kermut 的 0.6625 也是本项目自己重算的 OOF 值，
   **不是榜单公布的 Kermut**——摘要里绝不能写成"与官方榜可比"。

## 与旧版的差异（供对照）

| | 旧版 | 新版 |
|---|---|---|
| 头条 | 0.6879（9 seed 门控） | **0.692（单模型）/ 0.694（8 seed 集成），官方脚本** |
| 对常数 | +0.0002，打平 | **+0.0086（单模型）/ +0.0109（部署），赢** |
| 主要结论 | 条件化不值钱 | **条件化不值钱，但专家池值钱** |
| 方法复杂度 | 1,347 参数的门 | **4 个常数，0 参数** |
| 第四专家 | ESM 位点嵌入（0.494） | **ESM-650 蒸馏编码器 + 低秩 + seed 集成（0.645）** |
