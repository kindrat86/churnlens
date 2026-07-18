#!/bin/bash
# Pre-deploy QA gate for churnlens.site — run from the repo root before every deploy.
# Exits non-zero (aborting the deploy) if any check fails.
set -u
cd "$(dirname "$0")/.." || exit 1

# Positioning guardrail: abort the deploy if privacy-browser drift appears.
# ChurnLens is a SaaS churn/due-diligence tool, not a privacy tool.
# (see growth-engine GUARDRAILS.md §2)
python3 "$HOME/.growth-engine/inject-disambiguation.py" churnlens || true
node scripts/guard-positioning.mjs || exit 1

python3 - <<'PYEOF'
import os, re, sys, json
import xml.etree.ElementTree as ET

ROOT = os.getcwd()
SKIP_DIRS = {".git", ".vercel", "i18n", "i18n_out", "public", "api",
             "scripts", ".well-known", "node_modules"}
fails = []

def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        parts = [] if rel == "." else rel.split(os.sep)
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        for f in filenames:
            if f.endswith(".html"):
                yield os.path.join(dirpath, f)

# 1. vercel.json parses
try:
    cfg = json.load(open("vercel.json"))
except Exception as e:
    fails.append(f"vercel.json invalid JSON: {e}")
    cfg = {"rewrites": []}

root_rw, slug_html, slug_index = set(), set(), set()
for rw in cfg.get("rewrites", []):
    src, dst = rw.get("source", ""), rw.get("destination", "")
    m = re.fullmatch(r"/([a-z0-9-]+)/:slug", src)
    if m:
        (slug_html if dst.endswith(":slug.html") else slug_index).add(m.group(1))
    elif re.fullmatch(r"/[A-Za-z0-9.-]+", src) and dst == src + ".html":
        root_rw.add(src.lstrip("/"))

# 2. sitemap well-formed + every <loc> routable
try:
    tree = ET.parse("sitemap.xml")
    locs = [e.text for e in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if not locs:
        fails.append("sitemap.xml has zero <loc> entries")
    for loc in locs:
        p = loc.replace("https://churnlens.site", "") or "/"
        if p == "/":
            ok = os.path.isfile("index.html")
        else:
            segs = p.strip("/").split("/")
            if len(segs) == 1:
                n = segs[0]
                ok = (n in root_rw and os.path.isfile(n + ".html")) or \
                     os.path.isfile(os.path.join(n, "index.html"))
            elif len(segs) == 2:
                sec, slug = segs
                ok = os.path.isfile(os.path.join(sec, slug, "index.html")) or \
                     (sec in slug_html and os.path.isfile(os.path.join(sec, slug + ".html")))
            else:
                ok = False
        if not ok:
            fails.append(f"sitemap URL does not map to a file: {loc}")
except Exception as e:
    fails.append(f"sitemap.xml unparseable: {e}")

href_space = re.compile(r'href="((?:https://churnlens\.site)?/[^"?#]*(?: |%20)[^"?#]*)"')
title_dbl = re.compile(r"<title>[^<]*\b(\w+) \1\b[^<]*</title>", re.I)
asset_ref = re.compile(r'(?:href|src)="(/assets/[^"?#]+)"')
placeholder = re.compile(r"\{\{[a-z_]+\}\}|TODO_|LOREM IPSUM", re.I)

for path in html_files():
    relp = os.path.relpath(path, ROOT)
    s = open(path, encoding="utf-8", errors="replace").read()
    # 3. no literal-space / %20 internal hrefs
    m = href_space.search(s)
    if m:
        fails.append(f"{relp}: space in href {m.group(0)[:80]}")
    # 4. no doubled words in <title>
    m = title_dbl.search(s)
    if m and m.group(1).lower() not in ("that", "had"):
        fails.append(f"{relp}: doubled word in title ('{m.group(1)} {m.group(1)}')")
    # 5. every referenced /assets/* exists on disk
    for ref in asset_ref.findall(s):
        if not os.path.isfile(ref.lstrip("/")):
            fails.append(f"{relp}: references missing asset {ref}")
    # 6. no template placeholders
    m = placeholder.search(s)
    if m:
        fails.append(f"{relp}: placeholder text '{m.group(0)}'")

if fails:
    print(f"QA GATE FAILED — {len(fails)} problem(s):")
    for f in fails[:50]:
        print("  ✗", f)
    sys.exit(1)
print("QA gate passed.")
PYEOF
