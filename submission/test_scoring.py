"""Smoke test for compute_fitness.py: does it fuse the three experts as documented?

Runs the scoring script on three synthetic variants whose z-scores are known by hand, then checks
that the output equals 0.4 * Kermut_z + 0.4 * AMK_z + 0.2 * X_z.

    python submission/test_scoring.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "proteingym" / "baselines" / "cytomuta" / "compute_fitness.py"

K = [0.5, -0.1, 0.2]
A = [-0.3, 0.4, 0.9]
X = [0.7, -0.5, 0.1]


def z(v):
    """pandas .std() is the sample standard deviation (ddof=1); match it."""
    v = np.asarray(v, float)
    return (v - v.mean()) / v.std(ddof=1)


def main():
    tmp = tempfile.mkdtemp()
    seqs = ["MVA", "MVG", "MVD"]
    pd.DataFrame({"mutant": ["A1V", "A2G", "A3D"], "mutated_sequence": seqs,
                  "DMS_score": [0.1, -0.2, 0.3]}).to_csv(f"{tmp}/dms.csv", index=False)
    pd.DataFrame({"mutated_sequence": seqs, "Kermut_common_std": K,
                  "AMK_common": A}).to_csv(f"{tmp}/exp.csv", index=False)
    pd.DataFrame({"mutated_sequence": seqs, "pred": X}).to_csv(f"{tmp}/stu.csv", index=False)

    r = subprocess.run([sys.executable, str(SCRIPT),
                        "--dms_file", f"{tmp}/dms.csv",
                        "--expert_table", f"{tmp}/exp.csv",
                        "--student_preds", f"{tmp}/stu.csv",
                        "--out", f"{tmp}/out.csv"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]

    got = pd.read_csv(f"{tmp}/out.csv")["predictions_fitness"].to_numpy()
    want = 0.4 * z(K) + 0.4 * z(A) + 0.2 * z(X)
    assert np.allclose(got, want, atol=1e-9), f"{got} != {want}"
    print(f"ok fusion:        {np.round(got, 6).tolist()} == 0.4K + 0.4A + 0.2X on z-scores")

    # passthrough mode: the script must also work from already-fused predictions, which is the
    # path the maintainers can run without the research-use expert tables
    pd.DataFrame({"mutated_sequence": seqs,
                  "predictions_fitness": want}).to_csv(f"{tmp}/fused.csv", index=False)
    r2 = subprocess.run([sys.executable, str(SCRIPT),
                         "--dms_file", f"{tmp}/dms.csv",
                         "--fused_preds", f"{tmp}/fused.csv",
                         "--out", f"{tmp}/out2.csv"], capture_output=True, text=True)
    assert r2.returncode == 0, r2.stderr[-800:]
    got2 = pd.read_csv(f"{tmp}/out2.csv")["predictions_fitness"].to_numpy()
    assert np.allclose(got2, want, atol=1e-9), f"{got2} != {want}"
    print("ok passthrough:   same values from --fused_preds, no expert tables needed")


if __name__ == "__main__":
    main()
