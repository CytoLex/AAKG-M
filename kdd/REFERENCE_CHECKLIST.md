# Reference verification checklist

Status of every entry in `latex_ijcai/references.bib` as of the last check, and exactly what remains before
submission. Verification used the arXiv API (author lists, journal references) and the Crossref API (DOIs,
venue, volume, pages) — reachable from this machine; `github.com` is not, so proceedings index pages were not
re-read this round.

## Verified this round

| key | venue | evidence |
|---|---|---|
| `esm2` | Science 379(6637):1123–1130, 2023 | Crossref by DOI 10.1126/science.ade2574 — title, volume, pages, authors match |
| `deepsong` | Nature Biotechnology 40:1114–1122, 2022 | Crossref 10.1038/s41587-021-01146-5 |
| `fowler2014` | Nature Methods 11(8):801–807, 2014 | Crossref 10.1038/nmeth.3027 |
| `yang2019` | Nature Methods 16:687–694, 2019 | Crossref 10.1038/s41592-019-0496-6 (needed a retry; SSL flake on first attempt) |
| `jacobs1991` | Neural Computation 3(1):79–87, 1991 | Crossref 10.1162/neco.1991.3.1.79 |
| `claeskens2016forecast` | International Journal of Forecasting 32(3):754–762, 2016 | Crossref 10.1016/j.ijforecast.2015.12.005 |
| `timmermann2006forecast` | Handbook of Economic Forecasting 1:135–196, 2006 | Crossref 10.1016/S1574-0706(05)01004-9 |
| `wood2023unified` | JMLR 24(359), 2023 | arXiv journal reference field |

## Downgraded to explicit preprints

Three entries have no peer-reviewed version located. They are now marked `@misc` with a `note` saying so, so a
copy-editor can see the status without digging.

| key | what it supports in the paper | action if a published version is found |
|---|---|---|
| `qian2015forecast` | the *combining for adaptation vs improvement* distinction | replace with the journal version; the puzzle itself no longer depends on it |
| `frazier2023solving` | the objection that the puzzle may be a low-power-test artefact | replace, or keep as preprint with the caveat |
| `audhkhasi2013generalized` | generalized ambiguity decomposition beyond squared loss | replace; the classic origin is Krogh & Vedelsby (1994), see below |

**Why this matters:** the paper's central framing now rests on `claeskens2016forecast` and
`timmermann2006forecast`, both peer-reviewed. The preprints only carry secondary points, so a reviewer cannot say
the argument leans on unreviewed work.

## Still to check by hand — conference entries

These have no DOI and were verified against proceedings indexes in an earlier pass, but **not re-verified this
round** because `proceedings.neurips.cc` and `proceedings.mlr.press` were not reachable from here.

| key | what to confirm |
|---|---|
| `proteingym` | NeurIPS 2023 Datasets & Benchmarks track, exact title capitalisation, author list |
| `proteinnpt` | NeurIPS 2023, main track |
| `kermut` | NeurIPS 2024 — check the year; the arXiv version is 2024-04 (arXiv:2407.00002) |
| `esm1v` | NeurIPS 2021 |
| `tranception` | ICML 2022, PMLR 162:16990–17017 |
| `msatransformer` | ICML 2021, PMLR 139:8844–8856 |
| `flip` | NeurIPS 2021 Datasets & Benchmarks |
| `shazeer2017` | ICLR 2017 — cited with a `note` giving arXiv:1701.06538, which is the safer form for an ICLR paper |
| `rasmussen2006` | MIT Press 2006, no DOI; book, check edition/ISBN if the style requires it |

## One open question worth resolving

The ambiguity decomposition is attributed to `audhkhasi2013generalized`, which is a preprint. The original result
is **Krogh & Vedelsby, "Neural Network Ensembles, Cross Validation, and Active Learning", NeurIPS 1994**. That
would be the better citation for the origin and it is peer-reviewed — but its metadata was not verified this
round, because the proceedings index was unreachable. **Add it if the index can be reached; keep the preprint
only for the general-loss extension.**

## Build state

```
20 entries · 0 undefined citations · 0 bibtex warnings · 0 overfull boxes
8 pages total, 7 body
```

Re-run the check after any edit to the bibliography:

```
python3 /tmp/xref.py      # DOI and venue verification via Crossref
python3 /tmp/axmeta.py <arxiv-id> ...   # author lists and journal refs via arXiv
```
