#!/usr/bin/env python3
"""Inject embed mode into the free calculator pages.

Loading a tool with ?embed=1 (or framing it cross-origin) strips the page down
to the calculator itself and pins a compact attribution bar to the bottom. That
bar is the point: every site that embeds a widget publishes a link back.

Idempotent via the <!-- cl-embed-v1 --> marker — safe to re-run, and it injects
into existing HTML rather than regenerating it (see CLAUDE.md).
"""

import pathlib
import re
import sys

MARKER = "<!-- cl-embed-v4 -->"
# v1 forced a white background onto pages that are natively dark (#0f172a) with
# near-white headings, rendering the H1 at ~1.06:1 contrast. v2 keeps the page's
# own theme and hides the trailing prose that has no place in a widget. v3 stops
# assuming every tool wraps its calculator in .tool-card.
LEGACY_MARKERS = ("<!-- cl-embed-v1 -->", "<!-- cl-embed-v2 -->", "<!-- cl-embed-v3 -->")
ROOT = pathlib.Path(__file__).resolve().parent.parent
FREE = ROOT / "free"

# embed-widget is the gallery of snippets, not a widget itself.
SKIP = {"embed-widget"}

# Embeddability is DETECTED, not listed. Several pages under /free are named
# "calculator" but contain no form control at all — ltv-calculator and
# mrr-health-check are prose. Publishing those as widgets would put a wall of
# text on a third party's site labelled "Customer LTV Calculator", which is the
# worst place for this brand to be caught overclaiming. The fleet adds and
# rewrites tools constantly, so a hardcoded allowlist would rot; this re-derives
# the answer on every run.
FORM_CONTROL = re.compile(r"<(input|textarea|select)\b", re.I)


def is_interactive(html: str) -> bool:
    return bool(FORM_CONTROL.search(html))

BLOCK = """%s
<style>
/* Embed mode: the page is rendered inside somebody else's site, so drop the
   cross-sell, the methodology essay and the link farm — keep the tool. */
/* Keep the page's own palette — these pages are dark by design. */
html[data-embed] body { padding: 1rem 1rem 4.5rem; }
html[data-embed] .cta,
html[data-embed] .related,
html[data-embed] .related-links,
html[data-embed] .breadcrumbs,
html[data-embed] footer,
html[data-embed] [data-embed-hide] { display: none !important; }
html[data-embed] h1 { font-size: 1.3rem; margin-bottom: .35rem; }
html[data-embed] p.subtitle { font-size: .9rem; margin-bottom: 1.1rem; }
html[data-embed] .tool-card { box-shadow: none; margin-bottom: 0; }
.cl-embed-bar {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 2147483000;
  display: flex; align-items: center; justify-content: center; gap: .4rem;
  padding: .55rem .75rem; font: 500 .78rem/1.3 -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0f172a; color: #cbd5e1; text-align: center;
}
.cl-embed-bar a { color: #a5b4fc; text-decoration: none; font-weight: 700; }
.cl-embed-bar a:hover { text-decoration: underline; }
.cl-embed-bar span { opacity: .8; }
@media (max-width: 420px) { .cl-embed-bar { font-size: .72rem; } }
</style>
<script>
(function () {
  try {
    var framed = window.self !== window.top;
    var asked = /[?&]embed=1(&|$)/.test(window.location.search);
    if (!asked && !framed) return;
    document.documentElement.setAttribute('data-embed', '1');

    document.addEventListener('DOMContentLoaded', function () {
      if (document.querySelector('.cl-embed-bar')) return;

      /* Everything after the calculator is page furniture — methodology essays,
         cross-sell, link blocks. None of it belongs in somebody else's iframe,
         and most of it carries no class to target from CSS. */
      var cards = document.querySelectorAll('.tool-card');
      /* Not every tool uses .tool-card — the due-diligence simulator uses .card,
         and a page with neither would otherwise keep its whole prose tail. */
      if (!cards.length) cards = document.querySelectorAll('.card');
      if (!cards.length) {
        var form = document.querySelector('input, textarea, select');
        if (form) cards = [form];
      }
      if (cards.length) {
        var last = cards[cards.length - 1];
        while (last && last.parentNode !== document.body) last = last.parentNode;
        if (last) {
          var node = last.nextElementSibling;
          while (node) {
            node.style.display = 'none';
            node = node.nextElementSibling;
          }
        }
      }

      var slug = (window.location.pathname.split('/').filter(Boolean).pop() || 'widget');
      var href = 'https://churnlens.site/free?utm_source=embed&utm_medium=widget&utm_campaign=' +
        encodeURIComponent(slug);
      var bar = document.createElement('div');
      bar.className = 'cl-embed-bar';
      var link = document.createElement('a');
      link.href = href;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = 'ChurnLens';
      var lead = document.createElement('span');
      lead.textContent = 'Free SaaS metrics calculator by ';
      var tail = document.createElement('span');
      tail.textContent = ' — buyer-side due diligence';
      bar.appendChild(lead);
      bar.appendChild(link);
      bar.appendChild(tail);
      document.body.appendChild(bar);

      /* Tell the host page how tall we are so it can size the iframe.
         At DOMContentLoaded inside a fresh iframe the document has often not
         been laid out yet and every height reads 0. Posting that is worse than
         posting nothing: a host that trusts it collapses the widget to
         invisible. So never emit a non-positive height, and re-post once
         layout has actually happened. */
      var lastPosted = 0;
      function postHeight() {
        try {
          var h = Math.max(
            document.body.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.scrollHeight
          );
          if (!(h > 0) || h === lastPosted) return;
          lastPosted = h;
          window.parent.postMessage({ type: 'churnlens:height', height: h }, '*');
        } catch (e) { /* cross-origin parent: nothing to do */ }
      }
      postHeight();
      window.addEventListener('load', postHeight);
      window.addEventListener('resize', postHeight);
      setTimeout(postHeight, 300);
      setTimeout(postHeight, 1200);
      if (window.ResizeObserver) new ResizeObserver(postHeight).observe(document.body);
    });
  } catch (e) { /* never break the calculator */ }
})();
</script>
""" % MARKER


