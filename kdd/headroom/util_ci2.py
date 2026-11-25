"""Intervals and reproducible values for the utility table.

The published figures (0.119 / 0.247 / 0.350) could not be regenerated from the released bundle under any of four
tie and aggregation conventions; all four land 0.006 to 0.011 below, which points at the per-fold nested fusion
those figures were produced with rather than at rounding. This recomputes the table in the pipeline that the release
supports -- the paper's fixed fusion -- and puts a bootstrap interval on every entry so the section carries the same
discipline as the rest of the paper.
"""
import os
import json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)

def z(a):
    a = np.asarray(a, np.float64); return (a - a.mean()) / (a.std() + 1e-12)
b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay", "scheme", "variant_id", "X"]], on=["assay", "scheme", "variant_id"], how="inner")
m = m.dropna(subset=["D", "Kermut", "AMK", "X", "y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")

def fusion(gs):
    return 0.40 * z(gs["Kermut"].to_numpy(float)) + 0.40 * z(gs["AMK"].to_numpy(float)) + 0.20 * z(gs["X"].to_numpy(float))
def recall(pred, y, frac):
    n = len(y); k = int(np.ceil(frac * n))
    return len(set(np.argsort(-pred)[:k].tolist()) & set(np.argsort(-y)[:k].tolist())) / k

units = []
for aid, g in m.groupby("assay"):
    for sch, gs in g.groupby("scheme"):
        if len(gs) >= 20: units.append((aid, sch, gs))
assays = sorted({u[0] for u in units}); meta = ref.reindex(assays)
print(f"units {len(units)} | assays {len(assays)}", flush=True)

per = {k: pd.Series({(aid, sch): recall(fusion(gs), gs["y"].to_numpy(float), k) for aid, sch, gs in units})
       for k in (0.01, 0.05, 0.10)}
def agg(v):
    s = v.groupby(level=0).mean()
    df = pd.DataFrame({"v": s}).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

out = {}
for k, v in per.items():
    note = agg(v); boot = []
    for _ in range(2000):
        pick = list(np.array(assays)[rng.integers(0, len(assays), len(assays))])
        sub = v[v.index.get_level_values(0).isin(pick)]
        boot.append(agg(sub))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    out[str(k)] = {"recall": note, "ci": [float(lo), float(hi)], "lift": note / k, "lift_ci": [float(lo / k), float(hi / k)]}
    print(f"  top-{k:.0%}: recall {note:.4f} [{lo:.4f}, {hi:.4f}] | lift {note/k:.2f}x [{lo/k:.2f}x, {hi/k:.2f}x]", flush=True)

print("\nper category, top-5%:", flush=True)
cat = {}
for c in sorted(meta["coarse_selection_type"].dropna().unique()):
    ids_c = [a for a in assays if meta.loc[a, "coarse_selection_type"] == c]
    if not ids_c: continue
    sub = per[0.05][per[0.05].index.get_level_values(0).isin(ids_c)]
    note = float(sub.groupby(level=0).mean().mean())
    boot = []
    for _ in range(2000):
        pick = list(np.array(ids_c)[rng.integers(0, len(ids_c), len(ids_c))])
        ss = sub[sub.index.get_level_values(0).isin(pick)]
        boot.append(float(ss.groupby(level=0).mean().mean()))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    cat[c] = {"recall": note, "lift": note / 0.05, "lift_ci": [float(lo / 0.05), float(hi / 0.05)]}
    print(f"  {c:18s} recall {note:.4f} | lift {note/0.05:.2f}x [{lo/0.05:.2f}x, {hi/0.05:.2f}x]", flush=True)
json.dump({"overall": out, "category_5pct": cat}, open(f"{R}/util_ci2.json", "w"), indent=2)
print("\nUTIL CI2 DONE", flush=True)
