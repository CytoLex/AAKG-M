"""Variant-level split-half, under the same aggregation as the headroom numbers.

For each assay the oracle weights are fitted on half its variants and evaluated on the other half, against
the constant fitted on the other assays. Both halves are aggregated the paper's way -- UniProt then category
-- and the whole thing is repeated over independent random splits so it arrives with a spread.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
rng = np.random.default_rng(0)
REPS = 10

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean())/(a.std()+1e-12)
def sp(a, b): return spearmanr(a, b).correlation
def grid(k, step=0.1):
    n = int(round(1/step))
    return np.array([w for w in itertools.product(np.linspace(0,1,n+1), repeat=k) if abs(sum(w)-1) < 1e-9])

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target":"y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred":"X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
m = m.dropna(subset=["D","Kermut","AMK","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS = ["D","Kermut","AMK"]
G = grid(3)

pieces = {}
for (aid, sch), g in m.groupby(["assay","scheme"]):
    if len(g) < 20: continue
    pieces.setdefault(aid, []).append(g)
assays = sorted(pieces)
meta = ref.reindex(assays)
print("assays:", len(assays), flush=True)

def score_assay(aid, w, half=None):
    vals = []
    for g in pieces[aid]:
        gg = g if half is None else (g.iloc[half[0]] if half != "A" else None)
        if gg is None: continue
        Xm = [z(gg[c].to_numpy(float)) for c in COLS]
        vals.append(sp(sum(a*c for a, c in zip(w, Xm)), gg["y"].to_numpy(float)))
    return float(np.mean(vals)) if vals else np.nan

# constant weights per assay: fitted on the other assays (full data)
Sfull = np.empty((len(G), len(assays)))
for gi, w in enumerate(G):
    for i, aid in enumerate(assays):
        Sfull[gi, i] = score_assay(aid, w)
    if gi % 20 == 0: print(" full grid", gi, flush=True)
W_CONST = []
for i in range(len(assays)):
    others = (Sfull.sum(axis=1) - Sfull[:, i]) / (len(assays)-1)
    W_CONST.append(G[int(np.argmax(others))])

def aggregate(v):
    df = pd.DataFrame({"v": v}, index=assays).join(meta[["UniProt_ID","coarse_selection_type"]])
    g2 = df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean()
    return float(g2.groupby(level=1).mean().mean())

inp, tr = [], []
for rep in range(REPS):
    ip, tv = np.zeros(len(assays)), np.zeros(len(assays))
    for i, aid in enumerate(assays):
        # split each scheme's variants, then average the score over schemes for each half
        w_sel_vals = {g_i: None for g_i in range(len(G))}
        halves = []
        for g in pieces[aid]:
            n = len(g); idx = rng.permutation(n); h = n//2
            halves.append((g.iloc[idx[:h]], g.iloc[idx[h:]]))
        def sc(w, which):
            vals = []
            for ga, gb in halves:
                gg = ga if which == 0 else gb
                Xm = [z(gg[c].to_numpy(float)) for c in COLS]
                vals.append(sp(sum(a*c for a, c in zip(w, Xm)), gg["y"].to_numpy(float)))
            return float(np.mean(vals))
        best = max(G, key=lambda w: sc(w, 0))
        ip[i] = sc(best, 0) - sc(W_CONST[i], 0)
        tv[i] = sc(best, 1) - sc(W_CONST[i], 1)
    inp.append(aggregate(ip)); tr.append(aggregate(tv))
    print(f"  rep {rep}: in-place {inp[-1]:+.4f} transfer {tr[-1]:+.4f}", flush=True)

print(f"\nsplit-half, {REPS} splits, official aggregation:")
print(f"  in-place  {np.mean(inp):+.4f} +- {np.std(inp):.4f}")
print(f"  transfer  {np.mean(tr):+.4f} +- {np.std(tr):.4f}")
print(f"  survival  {np.mean(tr)/np.mean(inp):.0%}")
json.dump({"reps": REPS, "in_place": float(np.mean(inp)), "in_place_sd": float(np.std(inp)),
           "transfer": float(np.mean(tr)), "transfer_sd": float(np.std(tr)),
           "survival": float(np.mean(tr)/np.mean(inp))},
          open(f"{R}/splithalf_pipeline.json","w"), indent=2)
print("SPLITHALF DONE", flush=True)
