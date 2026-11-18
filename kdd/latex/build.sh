#!/bin/bash
# Build the KDD AI for Sciences draft from the markdown sources in the parent directory.
#
#   ./build.sh
#
# Needs: pandoc, and tectonic (a static binary; it fetches the TeX bundle on first run, so no local
# TeX installation is required).
set -euo pipefail
cd "$(dirname "$0")"

TECTONIC=${TECTONIC:-}
if [ -z "$TECTONIC" ]; then
  if command -v tectonic >/dev/null 2>&1; then TECTONIC=tectonic
  elif [ -x /tmp/tectonic ]; then TECTONIC=/tmp/tectonic
  else
    echo "tectonic not found. Install with 'brew install tectonic' or fetch a static binary from"
    echo "  https://github.com/tectonic-typesetting/tectonic/releases"
    exit 1
  fi
fi

python3 make_tex.py
TEXINPUTS=.:..:../figures: "$TECTONIC" -X compile paper.tex
cp paper.pdf AAKG_KDD_draft.pdf
python3 - <<'PY'
import re, zlib, pathlib
d = pathlib.Path("AAKG_KDD_draft.pdf").read_bytes()
n = len(re.findall(rb"/Type\s*/Page\b", d))
for m in re.finditer(rb"stream\r?\n", d):
    try:
        n += len(re.findall(rb"/Type\s*/Page\b", zlib.decompress(d[m.end():m.end()+200000])))
    except Exception:
        pass
print(f"AAKG_KDD_draft.pdf: {n} pages")
PY
