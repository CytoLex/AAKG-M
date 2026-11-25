"""Does the top-k headroom survive held-out variants?

The oracle at top-5% recall reports 5.8x the Spearman headroom, and Spearman-optimal weights capture under 9% of it.
Before that changes a conclusion, it must be shown not to be the oracle fitting sampling noise: top-k recall over
~50 variants is a far noisier statistic than a rank correlation over a thousand.

Protocol as everywhere else. Per assay, weights are fitted on half the variants to maximise top-k recall and,
separately, to maximise Spearman; the reference constant is fitted on the same half of the other assays. All three
are then evaluated on the untouched half.
"""
import os
import itertools, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"
KPCT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
REPS = 5

def z(a):
    a = np.asarray(a, np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0: return np.nan
    return spearmanr(a, b).correlation
def grid(k, step=0.1):
    m = int(round(1 / step))
    return np.array([w for w in itertools.product(np.linspace(0, 1, m + 1), repeat=k) if abs(sum(w) - 1) < 1e-9])
def topk(pred, y, frac):
    m = len(y); k = max(1, int(round(frac * m)))
    pi = set(np.argsort(-np.asarray(pred))[:k].tolist())
    ti = set(np.argsort(-np.asarray(y))[:k].tolist())
    return len(pi & ti) / k

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay", "scheme", "variant_id", "X"]], on=["assay", "scheme", "variant_id"], how="inner")
m = m.dropna(subset=["D", "Kermut", "AMK", "X", "y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS = ["D", "Kermut", "AMK", "X"]
units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per: units[aid] = per
ids = sorted(units); meta = ref.reindex(ids); n = len(ids)
rng = np.random.default_rng(0)
G = grid(4)
print(f"top-k {KPCT} | assays {n} | reps {REPS}", flush=True)

def score(aid, w, half, kind):
    """half is a list (one per scheme) of index arrays, or None for all variants."""
    vals = []
    for si, gs in enumerate(units[aid]):
        g = gs if half is None else gs.iloc[half[si]]
        Zm = [z(g[c].to_numpy(float)) for c in COLS]
        blend = sum(a * c for a, c in zip(w, Zm))
        y = g["y"].to_numpy(float)
        vals.append(topk(blend, y, KPCT) if kind == "topk" else sp(blend, y))
    return float(np.nanmean(vals))

def agg(v):
    df = pd.DataFrame({"v": v}, index=ids).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

acc = {}
for rep in range(REPS):
    halves = {aid: [np.array_split(rng.permutation(len(gs)), 2) for gs in units[aid]] for aid in ids}
    H_A = {aid: [h[0] for h in halves[aid]] for aid in ids}
    H_B = {aid: [h[1] for h in halves[aid]] for aid in ids}
    # score matrix per objective on half A: one pass, then the leave-one-out constant is a row subtraction
    def score_matrix(kind):
        M = np.empty((len(G), n))
        for gi, w in enumerate(G):
            for i, aid in enumerate(ids):
                M[gi, i] = score(aid, w, H_A[aid], kind)
        return M
    Mk, Ms = score_matrix("topk"), score_matrix("spearman")
    WA_k = [G[int(np.argmax(Mk[:, i]))] for i in range(n)]
    WA_s = [G[int(np.argmax(Ms[:, i]))] for i in range(n)]
    def const_from(M):
        return [G[int(np.argmax((M.sum(axis=1) - M[:, i]) / (n - 1)))] for i in range(n)]
    C_k, C_s = const_from(Mk), const_from(Ms)

    def evalfn(W, half, kind):
        return np.array([score(ids[i], W[i], half[ids[i]], kind) for i in range(n)])
    for tag, W, kind, half in (("topk_weights", WA_k, "topk", H_B),
                               ("spearman_weights_on_topk", WA_s, "topk", H_B),
                               ("topk_const", C_k, "topk", H_B),
                               ("spearman_weights", WA_s, "spearman", H_B),
                               ("spearman_const", C_s, "spearman", H_B)):
        acc.setdefault(tag, []).append(agg(evalfn(W, half, kind)))
    print(f"  rep {rep+1}/{REPS} done", flush=True)

print()
res = {k: float(np.mean(v)) for k, v in acc.items()}
for k, v in res.items(): print(f"  {k:26s} {v:.4f}")
hk = res["topk_weights"] - res["topk_const"]
sk = res["spearman_weights"] - res["spearman_const"]
print(f"\n  top-k headroom that transfers   : {hk:+.4f}")
print(f"  Spearman headroom that transfers: {sk:+.4f}")
print(f"  ratio                           : {hk/sk:.1f}x" if sk else "")
print(f"  Spearman-optimal weights capture : {(res['spearman_weights_on_topk']-res['topk_const'])/hk:.1%} of it")
json.dump(res, open(f"{R}/topk_holdout_{int(KPCT*100)}.json", "w"), indent=2)
print("HOLDOUT DONE", flush=True)
