"""Control for the grid-size confound.

Adding a column to a nested weight search enlarges the simplex that the leave-one-assay-out selection picks
from, so a useless column can still show a positive "marginal gain". If that bias grows with how orthogonal
the column is, it manufactures exactly the disagreement-value correlation the pilots reported. So the same
protocol is run with columns that carry no signal: pure noise, a shuffled copy of our expert (identical
marginal distribution, no signal), and the negated expert.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)

def z(a):
    a=np.asarray(a,np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.std()==0 or b.std()==0: return np.nan
    return spearmanr(a,b).correlation
def grid(k,step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
m = m.dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
POOL = ["D","Kermut","AMK"]
units = {}
for aid, g in m.groupby("assay"):
    per = [gs.copy() for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per: units[aid] = per
ids = sorted(units); meta = ref.reindex(ids)
print("assays:", len(ids), flush=True)

def sc_cols(aid, cols, w):
    vals=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in cols]
        vals.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(vals))

def agg(v):
    df = pd.DataFrame({"v": v}, index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

def nested(cols):
    G = grid(len(cols))
    S = np.empty((len(G), len(ids)))
    for gi,w in enumerate(G):
        for i,aid in enumerate(ids):
            S[gi,i] = sc_cols(aid, cols, w)
    n = len(ids)
    return agg(np.array([S[int(np.argmax((S.sum(1)-S[:,i])/(n-1))), i] for i in range(n)]))

base = nested(POOL)
print(f"pool baseline {base:.4f}", flush=True)

# build candidate extra columns, each standardised within assay-scheme
def make(name, kinds):
    for aid in ids:
        for gs in units[aid]:
            n = len(gs)
            if kinds == "noise":     v = rng.normal(size=n)
            elif kinds == "shuffle": v = rng.permutation(gs["X"].to_numpy(float))
            elif kinds == "negate":  v = -gs["X"].to_numpy(float)
            elif kinds == "real":    v = gs["X"].to_numpy(float)
            gs[name] = v
    return name

for label, kind in (("noise","noise"), ("shuffle","shuffle"), ("negate","negate"), ("real","real")):
    col = f"Z_{label}"
    make(col, kind)
    full = nested(POOL + [col])
    dis = []
    for aid in ids:
        pz = np.concatenate([z(gs[col].to_numpy(float)) for gs in units[aid]])
        pp = np.concatenate([np.mean([z(gs[c].to_numpy(float)) for c in POOL], axis=0) for gs in units[aid]])
        dis.append(1.0 - abs(sp(pz, pp)))
    solo = agg(np.array([sc_cols(aid, [col], np.array([1.0])) for aid in ids]))
    print(f"  add {label:8s}: solo {solo:+.4f} | disagreement {np.nanmean(dis):.3f} "
          f"| pool {full:.4f} | apparent marginal {full-base:+.4f}", flush=True)
print("\nIf noise and shuffle show apparent marginals near the real one, the pilots measured grid expansion,\n"
      "not expert value.", flush=True)
print("CONTROL DONE", flush=True)
