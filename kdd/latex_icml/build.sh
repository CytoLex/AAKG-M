#!/bin/bash
# Build the ICML 2027 variant of the paper.
#
#   ./build.sh
#
# Needs pandoc and tectonic. The ICML style files are already in this directory.
set -euo pipefail
cd "$(dirname "$0")"

TECTONIC=${TECTONIC:-}
if [ -z "$TECTONIC" ]; then
  if command -v tectonic >/dev/null 2>&1; then TECTONIC=tectonic
  elif [ -x /tmp/tectonic ]; then TECTONIC=/tmp/tectonic
  else echo "tectonic not found (brew install tectonic)"; exit 1
  fi
fi

python3 make_tex.py
TEXINPUTS=.:..:../figures: "$TECTONIC" -X compile paper.tex
cp paper.pdf AAKG_ICML_draft.pdf

python3 - <<'PY'
import re, zlib, pathlib
d = pathlib.Path("AAKG_ICML_draft.pdf").read_bytes()
n = len(re.findall(rb"/Type\s*/Page\b", d))
for m in re.finditer(rb"stream\r?\n", d):
    try:
        n += len(re.findall(rb"/Type\s*/Page\b", zlib.decompress(d[m.end():m.end() + 200000])))
    except Exception:
        pass
print(f"AAKG_ICML_draft.pdf: {n} pages total (main body is 8; the rest is appendix and references)")
PY
