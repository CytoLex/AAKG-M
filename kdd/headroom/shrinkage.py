"""Does partial pooling recover the allocation headroom that per-assay fitting cannot reach?

The paper measures two things: an oracle says +0.0051 is available in principle, and a variant-level split
says only 44% of it survives when the weights are fitted on the assay's own variants. The obvious fix is not
to abandon weighting but to pool it: shrink each assay's fitted weights toward the panel-wide constant by an
amount that depends on how many variants the assay has.

    w_i(lambda) = (1 - lambda) * w_global + lambda * w_oracle_i,    lambda = n_i / (n_i + k)

Small assays shrink hard, large assays barely shrink. k is selected on the panel, never on the held-out
half. Three rules are compared on the same held-out variants:

    constant      lambda = 0
    per-assay     lambda = 1   (the rule that fails)
    shrinkage     lambda = n_i / (n_i + k)
"""
import os
import os, glob, itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")   # see submission/oof/README.md
rng = np.random.default_rng(0)
REPS = 5
KS = [3, 10, 30, 100, 300, 1000, 3000]

def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean())/(a.std()+1e-12)
def sp(a, b): return spearmanr(a, b).correlation
def grid(k, step=0.1):
    n = int(round(1/step))
    return np.array([w for w in itertools.product(np.linspace(0,1,n+1), repeat=k) if abs(sum(w)-1) < 1e-9])

def run(name, units, meta, G, reps=REPS):
    meta_rows = [{"id": i} for i in meta["id"]]
    """units[i] = list of (X_ni_k, y_ni) over schemes; returns dict of results."""
    n = len(units)
    print(f"\n=== {name}: {n} assays, {G.shape[0]} grid points ===", flush=True)
    def sc(i, w, which):
        vals = []
        for X, y, halves in units[i]:
            idx = halves[which]
            Xa = X[idx]; ya = y[idx]
            Zm = [z(Xa[:, j]) for j in range(Xa.shape[1])]
            vals.append(sp(sum(a*c for a, c in zip(w, Zm)), ya))
        return float(np.mean(vals))
    meta_idx = meta.set_index("id")
    def aggregate(v):
        df = pd.DataFrame({"v": v}, index=[u["id"] for u in meta_rows]).join(meta_idx[["UniProt_ID","coarse_selection_type"]])
        g2 = df.groupby(["UniProt_ID","coarse_selection_type"])["v"].mean()
        return float(g2.groupby(level=1).mean().mean())

    rows = {k: [] for k in KS}; rows["constant"] = []; rows["per_assay"] = []
    for rep in range(reps):
        # fresh halves per unit and scheme, with at least 10 variants on each side
        for u in units:
            for t in u:
                X, y, half = t
                m = len(y)
                if m < 20: half[:] = [np.arange(m//2), np.arange(m//2, m)]
                else: half[:] = np.array_split(rng.permutation(m), 2)
        # per-assay optimal on half 0, and the panel-wide constant on half 0
        W_A = []
        for i in range(n):
            W_A.append(max(G, key=lambda w: sc(i, w, 0)))
        glob_scores = [(w, np.mean([sc(i, w, 0) for i in range(n)])) for w in G]
        w_glob = max(glob_scores, key=lambda t: t[1])[0]
        ns = np.array([len(np.concatenate([t[1] for t in u])) for u in units])
        out_const, out_orac = [], []
        for i in range(n):
            out_const.append(sc(i, w_glob, 1)); out_orac.append(sc(i, W_A[i], 1))
        rows["constant"].append(aggregate(np.array(out_const)))
        rows["per_assay"].append(aggregate(np.array(out_orac)))
        for k in KS:
            lam = ns / (ns + k)
            vals = []
            for i in range(n):
                w = (1-lam[i])*w_glob + lam[i]*W_A[i]
                vals.append(sc(i, w, 1))
            rows[k].append(aggregate(np.array(vals)))
        print(f"  rep {rep}: constant {rows['constant'][-1]:.4f} | per-assay {rows['per_assay'][-1]:.4f} | "
              f"best k so far {max(KS, key=lambda kk: np.mean(rows[kk]))}", flush=True)

    res = {str(k): float(np.mean(rows[k])) for k in KS}
    res["constant"] = float(np.mean(rows["constant"]))
    res["per_assay"] = float(np.mean(rows["per_assay"]))
    res["sd"] = {str(k): float(np.std(rows[k])) for k in KS}
    best_k = max(KS, key=lambda kk: res[str(kk)])
    print(f"  constant    {res['constant']:.4f}")
    print(f"  per-assay   {res['per_assay']:.4f}  ({res['per_assay']-res['constant']:+.4f} vs constant)")
    for k in KS:
        print(f"  k={k:5d}     {res[str(k)]:.4f}  ({res[str(k)]-res['constant']:+.4f} vs constant)")
    print(f"  best k = {best_k}: {res[str(best_k)]:.4f}", flush=True)
    return res

results = {}

# ---------------- substitutions ----------------
A = f"{R}/cytolex-aakg-ablation-1103-v1"
b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay","scheme","variant_id","X"]], on=["assay","scheme","variant_id"], how="inner")
m = m.dropna(subset=["D","Kermut","AMK","X","y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
COLS4 = ["D","Kermut","AMK","X"]
units, meta = [], []
for aid, g in m.groupby("assay"):
    per = []
    for sch, gs in g.groupby("scheme"):
        if len(gs) < 20: continue
        per.append([gs[COLS4].to_numpy(float), gs["y"].to_numpy(float), None])
    if not per: continue
    for t in per: t[2] = [np.arange(len(t[1]))]
    units.append(per); meta.append({"id": aid})
meta = pd.DataFrame(meta).join(ref[["UniProt_ID","coarse_selection_type"]], on="id")
results["substitutions"] = run("ProteinGym substitutions (4 experts)", units, meta, grid(4))

# ---------------- indels ----------------
W = f"{R}/indel-benchmark-1119"
units, meta = [], []
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence","fold_random_5"]]
    mm = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if mm.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True); y, P = z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    units.append([[P[ok], y[ok], None]]); units[-1][0][2] = [np.arange(ok.sum())]
    meta.append({"id": aid})
iref = pd.read_csv(f"{R}/indel-benchmark-1119/data/DMS_indels_ref.csv").set_index("DMS_id")
meta = pd.DataFrame(meta).join(iref[["UniProt_ID"]] if "UniProt_ID" in iref.columns else iref[["DMS_id"]], on="id")
if "coarse_selection_type" not in meta: meta["coarse_selection_type"] = "all"
save = meta.copy()
results["indels"] = run("ProteinGym indels (3 published experts)", units, save, grid(3))

json.dump(results, open(f"{R}/shrinkage.json","w"), indent=2)
print("\nSHRINKAGE DONE", flush=True)
