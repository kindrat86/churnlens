#!/usr/bin/env python3
"""Shared page shell for the 2026-07-25 acquirer-surface pSEO families.

Why most of the shell is *extracted from a live page* rather than hardcoded:
CLAUDE.md records that the base template in this repo is BARE, and that
regenerating from it silently drops the PostHog snippet, the ux.css/ux.js wiring
and the entity @graph. Reading those blocks out of pages that already carry them
makes drift structurally impossible instead of something to notice in review.

Sources:
  learn/gross-churn/index.html  -> entity @graph, nav, trust bar
  vs/baremetrics/index.html     -> PostHog init snippet

The one block NOT inherited is the inline <style>, because the template's version
hardcodes light-mode colours that break dark mode. See the note above STYLE.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://churnlens.site"

_SHELL_SRC = REPO / "learn" / "gross-churn" / "index.html"
_PH_SRC = REPO / "vs" / "baremetrics" / "index.html"


def _grab(text: str, pattern: str, what: str) -> str:
    m = re.search(pattern, text, re.S)
    if not m:
        raise SystemExit(f"shell extraction failed: {what} not found")
    return m.group(0)


_shell = _SHELL_SRC.read_text()
_ph = _PH_SRC.read_text()

ENTITY_GRAPH = _grab(_shell, r"<!-- entity-graph --><script type=\"application/ld\+json\">.*?</script>", "entity @graph")
NAV = _grab(_shell, r"<nav>.*?</nav>", "nav")
# The template's nav hardcodes the brand link to a near-black hex, which is invisible
# against ux.css's dark-mode surface. Same root cause as the <style> block below.
NAV = NAV.replace("color:#1a1a2e", "color:var(--ux-text,#1a1a2e)")

# NOTE: deliberately NOT extracted from the template page.
#
# The shared inline block on /learn/* hardcodes light-mode colours (p{color:#333},
# .lead{color:#555}, body{color:#1a1a2e}). ux.css ships a full variable-based theme
# with a prefers-color-scheme:dark block, and because ux.css never sets a colour on
# `p`, the hardcoded #333 wins there — so body text renders dark-grey-on-dark-navy
# for every dark-mode visitor. Verified live on churnlens.site/learn/gross-churn,
# so it is pre-existing and sitewide, not introduced here.
#
# Same geometry and type scale as the template, colours routed through ux.css's own
# custom properties with light-mode values as fallbacks.
STYLE = """<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.7;color:var(--ux-text,#1a1a2e);max-width:820px;margin:0 auto;padding:20px}
h1{font-size:2rem;margin:16px 0 8px;line-height:1.3;color:var(--ux-text,#1a1a2e)}
h2{font-size:1.4rem;margin:36px 0 12px;color:var(--ux-text,#1a1a2e)}
h3{font-size:1.08rem;margin:26px 0 8px;color:var(--ux-text,#1a1a2e)}
p{margin-bottom:16px;color:var(--ux-text,#1a1a2e)}
ul,ol{margin:0 0 16px 22px}li{margin-bottom:8px;color:var(--ux-text,#1a1a2e)}
nav{padding:12px 0;border-bottom:2px solid var(--ux-border,#f0f0f0);margin-bottom:20px}
nav a{margin-right:16px;color:var(--ux-accent,#667eea);text-decoration:none;font-weight:500;font-size:.9rem}
a{color:var(--ux-accent,#667eea)}
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--ux-border,#eee);color:var(--ux-text-secondary,#555);font-size:.85rem}
.lead{font-size:1.15rem;color:var(--ux-text-secondary,#555);margin-bottom:24px}
.pseo-scroll{overflow-x:auto;margin:16px 0;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;min-width:520px}
th,td{border:1px solid var(--ux-border,#e0e0e0);padding:10px 14px;text-align:left;font-size:.95rem;vertical-align:top;color:var(--ux-text,#1a1a2e)}
th{background:var(--ux-surface-raised,#f8f9fa);font-weight:600}
details{border:1px solid var(--ux-border,#e0e0e0);border-radius:8px;padding:12px 16px;margin-bottom:8px;background:var(--ux-surface-raised,#fafafa)}
summary{cursor:pointer;font-size:1rem;color:var(--ux-text,#1a1a2e)}
details p{margin-bottom:0}
code{background:var(--ux-surface-raised,#f1f5f9);border:1px solid var(--ux-border,#e2e8f0);padding:1px 5px;border-radius:4px;font-size:.88em}
blockquote{border-left:3px solid var(--ux-accent,#667eea);padding-left:16px;margin:16px 0;color:var(--ux-text-secondary,#444);font-style:italic}
.pseo-note{font-size:.85rem;color:var(--ux-text-secondary,#555);border-left:3px solid var(--ux-border,#eee);padding-left:14px;margin:24px 0}
.pseo-crumb{font-size:.85rem;color:var(--ux-text-secondary,#555);margin-bottom:4px}
</style>"""
TRUST_BAR = _grab(_shell, r"<!-- BRUNSON TRUST BAR.*?<!-- /BRUNSON TRUST BAR -->", "trust bar")
POSTHOG = _grab(_ph, r"<script>\(function\(\)\{if\(window\.posthog.*?</script>", "PostHog init")

FOOTER = ('<footer>&copy; 2026 ChurnLens. All rights reserved. '
          f'<a href="{BASE}/sitemap.xml">Sitemap</a></footer>')


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def jld(obj: dict) -> str:
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def faq_schema(faqs: list[tuple[str, str]]) -> str:
    return jld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    })


def breadcrumb(hub_name: str, hub_url: str, page_name: str, page_url: str) -> str:
    return jld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": hub_name, "item": hub_url},
            {"@type": "ListItem", "position": 3, "name": page_name, "item": page_url},
        ],
    })


def faq_html(faqs: list[tuple[str, str]]) -> str:
    out = ["<h2>Frequently asked questions</h2>"]
    for q, a in faqs:
        out.append(f"<details><summary><strong>{esc(q)}</strong></summary>"
                   f"<p style=\"margin-top:10px\">{a}</p></details>")
    return "\n".join(out)


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Wide prose tables scroll inside their own container rather than making the page
    scroll horizontally on mobile."""
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return ('<div class="pseo-scroll"><table><thead><tr>' + th
            + "</tr></thead><tbody>" + trs + "</tbody></table></div>")


CTA = (
    '<h2>Verify it against the raw rows</h2>'
    f'<p>Every check on this page can be run by hand in a spreadsheet, and if you have the '
    f'time you should. If you would rather not: send us the target\'s subscription export and '
    f'we run the full human-reviewed analysis — logo churn, revenue churn, customer '
    f'concentration, annual-plan decay, zombie MRR and an A&ndash;F revenue-quality grade. '
    f'The free <a href="{BASE}/pricing">Starter tier</a> covers one CSV per month, which is '
    f'enough to check a single deal.</p>'
    f'<p><a href="{BASE}/sample-churn-risk-report"><strong>See a sample report &rarr;</strong></a> '
    f'&nbsp;·&nbsp; <a href="{BASE}/get-the-checklist">Get the free 23-point checklist &rarr;</a></p>'
)


def render(*, url_path: str, title: str, description: str, h1: str, lead: str,
           body: str, faqs: list[tuple[str, str]], hub_name: str, hub_path: str,
           breadcrumb_name: str, extra_jsonld: str = "") -> str:
    """Assemble one page. url_path/hub_path are absolute, no trailing slash."""
    url = BASE + url_path
    hub_url = BASE + hub_path
    webpage = jld({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": breadcrumb_name,
        "url": url,
        "description": description,
        "isPartOf": {"@id": f"{BASE}/#website"},
        "publisher": {"@id": f"{BASE}/#organization"},
        "about": {"@id": f"{BASE}/#software"},
        "inLanguage": "en",
        "datePublished": "2026-07-25",
        "dateModified": "2026-07-25",
        "speakable": {"@type": "SpeakableSpecification",
                      "cssSelector": ["h1", "p:first-of-type"]},
    })
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="robots" content="index,follow">
<meta name="author" content="ChurnLens">
<meta property="article:published_time" content="2026-07-25">
<meta property="article:modified_time" content="2026-07-25">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ChurnLens">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
{webpage}
{breadcrumb(hub_name, hub_url, breadcrumb_name, url)}
{faq_schema(faqs)}{extra_jsonld}
{STYLE}
<!-- canonical-disambiguation -->
<link rel="stylesheet" href="/ux.css">
<script src="/ux.js" defer></script>
{POSTHOG}
{ENTITY_GRAPH}
</head><body>
{NAV}
<p class="pseo-crumb"><a href="{BASE}/">Home</a> &rsaquo; <a href="{hub_url}">{esc(hub_name)}</a></p>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
{body}
{CTA}
{faq_html(faqs)}
{FOOTER}
{TRUST_BAR}
</body></html>
"""


def write(rel_dir: str, content: str) -> None:
    d = REPO / rel_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(content)
