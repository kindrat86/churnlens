#!/usr/bin/env python3
"""Static light/dark contrast audit for pages whose own <style> hardcodes colours.

Why static rather than browser-driven: 217 served pages x 2 colour schemes is far
too slow to drive through a browser, and the emulated-colour-scheme switch in the
preview pane was observed returning stale computed styles (it reported
--ux-surface:#ffffff while body background computed to #0f172a, which is
impossible since body background *is* var(--ux-surface)). So the model is computed
here and spot-validated against a real browser load.

The model, mirroring how these pages actually cascade:
  * ux.css defines the theme tokens on :root, light by default and overridden
    inside @media (prefers-color-scheme: dark).
  * A page's own <style> that appears BEFORE the ux.css <link> loses to ux.css at
    equal specificity, and wins if it appears AFTER.
  * ux.css sets a colour on `body` but NOT on `p`, `li`, `td`, `.lead`, `footer`
    etc., so a hardcoded colour on those selectors wins regardless of order.
  * Effective background is the page's own hardcoded body background if it has
    one, else var(--ux-surface) for the active scheme.

Usage: python3 scripts/theme_contrast_audit.py [--json out.json]
Exit 1 if any served page falls below WCAG AA (4.5:1) in either scheme.
"""
from __future__ import annotations

import json
import os
import re
import sys

SKIP = ("i18n", "i18n_out", "dist", ".vercel", "public", "node_modules", ".git",
        "assets", "scripts", "schema", "embed", "widgets", "api")
# Pages that are fragments or intentionally standalone, not page-flow documents.
SKIP_FILES = {"404.html", "badge.html", "network-widget.html"}

AA = 4.5
AA_LARGE = 3.0

TOKENS = {
    "light": {"--ux-surface": "#ffffff", "--ux-surface-raised": "#f8fafc",
              "--ux-text": "#0f172a", "--ux-text-secondary": "#475569",
              "--ux-text-muted": "#94a3b8", "--ux-border": "#e2e8f0"},
    "dark":  {"--ux-surface": "#0f172a", "--ux-surface-raised": "#1e293b",
              "--ux-text": "#f1f5f9", "--ux-text-secondary": "#94a3b8",
              "--ux-text-muted": "#64748b", "--ux-border": "#334155"},
}

# Selectors ux.css itself gives a colour to (so page order decides the winner).
UXCSS_COLOURED = {"body"}
# Text selectors worth auditing, with whether they render as large text.
TEXT_SELECTORS = ["body", "p", ".lead", "footer"]
# Deliberately excluded: summary, td, th, dd, dt, blockquote, li. Those sit inside
# cards that carry their own background, so comparing them to the body background
# produces false positives. They need element-level review, not this model.
LARGE = {"h1", "h2", "h3"}


