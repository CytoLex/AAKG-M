"""Is the value of per-assay weighting predictable from the assay, before you fit it?

Per assay: how much the experts disagree, and how many variants the assay has. Does either explain the oracle
gain, and does a rule built on them beat always-weighting and never-weighting?

Efficiency: one score matrix S[grid, assay], then the oracle and the leave-one-out constant are both derived
from it. Computing the constant inside a per-assay loop made the previous attempt O(n^2 * grid) and it did not
finish in an hour; this is O(grid * n).
"""
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
def z(a):
    a = np.asarray(a, dtype=np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.std()==0 or b.std()==0: return np.nan
    return spearmanr(a,b).correlation
def grid(k, step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

def analyse(name, units, meta, G):
    ids=list(meta["id"]); n=len(units); mi=meta.set_index("id")
    def agg(v):
        df=pd.DataFrame({"v":v},index=ids).join(mi[["UniProt_ID","coarse_selection_type"]])
        return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())
    Zs = [[[z(t[0][:,j]) for j in range(t[0].shape[1])] for t in units[i]] for i in range(n)]
    def blended(i, w):
        return float(np.nanmean([sp(sum(a*c for a,c in zip(w, Zi)), t[1]) for Zi,t in zip(Zs[i], units[i])]))
    print(f"[{name}] building score matrix: {len(G)} x {n}", flush=True)
    S = np.empty((len(G), n))
    for gi, w in enumerate(G):
        for i in range(n):
            S[gi, i] = blended(i, w)
    oracle = S.max(axis=0)
    wc_idx = np.array([int(np.argmax((S.sum(axis=1) - S[:, i]) / (n-1))) for i in range(n)])
    constv = S[wc_idx, np.arange(n)]
    gain = oracle - constv

    ns = np.array([sum(len(t[1]) for t in u) for u in units])
    D = np.array([1.0 - np.mean([abs(sp(zr[a], zr[b])) for a in range(len(zr)) for b in range(a+1, len(zr))])
                  for zr in [[z(max(units[i], key=lambda t: len(t[1]))[0][:, j]) for j in range(units[i][0][0].shape[1])] for i in range(n)]])
    print(f"\n=== {name}: {n} assays ===")
    print(f"  disagreement {D.min():.3f} .. {D.max():.3f} (median {np.median(D):.3f})")
    print(f"  oracle gain  {gain.min():+.4f} .. {gain.max():+.4f} (median {np.median(gain):+.4f})")
    print(f"  corr(gain, disagreement)   r = {sp(gain, D):+.3f}")
    print(f"  corr(gain, log n)          r = {sp(gain, np.log(ns)):+.3f}")
    print(f"  corr(gain, D * n/(n+100))  r = {sp(gain, D*ns/(ns+100)):+.3f}", flush=True)

    Xd = np.column_stack([np.ones(n), D, np.log(ns)])
    pred = np.empty(n)
    for i in range(n):
        tr=[j for j in range(n) if j!=i]
        beta,*_ = np.linalg.lstsq(Xd[tr], gain[tr], rcond=None)
        pred[i] = Xd[i] @ beta
    print(f"  LOO predictor r = {sp(pred, gain):+.3f}", flush=True)
    rule = np.where(pred > 0, oracle, constv)
    print(f"  aggregate: never {agg(constv):.4f} | always {agg(oracle):.4f} | rule {agg(rule):.4f}"
          f" | rule weights {(pred>0).mean():.0%}", flush=True)
    return {"n":n, "corr_D":float(sp(gain,D)), "corr_logn":float(sp(gain,np.log(ns))),
            "corr_both":float(sp(gain, D*ns/(ns+100))), "loo_r":float(sp(pred,gain)),
            "agg_never":agg(constv), "agg_always":agg(oracle), "agg_rule":agg(rule),
            "frac":float((pred>0).mean())}

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
json.dump(results,open(f"{R}/predict.json","w"),indent=2)
print("\nPREDICT DONE", flush=True)
