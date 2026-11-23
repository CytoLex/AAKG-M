"""An interval on the rule's advantage, which the first run did not have.

The rule beat Spearman-optimised weights by +0.0106 in top-5% recall on a single averaged figure. The learned
shrinkage gate looked like a win at +0.0003 and +0.0013 under the same kind of reporting and became -0.0002 with
an interval excluding zero once it was properly averaged. This puts the same interval on the rule before it is
claimed: per-assay scores, paired, bootstrapped over assays with the official re-aggregation inside each resample.

Also repeats at k = 1% and 10%, since only 5% was tested.
"""
import itertools, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R = "/inspire/ssd/project/scientific-evidence-protocol/tangkezheng-253108540239"
A = f"{R}/cytolex-aakg-ablation-1103-v1"
LAMS = [0.0, 0.25, 0.5, 0.75, 1.0]
REPS = 4

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
G = grid(4)
rng = np.random.default_rng(0)

def score(aid, w, half, kind, frac):
    v = []
    for si, gs in enumerate(units[aid]):
        g = gs if half is None else gs.iloc[half[si]]
        Zm = [z(g[c].to_numpy(float)) for c in COLS]
        pred = sum(a * c for a, c in zip(w, Zm)); y = g["y"].to_numpy(float)
        v.append(topk(pred, y, frac) if kind == "topk" else sp(pred, y))
    return float(np.nanmean(v))

def agg(vals, idx=None):
    idx = np.arange(n) if idx is None else idx
    df = pd.DataFrame({"v": np.asarray(vals)[idx]}, index=[ids[i] for i in idx]).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())

for FRAC in (0.01, 0.05, 0.10):
    print(f"\n=== top-k {FRAC:.0%} ===", flush=True)
    acc = {k: np.zeros(n) for k in ("rule", "spearman", "constant")}
    for rep in range(REPS):
        halves = {aid: [np.array_split(rng.permutation(len(gs)), 2) for gs in units[aid]] for aid in ids}
        HA = {aid: [h[0] for h in halves[aid]] for aid in ids}
        HB = {aid: [h[1] for h in halves[aid]] for aid in ids}
        S = {}
        for kind in ("topk", "spearman"):
            M = np.empty((len(G), n))
            for gi, w in enumerate(G):
                for i, aid in enumerate(ids): M[gi, i] = score(aid, w, HA[aid], kind, FRAC)
            S[kind] = M
        const = {k: [G[int(np.argmax((v.sum(axis=1) - v[:, i]) / (n - 1)))] for i in range(n)] for k, v in S.items()}
        per = {k: [G[int(np.argmax(v[:, i]))] for i in range(n)] for k, v in S.items()}
        lam = {}
        for kind, v in S.items():
            cand = {l: np.array([score(ids[i], (1 - l) * const[kind][i] + l * per[kind][i], HA[ids[i]], kind, FRAC) for i in range(n)])
                    for l in LAMS}
            lam[kind] = [max(LAMS, key=lambda l: np.mean([cand[l][j] for j in range(n) if j != i])) for i in range(n)]
        rule = np.array([score(ids[i], (1 - lam["topk"][i]) * const["topk"][i] + lam["topk"][i] * per["topk"][i], HB[ids[i]], "topk", FRAC) for i in range(n)])
        spw = np.array([score(ids[i], (1 - lam["spearman"][i]) * const["spearman"][i] + lam["spearman"][i] * per["spearman"][i], HB[ids[i]], "topk", FRAC) for i in range(n)])
        cst = np.array([score(ids[i], const["topk"][i], HB[ids[i]], "topk", FRAC) for i in range(n)])
        acc["rule"] += rule / REPS; acc["spearman"] += spw / REPS; acc["constant"] += cst / REPS
        print(f"  rep {rep+1}/{REPS}", flush=True)
    for k in acc:
        print(f"  {k:10s} {agg(acc[k]):.4f}", flush=True)
    ds = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        ds.append(agg(acc["rule"], idx) - agg(acc["spearman"], idx))
    lo, hi = np.percentile(ds, [2.5, 97.5])
    print(f"  rule - spearman: {np.mean(ds):+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  P(rule>sp)={np.mean(np.array(ds)>0):.2f}", flush=True)
    ds2 = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        ds2.append(agg(acc["rule"], idx) - agg(acc["constant"], idx))
    lo2, hi2 = np.percentile(ds2, [2.5, 97.5])
    print(f"  rule - constant: {np.mean(ds2):+.4f}  95% CI [{lo2:+.4f}, {hi2:+.4f}]", flush=True)
    json.dump({"frac": FRAC, "rule": agg(acc["rule"]), "spearman": agg(acc["spearman"]), "constant": agg(acc["constant"]),
               "rule_minus_spearman": [float(lo), float(hi)], "rule_minus_constant": [float(lo2), float(hi2)]},
              open(f"{R}/rule_ci_{int(FRAC*100)}.json", "w"), indent=2)
print("\nRULE CI DONE", flush=True)
