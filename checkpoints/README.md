# AAKG-M fold checkpoints

Five gate checkpoints for the seed-1 headline configuration:

```text
model=mlp  hidden=64  dropout=0.1  ctx=ext
sched=cosine  lr=1e-3  epochs=100  folds=5  seed=1
```

Files:

| file | sha256 |
|---|---|
| `gate_fold0.pt` | `7cab6e69e4fc6fef9284746a3051f671fae2363a0783e4c8b23e83a0f0c2b940` |
| `gate_fold1.pt` | `cce7ba166d211e05e217b43b5a8fe84c075084555c4a462a69f68d084ee2acf4` |
| `gate_fold2.pt` | `717df4dd9a2eea781e6b4a9d4759bc71650da54dcba8b5a6f646af40c7571947` |
| `gate_fold3.pt` | `6ecb5bc313678c842c0f8f8e6d38141781ccdb3d037a44a01a85011273b961bf` |
| `gate_fold4.pt` | `e2e226e400f520ee0ac6696e76d95fc0a78a5a3efdee2641f9c796c960eea7a2` |

Each file is a `torch.save` dict:

```python
{
  "state_dict": {...},          # MLP gate weights
  "config": {
      "model": "mlp", "hidden": 64, "dropout": 0.1,
      "ctx": "ext", "ctx_dim": 17,
  },
  "ctx_cols": [...],             # exact 17 context columns, in order
  "base_cols": ["D_z", "Kermut_z", "AMK_z"],
  "ctx_mean": Tensor[17],        # fold-train context mean
  "ctx_std": Tensor[17],         # fold-train context std
  "fold": 0..4,
  "seed": 1,
}
```

## Loading

```python
import torch
from aakg_m import Gate

ckpt = torch.load("checkpoints/gate_fold0.pt", map_location="cpu", weights_only=False)
cfg = ckpt["config"]
gate = Gate(cfg["ctx_dim"], model=cfg["model"], hidden=cfg["hidden"], dropout=cfg["dropout"])
gate.load_state_dict(ckpt["state_dict"])
gate.eval()
```

The gate expects:

```text
c = (context - ckpt["ctx_mean"]) / ckpt["ctx_std"]
g = softmax(gate.net(c))
pred = g[0] * D_z + g[1] * Kermut_z + g[2] * AMK_z
```

`fold` is the **assay fold** assigned by `assign_folds(meta, k=5, seed=1)`, not the
ProteinGym variant fold.  The five checkpoints are the models that produced the
seed-1 per-unit predictions in `../results/per_unit.csv`.

## Scope

These checkpoints contain **only the gate**.  They do not contain D, Kermut or
AMK weights, OOF predictions, targets, or the context scaler for a new dataset.
To apply the gate to a new assay you must generate the three expert predictions
and the 17 context features with the same pipeline.
