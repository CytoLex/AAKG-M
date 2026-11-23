"""Is a parameter-free rank average actually worse than the tuned constant?

The gap measured +0.0010 in favour of the tuned constant. Every other 0.001-scale claim in this project has died
under a paired interval, so this one gets the same treatment before it is written down: per-assay scores, paired,
bootstrapped over assays with the official re-aggregation inside each resample.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
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
rng = np.random.default_rng(0)
print(f"assays {n}", flush=True)

def agg(v, idx=None):
    idx = np.arange(n) if idx is None else idx
    df = pd.DataFrame({"v": np.asarray(v)[idx]}, index=[ids[j] for j in idx]).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

rank_avg = []
for aid in ids:
    v = []
    for gs in units[aid]:
        Z = [rankdata(z(gs[c].to_numpy(float))) for c in COLS]
        v.append(sp(np.mean(Z, axis=0), gs["y"].to_numpy(float)))
    rank_avg.append(float(np.nanmean(v)))
rank_avg = np.array(rank_avg)

G = grid(4)
S = np.empty((len(G), n))
for gi, w in enumerate(G):
    for i, aid in enumerate(ids):
        v = []
        for gs in units[aid]:
            Z = [z(gs[c].to_numpy(float)) for c in COLS]
            v.append(sp(sum(a * c for a, c in zip(w, Z)), gs["y"].to_numpy(float)))
        S[gi, i] = float(np.nanmean(v))
const = np.array([S[int(np.argmax((S.sum(axis=1) - S[:, i]) / (n - 1))), i] for i in range(n)])

print(f"  rank average    {agg(rank_avg):.4f}", flush=True)
print(f"  tuned constant  {agg(const):.4f}", flush=True)
d = []
for _ in range(2000):
    idx = rng.integers(0, n, n)
    d.append(agg(rank_avg, idx) - agg(const, idx))
lo, hi = np.percentile(d, [2.5, 97.5])
print(f"\n  rank - tuned: {np.mean(d):+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  P(rank>tuned) = {np.mean(np.array(d)>0):.2f}", flush=True)
json.dump({"rank": agg(rank_avg), "tuned": agg(const), "diff_mean": float(np.mean(d)),
           "ci": [float(lo), float(hi)], "p_rank_better": float(np.mean(np.array(d) > 0))},
          open(f"{R}/base_ci.json", "w"), indent=2)
print("BASE CI DONE", flush=True)
