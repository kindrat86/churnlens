#!/usr/bin/env python3
"""Remaining WCAG AA failures on get-the-checklist, plus one repo-wide trust-bar value.

scripts/lock_dark_pages.py fixed the root cause (ux.css was supplying a white
surface to a page designed dark) and took the page from 23 AA failures to 10.
These are the rest, each verified in a browser with alpha-composited ancestor
backgrounds.

Page-local (get-the-checklist.html + its dir twin):

 1. The `background:white` card. It is deliberately a LIGHT card, but it sets no
    text colour, so its children inherited body's #f8fafc and rendered
    white-on-white (1.05:1). Give the card an explicit dark text colour rather than
    darkening each child, so anything added to it later is correct by default.
 2. "No spam. Unsubscribe anytime." inside that card: #888 on white is 3.54:1.
    -> #475569 (7.58:1), the same token value used elsewhere for muted text.
 3. The `background:#fef3c7` money-back card. Same shape as (1): a light amber card
    whose <strong> inherited #f8fafc, 1.06:1.
 4. `--cl-blue-light` (#3b82f6) used as TEXT on the page's dark cards: 3.58-3.98:1.
    The token itself must not be lightened - it is also a button BACKGROUND twice,
    and white-on-#60a5fa would drop to 2.5:1. So add a separate text-only token and
    switch the colour usages to it. #60a5fa measures 5.78:1 on #1e293b.

Repo-wide:

 5. The injected Brunson trust bar's small print is #6b7178 on its own dark gradient
    = 3.62:1, below AA, on every page carrying the bar. The component already uses
    #94a3b8 for its stat labels, so that is the consistent value and it measures
    ~5.9:1 on #1e293b. One value, mechanical, same defect class.

Idempotent: every replacement is a no-op once applied.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

PAGES = ["get-the-checklist.html", "get-the-checklist/index.html"]

PAGE_FIXES = [
    # (description, old, new)
    ("white card: give it explicit dark text",
     'style="background:white;border-radius:12px;padding:20px;max-width:500px;margin:0 auto 16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)"',
     'style="background:white;color:#0f172a;border-radius:12px;padding:20px;max-width:500px;margin:0 auto 16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)"'),
    ("'No spam' line: #888 on white 3.54 -> 7.58",
     'style="font-size:0.75rem;color:#888;margin-top:8px"',
     'style="font-size:0.75rem;color:#475569;margin-top:8px"'),
    ("amber money-back card: give it explicit dark text",
     'style="background:#fef3c7;border-radius:8px;padding:12px;margin:12px 0;text-align:center"',
     'style="background:#fef3c7;color:#0f172a;border-radius:8px;padding:12px;margin:12px 0;text-align:center"'),
    # The glossary <dd>s sit directly on the dark page: #555 is 2.39:1 there.
    # Matched on the exact dd pattern, NOT on #555 generally — the fourth #555 on
    # this page is inside the white card, where it is 7.46:1 and correct.
    ("glossary <dd>: #555 on the dark page 2.39 -> 6.96",
     '<dd style="margin:4px 0 0;color:#555">',
     '<dd style="margin:4px 0 0;color:#94a3b8">'),
]

# --cl-blue-light is ALSO a button background twice; only the colour usages move.
BLUE_TEXT_TOKEN = "--cl-blue-text"
BLUE_TEXT_VALUE = "#60a5fa"

TRUSTBAR_OLD = "color:#6b7178"
TRUSTBAR_NEW = "color:#94a3b8"

SKIP = ("i18n", "i18n_out", "dist", ".vercel", "public", "node_modules", ".git")


def fix_page(p: Path, dry: bool) -> list[str]:
    t = p.read_text(encoding="utf-8")
    log = []
    for desc, old, new in PAGE_FIXES:
        if old in t:
            t = t.replace(old, new)
            log.append(desc)
    # colour usages of --cl-blue-light -> the new text-only token
    t2, n = re.subn(r"color:\s*var\(--cl-blue-light\)",
                    f"color: var({BLUE_TEXT_TOKEN}, {BLUE_TEXT_VALUE})", t)
    if n:
        t = t2
        log.append(f"--cl-blue-light as text -> {BLUE_TEXT_TOKEN} ({n} usages)")
    # declare the token alongside the other --cl-* on :root
    if BLUE_TEXT_TOKEN not in t.split("<style>")[0] and f"{BLUE_TEXT_TOKEN}:" not in t:
        t, k = re.subn(r"(--cl-blue-light:\s*#3b82f6;)",
                       rf"\1 {BLUE_TEXT_TOKEN}: {BLUE_TEXT_VALUE};", t, count=1)
        if k:
            log.append(f"declared {BLUE_TEXT_TOKEN} on :root")
    if log and not dry:
        p.write_text(t, encoding="utf-8")
    return log


def sweep_trustbar(dry: bool) -> int:
    n = 0
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = Path(dp) / f
            t = p.read_text(encoding="utf-8", errors="replace")
            if TRUSTBAR_OLD not in t:
                continue
            if not dry:
                p.write_text(t.replace(TRUSTBAR_OLD, TRUSTBAR_NEW), encoding="utf-8")
            n += 1
    return n


def main() -> None:
    dry = "--dry-run" in sys.argv
    for rel in PAGES:
        p = Path(rel)
        if not p.exists():
            print(f"  {rel}: missing")
            continue
        log = fix_page(p, dry)
        print(f"  {rel}: {', '.join(log) if log else 'no change (already fixed)'}")
    n = sweep_trustbar(dry)
    print(f"trust-bar #6b7178 -> #94a3b8: {n} files")


if __name__ == "__main__":
    main()
