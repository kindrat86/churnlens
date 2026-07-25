#!/usr/bin/env python3
"""Sweep the shared lead-magnet block's contrast failures across every page carrying it.

`fix_checklist_contrast.py` fixed these on get-the-checklist only. Measuring /pricing
in a browser showed the identical failures there: the block is injected on ~45 served
pages, so the fix belonged repo-wide rather than on one page.

Only fixes that are correct on BOTH a dark and a light page are swept, because the
site is split: 148 served pages carry `<html data-cl-theme="dark">` and render dark
for everyone, while 52 have no such attribute and follow the OS preference. A value
that is right on one is not automatically right on the other.

 1-3. The `background:white` and `background:#fef3c7` cards set their own LIGHT
      background but no text colour, so children inherit the page's light text and
      render light-on-light. A hardcoded dark colour is correct on both kinds of page
      precisely because the card's own background is always light — a theme token
      would be wrong here, since it would follow the page rather than the card.
 4.   The "No spam" line at #888 sits inside that white card: 3.54:1 -> #475569 7.58:1.
 5.   The glossary <dd> at #555 renders on the PAGE background, not on a card, so it
      must follow the theme: `var(--ux-text-secondary, #555)` gives #94a3b8 on dark
      (6.96:1) and #475569 on light (7.58:1). Hardcoding the dark value here would
      break the 52 OS-following pages in light mode.

Deliberately NOT swept: `color: var(--cl-blue-light)` as text (13 pages). #60a5fa
clears AA on a dark card but not on a light surface, and which pages place it on
which is not determinable without per-page surface analysis. It stays fixed only on
get-the-checklist, where it was measured. Marginal anyway (3.58-3.98:1).

Idempotent. Usage: python3 scripts/fix_shared_leadmagnet_contrast.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SKIP = {"i18n", "i18n_out", "public", "dist", "node_modules", ".git", ".vercel"}

FIXES = [
    ("white card: explicit dark text",
     'style="background:white;border-radius:12px;padding:20px',
     'style="background:white;color:#0f172a;border-radius:12px;padding:20px'),
    ("amber money-back card: explicit dark text",
     'style="background:#fef3c7;border-radius:8px',
     'style="background:#fef3c7;color:#0f172a;border-radius:8px'),
    ("'No spam' line 3.54 -> 7.58",
     'style="font-size:0.75rem;color:#888;margin-top:8px"',
     'style="font-size:0.75rem;color:#475569;margin-top:8px"'),
    # On the page background, so it must follow the theme rather than be pinned.
    ("glossary <dd>: theme-aware muted",
     '<dd style="margin:4px 0 0;color:#555">',
     '<dd style="margin:4px 0 0;color:var(--ux-text-secondary,#555)">'),
    # get-the-checklist was fixed earlier with the dark value hardcoded; make it
    # consistent with the rest so it is also correct if that page ever goes light.
    ("glossary <dd>: unpin earlier hardcoded dark value",
     '<dd style="margin:4px 0 0;color:#94a3b8">',
     '<dd style="margin:4px 0 0;color:var(--ux-text-secondary,#555)">'),
]


def main() -> None:
    dry = "--dry-run" in sys.argv
    files = 0
    per_fix = {d: 0 for d, _, _ in FIXES}
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in sorted(fn):
            if not f.endswith(".html"):
                continue
            p = Path(dp) / f
            t = p.read_text(encoding="utf-8", errors="replace")
            orig = t
            for desc, old, new in FIXES:
                if old in t:
                    per_fix[desc] += t.count(old)
                    t = t.replace(old, new)
            if t != orig:
                files += 1
                if not dry:
                    p.write_text(t, encoding="utf-8")
    print(f"{'would fix' if dry else 'fixed'}: {files} files")
    for d, n in per_fix.items():
        print(f"  {n:5d}  {d}")


if __name__ == "__main__":
    main()
