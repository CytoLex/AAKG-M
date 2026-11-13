import os
"""Average the lr8 expert's predictions across its eight training seeds."""
from pathlib import Path
import numpy as np, pandas as pd

R = Path(os.environ.get("AAKG_RUNS", "runs"))           # directory holding preds_*_s*.csv
acc, n = None, 0
for s in range(1, 9):
    f = R / f"preds_lr8p_s{s}.csv"
    if not f.exists():
        print("missing", f.name, flush=True); continue
    d = pd.read_csv(f)
    d["variant_id"] = d["variant_id"].astype(str)
    key = d.set_index(["assay", "scheme", "variant_id"])["pred"]
    acc = key if acc is None else acc.add(key, fill_value=0.0)
    n += 1
avg = (acc / n).rename("pred").reset_index()
avg.to_csv(R / "preds_savg_s1.csv", index=False)
print(f"averaged {n} seeds, {len(avg)} rows", flush=True)
print("SEEDAVG_DONE", flush=True)
