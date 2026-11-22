"""The pooling null control on indels, where shrinkage is heavy.

On substitutions the derived lambda has a median of 0.93, permuting it costs nothing, and the per-assay
alignment turns out to do no work -- only the shrinkage level does. Indels are the opposite regime: small
assays, lambda around 0.39, and unregularised per-assay fitting loses. If the alignment matters anywhere, it
matters here, and that is what this measures.
"""
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W_ROOT = f"{R}/indel-benchmark-1119"
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

units, meta = [], []
iref = pd.read_csv(f"{W_ROOT}/data/DMS_indels_ref.csv").set_index("DMS_id")
for f in sorted(glob.glob(f"{W_ROOT}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W_ROOT}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W_ROOT}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence","fold_random_5"]]
    mm = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if mm.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True); y, P = z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    units.append({"id": aid, "X": P[ok], "y": y[ok]})
    meta.append({"id": aid, "UniProt_ID": iref.loc[aid,"UniProt_ID"], "coarse_selection_type": "all"})
meta = pd.DataFrame(meta); mets = meta.set_index("id")
n = len(units); ids = [u["id"] for u in units]
print(f"indel assays: {n}", flush=True)
G = grid(3)

Zs = [[z(u["X"][:, j]) for j in range(u["X"].shape[1])] for u in units]
def sc(i, w, idx=None):
    if idx is None: return sp(sum(a*c for a,c in zip(w, Zs[i])), units[i]["y"])
    Zi = [z(units[i]["X"][idx, j]) for j in range(units[i]["X"].shape[1])]
    return sp(sum(a*c for a,c in zip(w, Zi)), units[i]["y"][idx])
def agg(v):
    df = pd.DataFrame({"v": v}, index=ids).join(mets[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

# variance components from repeated half-splits
Wr = np.zeros((REPS, n, 3))
for rep in range(REPS):
    idx_half = [np.array_split(rng.permutation(len(u["y"])), 2) for u in units]
    for i in range(n):
        best, bs = None, -9
        for w in G:
            s = sc(i, w, idx_half[i][0])
            if s > bs: bs, best = s, w
        Wr[rep, i] = best
    print(f"  rep {rep+1}/{REPS}", flush=True)
wbar = Wr.mean(0)
sigma2 = ((Wr - wbar[None])**2).mean(axis=(0,2))
tau2 = max(wbar.var(axis=0).mean() - sigma2.mean(), 1e-6)
lam = tau2/(tau2 + sigma2)
print(f"tau^2 {tau2:.5f} | mean sigma^2 {sigma2.mean():.5f} | lambda median {np.median(lam):.3f}", flush=True)

S = np.empty((len(G), n))
for gi, w in enumerate(G):
    for i in range(n): S[gi,i] = sc(i, w)
best = S.argmax(0)
const = np.array([int(np.argmax((S.sum(1)-S[:,i])/(n-1))) for i in range(n)])
base = agg(S[const, np.arange(n)])
print(f"constant {base:.4f} | oracle {agg(S[best, np.arange(n)]):.4f}", flush=True)

def pooled(lv):
    return np.array([sc(i, (1-lv[i])*G[const[i]] + lv[i]*G[best[i]]) for i in range(n)])
real = agg(pooled(lam))
print(f"pooling, derived lambda : {real:.4f}  (gain {real-base:+.4f})", flush=True)
perm = [agg(pooled(lam[rng.permutation(n)])) - base for _ in range(40)]
lo, hi = np.percentile(perm, [2.5, 97.5])
print(f"NULL pooling, lambda permuted: {np.mean(perm):+.4f} [{lo:+.4f}, {hi:+.4f}]", flush=True)
print(f"real gain minus null: {(real-base)-np.mean(perm):+.4f}", flush=True)
# also: heavy but flat shrinkage, to separate level from alignment
for c in (0.2, 0.39, 0.6):
    print(f"  flat lambda={c:.2f}: gain {agg(pooled(np.full(n,c)))-base:+.4f}", flush=True)
json.dump({"tau2":float(tau2),"lam_median":float(np.median(lam)),"base":base,"real":real,
           "null":float(np.mean(perm)),"null_ci":[float(lo),float(hi)],
           "real_minus_null":float((real-base)-np.mean(perm))}, open(f"{R}/poolctl_indel.json","w"), indent=2)
print("POOLCTL INDEL DONE", flush=True)
