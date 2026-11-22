"""Run the protocol's control battery against the paper's four headline numbers.

The protocol says a control battery must pass before any claim is believed. It has been run for the marginal
value of a new expert. It has not been run for the other three headline numbers, and this does that:

  claim                                  null control
  allocation headroom  +0.0051            give each assay the oracle weights of a random OTHER assay
                                          (matched per-assay selection, zero information)
  expert gain          +0.0122            already controlled: noise column scores 0
  pooling gain         +0.0051 / +0.0021  permute the shrinkage coefficients across assays
  predictability       r = +0.534         permute the disagreement feature across assays

A claim whose null control is not zero was measuring selection, not signal.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
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
COLS=["D","Kermut","AMK","X"]
units={}
for aid,g in m.groupby("assay"):
    per=[gs for _,gs in g.groupby("scheme") if len(gs)>=20]
    if per: units[aid]=per
ids=sorted(units); meta=ref.reindex(ids); n=len(ids)
print("assays:", n, flush=True)

Zs = {aid: [[z(gs[c].to_numpy(float)) for c in COLS] for gs in units[aid]] for aid in ids}
def sc(aid, w):
    return float(np.nanmean([sp(sum(a*c for a,c in zip(w, Zi)), gs["y"].to_numpy(float))
                             for Zi, gs in zip(Zs[aid], units[aid])]))
def agg(v, idx=None):
    idx = np.arange(n) if idx is None else idx
    df=pd.DataFrame({"v":np.asarray(v)[idx]}, index=[ids[i] for i in idx]).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

G = grid(4)
print("score matrix", len(G), "x", n, flush=True)
S = np.empty((len(G), n))
for gi,w in enumerate(G):
    for i,aid in enumerate(ids): S[gi,i]=sc(aid,w)

best = S.argmax(axis=0)                                   # oracle index per assay
const_idx = np.array([int(np.argmax((S.sum(1)-S[:,i])/(n-1))) for i in range(n)])
const = S[const_idx, np.arange(n)]
oracle = S[best, np.arange(n)]
base = agg(const)
print(f"\nconstant {base:.4f} | oracle {agg(oracle):.4f} | headroom {agg(oracle)-base:+.4f}", flush=True)

# null 1: matched per-assay selection with no information
deltas = []
for _ in range(20):
    perm = rng.permutation(n)
    null = np.array([S[best[perm[i]], i] for i in range(n)])
    deltas.append(agg(null) - base)
lo, hi = np.percentile(deltas, [2.5, 97.5])
print(f"NULL oracle (weights from a random other assay): {np.mean(deltas):+.4f} "
      f"[{lo:+.4f}, {hi:+.4f}]  over 20 permutations", flush=True)

# pooling: derived shrinkage and its null
Wr = np.array([[best[i] for i in range(n)]])
sig = np.array([S[:, i].std() for i in range(n)])
lam = np.clip(1.0 - sig/np.maximum(sig.max(), 1e-9), 0, 1)
lam = 0.5*(lam + lam.mean())
def pooled(lamv):
    return np.array([sc(ids[i], (1-lamv[i])*G[const_idx[i]] + lamv[i]*G[best[i]]) for i in range(n)])
p_real = pooled(lam)
print(f"\npooling with the derived lambda: {agg(p_real):.4f} (gain {agg(p_real)-base:+.4f})", flush=True)
perm_gains = []
for _ in range(20):
    perm_gains.append(agg(pooled(lam[rng.permutation(n)])) - base)
lo2, hi2 = np.percentile(perm_gains, [2.5, 97.5])
print(f"NULL pooling (lambda permuted across assays): {np.mean(perm_gains):+.4f} [{lo2:+.4f}, {hi2:+.4f}]", flush=True)

# predictability control
D = []
for aid in ids:
    X0 = max(units[aid], key=lambda t: len(t))
    pr=[z(X0[c].to_numpy(float)) for c in COLS]
    D.append(1.0 - np.mean([abs(sp(pr[a],pr[b])) for a in range(len(pr)) for b in range(a+1,len(pr))]))
D=np.array(D); gain=oracle-const
print(f"\ncorr(gain, disagreement): {sp(gain,D):+.3f}", flush=True)
perm_r=[sp(gain, D[rng.permutation(n)]) for _ in range(200)]
print(f"NULL: permuted disagreement gives r = {np.mean(perm_r):+.3f} "
      f"[{np.percentile(perm_r,2.5):+.3f}, {np.percentile(perm_r,97.5):+.3f}]", flush=True)
print("\nCONFORM DONE", flush=True)
