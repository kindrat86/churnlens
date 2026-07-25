#!/usr/bin/env python3
"""
Internal Link Graph repair for churnlens.site.

Fixes, in order of impact:
  A. Homepage "Explore" hub directory   -> every hub gets an inlink from the strongest page
  B. Hub completeness                   -> each hub links to all of its own children
  C. Child -> hub + nearest siblings    -> every page gets contextual inlinks
  D. Anchor-text repair                 -> ".related-pages" blocks using raw *.html filenames
                                           get real page titles instead

Safety properties:
  * Idempotent. All injected markup is wrapped in <!-- ilg-v1 --> ... <!-- /ilg-v1 -->
    and replaced (not appended) on re-run.
  * Target set = sitemap URLs that return 200, minus utility/noindex pages.
    Never links to 404s, widgets, verification files or funnel-only pages.
  * Twin-aware: writes both `slug.html` and `slug/index.html` when both exist.
  * Never touches i18n/, i18n_out/, dist/, public/, .vercel/, assets/, scripts/.

Usage:  ilg.py --root <dir> [--apply]     (default is dry-run)
"""
import os, re, sys, json, html, argparse, collections, difflib

MARK_OPEN, MARK_CLOSE = "<!-- ilg-v1 -->", "<!-- /ilg-v1 -->"
SKIP_DIRS = ("i18n", "i18n_out", "dist", ".vercel", "public", "node_modules",
             ".git", "assets", "scripts", "schema", "embed", "widgets", "api")
# Pages that must never receive or emit editorial links (utility / funnel-only / noindex)
EXCLUDE_URLS = {
    "/404", "/thank-you", "/oto", "/badge", "/related-tools", "/network-widget",
    "/network/widget", "/striking-distance", "/index", "/affiliate", "/affiliates",
    "/masterclass", "/dream100", "/dream-100", "/citations", "/calculator",
    "/free/embed-widget", "/embed", "/embed/tools/portfolio-network", "/terms",
    "/privacy", "/contact", "/partners",
}
STOP = set("""a an the and or of for to in on with without your you our we is are be how what
why when which that this these those from by as it its at into vs versus guide 2026 2025 saas
churnlens best top free new more most can do does using use used about page pages tool tools""".split())


def is_skipped(path):
    parts = path.split(os.sep)
    return any(p in SKIP_DIRS for p in parts) or any(p.startswith(".") for p in parts if p)


def url_for(rel):
    u = "/" + rel.replace(os.sep, "/")
    if u.endswith("/index.html"):
        u = u[:-11]
    elif u.endswith(".html"):
        u = u[:-5]
    return u or "/"


def clean_title(t, url):
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    # strip brand suffixes/prefixes
    t = re.sub(r"\s*[|–—-]\s*Churn\s?Lens.*$", "", t, flags=re.I)
    t = re.sub(r"^\s*Churn\s?Lens\s*[|–—-]\s*", "", t, flags=re.I)
    t = re.sub(r"\s*\[\s*2026\s*Guide\s*\]\s*$", "", t, flags=re.I)
    t = t.strip(" -–—|·")
    if not t:
        t = url.rstrip("/").split("/")[-1].replace("-", " ").title()
    return t


def tokens(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


class Page:
    __slots__ = ("url", "files", "title", "desc", "family", "toks", "insite")

    def __init__(self, url):
        self.url, self.files = url, []
        self.title = self.desc = ""
        self.family = url.strip("/").split("/")[0] if url.count("/") > 1 else "(root)"
        self.toks = set()
        self.insite = True


def load(root):
    pages = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.startswith(".")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root)
            if is_skipped(rel):
                continue
            u = url_for(rel)
            p = pages.setdefault(u, Page(u))
            p.files.append(full)
            if p.title:
                continue
            h = open(full, encoding="utf-8", errors="ignore").read()
            m = re.search(r"(?is)<title[^>]*>(.*?)</title>", h)
            p.title = clean_title(m.group(1) if m else "", u)
            m = re.search(r'(?is)<meta\s+name="description"\s+content="([^"]*)"', h)
            p.desc = html.unescape(m.group(1)) if m else ""
            h1 = " ".join(re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", h))
            h1 = re.sub(r"(?s)<[^>]+>", " ", h1)
            p.toks = tokens(f"{p.title} {h1} {p.desc} {u.replace('/',' ').replace('-',' ')}")
    return pages


def contextual_links(h):
    """Links in the editorial body: nav, footer, and our own injected block removed."""
    b = re.sub(r"(?is)<nav.*?</nav>", " ", h)
    b = re.sub(r"(?is)<footer.*?</footer>", " ", b)
    b = re.sub(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE), " ", b, flags=re.S)
    out = set()
    for m in re.findall(r'href="([^"]+)"', b):
        m = m.split("#")[0].split("?")[0]
        if not m.startswith("/"):
            continue
        if m.endswith(".html"):
            m = m[:-5]
        if m.endswith("/index"):
            m = m[:-6]
        if len(m) > 1 and m.endswith("/"):
            m = m[:-1]
        out.add(m or "/")
    return out


