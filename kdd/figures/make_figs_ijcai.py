"""IJCAI variants of the two figures.

The parent make_figs.py authors them at 3.4 in wide for ACM/ICML columns. IJCAI's column is
(7.0 - 0.25)/2 = 3.375 in, and the build includes figures at 0.86 of that, so the artwork is authored
here at 2.90 in: the scale factor becomes 1.00 and an 8.5pt label renders at 8.5pt instead of 6.8pt.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

W = 2.30                      # matches 0.68 * IJCAI column width (3.375 in)
plt.rcParams.update({"font.size": 8.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0.6, "font.family": "DejaVu Sans"})

# ---------------------------------------------------------------- Figure 1
# Full-width, two panels: the two levers (left) and the thirteen expert-into-pool points (right).
# The right panel is the claim the title makes; it had only ever existed as a table.
const, oracle, poolB = 0.6830, 0.6881, 0.6952

# thirteen expert-into-pool points, from the run that produced r = +0.786
PTS = [
    ("D",      0.064, 0.0000, "4-expert pool"),
    ("Kermut", 0.143, 0.0062, "4-expert pool"),
    ("Kseq",   0.104, 0.0004, "4-expert pool"),
    ("AMK",    0.060, 0.0028, "4-expert pool"),
    ("X",      0.194, 0.0118, "4-expert pool"),
    ("Kseq",   0.126, 0.0040, "into D+Kermut"),
    ("AMK",    0.067, 0.0060, "into D+Kermut"),
    ("X",      0.190, 0.0136, "into D+Kermut"),
    ("D",      0.063, 0.0001, "into Kermut+AMK"),
    ("Kseq",   0.116, 0.0014, "into Kermut+AMK"),
    ("X",      0.189, 0.0122, "into Kermut+AMK"),
    ("Kseq",   0.097, 0.0007, "into D+K+AMK"),
    ("X",      0.193, 0.0122, "into D+K+AMK"),
]
COL = {"D": "#7f7f7f", "Kermut": "#3a6ea5", "Kseq": "#4c9a5a", "AMK": "#b0552a", "X": "#8e44ad"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 1.68), gridspec_kw={"width_ratios": [1, 1.15]})

# --- left: the two levers from one origin
ax1.set_xlim(0.6820, 0.6965); ax1.set_ylim(-0.9, 2.6)
ax1.annotate("", xy=(oracle, 1.55), xytext=(const, 1.55),
             arrowprops=dict(arrowstyle="<->", lw=1.0, color="#3a6ea5"))
ax1.text((const + oracle) / 2, 1.70, "allocation headroom\n+0.0051 (0.0038-0.0066)",
         ha="center", va="bottom", fontsize=6.6, color="#3a6ea5", linespacing=1.15)
ax1.annotate("", xy=(poolB, 0.55), xytext=(const, 0.55),
             arrowprops=dict(arrowstyle="<->", lw=1.0, color="#b0552a"))
ax1.text((const + poolB) / 2, 0.70, "one more expert\n+0.0122 (0.0099-0.0144)",
         ha="center", va="bottom", fontsize=6.6, color="#b0552a", linespacing=1.15)
for x, lab in ((const, "constant"), (oracle, "per-assay\noracle"), (poolB, "+ expert")):
    ax1.plot([x], [0.0], "o", ms=3.4, color="#222", zorder=4)
    ax1.text(x, -0.28, lab, ha="center", va="top", fontsize=6.4, linespacing=1.1)
ax1.set_yticks([])
ax1.set_xticks([0.683, 0.686, 0.689, 0.692, 0.695])
ax1.tick_params(axis="x", labelsize=6.4)
ax1.set_xlabel("official aggregation, 182 assays", fontsize=6.8)
for sp_ in ("left", "right", "top"): ax1.spines[sp_].set_visible(False)

# --- right: the thirteen points
for name, d, m, pool in PTS:
    ax2.plot(d, m, "o", ms=4.0, color=COL[name], alpha=0.92, zorder=4, label=name if pool == "4-expert pool" else None)
ax2.set_xlabel("disagreement with the pool", fontsize=6.8)
ax2.set_ylabel("marginal value", fontsize=6.8)
ax2.tick_params(labelsize=6.4)
ax2.grid(alpha=0.18, lw=0.4)
ax2.text(0.0455, 0.0148, "r = +0.786 over 13 pairs", fontsize=6.3, style="italic", va="top")
ax2.legend(fontsize=5.6, frameon=False, loc="lower right", handlelength=0.9, labelspacing=0.25,
           borderaxespad=0.2, title="expert", title_fontsize=5.8)
ax2.set_ylim(-0.0016, 0.0165); ax2.set_xlim(0.042, 0.215)
for sp_ in ("right", "top"): ax2.spines[sp_].set_visible(False)

fig.tight_layout(pad=0.25, w_pad=1.6)
fig.savefig("fig1_allocation_vs_expert_ijcai.pdf", bbox_inches="tight")
fig.savefig("fig1_allocation_vs_expert_ijcai.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------- Figure 2
cats = ["Activity", "Expression", "Organismal\nFitness", "Binding", "Stability"]
top1 = [0.0657, 0.1012, 0.1008, 0.1017, 0.2265]
top5 = [0.1720, 0.2090, 0.2284, 0.2435, 0.3837]
top10 = [0.2714, 0.3198, 0.3316, 0.3466, 0.4825]
rand = [0.0101, 0.0100, 0.0101, 0.0104, 0.0100]

x = np.arange(len(cats)); w = 0.26
fig, ax = plt.subplots(figsize=(W, 1.6))
ax.bar(x - w, top1, w, label="top 1%", color="#1f4e79")
ax.bar(x, top5, w, label="top 5%", color="#3a7ca5")
ax.bar(x + w, top10, w, label="top 10%", color="#90b8d4")
ax.plot(x, rand, "_", color="#c0392b", ms=10, mew=1.3, label="random", zorder=5)
ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=7.0)
ax.set_ylabel("recall of the true top-$k$", fontsize=7.8)
ax.tick_params(axis="y", labelsize=7.2)
ax.legend(fontsize=6.8, frameon=False, loc="upper left", handlelength=1.1)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.15)
fig.savefig("fig2_topk_by_category_ijcai.pdf", bbox_inches="tight")
fig.savefig("fig2_topk_by_category_ijcai.png", dpi=240, bbox_inches="tight")
print("wrote IJCAI-scaled figures")
