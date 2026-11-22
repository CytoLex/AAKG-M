import urllib.parse, urllib.request, re, sys, xml.etree.ElementTree as ET
def q(query, n=6):
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "max_results": n, "sortBy": "relevance"})
    with urllib.request.urlopen(url, timeout=40) as r: data = r.read()
    ns = {"a":"http://www.w3.org/2005/Atom"}
    root = ET.fromstring(data)
    out=[]
    for e in root.findall("a:entry", ns):
        t = " ".join(e.find("a:title",ns).text.split())
        s = " ".join(e.find("a:summary",ns).text.split())[:260]
        d = e.find("a:published",ns).text[:10]
        i = e.find("a:id",ns).text.rsplit("/",1)[-1]
        out.append((d,i,t,s))
    return out
for query in sys.argv[1:]:
    print("="*100); print("QUERY:", query)
    try:
        for d,i,t,s in q(query):
            print(f"  [{d}] {i}  {t[:95]}")
            print(f"      {s}")
    except Exception as e:
        print("  ERR", e)
