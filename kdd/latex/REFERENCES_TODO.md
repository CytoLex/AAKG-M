# Bibliography: what is verified and what is not

`references.bib` holds 14 entries. Every one was checked against a **primary source**, not typed from
memory — and that check caught two errors that would otherwise have shipped.

## How each entry was verified

| source | what it gave |
|---|---|
| `proceedings.neurips.cc` | venue, exact title and author list for the NeurIPS papers |
| `proceedings.mlr.press` | venue, title, authors, PMLR volume and page range for the ICML papers |
| `api.crossref.org/works/{doi}` | title, journal, volume, pages and authors for the journal articles |

## Two errors the verification caught

**Fowler & Fields 2014 had the wrong title.** I had written "Deep mutational scanning: a new method for
protein engineering". The paper is *Deep mutational scanning: a new **style** of protein science*,
Nature Methods 11:801–807, doi:10.1038/nmeth.3027.

**An DOI I expected was wrong.** doi:10.1038/nmeth.2897, which is the one that seems right if you are
recalling from memory, resolves to "A fair comparison" by Costea et al. — an unrelated letter in the same
journal. Had it gone in unchecked, a reviewer would have found it.

Both are now correct and carry the verified DOI.

## What is verified without a DOI

Five entries are conference papers in proceedings that do not mint DOIs. They are verified by the
proceedings index (title, authors, venue, and PMLR volume/pages where applicable):

`proteingym` (NeurIPS 2023 Datasets & Benchmarks), `proteinnpt` (NeurIPS 2023), `kermut` (NeurIPS 2024),
`esm1v` (NeurIPS 2021), `flip` (NeurIPS 2021 Datasets & Benchmarks), `tranception` (ICML 2022),
`msatransformer` (ICML 2021).

## The one entry still marked uncertain

`shazeer2017`. The OpenReview API did not return the ICLR 2017 record for it, so the entry cites the
venue but carries `note = {arXiv:1701.06538}` as its locator. If the ICLR proceedings page can be
reached, replace the note with the proceedings URL.

## Before submission

1. Spot-check two or three entries by hand. The pipeline is only as good as the index it queried, and
   `others` appears in the author lists of the two large-consortium papers.
2. Confirm the required section title against the KDD 2027 CFP verbatim.
3. Rebuild and confirm the reference list does not displace content from page 8.
