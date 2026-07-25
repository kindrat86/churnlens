#!/usr/bin/env python3
"""Make the light TL;DR callouts readable on this site's dark theme.

The callout hardcodes `background:#f0f7ff` inline while the theme paints text
`#f1f5f9` — about 1.03:1, so the copy is invisible. It reads as a blank white
box, and on /free/due-diligence-simulator it is the first thing anyone
embedding the widget sees.

The background is deliberate design, so this pins an explicit dark text colour
on the element rather than repainting the surface. Per the hardcoded-colour
lesson: never lighten a token used as both text and background, and never
blanket-replace a colour — this touches only callouts already carrying that
exact background.

Idempotent via the cl-callout-contrast-v1 marker.
"""

import pathlib
import re
import sys

MARKER = "<!-- cl-callout-contrast-v1 -->"
LIGHT_BG = "background:#f0f7ff"
TEXT = "#0f172a"      # same near-black the light surfaces elsewhere use
LINK = "#0b4ea2"      # 4.5:1+ on #f0f7ff, and still recognisably the brand blue

RULE = (
    '%s\n<style>\n'
    '/* Light TL;DR callouts inherit the dark theme\'s near-white text, which is\n'
    '   invisible on their own near-white background. Pin readable colours. */\n'
    '.callout[style*="#f0f7ff"] { color: %s; }\n'
    '.callout[style*="#f0f7ff"] strong { color: %s; }\n'
    '.callout[style*="#f0f7ff"] a { color: %s; }\n'
    '</style>\n'
) % (MARKER, TEXT, TEXT, LINK)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".vercel", "i18n", "i18n_out", "dist", "node_modules"}


def main() -> int:
    targets = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            html = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if re.search(r'class="callout"[^>]*' + re.escape(LIGHT_BG), html):
            targets.append((path, html))

    if not targets:
        print("no light callouts found")
        return 0

    changed = 0
    for path, html in targets:
        if MARKER in html:
            print("%-52s skip (already fixed)" % path.relative_to(ROOT))
            continue
        if "</head>" not in html:
            print("%-52s SKIP (no </head>)" % path.relative_to(ROOT))
            continue
        path.write_text(html.replace("</head>", RULE + "</head>", 1), encoding="utf-8")
        print("%-52s fixed" % path.relative_to(ROOT))
        changed += 1

    print("\n%d of %d file(s) updated" % (changed, len(targets)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
