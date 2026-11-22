"""Pilot A: is our hand-designed view already at the optimum of the disagreement trade-off?

The paper's own ablation says an expert earns its place through disagreement with the pool, and that
distilling it toward the pool destroys that value. But the view that produces the disagreement is hand-
designed -- wt, mut, difference, window -- and nothing optimises it. This traces the axis continuously:

    X_alpha = (1 - alpha) * z(X) + alpha * z(pool)      alpha in [0, 1]

alpha = 0 is our expert as trained; alpha = 1 makes it a copy of the pool (zero disagreement, and by the
paper's own account zero value). For each alpha we measure standalone quality, residual disagreement with
the pool, and the fusion gain when the expert joins the pool under the nested-constant protocol.

If fusion gain peaks at alpha > 0, our view is too far out and a learned view has room. If alpha = 0 is
optimal, the hand-designed view is already on the frontier.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)
ALPHAS = np.round(np.linspace(0, 1, 11), 2)

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
POOL = ["D","Kermut","AMK"]
units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per: units[aid] = per
ids = sorted(units)
meta = ref.reindex(ids)
print("assays:", len(ids), flush=True)

def blended(aid, w, row):
    vals=[]
    for gs in units[aid]:
        Zm=[z(gs[row].to_numpy(float)) for row in [row]]*0
        break
    return np.nan

def sc_cols(aid, cols, w):
    """score a blend of the named columns on one assay, mean over schemes."""
    vals=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in cols]
        vals.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(vals))

def agg(v):
    df = pd.DataFrame({"v": v}, index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

def nested(cols, G):
    S = np.empty((len(G), len(ids)))
    for gi,w in enumerate(G):
        for i,aid in enumerate(ids):
            S[gi,i] = sc_cols(aid, cols, w)
        if gi % 60 == 0: print(f"    grid {gi}/{len(G)}", flush=True)
    n = len(ids)
    const = np.array([S[int(np.argmax((S.sum(1)-S[:,i])/(n-1))), i] for i in range(n)])
    return agg(const), const

# the pool's own blend, fitted on the pool only
POOL_G = grid(3)
pool_const, pool_per_assay = nested(POOL, POOL_G)
print(f"pool of {POOL} constant {pool_const:.4f}", flush=True)

# per-variant pool prediction, used to build X_alpha
W_pool = np.zeros((len(ids), 3))
S = np.empty((len(POOL_G), len(ids)))
for gi,w in enumerate(POOL_G):
    for i,aid in enumerate(ids):
        S[gi,i] = sc_cols(aid, POOL, w)
for i in range(len(ids)):
    W_pool[i] = POOL_G[int(np.argmax((S.sum(1)-S[:,i])/(len(ids)-1)))]

rows = []
G4 = grid(4)
for alpha in ALPHAS:
    # build the synthetic column on every unit
    col = []
    for aid in ids:
        for gs in units[aid]:
            P = np.zeros(len(gs))
            for c, wt in zip(POOL, W_pool[ids.index(aid)]):
                P += wt * z(gs[c].to_numpy(float))
            pal = z(P); ex = z(gs["X"].to_numpy(float))
            col.append((1-alpha)*ex + alpha*pal)
    # attach as a column named "XV"
    k = 0
    for aid in ids:
        for gs in units[aid]:
            gs["XV"] = col[k]; k += 1
    stand = [sc_cols(aid, ["XV"], np.array([1.0])) for aid in ids]
    dis = [1.0 - abs(sp(
        np.concatenate([z(gs["XV"].to_numpy(float)) for gs in units[aid]]),
        np.concatenate([sum(wt*z(gs[c].to_numpy(float)) for c,wt in zip(POOL, W_pool[ids.index(aid)])) for gs in units[aid]])))
        for aid in ids]
    fus, _ = nested(POOL + ["XV"], G4)
    rows.append({"alpha": float(alpha), "standalone": agg(np.array(stand)),
                 "disagreement": float(np.nanmean(dis)), "fusion": fus, "gain": fus - pool_const})
    print(f"  alpha {alpha:.2f}: standalone {rows[-1]['standalone']:.4f} | disagreement {rows[-1]['disagreement']:.3f} "
          f"| fusion {fus:.4f} | gain {fus-pool_const:+.4f}", flush=True)

best = max(rows, key=lambda r: r["gain"])
print(f"\nAT ALPHA 0 (our view): gain {rows[0]['gain']:+.4f}")
print(f"BEST ALPHA {best['alpha']:.2f}: gain {best['gain']:+.4f}")
print(f"headroom lost by our view: {best['gain']-rows[0]['gain']:+.4f}")
json.dump(rows, open(f"{R}/pilotA.json","w"), indent=2)
print("PILOT A DONE", flush=True)
