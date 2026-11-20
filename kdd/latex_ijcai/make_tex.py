"""Assemble the markdown sections into paper.tex. Deterministic; run before build.sh."""
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
    ("## 3 Allocation has no headroom", (KDD / "ijcai_sections" / "IJ3_LEAD.md").read_text().strip()),
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


def make_table(n):
    hdr, rows = tables[n - 1]
    cols = "l" + "r" * (len(hdr) - 1)
    o = ["\\begin{table*}[t]", "\\centering", "\\small",
         "\\begin{tabular}{" + cols + "}", "\\hline",
         " & ".join(esc(h) for h in hdr) + r" \\", "\\hline"]
    for r in rows:
        r = r + [""] * (len(hdr) - len(r))
        o.append(" & ".join(esc(c) for c in r[:len(hdr)]) + r" \\")
    o += ["\\hline", "\\end{tabular}", "\\end{table*}"]
    return "\n".join(o)


# ICML's page limit applies to the main body only, so the supporting tables live in the appendix.
APPENDIX_TABLES = set()
_moved = []
for n in range(1, len(tables) + 1):
    if n in APPENDIX_TABLES:
        _moved.append(make_table(n))
        tex_body = tex_body.replace(f"TABLEPLACEHOLDER{n}", "")
    else:
        tex_body = tex_body.replace(f"TABLEPLACEHOLDER{n}", make_table(n))
for a in ("toprule", "midrule", "bottomrule"):
    tex_body = tex_body.replace("\\" + a, "\\hline")
(LATEX / "_body.tex").unlink()

FIG1 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.76\columnwidth]{../figures/fig1_allocation_vs_expert_ijcai.pdf}
\caption{Both levers measured from the same origin and in one pipeline. The upper arrow is what any
weighting rule could gain over a constant fitted on the other assays (a per-assay oracle, +0.0051); the
lower is what adding one expert is worth (+0.0122). The intervals do not overlap, so allocation is the
smaller lever by a margin that is not noise.}
\label{fig:allocation}
\end{figure}
"""
FIG2 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.76\columnwidth]{../figures/fig2_topk_by_category_ijcai.pdf}
\caption{Top-of-list utility by functional category: recall of the true top-$k$ variants when the top
$k$ of our ranking is taken, for $k \in \{1\%, 5\%, 10\%\}$, with the random-ordering expectation
marked. Stability is consistently strongest and activity weakest, a spread the aggregate Spearman does
not reveal.}
\label{fig:topk}
\end{figure}
"""
tex_body = tex_body.replace("\\section{Allocation has no headroom}",
                            FIG1 + "\n\\section{Allocation has no headroom}", 1)
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

\title{The Ceiling on Adaptive Weighting in Protein Fitness Prediction, and How to Reach It}

% Anonymous submission: no author block.
\author{}
\maketitle

\begin{abstract}
Protein engineering screens rank candidate mutations, and the field's models combine several predictors with
per-assay weights. We measure what that combination is worth. A per-assay oracle bounds the entire headroom
any weighting rule can capture at +0.0051 over a constant fitted on the other assays, against +0.0122 for
adding a single expert: allocation is 42\% of the expert lever, the intervals do not overlap, and the bound
replicates on ProteinGym's indel assays, where the oracle gap is larger but weights fitted on half an assay
lose to a constant on the other half. That loss is repairable: partial pooling by $\lambda = n/(n+k)$ gains
+0.0051 and +0.0021 on the two benchmarks, turning a deficit into a gain on the small assays where per-assay
fitting fails. The expert lever is representation. An encoder over reference-minus-mutant features in a local
neighbourhood, distilled from the strongest experts and fused at four fixed weights, reaches 0.694 on the
official metric against 0.657 for the published leader, and the same representation wins six of seven splits
of FLIP2, an independently collected benchmark. For the domain we report the utility profile: the top 5\%
recovers 24.7\% of the true top 5\%, a 4.96x lift, but 7.7x on stability assays against 3.4x on activity,
and parity on the largest quartile. We release per-mutant predictions for all 696,311 mutants.
\end{abstract}
"""


(LATEX / "paper.tex").write_text(PRE + tex_body + "\n" + BIB + "\n\\end{document}\n")
n_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]+", md))
print("paper.tex written: %d tables, 2 figures, %d words" % (len(tables), n_words))
