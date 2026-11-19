"""Convert the assemblers' markdown headings into correctly levelled LaTeX headings.

pandoc turns every level-2 heading into \\subsection{...} with the intended number left in the text, e.g.
\\subsection{3.2 The bound is small}. Emitting that as \\section makes LaTeX number it as the next
section while the title still reads "3.2", so the printed numbering drifts from the text. This maps the
intended number to the intended level and strips it, letting LaTeX do the numbering.
"""
import re

_NUM2 = re.compile(r"^(\d+)\.(\d+)\s+(.*)$")
_NUM1 = re.compile(r"^(\d+)\s+(.*)$")


def _fix_level(macroname):
    def repl(m):
        title = m.group(1).strip()
        deep = _NUM2.match(title)
        if deep:
            return "\\subsection{" + deep.group(3) + "}"
        top = _NUM1.match(title)
        if top:
            return "\\section{" + top.group(2) + "}"
        if macroname == "subsection":
            return "\\subsection*{" + title + "}"
        return "\\subsubsection*{" + title + "}"
    return repl


def fix_headings(tex):
    tex = re.sub(r"\\subsection\{([^}]*)\}", _fix_level("subsection"), tex)
    tex = re.sub(r"\\subsubsection\{([^}]*)\}", _fix_level("subsubsection"), tex)
    # pandoc leaves a stray closing brace after a \\label that closed a hypertarget group
    tex = re.sub(r"(\\label\{[^}]*\})\}", r"\1", tex)
    return tex
