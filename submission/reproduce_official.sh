#!/bin/bash
# Reproduce the reported scores by running the official ProteinGym performance script
# on the score file in this directory. No GPU, no cluster, no proprietary tables.
set -euo pipefail

# 1. clone the official repository
[ -d ProteinGym ] || git clone --depth 1 https://github.com/OATML-Markslab/ProteinGym.git

# 2. the official reference table is part of that repository
REF=ProteinGym/reference_files/DMS_substitutions.csv
[ -f "$REF" ] || { echo "missing $REF"; exit 1; }

# 3. run their script unmodified, with our score file as the only input
python ProteinGym/proteingym/performance_DMS_supervised_benchmarks.py \
    --input_scoring_file raw_score_file.csv \
    --output_performance_file_folder ./official_out \
    --DMS_reference_file_path "$REF" \
    --top_model Kermut \
    --number_assay_reshuffle 100

# 4. the summary row
column -s, -t < official_out/Spearman/Summary_performance_DMS_substitutions_Spearman.csv \
  | cut -c1-160
