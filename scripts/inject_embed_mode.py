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

MARKER = "<!-- cl-embed-v1 -->"
ROOT = pathlib.Path(__file__).resolve().parent.parent
FREE = ROOT / "free"

# embed-widget is the gallery of snippets, not a widget itself.
SKIP = {"embed-widget"}

BLOCK = """%s
<style>
/* Embed mode: the page is rendered inside somebody else's site, so drop the
   cross-sell, the methodology essay and the link farm — keep the tool. */
html[data-embed] body { padding: 1rem 1rem 4.5rem; background: #fff; }
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

      /* Tell the host page how tall we are so it can size the iframe. */
      function postHeight() {
        try {
          var h = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
          );
          window.parent.postMessage({ type: 'churnlens:height', height: h }, '*');
        } catch (e) { /* cross-origin parent: nothing to do */ }
      }
      postHeight();
      window.addEventListener('resize', postHeight);
      if (window.ResizeObserver) new ResizeObserver(postHeight).observe(document.body);
    });
  } catch (e) { /* never break the calculator */ }
})();
</script>
""" % MARKER


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


def inject(path: pathlib.Path, slug: str) -> str:
    html = path.read_text(encoding="utf-8")
    if "</head>" not in html:
        return "SKIP (no </head>)"

    added = []
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
