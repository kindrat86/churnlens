#!/usr/bin/env python3
"""
inject_entity_graph.py — inject ONE canonical entity @graph into every page.
Consistent @ids (#organization/#software/#website/#founder) so engines MERGE
(enrich) rather than duplicate. Idempotent (marker). Never fabricates.
"""
import json, os, re, sys

ROOT = os.getcwd()
MARKER = "<!-- entity-graph -->"
E = json.load(open(os.path.join(ROOT, "entity.json"), encoding="utf-8"))

org = {
    "@type": "Organization", "@id": E["url"] + "/#organization",
    "name": E["brand"], "url": E["url"],
    "description": E["description"], "disambiguatingDescription": E["disambiguatingDescription"],
    "knowsAbout": E["knowsAbout"], "sameAs": E["sameAs"],
    "logo": {"@type": "ImageObject", "url": E["url"] + "/og.png"},
    "contactPoint": {"@type": "ContactPoint", "email": E["contactEmail"], "contactType": "customer support"},
}
software = {
    "@type": "SoftwareApplication", "@id": E["url"] + "/#software",
    "name": E["brand"], "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
    "url": E["url"], "description": E["description"], "publisher": {"@id": E["url"] + "/#organization"},
    "offers": [{"@type": "Offer", "name": o["name"], "price": o["price"], "priceCurrency": o["priceCurrency"]} for o in E["offers"]],
}
website = {"@type": "WebSite", "@id": E["url"] + "/#website", "url": E["url"], "name": E["brand"], "publisher": {"@id": E["url"] + "/#organization"}}
graph = [org, software, website]

# Founder Person — only if a real name is present (never fabricate)
fname = E.get("founder", {}).get("name", "")
if fname and "OWNER_TODO" not in fname:
    person = {"@type": "Person", "@id": E["url"] + "/#founder", "name": fname, "sameAs": E["founder"].get("sameAs", []), "worksFor": {"@id": E["url"] + "/#organization"}}
    graph.append(person)
    org["founder"] = {"@id": E["url"] + "/#founder"}
else:
    print("  NOTE: founder name is an owner-TODO — Person node omitted (no fabrication).")

block = MARKER + '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")) + "</script>"
block_re = re.compile(re.escape(MARKER) + r'<script type="application/ld\+json">.*?</script>', re.S)

SKIP = {"node_modules", ".git", ".vercel", ".well-known"}
count = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP]
    for fn in filenames:
        if not fn.endswith(".html"): continue
        p = os.path.join(dirpath, fn)
        try: t = open(p, encoding="utf-8").read()
        except Exception: continue
        if "</head>" not in t: continue
        new = block_re.sub(lambda _: block, t) if MARKER in t else t.replace("</head>", block + "\n</head>", 1)
        # align stray #org -> #organization (turn-1 dup-node bug), leaving other schema intact
        new = new.replace('"@id": "' + E["url"] + '/#org"', '"@id": "' + E["url"] + '/#organization"')
        if new != t:
            open(p, "w", encoding="utf-8").write(new); count += 1
print(f"✓ entity graph injected/updated on {count} pages")
