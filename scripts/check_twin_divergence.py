#!/usr/bin/env python3
"""Release gate: the .html twin and the directory twin must agree on what they declare.

41 routes in this repo exist twice — `foo.html` and `foo/index.html`. Vercel serves
the DIRECTORY one at `/foo` and 308s `/foo.html` to it, so the `.html` copy is dead
weight that nobody sees. That is harmless right up until someone edits it, at which
point the edit silently does nothing in production.

This cost real time twice on 2026-08-12 alone:
  * `/network` was set to noindex in network.html; production kept serving
    `index, follow` from network/index.html.
  * The "funded by subscribers" claim was removed from about.html; /about kept
    serving it from about/index.html.

Both passed every other gate. Neither was visible without checking the live URL.

So this asserts that for every twin pair the two files agree on the things that
change what a crawler or a reader is told:
  * the robots meta directive
  * the canonical URL
  * a small set of claim strings that must never resurface

It does NOT demand byte-equality — 12 pairs differ legitimately in body copy and
that is not this gate's business. It only cares about declarations that must not
diverge, plus claims that must not come back.

Exit 1 on any divergence. Wire into scripts/qa-check.sh.
"""
import os
import re
import sys

EXCLUDE_DIRS = {".git", "node_modules", ".vercel", ".claude", "dist", "i18n", "i18n_out", "scripts"}

ROBOTS = re.compile(r'<meta\s+name="robots"[^>]*content="([^"]+)"', re.I)
CANON = re.compile(r'rel="canonical"[^>]*href="([^"]+)"', re.I)

# Claims removed on 2026-08-12 that must not reappear on either twin. Each one
# shipped live for weeks; every one of them was false.
BANNED = [
    ("funded by subscribers", "there are no subscribers; lifetime revenue is $0"),
    ("npm install saas-metrics", "that package is a 404 on the npm registry"),
    ("created by our editorial team", "there is no editorial team"),
    ("Already integrated", "there is no integration with any billing platform"),
    ("author-byline eeat", "hidden 1x1 clipped byline — Google spam policy"),
    ('"name":"Churn Lens"', "the brand is one word: ChurnLens"),
]


def twin_pairs():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if not fn.endswith(".html") or fn == "index.html":
                continue
            flat = os.path.join(root, fn)
            nested = os.path.join(root, fn[:-len(".html")], "index.html")
            if os.path.isfile(nested):
                yield flat, nested


def read(path):
    try:
        return open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def main():
    problems = []

    for flat, nested in twin_pairs():
        a, b = read(flat), read(nested)
        ra, rb = ROBOTS.findall(a), ROBOTS.findall(b)
        # noindex on one twin and not the other is the failure that matters:
        # the served copy silently keeps the old directive.
        if ("noindex" in " ".join(ra)) != ("noindex" in " ".join(rb)):
            problems.append(
                "%s\n      robots disagree — .html says %s, served dir says %s\n"
                "      Vercel serves the DIRECTORY twin; editing the .html changes nothing."
                % (flat, ra or ["(none)"], rb or ["(none)"]))
        ca, cb = CANON.findall(a), CANON.findall(b)
        if ca and cb and ca != cb:
            problems.append("%s\n      canonical disagrees — .html %s vs served dir %s" % (flat, ca, cb))

    banned_hits = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            html = read(path)
            for needle, why in BANNED:
                if needle in html:
                    banned_hits.append("%s\n      contains %r — %s" % (path, needle, why))

    if problems:
        print("[check_twin_divergence] FAIL - %d twin pair(s) disagree on what they declare:\n" % len(problems))
        for p in problems:
            print("  " + p)
        print()
    if banned_hits:
        print("[check_twin_divergence] FAIL - %d file(s) carry a claim that was removed as false:\n" % len(banned_hits))
        for h in banned_hits[:20]:
            print("  " + h)
        print()

    if problems or banned_hits:
        return 1
    print("[check_twin_divergence] OK - twins agree on robots/canonical; no retired claims resurfaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
