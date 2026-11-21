"""A gate on the variance axis: predict how much to trust the local estimate, not which expert to pick.

Every gating layer in this literature outputs a weight vector over experts. The paper's own measurements say
that axis is nearly exhausted and that the binding constraint is estimation error. So the alternative
architecture gates on the shrinkage coefficient instead:

    lambda_i = gate(n_i, disagreement_i, ...)        learned from assay statistics
    w(lam)   = (1 - lam) * w_panel + lam * w_i

Compared against: the constant, unregularised per-assay fitting, the tuned k, the derived empirical-Bayes
lambda, and the learned gate. Target for the gate is each assay's own out-of-sample optimal lambda, fitted
leave-one-assay-out so the reported number never sees the assay it is scored on.
"""
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
rng = np.random.default_rng(0)
LAMS = np.linspace(0, 1, 11)

def z(a):
    a=np.asarray(a,np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.std()==0 or b.std()==0: return np.nan
    return spearmanr(a,b).correlation
def grid(k,step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

def analyse(name, units, meta, G):
    ids=list(meta["id"]); n=len(units); mi=meta.set_index("id")
    def agg(v):
        df=pd.DataFrame({"v":v},index=ids).join(mi[["UniProt_ID","coarse_selection_type"]])
        return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())
    def split_all():
        for u in units:
            for X,y,half in u:
                half[0], half[1] = np.array_split(rng.permutation(len(y)), 2)
    def sc(i, w, h):
        vals=[]
        for X,y,half in units[i]:
            idx=half[h]; Xa=X[idx]; ya=y[idx]
            Zm=[z(Xa[:,j]) for j in range(Xa.shape[1])]
            vals.append(sp(sum(a*c for a,c in zip(w,Zm)), ya))
        return float(np.nanmean(vals))

    ns = np.array([sum(len(t[1]) for t in u) for u in units])
    # assay statistics that a gate could read before fitting anything
    D, spread = [], []
    for i in range(n):
        X0 = max(units[i], key=lambda t: len(t[1]))[0]
        pr = [z(X0[:, j]) for j in range(X0.shape[1])]
        pair = [abs(sp(pr[a], pr[b])) for a in range(len(pr)) for b in range(a+1, len(pr))]
        D.append(1.0 - np.mean(pair))
        sc0 = [sp(pr[j], max(units[i], key=lambda t: len(t[1]))[1]) for j in range(len(pr))]
        spread.append(float(np.std(sc0)))
    D = np.array(D); spread = np.array(spread)

    # target: each assay's own out-of-sample optimal lambda, averaged over splits
    lam_star = np.full(n, np.nan)
    REPS = 3
    acc = np.zeros((n, len(LAMS))); cnt = np.zeros(n)
    for rep in range(REPS):
        split_all()
        W_A = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
        wg  = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
        for i in range(n):
            for li, lam in enumerate(LAMS):
                acc[i, li] += sc(i, (1-lam)*wg + lam*W_A[i], 1)
            cnt[i] += 1
        print(f"  [{name}] target rep {rep+1}/{REPS}", flush=True)
    acc /= cnt[:,None]
    lam_star = LAMS[np.argmax(acc, axis=1)]

    # leave-one-assay-out ridge from assay statistics to the optimal lambda
    F = np.column_stack([np.ones(n), D, np.log(ns), spread, D*np.log(ns)])
    lam_hat = np.empty(n)
    for i in range(n):
        tr=[j for j in range(n) if j!=i]
        beta,*_ = np.linalg.lstsq(F[tr], lam_star[tr], rcond=None)
        lam_hat[i] = float(np.clip(F[i] @ beta, 0, 1))
    print(f"[{name}] lambda* median {np.median(lam_star):.2f} | gate corr with lambda* {sp(lam_hat, lam_star):+.3f}")

    # empirical-Bayes lambda from variance components
    Wr = np.zeros((REPS, n, G.shape[1]))
    for rep in range(REPS):
        split_all()
        for i in range(n):
            Wr[rep, i] = max(G, key=lambda w: sc(i,w,0))
    wbar = Wr.mean(0)
    sigma2 = ((Wr - wbar[None])**2).mean(axis=(0,2))
    tau2 = max(wbar.var(axis=0).mean() - sigma2.mean(), 1e-6)
    lam_eb = tau2/(tau2+sigma2)

    # evaluate every rule on one fresh split
    split_all()
    W_A = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
    wg  = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
    g_const = np.array([sc(i,wg,1) for i in range(n)])
    def rule(lam): return np.array([sc(i,(1-lam[i])*wg + lam[i]*W_A[i],1) for i in range(n)]) - g_const
    out = {"constant": agg(g_const)}
    out["per_assay"] = agg(rule(np.ones(n)) + g_const)
    for k in (10,30,100,300,1000):
        out[f"tuned_k{k}"] = agg(rule(ns/(ns+k)) + g_const)
    out["EB"] = agg(rule(lam_eb) + g_const)
    out["GATE"] = agg(rule(lam_hat) + g_const)
    for kk,vv in out.items(): print(f"[{name}]   {kk:12s} {vv:.4f}")
    print(f"[{name}] gate beats EB by {out['GATE']-out['EB']:+.4f}", flush=True)
    return {"n":n, "lam_star_median":float(np.median(lam_star)),
            "gate_corr":float(sp(lam_hat, lam_star)), "lam_eb_median":float(np.median(lam_eb)),
            **{k:float(v) for k,v in out.items()}}

results={}
A=f"{R}/cytolex-aakg-ablation-1103-v1"
b=pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x=pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m=b.merge(x[["assay","scheme","variant_id","X"]],on=["assay","scheme","variant_id"],how="inner").dropna(subset=["D","Kermut","AMK","X","y"])
ref=pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS=["D","Kermut","AMK","X"]; units,meta=[],[]
for aid,g in m.groupby("assay"):
    per=[[gs[COLS].to_numpy(float), gs["y"].to_numpy(float), None] for _,gs in g.groupby("scheme") if len(gs)>=20]
    if not per: continue
    for t in per: t[2]=[np.arange(len(t[1])),np.arange(len(t[1]))]
    units.append(per); meta.append({"id":aid, **ref.loc[aid,["UniProt_ID","coarse_selection_type"]].to_dict()})
results["substitutions"]=analyse("substitutions",units,pd.DataFrame(meta),grid(4))

W=f"{R}/indel-benchmark-1119"; units,meta=[],[]
iref=pd.read_csv(f"{W}/data/DMS_indels_ref.csv").set_index("DMS_id")
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid=os.path.basename(f)[:-4]
    bench=pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag=f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo=pd.read_csv(frag)[["mutated_sequence","fold_random_5"]]
    mm=bench.reset_index().merge(fo,on="mutated_sequence",how="left").sort_values("index")
    if mm.fold_random_5.isna().any(): continue
    z0=np.load(f,allow_pickle=True); y,P=z0["y"],z0["P"]
    if len(y)!=len(bench): continue
    ok=np.isfinite(y)
    units.append([[P[ok],y[ok],[np.arange(ok.sum()),np.arange(ok.sum())]]])
    meta.append({"id":aid,"UniProt_ID":iref.loc[aid,"UniProt_ID"],"coarse_selection_type":"all"})
results["indels"]=analyse("indels",units,pd.DataFrame(meta),grid(3))
json.dump(results,open(f"{R}/sgate.json","w"),indent=2)
print("\nSGATE DONE", flush=True)
