"""Map the competence floor: where does pushing an expert's disagreement stop paying?

The paper states the design objective as "maximise residual disagreement subject to a competence floor" and gives
only two points either side of it. This sweeps an axis finely and reports the whole frontier: standalone accuracy,
disagreement with the pool, and the expert's marginal value to the fusion, at every step.

Two axes, run as separate jobs so the shape is not an artefact of one construction:
  residual   m(beta) = z(X) - beta * z(pool)     subtracts the pool's own component
  noise      m(eps)  = z(X) + eps * N(0,1)       degrades accuracy without touching the pool direction
"""
import os, itertools, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
AXIS = sys.argv[1] if len(sys.argv) > 1 else "residual"
STEPS = [round(x, 2) for x in np.arange(0, 2.01, 0.125)]
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
POOL=["D","Kermut","AMK"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs.copy() for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids); n=len(ids)
print(f"axis={AXIS} | assays={n}", flush=True)

def sc(aid, cols, w):
    v=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in cols]
        v.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

G3, G4 = grid(3), grid(4)
S3=np.empty((len(G3),n))
for gi,w in enumerate(G3):
    for i,aid in enumerate(ids): S3[gi,i]=sc(aid,POOL,w)
const_idx=np.array([int(np.argmax((S3.sum(1)-S3[:,i])/(n-1))) for i in range(n)])
base=agg(S3[const_idx,np.arange(n)])
print(f"pool constant {base:.4f}", flush=True)

rows=[]
for step in STEPS:
    for i,aid in enumerate(ids):
        for gs in units[aid]:
            ex=z(gs["X"].to_numpy(float))
            P=sum(wt*z(gs[c].to_numpy(float)) for c,wt in zip(POOL, G3[const_idx[i]]))
            if AXIS=="residual":   gs["M"] = ex - step*P
            else:                  gs["M"] = ex + step*rng.normal(size=len(ex))
    solo = agg(np.array([sc(aid,["M"],np.array([1.0])) for aid in ids]))
    dis = float(np.nanmean([1.0-abs(sp(
        np.concatenate([z(gs["M"].to_numpy(float)) for gs in units[aid]]),
        np.concatenate([sum(wt*z(gs[c].to_numpy(float)) for c,wt in zip(POOL,G3[const_idx[i]])) for gs in units[aid]])))
        for i,aid in enumerate(ids)]))
    SA=np.empty((len(G4),n))
    for gi,w in enumerate(G4):
        for i,aid in enumerate(ids): SA[gi,i]=sc(aid,POOL+["M"],w)
    orc=SA.max(0); cst=np.array([SA[int(np.argmax((SA.sum(1)-SA[:,i])/(n-1))),i] for i in range(n)])
    gain=agg(orc)-agg(cst)
    rows.append({"step":step,"solo":solo,"disagreement":dis,"gain":gain,"oracle":agg(orc)})
    print(f"  {AXIS} {step:.3f}: solo {solo:+.4f} | disagreement {dis:.3f} | oracle {agg(orc):.4f} | gain {gain:+.4f}", flush=True)

best=max(rows,key=lambda r:r["gain"])
print(f"\nBEST {AXIS}: step {best['step']:.3f} | solo {best['solo']:+.4f} | gain {best['gain']:+.4f}")
print(f"at step 0: gain {rows[0]['gain']:+.4f} (solo {rows[0]['solo']:.4f})")
print(f"headroom above step 0: {best['gain']-rows[0]['gain']:+.4f}")
json.dump(rows, open(f"{R}/frontier_{AXIS}.json","w"), indent=2)
print(f"FRONTIER {AXIS.upper()} DONE", flush=True)
