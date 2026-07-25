#!/usr/bin/env python3
"""Repair hardcoded text colours in per-page <style> blocks so they survive both
colour schemes.

The defect: ~50 served pages carry an inline <style> that hardcodes a light-mode
text colour (p{color:#333}, .lead{color:#555}, footer{color:#6b7280} ...). ux.css
ships a variable-based theme with a prefers-color-scheme:dark block but never sets
a colour on p/.lead/footer, so the hardcoded value wins and body text renders
dark-grey-on-dark-navy for every dark-mode visitor. Measured: p #333 on #0f172a is
1.41:1 against a WCAG AA floor of 4.5:1.

Two different fixes, chosen per page by where the background comes from:

  * theme-following page (no background of its own, so ux.css supplies it)
    -> route the colour through ux.css's own token, keeping the original as the
       fallback: color: var(--ux-text, #333). Now correct in both schemes.

  * self-dark page (declares its own dark background, e.g. background:var(--cl-navy))
    -> a token would resolve to a DARK grey in light mode and break it further.
       Substitute a fixed light grey that clears AA on that page's own background.

Only the exact selector rules the audit flagged are touched, only inside the page's
own <style> blocks, and only when the declaration is still a literal colour — so
the script is idempotent and safe to re-run.

Usage:
  python3 scripts/theme_contrast_audit.py --json /tmp/before.json
  python3 scripts/fix_theme_colors.py /tmp/before.json [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "scripts")
from theme_contrast_audit import (  # noqa: E402
    TOKENS, contrast, decls_for, hex2rgb, local_props, resolve, strip_dark_mq,
)

# Which ux.css token each selector should follow.
TOKEN_FOR = {
    "body": "--ux-text",
    "p": "--ux-text",
    ".lead": "--ux-text-secondary",
    "footer": "--ux-text-secondary",
}
# Fallback for self-dark pages: light greys that clear AA on a dark surface.
SELF_DARK_SUB = {
    "body": "#f1f5f9",
    "p": "#e2e8f0",
    ".lead": "#cbd5e1",
    "footer": "#94a3b8",
}


def page_has_own_bg(css: str, local: dict) -> tuple[bool, tuple | None]:
    own_bg = decls_for(css, "body", "background-color") or decls_for(css, "body", "background")
    if not own_bg:
        return False, None
    for tok in re.findall(r"var\([^)]*\)|#[0-9a-fA-F]{3,6}|rgba?\([^)]*\)|\b[a-z]+\b", own_bg):
        rgb = resolve(tok, "light", local)
        if rgb:
            return True, rgb
    return False, None


def replace_in_rule(css: str, selector: str, old: str, new: str) -> tuple[str, int]:
    """Replace `color: old` with `color: new` only inside rules whose selector list
    contains `selector` as a whole token."""
    n = 0
    out, last = [], 0
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = [s.strip() for s in m.group(1).split(",")]
        if selector not in sels:
            continue
        body = m.group(2)
        new_body, cnt = re.subn(
            rf"(^|;)(\s*)color\s*:\s*{re.escape(old)}\s*(?=;|$)",
            rf"\1\2color:{new}", body)
        if not cnt:
            continue
        out.append(css[last:m.start(2)])
        out.append(new_body)
        last = m.end(2)
        n += cnt
    out.append(css[last:])
    return "".join(out), n


def main() -> None:
    findings = json.load(open(sys.argv[1]))
    dry = "--dry-run" in sys.argv
    total_files = total_decls = 0
    mode_count = {"theme-following": 0, "self-dark": 0}
    skipped = []

    for rel, rows in sorted(findings.items()):
        t = open(rel, encoding="utf-8", errors="replace").read()
        blocks = [(m.start(1), m.end(1), m.group(1))
                  for m in re.finditer(r"<style[^>]*>(.*?)</style>", t, re.S)]
        if not blocks:
            skipped.append((rel, "no <style>"))
            continue
        css_all = "\n".join(strip_dark_mq(b[2]) for b in blocks)
        local = local_props(css_all)
        self_dark, bg = page_has_own_bg(css_all, local)
        # only "self-dark" if that background is genuinely dark
        if self_dark and bg is not None:
            white = hex2rgb("#ffffff")
            self_dark = contrast(bg, white) > 2.0

        changed = 0
        new_t = t
        # work back-to-front so earlier offsets stay valid
        for s, e, block in reversed(blocks):
            block_new = block
            for sel, col in {(r["selector"], r["color"]) for r in rows}:
                if sel not in TOKEN_FOR or not col.startswith("#"):
                    continue
                if self_dark:
                    repl = SELF_DARK_SUB[sel]
                else:
                    repl = f"var({TOKEN_FOR[sel]},{col})"
                block_new, n = replace_in_rule(block_new, sel, col, repl)
                changed += n
            if block_new != block:
                new_t = new_t[:s] + block_new + new_t[e:]

        if not changed:
            skipped.append((rel, "nothing matched (already fixed?)"))
            continue
        mode_count["self-dark" if self_dark else "theme-following"] += 1
        total_files += 1
        total_decls += changed
        if not dry:
            open(rel, "w", encoding="utf-8").write(new_t)

    print(f"{'would fix' if dry else 'fixed'}: {total_files} files, {total_decls} declarations")
    for k, v in mode_count.items():
        print(f"  {k:16s} {v} files")
    if skipped:
        print(f"skipped: {len(skipped)}")
        for rel, why in skipped[:8]:
            print(f"  {rel} — {why}")


if __name__ == "__main__":
    main()
