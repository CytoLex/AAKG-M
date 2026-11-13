"""Train a head on the mutant-sequence multi-layer features (emb650_mut_v2).

Variants
    site   L33 at the mutated position                    (baseline)
    multi  L20 + L30 + L33                                 (+ depth)
    nbhd   multi + neighbourhood means N30/N33             (+ local context)
    dist   nbhd features, also distilled from the K+A blend (alpha 0.9)

Everything uses the paper's protocol: within-assay 5-fold OOF, three schemes,
official category-balanced aggregate.
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

CATS = ["Activity", "Binding", "Expression", "OrganismalFitness", "Stability"]
SCHEMES = ("fold_random_5", "fold_modulo_5", "fold_contiguous_5")
S = Path(os.environ.get("AAKG_DATA", "./data"))          # feature archives + bundle
MUT = S / "models" / "emb650_mut_v2"
ESMC = S / "models" / "esmc_mut"
FULL2 = S / "emb650_full2"


class LowRankResidual(nn.Module):
    """One rank-r linear map per category, added to the head output (zero-init)."""

    def __init__(self, d_in, r=8, n_cat=5):
        super().__init__()
        self.U = nn.Parameter(torch.zeros(n_cat, d_in, r))
        self.V = nn.Parameter(torch.randn(n_cat, r, 1) * 0.01)

    def forward(self, x, ci):
        U = self.U[ci]
        V = self.V[ci]
        z = torch.einsum("bd,bdr->br", x, U)
        return (z.unsqueeze(-1) * V).sum(dim=(-1, -2))


class Head(nn.Module):
    def __init__(self, d_in, d=256):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, d), nn.GELU(),
                                 nn.Linear(d, 64), nn.GELU(), nn.Linear(64, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


def teacher_map(bundle, scheme):
    b = pd.read_csv(bundle)
    b = b.dropna(subset=["target", "D", "Kermut", "AMK"])
    for c in ("D", "Kermut", "AMK"):
        g = b.groupby("assay")[c]
        b[c + "_z"] = ((b[c] - g.transform("mean")) / g.transform("std")
                       .replace(0, np.nan)).fillna(0).clip(-8, 8)
    b["t"] = 0.40 * b["Kermut_z"] + 0.50 * b["AMK_z"]
    g = b.groupby("assay")["t"]
    b["t"] = (b["t"] - g.transform("mean")) / g.transform("std").replace(0, np.nan)
    b = b[b.scheme == scheme]
    return {(r.assay, str(r.variant_id)): r.t for r in b.itertuples()}


WTL = {}
WTL_PATH = S / 'models' / 'emb650_layers'


def metric_weights(assay, cat, cap=100.0, iters=50):
    """Inverse assay-size x inverse category-assay-count, mean 1, capped with redistribution."""
    import collections
    n_a = collections.Counter(assay)
    per_assay_cat = dict(zip(assay, cat))
    n_c = collections.Counter(per_assay_cat.values())
    w = np.array([1.0 / n_a[a] * 1.0 / n_c[c] for a, c in zip(assay, cat)], np.float64)
    w *= len(w) / w.sum()
    for _ in range(iters):
        over = w > cap
        if not over.any():
            break
        excess = (w[over] - cap).sum()
        w[over] = cap
        free = ~over
        if not free.any():
            break
        w[free] += excess * w[free] / w[free].sum()
        w *= len(w) / w.sum()
    return w.astype(np.float32)


def build(variant, a_cap=0, a_seed=1, src="esm650"):
    cat_of = pd.read_csv(os.environ["AAKG_BUNDLE"], usecols=["assay", "category"]) \
        .groupby("assay")["category"].first().to_dict()
    X, Y, A, C, F, K = [], [], [], [], [], []
    for f in sorted(MUT.glob("*.npz")):
        assay = f.stem
        if assay not in cat_of or not (FULL2 / f"{assay}.npz").exists():
            continue
        d = np.load(f)
        z = np.load(FULL2 / f"{assay}.npz", allow_pickle=True)
        if src == "esmc":
            ef = ESMC / f"{assay}.npz"
            if not ef.exists():
                continue
            e = np.load(ef)
            A20, A30, A33 = e["L15"], e["L25"], e["L30"]
            if variant in ("nbhd", "dist"):
                raise SystemExit("src=esmc has no neighbourhood features; use --variant multi")
            B30, B33 = A30, A33
            if len(np.asarray(e["mutant"])) != len(np.asarray(d["mutant"])):
                continue
        else:
            A20, A30, A33 = d["L20"], d["L30"], d["L33"]
            B30, B33 = d["N30"], d["N33"]
        EMC = None
        if src == "both":
            ef = ESMC / f"{assay}.npz"
            if not ef.exists():
                continue
            _e = np.load(ef)
            if len(np.asarray(_e["mutant"])) != len(np.asarray(d["mutant"])):
                continue
            EMC = (_e["L15"], _e["L25"], _e["L30"])   # hoist: npz decompresses on every access
        if variant == "union":
            wl = np.load(WTL_PATH / f"{assay}.npz")
            WTL[assay] = (wl["L20"], wl["L30"], wl["L33"])
        Zmut = z["mut"]
        Zwt = z["wt"]
        Ysc = z["DMS_score"]
        Fsc = {s_: z[s_] for s_ in SCHEMES}
        Msc = np.asarray(z["mutant"]).astype(str)
        idx = {m: i for i, m in enumerate(Msc)}
        kept = np.asarray(d["mutant"]).astype(str)
        rows, ys, fs, kok = [], [], [], []
        for j, m in enumerate(kept):
            i = idx.get(m)
            if i is None:
                continue
            parts = []
            if variant == "full2sub":
                parts += [Zmut[i].astype(np.float32), Zwt.astype(np.float32)]
            if variant == "union":
                # mutant-sequence layers + WT layers + full2, the union of both lines
                W_ = WTL.get(assay)
                parts += [A20[j].astype(np.float32), A30[j].astype(np.float32),
                          A33[j].astype(np.float32), B30[j].astype(np.float32),
                          B33[j].astype(np.float32)]
                if W_ is not None:
                    pos = int(str(m)[1:-1]) - 1
                    if 0 <= pos < W_[0].shape[0]:
                        parts += [W_[0][pos].astype(np.float32), W_[1][pos].astype(np.float32),
                                  W_[2][pos].astype(np.float32)]
                    else:
                        parts += [np.zeros(1280, np.float32)] * 3
                else:
                    parts += [np.zeros(1280, np.float32)] * 3
                parts += [Zmut[i].astype(np.float32), (Zmut[i] - Zwt).astype(np.float32)]
            if variant in ("site", "multi", "nbhd", "dist"):
                parts.append(A33[j].astype(np.float32))
            if src == "both":
                parts += [EMC[0][j].astype(np.float32), EMC[1][j].astype(np.float32),
                          EMC[2][j].astype(np.float32)]
            if variant in ("multi", "nbhd", "dist"):
                parts += [A20[j].astype(np.float32), A30[j].astype(np.float32)]
            if variant in ("nbhd", "dist"):
                parts += [B30[j].astype(np.float32), B33[j].astype(np.float32)]
            rows.append(np.concatenate(parts))
            kok.append(m)
            ys.append(float(Ysc[i]))
            fs.append([int(Fsc[s_][i]) for s_ in SCHEMES])
        if not rows:
            continue
        if a_cap > 0 and len(rows) > a_cap:
            sel = np.random.default_rng(a_seed * 1000 + len(rows)).choice(len(rows), a_cap, replace=False)
            sel = np.sort(sel)
            rows = [rows[i] for i in sel]
            ys = [ys[i] for i in sel]
            fs = [fs[i] for i in sel]
            kok = [kok[i] for i in sel]
        arr = np.stack(rows)
        mu, sd = arr.mean(0), arr.std(0)
        sd[sd < 1e-6] = 1.0
        X.append(((arr - mu) / sd).astype(np.float32))
        Y.append(np.asarray(ys, np.float32))
        A.append(np.array([assay] * len(ys)))
        C.append(np.array([cat_of[assay]] * len(ys)))
        F.append(np.asarray(fs))
        K.append(np.asarray(kok))
    return (np.vstack(X), np.concatenate(Y), np.concatenate(A),
            np.concatenate(C), np.vstack(F), np.concatenate(K))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True,
                    choices=("full2sub", "site", "multi", "nbhd", "dist", "union"))
    ap.add_argument("--alpha", type=float, default=0.9)
    ap.add_argument("--teacher-csv", default="")
    ap.add_argument("--target-csv", default="", help="override the regression target (e.g. a residual)")
    ap.add_argument("--catbal", action="store_true", help="static category-balanced MSE")
    ap.add_argument("--cap", type=int, default=0, help="cap variants per assay (0 = no cap)")
    ap.add_argument("--losscap", type=float, default=0.0, help="clamp per-sample squared error at this value")
    ap.add_argument("--lowrank", type=int, default=0, help="add a category-shared rank-r residual branch")
    ap.add_argument("--lrshared", action="store_true", help="single rank-r branch shared by all categories")
    ap.add_argument("--assaybal", action="store_true", help="each assay contributes equally to the loss")
    ap.add_argument("--metricbal", action="store_true", help="official-metric row weights, cap 100 (the r3 scheme)")
    ap.add_argument("--src", default="esm650", choices=("esm650", "esmc", "both"))
    ap.add_argument("--dro", action="store_true", help="category GroupDRO (dynamic weights)")
    ap.add_argument("--dro-eta", type=float, default=0.05)
    ap.add_argument("--dro-cap", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--out", required=True)
    ap.add_argument("--units", default="")
    ap.add_argument("--preds", default="")
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed)

    X, y, assay, cat, F, kept = build(a.variant, a.cap, a.seed, a.src)
    print(f"variant={a.variant} rows {len(y)} assays {len(np.unique(assay))} dim {X.shape[1]}",
          flush=True)
    yy = y.copy()
    for k in np.unique(assay):
        m = assay == k
        s = yy[m].std()
        yy[m] = (yy[m] - yy[m].mean()) / (s if s > 1e-9 else 1.0)
    if a.target_csv:
        tj = pd.read_csv(a.target_csv).set_index(["assay", "variant_id"])["resid"]
        newy = np.array([tj.get((str(au), str(kk)), np.nan)
                         for au, kk in zip(assay, kept)], np.float32)
        ok = np.isfinite(newy)
        print(f"target override hit {ok.mean():.3f}", flush=True)
        y = newy
    catidx = np.array([CATS.index(c) for c in cat], np.int64)
    wrow = None
    if a.metricbal:
        wrow = metric_weights(list(assay), list(cat))
        print(f"metricbal weights mean {wrow.mean():.4f} max {wrow.max():.4f} "
              f"min {wrow.min():.4f} capped_frac {(wrow >= 99.99).mean():.4f}", flush=True)
    uniq_assay = {a: i for i, a in enumerate(sorted(np.unique(assay)))}
    assayidx = np.array([uniq_assay[a] for a in assay], np.int64)
    print(f"assaybal rows/assay mean {np.bincount(assayidx).mean():.0f}", flush=True)
    print(f"category counts {np.bincount(catidx, minlength=5).tolist()}", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    Xt = torch.from_numpy(X).to(device); yt = torch.from_numpy(yy).to(device)

    ext = None
    if a.teacher_csv:
        ext = pd.read_csv(a.teacher_csv)
        ext["variant_id"] = ext["variant_id"].astype(str)
        print(f"external teacher {len(ext)} rows", flush=True)
    if a.alpha > 0:
        tmaps = {s: teacher_map(os.environ["AAKG_BUNDLE"], s) for s in SCHEMES}

    q = torch.ones(5, device=device) / 5 if (a.dro or a.catbal) else None
    ess_min = [1e9]
    units = []
    allpred = []
    for si, scheme in enumerate(SCHEMES):
        pred = np.full(len(y), np.nan, np.float32)
        if a.alpha > 0:
            if ext is not None:
                sub = ext[ext.scheme == scheme].set_index(["assay", "variant_id"])["teacher"]
                tv = np.array([sub.get((str(au), str(kk)), np.nan)
                               for au, kk in zip(assay, kept)], dtype=np.float32)
                print(f"  {scheme}: teacher hit {np.isfinite(tv).mean():.3f}", flush=True)
            else:
                tv = np.array([tmaps[scheme].get((str(au), str(kk)), np.nan)
                               for au, kk in zip(assay, kept)], dtype=np.float32)
            tt = torch.from_numpy(np.nan_to_num(tv)).to(device)
        for f in range(5):
            tr = np.where(F[:, si] != f)[0]; te = np.where(F[:, si] == f)[0]
            if len(tr) < 100 or len(te) < 50:
                continue
            model = Head(X.shape[1], a.width).to(device)
            lr_branch = None
            if a.lowrank > 0:
                ncat = 1 if a.lrshared else 5
                lr_branch = LowRankResidual(X.shape[1], a.lowrank, n_cat=ncat).to(device)
            params = list(model.parameters()) + (list(lr_branch.parameters()) if lr_branch else [])
            opt = torch.optim.AdamW(params, lr=1e-3, weight_decay=1e-4)
            sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
            rng = np.random.default_rng(a.seed * 100 + f)
            for ep in range(a.epochs):
                model.train(); perm = rng.permutation(tr)
                for s0 in range(0, len(tr), 16384):
                    idx = perm[s0:s0 + 16384]
                    ci_b = torch.from_numpy(catidx[idx]).to(device)
                    out = model(Xt[idx])
                    if lr_branch is not None:
                        ci_lr = torch.zeros_like(ci_b) if a.lrshared else ci_b
                        out = out + lr_branch(Xt[idx], ci_lr)
                    err = (out - yt[idx]) ** 2
                    if a.dro:
                        ci = ci_b
                        Lc = torch.zeros(5, device=device)
                        present = torch.zeros(5, dtype=torch.bool, device=device)
                        for c in range(5):
                            m = ci == c
                            if bool(m.any()):
                                Lc[c] = err[m].mean(); present[c] = True
                        with torch.no_grad():
                            q = q * torch.exp(a.dro_eta * Lc * present.float())
                            q = q / q.sum()
                            q = q.clamp(max=a.dro_cap); q = q / q.sum()
                            ess = float(1.0 / (q ** 2).sum())
                            if ess < ess_min[0]:
                                ess_min[0] = ess
                        loss_t = (q[present] * Lc[present]).sum() / q[present].sum()
                    elif a.catbal:
                        ci = ci_b
                        parts = [err[ci == c].mean() for c in range(5) if bool((ci == c).any())]
                        loss_t = torch.stack(parts).mean()
                    elif a.metricbal:
                        wv = torch.from_numpy(wrow[idx]).to(device)
                        loss_t = (err * wv).sum() / wv.sum()
                    elif a.assaybal:
                        ai = torch.from_numpy(assayidx[idx]).to(device)
                        u = torch.unique(ai)
                        parts = [err[ai == uu].mean() for uu in u]
                        loss_t = torch.stack(parts).mean()
                    elif a.losscap > 0:
                        loss_t = err.clamp(max=a.losscap).mean()
                    else:
                        loss_t = err.mean()
                    loss = loss_t
                    if a.alpha > 0:
                        loss = (1 - a.alpha) * loss + a.alpha * ((out - tt[idx]) ** 2).mean()
                    opt.zero_grad(); loss.backward(); opt.step()
                sch.step()
            model.eval()
            if lr_branch is not None:
                lr_branch.eval()
            with torch.no_grad():
                for s0 in range(0, len(te), 60000):
                    idx = te[s0:s0 + 60000]
                    pv = model(Xt[idx])
                    if lr_branch is not None:
                        ci_e = torch.from_numpy(catidx[idx]).to(device)
                        pv = pv + lr_branch(Xt[idx], torch.zeros_like(ci_e) if a.lrshared else ci_e)
                    pred[idx] = pv.cpu().numpy()
        allpred.append(pd.DataFrame({"assay": assay, "scheme": scheme,
                                     "variant_id": kept, "pred": pred}))
        for k in np.unique(assay):
            m = assay == k; p = pred[m]
            if not np.isfinite(p).all() or len(np.unique(y[m])) < 3:
                continue
            units.append({"assay": str(k), "scheme": scheme, "category": cat[m][0],
                          "r": pd.Series(y[m]).corr(pd.Series(p), method="spearman")})
        print(f"  {scheme} done", flush=True)
    u = pd.DataFrame(units)
    per = u.groupby(["assay", "category"])["r"].mean()
    score = float(per.groupby("category").mean().mean())
    print(json.dumps({"variant": a.variant, "official": round(score, 6),
                      "assays": int(u.assay.nunique())}), flush=True)
    diag = {"dro": bool(a.dro), "catbal": bool(a.catbal), "eta": a.dro_eta,
            "cap": a.dro_cap, "losscap": a.losscap, "lowrank": a.lowrank, "assaybal": bool(a.assaybal), "metricbal": bool(a.metricbal), "ess_min": None if ess_min[0] > 1e8 else round(ess_min[0], 4),
            "q_final": None if q is None else [round(float(x), 4) for x in q]}
    print(json.dumps(diag), flush=True)
    Path(a.out).write_text(json.dumps({"variant": a.variant, "official": score,
                                       "assays": int(u.assay.nunique()), **diag}, indent=2))
    if a.units:
        u.to_csv(a.units, index=False)
    if a.preds:
        pd.concat(allpred, ignore_index=True).to_csv(a.preds, index=False)


if __name__ == "__main__":
    main()
