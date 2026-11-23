"""Which convention reproduces the paper's utility numbers, and what are their intervals?

An independent recomputation gave top-k recall of 0.108 / 0.237 / 0.344 against the paper's 0.119 / 0.247 / 0.350 --
same ordering, different numbers. The paper's figures came from the per-fold nested fusion and the recomputation
from a fixed one, and the tie and rounding conventions may also differ. Rather than overwrite either, this tries the
candidate conventions, reports which reproduces the published values, and bootstraps an interval in that one.
"""
import json, itertools
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from scipy.stats import rankdata

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
TARGET = {0.01: 0.119, 0.05: 0.247, 0.10: 0.350}
rng = np.random.default_rng(0)

def z(a):
    a = np.asarray(a, np.float64); return (a - a.mean()) / (a.std() + 1e-12)

b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay", "scheme", "variant_id", "X"]], on=["assay", "scheme", "variant_id"], how="inner")
m = m.dropna(subset=["D", "Kermut", "AMK", "X", "y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")

def fusion(gs):
    return 0.40 * z(gs["Kermut"].to_numpy(float)) + 0.40 * z(gs["AMK"].to_numpy(float)) + 0.20 * z(gs["X"].to_numpy(float))

def recall(pred, y, frac, how):
    n = len(y)
    k = int(np.ceil(frac * n)) if how == "ceil" else max(1, int(round(frac * n)))
    pi = np.argsort(-pred)[:k]; ti = np.argsort(-y)[:k]
    return len(set(pi.tolist()) & set(ti.tolist())) / k

units = []
for aid, g in m.groupby("assay"):
    for sch, gs in g.groupby("scheme"):
        if len(gs) >= 20: units.append((aid, sch, gs))
assays = sorted({u[0] for u in units})
meta = ref.reindex(assays)
print(f"units {len(units)} | assays {len(assays)}", flush=True)

def agg_by_assay(val_by_unit):
    """mean over schemes per assay, then UniProt -> category -> mean."""
    s = pd.Series(val_by_unit).groupby(level=0).mean()
    df = pd.DataFrame({"v": s}).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

def agg_by_unit(val_by_unit):
    s = pd.Series(val_by_unit)
    df = pd.DataFrame({"v": s}).join(meta[["UniProt_ID", "coarse_selection_type"]], on=s.index.get_level_values(0))
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

for how in ("round", "ceil"):
    for aggname, aggf in (("by-assay", agg_by_assay), ("by-unit", agg_by_unit)):
        line = []
        vals = {}
        for k in (0.01, 0.05, 0.10):
            v = pd.Series({(aid, sch): recall(fusion(gs), gs["y"].to_numpy(float), k, how) for aid, sch, gs in units})
            vals[k] = (v, aggf)
            note = aggf(v)
            tgt = TARGET[k]
            line.append(f"{k:.0%}: {note:.3f} (target {tgt:.3f}, diff {note-tgt:+.3f})")
        print(f"  {how:5s} {aggname:9s} | " + " | ".join(line), flush=True)
        # if this is the closest, bootstrap it
        diffs = [abs(aggf(v) - TARGET[k]) for k, (v, aggf) in vals.items()]
        if max(diffs) < 0.006:
            print(f"    -> reproduces the target; bootstrapping", flush=True)
            out = {}
            for k, (v, f) in vals.items():
                boot = []
                for _ in range(2000):
                    aidx = rng.integers(0, len(assays), len(assays))
                    pick = [a for a in np.array(assays)[aidx]]
                    sub = v[v.index.get_level_values(0).isin(pick)]
                    if len(sub) < 10: continue
                    boot.append(f(sub))
                lo, hi = np.percentile(boot, [2.5, 97.5])
                out[str(k)] = {"recall": float(f(v)), "ci": [float(lo), float(hi)],
                               "lift": float(f(v) / k), "lift_ci": [float(lo / k), float(hi / k)]}
                print(f"      top-{k:.0%}: {f(v):.4f} [{lo:.4f}, {hi:.4f}] | lift {f(v)/k:.2f}x [{lo/k:.2f}x, {hi/k:.2f}x]", flush=True)
            json.dump(out, open(f"{R}/util_matched.json", "w"), indent=2)
print("UTIL MATCH DONE", flush=True)
