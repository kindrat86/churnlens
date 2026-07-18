#!/usr/bin/env python3
"""
Add cross-links from 6 core money pages to proprietary ChurnLens framework pages.

SCRIPT-TAG-AWARE: only modifies text in <body> — never inside <script>, <style>,
JSON-LD, or existing <a> tags. Targets only the 6 money pages.

Run from ~/churnlens. Idempotent — safe to re-run.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Only 6 core money pages
MONEY_PAGES = [
    "hidden-churn-saas-acquisition.html",
    "customer-concentration-risk.html",
    "saas-revenue-quality-score.html",
    "saas-due-diligence-checklist.html",
    "mrr-vs-revenue-quality.html",
    "saas-acquisition-red-flags.html",
]

# (regex pattern, href, label for display)
# Case-insensitive word-boundary matching. Only generic terms that map to ChurnLens frameworks.
LINKS = [
    (r'\b(Customer [Cc]oncentration [Rr]isk)\b', "/concentration-vulnerability-index"),
    (r'\b([Rr]evenue [Qq]uality [Ss]core)\b', "/revenue-quality-scorecard"),
    (r'\b([Zz]ombie MRR)\b', "/zombie-mrr-detector"),
    (r'\b([Mm]onthly [Rr]ecurring [Rr]evenue trajectory)\b', "/mrr-trajectory-forensics"),
    (r'\b([Aa]nnual[- ]?[Pp]lan [Dd]ecay)\b', "/annual-plan-decay-projection"),
    (r'\b([Cc]hurn [Dd]ivergence)\b', "/churn-divergence-detector"),
]


def is_inside_anchor(text: str, pos: int) -> bool:
    """Check if position pos in text is inside <a>...</a>."""
    before = text[max(0, pos - 600):pos]
    last_open = before.rfind('<a ')
    last_close = before.rfind('</a>')
    return last_open > last_close


def link_text(html: str, pattern: str, href: str) -> str:
    """Add ONE link per page to the first body-text occurrence."""
    # Skip if already linked
    if f'href="{href}"' in html:
        return html

    # Find body start
    body_start = html.find('<body')
    if body_start == -1:
        return html  # no body tag, skip
    
    # Also find body end
    body_end = html.find('</body>')
    if body_end == -1:
        body_end = len(html)
    
    # Work on body content only
    body = html[body_start:body_end]
    
    rx = re.compile(pattern)
    pos = 0
    while True:
        m = rx.search(body, pos)
        if not m:
            return html
        
        start, end = m.span()
        
        # Skip if inside script/style tag — scan back for most recent relevant tag
        before_text = body[max(0, start - 300):start]
        if re.search(r'<script[^>]*>', before_text) and not re.search(r'</script>', before_text):
            pos = end
            continue
        if re.search(r'<style[^>]*>', before_text) and not re.search(r'</style>', before_text):
            pos = end
            continue
            
        # Skip if inside an <a> tag
        if is_inside_anchor(body, start):
            pos = end
            continue
        
        # Found valid target
        match_text = m.group(1)  # the captured group
        replacement = f'<a href="{href}">{match_text}</a>'
        body = body[:start] + replacement + body[end:]
        # Put back into full HTML
        return html[:body_start] + body + html[body_end:]
    
    return html


def process_file(path: Path) -> int:
    orig = path.read_text(encoding="utf-8")
    out = orig
    total = 0
    for pattern, href in LINKS:
        before = out
        out = link_text(out, pattern, href)
        if out != before:
            total += 1
    if out != orig:
        path.write_text(out, encoding="utf-8")
    return total


def main():
    total = 0
    for fname in MONEY_PAGES:
        p = ROOT / fname
        if not p.exists():
            print(f"  ✗      {fname} (not found)")
            continue
        n = process_file(p)
        marker = f"✓ +{n}" if n else "  ok "
        print(f"  {marker}  {fname}")
        total += n
    print(f"\nTotal: {total} cross-links added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
