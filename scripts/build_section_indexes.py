#!/usr/bin/env python3
"""
Generate missing section index pages for /benchmarks, /calculators, /checklists,
/redflags, /faq, /industries, /templates.

Each generated page is an entity-rich topical hub — not a bare file list. It:
- Declares the category and ChurnLens's buyer-side-DD wedge in the first paragraph
- Lists the pages in the section with descriptive titles (entity-rich)
- Carries clean Organization + ItemList JSON-LD
- Uses the canonical ChurnLens brand and disambiguatingDescription

Run from ~/churnlens. Safe to re-run (skips directories with an existing index.html
unless --force is passed).
"""
import json
import os
import re
import sys
import html as html_lib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://churnlens.site"

SECTIONS = {
    "benchmarks": {
        "title": "SaaS Benchmarks for Acquirers (2025–26) — Curated Buyer-Side Reference",
        "h1": "SaaS Benchmarks for Acquirers",
        "lede": "Curated SaaS benchmark reference points for buyer-side due diligence — churn, NRR, CAC payback, expansion revenue, logo retention, and revenue concentration. Drawn from public SaaS benchmarking research (SaaS Capital, Recurly, Benchmarkit, High Alpha, First Page Sage) and organized for acquisition analysis. These are reference points, not original ChurnLens data; verify against the primary source before relying on a number in a deal.",
        "what": "benchmarks",
    },
    "calculators": {
        "title": "SaaS Due-Diligence Calculators — Churn, NRR, Concentration, Zombie MRR",
        "h1": "SaaS Due-Diligence Calculators",
        "lede": "Free buyer-side calculators that turn a target's subscription CSV into the numbers that matter in a SaaS acquisition — churn cost, net revenue retention, revenue concentration, and zombie (inactive paid account) MRR. Built for acquirers, PE/M&A analysts, and founders evaluating a purchase.",
        "what": "calculators",
    },
    "checklists": {
        "title": "SaaS Acquisition Due-Diligence Checklists — Pre-LOI to Close",
        "h1": "SaaS Acquisition Due-Diligence Checklists",
        "lede": "Buyer-side checklists for SaaS due diligence — pre-LOI, churn audit, revenue quality, and the full SaaS DD workflow. Each checklist is built around the five-risk buyer-side method ChurnLens uses to surface hidden churn before an acquisition.",
        "what": "checklists",
    },
    "redflags": {
        "title": "SaaS Acquisition Red Flags — Hidden Churn & Revenue Quality Signals",
        "h1": "SaaS Acquisition Red Flags",
        "lede": "The red flags that surface hidden churn, revenue concentration, and quality-of-earnings risk in a SaaS target — before you buy. Organized by the five-risk buyer-side method ChurnLens applies to subscription CSV data.",
        "what": "red flags",
    },
    "faq": {
        "title": "SaaS Churn & Acquisition Due Diligence — Frequently Asked Questions",
        "h1": "SaaS Churn & Due Diligence FAQ",
        "lede": "Answers to the questions SaaS acquirers, PE/M&A analysts, and founders ask about hidden churn, revenue quality, logo vs revenue retention, and how buyer-side due diligence differs from operating-side churn analysis.",
        "what": "frequently asked questions",
    },
    "industries": {
        "title": "SaaS Churn & Revenue Risk by Industry — Buyer-Side Due Diligence",
        "h1": "SaaS Due Diligence by Industry",
        "lede": "Buyer-side due-diligence lenses for SaaS targets in specific verticals — devtools, martech, fintech, vertical SaaS, and more. Each industry has its own churn signatures, concentration patterns, and revenue-quality pitfalls; these pages organize the signals an acquirer should check.",
        "what": "industry lenses",
    },
    "templates": {
        "title": "Free SaaS Due-Diligence Templates — Checklists, Scorecards, Worksheets",
        "h1": "SaaS Due-Diligence Templates",
        "lede": "Free templates for SaaS acquisition due diligence — customer health score, NRR improvement, renewal forecast, revenue quality scorecard, and the pre-LOI SaaS DD checklist. Built for acquirers evaluating a SaaS target before purchase.",
        "what": "templates",
    },
}


def humanize_slug(slug: str) -> str:
    s = slug.replace("-", " ").replace("_", " ")
    s = re.sub(r"\.html$", "", s)
    # Title-case but keep common short words lowercase
    small = {"a", "an", "the", "and", "or", "for", "to", "of", "in", "vs", "by"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        if i > 0 and w.lower() in small:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def scan_section(dirpath: Path) -> list:
    """Return list of (slug, title) tuples for the section's pages."""
    items = []
    for entry in sorted(dirpath.iterdir()):
        if entry.name == "index.html":
            continue
        if entry.is_file() and entry.suffix == ".html":
            slug = entry.stem
            # Try to read <title>
            try:
                txt = entry.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"<title>([^<]+)</title>", txt, re.IGNORECASE)
                title = m.group(1).strip() if m else humanize_slug(slug)
                # Strip common suffixes
                title = re.sub(r"\s*\[\d{4}.*?\]\s*$", "", title)
                title = re.sub(r"\s*\|\s*ChurnLens\s*$", "", title, flags=re.IGNORECASE)
            except Exception:
                title = humanize_slug(slug)
            items.append((slug, title))
        elif entry.is_dir() and (entry / "index.html").exists():
            slug = entry.name
            try:
                txt = (entry / "index.html").read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"<title>([^<]+)</title>", txt, re.IGNORECASE)
                title = m.group(1).strip() if m else humanize_slug(slug)
                title = re.sub(r"\s*\[\d{4}.*?\]\s*$", "", title)
                title = re.sub(r"\s*\|\s*ChurnLens\s*$", "", title, flags=re.IGNORECASE)
            except Exception:
                title = humanize_slug(slug)
            items.append((slug, title))
    return items


