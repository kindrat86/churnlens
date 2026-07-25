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
    "foundingDate": E["foundingDate"],
    "knowsAbout": E["knowsAbout"], "sameAs": E["sameAs"],
    "logo": {"@type": "ImageObject", "url": E["url"] + "/og.png"},
    "image": E["image"],
    "contactPoint": {"@type": "ContactPoint", "email": E["contactEmail"], "contactType": "customer support"},
}
# PostalAddress (741bf6c). Kept optional so the injector never invents a location,
# but emitted whenever entity.json carries one — it was being silently dropped on
# every run, reverting the committed address across the whole site.
if E.get("address"):
    org["address"] = E["address"]
software = {
    "@type": "SoftwareApplication", "@id": E["url"] + "/#software",
    "name": E["brand"], "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
    "url": E["url"], "description": E["description"], "publisher": {"@id": E["url"] + "/#organization"},
    "author": {"@id": E["url"] + "/#organization"},
    "featureList": E["featureList"],
    "offers": [{"@type": "Offer", "name": o["name"], "price": o["price"], "priceCurrency": o["priceCurrency"]} for o in E["offers"]],
}
# NOTE: no WebSite.potentialAction/SearchAction here on purpose. A legacy node
# declared one targeting /?q={search_term_string}, but this site has no search
# endpoint — /?q=… returns the homepage byte-for-byte. Declaring a sitelinks
# searchbox that does not exist is a false claim, so it is dropped, not migrated.
website = {"@type": "WebSite", "@id": E["url"] + "/#website", "url": E["url"], "name": E["brand"],
           "description": E["siteDescription"], "inLanguage": E["inLanguage"],
           "publisher": {"@id": E["url"] + "/#organization"}}
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

# i18n/ and i18n_out/ are .vercelignore'd, public/* is 308-redirected to /*, and
# dist/ 404s — none of them ship. Keeping this list identical to SKIP_DIRS in
# dedupe_entity_graph.py matters: the two scripts must cover the same pages, or
# dedupe leaves behind entity nodes on pages inject never reached.
SKIP = {
    "node_modules", ".git", ".vercel", ".well-known",
    "i18n", "i18n_out", "dist", "public", "__pycache__",
}
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
