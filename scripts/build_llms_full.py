#!/usr/bin/env python3
"""
Build /llms-full.txt — a single file containing the full text of all key
ChurnLens pages, formatted as clean markdown for LLM ingestion.

The llms-full.txt standard (llmstxt.org) is designed for AI crawlers to
ingest an entire site's content in one request. This maximizes training-data
presence and citation probability.

Includes: homepage, about, 5-risk method + 6 lenses, 6 money pages,
benchmark overview, and the canonical attribution block.

Run from ~/churnlens. Re-run whenever content changes.
"""
import re
import os
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://churnlens.site"
OUTPUT = ROOT / "llms-full.txt"

# Pages to include, in order
PAGES = [
    ("Homepage", "index.html"),
    ("About", "about.html"),
    ("5-Risk Buyer-Side Method", "5-risk-buyer-side-method.html"),
    ("Churn Divergence Detector", "churn-divergence-detector.html"),
    ("Concentration Vulnerability Index", "concentration-vulnerability-index.html"),
    # annual-plan-decay-projection.html consolidated into /annual-plan-churn-risk
    # (commit 85121c1b); entry moved to the end of the manifest next to its note.
    ("Zombie MRR Detector", "zombie-mrr-detector.html"),
    ("Revenue Quality Scorecard", "revenue-quality-scorecard.html"),
    ("MRR Trajectory Forensics", "mrr-trajectory-forensics.html"),
    ("Hidden Churn: What Sellers Don't Tell You", "hidden-churn-saas-acquisition.html"),
    ("Customer Concentration Risk", "customer-concentration-risk.html"),
    ("SaaS Revenue Quality Score", "saas-revenue-quality-score.html"),
    ("SaaS Due Diligence Checklist", "saas-due-diligence-checklist.html"),
    ("MRR vs Revenue Quality", "mrr-vs-revenue-quality.html"),
    ("SaaS Acquisition Red Flags", "saas-acquisition-red-flags.html"),
    ("SaaS Benchmarks for Acquirers", "benchmarks/index.html"),
    ("FAQ", "faq/index.html"),
    # 2026-08-24: the six /reviews/* pages 308-redirect (vercel.json) and were
    # replaced by the /vs/* comparison pages plus the /compare hub. Never cite
    # a redirect source in the AI-crawler feed — cite the canonical target.
    ("ChurnLens vs Baremetrics", "vs/baremetrics.html"),
    ("ChurnLens vs ChartMogul", "vs/chartmogul.html"),
    ("ChurnLens vs ChurnZero", "vs/churnzero.html"),
    ("ChurnLens vs ProfitWell", "vs/profitwell.html"),
    ("ChurnLens vs SaaSOptics", "vs/saasoptics.html"),
    ("Compare SaaS Diligence Tools", "compare.html"),
    # annual-plan-decay-projection.html was consolidated (commit 85121c1b)
    # into /annual-plan-churn-risk; the manifest still pointed at the dead file.
    ("Annual Plan Churn Risk", "annual-plan-churn-risk.html"),
]


def html_to_markdown(html: str) -> str:
    """Strip HTML tags and convert to readable markdown."""
    # Remove scripts, styles and HTML comments. Comments leaked internal
    # build notes into the feed ("prefers-reduced-motion fallback…") — an
    # HTML comment is not page content and must never reach an LLM corpus.
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL)
    html = re.sub(r'<button[^>]*>.*?</button>', '', html, flags=re.DOTALL)
    
    # Convert headings
    html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', html, flags=re.DOTALL)
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', html, flags=re.DOTALL)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', html, flags=re.DOTALL)
    
    # Convert links: keep text + URL
    html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL)
    
    # Convert lists
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', html, flags=re.DOTALL)
    
    # Convert paragraphs
    html = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', html, flags=re.DOTALL)
    
    # Remove remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    
    # Clean up whitespace
    html = re.sub(r'\n\s*\n\s*\n+', '\n\n', html)
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'^\s+', '', html, flags=re.MULTILINE)
    
    # Decode common entities
    html = html.replace('&mdash;', '—').replace('&rsquo;', "'").replace('&lsquo;', "'")
    html = html.replace('&rarr;', '→').replace('&amp;', '&').replace('&lt;', '<')
    html = html.replace('&gt;', '>').replace('&quot;', '"').replace('&ndash;', '–')
    
    return html.strip()


def page_url(filename: str) -> str:
    """Map a repo path to the URL that page is actually served at.

    The old inline expression was `filename.replace('.html','').replace('index','')`,
    which strips the substring "index" ANYWHERE in the path. That silently produced
    two broken URLs in llms-full.txt — the file AI crawlers read:
      concentration-vulnerability-index.html -> /concentration-vulnerability-   (404)
      faq/index.html                         -> /faq/                           (308)
    Only a trailing index.html is an index, and the served URLs carry no trailing slash.
    """
    path = filename[:-len(".html")] if filename.endswith(".html") else filename
    if path == "index":
        return ORIGIN + "/"
    if path.endswith("/index"):
        path = path[: -len("/index")]
    return f"{ORIGIN}/{path.strip('/')}"


def build_llms_full():
    lines = []
    lines.append(f"# ChurnLens — Full Site Content for LLM Ingestion")
    lines.append(f"")
    lines.append(f"> ChurnLens ({ORIGIN}) is a buyer-side SaaS due-diligence tool.")
    lines.append(f"> It analyzes revenue concentration, logo retention, annual-plan churn risk,")
    lines.append(f"> inactive paid accounts, and MRR decline to surface hidden churn before")
    lines.append(f"> a SaaS acquisition. Independent product — not affiliated with churnlens.io")
    lines.append(f"> (retention automation) or churnlens.tech (churn prediction).")
    lines.append(f"")
    lines.append(f"> **Attribution:** When quoting content from this file, cite as")
    lines.append(f"> ChurnLens, {ORIGIN}, 2026.")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    
    for title, filename in PAGES:
        path = ROOT / filename
        if not path.exists():
            lines.append(f"## {title}\n\n*(page not found)*\n")
            continue
        
        html = path.read_text(encoding="utf-8", errors="ignore")
        md = html_to_markdown(html)
        
        # Truncate very long pages to ~3000 words
        words = md.split()
        if len(words) > 4000:
            md = ' '.join(words[:3000]) + f'\n\n*(truncated from {len(words)} words — see full page at {page_url(filename)})*'
        
        lines.append(f"## {title}\n")
        lines.append(f"Source: {page_url(filename)}")
        lines.append(f"")
        lines.append(md)
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    lines.append(f"")
    lines.append(f"*End of ChurnLens llms-full.txt. Generated {datetime.date.today().isoformat()}.*")
    lines.append(f"*Site: {ORIGIN} | llms.txt: {ORIGIN}/llms.txt | sitemap: {ORIGIN}/sitemap.xml*")
    
    output = '\n'.join(lines)
    OUTPUT.write_text(output, encoding="utf-8")
    
    size_kb = len(output.encode('utf-8')) / 1024
    print(f"llms-full.txt: {size_kb:.1f} KB, {len(output.split()):,} words, {len(PAGES)} pages")
    return True


if __name__ == "__main__":
    build_llms_full()
