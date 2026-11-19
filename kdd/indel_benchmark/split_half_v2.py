"""Split-half with the same reference the substitution paper uses: the tuned constant.

Paper: 'weights selected on A and evaluated on B transfer a gain of +0.0041, which is 49% of the +0.0083
obtainable when selection and evaluation share variants.'  Reference = the tuned constant.
"""
import glob, os, itertools
import numpy as np, pandas as pd
from scipy.stats import spearmanr

MODELS = ["Embeddings_ESM1v_indels_predictions",
          "Embeddings_MSA_Transformer_indels_predictions",
          "Embeddings_Tranception_indels_predictions"]
G = np.array([w for w in itertools.product(np.linspace(0,1,11), repeat=3) if abs(sum(w)-1) < 1e-9])
rng = np.random.default_rng(0)

rows = []
for f in sorted(glob.glob("DMS_supervised_indels_scores/fold_random_5/*.csv")):
    d = pd.read_csv(f).dropna(subset=["DMS_score"])
    if len(d) < 50: continue
    y = d["DMS_score"].to_numpy()
    if np.std(y) == 0: continue
    rows.append({"assay": os.path.basename(f)[:-4], "n": len(d), "y": y,
                 "X": np.column_stack([d[m].to_numpy() for m in MODELS])})
def sp(p, y): return spearmanr(p, y).correlation

# the tuned constant: one weight vector chosen on the whole panel (assay-independent)
Xall = np.vstack([r["X"] for r in rows]); yall = np.concatenate([r["y"] for r in rows])
# assay-standardised stacking
Xa, ya = [], []
for r in rows:
    Xa.append((r["X"] - r["X"].mean(0)) / (r["X"].std(0)+1e-12)); ya.append(r["y"])
const_w = G[int(np.argmax([np.mean([sp(Xa[i] @ w, ya[i]) for i in range(len(rows))]) for w in G]))]
print("tuned constant weights:", np.round(const_w, 2))

inplace, transfer, constB = [], [], []
for r in rows:
    n = len(r["y"]); idx = rng.permutation(n); A, B = idx[:n//2], idx[n//2:]
    mu, sd = r["X"][A].mean(0), r["X"][A].std(0)+1e-12
    XA, XB = (r["X"][A]-mu)/sd, (r["X"][B]-mu)/sd
    yA, yB = r["y"][A], r["y"][B]
    j = int(np.argmax([sp(XA @ w, yA) for w in G])); w = G[j]
    inplace.append(sp(XA @ w, yA) - sp(XA @ const_w, yA))
    transfer.append(sp(XB @ w, yB) - sp(XB @ const_w, yB))
    constB.append(sp(XB @ const_w, yB))
ip, tr = np.array(inplace), np.array(transfer)
print(f"\nassays {len(rows)}")
print(f"in-place gain of the per-assay oracle over the constant : {ip.mean():+.4f}")
print(f"the same weights on the disjoint half B                 : {tr.mean():+.4f}")
print(f"fraction surviving the split                            : {tr.mean()/ip.mean():.0%}")
d = pd.DataFrame({"assay":[r["assay"] for r in rows], "n":[r["n"] for r in rows],
                  "inplace":ip, "transfer":tr})
d.to_csv("/tmp/pgindel/indel_split_half.csv", index=False)
print("\nby assay size:")
d["q"] = pd.qcut(d.n, 4, labels=["Q1 small","Q2","Q3","Q4 large"], duplicates="drop")
print(d.groupby("q", observed=True).agg(assays=("n","size"), median_n=("n","median"),
      inplace=("inplace","mean"), transfer=("transfer","mean")).round(4).to_string())