def inject(h, block, marker_only=False):
    """Replace an existing ilg block, else insert at the best editorial position."""
    pat = re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE)
    if re.search(pat, h, re.S):
        return re.sub(pat, lambda _: block, h, count=1, flags=re.S)
    if marker_only:
        return h
    for anchor in ("</main>", "</article>"):
        i = h.rfind(anchor)
        if i != -1:
            return h[:i] + block + "\n" + h[i:]
    i = h.rfind("<footer")
    if i != -1:
        return h[:i] + block + "\n" + h[i:]
    i = h.rfind("</body>")
    if i != -1:
        return h[:i] + block + "\n" + h[i:]
    return h + block


def li(p):
    d = p.desc.split(".")[0].strip()
    if len(d) > 78:
        d = d[:75].rsplit(" ", 1)[0] + "…"
    tail = f" — {html.escape(d)}" if d else ""
    return f'<li><a href="{p.url}">{html.escape(p.title)}</a>{tail}</li>'


BOX = ('<div class="related-links ilg" style="background:rgba(148,163,184,0.14);'
       'padding:1rem 1.25rem;border-radius:.5rem;margin:2rem 0;">')


def related_block(heading, items):
    lis = "\n".join(li(p) for p in items)
    return (f'{MARK_OPEN}\n{BOX}\n<h3>{heading}</h3>\n'
            f'<ul style="margin:0.25rem 0 0;padding-left:1.25rem;">\n{lis}\n</ul>\n</div>\n{MARK_CLOSE}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--sitemap", required=True, help="file of live-200 sitemap URLs")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = a.root.rstrip("/")

    live = set()
    for l in open(a.sitemap):
        l = l.strip().replace("https://churnlens.site", "")
        if l:
            live.add(l.rstrip("/") or "/")

    pages = load(root)
    # linkable = in sitemap, 200, not utility
    linkable = {u: p for u, p in pages.items() if u in live and u not in EXCLUDE_URLS}
    print(f"pages found: {len(pages)}   linkable target set: {len(linkable)}")

    # ---- current graph (contextual only) ----
    inl = collections.Counter()
    body = {}
    for u, p in pages.items():
        h = open(p.files[0], encoding="utf-8", errors="ignore").read()
        body[u] = h
        for t in contextual_links(h):
            inl[t] += 1
    before_orphans = [u for u in linkable if inl[u] == 0]
    print(f"BEFORE: orphans among linkable = {len(before_orphans)}")

    # ---- families / hubs ----
    fam = collections.defaultdict(list)
    for u, p in linkable.items():
        fam[p.family].append(p)
    hubs = {}
    for f, kids in fam.items():
        if f == "(root)":
            continue
        hu = "/" + f
        if hu in linkable:
            hubs[f] = linkable[hu]

    edits = collections.defaultdict(list)   # file -> list of (kind, block)
    plan = []

    # ---- A. homepage Explore directory ----
    home = pages.get("/")
    if home:
        groups = [
            ("Core method", ["/5-risk-buyer-side-method", "/saas-m-and-a-due-diligence-framework",
                             "/sample-churn-risk-report", "/saas-churn-rate-benchmarks"]),
            ("Research & data", ["/benchmarks", "/data", "/research", "/stats", "/glossary"]),
            ("Free tools", ["/calculators", "/free/due-diligence-simulator", "/saas-valuation-calculator", "/tools"]),
            ("Compare tools", ["/vs", "/compare", "/alternatives-to", "/reviews", "/best", "/cost-of"]),
            ("By buyer & sector", ["/for", "/use-cases", "/industries", "/sectors", "/scenarios"]),
            ("Learn", ["/learn", "/guides", "/how-to", "/faq", "/answers", "/redflags",
                       "/checklists", "/templates", "/integrations", "/pricing-questions"]),
        ]
        rows = []
        for gname, urls in groups:
            got = [linkable[u] for u in urls if u in linkable]
            if got:
                rows.append((gname, got))
        if rows:
            inner = []
            for gname, got in rows:
                def short(t):
                    t = re.split(r"\s+[—–:|]\s+", t)[0]
                    t = re.sub(r"\s*\(2026\)\s*$", "", t).strip()
                    return t if len(t) <= 46 else t[:43].rsplit(" ", 1)[0] + "…"
                links = " · ".join(f'<a href="{p.url}">{html.escape(short(p.title))}</a>' for p in got)
                inner.append(f'<p style="margin:.45rem 0"><strong>{gname}:</strong> {links}</p>')
            blk = (f'{MARK_OPEN}\n<section class="related-links ilg" '
                   f'style="background:rgba(148,163,184,0.14);padding:1.25rem 1.5rem;'
                   f'border-radius:.5rem;margin:2.5rem 0;">\n'
                   f'<h2 style="margin-top:0">Explore ChurnLens</h2>\n'
                   + "\n".join(inner) + f'\n</section>\n{MARK_CLOSE}')
            for f in home.files:
                edits[f].append(("A: homepage explore", blk))
            n = sum(len(g) for _, g in rows)
            plan.append(f"A. homepage Explore directory -> {n} hub links across {len(rows)} groups")

    # ---- B. hub completeness ----
    b_count = 0
    for f, hub in sorted(hubs.items()):
        kids = sorted([p for p in fam[f] if p.url != hub.url], key=lambda p: p.title)
        if not kids:
            continue
        have = contextual_links(body[hub.url])
        missing = [k for k in kids if k.url not in have]
        if not missing:
            continue
        blk = related_block(f"All {html.escape(hub.title)} pages", kids)
        for fp in hub.files:
            edits[fp].append((f"B: hub /{f} (+{len(missing)} child links)", blk))
        b_count += len(missing)
        plan.append(f"B. hub /{f}: +{len(missing)} missing child links (lists all {len(kids)})")
    print(f"B total new hub->child links: {b_count}")

    # ---- C. child -> hub + nearest siblings ----
    c_count = 0
    for u, p in sorted(linkable.items()):
        if p.url in hubs.values() or any(p.url == h.url for h in hubs.values()):
            continue
        if u == "/":
            continue
        have = contextual_links(body[u])
        picks, seen = [], {u}
        hub = hubs.get(p.family)
        if hub and hub.url not in seen:
            picks.append(hub); seen.add(hub.url)
        sibs = [q for q in fam[p.family] if q.url not in seen]
        pool = sibs + [q for q in linkable.values() if q.url not in seen and q.family != p.family]
        scored = []
        for q in pool:
            if q.url in seen:
                continue
            ov = len(p.toks & q.toks) / max(1, len(p.toks | q.toks))
            if q in sibs:
                ov += 0.12          # prefer same-family
            scored.append((ov, q.url, q))
        scored.sort(key=lambda x: (-x[0], x[1]))
        for ov, _, q in scored:
            if len(picks) >= 5:
                break
            if ov <= 0.02 or q.url in seen:
                continue
            picks.append(q); seen.add(q.url)
        if len(picks) < 3:
            for _, _, q in scored:
                if len(picks) >= 3:
                    break
                if q.url not in seen:
                    picks.append(q); seen.add(q.url)
        new = [q for q in picks if q.url not in have]
        if not new:
            continue
        blk = related_block("Related", picks)
        for fp in p.files:
            edits[fp].append((f"C: {u} (+{len(new)})", blk))
        c_count += len(new)
    print(f"C total new sibling/hub links: {c_count}")

    # ---- D. anchor-text repair on .related-pages blocks ----
    d_files = 0
    d_fix = 0
    title_by_url = {u: p.title for u, p in pages.items()}
    for u, p in pages.items():
        for fp in p.files:
            h = open(fp, encoding="utf-8", errors="ignore").read()
            if 'class="related-pages"' not in h:
                continue
            def repl(m):
                nonlocal d_fix
                href, txt = m.group(1), m.group(2)
                if not re.fullmatch(r"[a-z0-9\-/]+\.html", txt.strip(), flags=re.I):
                    return m.group(0)
                key = href.rstrip("/") or "/"
                t = title_by_url.get(key)
                if not t:
                    t = txt.strip()[:-5].replace("-", " ").title()
                d_fix += 1
                return f'<a href="{href}">{html.escape(t)}</a>'
            new = re.sub(r'<a href="(/[^"]*)">([^<]*\.html)</a>', repl, h)
            if new != h:
                d_files += 1
                edits[fp].append(("D: anchor-text repair", ("__RAW__", new)))
    print(f"D anchor-text repairs: {d_fix} links across {d_files} files")

    # ---- report ----
    print("\n=== PLAN ===")
    for l in plan[:40]:
        print("  " + l)
    if len(plan) > 40:
        print(f"  ... and {len(plan)-40} more")
    print(f"\nfiles to modify: {len(edits)}")

    if not a.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply")
        return

    # ---- apply ----
    written = 0
    for fp, ops in edits.items():
        h = open(fp, encoding="utf-8", errors="ignore").read()
        orig = h
        for kind, blk in ops:
            if isinstance(blk, tuple) and blk[0] == "__RAW__":
                h = blk[1]
            else:
                h = inject(h, blk)
        if h != orig:
            open(fp, "w", encoding="utf-8").write(h)
            written += 1
    print(f"\nWROTE {written} files")


if __name__ == "__main__":
    main()
