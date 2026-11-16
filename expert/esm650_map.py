"""Map the fair-esm checkpoint keys onto the installed ESM2 module and verify.

Checkpoint (BERT-style)                Model (Llama-style)
  esm.embeddings.word_embeddings.weight   embed_tokens.weight
  ...layer.N.attention.self.query         layers.N.self_attn.q_proj
  ...layer.N.attention.self.key           layers.N.self_attn.k_proj
  ...layer.N.attention.self.value         layers.N.self_attn.v_proj
  ...layer.N.attention.output.dense       layers.N.self_attn.out_proj
  ...layer.N.attention.self.rotary_embeddings  layers.N.self_attn.rot_emb
  ...layer.N.attention.LayerNorm          layers.N.input_layernorm
  ...layer.N.LayerNorm                    layers.N.final_layer_norm
  ...layer.N.intermediate.dense           layers.N.fc1
  ...layer.N.output.dense                 layers.N.fc2
  ...encoder.emb_layer_norm_after         emb_layer_norm_after

The script prints which model tensors stay unmatched and verifies that a mapped
tensor really carries the checkpoint values.
"""
import json
import os
import struct
import sys

import numpy as np
import torch

ROOT = os.environ.get("AAKG_DATA", "./data")
MERGED = ROOT + "/models/esm650_merged.bin"
DT = {"F32": np.float32, "F16": np.float16, "I64": np.int64, "I32": np.int32,
      "I16": np.int16, "U8": np.uint8, "BOOL": bool}


def read_safetensors(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
        base = 8 + n
        out = {}
        for name, info in header.items():
            if name == "__metadata__":
                continue
            a, b = info["data_offsets"]
            f.seek(base + a)
            raw = f.read(b - a)
            if info["dtype"] == "BF16":
                u = np.frombuffer(raw, dtype=np.uint16).astype(np.uint32) << 16
                arr = u.view(np.float32).reshape(info["shape"])
            else:
                arr = np.frombuffer(raw, dtype=DT[info["dtype"]]).reshape(info["shape"]).copy()
            out[name] = torch.from_numpy(arr)
    return out


def translate(k):
    if k.startswith("esm.embeddings.word_embeddings."):
        return "embed_tokens" + k[len("esm.embeddings.word_embeddings"):]
    if k.startswith("esm.contact_head."):
        return "contact_head" + k[len("esm.contact_head"):]
    if k.startswith("lm_head."):
        return k
    if k.startswith("esm.encoder.emb_layer_norm_after."):
        return "emb_layer_norm_after" + k[len("esm.encoder.emb_layer_norm_after"):]
    if k.startswith("esm.encoder.layer."):
        rest = k[len("esm.encoder.layer."):]
        idx, _, tail = rest.partition(".")
        t = tail
        t = t.replace("attention.self.rotary_embeddings.", "self_attn.rot_emb.")
        t = t.replace("attention.self.query.", "self_attn.q_proj.")
        t = t.replace("attention.self.key.", "self_attn.k_proj.")
        t = t.replace("attention.self.value.", "self_attn.v_proj.")
        t = t.replace("attention.output.dense.", "self_attn.out_proj.")
        t = t.replace("attention.LayerNorm.", "self_attn_layer_norm.")
        if t.startswith("LayerNorm."):
            t = "final_layer_norm." + t[len("LayerNorm."):]
        t = t.replace("intermediate.dense.", "fc1.")
        t = t.replace("output.dense.", "fc2.")
        return f"layers.{idx}.{t}"
    return None


def main():
    sd = read_safetensors(MERGED)
    import esm
    from esm.model.esm2 import ESM2
    alphabet = esm.data.Alphabet.from_architecture("ESM-1b")
    model = ESM2(num_layers=33, embed_dim=1280, attention_heads=20,
                 alphabet=alphabet, token_dropout=True)
    tgt = model.state_dict()

    new, unmapped, dropped = {}, [], []
    for k, v in sd.items():
        nk = translate(k)
        if nk is None:
            dropped.append(k)
            continue
        if nk not in tgt:
            unmapped.append((k, nk))
            continue
        if tuple(tgt[nk].shape) != tuple(v.shape):
            unmapped.append((k, nk, "shape", tuple(v.shape), tuple(tgt[nk].shape)))
            continue
        new[nk] = v
    missing = [k for k in tgt if k not in new]
    print(json.dumps({"mapped": len(new), "target": len(tgt),
                      "unmapped": unmapped[:5], "dropped": dropped[:5],
                      "missing_model_keys": missing[:8]}, indent=1), flush=True)

    model.load_state_dict(new, strict=False)
    # value check: the first layer's q_proj must equal the checkpoint's query
    src = sd["esm.encoder.layer.0.attention.self.query.weight"]
    got = model.layers[0].self_attn.q_proj.weight.detach()
    print("identity check:", torch.allclose(src.float(), got.float(), atol=1e-6), flush=True)

    model.eval()
    bc = alphabet.get_batch_converter()
    _, _, toks = bc([("p", "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ")])
    with torch.no_grad():
        rep = model(toks, repr_layers=[33], return_contacts=False)["representations"][33]
    print(json.dumps({"rep": list(rep.shape)}), flush=True)
    json.dump({"mapped": len(new), "missing": missing}, open(ROOT + "/models/esm650_map.json", "w"))
    print("MAP_OK", flush=True)


if __name__ == "__main__":
    main()
