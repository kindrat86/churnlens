#!/usr/bin/env python3
"""Rebuild sitemap.xml from each page's OWN declared <link rel="canonical">.

Why derived from canonicals rather than from filenames: the audit on 2026-07-25
found 15 sitemap URLs that self-canonicalised to a different variant (notably
/pricing -> /pricing/, which left the pricing page never crawled). Deriving the
sitemap from the canonical each page actually declares makes that class of drift
structurally impossible instead of something to re-fix by hand.

Excluded: noindex pages, Google verification files, embed/widget fragments, and
anything under .vercelignore'd paths that is never served.

Safe to re-run; output is deterministic and sorted.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://churnlens.site"

SKIP_DIRS = {
    "i18n", "i18n_out", "dist", ".vercel", ".git", "node_modules",
    "scripts", "public", "embed", "widgets", "schema",
}
SKIP_FILES = {"404.html", "index.html_backup"}

# Hub/utility URLs that should not be advertised for indexing.
SKIP_URLS = {
    f"{BASE}/thank-you",
    f"{BASE}/oto",
    f"{BASE}/404",
}

PRIORITY = [
    (re.compile(r"^/$"), "1.0", "weekly"),
    (re.compile(r"^/(pricing|about|contact)$"), "0.9", "monthly"),
    (re.compile(r"^/(alternatives-to|vs|compare|reviews|best)/"), "0.8", "monthly"),
    (re.compile(r"^/(free|calculators|tools)/"), "0.8", "monthly"),
    (re.compile(r"^/(benchmarks|research|data|stats)/"), "0.7", "monthly"),
]


def git_lastmod(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(REPO))],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", out):
            return out
    except Exception:
        pass
    return "2026-07-25"


def classify(url: str) -> tuple[str, str]:
    path = url[len(BASE):] or "/"
    for pat, prio, freq in PRIORITY:
        if pat.search(path):
            return prio, freq
    return "0.6", "monthly"


def main() -> None:
    found: dict[str, Path] = {}
    skipped_noindex = skipped_nocanon = 0

    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if set(rel.parts[:-1]) & SKIP_DIRS or rel.parts[0] in SKIP_DIRS:
            continue
        if rel.name in SKIP_FILES:
            continue
        html = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'name="robots"[^>]*noindex', html, re.I) or "<meta name=\"robots\" content=\"noindex" in html:
            skipped_noindex += 1
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if not m:
            skipped_nocanon += 1
            continue
        url = m.group(1).rstrip("/") or BASE
        if url == BASE:
            url = BASE + "/"
        if url in SKIP_URLS:
            continue
        # first writer wins, but prefer the flat file over the dir twin for lastmod
        if url not in found or rel.name != "index.html":
            found[url] = p

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(found):
        prio, freq = classify(url)
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{git_lastmod(found[url])}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    (REPO / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml: {len(found)} URLs")
    print(f"  skipped noindex:        {skipped_noindex}")
    print(f"  skipped (no canonical): {skipped_nocanon}")


if __name__ == "__main__":
    main()
