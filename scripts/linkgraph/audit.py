#!/usr/bin/env python3
"""Report internal-link-graph health. Exit 1 if any release-blocking check fails."""
import os, re, json, sys, collections, statistics
from html.parser import HTMLParser
SKIP = ("i18n","i18n_out","dist",".vercel","public","node_modules",".git","assets","scripts","schema","embed","widgets","api")
EXCLUDE = {"/404","/thank-you","/oto","/badge","/related-tools","/network-widget","/network/widget",
"/striking-distance","/index","/affiliate","/affiliates","/masterclass","/dream100","/dream-100",
"/citations","/calculator","/free/embed-widget","/embed","/embed/tools/portfolio-network",
"/terms","/privacy","/contact","/partners","/walkthrough","/network"}
v = json.load(open("vercel.json")) if os.path.exists("vercel.json") else {}
lit = [r for r in v.get("redirects", []) if "(" not in r["source"] and ":" not in r["source"]]
redir = {r["source"].rstrip("/") for r in lit}
m = {r["source"].rstrip("/"): r["destination"] for r in lit}
loops = 0
for s in m:
    path, cur = [s], m[s]
    while True:
        k = cur.split("#")[0].rstrip("/")
        if k in path: loops += 1; break
        if k not in m: break
        path.append(k); cur = m[k]
exist, pages = set(), {}
for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), ".")
        if any(p in SKIP for p in rel.split(os.sep)): continue
        if f.endswith(".html"):
            u = "/" + rel.replace(os.sep, "/")
            u = u[:-11] if u.endswith("/index.html") else u[:-5]
            exist.add(u or "/"); pages.setdefault(u or "/", []).append(os.path.join(dp, f))
        exist.add("/" + rel.replace(os.sep, "/"))
ASSET = re.compile(r"\.(css|js|png|jpe?g|svg|ico|xml|txt|json|webp|pdf|gif)$", re.I)
def ctx(h):
    b = re.sub(r"(?is)<nav.*?</nav>", " ", h); b = re.sub(r"(?is)<footer.*?</footer>", " ", b)
    o = set()
    for x in re.findall(r'href="(/[^"]*)"', b):
        t = x.split("#")[0].split("?")[0]
        if not t or ASSET.search(t): continue
        n = t[:-5] if t.endswith(".html") else t
        n = n[:-6] if n.endswith("/index") else n
        n = n[:-1] if len(n) > 1 and n.endswith("/") else n
        o.add(n or "/")
    return o
inl, broken, pf = collections.Counter(), collections.Counter(), 0
for u, fs in pages.items():
    h = open(fs[0], encoding="utf-8", errors="ignore").read()
    try:
        p = HTMLParser(); p.feed(h); p.close()
    except Exception: pf += 1
    for t in ctx(h):
        inl[t] += 1
        if t not in exist and t not in redir: broken[t] += 1
lk = [u for u in pages if u not in EXCLUDE and not re.match(r"/google[0-9a-f]{16}$", u)]
orph = sum(1 for u in lk if inl[u] == 0)
med = int(statistics.median([inl[u] for u in lk])) if lk else 0
print(f"indexable pages      {len(lk)}")
print(f"orphans              {orph}        (target 0)")
print(f"weak (1-2 inlinks)   {sum(1 for u in lk if 0 < inl[u] <= 2)}")
print(f"median inlinks       {med}        (target >=6)")
print(f"dead internal links  {sum(broken.values())}        (target 0)")
print(f"redirect loops       {loops}        (target 0 — RELEASE BLOCKER)")
print(f"HTML parse failures  {pf}        (target 0)")
if orph: print("\norphans:", ", ".join(sorted(u for u in lk if inl[u] == 0))[:600])
if broken: print("\ndead targets:", ", ".join(f"{t}({c})" for t, c in broken.most_common(10)))
sys.exit(1 if (orph or sum(broken.values()) or loops or pf) else 0)
