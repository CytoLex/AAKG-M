#!/usr/bin/env python3
"""Cross-assay supervised meta-stacker over frozen OOF predictions.

The base predictions are already out-of-fold.  For each held-out assay, the
meta-model is fit on all *other* assays and applied to the held-out assay.
No target label of the held-out assay is used for fitting or scaling.

This is a diagnostic for the supervised-leaderboard setting: it uses the full
training panel, not just per-assay inner-CV selection.
"""
import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(os.environ.get("AAKG_ROOT", Path(__file__).resolve().parent))
DATA = ROOT / "data"
FULL = DATA / "oof_predictions.csv"
KSEQ = DATA / "kseq_oof_predictions.csv"
DEV_UNITS = DATA / "dev20_units"
AMK197_UNITS = DATA / "amk197_units"
CONTRACT = DATA / "contract.json"
BUNDLE = DATA / "oof_bundle.csv.gz"
OUT = ROOT / "results" / "run"


def load_oof():
    if BUNDLE.exists():
        meta = pd.read_csv(BUNDLE)
        required = {"assay", "scheme", "variant_id", "fold", "category",
                    "target", "D", "Kermut", "Kseq", "AMK"}
        missing = required.difference(meta.columns)
        if missing:
            raise ValueError(f"OOF bundle missing columns: {sorted(missing)}")
        return meta.dropna(subset=["target", "D", "Kermut", "Kseq", "AMK"]).reset_index(drop=True)

    full = pd.read_csv(
        FULL,
        usecols=["assay", "scheme", "variant", "fold", "target_common_std",
                 "D_common_std", "Kermut_common_std"],
    ).rename(columns={
        "variant": "variant_id", "target_common_std": "target",
        "D_common_std": "D", "Kermut_common_std": "Kermut",
    })
    kseq = pd.read_csv(
        KSEQ,
        usecols=["assay", "scheme", "variant", "fold", "K_feature_common_std"],
    ).rename(columns={"variant": "variant_id", "K_feature_common_std": "Kseq"})
    full = full.merge(
        kseq, on=["assay", "scheme", "variant_id", "fold"], how="inner", validate="one_to_one"
    )
    if len(full) != len(kseq):
        raise ValueError(f"Kseq merge changed rows: {len(full)} vs {len(kseq)}")

    rows = []
    for root in (DEV_UNITS, AMK197_UNITS):
        for path in sorted(root.glob("*/*/oof.csv")):
            assay = path.parent.parent.name
            scheme = path.parent.name
            d = pd.read_csv(path, usecols=["variant_id", "fold", "AMK_common"])
            d["assay"] = assay
            d["scheme"] = scheme
            rows.append(d)
    amk = pd.concat(rows, ignore_index=True)
    if amk.duplicated(["assay", "scheme", "variant_id", "fold"]).any():
        raise ValueError("duplicate AMK OOF keys")
    meta = full.merge(
        amk, on=["assay", "scheme", "variant_id", "fold"], how="inner", validate="one_to_one"
    )
    if len(meta) != len(full):
        raise ValueError(f"merged {len(meta)} of {len(full)} full OOF rows")
    meta = meta.rename(columns={"AMK_common": "AMK"})
    meta = meta.dropna(subset=["target", "D", "Kermut", "Kseq", "AMK"]).reset_index(drop=True)
    return meta


def add_features(meta, use_z=True):
    # Per-assay feature normalization.  This uses predictions only, never target.
    for col in ("D", "Kermut", "Kseq", "AMK"):
        if use_z:
            g = meta.groupby("assay")[col]
            mu = g.transform("mean")
            sd = g.transform("std").replace(0.0, np.nan)
            meta[col + "_z"] = ((meta[col] - mu) / sd).fillna(0.0).clip(-8.0, 8.0)
        else:
            meta[col + "_z"] = meta[col]

    meta["D_minus_K"] = meta["D_z"] - meta["Kermut_z"]
    meta["AMK_minus_K"] = meta["AMK_z"] - meta["Kermut_z"]
    meta["AMK_minus_D"] = meta["AMK_z"] - meta["D_z"]
    meta["Kseq_minus_K"] = meta["Kseq_z"] - meta["Kermut_z"]
    meta["D_x_K"] = meta["D_z"] * meta["Kermut_z"]
    meta["D_x_AMK"] = meta["D_z"] * meta["AMK_z"]
    meta["K_x_AMK"] = meta["Kermut_z"] * meta["AMK_z"]
    meta["D_sq"] = meta["D_z"] ** 2
    meta["K_sq"] = meta["Kermut_z"] ** 2
    meta["AMK_sq"] = meta["AMK_z"] ** 2

    counts = meta.groupby("assay")["target"].transform("size")
    meta["log_n"] = np.log1p(counts)
    meta["n_centered"] = meta["log_n"] - meta["log_n"].mean()

    categories = sorted(meta["category"].dropna().unique().tolist())
    for cat in categories:
        meta["cat_" + cat] = (meta["category"] == cat).astype(np.float32)
    return meta, categories


