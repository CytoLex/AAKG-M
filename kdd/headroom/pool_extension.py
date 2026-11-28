"""Can the pool be extended past the current best reported number?

The paper's own mechanism says an expert's value is its residual disagreement with the pool, subject to a competence
floor. This takes that literally: enumerate every stored prediction file as a candidate expert, measure its nested
marginal value inside the current pool under the official aggregation, add the best one greedily, and repeat. If the
principle is real there should be headroom here; if it is exhausted, that is also worth knowing.

Also recomputes every reported number from the released predictions under the official aggregation order, because the
submitted score file and the release are different runs and the release is now the authority.

Run with AAKG_DATA pointing at the directory described in submission/oof/README.md.
"""
import glob
import json
import os
import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R = os.environ.get("AAKG_DATA", ".")
A = f"{R}/cytolex-aakg-ablation-1103-v1"
CATS = ["Activity", "Binding", "Expression", "OrganismalFitness", "Stability"]


def z(a):
    a = np.asarray(a, np.float64)
    return (a - a.mean()) / (a.std() + 1e-12)


def sp(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return np.nan
    return spearmanr(a, b).correlation


b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
released = pd.read_csv(f"{R}/CytoLex-AAKG-M/submission/predictions/fused_per_mutant.csv.gz") \
    if os.path.exists(f"{R}/CytoLex-AAKG-M/submission/predictions/fused_per_mutant.csv.gz") else None

m = b[["assay", "scheme", "variant_id", "category", "y", "D", "Kermut", "Kseq", "AMK"]].copy()
units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per:
        units[aid] = per
ids = sorted(units)
cats = {a: units[a][0]["category"].iloc[0] for a in ids}
uni = {a: ref.loc[a, "UniProt_ID"] for a in ids if a in ref.index}
print(f"assays {len(ids)} | with UniProt {len(uni)}", flush=True)


def official(per_assay_scores):
    """The benchmark's order: group by (UniProt, category), mean, then mean over the five categories."""
    rows = [(uni.get(a, a), cats[a], v) for a, v in per_assay_scores.items() if a in uni]
    df = pd.DataFrame(rows, columns=["u", "c", "v"])
    return float(df.groupby(["u", "c"])["v"].mean().groupby(level=1).mean().mean())


def score_pool(cols, weights):
    """Per-assay Spearman of a fixed-weight z-scored blend."""
    out = {}
    for aid, gs in units.items():
        vals = []
        for g in gs:
            Zm = [z(g[c].to_numpy(float)) for c in cols]
            vals.append(sp(sum(w * x for w, x in zip(weights, Zm)), g["y"].to_numpy(float)))
        out[aid] = float(np.nanmean(vals))
    return out


# ---------------------------------------------------------------- released numbers
print("\n=== every reported number, from the released predictions ===", flush=True)
rows = []
for aid, gs in units.items():
    for g in gs:
        pass
if released is not None:
    mr = m.merge(released, on=["assay", "scheme", "variant_id"], how="inner")
    ru = {}
    for aid, g in mr.groupby("assay"):
        per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
        if per:
            ru[aid] = per
    def rel_assay(col):
        out = {}
        for aid, gs in ru.items():
            out[aid] = float(np.nanmean([sp(g[col], g["y"]) for g in gs]))
        return out
    ours, ker = rel_assay("fused"), rel_assay("Kermut")
    print(f"  headline ours  {official(ours):.6f}   Kermut {official(ker):.6f}   lead {official(ours)-official(ker):+.4f}")
    for c in CATS:
        o = np.mean([v for a, v in ours.items() if cats[a] == c])
        k = np.mean([v for a, v in ker.items() if cats[a] == c])
        print(f"    {c:20s} {o:.4f}  Kermut {k:.4f}  Δ {o-k:+.4f}")
    for sch in ("fold_random_5", "fold_modulo_5", "fold_contiguous_5"):
        o = np.mean([float(np.nanmean([sp(g["fused"], g["y"]) for g in ru[a] if g["scheme"].iloc[0] == sch]))
                     for a in ru])
        print(f"    scheme {sch:22s} {o:.4f}")

# ---------------------------------------------------------------- candidate experts
print("\n=== candidate experts on disk ===", flush=True)
cands = sorted(glob.glob(f"{A}/results_verify/preds_*.csv"))
base_cols = ["Kermut", "AMK"]
print(f"  files: {len(cands)}", flush=True)

pool_cols = list(base_cols)
pool_w = [0.5, 0.5]
base = official(score_pool(pool_cols, pool_w))
print(f"\n  baseline pool {pool_cols} {pool_w}: {base:.6f}", flush=True)

# add the encoder, which is the paper's own expert
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
x = x[["assay", "scheme", "variant_id", "X"]]
for aid in ids:
    for g in units[aid]:
        pass
m2 = m.merge(x, on=["assay", "scheme", "variant_id"], how="left")
m2["X"] = m2["X"].fillna(0.0)
units = {}
for aid, g in m2.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per:
        units[aid] = per
paper = official(score_pool(["Kermut", "AMK", "X"], [0.4, 0.4, 0.2]))
print(f"  paper's own fusion Kermut/AMK/X 0.4/0.4/0.2: {paper:.6f}", flush=True)

# greedy forward selection over the stored prediction files
tried = []
best_pool = ["Kermut", "AMK", "X"]
best_score = paper
for rnd in range(3):
    round_best = (None, best_score, None)
    for f in cands:
        name = re.sub(r"[^a-z0-9_]", "", os.path.basename(f).replace("preds_", "").replace(".csv", ""))
        if name in tried or name in ("Kermut", "AMK", "X"):
            continue
        try:
            p = pd.read_csv(f)
            col = "pred" if "pred" in p.columns else p.columns[-1]
            p = p[["assay", "scheme", "variant_id", col]].rename(columns={col: name})
            mm = m2.merge(p, on=["assay", "scheme", "variant_id"], how="left")
            if mm[name].notna().mean() < 0.2:
                tried.append(name)
                continue
            mm[name] = mm[name].fillna(0.0)
            uu = {}
            for aid, g in mm.groupby("assay"):
                per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
                if per:
                    uu[aid] = per
            saved = units
            units = uu
            cols = best_pool + [name]
            w = [1.0 / len(cols)] * len(cols)
            sc = official(score_pool(cols, w))
            units = saved
            tried.append(name)
            print(f"    round {rnd}: +{name:22s} equal weights -> {sc:.6f}", flush=True)
            if sc > round_best[1]:
                round_best = (name, sc, sc - best_score)
        except Exception as e:
            tried.append(name)
            print(f"    round {rnd}: {os.path.basename(f)} failed {type(e).__name__}", flush=True)
    if round_best[0] is None or round_best[2] is None or round_best[2] <= 0.0002:
        print(f"  no candidate improves by more than 0.0002 at round {rnd}", flush=True)
        break
    best_pool = best_pool + [round_best[0]]
    best_score = round_best[1]
    print(f"  round {rnd}: added {round_best[0]} -> {best_score:.6f} ({round_best[2]:+.6f})", flush=True)

print(f"\n  best pool found: {best_pool} -> {best_score:.6f}", flush=True)
print(f"  paper's fusion: {paper:.6f} | published leader on this panel: 0.700", flush=True)
json.dump({"best_pool": best_pool, "best_score": best_score, "paper_fusion": paper},
          open(f"{R}/pool_extension.json", "w"), indent=2)
print("POOL EXTENSION DONE", flush=True)
