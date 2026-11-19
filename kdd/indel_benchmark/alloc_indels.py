"""Does the allocation finding replicate on the ProteinGym indel benchmark?

Second benchmark, different mutation type, different expert pool (three published supervised indel
models), same question: how much could ANY per-assay weighting of this pool gain over one tuned constant?
"""
import glob, os, itertools
import numpy as np, pandas as pd
from scipy.stats import spearmanr

MODELS = ["Embeddings_ESM1v_indels_predictions",
          "Embeddings_MSA_Transformer_indels_predictions",
          "Embeddings_Tranception_indels_predictions"]

rows = []
for f in sorted(glob.glob("DMS_supervised_indels_scores/fold_random_5/*.csv")):
    aid = os.path.basename(f)[:-4]
    d = pd.read_csv(f)
    d = d.dropna(subset=["DMS_score"])
    if len(d) < 50:
        continue
    y = d["DMS_score"].to_numpy()
    if np.std(y) == 0:
        continue
    X = np.column_stack([d[m].to_numpy() for m in MODELS])
    # standardise predictions within the assay so a blend is comparable across models
    X = (X - X.mean(0)) / (X.std(0) + 1e-12)
    base = [spearmanr(X[:, j], y).correlation for j in range(3)]
    rows.append({"assay": aid, "n": len(d), "y": y, "X": X, "base": base})

print("assays used:", len(rows), "| variants:", sum(r["n"] for r in rows))
print("mean per-model Spearman:")
for j, m in enumerate(MODELS):
    print(f"   {m.split('_')[1]:16s} {np.mean([r['base'][j] for r in rows]):.4f}")

# simplex grid over three weights
G = [w for w in itertools.product(np.linspace(0, 1, 11), repeat=3) if abs(sum(w) - 1) < 1e-9]
G = np.array(G)
print("grid points:", len(G))

def blend_sp(r, w):
    p = r["X"] @ w
    return spearmanr(p, r["y"]).correlation

# per-assay oracle: the best any weighting could do
oracle = np.array([max(blend_sp(r, w) for w in G) for r in rows])

# nested constant: weights chosen on the OTHER assays, applied to this one (assay-held-out)
nested = np.empty(len(rows))
best_w = np.empty((len(rows), 3))
for i, r in enumerate(rows):
    others = [q for k, q in enumerate(rows) if k != i]
    score = [np.mean([blend_sp(q, w) for q in others]) for w in G]
    j = int(np.argmax(score))
    best_w[i] = G[j]
    nested[i] = blend_sp(r, G[j])

# equal-weight and best-single references
equal = np.array([blend_sp(r, np.ones(3) / 3) for r in rows])
best_single = np.array([max(r["base"]) for r in rows])

print()
print(f"best single expert      {best_single.mean():.4f}")
print(f"equal-weight blend      {equal.mean():.4f}")
print(f"nested tuned constant   {nested.mean():.4f}")
print(f"per-assay oracle        {oracle.mean():.4f}")
print()
print(f"ALLOCATION HEADROOM (oracle - constant) = {oracle.mean() - nested.mean():+.4f}")
print(f"gain from tuning at all (constant - equal) = {nested.mean() - equal.mean():+.4f}")
print(f"nested constant beats best single by        {nested.mean() - best_single.mean():+.4f}")
print()
print("per-assay winning weights (mean over held-out assays):", np.round(best_w.mean(0), 3))
np.save("/tmp/pgindel/indel_oracle.npy", oracle)
np.save("/tmp/pgindel/indel_nested.npy", nested)
pd.DataFrame({"assay": [r["assay"] for r in rows], "n": [r["n"] for r in rows],
              "oracle": oracle, "nested": nested, "equal": equal, "best_single": best_single}
             ).to_csv("/tmp/pgindel/indel_allocation.csv", index=False)
