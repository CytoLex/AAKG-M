"""Assemble the markdown sections into paper.tex. Deterministic; run before build.sh."""
import json, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from md2tex import md2tex

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
    ("## 3 Allocation has no headroom", (KDD / "ijcai_sections" / "IJ3_ALLOCATION.md").read_text().strip()),
    ("## 4 The expert", (KDD / "ijcai_sections" / "IJ4_EXPERT.md").read_text().strip()),
    ("## 5 What the ranker is worth", (KDD / "ijcai_sections" / "IJ5_UTILITY.md").read_text().strip()),
    ("## 6 Limitations and Ethical Considerations", (KDD / "ijcai_sections" / "IJ6_ETHICS.md").read_text().strip()),
    ("## 7 Discussion", (KDD / "ijcai_sections" / "IJ7_DISCUSSION.md").read_text().strip()),
]
out = []
for title, txt in sections:
    txt = re.sub(r"^#+\s*[0-9. ]*[^\n]*\n", "", txt, count=1)
    out.append(f"{title}\n\n{txt}")
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
tex_body = re.sub(r"\\subsection\{((?:[0-9]|[A-Z])[^}]*)\}", r"\\section{\1}", tex_body)
tex_body = re.sub(r"(\\(?:sub)*section\{[^}]*\}(?:\\label\{[^}]*\})?)\}", r"\1", tex_body)


def esc(t):
    for a, b in (("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$")):
        t = t.replace(a, b)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = t.replace("\u2212", "-").replace("\u2013", "--").replace("\u2014", "---")
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
\includegraphics[width=0.86\columnwidth]{../figures/fig1_allocation_vs_expert.pdf}
\caption{Allocation headroom against expert headroom, same protocol. The shaded band spans what any
weighting rule could gain over a tuned constant (a per-assay oracle, +0.0027); the lower arrow spans
what replacing one expert gained (+0.0077). Every adaptive mechanism we measured lands inside or below
the band.}
\label{fig:allocation}
\end{figure}
"""
FIG2 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.86\columnwidth]{../figures/fig2_topk_by_category.pdf}
\caption{Top-of-list utility by functional category: recall of the true top-$k$ variants when the top
$k$ of our ranking is taken, for $k \in \{1\%, 5\%, 10\%\}$, with the random-ordering expectation
marked. Stability is consistently strongest and activity weakest, a spread the aggregate Spearman does
not reveal.}
\label{fig:topk}
\end{figure}
"""
tex_body = tex_body.replace("\\section{3 Allocation has no headroom}",
                            FIG1 + "\n\\section{3 Allocation has no headroom}", 1)
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
tex_body = tex_body.replace("\\section{5 What the ranker is worth}",
                            FIG2 + "\n\\section{5 What the ranker is worth}", 1)

BIB = r"""
\section*{AI Disclosure Statement}
\addcontentsline{toc}{section}{AI Disclosure Statement}

Analysis scripts, evaluation harnesses and \LaTeX{} assembly were written and revised with an AI coding
assistant; the manuscript prose was drafted with the same assistant and then reviewed, corrected and
rewritten by the authors. Reference metadata was resolved programmatically against the NeurIPS and ICML
proceedings indexes and the Crossref API rather than recalled, and that verification caught a wrong
paper title and a DOI belonging to a different article. The experimental design, the choice of baselines,
the falsification strategy and every interpretation are the authors\'. No result reported here was
generated by a model, no AI system is listed as an author, and the authors take full responsibility for
the content.

\bibliographystyle{named}
\bibliography{references}
"""



PRE = r"""\documentclass{article}
\pdfpagewidth=8.5in
\pdfpageheight=11in
\usepackage{ijcai27}
\usepackage{times}
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

\title{Allocation was never the bottleneck: what actually moves a protein-fitness ranker}

% Anonymous submission: no author block.
\author{}
\maketitle

\begin{abstract}
Protein engineering screens rank candidate mutations, but the field optimises the fusion of sequence and
structure models. We test that premise on the ProteinGym substitution benchmark, 217 assays and 651
assay-by-split units, and find that every one of seven adaptive weighting mechanisms we measured ties a
single constant tuned on held-out assays. A per-assay oracle bounds the entire headroom any weighting
rule could capture at +0.0027, against +0.0077 for replacing a single expert. We then show where the
headroom is: an encoder over reference-minus-mutant representations in a local neighbourhood, distilled
from the strongest experts, with a category-specific low-rank residual and eight-seed averaging, fused
as four fixed weights reaches 0.694 on the official metric against 0.657 for the published leader. The
useful result for the domain is the shape of the ranking: the top 5\% recovers 24.7\% of the true top
5\%, a 4.96x lift, but 7.7x on stability assays against 3.4x on activity. We release per-mutant
predictions for all 696,311 mutants.
\end{abstract}
"""


(LATEX / "paper.tex").write_text(PRE + tex_body + "\n" + APPENDIX + "\n" + BIB + "\n\\end{document}\n")
n_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]+", md))
print("paper.tex written: %d tables, 2 figures, %d words" % (len(tables), n_words))
