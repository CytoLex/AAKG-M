"""Null control for the pooling claim, using the real derived lambda.

The conformance run tested pooling with a crude stand-in for lambda and found that permuting it did no harm,
which invalidates that stand-in rather than the claim. This reruns the control with the actual estimator:
sigma_i^2 from repeated half-splits, tau^2 as total variance minus mean sampling variance, lambda_i =
tau^2/(tau^2 + sigma_i^2). The null permutes those lambdas across assays, which preserves the distribution and
destroys the alignment with each assay's sample size.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)
REPS = 4

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
G=grid(4)

def sc(aid,w,half=None):
    v=[]
    for gs in units[aid]:
        if half is not None:
            gs = gs.iloc[half]
        Zm=[z(gs[c].to_numpy(float)) for c in COLS]
        v.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(v))
def agg(v):
    df=pd.DataFrame({"v":v},index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

# variance components from repeated half-splits on half A
W=np.zeros((REPS,n,len(COLS)))
for r in range(REPS):
    for aid in ids:
        for gs in units[aid]:
            gs.attrs["half"] = None
    halves={}
    for aid in ids:
        halves[aid]=[np.array_split(rng.permutation(len(gs)),2) for gs in units[aid]]
    for i,aid in enumerate(ids):
        best=None; bs=-9
        for w in G:
            v=[]
            for gs,hh in zip(units[aid],halves[aid]):
                gg=gs.iloc[hh[0]]
                Zm=[z(gg[c].to_numpy(float)) for c in COLS]
                v.append(sp(sum(a*c for a,c in zip(w,Zm)), gg["y"].to_numpy(float)))
            s=float(np.nanmean(v))
            if s>bs: bs=s; best=w
        W[r,i]=best
    print(f"  rep {r+1}/{REPS}", flush=True)
wbar=W.mean(0)
sigma2=((W-wbar[None])**2).mean(axis=(0,2))
tau2=max(wbar.var(axis=0).mean()-sigma2.mean(), 1e-6)
lam=tau2/(tau2+sigma2)
print(f"tau^2 {tau2:.5f} | mean sigma^2 {sigma2.mean():.5f} | lambda median {np.median(lam):.3f}", flush=True)

# score matrix for the constant and the per-assay best, on full data
S=np.empty((len(G),n))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): S[gi,i]=sc(aid,w)
best=S.argmax(0); const=np.array([int(np.argmax((S.sum(1)-S[:,i])/(n-1))) for i in range(n)])
base=agg(S[const,np.arange(n)])
print(f"constant {base:.4f}", flush=True)

def pooled(lv):
    return np.array([sc(ids[i], (1-lv[i])*G[const[i]] + lv[i]*G[best[i]]) for i in range(n)])
real=agg(pooled(lam))
print(f"pooling, derived lambda : {real:.4f}  (gain {real-base:+.4f})", flush=True)
perm=[]
for _ in range(20):
    perm.append(agg(pooled(lam[rng.permutation(n)]))-base)
lo,hi=np.percentile(perm,[2.5,97.5])
print(f"NULL pooling, lambda permuted: {np.mean(perm):+.4f} [{lo:+.4f}, {hi:+.4f}]", flush=True)
print(f"real gain minus null: {(real-base)-np.mean(perm):+.4f}", flush=True)
json.dump({"tau2":float(tau2),"lam_median":float(np.median(lam)),"real":real,"base":base,
           "null":float(np.mean(perm)),"null_ci":[float(lo),float(hi)]},
          open(f"{R}/poolctl.json","w"), indent=2)
print("POOLCTL DONE", flush=True)
