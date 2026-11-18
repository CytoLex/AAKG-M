"""Minimal markdown to LaTeX for appendix prose: bold, code spans, em dashes, underscores."""
import re


def md2tex(text):
    def code(m):
        return r"\texttt{" + m.group(1).replace("_", r"\_") + "}"

    t = re.sub(r"`([^`]+)`", code, text)
    t = re.sub(r"\*\*(.+?)\*\*", lambda m: r"\textbf{" + m.group(1) + "}", t)
    t = t.replace("\u2014", "---").replace("\u2013", "--")
    t = re.sub(r"(?<!\\)_", r"\_", t)          # escape bare underscores, not already-escaped ones
    return t
