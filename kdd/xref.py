import json, urllib.request, urllib.parse, sys, time

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent":"AAKG-refcheck/1.0 (mailto:noreply@example.com)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

DOIS = {
 "esm2":"10.1126/science.ade2574",
 "deepsong":"10.1038/s41587-021-01146-5",
 "fowler2014":"10.1038/nmeth.3027",
 "yang2019":"10.1038/s41592-019-0496-6",
 "jacobs1991":"10.1162/neco.1991.3.1.79",
}
print("=== DOI verification ===")
for k, doi in DOIS.items():
    try:
        d = get(f"https://api.crossref.org/works/{doi}")["message"]
        au = ", ".join(f"{a.get('family','')}" for a in d.get("author",[])[:4])
        yr = (d.get("issued",{}).get("date-parts") or [[None]])[0][0]
        print(f"  {k:12s} OK  {d.get('container-title',['?'])[0][:34]:34s} {yr}  vol {d.get('volume','?')} p{d.get('page','?')}")
        print(f"               title: {d.get('title',['?'])[0][:88]}")
        print(f"               authors: {au}")
    except Exception as e:
        print(f"  {k:12s} ERR {e}")
    time.sleep(0.4)

print("\n=== arXiv-only entries: is there a published version? ===")
TITLES = {
 "audhkhasi2013generalized":"Generalized Ambiguity Decomposition for Understanding Ensemble Diversity",
 "qian2015forecast":"On the Forecast Combination Puzzle",
 "frazier2023solving":"Solving the Forecast Combination Puzzle",
 "wood2023unified":"A Unified Theory of Diversity in Ensemble Learning",
}
for k, t in TITLES.items():
    q = urllib.parse.urlencode({"query.bibliographic": t, "rows": 3})
    try:
        r = get(f"https://api.crossref.org/works?{q}")["message"]["items"]
        print(f"  {k}:")
        if not r: print("     no match")
        for it in r[:3]:
            ti = (it.get("title") or ["?"])[0][:80]
            ct = (it.get("container-title") or ["(no venue)"])[0][:40]
            yr = (it.get("issued",{}).get("date-parts") or [[None]])[0][0]
            print(f"     [{yr}] {ct:40s} | {ti}")
    except Exception as e:
        print(f"  {k}: ERR {e}")
    time.sleep(0.4)
