"""The standard fusion baselines the mechanism table never had.

All seven mechanisms in the paper are conditional: they vary weights by assay, by category or by variant. What is
absent is the unconditional family every ensemble paper reports -- equal-weight averaging of standardised scores,
rank averaging, and a median -- and those are what a reader in this literature will ask about first. If a
parameter-free average matches the tuned constant, the baseline the paper spends a section defending is not the
right one; if it does not, the claim is stronger for having been checked.
"""
import os
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"

def z(a):
    a = np.asarray(a, np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0: return np.nan
    return spearmanr(a, b).correlation
def grid(k, step=0.1):
    m = int(round(1 / step))
    return np.array([w for w in itertools.product(np.linspace(0, 1, m + 1), repeat=k) if abs(sum(w) - 1) < 1e-9])

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay", "scheme", "variant_id", "X"]], on=["assay", "scheme", "variant_id"], how="inner")
m = m.dropna(subset=["D", "Kermut", "AMK", "X", "y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS = ["D", "Kermut", "AMK", "X"]
units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per: units[aid] = per
ids = sorted(units); meta = ref.reindex(ids); n = len(ids)
print(f"assays {n} | experts {COLS}", flush=True)

def agg(vals):
    df = pd.DataFrame({"v": vals}, index=ids).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

# --- unconditional rules: no labels used to set weights ---
def rule_score(aid, kind):
    v = []
    for gs in units[aid]:
        y = gs["y"].to_numpy(float)
        Z = [z(gs[c].to_numpy(float)) for c in COLS]
        if kind == "equal_z":      pred = np.mean(Z, axis=0)
        elif kind == "rank_avg":   pred = np.mean([rankdata(vv) for vv in Z], axis=0)
        elif kind == "median":     pred = np.median(np.vstack(Z), axis=0)
        elif kind == "two_best":   pred = np.mean([z(gs[c].to_numpy(float)) for c in ("Kermut", "AMK")], axis=0)
        v.append(sp(pred, y))
    return float(np.nanmean(v))

rules = ("equal_z", "rank_avg", "median", "two_best")
res = {}
for kind in rules:
    res[kind] = agg(np.array([rule_score(aid, kind) for aid in ids]))
    print(f"  {kind:10s} {res[kind]:.4f}", flush=True)

# --- tuned constants, for reference on the same units ---
G = grid(4)
S = np.empty((len(G), n))
for gi, w in enumerate(G):
    for i, aid in enumerate(ids):
        v = []
        for gs in units[aid]:
            Z = [z(gs[c].to_numpy(float)) for c in COLS]
            v.append(sp(sum(a * c for a, c in zip(w, Z)), gs["y"].to_numpy(float)))
        S[gi, i] = float(np.nanmean(v))
looconst = np.array([S[int(np.argmax((S.sum(axis=1) - S[:, i]) / (n - 1))), i] for i in range(n)])
res["tuned_constant_loo"] = agg(looconst)
print(f"  {'tuned LOO':10s} {res['tuned_constant_loo']:.4f}", flush=True)

best_rule = max(rules, key=lambda k: res[k])
print(f"\nbest unconditional rule: {best_rule} at {res[best_rule]:.4f}")
print(f"tuned constant minus best unconditional: {res['tuned_constant_loo'] - res[best_rule]:+.4f}", flush=True)
json.dump(res, open(f"{R}/baselines.json", "w"), indent=2)
print("BASELINES DONE", flush=True)
