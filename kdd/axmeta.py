import urllib.request, sys, xml.etree.ElementTree as ET
ns={"a":"http://www.w3.org/2005/Atom"}
for i in sys.argv[1:]:
    url=f"http://export.arxiv.org/api/query?id_list={i}"
    with urllib.request.urlopen(url, timeout=40) as r: data=r.read()
    e=ET.fromstring(data).find("a:entry", ns)
    au=[a.find("a:name",ns).text for a in e.findall("a:author",ns)]
    jr=e.find("{http://arxiv.org/schemas/atom}journal_ref")
    print(f"{i} | {' '.join(e.find('a:title',ns).text.split())[:70]}")
    print(f"   authors: {', '.join(au)}")
    print(f"   journal_ref: {jr.text if jr is not None else '(none)'}")
