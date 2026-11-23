"""The top-k rule on the indel benchmark, where the pool is different and rho is not the paper's only regime.

Every other claim in the paper replicates on ProteinGym's indels. The rule was validated on substitutions only,
at one k. This runs it on the indel pool (three published experts, 65 assays) at k = 5%, 10%.
"""
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W = f"{R}/indel-benchmark-1119"
LAMS = [0.0, 0.25, 0.5, 0.75, 1.0]
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
    pi = set(np.argsort(-np.asarray(pred))[:k].tolist()); ti = set(np.argsort(-np.asarray(y))[:k].tolist())
    return len(pi & ti) / k

units, meta = [], []
iref = pd.read_csv(f"{W}/data/DMS_indels_ref.csv").set_index("DMS_id")
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence", "fold_random_5"]]
    mm = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if mm.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True); y, P = z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    units.append({"id": aid, "X": P[ok], "y": y[ok]})
    meta.append({"id": aid, "UniProt_ID": iref.loc[aid, "UniProt_ID"], "coarse_selection_type": "all"})
meta = pd.DataFrame(meta); mets = meta.set_index("id")
ids = [u["id"] for u in units]; n = len(units)
K = units[0]["X"].shape[1]
G = grid(K)
rng = np.random.default_rng(0)
print(f"indels: {n} assays | {K} experts | grid {len(G)}", flush=True)

def obj(u, w, idx, kind):
    X = u["X"] if idx is None else u["X"][idx]
    y = u["y"] if idx is None else u["y"][idx]
    Zm = [z(X[:, j]) for j in range(K)]
    pred = sum(a * c for a, c in zip(w, Zm))
    return topk(pred, y, FRAC) if kind == "topk" else sp(pred, y)

def agg(vals):
    df = pd.DataFrame({"v": vals}, index=ids).join(mets[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

for FRAC in (0.05, 0.10):
    print(f"\n--- top-k {FRAC:.0%} ---", flush=True)
    out = {}
    for rep in range(REPS):
        halves = [np.array_split(rng.permutation(len(u["y"])), 2) for u in units]
        HA = [h[0] for h in halves]; HB = [h[1] for h in halves]
        S = {kind: np.empty((len(G), n)) for kind in ("topk", "spearman")}
        for kind in S:
            for gi, w in enumerate(G):
                for i, u in enumerate(units): S[kind][gi, i] = obj(u, w, HA[i], kind)
        const = {k: [G[int(np.argmax((v.sum(axis=1) - v[:, i]) / (n - 1)))] for i in range(n)] for k, v in S.items()}
        per = {k: [G[int(np.argmax(v[:, i]))] for i in range(n)] for k, v in S.items()}
        lam = {}
        for kind, v in S.items():
            cand = {l: np.array([obj(units[i], (1 - l) * const[kind][i] + l * per[kind][i], HA[i], kind) for i in range(n)])
                    for l in LAMS}
            lam[kind] = [max(LAMS, key=lambda l: np.mean([cand[l][j] for j in range(n) if j != i])) for i in range(n)]
        def ev(kind, shrunk):
            vals = []
            for i, u in enumerate(units):
                l = lam[kind][i] if shrunk else 0.0
                w = (1 - l) * const[kind][i] + l * per[kind][i]
                vals.append(obj(u, w, HB[i], "topk"))
            return agg(np.array(vals))
        for key, (kind, sh) in {"topk_shrunk": ("topk", True), "topk": ("topk", False),
                                "spearman": ("spearman", False), "spearman_shrunk": ("spearman", True)}.items():
            out.setdefault(key, []).append(ev(kind, sh))
    means = {k: float(np.mean(v)) for k, v in out.items()}
    for k in sorted(means): print(f"  {k:16s} {means[k]:.4f}", flush=True)
    json.dump(means, open(f"{R}/rule_indel_{int(FRAC*100)}.json", "w"), indent=2)
print("RULE INDEL DONE", flush=True)
