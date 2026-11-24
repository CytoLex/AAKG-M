"""Assemble the markdown sections into paper.tex. Deterministic; run before build.sh."""
import re
import json, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from md2tex import md2tex
from headings import fix_headings

KDD = pathlib.Path(__file__).resolve().parent.parent
LATEX = KDD / "latex_ijcai"


def body(name, end_marker="## Note"):
    s = (KDD / name).read_text()
    parts = s.split("\n---\n")
    txt = parts[1] if len(parts) > 1 else s
    if end_marker in txt:
        txt = txt.split(end_marker)[0]
    return txt.strip()


sections = [
    ("## 1 Introduction", (KDD / "ijcai_sections" / "IJ1_INTRO.md").read_text().strip()),
    ("## 2 Related work", (KDD / "ijcai_sections" / "IJ2_RELATED.md").read_text().strip()),
    ("## 3 What allocation is worth", (KDD / "ijcai_sections" / "IJ3_LEAD.md").read_text().strip()),
    ("", (KDD / "ijcai_sections" / "IJ3A_PROTOCOL.md").read_text().strip()),
    ("", (KDD / "ijcai_sections" / "IJ3B_MECHANISMS.md").read_text().strip()),
    ("", (KDD / "ijcai_sections" / "IJ3D_INDELS.md").read_text().strip()),
    ("", (KDD / "ijcai_sections" / "IJ3E_MEANING.md").read_text().strip()),
    ("## 4 The expert", (KDD / "ijcai_sections" / "IJ4_EXPERT.md").read_text().strip()),
    ("## 5 What the ranker is worth", (KDD / "ijcai_sections" / "IJ5_UTILITY.md").read_text().strip()),
    ("## 6 Limitations and Ethical Considerations", (KDD / "ijcai_sections" / "IJ6_ETHICS.md").read_text().strip()),
    ("## 7 Discussion", (KDD / "ijcai_sections" / "IJ7_DISCUSSION.md").read_text().strip()),
]
out = []
for title, txt in sections:
    out.append(f"{title}\n\n{txt}" if title else txt)
md = "\n\n".join(out)

# --- pull the markdown pipe tables out and replace with placeholders
lines, tables, placeholders, i = md.split("\n"), [], [], 0
out = []                      # fresh list: `out` above holds the section texts
while i < len(lines):
    ln = lines[i]
    if ln.strip().startswith("|") and i + 1 < len(lines) and \
       set(lines[i + 1].replace("|", "").replace(" ", "").replace("\t", "")) <= set("-:"):
        hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
        i += 2
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        tables.append((hdr, rows))
        placeholders.append(f"TABLEPLACEHOLDER{len(tables)}")
        out.append(f"\nTABLEPLACEHOLDER{len(tables)}\n")
    else:
        out.append(ln)
        i += 1
clean = "\n".join(out)
(LATEX / "paper.md").write_text(md)
tmp = LATEX / "_body.md"
tmp.write_text(clean)
subprocess.run(["pandoc", str(tmp), "-f", "markdown", "-t", "latex", "--wrap=preserve",
                "-o", str(LATEX / "_body.tex")], check=True)
tmp.unlink()

tex_body = (LATEX / "_body.tex").read_text()
tex_body = re.sub(r"\\hypertarget\{[^}]*\}\{%\s*\n", "", tex_body)
tex_body = fix_headings(tex_body)

# long monospace filenames cannot break inside \texttt and overflow the column; \path allows breaks
tex_body = tex_body.replace("\\texttt{performance\\_DMS\\_supervised\\_benchmarks.py}",
                            "\\path{performance_DMS_supervised_benchmarks.py}")

tex_body = re.sub(r"(\\(?:sub)*section\{[^}]*\}(?:\\label\{[^}]*\})?)\}", r"\1", tex_body)


def esc(t):
    for a, b in (("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$")):
        t = t.replace(a, b)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = t.replace("\u2212", "$-$").replace("\u2013", "--").replace("\u2014", "---")
    t = t.replace("\u0394", r"$\Delta$")          # after the $ escape, so it survives
    return t


WIDE_TABLES = {1}   # the seven-mechanism comparison needs the full width


def make_table(n):
    hdr, rows = tables[n - 1]
    cols = "l" + "r" * (len(hdr) - 1)
    # narrow tables go in a single column: full-width floats compete for the top of each page and a spare
    # one is pushed to a page of its own
    env = "table*" if (n in WIDE_TABLES or len(hdr) > 4) else "table"
    o = ["\\begin{" + env + "}[!t]", "\\centering", "\\small",
         "\\begin{tabular}{" + cols + "}", "\\hline",
         " & ".join(esc(h) for h in hdr) + r" \\", "\\hline"]
    for r in rows:
        r = r + [""] * (len(hdr) - len(r))
        o.append(" & ".join(esc(c) for c in r[:len(hdr)]) + r" \\")
    o += ["\\hline", "\\end{tabular}", "\\end{" + env + "}"]
    return "\n".join(o)


# ICML's page limit applies to the main body only, so the supporting tables live in the appendix.
APPENDIX_TABLES = set()
_moved = []
for n in range(1, len(tables) + 1):
    if n in APPENDIX_TABLES:
        _moved.append(make_table(n))
        tex_body = tex_body.replace(f"TABLEPLACEHOLDER{n}", "")
    else:
        # the lookahead matters: without it "TABLEPLACEHOLDER1" also matches the prefix of
        # "TABLEPLACEHOLDER10", so the tenth table silently receives the first table's content
        tex_body = re.sub(rf"TABLEPLACEHOLDER{n}(?!\d)", lambda _m: make_table(n), tex_body)