def add_context(meta, categories):
    """Assay-level context, computed only from predictions and metadata (no target)."""
    g = meta.groupby("assay")
    stats = g.agg(
        n=("target", "size"),
        D_mean=("D", "mean"), D_std=("D", "std"),
        K_mean=("Kermut", "mean"), K_std=("Kermut", "std"),
        A_mean=("AMK", "mean"), A_std=("AMK", "std"),
        Q_mean=("Kseq", "mean"), Q_std=("Kseq", "std"),
    )
    corr = g.apply(
        lambda x: pd.Series({
            "D_K_corr": x["D"].corr(x["Kermut"]),
            "D_A_corr": x["D"].corr(x["AMK"]),
            "K_A_corr": x["Kermut"].corr(x["AMK"]),
            "Q_K_corr": x["Kseq"].corr(x["Kermut"]),
            "Q_A_corr": x["Kseq"].corr(x["AMK"]),
            "Q_D_corr": x["Kseq"].corr(x["D"]),
        }), include_groups=False
    )
    stats = stats.join(corr)
    stats["log_n"] = np.log1p(stats["n"])
    for c in stats.columns:
        if c == "n":
            continue
        mu = stats[c].mean()
        sd = stats[c].std()
        stats[c + "_z"] = ((stats[c] - mu) / sd).fillna(0.0).clip(-8.0, 8.0)
    meta = meta.merge(stats.drop(columns=["n"]), left_on="assay", right_index=True, how="left")
    ctx = ["log_n_z", "D_std_z", "K_std_z", "A_std_z", "Q_std_z",
           "D_K_corr_z", "D_A_corr_z", "K_A_corr_z",
           "Q_K_corr_z", "Q_A_corr_z", "Q_D_corr_z"] + ["cat_" + c for c in categories]
    for b in ("D", "Kermut", "Kseq", "AMK"):
        for c in ctx:
            meta[f"{b}_x_{c}"] = meta[b] * meta[c]
    return meta


def design_contextual(meta, categories, with_kseq=False):
    base = ["D", "Kermut"] + (["Kseq"] if with_kseq else []) + ["AMK"]
    ctx = ["log_n_z", "D_std_z", "K_std_z", "A_std_z"]
    if with_kseq:
        ctx += ["Q_std_z", "Q_K_corr_z", "Q_A_corr_z", "Q_D_corr_z"]
    ctx += ["D_K_corr_z", "D_A_corr_z", "K_A_corr_z"] + ["cat_" + c for c in categories]
    cols = list(base) + ["log_n_z"] + ["cat_" + c for c in categories]
    for b in base:
        for c in ctx:
            cols.append(f"{b}_x_{c}")
    X = meta[cols].to_numpy(dtype=np.float64)
    # Global unsupervised standardization; target is not used.
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    X = (X - mu) / sd
    X = np.column_stack([np.ones(len(X)), X])
    return X, cols


def design(meta, categories, mode, drop_amk=False, drop_category=False, with_kseq=False):
    base = ["D_z", "Kermut_z"] + (["Kseq_z"] if with_kseq else []) + ([] if drop_amk else ["AMK_z"]) + ["n_centered"]
    if not drop_category:
        base += ["cat_" + c for c in categories]
    if mode == "linear":
        cols = base
    elif mode == "interactions":
        cols = base + ["D_minus_K", "D_x_K", "D_sq", "K_sq"]
        if with_kseq:
            cols += ["Kseq_minus_K"]
        if not drop_amk:
            cols += ["AMK_minus_K", "AMK_minus_D", "D_x_AMK", "K_x_AMK", "AMK_sq"]
    else:
        raise ValueError(mode)
    X = meta[cols].to_numpy(dtype=np.float64)
    X = np.column_stack([np.ones(len(X)), X])
    return X, cols


def fit_predict_loao(meta, X, y, assays):
    """Closed-form leave-one-assay-out ridge; intercept is not penalized."""
    n_feat = X.shape[1]
    gram = np.zeros((n_feat, n_feat), dtype=np.float64)
    xty = np.zeros(n_feat, dtype=np.float64)
    per = {}
    for assay, idx in meta.groupby("assay").indices.items():
        Xa = X[idx]
        ya = y[idx]
        ga = Xa.T @ Xa
        ha = Xa.T @ ya
        per[assay] = (ga, ha, idx)
        gram += ga
        xty += ha
    pred = np.full(len(meta), np.nan, dtype=np.float64)
    alpha = 1.0
    penalty = np.eye(n_feat) * alpha
    penalty[0, 0] = 0.0
    coefs = {}
    for assay, (ga, ha, idx) in per.items():
        g = gram - ga
        h = xty - ha
        w = np.linalg.solve(g + penalty, h)
        pred[idx] = X[idx] @ w
        coefs[assay] = w.tolist()
    return pred, coefs


