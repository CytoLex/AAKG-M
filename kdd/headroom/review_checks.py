"""Robustness checks on the thirteen expert-into-pool points.

A reviewer asked whether r = +0.786 between disagreement and marginal value survives three checks: whether it is
driven by one expert, whether pools that already contain that expert behave differently, and whether disagreement
carries information beyond standalone accuracy. This script answers all three from the same computation that
produces Figure 1's right panel.

Run with AAKG_DATA pointing at the directory described in submission/oof/README.md.
"""
import itertools
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

R = os.environ.get("AAKG_DATA", ".")
A = f"{R}/cytolex-aakg-ablation-1103-v1"


def z(a):
    a = np.asarray(a, np.float64)
    return (a - a.mean()) / (a.std() + 1e-12)


def sp(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return np.nan
    return spearmanr(a, b).correlation


def grid(k, step=0.1):
    n = int(round(1 / step))
    return np.array([w for w in itertools.product(np.linspace(0, 1, n + 1), repeat=k) if abs(sum(w) - 1) < 1e-9])


b = pd.read_csv(f"{A}/data/oof_bundle.csv.gz").rename(columns={"target": "y"})
x = pd.read_csv(f"{A}/results_verify/preds_savg_s1.csv").rename(columns={"pred": "X"})
m = b.merge(x[["assay", "scheme", "variant_id", "X"]], on=["assay", "scheme", "variant_id"], how="inner")
m = m.dropna(subset=["D", "Kermut", "Kseq", "AMK", "X", "y"])
ref = pd.read_csv(f"{A}/ref_slim.csv").set_index("DMS_id")
EXPERTS = ["D", "Kermut", "Kseq", "AMK", "X"]

units = {}
for aid, g in m.groupby("assay"):
    per = [gs for _, gs in g.groupby("scheme") if len(gs) >= 20]
    if per:
        units[aid] = per
ids = sorted(units)
meta = ref.reindex(ids)
print(f"assays {len(ids)} | experts {EXPERTS}", flush=True)


def sc(aid, cols, w):
    vals = []
    for gs in units[aid]:
        Zm = [z(gs[c].to_numpy(float)) for c in cols]
        vals.append(sp(sum(a * c for a, c in zip(w, Zm)), gs["y"].to_numpy(float)))
    return float(np.nanmean(vals))


def agg(v):
    df = pd.DataFrame({"v": np.asarray(v, float)}, index=ids).join(meta[["UniProt_ID", "coarse_selection_type"]])
    return float(df.groupby(["UniProt_ID", "coarse_selection_type"])["v"].mean().groupby(level=1).mean().mean())


def nested(cols):
    G = grid(len(cols))
    S = np.empty((len(G), len(ids)))
    for gi, w in enumerate(G):
        for i, aid in enumerate(ids):
            S[gi, i] = sc(aid, cols, w)
    n = len(ids)
    return agg(np.array([S[int(np.argmax((S.sum(1) - S[:, i]) / (n - 1))), i] for i in range(n)]))


def disagreement(aid, e, pool):
    pe = np.concatenate([z(gs[e].to_numpy(float)) for gs in units[aid]])
    rp = np.concatenate([np.mean([z(gs[c].to_numpy(float)) for c in pool], axis=0) for gs in units[aid]])
    return 1.0 - abs(sp(pe, rp))


rows = []
for e in EXPERTS:
    rest = [c for c in EXPERTS if c != e]
    solo = agg(np.array([sc(aid, [e], np.array([1.0])) for aid in ids]))
    base = nested(rest)
    full = nested(rest + [e])
    dis = float(np.nanmean([disagreement(aid, e, rest) for aid in ids]))
    rows.append(dict(pool="+".join(rest), expert=e, solo=solo, marginal=full - base, disagree=dis))
    print(f"  {e:7s} solo {solo:.4f} | marginal {full - base:+.4f} | disagree {dis:.3f}", flush=True)

for combo in (["D", "Kermut"], ["Kermut", "AMK"], ["D", "Kermut", "AMK"]):
    base = nested(combo)
    for e in [c for c in EXPERTS if c not in combo]:
        full = nested(combo + [e])
        dis = float(np.nanmean([disagreement(aid, e, combo) for aid in ids]))
        rows.append(dict(pool="+".join(combo), expert=e, solo=np.nan, marginal=full - base, disagree=dis))
        print(f"  {e:7s} into {'+'.join(combo):16s} marginal {full - base:+.4f} | disagree {dis:.3f}", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{R}/pts13_review.csv", index=False)
print()
print(d.round(4).to_string(index=False))
print()


def report(df, label):
    if len(df) < 3:
        print(f"{label:34s} n={len(df)} -> too few for a correlation")
        return
    r = float(spearmanr(df.disagree, df.marginal).correlation)
    pr = float(pearsonr(df.disagree, df.marginal)[0])
    print(f"{label:34s} n={len(df):2d} | spearman {r:+.3f} | pearson {pr:+.3f}")


print("=== the correlation under the reviewer's checks ===")
report(d, "all points")
report(d[d.expert != "X"], "dropping our encoder X")
report(d[d.pool.str.contains("X")], "pools that contain X")
report(d[~d.pool.str.contains("X")], "pools that do not contain X")
report(d[d.expert.isin(["D", "Kermut", "Kseq"])], "published experts only")

dd = d.dropna(subset=["solo"])


def partial(df, a_, b_, c_):
    ra = df[a_] - np.polyval(np.polyfit(df[c_], df[a_], 1), df[c_])
    rb = df[b_] - np.polyval(np.polyfit(df[c_], df[b_], 1), df[c_])
    return float(pearsonr(ra, rb)[0])


print()
print(f"=== does disagreement explain beyond standalone accuracy (n={len(dd)} rows with a solo score) ===")
print(f"  r(solo, marginal)                          {float(spearmanr(dd.solo, dd.marginal).correlation):+.3f}")
print(f"  partial r(disagree, marginal | solo)       {partial(dd, 'disagree', 'marginal', 'solo'):+.3f}")
json.dump({"rows": d.to_dict("records")}, open(f"{R}/review_checks.json", "w"), indent=2)
print("REVIEW CHECKS DONE", flush=True)
