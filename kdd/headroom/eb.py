"""From a tuned heuristic to a derived estimator, and from a measurement to a prediction.

Part 1. The pooling strength lambda = n/(n+k) carries a tuned k. But shrinkage has a closed form: if each
assay's fitted weights have sampling variance sigma_i^2 around a true weight with between-assay variance
tau^2, the optimal shrink is lambda_i = tau^2 / (tau^2 + sigma_i^2). Both variances are estimable here --
sigma_i^2 from repeated half-splits, tau^2 as the total variance of the assay mean weights minus the mean
sampling variance. We check whether the derived lambda reproduces the k that was tuned on the panel.

Part 2. Whether per-assay weighting is worth attempting should be predictable from the assay, not discovered
by trying it. We relate the per-assay oracle gain to expert disagreement, and test a decision rule against
always-on and always-off.
"""
import os
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
rng = np.random.default_rng(0)
REPS = 6
KS = [10, 30, 100, 300, 1000, 3000]

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a-a.mean())/(a.std()+1e-12)
def sp(a,b): return spearmanr(a,b).correlation
def grid(k, step=0.1):
    n=int(round(1/step)); return np.array([w for w in itertools.product(np.linspace(0,1,n+1),repeat=k) if abs(sum(w)-1)<1e-9])

def analyse(name, units, meta, G):
    ids = list(meta["id"]); n = len(units)
    meta_idx = meta.set_index("id")
    def agg(v):
        df = pd.DataFrame({"v": v}, index=ids).join(meta_idx[["UniProt_ID","coarse_selection_type"]])
        return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())
    def sc(i, w, h):
        vals=[]
        for X,y,half in units[i]:
            idx=half[h]; Xa=X[idx]; ya=y[idx]
            Zm=[z(Xa[:,j]) for j in range(Xa.shape[1])]
            vals.append(sp(sum(a*c for a,c in zip(w,Zm)), ya))
        return float(np.mean(vals))

    # ---- repeated half-splits: fitted weights and their sampling variance ----
    W = np.zeros((REPS, n, G.shape[1]))
    for rep in range(REPS):
        for u in units:
            for X,y,half in u:
                half[0], half[1] = np.array_split(rng.permutation(len(y)), 2)
        for i in range(n):
            W[rep, i] = max(G, key=lambda w: sc(i,w,0))
        print(f"  [{name}] replicate {rep+1}/{REPS}", flush=True)
    wbar = W.mean(axis=0)                                   # (n, k)
    sigma2_i = ((W - wbar[None])**2).mean(axis=(0,2))       # variance of ONE fitted weight vector, per assay
    total_var = wbar.var(axis=0).mean()                      # across assays, averaged over coordinates
    tau2 = max(total_var - sigma2_i.mean(), 1e-6)
    lam_eb = tau2 / (tau2 + sigma2_i)
    ns = np.array([sum(len(t[1]) for t in u) for u in units])
    print(f"\n[{name}] total var {total_var:.5f} | mean sigma^2 {sigma2_i.mean():.5f} | tau^2 {tau2:.5f}")
    print(f"[{name}] lambda_EB: min {lam_eb.min():.3f} median {np.median(lam_eb):.3f} max {lam_eb.max():.3f}"
          f" | corr with n {sp(lam_eb, ns):+.3f}", flush=True)

    # ---- evaluate: constant, per-assay, tuned-k pooling, EB pooling ----
    def evaluate(rep):
        for u in units:
            for X,y,half in u:
                half[0], half[1] = np.array_split(rng.permutation(len(y)), 2)
        W_A = [max(G, key=lambda w: sc(i,w,0)) for i in range(n)]
        wg = max(G, key=lambda w: np.mean([sc(i,w,0) for i in range(n)]))
        cB = np.array([sc(i,wg,1) for i in range(n)])
        pB = np.array([sc(i,W_A[i],1) for i in range(n)])
        out = {"per_assay": agg(pB)-agg(cB)}
        for k in KS:
            lam = ns/(ns+k)
            out[f"k{k}"] = agg(np.array([sc(i,(1-lam[i])*wg+lam[i]*W_A[i],1) for i in range(n)]))-agg(cB)
        lam = lam_eb
        out["EB"] = agg(np.array([sc(i,(1-lam[i])*wg+lam[i]*W_A[i],1) for i in range(n)]))-agg(cB)
        return out
    evals = [evaluate(r) for r in range(3)]
    res = {kk: float(np.mean([e[kk] for e in evals])) for kk in evals[0]}
    best_k = max(KS, key=lambda kk: res[f"k{kk}"])
    print(f"[{name}] per-assay {res['per_assay']:+.4f}")
    for k in KS: print(f"[{name}]   k={k:5d} {res[f'k{k}']:+.4f}")
    print(f"[{name}]   EB      {res['EB']:+.4f}   (tuned best k={best_k}: {res[f'k{best_k}']:+.4f})", flush=True)

    # implied k from EB
    with np.errstate(divide="ignore"):
        k_implied = ns*(1-lam_eb)/np.maximum(lam_eb, 1e-9)
    print(f"[{name}] implied k from EB: median {np.median(k_implied):.0f} | tuned best k {best_k}", flush=True)

    # ---- part 2: is the gain predictable from disagreement? ----
    # per-assay: how much the experts agree, and how much an oracle could gain over the constant
    agree, gain = [], []
    for i in range(n):
        def blended(w):
            vals = []
            for X, y, _ in units[i]:
                Zm = [z(X[:, j]) for j in range(X.shape[1])]
                vals.append(sp(sum(a*c for a, c in zip(w, Zm)), y))
            return float(np.mean(vals))
        # disagreement: how much the experts disagree about THIS assay's variants
        X0, y0, _ = max(units[i], key=lambda t: len(t[1]))
        preds = [z(X0[:, j]) for j in range(X0.shape[1])]
        pair = [abs(sp(preds[a], preds[b])) for a in range(len(preds)) for b in range(a+1, len(preds))]
        agree.append(float(np.mean(pair)))
        wg = max(G, key=blended)
        wo = max(G, key=blended)
        gain.append(blended(wo) - blended(wg))
    agree = np.array(agree); gain = np.array(gain)
    ok = np.isfinite(agree)
    print(f"[{name}] assays with a disagreement estimate: {int(ok.sum())}/{n}", flush=True)
    if ok.sum() > 3:
        print(f"[{name}] disagreement (1 - mean expert agreement) vs per-assay oracle gain: "
              f"r = {sp(1-agree[ok], gain[ok]):+.3f}", flush=True)
    np.save(f"{R}/eb_{name}_agree.npy", agree)
    np.save(f"{R}/eb_{name}_gain.npy", gain)
    return {"n": n, "tau2": float(tau2), "mean_sigma2": float(sigma2_i.mean()),
            "lambda_median": float(np.median(lam_eb)), "lambda_n_corr": float(sp(lam_eb, ns)),
            "res": res, "best_k": int(best_k), "k_implied_median": float(np.median(k_implied)),
            "disagreement_corr": float(sp(1-agree, gain))}

results = {}
A = f"{R}/cytolex-aakg-ablation-1103-v1"
b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner").dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS=["D","Kermut","AMK","X"]; units, meta = [], []
for aid,g in m.groupby("assay"):
    per=[[gs[COLS].to_numpy(float), gs["y"].to_numpy(float), None] for _,gs in g.groupby("scheme") if len(gs)>=20]
    if not per: continue
    for t in per: t[2]=[np.arange(len(t[1])), np.arange(len(t[1]))]
    units.append(per); meta.append({"id":aid, **ref.loc[aid,["UniProt_ID","coarse_selection_type"]].to_dict()})
results["substitutions"] = analyse("substitutions", units, pd.DataFrame(meta), grid(4))

W = f"{R}/indel-benchmark-1119"; units, meta = [], []
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
results["indels"] = analyse("indels", units, pd.DataFrame(meta), grid(3))

json.dump(results, open(f"{R}/eb.json","w"), indent=2)
print("\nEB DONE", flush=True)
