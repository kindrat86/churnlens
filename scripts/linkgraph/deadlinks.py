#!/usr/bin/env python3
"""
Repair dead internal links on churnlens.site (157 links -> 43 non-existent URLs).

Policy, deliberately conservative:
  * REMAP only when the dead slug is the same entity or the correct parent audience
    page (verified against the pages that actually exist).
  * Otherwise REMOVE the link rather than invent a destination:
      - inside a <li>, drop the whole list item
      - in prose, unwrap the <a> and keep the text
  * Never invents a redirect that would mislead a reader (e.g. Gainsight -> ChurnZero).

Usage: deadlinks.py --root <dir> [--apply]
"""
import os, re, argparse, collections

SKIP = ("i18n", "i18n_out", "dist", ".vercel", "public", "node_modules", ".git")

# Same entity, or the correct audience parent. Verified against existing pages.
REMAP = {
    "/benchmarks/saas-churn-rate-2026":            "/benchmarks/saas-churn-rate",
    "/benchmarks/saas-logo-churn":                 "/benchmarks/logo-retention-benchmarks",
    "/industries/martech":                         "/industries/martech-saas",
    "/industries/devtools":                        "/industries/devtools-saas",
    "/industries/vertical-saas-churn-patterns":    "/industries/vertical-saas",
    "/templates/revenue-quality-scorecard-template": "/templates/revenue-quality-scorecard",
    "/for/search-funds":                           "/for/searchers",
    "/for/search-fund-operators":                  "/for/searchers",
    "/for/saas-founders-selling":                  "/for/founders-selling",
    "/for/indie-acquirers":                        "/for/saas-acquirers",
    "/for/saas-brokers":                           "/for/saas-acquirers",
    "/for/investment-bankers":                     "/for/ma-advisors",   # investment bankers == M&A advisors
    "/for/micro-pe":                               "/for/pe-analysts",
    # SaaSOptics rebranded to Maxio, so this is the same product:
    "/vs/maxio":                                   "/vs/saasoptics",
}


def url_for(rel):
    u = "/" + rel.replace(os.sep, "/")
    if u.endswith("/index.html"):
        u = u[:-11]
    elif u.endswith(".html"):
        u = u[:-5]
    return u or "/"


def norm(t):
    t = t.split("#")[0].split("?")[0]
    if t.endswith(".html"):
        t = t[:-5]
    if t.endswith("/index"):
        t = t[:-6]
    if len(t) > 1 and t.endswith("/"):
        t = t[:-1]
    return t or "/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = a.root.rstrip("/")

    # --- resolve vercel.json redirects to their terminal destination ---
    import json as _json
    redir = {}
    vj = os.path.join(root, "vercel.json")
    if os.path.exists(vj):
        for r in _json.load(open(vj)).get("redirects", []):
            src, dst = r.get("source", ""), r.get("destination", "")
            if "(" in src or ":" in src or not src.startswith("/"):
                continue
            redir[src.rstrip("/") or "/"] = dst
    def terminal(u, seen=None):
        seen = seen or set()
        cur = u
        while True:
            k = cur.split("#")[0].rstrip("/") or "/"
            if k in seen or k not in redir:
                return cur
            seen.add(k)
            cur = redir[k]
    REDIR_RESOLVED = {k: terminal(k) for k in redir}
    REDIR_RESOLVED = {k: v for k, v in REDIR_RESOLVED.items()
                      if (v.split("#")[0].rstrip("/") or "/") != k}
    print(f"redirect rules loaded: {len(redir)}  usable remaps: {len(REDIR_RESOLVED)}")

    exist, files = set(), []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root)
            if any(p in SKIP for p in rel.split(os.sep)):
                continue
            if f.endswith(".html"):
                exist.add(url_for(rel))
                files.append(full)
            exist.add("/" + rel.replace(os.sep, "/"))

    remapped = collections.Counter()
    dropped_li = collections.Counter()
    unwrapped = collections.Counter()
    touched = 0

    ASSET = re.compile(r"\.(css|js|png|jpe?g|svg|ico|xml|txt|json|webp|pdf|gif)$", re.I)

    for fp in files:
        h = open(fp, encoding="utf-8", errors="ignore").read()
        orig = h

        # 0. point links at the terminal destination of any vercel redirect
        for src, dst in REDIR_RESOLVED.items():
            for variant in (src, src + "/", src + ".html"):
                if f'href="{variant}"' in h:
                    h = h.replace(f'href="{variant}"', f'href="{dst}"')
                    remapped["(redirect) " + src] += 1

        # 1. remap known-good targets (href value only, exact match)
        for dead, good in REMAP.items():
            for variant in (dead, dead + "/", dead + ".html"):
                if f'href="{variant}"' in h:
                    h = h.replace(f'href="{variant}"', f'href="{good}"')
                    remapped[dead] += 1

        # 2. drop <li> items whose only link is dead
        def li_repl(m):
            block = m.group(0)
            hrefs = [norm(x) for x in re.findall(r'href="(/[^"]*)"', block)]
            hrefs = [x for x in hrefs if not ASSET.search(x)]
            if not hrefs:
                return block
            if all(x not in exist for x in hrefs):
                dropped_li[hrefs[0]] += 1
                return ""
            return block

        h = re.sub(r"(?is)<li\b[^>]*>.*?</li>\s*", li_repl, h)

        # 3. unwrap remaining dead links in prose, keeping the text
        def a_repl(m):
            href, inner = m.group(1), m.group(2)
            t = norm(href)
            if ASSET.search(t) or t in exist:
                return m.group(0)
            unwrapped[t] += 1
            return inner

        h = re.sub(r'<a\s[^>]*href="(/[^"]*)"[^>]*>(.*?)</a>', a_repl, h, flags=re.S)

        if h != orig:
            touched += 1
            if a.apply:
                open(fp, "w", encoding="utf-8").write(h)

    print(f"files touched: {touched}")
    rd = {k: v for k, v in remapped.items() if k.startswith("(redirect) ")}
    rm = {k: v for k, v in remapped.items() if not k.startswith("(redirect) ")}
    print(f"\nRETARGETED to redirect destination (no hop): {sum(rd.values())} links")
    for k, v in sorted(rd.items(), key=lambda x: -x[1])[:10]:
        src = k.replace("(redirect) ", "")
        print(f"   {v:>3}x {src}  ->  {REDIR_RESOLVED[src]}")
    print(f"\nREMAPPED (same entity / correct parent): {sum(rm.values())} links")
    for k, v in sorted(rm.items(), key=lambda x: -x[1]):
        print(f"   {v:>3}x {k}  ->  {REMAP[k]}")
    print(f"\nLIST ITEMS DROPPED (dead, no honest target): {sum(dropped_li.values())}")
    for k, v in dropped_li.most_common(15):
        print(f"   {v:>3}x {k}")
    print(f"\nPROSE LINKS UNWRAPPED (text kept): {sum(unwrapped.values())}")
    for k, v in unwrapped.most_common(15):
        print(f"   {v:>3}x {k}")
    if not a.apply:
        print("\nDRY RUN — nothing written.")


if __name__ == "__main__":
    main()