def metrics(meta, pred_col):
    rows = []
    for (assay, scheme, category), g in meta.groupby(["assay", "scheme", "category"], sort=False):
        if len(g) < 5 or g["target"].nunique() < 3:
            continue
        rec = {"assay": assay, "scheme": scheme, "category": category, "n": len(g)}
        for arm, col in (("AMK", "AMK"), ("D", "D"), ("Kermut", "Kermut"),
                         ("Kseq", "Kseq"), ("Blend", "Blend"), ("Meta", pred_col)):
            r = spearmanr(g["target"].to_numpy(), g[col].to_numpy()).statistic
            rec[arm] = float(r) if r == r else np.nan
        rows.append(rec)
    per = pd.DataFrame(rows)
    cats = per.groupby("category")[["AMK", "D", "Kermut", "Kseq", "Blend", "Meta"]].mean()
    schemes = per.groupby("scheme")[["AMK", "D", "Kermut", "Kseq", "Blend", "Meta"]].mean()
    official = {arm: float(cats[arm].mean()) for arm in ("AMK", "D", "Kermut", "Kseq", "Blend", "Meta")}
    return per, cats, schemes, official


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--max-assays", type=int, default=None)
    parser.add_argument("--drop-amk", action="store_true")
    parser.add_argument("--drop-category", action="store_true")
    parser.add_argument("--raw-features", action="store_true")
    parser.add_argument("--only-linear", action="store_true")
    parser.add_argument("--contextual", action="store_true")
    parser.add_argument("--with-kseq", action="store_true")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT.read_text())
    cat = {e["DMS_id"]: e.get("coarse_selection_type", e.get("category", "Unknown"))
           for e in contract["panel"]}
    meta = load_oof()
    meta["category"] = meta["assay"].map(cat).fillna("Unknown")
    if args.max_assays:
        keep = sorted(meta["assay"].unique())[: args.max_assays]
        meta = meta[meta["assay"].isin(keep)].reset_index(drop=True)
    meta = meta.dropna(subset=["category"]).reset_index(drop=True)
    meta, categories = add_features(meta, use_z=not args.raw_features)
    if args.contextual:
        meta = add_context(meta, categories)
    meta["Blend"] = 0.5 * (meta["D"] + meta["Kermut"])
    y = meta["target"].to_numpy(dtype=np.float64)

    results = {"rows": len(meta), "assays": int(meta["assay"].nunique()),
               "categories": categories, "feature_sets": {}}
    if args.contextual:
        mode_list = ("contextual",)
    else:
        mode_list = (("linear",) if args.only_linear else ("linear", "interactions"))
    for mode in mode_list:
        if mode == "contextual":
            X, cols = design_contextual(meta, categories, with_kseq=args.with_kseq)
        else:
            X, cols = design(meta, categories, mode, drop_amk=args.drop_amk,
                             drop_category=args.drop_category, with_kseq=args.with_kseq)
        pred, coefs = fit_predict_loao(meta, X, y, meta["assay"].unique())
        meta["Meta_" + mode] = pred
        per, cats, schemes, official = metrics(meta, "Meta_" + mode)
        results["feature_sets"][mode] = {
            "columns": cols,
            "official": official,
            "categories": cats.round(6).to_dict(),
            "schemes": schemes.round(6).to_dict(),
            "wins": {
                "Meta>AMK": int((per["Meta"] > per["AMK"]).sum()),
                "Meta>Kermut": int((per["Meta"] > per["Kermut"]).sum()),
                "Meta>Blend": int((per["Meta"] > per["Blend"]).sum()),
                "units": int(len(per)),
            },
        }
        per.to_csv(out / f"per_unit_{mode}.csv", index=False)
        (out / f"coefs_{mode}.json").write_text(json.dumps(coefs))
        print(json.dumps({"mode": mode, "official": official,
                          "wins": results["feature_sets"][mode]["wins"]}), flush=True)

    results["baseline"] = metrics(meta, "AMK")[3]
    (out / "meta_stack_217.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({"stage": "META_STACK_DONE", "rows": len(meta),
                      "assays": int(meta["assay"].nunique()), "out": str(out)}), flush=True)


if __name__ == "__main__":
    main()
