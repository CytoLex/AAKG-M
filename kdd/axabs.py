import urllib.request, sys, xml.etree.ElementTree as ET
ns={"a":"http://www.w3.org/2005/Atom"}
for i in sys.argv[1:]:
    url=f"http://export.arxiv.org/api/query?id_list={i}"
    with urllib.request.urlopen(url, timeout=40) as r: data=r.read()
    e=ET.fromstring(data).find("a:entry", ns)
    print("="*100)
    print(" ".join(e.find("a:title",ns).text.split()))
    print("id:", i, "| published:", e.find("a:published",ns).text[:10])
    print(" ".join(e.find("a:summary",ns).text.split()))
    print()
