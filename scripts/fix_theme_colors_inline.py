#!/usr/bin/env python3
"""Second pass: repair hardcoded dark text in inline `style="..."` attributes.

`fix_theme_colors.py` only rewrites <style> blocks. Inline style attributes beat
every stylesheet, so an injected `<p style="...;color:#333">` or the nav brand link
`<a style="font-weight:700;color:#1a1a2e">` stays dark-on-dark-navy in dark mode no
matter what ux.css or the page's own <style> says. The nav brand link was visibly
invisible on /learn/* in a dark-mode screenshot.

Same three-way branch as the <style> pass, because the right fix depends on where
the page's background comes from:

  theme-following (background from ux.css)  -> color: var(--ux-text, #333)
  self-dark       (own dark background)     -> substitute a light grey
  self-light      (own LIGHT background)    -> LEAVE ALONE. Hardcoded dark text is
                                               already correct on a hardcoded light
                                               background, and a token would flip it
                                               light in dark mode and break it.

Never touched:
  * attributes that also set a `background` — those are self-consistent
    (verified: `background:#fff;color:#111827` chips, and `-webkit-text-fill-color`).
  * `border-color` / `-color` properties that merely contain a hex.
  * inline LIGHT text (`color:#fff` and friends). Measured with proper alpha
    compositing up the ancestor chain, these sit on hardcoded blue buttons (5.17:1)
    and dark cards (17.85:1) and already pass AA in both schemes.

Usage: python3 scripts/fix_theme_colors_inline.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, "scripts")
from theme_contrast_audit import (  # noqa: E402
    SKIP, SKIP_FILES, contrast, hex2rgb, local_props, strip_dark_mq,
)
from fix_theme_colors import page_has_own_bg  # noqa: E402

# Dark text values that go invisible on a dark surface.
DARK_TEXT = {"#333", "#1a1a2e", "#0a0a0a", "#222222", "#1a1a1a", "#111", "#000"}
SELF_DARK_SUB = "#e2e8f0"


def classify(rel: str, t: str) -> str:
    css_all = "\n".join(strip_dark_mq(m.group(1))
                        for m in re.finditer(r"<style[^>]*>(.*?)</style>", t, re.S))
    if not css_all:
        return "theme-following"
    local = local_props(css_all)
    has_bg, bg = page_has_own_bg(css_all, local)
    if not has_bg or bg is None:
        return "theme-following"
    return "self-dark" if contrast(bg, hex2rgb("#ffffff")) > 2.0 else "self-light"


def fix_attr(attr: str, kind: str) -> tuple[str, int]:
    """Rewrite `color:<dark>` inside one style attribute value."""
    if re.search(r"(?:^|;)\s*background", attr):
        return attr, 0
    n = 0

    def sub(m):
        nonlocal n
        val = m.group(2).strip().lower()
        if val not in DARK_TEXT:
            return m.group(0)
        n += 1
        repl = SELF_DARK_SUB if kind == "self-dark" else f"var(--ux-text,{m.group(2).strip()})"
        return f"{m.group(1)}color:{repl}"

    # (?<![-\w]) keeps this off `border-color`, `-webkit-text-fill-color`, etc.
    out = re.sub(r"(^|;)\s*(?<![-\w])color\s*:\s*(#[0-9a-fA-F]{3,6})\s*(?=;|$)", sub, attr)
    return out, n


def main() -> None:
    dry = "--dry-run" in sys.argv
    files = totals = 0
    by_kind = {"theme-following": 0, "self-dark": 0, "self-light-skipped": 0}

    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in sorted(fn):
            if not f.endswith(".html") or f in SKIP_FILES:
                continue
            rel = os.path.relpath(os.path.join(dp, f), ".")
            if any(p in SKIP for p in rel.split(os.sep)):
                continue
            t = open(rel, encoding="utf-8", errors="replace").read()
            if not re.search(r'style="[^"]*color:\s*#', t):
                continue
            kind = classify(rel, t)

            changed = 0

            def repl_attr(m):
                nonlocal changed
                if kind == "self-light":
                    return m.group(0)
                new, n = fix_attr(m.group(1), kind)
                changed += n
                return f'style="{new}"' if n else m.group(0)

            new_t = re.sub(r'style="([^"]*)"', repl_attr, t)
            if kind == "self-light" and re.search(
                    r'style="[^"]*(?<![-\w])color:\s*(#333|#1a1a2e|#0a0a0a)\b', t):
                by_kind["self-light-skipped"] += 1
            if not changed:
                continue
            files += 1
            totals += changed
            by_kind[kind] += 1
            if not dry:
                open(rel, "w", encoding="utf-8").write(new_t)

    print(f"{'would fix' if dry else 'fixed'}: {files} files, {totals} inline declarations")
    for k, v in by_kind.items():
        print(f"  {k:22s} {v} files")


if __name__ == "__main__":
    main()
