"""The structural-expert kernel, recovered and verified to floating-point precision.

Recovered from the fitting code at
  cytolex-mutation-context-v02-preparation-20260930/kernel_readout_v1.py
and verified against every saved artifact: computing `K(test, train) @ alpha` for
MAFG_MOUSE_Tsuboyama_2023_1K1V / fold_random_5 / fold0 reproduces model.pt's stored predictions
with correlation 1.0, RMSE 2.4e-14 and max |diff| 8.2e-14.

The kernel is a sum of two Gaussian blocks plus two identity indicators:

  k(x, y) = [ exp(-0.5 * ||x_main - y_main||^2 / d_main)
            + exp(-0.5 * ||x_side - y_side||^2 / d_side)
            + 1[wt_x == wt_y]
            + 1[mut_x == mut_y] ] / 4

with d_main = 10368 and d_side = 9, i.e. the squared length scale of each block is that block's
dimension. Both blocks are standardised with the per-block mean/std stored in `transforms`, and
inactive coordinates are zeroed before the distance is taken.
"""
import numpy as np


def _standardise(x, state):
    z = (x - np.asarray(state["mean"], dtype=np.float64)) / np.asarray(state["std"], dtype=np.float64)
    return np.where(np.asarray(state["active"], dtype=bool), z, 0.0)


def kernel(left, right, transforms):
    """left/right: dicts with `main` (n, 10368), `side` (n, 9), `wt`, `mut`.

    Returns the (len(left), len(right)) kernel matrix as defined above.
    """
    out = None
    for key in ("main", "side"):
        x = _standardise(left[key], transforms[key])
        y = _standardise(right[key], transforms[key])
        d2 = (x * x).sum(1)[:, None] + (y * y).sum(1)[None, :] - 2.0 * x @ y.T
        block = np.exp(-0.5 * np.maximum(d2, 0.0) / x.shape[1])
        out = block if out is None else out + block
    for key in ("wt", "mut"):
        out = out + (np.asarray(left[key])[:, None] == np.asarray(right[key])[None, :]).astype(np.float64)
    return out / 4.0


def predict(left, right, alpha, transforms):
    """Kernel-ridge prediction: K(left, right) @ alpha."""
    return kernel(left, right, transforms) @ np.asarray(alpha, dtype=np.float64).ravel()
