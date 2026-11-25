"""Pilot B: the same question on real experts rather than synthetic blends.

For every expert in the bundle and every pool it can join, measure three things: how well it does alone, how
much it disagrees with the rest of the pool, and what it actually adds to the fusion. Five experts give a
handful of real points, enough to see whether marginal value tracks disagreement at all -- and unlike pilot
A, nothing here is synthesised.
"""
import os
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
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
m = m.dropna(subset=["D","Kermut","Kseq","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
EXPERTS = ["D","Kermut","Kseq","AMK","X"]
units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per: units[aid] = per
ids = sorted(units); meta = ref.reindex(ids)
print(f"assays {len(ids)} | experts {EXPERTS}", flush=True)

def sc_cols(aid, cols, w):
    vals=[]
    for gs in units[aid]:
        Zm=[z(gs[c].to_numpy(float)) for c in cols]
        vals.append(sp(sum(a*c for a,c in zip(w,Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(vals))

def agg(v):
    df = pd.DataFrame({"v": v}, index=ids).join(meta[["UniProt_ID","coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

def nested(cols):
    G = grid(len(cols))
    S = np.empty((len(G), len(ids)))
    for gi,w in enumerate(G):
        for i,aid in enumerate(ids):
            S[gi,i] = sc_cols(aid, cols, w)
    n = len(ids)
    return agg(np.array([S[int(np.argmax((S.sum(1)-S[:,i])/(n-1))), i] for i in range(n)]))

rows = []
# every expert: solo quality, disagreement with the rest, marginal value
for e in EXPERTS:
    rest = [c for c in EXPERTS if c != e]
    solo = agg(np.array([sc_cols(aid, [e], np.array([1.0])) for aid in ids]))
    base = nested(rest)
    full = nested(rest + [e])
    dis = []
    for aid in ids:
        pe = np.concatenate([z(gs[e].to_numpy(float)) for gs in units[aid]])
        rp = np.concatenate([np.mean([z(gs[c].to_numpy(float)) for c in rest], axis=0) for gs in units[aid]])
        dis.append(1.0 - abs(sp(pe, rp)))
    rows.append({"expert": e, "solo": solo, "pool_of_4": base, "pool_of_5": full,
                 "marginal": full - base, "disagreement": float(np.nanmean(dis))})
    print(f"  {e:7s} solo {solo:.4f} | pool-of-4 {base:.4f} | marginal {full-base:+.4f} "
          f"| disagreement {rows[-1]['disagreement']:.3f}", flush=True)

# a minimal pool too, since marginal value is pool-dependent
for combo in (["D","Kermut"], ["Kermut","AMK"], ["D","Kermut","AMK"]):
    base = nested(combo)
    for e in [c for c in EXPERTS if c not in combo]:
        full = nested(combo + [e])
        dis = []
        for aid in ids:
            pe = np.concatenate([z(gs[e].to_numpy(float)) for gs in units[aid]])
            rp = np.concatenate([np.mean([z(gs[c].to_numpy(float)) for c in combo], axis=0) for gs in units[aid]])
            dis.append(1.0 - abs(sp(pe, rp)))
        rows.append({"expert": f"{e} into {'+'.join(combo)}", "solo": None, "pool_of_4": base,
                     "pool_of_5": full, "marginal": full - base, "disagreement": float(np.nanmean(dis))})
        print(f"  {e:7s} into {'+'.join(combo):18s} marginal {full-base:+.4f} | disagreement {rows[-1]['disagreement']:.3f}", flush=True)

dis = np.array([r["disagreement"] for r in rows]); marg = np.array([r["marginal"] for r in rows])
print(f"\ncorr(marginal value, disagreement) across {len(rows)} real (expert, pool) points: r = {sp(marg, dis):+.3f}")
json.dump({"rows": rows, "corr_disagreement_marginal": float(sp(marg, dis))},
          open(f"{R}/pilotB.json","w"), indent=2)
print("PILOT B DONE", flush=True)
