"""IJCAI variants of the two figures.

The parent make_figs.py authors them at 3.4 in wide for ACM/ICML columns. IJCAI's column is
(7.0 - 0.25)/2 = 3.375 in, and the build includes figures at 0.86 of that, so the artwork is authored
here at 2.90 in: the scale factor becomes 1.00 and an 8.5pt label renders at 8.5pt instead of 6.8pt.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

W = 2.90                      # matches 0.86 * IJCAI column width
plt.rcParams.update({"font.size": 8.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0.6, "font.family": "DejaVu Sans"})

# ---------------------------------------------------------------- Figure 1
const, gate, blend, oracle, final = 0.687637, 0.687888, 0.690808, 0.693544, 0.698495
fig, ax = plt.subplots(figsize=(W, 1.75))
ax.set_xlim(0.6868, 0.6992); ax.set_ylim(-0.7, 2.3)

ax.add_patch(plt.Rectangle((const, 0.55), oracle - const, 0.32, facecolor="#c8d8ec",
                           edgecolor="#3a6ea5", lw=0.7, zorder=2))
ax.annotate("", xy=(oracle, 1.06), xytext=(const, 1.06),
            arrowprops=dict(arrowstyle="<->", lw=0.8, color="#3a6ea5"))
ax.text((const + oracle) / 2, 1.15, "allocation headroom\n+0.0027", ha="center", va="bottom",
        fontsize=7.5, color="#3a6ea5", linespacing=1.15)

ax.annotate("", xy=(final, -0.16), xytext=(blend, -0.16),
            arrowprops=dict(arrowstyle="<->", lw=0.8, color="#b0552a"))
ax.text((blend + final) / 2, -0.30, "expert swap\n+0.0077", ha="center", va="top",
        fontsize=7.5, color="#b0552a", linespacing=1.15)

for x, label, y, ha in ((const, "tuned\nconstant", 0.40, "right"),
                        (gate, "MLP gate", 1.02, "left"),
                        (blend, "fixed blend", 0.40, "left"),
                        (oracle, "per-assay\noracle", 0.40, "center"),
                        (final, "this fusion", 0.08, "center")):
    ax.plot([x], [0.71], "o", ms=3.4, color="#222", zorder=4)
    ax.text(x, y, label, ha=ha, va="center", fontsize=7.0, linespacing=1.1)

ax.set_yticks([]); ax.set_xlabel("official aggregation, per-assay protocol", fontsize=7.8)
for s in ("left", "right", "top"): ax.spines[s].set_visible(False)
ax.set_xticks([0.688, 0.690, 0.692, 0.694, 0.696, 0.698])
ax.tick_params(axis="x", labelsize=7.2)
fig.tight_layout(pad=0.15)
fig.savefig("fig1_allocation_vs_expert_ijcai.pdf", bbox_inches="tight")
fig.savefig("fig1_allocation_vs_expert_ijcai.png", dpi=240, bbox_inches="tight")

# ---------------------------------------------------------------- Figure 2
cats = ["Activity", "Expression", "Organismal\nFitness", "Binding", "Stability"]
top1 = [0.0657, 0.1012, 0.1008, 0.1017, 0.2265]
top5 = [0.1720, 0.2090, 0.2284, 0.2435, 0.3837]
top10 = [0.2714, 0.3198, 0.3316, 0.3466, 0.4825]
rand = [0.0101, 0.0100, 0.0101, 0.0104, 0.0100]

x = np.arange(len(cats)); w = 0.26
fig, ax = plt.subplots(figsize=(W, 1.85))
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
