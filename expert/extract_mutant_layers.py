"""Per-variant multi-layer embeddings from MUTANT sequences.

The WT-sequence extraction was weaker than the mutant-site features, so the
representation has to be built the same way the strong features were: run the
model on the mutated protein and read the site.

Each worker loads the model once and handles a shard of the assays.  For every
variant we keep five vectors (all 1280-d):
    L20_site, L30_site, L33_site, L30_nbhd(+-k), L33_nbhd(+-k)

Output: emb650_mut/<assay>.npz with those arrays (float16).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

# Point these at your own copies. Nothing below assumes a particular machine.
ROOT = Path(os.environ.get("AAKG_DATA", "./data"))            # models/, emb650_full2/
PP = Path(os.environ.get("AAKG_PROBABILITIES", "./probabilities"))   # <assay>/probability.pt
OUT = Path(os.environ.get("AAKG_OUT", "./emb650_mut_v2"))
LAYERS = [20, 30, 33]
K = 4
BATCH = 96


def build_model():
    import esm
    from esm.model.esm2 import ESM2
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from esm650_map import read_safetensors, translate
    sd = read_safetensors(str(Path(os.environ.get("AAKG_ESM650", ROOT / "models" / "esm650_merged.bin"))))
    alphabet = esm.data.Alphabet.from_architecture("ESM-1b")
    model = ESM2(num_layers=33, embed_dim=1280, attention_heads=20,
                 alphabet=alphabet, token_dropout=False)
    tgt = model.state_dict()
    new = {translate(k): v for k, v in sd.items()
           if translate(k) in tgt and tuple(tgt[translate(k)].shape) == tuple(v.shape)}
    model.load_state_dict(new, strict=False)
    model.eval()
    return model, alphabet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, alphabet = build_model()
    model = model.to(device)
    aa = "ACDEFGHIKLMNPQRSTVWY"
    t0 = time.time()
    stats = {"assays": 0, "variants": 0}

    assays = sorted(p.parent.name for p in PP.glob("*/probability.pt"))
    mine = assays[a.shard::a.nshards]
    for assay in mine:
        outp = OUT / f"{assay}.npz"
        if outp.exists():
            continue
        d = torch.load(str(PP / assay / "probability.pt"), map_location="cpu", weights_only=False)
        seq = d.get("WT")
        if not isinstance(seq, str) or len(seq) < 10:
            continue
        base = torch.tensor([alphabet.encode(seq)], device=device)[0]
        if len(base) != len(seq) + 2:
            print(f"skip {assay}: {len(seq)} residues but {len(base)} tokens", flush=True)
            continue

        import pandas as pd
        z = np.load(ROOT / "emb650_full2" / f"{assay}.npz", allow_pickle=True)
        mutants = np.asarray(z["mutant"]).astype(str)
        picks = []
        for v in mutants:
            try:
                wt, p, mut = str(v)[0], int(str(v)[1:-1]), str(v)[-1]
            except Exception:
                continue
            if wt not in aa or mut not in aa or p < 1 or p > len(seq) or p >= len(base) - 1:
                continue
            if seq[p - 1] != wt:
                continue
            picks.append((p, mut))
        if not picks:
            continue

        L20, L30, L33, N30, N33 = [], [], [], [], []
        with torch.no_grad():
            for s0 in range(0, len(picks), BATCH):
                chunk = picks[s0:s0 + BATCH]
                toks = base.repeat(len(chunk), 1)
                for r, (p, mut) in enumerate(chunk):
                    toks[r, p] = alphabet.get_idx(mut)
                o = model(toks, repr_layers=LAYERS, return_contacts=False)["representations"]
                rep = {L: o[L].detach() for L in LAYERS}
                for r, (p, _) in enumerate(chunk):
                    lo, hi = max(0, p - 1 - K), min(len(seq), p + K)
                    L20.append(rep[20][r, p].to(torch.float16).cpu().numpy())
                    L30.append(rep[30][r, p].to(torch.float16).cpu().numpy())
                    L33.append(rep[33][r, p].to(torch.float16).cpu().numpy())
                    N30.append(rep[30][r, lo:hi].mean(0).to(torch.float16).cpu().numpy())
                    N33.append(rep[33][r, lo:hi].mean(0).to(torch.float16).cpu().numpy())
                del rep
        kept = np.array([f"{seq[p-1]}{p}{m}" for p, m in picks])
        np.savez_compressed(outp, L20=np.stack(L20), L30=np.stack(L30), L33=np.stack(L33),
                            N30=np.stack(N30), N33=np.stack(N33), mutant=kept)
        stats["assays"] += 1
        stats["variants"] += len(picks)
        if stats["assays"] % 5 == 0:
            rate = stats["variants"] / max(time.time() - t0, 1)
            print(f"shard{a.shard}: {stats['assays']} assays {stats['variants']} variants "
                  f"{rate:.0f}/s", flush=True)
    print(json.dumps({"shard": a.shard, **stats}), flush=True)


if __name__ == "__main__":
    main()
