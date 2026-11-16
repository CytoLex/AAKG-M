# Licence for weights, expert predictions and derived scores

`LICENSE` (Apache-2.0) covers the **code** in this repository: the gate, the expert training scripts,
the fusion and evaluation scripts, and the tests.

It does **not** cover the following, which remain copyright CytoLex and are licensed separately:

- the trained model weights and per-assay checkpoints;
- the structural expert prediction tables (`D`, `AMK`) and any per-mutant prediction files;
- the ESM-650 feature archives.

## What you may do with those

**Research use is permitted without asking.** You may download, run, evaluate and build on the weights
and prediction tables for non-commercial research, including reproducing the numbers in this
repository and citing them in academic work.

**Commercial use requires written permission.** Contact CytoLex before using the weights or prediction
tables in a product, a paid service, or internal commercial research.

**Redistribution.** You may redistribute the weights and tables alongside a copy of this file, provided
this file travels with them. Modified versions must be marked as modified.

## Why the split

ProteinGym's submission criteria require that a submitted model be open source so that its scores can
be reproduced. The code needed to reproduce every number in this repository is under Apache-2.0, and
`submission/reproduce_official.sh` reproduces the leaderboard figures from two public repositories
plus `submission/raw_score_file.csv`. The weights and the third-party-derived prediction tables stay
under the terms above because they encode work that predates and extends beyond this benchmark entry.

## Third-party material

`Kermut` and `AMK` prediction columns derive from other groups' methods and carry their own terms.
Nothing in this file grants rights to that material.
