"""A weighting rule for the deployment metric, built around a smooth surrogate.

Direct top-k recall is a counting statistic: with k% of ~1000 variants, a few flipped ranks move it a lot, so
fitting weights to maximise it directly is high-variance. The paper's own finding is that shrinkage fixes exactly
this kind of variance problem, so two ideas are tested together:

  objective   spearman   rank correlation (what everything in the paper uses)
              topk       fractions of the true top k recovered -- the noisy statistic itself
              margin     mean score on the true top k minus mean score off it -- smooth, same target
  shrinkage   w(lambda) = (1 - lambda) * w_panel + lambda * w_assay, with lambda chosen leave-one-assay-out

Evaluated on held-out variants, scored by top-k recall, aggregated the official way.
"""
import os
import itertools, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
A = f"{R}/cytolex-aakg-ablation-1103-v1"
KPCT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
REPS = 5
LAMS = [0.0, 0.25, 0.5, 0.75, 1.0]

def z(a):
    a = np.asarray(a, np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0: return np.nan
    return spearmanr(a, b).correlation
def grid(k, step=0.1):
    m = int(round(1 / step))
    return np.array([w for w in itertools.product(np.linspace(0, 1, m + 1), repeat=k) if abs(sum(w) - 1) < 1e-9])
def topk_recall(pred, y, frac):
    m = len(y); k = max(1, int(round(frac * m)))
    pi = set(np.argsort(-pred)[:k].tolist()); ti = set(np.argsort(-y)[:k].tolist())
    return len(pi & ti) / k
def margin(pred, y, frac):
    m = len(y); k = max(1, int(round(frac * m)))
    order = np.argsort(-y); top = order[:k]; rest = order[k:]
    if len(rest) == 0: return 0.0
    return float(pred[top].mean() - pred[rest].mean())

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
print(f"top-k {KPCT} | assays {n} | reps {REPS} | objectives spearman/topk/margin", flush=True)

def blend(gs, w):
    return sum(a * z(gs[c].to_numpy(float)) for a, c in zip(w, COLS))

def obj_score(aid, w, half, kind):
    """kind in {spearman, topk, margin}; half = list of idx arrays per scheme or None."""
    v = []
    for si, gs in enumerate(units[aid]):
        g = gs if half is None else gs.iloc[half[si]]
        pred = blend(g, w); y = g["y"].to_numpy(float)
        if kind == "spearman": v.append(sp(pred, y))
        elif kind == "topk":   v.append(topk_recall(pred, y, KPCT))
        else:                  v.append(margin(pred, y, KPCT))
    return float(np.nanmean(v))

def agg(vals):
    df = pd.DataFrame({"v": vals}, index=ids).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

res = {}
for rep in range(REPS):
    halves = {aid: [np.array_split(rng.permutation(len(gs)), 2) for gs in units[aid]] for aid in ids}
    HA = {aid: [h[0] for h in halves[aid]] for aid in ids}
    HB = {aid: [h[1] for h in halves[aid]] for aid in ids}
    M = {}
    for kind in ("spearman", "topk", "margin"):
        S = np.empty((len(G), n))
        for gi, w in enumerate(G):
            for i, aid in enumerate(ids):
                S[gi, i] = obj_score(aid, w, HA[aid], kind)
        M[kind] = S
    const = {}
    for kind, S in M.items():
        const[kind] = [G[int(np.argmax((S.sum(axis=1) - S[:, i]) / (n - 1)))] for i in range(n)]
    per_assay = {kind: [G[int(np.argmax(S[:, i]))] for i in range(n)] for kind, S in M.items()}
    # choose lambda leave-one-assay-out inside the training half for each objective
    lam_best = {}
    for kind, S in M.items():
        cands = {}
        for lam in LAMS:
            sc = np.array([obj_score(ids[i], (1 - lam) * const[kind][i] + lam * per_assay[kind][i], HA[ids[i]], kind)
                           for i in range(n)])
            cands[lam] = sc
        lam_best[kind] = [max(LAMS, key=lambda lam: np.mean([cands[lam][j] for j in range(n) if j != i])) for i in range(n)]
    # evaluate top-k recall on held-out half
    def eval_rule(kind, shrunk):
        vals = []
        for i, aid in enumerate(ids):
            lam = lam_best[kind][i] if shrunk else 0.0
            w = (1 - lam) * const[kind][i] + lam * per_assay[kind][i]
            vals.append(obj_score(aid, w, HB[aid], "topk"))
        return agg(np.array(vals))
    for kind in ("spearman", "topk", "margin"):
        for shrunk in (False, True):
            key = f"{kind}{'_shrunk' if shrunk else ''}"
            res.setdefault(key, []).append(eval_rule(kind, shrunk))
    print(f"  rep {rep+1}/{REPS}", flush=True)

print()
means = {k: float(np.mean(v)) for k, v in res.items()}
for k in sorted(means): print(f"  {k:18s} top-k recall {means[k]:.4f}")
base = means["topk"]  # unshrunk top-k rule as a reference line
print(f"\n  best rule: {max(means, key=means.get)} -> {max(means.values()):.4f}")
json.dump(means, open(f"{R}/topk_rule_{int(KPCT*100)}.json", "w"), indent=2)
print("TOP-K RULE DONE", flush=True)
