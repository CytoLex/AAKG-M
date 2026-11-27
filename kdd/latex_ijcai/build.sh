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
# page count alone says nothing about compliance; the body is what the limit applies to
import shutil, subprocess, os
tmp = pathlib.Path("/tmp/_bodycheck")
shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
src = pathlib.Path(".").resolve()
for f in src.iterdir():
    if f.is_file() and f.suffix in (".tex", ".bib", ".bst", ".sty"):
        shutil.copy(f, tmp / f.name)
t = (tmp / "paper.tex").read_text().replace("../figures/", f"{src.parent}/figures/")
i = t.find("\\bibliographystyle{named}")
(tmp / "paper.tex").write_text((t[:i] if i > 0 else t) + "\n\\end{document}\n")
subprocess.run([os.environ.get("TECTONIC", "/tmp/tectonic"), "-X", "compile", "paper.tex"],
               cwd=tmp, capture_output=True, env={**os.environ})
b = (tmp / "paper.pdf").read_bytes()
body = len(re.findall(rb"/Type\s*/Page\b", b))
for m in re.finditer(rb"stream\r?\n", b):
    try:
        body += len(re.findall(rb"/Type\s*/Page\b", zlib.decompress(b[m.end():m.end() + 200000])))
    except Exception:
        pass
verdict = "OK" if body <= 7 and n <= 9 else "OVER LIMIT"
print(f"AAKG_IJCAI_draft.pdf: {n} pages total, {body} body (IJCAI limit: 7 body + up to 2 references) -> {verdict}")
PY
