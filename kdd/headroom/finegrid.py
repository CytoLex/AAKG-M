"""Is pilot C's extra +0.0014 real, or grid resolution?

Pool P plus an extra column c spans the blends {(1-w)P + w*c}. For c = X that is {(1-w)P + wX}. For
c = X - 1.25P it is {(1-w-1.25w)P + wX} -- the same family, reparametrised, so the achievable set is
identical and any difference must come from where the discrete simplex lands. Refining the step decides it:
if both columns converge to the same value, the beta headroom was discretisation.
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
def grid(k,step):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
m = m.dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
POOL=["D","Kermut","AMK"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs.copy() for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids)
print("assays:", len(ids), flush=True)

def sc(aid, cols, w):
    v=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in cols]
        v.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())
def nested(cols, step):
    G=grid(len(cols), step); S=np.empty((len(G),len(ids)))
    for gi,w in enumerate(G):
        for i,aid in enumerate(ids): S[gi,i]=sc(aid,cols,w)
    n=len(ids)
    return agg(np.array([S[int(np.argmax((S.sum(1)-S[:,i])/(n-1))),i] for i in range(n)]))

for step in (0.1, 0.05):
    print(f"\n--- grid step {step} ({len(grid(4,step))} points) ---", flush=True)
    # plain X
    for gs in [  ]: pass
    for aid in ids:
        for gs in units[aid]: gs["XA"] = gs["X"].to_numpy(float)
    print(f"  pool + X          : {nested(POOL+['XA'], step):.4f}", flush=True)
    # beta = 1.25 residualised column, needs the pool blend per assay
    wpool = {}
    G3 = grid(3, step)
    S3 = np.empty((len(G3), len(ids)))
    for gi,w in enumerate(G3):
        for i,aid in enumerate(ids): S3[gi,i]=sc(aid,POOL,w)
    n=len(ids)
    for i,aid in enumerate(ids):
        wpool[aid] = G3[int(np.argmax((S3.sum(1)-S3[:,i])/(n-1)))]
    for aid in ids:
        for gs in units[aid]:
            P = sum(wt*z(gs[c].to_numpy(float)) for c,wt in zip(POOL, wpool[aid]))
            gs["XB"] = z(gs["X"].to_numpy(float)) - 1.25*P
    print(f"  pool + (X-1.25P)  : {nested(POOL+['XB'], step):.4f}", flush=True)
print("\nFG DONE", flush=True)