def build_page(section: str, meta: dict, items: list, force: bool = False) -> bool:
    dirpath = ROOT / section
    out = dirpath / "index.html"
    if out.exists() and not force:
        return False

    canonical = f"{origin}/{section}" if False else f"{ORIGIN}/{section}"
    item_list = [{"@type": "ListItem", "position": i + 1, "name": html_lib.unescape(t),
                  "url": f"{ORIGIN}/{section}/{s}"} for i, (s, t) in enumerate(items)]
    org_ref = {"@id": f"{ORIGIN}/#organization"}
    json_ld_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage",
             "@id": canonical,
             "name": meta["h1"],
             "description": meta["lede"][:300],
             "url": canonical,
             "isPartOf": {"@id": f"{ORIGIN}/#website"},
             "about": org_ref,
             "mainEntity": {"@type": "ItemList", "numberOfItems": len(items),
                            "itemListElement": item_list}},
            {"@type": "BreadcrumbList",
             "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{ORIGIN}/"},
                 {"@type": "ListItem", "position": 2, "name": meta["h1"], "item": canonical},
             ]},
        ],
    }

    links_html = "\n".join(
        f'    <li><a href="/{section}/{s}">{html_lib.escape(t)}</a></li>'
        for s, t in items
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(meta["title"])}</title>
<meta name="description" content="{html_lib.escape(meta["lede"][:155])}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" href="/favicon.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{html_lib.escape(meta["title"])}">
<meta property="og:description" content="{html_lib.escape(meta["lede"][:155])}">
<meta property="og:image" content="{ORIGIN}/og.png">
<meta property="og:site_name" content="ChurnLens">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_lib.escape(meta["title"])}">
<meta name="twitter:description" content="{html_lib.escape(meta["lede"][:155])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<script type="application/ld+json">{json.dumps(json_ld_graph, ensure_ascii=False)}</script>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;color:#0a0a0a;max-width:760px;margin:0 auto;padding:2rem 1.25rem}}
h1{{font-size:2.1rem;line-height:1.2;margin:.3em 0}}
h2{{font-size:1.45rem;margin-top:2rem;border-bottom:2px solid #e5e7eb;padding-bottom:.3rem}}
a{{color:#0066cc;text-decoration:none}}a:hover{{text-decoration:underline}}
.lede{{font-size:1.1rem;color:#374151;margin-bottom:1.5rem}}
ul.section-list{{list-style:none;padding-left:0}}
ul.section-list li{{padding:.5rem 0;border-bottom:1px solid #f3f4f6}}
ul.section-list a{{font-weight:500;display:block}}
.disambig{{background:#f0f7ff;border-left:4px solid #0066cc;padding:.75rem 1rem;margin:1.5rem 0;border-radius:0 .375rem .375rem 0;font-size:.9rem;color:#1e40af}}
.cta{{background:linear-gradient(135deg,#0066cc,#004499);color:#fff;padding:2rem;border-radius:.75rem;margin-top:2rem;text-align:center}}
.cta h2{{color:#fff;border:none}}.cta .btn{{display:inline-block;background:#fff;color:#0066cc;padding:.75rem 1.5rem;border-radius:.375rem;font-weight:600;margin-top:.5rem}}
footer{{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #e5e7eb;color:#6b7280;font-size:.9rem}}
</style>
</head>
<body>
<nav style="margin-bottom:1.5rem;font-size:.9rem;color:#6b7280"><a href="/" style="color:#0066cc;text-decoration:none">ChurnLens</a> &rsaquo; <span>{html_lib.escape(meta["h1"])}</span></nav>
<h1>{html_lib.escape(meta["h1"])}</h1>
<p class="lede">{html_lib.escape(meta["lede"])}</p>
<div class="disambig"><strong>About ChurnLens:</strong> ChurnLens (churnlens.site) is a buyer-side SaaS due-diligence tool for acquirers, PE/M&amp;A analysts, and founders selling &mdash; it scores a target&rsquo;s revenue quality and surfaces hidden churn before an acquisition. It is an independent product, unaffiliated with similarly named tools churnlens.io (retention automation) or churnlens.tech (churn prediction).</div>
<h2>{len(items)} {html_lib.escape(meta["what"])} in this section</h2>
<ul class="section-list">
{links_html}
</ul>
<section class="cta">
<h2>Run a target&rsquo;s CSV through ChurnLens</h2>
<p>See hidden churn, concentration risk, and revenue decay before you buy a SaaS.</p>
<a href="/" class="btn">Get started &rarr;</a>
</section>
<footer><p>&copy; 2026 ChurnLens. <a href="{ORIGIN}/">churnlens.site</a></p></footer>
</body>
</html>
"""
    out.write_text(page, encoding="utf-8")
    return True


def main():
    force = "--force" in sys.argv
    created = 0
    skipped = 0
    for section, meta in SECTIONS.items():
        dirpath = ROOT / section
        if not dirpath.exists():
            print(f"  ✗      {section}/ (directory missing)")
            continue
        items = scan_section(dirpath)
        if not items:
            print(f"  empty  {section}/ (no pages to list)")
            continue
        made = build_page(section, meta, items, force=force)
        marker = "✓ made" if made else "  skip"
        print(f"  {marker}  {section}/index.html  ({len(items)} items)")
        if made:
            created += 1
        else:
            skipped += 1
    print()
    print(f"Created {created}, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
