"""Does accuracy-adjusting the disagreement improve its power to predict the gain?

2607.17384 reports that raw correctness correlation is a poor predictor of ensemble lift (R^2 <= 0.09) while an
accuracy-adjusted version reaches 0.67. The paper's predictor currently uses raw disagreement, so this builds
four candidates and compares them under identical leave-one-assay-out linear predictors of the oracle gain:

  raw       1 - mean pairwise |Spearman| between expert predictions          (current)
  skill     the same, weighting each pair by the product of the experts' own scores
  ambiguity variance of the experts' per-assay scores (the Krogh-Vedelsby term)
  residual  1 - mean pairwise |Spearman| between each expert's residual after regressing it on the pool

If the adjusted versions do not beat raw here, that is a result too: the adjustment may not survive a rank
metric, which is worth stating rather than assuming.
"""
import os, glob, itertools, json
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
COLS=["D","Kermut","AMK","X"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids); n=len(ids)
print("assays:", n, flush=True)

def sc(aid, w):
    v=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in COLS]
        v.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

G=grid(4); S=np.empty((len(G),n))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): S[gi,i]=sc(aid,w)
    if gi%60==0: print(f"  grid {gi}/{len(G)}", flush=True)
best=S.argmax(0); const=np.array([int(np.argmax((S.sum(1)-S[:,i])/(n-1))) for i in range(n)])
gain = S[best,np.arange(n)] - S[const,np.arange(n)]
print(f"oracle gain: median {np.median(gain):+.4f}", flush=True)

ns = np.array([sum(len(gs) for gs in units[aid]) for aid in ids])
feats = {k: np.zeros(n) for k in ("raw","skill","ambiguity","residual")}
for i,aid in enumerate(ids):
    # per-assay expert predictions and their own scores
    preds, scores = [], []
    for c in COLS:
        pv=[]; sv=[]
        for gs in units[aid]:
            pv.append(z(gs[c].to_numpy(float)))
            sv.append(sp(z(gs[c].to_numpy(float)), gs["y"].to_numpy(float)))
        preds.append(np.concatenate(pv)); scores.append(np.nanmean(sv))
    scores=np.array(scores); K=len(COLS)
    Rij=np.zeros((K,K))
    for a in range(K):
        for bb in range(a+1,K):
            Rij[a,bb]=Rij[bb,a]=abs(sp(preds[a],preds[bb]))
    iu=np.triu_indices(K,1)
    feats["raw"][i] = 1.0-np.nanmean(Rij[iu])
    wts=np.clip(scores-scores.min(),0,None)+1e-9
    ww=np.array([wts[a]*wts[bb] for a,bb in zip(*iu)])
    feats["skill"][i] = 1.0-np.nansum(ww*Rij[iu])/np.sum(ww)
    feats["ambiguity"][i] = float(np.nanvar(scores))
    # residuals after regressing each expert on the pool mean
    pool=np.mean(preds,axis=0)
    resid=[]
    for a in range(K):
        beta=np.polyfit(pool,preds[a],1)
        resid.append(preds[a]-np.polyval(beta,pool))
    rr=np.array([abs(sp(resid[a],resid[bb])) for a,bb in zip(*iu)])
    feats["residual"][i] = 1.0-np.nanmean(rr)

def loo_r(xf):
    F=np.column_stack([np.ones(n), xf, np.log(ns)])
    pred=np.empty(n)
    for i in range(n):
        tr=[j for j in range(n) if j!=i]
        beta,*_=np.linalg.lstsq(F[tr],gain[tr],rcond=None)
        pred[i]=F[i]@beta
    return sp(pred,gain)

print(f"\n{'predictor':28s} {'LOO r':>8s}")
rows={}
for k,f in feats.items():
    r1 = sp(gain, f)
    r2 = loo_r(f)
    rows[k]={"direct_r":float(r1),"loo_r":float(r2)}
    print(f"  {k:26s} {r1:+8.3f}   LOO predictor r = {r2:+.3f}", flush=True)
# combined: raw + ambiguity
both=feats["raw"]+feats["ambiguity"]
rows["raw+ambiguity"]={"direct_r":float(sp(gain,both)),"loo_r":float(loo_r(both))}
print(f"  {'raw+ambiguity':26s} {sp(gain,both):+8.3f}   LOO predictor r = {loo_r(both):+.3f}", flush=True)
json.dump(rows, open(f"{R}/adjdiv.json","w"), indent=2)
print("ADJDIV DONE", flush=True)
