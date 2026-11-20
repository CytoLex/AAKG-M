"""Confidence intervals for the allocation headroom, on both benchmarks.

First reproduce the paper's figure from the out-of-fold bundle by trying the plausible expert subsets, then
put a bootstrap CI and a grouped-fold sensitivity around whichever subset matches. The indel side needs no
training either: the published experts' predictions are already cached.
"""
import os, glob, json, itertools, numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
rng = np.random.default_rng(0)

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b): return spearmanr(a, b).correlation
def grid(k, step=0.1):
    n = int(round(1/step))
    return np.array([w for w in itertools.product(np.linspace(0,1,n+1), repeat=k) if abs(sum(w)-1) < 1e-9])

def score_matrix(expert_list, ys, G):
    Z = [[z(cols[:, j]) for j in range(cols.shape[1])] for cols in expert_list]
    n = len(expert_list)
    S = np.empty((len(G), n))
    for gi, w in enumerate(G):
        for i in range(n):
            S[gi, i] = sp(sum(a*b for a, b in zip(w, Z[i])), ys[i])
    return S

def score_matrix_by_scheme(groups, G):
    """Paper protocol: Spearman within each (assay, scheme), then average over schemes.

    groups[i] = list of (X_ni, y_ni) pairs, one per scheme. Z-scoring is done within the scheme, matching
    how the published pipeline standardises.
    """
    n = len(groups)
    S = np.empty((len(G), n))
    for gi, w in enumerate(G):
        for i in range(n):
            per = []
            for X, y in groups[i]:
                Zc = [z(X[:, j]) for j in range(X.shape[1])]
                per.append(sp(sum(a*b for a, b in zip(w, Zc)), y))
            S[gi, i] = float(np.mean(per))
    return S

def headroom(S):
    n = S.shape[1]
    oracle = S.max(axis=0)
    nested = np.empty(n)
    for i in range(n):
        others = (S.sum(axis=1) - S[:, i]) / (n-1)
        nested[i] = S[int(np.argmax(others)), i]
    return oracle, nested

def report(name, S):
    n = S.shape[1]
    oracle, nested = headroom(S)
    d = oracle - nested
    boots = [d[rng.integers(0, n, n)].mean() for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    fold = []
    for rep in range(10):
        assign = rng.permutation(n) % 5
        parts = []
        for k in range(5):
            te = np.where(assign == k)[0]; tr = np.where(assign != k)[0]
            w = int(np.argmax(S[:, tr].mean(axis=1)))
            parts.append(np.mean([S[:, j].max() for j in te]) - np.mean([S[w, j] for j in te]))
        fold.append(float(np.mean(parts)))
    print(f"\n=== {name} ===")
    print(f"  units {n} | nested constant {nested.mean():.4f} | oracle {oracle.mean():.4f}")
    print(f"  headroom {d.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  bootstrap sd {np.std(boots):.4f}")
    print(f"  grouped-fold (fit on 4/5 of assays): {np.mean(fold):+.4f} +- {np.std(fold):.4f}")
    return {"n_units": n, "nested": float(nested.mean()), "oracle": float(oracle.mean()),
            "headroom": float(d.mean()), "ci95": [float(lo), float(hi)],
            "boot_sd": float(np.std(boots)), "grouped_mean": float(np.mean(fold)),
            "grouped_sd": float(np.std(fold))}

results = {}
b = pd.read_csv(f"{R}/cytolex-aakg-ablation-1103-v1/data/oof_bundle.csv.gz")
print("columns:", list(b.columns), "| rows:", len(b), flush=True)
b = b.rename(columns={"target": "y"})

print("\n--- reproducing the paper figure across expert subsets ---", flush=True)
best = None
for subset in (("D","Kermut","AMK"), ("D","Kermut","Kseq","AMK"), ("Kermut","AMK"),
               ("D","Kermut"), ("Kermut","AMK","Kseq")):
    if not all(c in b.columns for c in subset): continue
    cols, ys = [], []
    for aid, g in b.groupby("assay"):
        g = g.dropna(subset=list(subset)+["y"])
        if len(g) < 50: continue
        cols.append(g[list(subset)].to_numpy(float)); ys.append(g["y"].to_numpy(float))
    S = score_matrix(cols, ys, grid(len(subset)))
    o, nn = headroom(S)
    print(f"  {str(subset):34s} units {len(cols):3d} | nested {nn.mean():.4f} oracle {o.mean():.4f} "
          f"| headroom {o.mean()-nn.mean():+.4f}", flush=True)
    if len(subset) == 3 and best is None:
        groups = []
        for aid, g in b.groupby("assay"):
            g = g.dropna(subset=list(subset)+["y"])
            if len(g) < 50: continue
            per = []
            for sch, gs in g.groupby("scheme"):
                if len(gs) < 20: continue
                per.append((gs[list(subset)].to_numpy(float), gs["y"].to_numpy(float)))
            if per: groups.append(per)
        S_scheme = score_matrix_by_scheme(groups, grid(3))
        best = (subset, S_scheme)
if best:
    results["substitutions"] = report(f"ProteinGym substitutions {best[0]}", best[1])

# ---------------- indels ----------------
W = f"{R}/indel-benchmark-1119"
cols, ys = [], []
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence", "fold_random_5"]]
    m = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if m.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True); y, P = z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    cols.append(P[ok]); ys.append(y[ok])
S = score_matrix(cols, ys, grid(3))
results["indels"] = report("ProteinGym indels (3 published experts)", S)

json.dump(results, open(f"{R}/headroom_ci.json", "w"), indent=2)
print("\nHEADROOM CI DONE", flush=True)
