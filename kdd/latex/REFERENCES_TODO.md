# Bibliography status

`references.bib` has 14 entries, resolved through the OpenAlex API by title search rather than typed
from memory. Every title, year, venue, author list and DOI in the file is what the API returned.

Two kinds of entry still need a human:

## Seven `[VENUE-CHECK]` entries

OpenAlex only has a preprint record for these, so the entry currently cites a bioRxiv or arXiv version.
A conference version very likely exists and should replace it, but **I did not verify those venues** and
did not want to assert them:

| key | what the entry currently says | what to check |
|---|---|---|
| `esm1v` | bioRxiv 2021 | NeurIPS 2021 version |
| `tranception` | arXiv 2022 | ICML 2022 version |
| `msatransformer` | bioRxiv 2021 | ICML 2021 version |
| `flip` | bioRxiv 2021 | NeurIPS 2021 Datasets & Benchmarks version |
| `proteingym` | NeurIPS 2023, **DOI missing** | the NeurIPS record exists (seen in OpenAlex) but its DOI was not captured |
| `kermut` | NeurIPS 2024 | venue confirmed; check the DOI OpenAlex gave |
| `shazeer2017` | arXiv 2017 | ICLR 2017 version |

## One `[REPLACE]` entry

`fowler2014`. OpenAlex returned a different, unrelated 2015 review for that title. The entry now holds
the canonical reference — Fowler & Fields, *Deep mutational scanning: a new method for protein
engineering*, Nature Methods 2014 — with **volume, pages and DOI deliberately blank**. Fill them from
the journal, do not guess.

## How it was built

```python
# for each reference: OpenAlex title search, accept a hit only if >=60% of query tokens appear in the
# returned title, then record the API's own metadata.
```

The overlap guard matters: without it, two of the first attempts matched unrelated papers (Tranception
resolved to a paper on C0[0,1]-valued autoregressive processes, and the MSA Transformer to a phylogeny
paper). Both were caught and discarded.

## Before submission

1. Resolve the seven venue checks and the one replacement.
2. Add `\cite` commands to the text — **the manuscript currently cites nothing at all**, which is a
   larger gap than the .bib itself. §2 names three literatures and should carry roughly a dozen
   citations across them.
3. Rebuild and confirm the bibliography section does not push the paper past 8 pages. ACM's reference
   format sits outside the content limit, so this is safe, but the in-text additions are not.
