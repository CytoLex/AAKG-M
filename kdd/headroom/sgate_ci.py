"""Is the learned shrinkage gate actually better than the closed form?

Per-assay scores are saved for every rule and compared on the same split (paired), then two uncertainties:
across fresh splits, and a bootstrap over assays with the official re-aggregation inside each resample.
"""
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
rng = np.random.default_rng(0)
LAMS = np.linspace(0, 1, 11)
NSPLIT = 5

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
    def agg(v, idx=None):
        idx = np.arange(len(ids)) if idx is None else idx
        df=pd.DataFrame({"v":np.asarray(v)[idx]},index=[ids[i] for i in idx]).join(mi[["UniProt_ID","coarse_selection_type"]])
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
    D, spread = [], []
    for i in range(n):
        X0 = max(units[i], key=lambda t: len(t[1]))[0]
        y0 = max(units[i], key=lambda t: len(t[1]))[1]
        pr = [z(X0[:, j]) for j in range(X0.shape[1])]
        pair = [abs(sp(pr[a], pr[b])) for a in range(len(pr)) for b in range(a+1, len(pr))]
        D.append(1.0 - np.mean(pair)); spread.append(float(np.std([sp(p, y0) for p in pr])))
    D = np.array(D); spread = np.array(spread)

    # target lambda*, and variance components for the EB rule
    acc = np.zeros((n, len(LAMS))); cnt = 0
    Wr = []
    for rep in range(3):
        split_all()
        W_A = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
        Wr.append(np.array(W_A))
        wg  = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
        for i in range(n):
            for li, lam in enumerate(LAMS):
                acc[i, li] += sc(i, (1-lam)*wg + lam*W_A[i], 1)
        cnt += 1
        print(f"  [{name}] target rep {rep+1}/3", flush=True)
    acc /= cnt
    lam_star = LAMS[np.argmax(acc, axis=1)]
    Wr = np.array(Wr); wbar = Wr.mean(0)
    sigma2 = ((Wr - wbar[None])**2).mean(axis=(0,2))
    tau2 = max(wbar.var(axis=0).mean() - sigma2.mean(), 1e-6)
    lam_eb = tau2/(tau2+sigma2)
    F = np.column_stack([np.ones(n), D, np.log(ns), spread, D*np.log(ns)])
    lam_hat = np.empty(n)
    for i in range(n):
        tr=[j for j in range(n) if j!=i]
        beta,*_ = np.linalg.lstsq(F[tr], lam_star[tr], rcond=None)
        lam_hat[i] = float(np.clip(F[i] @ beta, 0, 1))

    RULES = {"per_assay": np.ones(n), "tuned_k300": ns/(ns+300), "EB": lam_eb, "GATE": lam_hat}
    per_rule = {k: np.zeros((NSPLIT, n)) for k in RULES}
    for s in range(NSPLIT):
        split_all()
        W_A = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
        wg  = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
        for k_, lam in RULES.items():
            per_rule[k_][s] = [sc(i, (1-lam[i])*wg + lam[i]*W_A[i], 1) for i in range(n)]
        print(f"  [{name}] split {s+1}/{NSPLIT}", flush=True)

    mean_per_assay = {k_: v.mean(0) for k_, v in per_rule.items()}
    across = {k_: float(np.std([agg(per_rule[k_][s]) for s in range(NSPLIT)])) for k_ in RULES}
    print(f"\n=== {name} ({n} assays) ===")
    for k_ in ("GATE","EB","tuned_k300","per_assay"):
        print(f"  {k_:12s} {agg(mean_per_assay[k_]):.4f}  (split sd {across[k_]:.5f})")

    NB = 2000
    diffs = {}
    for a_, b_ in (("GATE","EB"), ("GATE","tuned_k300"), ("GATE","per_assay")):
        ds = []
        for _ in range(NB):
            idx = rng.integers(0, n, n)
            ds.append(agg(mean_per_assay[a_], idx) - agg(mean_per_assay[b_], idx))
        lo, hi = np.percentile(ds, [2.5, 97.5])
        frac_pos = float(np.mean(np.array(ds) > 0))
        diffs[f"{a_}_minus_{b_}"] = {"mean": float(np.mean(ds)), "ci95": [float(lo), float(hi)],
                                     "frac_positive": frac_pos}
        print(f"  {a_} - {b_}: {np.mean(ds):+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  "
              f"P({a_}>{b_}) = {frac_pos:.2f}", flush=True)
    return {"n": n, "lam_star_median": float(np.median(lam_star)),
            "agg": {k_: agg(mean_per_assay[k_]) for k_ in RULES},
            "split_sd": across, "diffs": diffs}

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
json.dump(results,open(f"{R}/sgate_ci.json","w"),indent=2)
print("\nSGATE CI DONE", flush=True)
