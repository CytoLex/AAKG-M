"""One protocol for the oracle, the estimability test and the pooling fix.

Earlier runs fitted the reference constant on full data in one place and on half data in another, which made
the transfer fractions disagree. Here every quantity is computed from the same halves:

  in-place oracle gain   O_A - C_A      weights fitted on half A and scored on half A
  estimable transfer     P_A->B - C_B   same weights, scored on the untouched half B
  shrinkage              S_A->B - C_B   pooled weights, scored on B

where C is the constant fitted on half A of the other assays, and shrinkage strength is lambda = n/(n+k).
"""
import os
import itertools, json, glob, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
rng = np.random.default_rng(0); REPS = 5; KS = [10, 30, 100, 300, 1000]

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b): return spearmanr(a,b).correlation
def grid(k, step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

def run(name, units, meta, G):
    meta_idx = meta.set_index("id"); ids = list(meta["id"]); n = len(units)
    def agg(v):
        df = pd.DataFrame({"v": v}, index=ids).join(meta_idx[["UniProt_ID","coarse_selection_type"]])
        return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())
    def sc(i, w, h):
        vals=[]
        for X,y,half in units[i]:
            idx = half[h]; Xa=X[idx]; ya=y[idx]
            Zm=[z(Xa[:,j]) for j in range(Xa.shape[1])]
            vals.append(sp(sum(a*c for a,c in zip(w,Zm)), ya))
        return float(np.mean(vals))
    acc = {kk: [] for kk in ("oracle_A","const_A","const_B","per_B","shr_B")}
    bestk = []
    for rep in range(REPS):
        for u in units:
            for X,y,half in u:
                half[0], half[1] = np.array_split(rng.permutation(len(y)), 2)
        WA = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
        wg = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
        ns = np.array([sum(len(t[1]) for t in u) for u in units])
        oA=[sc(i,WA[i],0) for i in range(n)]; cA=[sc(i,wg,0) for i in range(n)]
        cB=[sc(i,wg,1) for i in range(n)]; pB=[sc(i,WA[i],1) for i in range(n)]
        acc["oracle_A"].append(agg(np.array(oA)-np.array(cA)))
        acc["const_A"].append(agg(np.array(cA))); acc["const_B"].append(agg(np.array(cB)))
        acc["per_B"].append(agg(np.array(pB))-agg(np.array(cB)))
        scores={}
        for k in KS:
            lam = ns/(ns+k)
            vals=[sc(i,(1-lam[i])*wg+lam[i]*WA[i],1) for i in range(n)]
            scores[k]=agg(np.array(vals))-agg(np.array(cB))
            acc["shr_B"].append(scores[k])
        bestk.append(max(KS, key=lambda kk: scores[kk]))
        print(f"  rep {rep} done", flush=True)
    out = {"n": n,
           "in_place_oracle": float(np.mean(acc["oracle_A"])),
           "estimable_transfer": float(np.mean(acc["per_B"])),
           "best_k": int(max(set(bestk), key=bestk.count))}
    # recompute shrinkage per k cleanly
    shr = {}
    for j,k in enumerate(KS):
        shr[str(k)] = float(np.mean([acc["shr_B"][i*len(KS)+j] for i in range(REPS)]))
    out["shrinkage"] = shr
    out["best_k"] = int(max(KS, key=lambda k: shr[str(k)]))
    print(f"\n=== {name} ===")
    print(f"  in-place oracle gain  {out['in_place_oracle']:+.4f}")
    print(f"  estimable transfer    {out['estimable_transfer']:+.4f}  "
          f"({out['estimable_transfer']/out['in_place_oracle']:.0%} of the oracle)")
    for k in KS: print(f"  shrinkage k={k:5d}     {shr[str(k)]:+.4f}")
    print(f"  best k={out['best_k']}: {shr[str(out['best_k'])]:+.4f}", flush=True)
    return out

results = {}
A = f"{R}/cytolex-aakg-ablation-1103-v1"
b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner").dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS=["D","Kermut","AMK","X"]
units, meta = [], []
for aid,g in m.groupby("assay"):
    per=[[gs[COLS].to_numpy(float), gs["y"].to_numpy(float), None] for _,gs in g.groupby("scheme") if len(gs)>=20]
    if not per: continue
    for t in per: t[2]=[np.arange(len(t[1])), np.arange(len(t[1]))]
    units.append(per); meta.append({"id":aid, **ref.loc[aid, ["UniProt_ID","coarse_selection_type"]].to_dict()})
results["substitutions"] = run("ProteinGym substitutions", units, pd.DataFrame(meta), grid(4))

W = f"{R}/indel-benchmark-1119"
units, meta = [], []
iref = pd.read_csv(f"{W}/data/DMS_indels_ref.csv").set_index("DMS_id")
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
results["indels"] = run("ProteinGym indels", units, pd.DataFrame(meta), grid(3))

json.dump(results, open(f"{R}/consistent.json","w"), indent=2)
print("\nCONSISTENT DONE", flush=True)
