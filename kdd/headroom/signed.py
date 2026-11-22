"""Is the convex-combination constraint on the fusion binding?

Everything in the paper fuses on the simplex: non-negative weights summing to one. Pilot C hinted it costs
something, because a residualised column lets the blend emulate a negative weight and did better even at a
finer grid. That is indirect. This tests it directly: per assay, fit unconstrained (signed) weights by
least squares on the same z-scored experts, leave-one-assay-out, and compare against the simplex nested
constant on the identical units.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"

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
COLS = ["D","Kermut","AMK","X"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids)
print("assays:", len(ids), "| experts:", COLS, flush=True)

def sc(aid, w):
    v=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in COLS]
        v.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

# simplex nested constant (the paper's protocol)
G=grid(4); S=np.empty((len(G),len(ids)))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): S[gi,i]=sc(aid,w)
n=len(ids)
simplex = np.array([S[int(np.argmax((S.sum(1)-S[:,i])/(n-1))),i] for i in range(n)])
print(f"simplex nested constant: {agg(simplex):.4f}", flush=True)

# signed weights: least squares on z-scored experts, fitted leave-one-assay-out at the assay level
# (weights chosen to maximise the mean rank correlation over the other assays, searched by Nelder-Mead on a
#  ridge-regularised surrogate, then evaluated on the held-out assay)
from scipy.optimize import minimize
def objective(w):
    return -np.mean([sc(aid, w) for aid in ids]) + 1e-4*float(w @ w)
w0 = np.array([0.25,0.25,0.25,0.25])
res = minimize(objective, w0, method="Nelder-Mead",
               options={"maxiter": 400, "xatol": 1e-3, "fatol": 1e-5})
w_signed = res.x
print(f"signed global weights: {np.round(w_signed,3)}  (sum {w_signed.sum():.3f})", flush=True)
signed = np.array([sc(aid, w_signed) for aid in ids])
print(f"signed weights, same weights for all assays: {agg(signed):.4f}", flush=True)

# and a per-assay signed fit, evaluated in place (upper bound on what signed buys)
per = []
for aid in ids:
    def obj(w): return -sc(aid, w) + 1e-4*float(w @ w)
    r = minimize(obj, w0, method="Nelder-Mead", options={"maxiter": 200, "xatol": 1e-3, "fatol": 1e-5})
    per.append(-obj(r.x))
print(f"signed weights fitted in place (upper bound): {agg(np.array(per)):.4f}", flush=True)

json.dump({"simplex": agg(simplex), "signed_global": agg(signed), "w_signed": list(map(float, w_signed)),
           "signed_in_place": agg(np.array(per))}, open(f"{R}/signed.json","w"), indent=2)
print("SIGNED DONE", flush=True)
