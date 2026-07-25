#!/usr/bin/env python3
"""Emit the indexable page set (exists on disk, not noindex, not a verification stub)."""
import os, re
SKIP = ("i18n","i18n_out","dist",".vercel","public","node_modules",".git","assets","scripts","schema","embed","widgets","api")
out = []
for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
    for f in fn:
        if not f.endswith(".html"): continue
        rel = os.path.relpath(os.path.join(dp, f), ".")
        if any(p in SKIP for p in rel.split(os.sep)): continue
        u = "/" + rel.replace(os.sep, "/")
        u = u[:-11] if u.endswith("/index.html") else (u[:-5] if u.endswith(".html") else u)
        u = u or "/"
        h = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
        if re.search(r'name="robots"[^>]*content="[^"]*noindex', h, re.I): continue
        if re.match(r"/google[0-9a-f]{16}$", u): continue
        out.append(u)
print("\n".join(sorted(set(out))))
