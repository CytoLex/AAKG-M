import os
"""Headline across seeds: union expert with old-E fallback, all 217 assays."""
import glob, json, os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata

CATS = ["Activity", "Binding", "Expression", "OrganismalFitness", "Stability"]
SCHEMES = ("fold_random_5", "fold_modulo_5", "fold_contiguous_5")
STEP = 0.1
PREFIX = os.environ.get("PREFIX", "preds_union_s")
W = Path(os.environ.get("AAKG_WORK", "."))              # bundle + cached predictions


def simplex4(step=STEP):
    n = int(round(1 / step)); out = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            for l in range(n + 1 - i - j):
                out.append((i * step, j * step, l * step, 1 - (i + j + l) * step))
    return np.array(out, float)


def sc_cols(RY, RV):
    a = RY - RY.mean(); b = RV - RV.mean(0)
    return (a @ b) / (np.sqrt((a ** 2).sum()) * np.sqrt((b ** 2).sum(0)) + 1e-12)


def assign_folds(assays, cats, k, s):
    rng = np.random.default_rng(s); fold = {}
    for c in CATS:
        a = np.array(sorted(x for x, cc in zip(assays, cats) if cc == c)); rng.shuffle(a)
        for i, x in enumerate(a): fold[x] = i % k
    return fold


def nested(df, col, assays, cats, fmap, grid):
    S = []
    for assay, g in df.groupby("assay", sort=True):
        acc = []
        for scheme in SCHEMES:
            gu = g[g.scheme == scheme]
            if len(gu) < 20 or gu["target"].nunique() < 3:
                continue
            y = gu["target"].to_numpy()
            cols = ["D_z", "Kermut_z", "AMK_z", col]
            acc.append(sc_cols(rankdata(y), rankdata(gu[cols].to_numpy(float) @ grid.T, axis=0)))
        S.append(np.mean(acc, 0) if acc else np.zeros(len(grid)))
    S = np.vstack(S)
    ch = np.empty(len(assays))
    for f in range(5):
        te, tr = fmap == f, fmap != f
        s2 = np.array([np.mean([S[tr][cats[tr] == c, i].mean() for c in CATS])
                       for i in range(S.shape[1])])
        ch[te] = S[te, int(np.argmax(s2))]
    return np.mean([ch[cats == c].mean() for c in CATS]), ch


def main():
    df = pd.read_csv(W / "data/oof_bundle.csv.gz")
    df = df.dropna(subset=["target", "D", "Kermut", "AMK"]).reset_index(drop=True)
    E = []
    for f in sorted(glob.glob(str(W / "results_verify" / "pred_both_s1_*.npz"))):
        z = np.load(f, allow_pickle=True)
        E.append(pd.DataFrame({"assay": z["assay"], "scheme": z["scheme"],
                               "variant_id": z["variant"], "E": z["pred"]}))
    df = df.merge(pd.concat(E, ignore_index=True), on=["assay", "scheme", "variant_id"], how="left")
    df["E"] = df["E"].fillna(0.0)
    assays = sorted(df["assay"].unique())
    cats = df.groupby("assay")["category"].first().reindex(assays).to_numpy()
    fmap = np.array([assign_folds(assays, cats, 5, 1)[a] for a in assays])
    grid = simplex4()

    def z(dfx, cols):
        out = dfx.copy()
        for c in cols:
            g = out.groupby("assay")[c]
            out[c + "_z"] = ((out[c] - g.transform("mean")) / g.transform("std")
                             .replace(0, np.nan)).fillna(0).clip(-8, 8)
        return out

    base = z(df, ["D", "Kermut", "AMK", "E"])
    old, old_ch = nested(base, "E_z", assays, cats, fmap, grid)
    print(f"old_E: {old:.6f}", flush=True)
    seeds, deltas = {}, {}
    all_ch = []
    for s in range(1, 9):
        f = W / "results_verify" / f"{PREFIX}_s{s}.csv"
        if not f.exists():
            print(f"seed {s}: no predictions", flush=True); continue
        U = pd.read_csv(f).rename(columns={"pred": f"U{s}"})
        d2 = df.merge(U, on=["assay", "scheme", "variant_id"], how="left")
        d2[f"X{s}"] = d2[f"U{s}"].fillna(d2["E"])
        d2 = z(d2, ["D", "Kermut", "AMK", "E", f"X{s}"])
        sc, ch = nested(d2, f"X{s}_z", assays, cats, fmap, grid)
        all_ch.append(ch)
        seeds[s] = float(sc); deltas[s] = float(sc - old)
        print(f"seed {s}: {sc:.6f}  delta {sc-old:+.6f}", flush=True)
    arr = np.array(list(seeds.values()))
    dd = np.array(list(deltas.values()))
    np.save(W / "results_verify" / f"ch_{PREFIX}.npy", np.vstack(all_ch))
    # two-level bootstrap: assays within category, seeds resampled
    rng2 = np.random.default_rng(20261109)
    CH = np.vstack(all_ch)            # (n_seeds, n_assays)
    dmat = CH - old_ch[None, :]       # paired per assay per seed
    boot = []
    for _ in range(4000):
        sel = np.concatenate([np.where(cats == c)[0][
            rng2.integers(0, (cats == c).sum(), (cats == c).sum())] for c in CATS])
        ss = rng2.integers(0, CH.shape[0], CH.shape[0])
        boot.append(np.mean([np.mean([dmat[k][sel][cats[sel] == c].mean() for c in CATS])
                             for k in ss]))
    blo, bhi = np.percentile(boot, [2.5, 97.5])
    print(f"two-level CI for delta: [{blo:+.6f}, {bhi:+.6f}]", flush=True)
    out = {"assays": len(assays), "old_E": float(old), "per_seed": seeds,
           "ci_two_level": [float(blo), float(bhi)],
           "mean": float(arr.mean()), "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
           "delta_mean": float(dd.mean()),
           "delta_sd": float(dd.std(ddof=1)) if len(dd) > 1 else 0.0,
           "delta_min": float(dd.min()), "n_seeds": len(arr)}
    print(json.dumps(out, indent=1), flush=True)
    (W / "results_verify" / f"headline_{PREFIX}.json").write_text(json.dumps(out, indent=2))
    print("HS_DONE", flush=True)


if __name__ == "__main__":
    main()