for a in ("toprule", "midrule", "bottomrule"):
    tex_body = tex_body.replace("\\" + a, "\\hline")
(LATEX / "_body.tex").unlink()

FIG1 = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=0.92\textwidth]{../figures/fig1_allocation_vs_expert_ijcai.pdf}
\caption{Left: both levers measured from one origin in one pipeline, the upper arrow being what any weighting of
the pool could gain (a per-assay oracle, +0.0051) and the lower what adding one expert is worth (+0.0122). Right:
the thirteen expert-into-pool pairs, marginal value against disagreement with the pool; colour is the expert and
marker shape is which pool it joins, since four of the thirteen are the same expert entering different pools and two
of those coincide within a marker diameter. The expert with the \emph{lowest} standalone score (X, 0.6449)
contributes the most and the highest (AMK, 0.6651) almost nothing, which is the claim the title makes; the noise,
shuffle and negate controls each score zero.}
\label{fig:allocation}
\end{figure*}
"""
FIG2 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.68\columnwidth]{../figures/fig2_topk_by_category_ijcai.pdf}
\caption{Top-of-list utility by functional category: recall of the true top-$k$ variants when the top
$k$ of our ranking is taken, for $k \in \{1\%, 5\%, 10\%\}$, with the random-ordering expectation
marked. Stability is consistently strongest and activity weakest, a spread the aggregate Spearman does
not reveal.}
\label{fig:topk}
\end{figure}
"""
tex_body = tex_body.replace("\\section{What allocation is worth}",
                            FIG1 + "\n\\section{What allocation is worth}", 1)
# --- appendix: material that ICML lets us keep outside the page limit
APPENDIX = r"""
\newpage
\appendix
\section{Experimental setup}
""" + md2tex(body("SECTION_SETUP.md").replace("## Setup", "").strip()) + r"""
\section{What this contributes to protein engineering}
""" + md2tex(body("SECTION_DOMAIN.md").replace("## Draft", "").replace("## Notes", "").strip()) + r"""
\section{Supporting tables}
""" + "\n\n".join(_moved) + r"""
"""
tex_body = tex_body.replace("\\section{What the ranker is worth}",
                            FIG2 + "\n\\section{What the ranker is worth}", 1)

BIB = r"""
\bibliographystyle{named}
\bibliography{references}
"""



PRE = r"""\documentclass{article}
\pdfpagewidth=8.5in
\pdfpageheight=11in
\usepackage{ijcai27}
% The kit says 'Use the postscript times font!'. Under XeTeX, \usepackage{times} silently falls
% back to Latin Modern (TU/ptm/m/n undefined), so the typeface is set explicitly instead.
% TeX Gyre Termes is a Times clone and ships with the engine's bundle, so the build is portable.
\usepackage{fontspec}
\setmainfont{texgyretermes}[Extension=.otf, UprightFont=*-regular, BoldFont=*-bold,
  ItalicFont=*-italic, BoldItalicFont=*-bolditalic]
\setmonofont{texgyrecursor}[Extension=.otf, UprightFont=*-regular, BoldFont=*-bold,
  ItalicFont=*-italic, BoldItalicFont=*-bolditalic, Scale=0.9]
\usepackage{unicode-math}
\setmathfont{texgyretermes-math.otf}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\usepackage[utf8]{inputenc}
\usepackage[small]{caption}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage[switch]{lineno}
\usepackage{booktabs}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\urlstyle{same}

\begin{document}
\linenumbers

\title{What Moves a Protein-Fitness Predictor: Disagreement, Not Accuracy}

% Anonymous submission: no author block.
\author{}
\maketitle

\begin{abstract}
Protein engineering screens rank candidate mutations, and the field's models combine several predictors, each new
one added because it scores well on its own. Both habits are worth less than they look. We measure the two levers
directly on ProteinGym. A per-assay oracle bounds what any weighting of a fixed expert pool can capture at
\textbf{+0.0051} over a constant fitted on the other assays, against \textbf{+0.0122} for adding one expert:
allocation is 42\% of the expert lever, the intervals do not overlap, and the bound replicates on the indel
benchmark. It is a bound under Spearman: under top-of-list recall, the metric a campaign experiences, the
transferable headroom is 2.8 times larger and standard weights capture a tenth of it; at top-1\%, a threshold a
campaign actually operates at, a rule that optimises that recall and then shrinks beats them by +0.0093. That loss is repairable —
shrinkage toward the panel constant recovers the headroom without per-assay tuning — and it is concentrated: the
top ambiguity quartile holds 57\% of it. The expert lever is disagreement, not accuracy. Across thirteen
expert-into-pool pairs, marginal value tracks disagreement at r = \textbf{+0.786} while the weakest expert alone
contributes the most and the strongest almost nothing, a measurement whose noise and shuffle controls each score
zero. An encoder built on that principle — reference-minus-mutant features in a local neighbourhood,
distilled and fused at four fixed weights — reaches \textbf{0.694} on the official metric against 0.657 for the
published leader. For the domain we report where the ranking can be trusted: the top 5\% recovers 24.7\% of the
true top 5\%, 7.7x on stability against 3.4x on activity, and parity on the largest quartile. We release
per-mutant predictions for all 696,311 mutants.
\end{abstract}
"""


(LATEX / "paper.tex").write_text(PRE + tex_body + "\n" + BIB + "\n\\end{document}\n")
n_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]+", md))
print("paper.tex written: %d tables, 2 figures, %d words" % (len(tables), n_words))
