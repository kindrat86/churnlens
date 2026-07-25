#!/usr/bin/env python3
"""Add contextual links to /free/saas-churn-analyzer and the /free/ hub.

Idempotent via the <!-- csv-analyzer-v1 --> marker: re-running replaces the block
rather than stacking copies, and no file is ever created or deleted. Placement is
inside the existing `<section class="cta">` where one exists (the six lens pages and
the framework pages all have one), otherwise immediately before `<footer`.

Run from the repo root:  python3 scripts/inject_csv_analyzer_links.py [--dry-run]
"""
import os
import re
import sys

MARK_OPEN = "<!-- csv-analyzer-v1 -->"
MARK_CLOSE = "<!-- /csv-analyzer-v1 -->"

BLOCK = (
    MARK_OPEN
    + '<p style="margin-top:14px;font-size:.95rem">'
      'Already hold the ledger? Run it yourself, free and instantly, in the '
      '<a href="/free/saas-churn-analyzer">SaaS Churn &amp; Revenue-Quality Analyzer</a> — '
      'the same six lenses computed in your browser, so the CSV never leaves your machine. '
      'See all <a href="/free">free buyer-side tools</a>.'
      '</p>'
    + MARK_CLOSE
)

TARGETS = [
    "index.html",
    "5-risk-buyer-side-method.html",
    "churn-divergence-detector.html",
    "concentration-vulnerability-index.html",
    "annual-plan-churn-risk.html",
    "zombie-mrr-detector.html",
    "revenue-quality-scorecard.html",
    "mrr-trajectory-forensics.html",
    "saas-due-diligence-checklist.html",
    "ultimate-saas-due-diligence-guide.html",
    "saas-m-and-a-due-diligence-framework.html",
    "sample-churn-risk-report.html",
    "calculators/index.html",
    "learn/index.html",
]

CTA_RE = re.compile(r'<section[^>]*class="[^"]*\bcta\b[^"]*"[^>]*>', re.I)


def inject(html):
    """Return (new_html, action). Never raises on unexpected shapes."""
    existing = re.search(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE), html, re.S)
    if existing:
        if existing.group(0) == BLOCK:
            return html, "unchanged"
        return html[: existing.start()] + BLOCK + html[existing.end():], "updated"

    m = CTA_RE.search(html)
    if m:
        close = html.find("</section>", m.end())
        if close != -1:
            return html[:close] + BLOCK + html[close:], "cta"

    for anchor in ("<footer", "</body>"):
        i = html.rfind(anchor)
        if i != -1:
            return html[:i] + BLOCK + "\n" + html[i:], "pre-" + anchor.strip("<>/")
    return html, "no-anchor"


def main():
    dry = "--dry-run" in sys.argv
    counts = {}
    for rel in TARGETS:
        if not os.path.isfile(rel):
            counts["missing"] = counts.get("missing", 0) + 1
            print(f"  SKIP     {rel} (not found)")
            continue
        with open(rel, encoding="utf-8") as fh:
            before = fh.read()
        after, action = inject(before)
        counts[action] = counts.get(action, 0) + 1
        print(f"  {action:<9}{rel}")
        if after != before and not dry:
            with open(rel, "w", encoding="utf-8") as fh:
                fh.write(after)
    print("\n" + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) + (" (dry run)" if dry else ""))
    if counts.get("no-anchor"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
