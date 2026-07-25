#!/usr/bin/env python3
"""Recolour the Brunson trust bar to the dark palette it now sits on.

The block was injected with a light palette (#f0f9ff->#e8f5e9 gradient, a white
card, a #fef3c7 amber strip) and dark text. Later sitewide contrast work flipped
its text to light — but left the backgrounds light. Measured live on /who:

  h2      "See Hidden Churn Before You Buy a SaaS"   rgb(226,232,240) on rgb(240,249,255)  1.16:1
  strong  "100% Money-Back ..."                      rgb(241,245,249) on rgb(254,243,199)  1.02:1
  p       "Free SaaS Due Diligence Checklist"        rgb(241,245,249) on rgb(255,255,255)  1.10:1
  p       "No spam. Unsubscribe anytime."            rgb(136,136,136) on rgb(255,255,255)  3.54:1

i.e. the entire lead-magnet CTA is invisible on every page carrying it. Removing
the block was the other option on the table; recolouring keeps the CTA, which an
invisible block was not delivering anyway.

Edits are confined to the <section> between the `Brunson Trust Bar` comment and
its closing tag, so no other block on the page can be affected. Idempotent: a
section already carrying the dark gradient is left alone.
"""
import os, re, sys

START = re.compile(r'<!-- Brunson Trust Bar[^>]*-->')
DARK_GRADIENT = 'linear-gradient(135deg,#111c33,#122a25)'

SUBS = [
    # the slab itself -> dark, keeping the blue->green hue hint of the original
    ('background:linear-gradient(135deg,#f0f9ff,#e8f5e9)', f'background:{DARK_GRADIENT}'),
    # amber guarantee strip -> translucent amber on dark, so light text reads
    ('background:#fef3c7;border-radius:8px', 'background:rgba(251,191,36,0.16);border-radius:8px'),
    # the white lead-capture card -> dark card with a hairline instead of a shadow
    ('background:white;border-radius:12px;padding:20px;max-width:500px;margin:0 auto 16px;'
     'box-shadow:0 2px 8px rgba(0,0,0,0.08)',
     'background:rgba(15,23,42,0.55);border:1px solid #26364d;border-radius:12px;'
     'padding:20px;max-width:500px;margin:0 auto 16px'),
    # muted greys that were chosen for a white card
    ('color:#555', 'color:#94a3b8'),
    ('color:#888', 'color:#94a3b8'),
    # dark heading left over on pages the later pass did not touch
    ('color:#1a1a1a', 'color:#e2e8f0'),
]


def fix_section(sec):
    if DARK_GRADIENT in sec:
        return sec, 0
    n = 0
    for old, new in SUBS:
        c = sec.count(old)
        if c:
            sec = sec.replace(old, new)
            n += c
    return sec, n


def process(html):
    m = START.search(html)
    if not m:
        return html, 'no-trustbar'
    # ONLY touch pages whose own palette is dark. On a light page the trust bar's
    # text is dark (inherited or #1a1a1a) and its light background is already
    # correct — darkening it there inverts the bug into dark-on-dark. Measured:
    # doing it unconditionally broke 30 of 48 pages at 1.05:1. This is the
    # self-light "leave alone" branch.
    theme = re.search(r'data-cl-theme="([a-z]+)"', html)
    if not theme:
        return html, 'skip:no-theme-attr'
    if theme.group(1) != 'dark':
        # Light page: the block's palette is already right, but its small print
        # ("No spam. Unsubscribe anytime.") is #888 on the white card = 3.54:1,
        # under the 4.5 floor. Pre-existing, and the only failure left on these
        # 30 pages. #4b5563 measures 6.35:1 on white. Scoped to the section so
        # the identical #888 elsewhere on the page is untouched.
        end = html.find('</section>', m.end())
        if end < 0:
            return html, 'unterminated'
        end += len('</section>')
        sec = html[m.start():end]
        if 'color:#888' not in sec:
            return html, 'skip:light-page'
        sec = sec.replace('color:#888', 'color:#4b5563')
        return html[:m.start()] + sec + html[end:], 'light-smallprint'
    end = html.find('</section>', m.end())
    if end < 0:
        return html, 'unterminated'
    end += len('</section>')
    sec, n = fix_section(html[m.start():end])
    if not n:
        return html, 'already-dark'
    return html[:m.start()] + sec + html[end:], f'fixed:{n}'


def main(root):
    SKIP = {'.git', 'node_modules', 'dist', 'i18n', 'i18n_out', 'assets', '.vercel', '__pycache__', 'public'}
    stats, changed = {}, 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP]
        for f in sorted(fn):
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            try:
                src = open(p, encoding='utf-8').read()
            except (OSError, UnicodeDecodeError):
                continue
            out, what = process(src)
            key = what.split(':')[0]
            stats[key] = stats.get(key, 0) + 1
            if out != src:
                open(p, 'w', encoding='utf-8').write(out)
                changed += 1
    print(f'files rewritten: {changed}')
    for k in sorted(stats):
        print(f'  {k}: {stats[k]}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
