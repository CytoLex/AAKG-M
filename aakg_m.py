#!/usr/bin/env python3
"""AAKG training-capacity sweep.

Same assay-held-out protocol as meta_softgate.py, but supports:
  - longer training / LR / cosine schedule
  - richer label-free assay context
  - context-only MLP gate (not a per-variant gate)
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

import meta_stack as ms

OUT = Path(os.environ.get("AAKG_OUT", str(Path(__file__).resolve().parent / "results" / "run")))


class Gate(nn.Module):
    def __init__(self, dim, model="linear", hidden=32, dropout=0.0):
        super().__init__()
        self.model = model
        if model == "linear":
            self.logits = nn.Linear(dim, 3)
            nn.init.zeros_(self.logits.weight)
            nn.init.zeros_(self.logits.bias)
        else:
            self.net = nn.Sequential(
                nn.Linear(dim, hidden), nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(hidden, 3),
            )
            nn.init.zeros_(self.net[-1].weight)
            nn.init.zeros_(self.net[-1].bias)

    def forward(self, ctx, base):
        logits = self.logits(ctx) if self.model == "linear" else self.net(ctx)
        w = torch.softmax(logits, dim=1)
        return (w * base).sum(dim=1), w


def assign_folds(meta, k, seed):
    rng = np.random.default_rng(seed)
    fold = {}
    for _, g in meta.groupby("category", sort=True):
        assays = np.array(sorted(g["assay"].unique()))
        rng.shuffle(assays)
        for i, a in enumerate(assays):
            fold[a] = int(i % k)
    return fold


def context_columns(meta, categories, mode):
    base = ["log_n_z", "D_std_z", "K_std_z", "A_std_z",
            "D_K_corr_z", "D_A_corr_z", "K_A_corr_z"]
    if mode == "ext":
        base += ["D_mean_z", "K_mean_z", "A_mean_z", "seq_len_z", "dms_z"]
    return base + ["cat_" + c for c in categories]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=32768)
    parser.add_argument("--lr", type=float, default=1e-2)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--model", choices=("linear", "mlp"), default="linear")
    parser.add_argument("--hidden", type=int, default=32)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--ctx", choices=("base", "ext"), default="base")
    parser.add_argument("--sched", choices=("none", "cosine"), default="none")
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
    if device == "auto":
        device = "cpu"
    if device == "cpu":
        torch.set_num_threads(8)
    else:
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
    print(json.dumps({"stage": "DEVICE", "device": device, "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None}), flush=True)

    contract = json.loads(ms.CONTRACT.read_text())
    ent = {e["DMS_id"]: e for e in contract["panel"]}
    cat = {k: v.get("coarse_selection_type", v.get("category", "Unknown")) for k, v in ent.items()}
    meta = ms.load_oof()
    meta["category"] = meta["assay"].map(cat).fillna("Unknown")
    meta = meta.dropna(subset=["category"]).reset_index(drop=True)
    meta, categories = ms.add_features(meta, use_z=True)
    meta = ms.add_context(meta, categories)
    meta["seq_len"] = meta["assay"].map(lambda a: float(ent[a]["seq_len"]))
    meta["dms_number"] = meta["assay"].map(lambda a: float(ent[a]["DMS_number_single_mutants"]))
    meta["seq_len_z"] = (np.log1p(meta["seq_len"]) - np.log1p(meta["seq_len"]).mean()) / np.log1p(meta["seq_len"]).std()
    meta["dms_z"] = (np.log1p(meta["dms_number"]) - np.log1p(meta["dms_number"]).mean()) / np.log1p(meta["dms_number"]).std()
    meta["Blend"] = 0.5 * (meta["D"] + meta["Kermut"])

    ctx_cols = context_columns(meta, categories, args.ctx)
    base_cols = ["D_z", "Kermut_z", "AMK_z"]
    C = meta[ctx_cols].to_numpy(dtype=np.float32)
    B = meta[base_cols].to_numpy(dtype=np.float32)
    y = meta["target"].to_numpy(dtype=np.float32)
    fold = meta["assay"].map(assign_folds(meta, args.folds, args.seed)).to_numpy()
    n_by_assay = meta.groupby("assay")["target"].transform("size").to_numpy()
    w_row = (1.0 / n_by_assay).astype(np.float64)
    w_row /= w_row.mean()

    pred = np.full(len(meta), np.nan, dtype=np.float32)
    gate_w = np.full((len(meta), 3), np.nan, dtype=np.float32)
    history = []
    print(json.dumps({"stage": "LOADED", "rows": len(meta), "assays": int(meta["assay"].nunique()),
                      "ctx": len(ctx_cols), "model": args.model, "epochs": args.epochs,
                      "lr": args.lr, "sched": args.sched, "seed": args.seed}), flush=True)

    for f in range(args.folds):
        tr = np.where(fold != f)[0]
        te = np.where(fold == f)[0]
        mu, sd = C[tr].mean(0), C[tr].std(0)
        sd[sd < 1e-6] = 1.0
        Ct = torch.from_numpy((C - mu) / sd).to(device)
        Bt = torch.from_numpy(B).to(device)
        yt = torch.from_numpy(y).to(device)
        wt = torch.from_numpy(w_row.astype(np.float32)).to(device)
        model = Gate(C.shape[1], model=args.model, hidden=args.hidden, dropout=args.dropout).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs) if args.sched == "cosine" else None
        for epoch in range(args.epochs):
            model.train()
            perm = torch.from_numpy(np.random.permutation(tr)).to(device)
            total = 0.0
            for start in range(0, len(tr), args.batch):
                idx = perm[start:start + args.batch]
                out, _ = model(Ct[idx], Bt[idx])
                loss = ((out - yt[idx]) ** 2 * wt[idx]).sum() / wt[idx].sum()
                opt.zero_grad()
                loss.backward()
                opt.step()
                total += float(loss) * len(idx)
            if sched is not None:
                sched.step()
            if epoch % args.log_every == 0 or epoch == args.epochs - 1:
                rec = {"fold": f, "epoch": epoch, "loss": total / len(tr), "lr": opt.param_groups[0]["lr"]}
                history.append(rec)
                print(json.dumps({"stage": "EPOCH", **rec}), flush=True)
        model.eval()
        with torch.no_grad():
            outs, ws = [], []
            for i in range(0, len(te), args.batch):
                o, w = model(Ct[te[i:i + args.batch]], Bt[te[i:i + args.batch]])
                outs.append(o); ws.append(w)
            pred[te] = torch.cat(outs).cpu().numpy()
            gate_w[te] = torch.cat(ws).cpu().numpy()
        print(json.dumps({"stage": "FOLD_DONE", "fold": f}), flush=True)

    meta["Meta"] = pred
    per, cats, schemes, official = ms.metrics(meta, "Meta")
    out = {
        "config": vars(args),
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
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    meta["w_D"], meta["w_K"], meta["w_A"] = gate_w[:, 0], gate_w[:, 1], gate_w[:, 2]
    meta.groupby("assay")[["w_D", "w_K", "w_A"]].mean().to_csv(outdir / "assay_weights.csv")
    per.to_csv(outdir / "per_unit.csv", index=False)
    (outdir / "history.json").write_text(json.dumps(history, indent=2))
    (outdir / "result.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"stage": "SWEEP_DONE", **out}), flush=True)


if __name__ == "__main__":
    main()
