#!/bin/bash
# Build the IJCAI 2027 AI4Science submission.
#
#   ./build.sh
#
# Needs pandoc and tectonic. ijcai27.sty and named.bst are in this directory.
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
cp paper.pdf AAKG_IJCAI_draft.pdf

python3 - <<'PY'
import re, zlib, pathlib
d = pathlib.Path("AAKG_IJCAI_draft.pdf").read_bytes()
n = len(re.findall(rb"/Type\s*/Page\b", d))
for m in re.finditer(rb"stream\r?\n", d):
    try:
        n += len(re.findall(rb"/Type\s*/Page\b", zlib.decompress(d[m.end():m.end() + 200000])))
    except Exception:
        pass
print(f"AAKG_IJCAI_draft.pdf: {n} pages (limit is 9: 7 body + up to 2 references)")
PY
