#!/usr/bin/env python3
"""Point internal links at the URL that actually serves, not at a 301.

232 internal links across the deployed tree pointed at URLs that vercel.json
301-redirects away — 35 distinct targets, mostly from thin-content consolidations
(/reviews/*-review-for-acquirers -> /vs/*, /learn/* -> the canonical article,
/integrations/* -> /vs/* or /export). Three of them redirected into /integrations,
which has no index.html and returns 404, so those were internal links to a dead end.

Every one of those links costs a crawler an extra request, dilutes the internal
link graph, and — for the ones ending in a 404 — leaks equity entirely. On a site
getting 908 impressions a quarter, crawl budget spent re-resolving our own
redirects is budget not spent on the 197 pages Google has never shown at all.

The redirects themselves stay: external links and old SERP entries still need
them. Only OUR OWN links are rewritten, and only to the FINAL destination
(chains are resolved, so a link never lands on another redirect).

Usage:  python3 scripts/fix_internal_links_to_redirects.py [--apply]
"""
import json
import os
import re
import sys
from collections import Counter

EXCLUDE_DIRS = {".git", "node_modules", ".vercel", ".claude", "dist", "i18n", "i18n_out", "scripts"}


def load_redirect_map():
    cfg = json.load(open("vercel.json", encoding="utf-8"))
    raw = {}
    for r in cfg.get("redirects", []):
        src = r.get("source", "")
        dst = r.get("destination", "")
        # Only literal, non-parameterised sources can be rewritten safely.
        if ":" in src or "*" in src or not src.startswith("/"):
            continue
        raw[src.rstrip("/") or "/"] = dst
    # Resolve chains so a rewritten link never lands on another redirect.
    resolved = {}
    for src in raw:
        seen, cur = {src}, raw[src]
        while True:
            key = cur.split("#")[0].split("?")[0].rstrip("/") or "/"
            if key in raw and key not in seen:
                seen.add(key)
                cur = raw[key]
                continue
            break
        resolved[src] = cur
    return resolved


def main():
    apply = "--apply" in sys.argv
    red = load_redirect_map()
    counts = Counter()
    files = set()

    for root, dirs, fnames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in fnames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            try:
                html = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if 'href="/' not in html:
                continue
            changed = 0

            def sub(m):
                nonlocal changed
                href = m.group(1)
                base = href.split("#")[0].split("?")[0]
                key = base.rstrip("/") or "/"
                if key not in red:
                    return m.group(0)
                tail = href[len(base):]          # keep #fragment / ?query
                dest = red[key]
                if dest.split("#")[0].rstrip("/") == key:
                    return m.group(0)           # would be a no-op
                changed += 1
                counts[f"{key} -> {dest}"] += 1
                return 'href="%s%s"' % (dest, tail if "#" not in dest else "")

            new = re.sub(r'href="(/[^"]*)"', sub, html)
            if changed:
                files.add(path)
                if apply:
                    open(path, "w", encoding="utf-8").write(new)

    print("MODE:", "APPLY" if apply else "DRY RUN")
    print("literal redirects in vercel.json:", len(red))
    print("internal links repointed:", sum(counts.values()), "across", len(files), "files")
    print("\ntop rewrites:")
    for k, v in counts.most_common(25):
        print("  %4d  %s" % (v, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
