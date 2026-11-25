"""Is the allocation headroom a property of the pool, or of the metric we happened to optimise?

Every oracle in this paper maximises Spearman. The paper's own section 5 argues that aggregate Spearman is not a
deployment specification and that top-of-list recall is what a campaign experiences. If the headroom is much larger
under top-k than under Spearman, then the "42%" is an artefact of the objective, not a property of the experts --
which is the paper's own thesis turned on itself.

Per assay, for every weight vector on the simplex: top-k recall (fraction of the true top k that the predicted top
k recovers). Then the usual LOO constant and per-assay oracle, aggregated the official way.
"""
import os
import os, itertools, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"
KPCT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05

def z(a):
    a=np.asarray(a,np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.std()==0 or b.std()==0: return np.nan
    return spearmanr(a,b).correlation
def grid(k,step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])
def topk_recall(pred, y, frac):
    m=len(y); k=max(1,int(round(frac*m)))
    pi=np.argsort(-np.asarray(pred))[:k]; ti=set(np.argsort(-np.asarray(y))[:k].tolist())
    return len(set(pi.tolist()) & ti)/k

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
m = m.dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS=["D","Kermut","AMK","X"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids); n=len(ids)
print(f"top-k fraction {KPCT} | assays {n}", flush=True)

def metric(aid, w, kind):
    v=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in COLS]
        blend=sum(a*c for a,c in zip(w,Zm))
        v.append(topk_recall(blend, gs["y"].to_numpy(float), KPCT) if kind=="topk"
                 else sp(blend, gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

G=grid(4)
S=np.empty((len(G),n))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): S[gi,i]=metric(aid,w,"topk")
    if gi%80==0: print(f"  grid {gi}/{len(G)}", flush=True)
orc=S.max(0); ci=np.array([int(np.argmax((S.sum(1)-S[:,i])/(n-1))) for i in range(n)])
cst=S[ci,np.arange(n)]
print(f"\ntop-k recall @ {KPCT:.0%}: constant {agg(cst):.4f} | oracle {agg(orc):.4f} | headroom {agg(orc)-agg(cst):+.4f}", flush=True)

# how much does the Spearman-optimal weight cost in top-k?
Spr=np.empty((len(G),n))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): Spr[gi,i]=metric(aid,w,"spearman")
sp_best=Spr.argmax(0)
sp_ci=np.array([int(np.argmax((Spr.sum(1)-Spr[:,i])/(n-1))) for i in range(n)])
topk_of_sp = S[sp_best, np.arange(n)]
topk_of_spc = S[sp_ci, np.arange(n)]
print(f"top-k with the SPEARMAN-optimal per-assay weights: {agg(topk_of_sp):.4f}", flush=True)
print(f"top-k with the SPEARMAN-optimal constant       : {agg(topk_of_spc):.4f}", flush=True)
print(f"captured by Spearman-optimal weights: {(agg(topk_of_sp)-agg(topk_of_spc))/(agg(orc)-agg(cst)):.1%} of the top-k headroom", flush=True)
json.dump({"frac":KPCT,"constant":agg(cst),"oracle":agg(orc),"headroom":agg(orc)-agg(cst),
           "topk_of_spearman_oracle":agg(topk_of_sp),"topk_of_spearman_constant":agg(topk_of_spc),
           "captured":(agg(topk_of_sp)-agg(topk_of_spc))/(agg(orc)-agg(cst))},
          open(f"{R}/topk_oracle_{int(KPCT*100)}.json","w"), indent=2)
print(f"TOPK {KPCT} DONE", flush=True)
