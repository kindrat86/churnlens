#!/usr/bin/env python3
"""Pin ux.css's theme tokens to their dark values on pages that are designed dark.

The defect this fixes, measured in a browser on get-the-checklist.html with a
light-preference OS: the <h1> rendered white-on-white (1:1) and 23 elements failed
WCAG AA.

Mechanism. The page is unambiguously designed dark — its own <style> sets
`body{background:var(--cl-navy)}` (`--cl-navy:#0f172a` on :root) and every card,
heading and badge hardcodes light text. But that <style> block sits at byte ~2.9k
while the /ux.css <link> is at ~14.4k, and ux.css carries
`body{background:var(--ux-surface);color:var(--ux-text)}`. Equal specificity, later
wins — so ux.css supplies the surface, and on a light-preference OS that surface is
white while all the page's own text stays light.

Fixing `body` alone would not be enough: other ux.css rules read the tokens too
(`a{color:var(--ux-accent)}` was overriding `.logo{color:#fff}` with #2563eb, giving
2.21:1 on a dark nav). Pinning the tokens themselves makes the whole ux.css theme
resolve dark on this page unconditionally, which is what the design already assumes,
instead of chasing individual rules.

`--ux-text-muted` is deliberately raised from ux.css's dark #64748b (3.75:1 on
#0f172a, below AA) to #94a3b8 (6.96:1).

Idempotent via the `theme-lock-v1` marker. Applies to a page and its flat/dir twin.

Usage: python3 scripts/lock_dark_pages.py <page.html> [more.html ...] [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MARKER = "theme-lock-v1"

BLOCK = """<!-- theme-lock-v1 -->
<style>
/* This page is designed dark: its own <style> sets body{background:var(--cl-navy)}
   and every card, heading and badge hardcodes light text. That block loads BEFORE
   /ux.css, whose body{background:var(--ux-surface);color:var(--ux-text)} wins at
   equal specificity — so on a light-preference OS the page put its light text on a
   white surface (the h1 was white-on-white, 1:1, and 23 elements failed WCAG AA).
   Pinning ux.css's own tokens to their dark values makes the whole theme resolve
   dark here unconditionally, which is what the design already assumes, rather than
   fighting individual ux.css rules one at a time. */
:root {
  color-scheme: dark;
  --ux-surface: #0f172a;
  --ux-surface-raised: #1e293b;
  --ux-text: #f1f5f9;
  --ux-text-secondary: #94a3b8;
  --ux-text-muted: #94a3b8;
  --ux-border: #334155;
  --ux-accent: #60a5fa;
  --ux-accent-hover: #93bbfd;
  --ux-accent-ghost: rgba(96, 165, 250, 0.12);
}
body { background: var(--cl-navy, #0f172a); color: #f8fafc; }
</style>
"""


def apply(path: Path, dry: bool) -> str:
    t = path.read_text(encoding="utf-8")
    if MARKER in t:
        return "already locked"
    # Insert immediately after the LAST ux.css <link>, so it wins the cascade.
    links = list(re.finditer(r'<link[^>]+href="/ux\.css"[^>]*>', t))
    if not links:
        return "no /ux.css link — skipped"
    at = links[-1].end()
    new = t[:at] + "\n" + BLOCK + t[at:]
    if not dry:
        path.write_text(new, encoding="utf-8")
    return "locked"


def twins(rel: str):
    """A flat page and its dir/index.html counterpart, whichever exist."""
    p = Path(rel)
    out = {p}
    if p.name == "index.html":
        out.add(Path(str(p.parent) + ".html"))
    elif p.suffix == ".html":
        out.add(p.with_suffix("") / "index.html")
    return sorted({q for q in out if q.exists()})


def main() -> None:
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("usage: lock_dark_pages.py <page.html> [...] [--dry-run]")
    for a in args:
        for p in twins(a):
            print(f"  {p}: {apply(p, dry)}")


if __name__ == "__main__":
    main()
