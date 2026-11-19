"""Three-expert reference on exactly the assay set the encoder run used. No training."""
import os, glob, json, itertools, numpy as np, pandas as pd
from scipy.stats import spearmanr
R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
W = f"{R}/indel-benchmark-1119"
def z(a):
    a = np.asarray(a, dtype=np.float64); return (a - a.mean()) / (a.std() + 1e-12)
def sp(a, b): return spearmanr(a, b).correlation
data = []
for f in sorted(glob.glob(f"{W}/out/*.npz")):
    aid = os.path.basename(f)[:-4]
    bench = pd.read_csv(f"{W}/data/DMS_ProteinGym_indels/{aid}.csv")
    frag = f"{W}/folds/cv_folds_indels/{aid}.csv"
    if not os.path.exists(frag): continue
    fo = pd.read_csv(frag)[["mutated_sequence", "fold_random_5"]]
    merged = bench.reset_index().merge(fo, on="mutated_sequence", how="left").sort_values("index")
    if merged.fold_random_5.isna().any(): continue
    z0 = np.load(f, allow_pickle=True)
    y, P = z0["y"], z0["P"]
    if len(y) != len(bench): continue
    ok = np.isfinite(y)
    # no variant floor: match the encoder run, which kept every assay with a complete fold join
    data.append({"id": aid, "y": y[ok], "P": P[ok]})
n = len(data); print("assays:", n, flush=True)
base = np.array([[sp(d["P"][:, j], d["y"]) for j in range(3)] for d in data])
print("published experts mean:", base.mean(0).round(4), flush=True)
cols = [[z(d["P"][:, j]) for j in range(3)] for d in data]
G = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=3) if abs(sum(w)-1) < 1e-9])
S = np.empty((len(G), n))
for gi, w in enumerate(G):
    for i in range(n):
        S[gi, i] = sp(sum(a*b for a, b in zip(w, cols[i])), data[i]["y"])
nested = np.empty(n)
for i in range(n):
    others = (S.sum(axis=1) - S[:, i]) / (n-1); nested[i] = S[int(np.argmax(others)), i]
print(f"3-expert: nested {nested.mean():.4f} | oracle {S.max(axis=0).mean():.4f} "
      f"| headroom {S.max(axis=0).mean()-nested.mean():+.4f}", flush=True)
json.dump({"n": n, "base": base.mean(0).tolist(), "nested": float(nested.mean()),
           "oracle": float(S.max(axis=0).mean())}, open(f"{W}/out/ref3.json", "w"), indent=2)
print("REF3 DONE", flush=True)