GUARD_MARKER = "<!-- cl-embed-guard-v1 -->"

# Must run BEFORE the site's PostHog snippet, which sits partway down <head>.
# Embedding a third-party tracker into somebody else's page — while the embed
# gallery promises "no tracking, no cookies, no third-party scripts" — is a
# claim we should make true rather than reword. The site's own snippet opens
# with `if (window.posthog && window.posthog.__loaded) return;`, so presenting
# an already-loaded stub makes it bail out on its own terms.
GUARD_BLOCK = """%s
<script>
(function () {
  try {
    if (window.self === window.top && !/[?&]embed=1(&|$)/.test(window.location.search)) return;
    var noop = function () {};
    window.posthog = {
      __loaded: true, __cl_embed_stub: true,
      init: noop, capture: noop, identify: noop, register: noop, reset: noop,
      opt_out_capturing: noop, opt_in_capturing: noop,
      onFeatureFlags: noop, isFeatureEnabled: function () { return false; }
    };
  } catch (e) { /* never break the calculator */ }
})();
</script>
""" % GUARD_MARKER

OEMBED_MARKER = "<!-- cl-oembed-v1 -->"

OEMBED_LINK = (
    '%s\n'
    '<link rel="alternate" type="application/json+oembed"\n'
    '      href="https://churnlens.site/api/oembed?url=https%%3A%%2F%%2Fchurnlens.site%%2Ffree%%2F{slug}&format=json"\n'
    '      title="{title} by ChurnLens">\n'
) % OEMBED_MARKER


def title_of(html: str, slug: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    if not match:
        return slug.replace("-", " ").title()
    # Strip the " | ChurnLens" suffix; the link's own title adds attribution.
    return re.sub(r"\s*[|—-]\s*ChurnLens\s*$", "", match.group(1).strip())


def strip_block(html: str, marker: str) -> tuple:
    pattern = re.compile(re.escape(marker) + r".*?</script>\s*", re.S)
    return pattern.subn("", html, count=1)


def strip_oembed(html: str) -> tuple:
    pattern = re.compile(
        re.escape(OEMBED_MARKER) + r'\s*<link rel="alternate" type="application/json\+oembed".*?>\s*',
        re.S,
    )
    return pattern.subn("", html, count=1)


def inject(path: pathlib.Path, slug: str) -> str:
    html = path.read_text(encoding="utf-8")
    if "</head>" not in html:
        return "SKIP (no </head>)"

    added = []

    # Strip any superseded block first, so an upgrade replaces rather than stacks.
    for legacy in LEGACY_MARKERS:
        if legacy in html:
            html, n = strip_block(html, legacy)
            if n:
                added.append("removed " + legacy.strip("<!- >"))

    # A page with no form control is not a widget. If one was injected before
    # (or the page lost its interactivity), take the embed surface back off it
    # rather than advertising prose as a calculator.
    if not is_interactive(html):
        removed = []
        html, n = strip_block(html, MARKER)
        if n:
            removed.append("embed-mode")
        html, n = strip_block(html, GUARD_MARKER)
        if n:
            removed.append("tracker-guard")
        html, n = strip_oembed(html)
        if n:
            removed.append("oembed-link")
        if removed or added:
            path.write_text(html, encoding="utf-8")
            return "NOT INTERACTIVE — withdrew " + ", ".join(removed or ["nothing"])
        return "skip (not interactive, nothing to withdraw)"

    if GUARD_MARKER not in html:
        # Top of <head>, ahead of the PostHog snippet it needs to pre-empt.
        html, n = re.subn(r"(<head[^>]*>)", lambda m: m.group(1) + "\n" + GUARD_BLOCK, html, count=1)
        if n:
            added.append("tracker-guard")

    if MARKER not in html:
        html = html.replace("</head>", BLOCK + "</head>", 1)
        added.append("embed-mode")

    if OEMBED_MARKER not in html:
        link = OEMBED_LINK.format(
            slug=slug,
            title=title_of(html, slug).replace('"', "&quot;"),
        )
        html = html.replace("</head>", link + "</head>", 1)
        added.append("oembed-link")

    if not added:
        return "skip (already injected)"

    path.write_text(html, encoding="utf-8")
    return "injected: " + ", ".join(added)


def main() -> int:
    if not FREE.is_dir():
        print("no free/ directory", file=sys.stderr)
        return 1

    changed = 0
    for tool_dir in sorted(FREE.iterdir()):
        if not tool_dir.is_dir() or tool_dir.name in SKIP:
            continue
        for candidate in (tool_dir / "index.html", FREE / (tool_dir.name + ".html")):
            if candidate.is_file():
                status = inject(candidate, tool_dir.name)
                print("%-48s %s" % (candidate.relative_to(ROOT), status))
                if status.startswith("injected"):
                    changed += 1
    print("\n%d file(s) injected" % changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