def hex2rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def lum(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = lum(fg), lum(bg)
    return round((max(a, b) + 0.05) / (min(a, b) + 0.05), 2)


def resolve(value: str, scheme: str, local: dict | None = None):
    """Resolve a CSS colour value to rgb, through var(--tok, fallback), the ux.css
    theme tokens, and any custom properties the page defines itself."""
    local = local or {}
    value = value.strip()
    m = re.match(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)", value)
    if m:
        tok, fb = m.group(1), m.group(2)
        if tok in TOKENS[scheme]:
            return hex2rgb(TOKENS[scheme][tok])
        if tok in local:
            return resolve(local[tok], scheme, local)
        return resolve(fb, scheme, local) if fb else None
    if value.startswith("#"):
        return hex2rgb(value)
    m = re.match(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)", value)
    if m:
        return tuple(int(m.group(i)) for i in (1, 2, 3))
    return {"white": (255, 255, 255), "black": (0, 0, 0)}.get(value.lower())


def local_props(css: str) -> dict:
    """Custom properties the page declares on :root / html / body."""
    out = {}
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = [s.strip() for s in m.group(1).split(",")]
        if not any(s in (":root", "html", "body") for s in sels):
            continue
        for d in re.finditer(r"(--[\w-]+)\s*:\s*([^;!}]+)", m.group(2)):
            out[d.group(1)] = d.group(2).strip()
    return out


def strip_dark_mq(css: str) -> str:
    """Remove @media prefers-color-scheme:dark blocks (brace-balanced)."""
    out, i = [], 0
    while True:
        m = re.search(r"@media[^{]*prefers-color-scheme:\s*dark[^{]*\{", css[i:])
        if not m:
            out.append(css[i:])
            break
        start = i + m.start()
        out.append(css[i:start])
        j = i + m.end()
        depth = 1
        while j < len(css) and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        i = j
    return "".join(out)


def decls_for(css: str, selector: str, prop: str):
    """Last declaration of `prop` in a rule whose selector list contains
    `selector` as a whole token, ignoring descendant/compound selectors."""
    found = None
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = [s.strip() for s in m.group(1).split(",")]
        if selector not in sels:
            continue
        for d in re.finditer(rf"(?:^|;)\s*{prop}\s*:\s*([^;!]+)", m.group(2)):
            found = d.group(1).strip()
    return found


def audit_page(rel: str):
    t = open(rel, encoding="utf-8", errors="replace").read()
    ux = t.find("/ux.css")
    if ux < 0:
        return None
    own = []
    page_wins_body = False
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", t, re.S):
        own.append(strip_dark_mq(m.group(1)))
        if m.start() > ux:
            page_wins_body = True
    if not own:
        return None
    css = "\n".join(own)
    local = local_props(css)

    rows = []
    for scheme in ("light", "dark"):
        # effective page background
        own_bg = decls_for(css, "body", "background-color") or decls_for(css, "body", "background")
        bg = None
        if own_bg:
            # background shorthand: try each token until one resolves to a colour
            for tokv in re.findall(r"var\([^)]*\)|#[0-9a-fA-F]{3,6}|rgba?\([^)]*\)|\b[a-z]+\b", own_bg):
                bg = resolve(tokv, scheme, local)
                if bg:
                    break
        if bg is None:
            bg = hex2rgb(TOKENS[scheme]["--ux-surface"])

        for sel in TEXT_SELECTORS:
            own_col = decls_for(css, sel, "color")
            if not own_col:
                continue
            # ux.css colours `body`; if the page's block comes first, ux.css wins
            if sel in UXCSS_COLOURED and not page_wins_body:
                continue
            fg = resolve(own_col, scheme, local)
            if fg is None:
                continue
            # a page that hardcodes its own background for this surface is
            # self-consistent; only flag the pair actually rendered
            ratio = contrast(fg, bg)
            need = AA_LARGE if sel in LARGE else AA
            if ratio < need:
                rows.append({"scheme": scheme, "selector": sel,
                             "color": own_col, "bg": "#%02x%02x%02x" % bg,
                             "ratio": ratio, "need": need})
    return rows


def main() -> None:
    pages = []
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in fn:
            if not f.endswith(".html") or f in SKIP_FILES:
                continue
            rel = os.path.relpath(os.path.join(dp, f), ".")
            if any(p in SKIP for p in rel.split(os.sep)):
                continue
            pages.append(rel)

    failures, by_scheme = {}, {"light": 0, "dark": 0}
    for rel in sorted(pages):
        rows = audit_page(rel)
        if rows:
            failures[rel] = rows
            for s in {r["scheme"] for r in rows}:
                by_scheme[s] += 1

    print(f"served pages audited      {len(pages)}")
    print(f"pages failing WCAG AA     {len(failures)}")
    print(f"  broken in dark mode     {by_scheme['dark']}")
    print(f"  broken in light mode    {by_scheme['light']}")
    if failures:
        agg = {}
        for rel, rows in failures.items():
            for r in rows:
                k = (r["scheme"], r["selector"], r["color"], r["bg"], r["ratio"])
                agg[k] = agg.get(k, 0) + 1
        print("\nworst patterns:")
        for (sch, sel, col, bg, ratio), n in sorted(agg.items(), key=lambda kv: (kv[0][4], -kv[1]))[:12]:
            print(f"  {n:4d} pages  {sch:5s}  {sel:9s} {col:22s} on {bg}  = {ratio}:1")
    if "--json" in sys.argv:
        json.dump(failures, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
