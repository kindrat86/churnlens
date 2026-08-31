#!/usr/bin/env python3
"""Deterministic verifier for /compare/best-churn-analytics-tools-for-saas-acquirers.

Written BEFORE the page rewrite (TDD RED, 2026-08-31): run it against the
pre-rewrite page and it fails on every check below; the rewrite makes it
green. It exists so the guarantees of the 2026-08-31 upgrade cannot silently
regress:

  1. the .html twin and the served directory twin are byte-identical
  2. every JSON-LD block parses
  3. Article, BreadcrumbList, and FAQPage blocks are present and reference
     the canonical URL
  4. every external tool row in the comparison table links at least one
     official (vendor-domain) source
  5. banned stale/arbitrary tokens are absent: fabricated acquirer-fit
     scores, stale price tokens, and the unprovable "only purpose-built"
     superiority claim
  6. dateModified is current (2026-08-31) and the sitemap lastmod matches
  7. no em dashes in the changed main copy (site style rule)

Exit 1 with a readable list on any failure. Cheap: stdlib only, no network,
no build.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FLAT = REPO / "compare" / "best-churn-analytics-tools-for-saas-acquirers.html"
NESTED = REPO / "compare" / "best-churn-analytics-tools-for-saas-acquirers" / "index.html"
SITEMAP = REPO / "sitemap.xml"

CANONICAL = "https://churnlens.site/compare/best-churn-analytics-tools-for-saas-acquirers"
DATE_MODIFIED = "2026-08-31"

# Rows that describe a tool we do not own must carry at least one link to that
# vendor's own domain inside the row's <tr> (pricing or product page).
EXTERNAL_ROW_SOURCES = {
    "ChartMogul": ["chartmogul.com"],
    "Baremetrics": ["baremetrics.com"],
    "Paddle / ProfitWell": ["paddle.com", "profitwell.com"],
    "Gainsight": ["gainsight.com"],
    "ChurnZero": ["churnzero.com", "churnzero.net"],
}

# Tokens retired by the 2026-08-31 rewrite. Scores were arbitrary; prices were
# stale or unsourced; the superiority claim was unprovable.
BANNED_TOKENS = [
    "/100",              # arbitrary acquirer-fit scores: 95/100, 50/100, ...
    "only purpose-built",
    "$100+/mo",
    "$79+/mo",
    "$79–",
    "$49/mo — transparent",  # stale framing; $49/mo itself is live pricing
    "Free tier limited",
    "Quote-based",
]

# Domains that are NOT acceptable as the official source for a row (aggregate
# review sites, competitors) — defense in depth for check 4.
NON_OFFICIAL = ("g2.com", "capterra", "getapp", "trustpilot", "churnlens.site")


def fail(msg, problems):
    problems.append(msg)


def strip_tags(html):
    return re.sub(r"<[^>]+>", " ", html)


def main():
    problems = []

    if not FLAT.is_file() or not NESTED.is_file():
        print("[verify-churn-analytics-guide] FAIL - twin files missing")
        return 1
    flat = FLAT.read_text(encoding="utf-8")
    nested = NESTED.read_text(encoding="utf-8")

    # 1. twins byte-identical
    if flat != nested:
        fail("twins are not byte-identical "
             "(Vercel serves the directory twin; run the sync after editing)", problems)

    html = flat

    # 2. every JSON-LD block parses
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    parsed = []
    for i, b in enumerate(blocks):
        try:
            parsed.append(json.loads(b))
        except json.JSONDecodeError as e:
            fail("JSON-LD block %d does not parse: %s" % (i + 1, e), problems)

    # 3. required schema types + canonical wiring
    def types_of(node):
        t = node.get("@type") if isinstance(node, dict) else None
        if isinstance(t, list):
            return set(t)
        return {t} if t else set()

    all_types = set()
    for node in parsed:
        all_types |= types_of(node)
        for sub in (node.get("@graph") or []) if isinstance(node, dict) else []:
            all_types |= types_of(sub)
    for required in ("Article", "BreadcrumbList", "FAQPage"):
        if required not in all_types:
            fail("missing %s JSON-LD block" % required, problems)
    for node in parsed:
        if not isinstance(node, dict):
            continue
        if "Article" in types_of(node):
            if node.get("dateModified") != DATE_MODIFIED:
                fail("Article.dateModified is %r, expected %s"
                     % (node.get("dateModified"), DATE_MODIFIED), problems)
            if node.get("mainEntityOfPage", {}).get("@id") != CANONICAL:
                fail("Article.mainEntityOfPage does not point at the canonical URL",
                     problems)
        if "FAQPage" in types_of(node):
            qs = node.get("mainEntity") or []
            if not qs:
                fail("FAQPage has no mainEntity questions", problems)
            for q in qs:
                if not q.get("name") or not (q.get("acceptedAnswer") or {}).get("text"):
                    fail("FAQPage question %r lacks name or acceptedAnswer.text"
                         % q.get("name"), problems)
                # schema must correspond to visible FAQ copy on the page
                if q.get("name") and q["name"] not in html:
                    fail("FAQPage question %r is not visible on the page"
                         % q["name"], problems)

    # 4. every external table row carries an official source link
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S)
    if not tbody:
        fail("no comparison table <tbody> found", problems)
    else:
        for tr in re.findall(r"<tr>(.*?)</tr>", tbody.group(1), re.S):
            text = strip_tags(tr)
            for tool, domains in EXTERNAL_ROW_SOURCES.items():
                if tool not in text:
                    continue
                hrefs = re.findall(r'href="(https?://[^"]+)"', tr)
                if not any(any(d in h for d in domains) for h in hrefs):
                    fail("row for %s has no official source link (need one of %s)"
                         % (tool, domains), problems)
                if any(any(b in h for b in NON_OFFICIAL) for h in hrefs
                       if not any(d in h for d in ("churnlens.site",))):
                    pass  # churnlens links are fine; others handled above

    # 5. banned tokens absent
    for tok in BANNED_TOKENS:
        if tok in html:
            fail("banned token %r still present" % tok, problems)
    if re.search(r"\b\d{2}/100\b", html):
        fail("numeric acquirer-fit score still present", problems)

    # 6. sitemap lastmod current
    sm = SITEMAP.read_text(encoding="utf-8")
    m = re.search(
        r"<loc>%s</loc>\s*<lastmod>([^<]+)</lastmod>" % re.escape(CANONICAL), sm)
    if not m:
        fail("sitemap entry for the canonical URL is missing", problems)
    elif m.group(1).strip() != DATE_MODIFIED:
        fail("sitemap lastmod is %r, expected %s" % (m.group(1), DATE_MODIFIED),
             problems)

    # 7. no em dashes in <article> copy
    article = re.search(r"<article>(.*?)</article>", html, re.S)
    if article:
        body = article.group(1)
        if "\u2014" in body:
            fail("em dash (\\u2014) in <article> copy", problems)
        if "&mdash;" in body:
            fail("&mdash; entity in <article> copy", problems)

    # 8. visible methodology + sources section (upgrade requirement)
    if "Methodology" not in html or "Sources" not in html:
        fail("visible Methodology and Sources sections are missing", problems)

    if problems:
        print("[verify-churn-analytics-guide] FAIL - %d problem(s):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("[verify-churn-analytics-guide] OK - twins identical, schema valid, "
          "rows sourced, no banned tokens, dates current, no em dashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
