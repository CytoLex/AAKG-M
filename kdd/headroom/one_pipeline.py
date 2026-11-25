"""Allocation headroom and expert gain, measured in one pipeline.

The paper's +0.0027 compared a three-expert oracle against a four-expert fusion -- two different pools -- so
it is not a within-pool allocation headroom. This recomputes both quantities inside a single aggregation:

  aggregation   per (assay, scheme) Spearman -> mean over schemes -> mean by UniProt -> mean over the five
                categories, which is the paper's chain
  pool A        D, Kermut, AMK
  pool B        the same three plus the distilled encoder X, from preds_savg_s1.csv
  allocation    A's per-assay oracle minus A's nested constant
  expert gain   B's nested constant minus A's nested constant
"""
import os
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean())/(a.std()+1e-12)
def sp(a, b): return spearmanr(a, b).correlation
def grid(k, step=0.1):
    n = int(round(1/step))
    return np.array([w for w in itertools.product(np.linspace(0,1,n+1), repeat=k) if abs(sum(w)-1) < 1e-9])

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
print("bundle", b.shape, "| encoder preds", x.shape, flush=True)
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
print("joined rows:", len(m), "| assays:", m.assay.nunique(), flush=True)
m = m.dropna(subset=["D","Kermut","AMK","X","y"])

ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
pieces = {}
for (aid, sch), g in m.groupby(["assay","scheme"]):
    if len(g) < 20: continue
    pieces.setdefault(aid, []).append(g)
assays = sorted(pieces)
meta = ref.reindex(assays)
print("assays in analysis:", len(assays), "| with UniProt/category:",
      int(meta[["UniProt_ID","coarse_selection_type"]].notna().all(axis=1).sum()), flush=True)

def scores(cols, G):
    """S[g, i]: blend score for grid point g on assay i, averaged over that assay's schemes."""
    n = len(assays)
    S = np.empty((len(G), n))
    for gi, w in enumerate(G):
        for i, aid in enumerate(assays):
            vals = []
            for g in pieces[aid]:
                Xm = [z(g[c].to_numpy(float)) for c in cols]
                vals.append(sp(sum(a*c for a, c in zip(w, Xm)), g["y"].to_numpy(float)))
            S[gi, i] = float(np.mean(vals))
        if gi % 25 == 0: print(f"  grid {gi}/{len(G)}", flush=True)
    return S

def aggregate(v):
    df = pd.DataFrame({"v": v}, index=assays).join(meta[["UniProt_ID","coarse_selection_type"]])
    g2 = df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean()
    return float(g2.groupby(level=1).mean().mean())

def nested_of(S):
    n = S.shape[1]
    out = np.empty(n)
    for i in range(n):
        others = (S.sum(axis=1) - S[:, i]) / (n-1)
        out[i] = S[int(np.argmax(others)), i]
    return out

res = {}
COLS_A = ["D","Kermut","AMK"]
COLS_B = COLS_A + ["X"]
GA, GB = grid(3), grid(4)
print("\nfitting pool A (3 experts, %d grid points)" % len(GA), flush=True)
SA = scores(COLS_A, GA)
print("fitting pool B (4 experts, %d grid points)" % len(GB), flush=True)
SB = scores(COLS_B, GB)

nA_o, nA_n = SA.max(axis=0), nested_of(SA)
nB_o, nB_n = SB.max(axis=0), nested_of(SB)

A_const, A_oracle = aggregate(nA_n), aggregate(nA_o)
B_const, B_oracle = aggregate(nB_n), aggregate(nB_o)
alloc = A_oracle - A_const
expert = B_const - A_const
print(f"\npool A  constant {A_const:.4f} | oracle {A_oracle:.4f} | allocation headroom {alloc:+.4f}", flush=True)
print(f"pool B  constant {B_const:.4f} | oracle {B_oracle:.4f} | its own headroom {B_oracle-B_const:+.4f}", flush=True)
print(f"expert gain (B constant - A constant) {expert:+.4f}", flush=True)
print(f"ratio allocation / expert gain = {alloc/expert:.2f}", flush=True)

# bootstrap over assays for both quantities
boots_a, boots_e = [], []
for _ in range(500):
    idx = rng.integers(0, len(assays), len(assays))
    sub = [assays[i] for i in idx]
    ms = meta.reindex(sub)
    def agg(v):
        df = pd.DataFrame({"v": v[idx]}, index=sub).join(ms[["UniProt_ID","coarse_selection_type"]])
        g2 = df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean()
        return float(g2.groupby(level=1).mean().mean())
    boots_a.append(agg(nA_o) - agg(nA_n))
    boots_e.append(agg(nB_n) - agg(nA_n))
la, ha = np.percentile(boots_a, [2.5, 97.5])
le, he = np.percentile(boots_e, [2.5, 97.5])
print(f"\nallocation  95% CI [{la:+.4f}, {ha:+.4f}]", flush=True)
print(f"expert gain 95% CI [{le:+.4f}, {he:+.4f}]", flush=True)

res = {"n_assays": len(assays), "pool_A": {"constant": A_const, "oracle": A_oracle},
       "pool_B": {"constant": B_const, "oracle": B_oracle},
       "allocation_headroom": alloc, "allocation_ci95": [float(la), float(ha)],
       "expert_gain": expert, "expert_ci95": [float(le), float(he)],
       "ratio": alloc/expert}
json.dump(res, open(f"{R}/one_pipeline.json", "w"), indent=2)
print("\nONE PIPELINE DONE", flush=True)
