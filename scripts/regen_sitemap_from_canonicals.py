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

import json
import re
import subprocess
import sys
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


def vercelignored() -> set[str]:
    """Files .vercelignore'd are never uploaded, so their URLs always 404.

    Pre-fix, /striking-distance was emitted into the sitemap on every run purely
    because the file carried a canonical — it is .vercelignore'd and 404s live.
    """
    out: set[str] = set()
    vi = REPO / ".vercelignore"
    if not vi.exists():
        return out
    for raw in vi.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line.rstrip("/"))
    return out


def _vercel_cfg() -> dict:
    p = REPO / "vercel.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def redirect_sources(cfg: dict) -> set[str]:
    """A URL that 301s must never be advertised in the sitemap."""
    return {r["source"] for r in cfg.get("redirects", []) if "source" in r}


def rewrite_matchers(cfg: dict) -> list[re.Pattern]:
    """vercel.json rewrites are what make an extensionless path resolvable.

    This site sets neither cleanUrls nor trailingSlash, so `/foo` does NOT fall
    back to `foo.html`; it resolves only via a dir twin or an explicit rewrite.
    That is why /badge and /7-revenue-churn-red-flags 404 while /vs/chartmogul
    (covered by the `/vs/:slug` rewrite) serves fine.
    """
    pats = []
    for r in cfg.get("rewrites", []):
        src = r.get("source")
        if not src:
            continue
        # Build from the RAW source: re.escape() leaves ':' untouched on modern
        # Python, so escaping first makes every ':param' pattern unmatchable —
        # that silently dropped every rewrite-served page (e.g. /faq/:slug).
        out, i = [], 0
        for m in re.finditer(r":([A-Za-z_]+)(\*?)", src):
            out.append(re.escape(src[i:m.start()]))
            out.append(".*" if m.group(2) else "[^/]+")
            i = m.end()
        out.append(re.escape(src[i:]))
        try:
            pats.append(re.compile(rf"^{''.join(out)}$"))
        except re.error:
            continue
    return pats


def is_routable(url: str, path: Path, rewrites: list[re.Pattern]) -> bool:
    """True when Vercel can actually serve this URL."""
    slug = url[len(BASE):] or "/"
    if slug == "/":
        return True
    if (REPO / slug.lstrip("/") / "index.html").exists():
        return True          # directory twin resolves natively
    return any(p.match(slug) for p in rewrites)


def normalize_declared_canonical(path: Path, url: str) -> bool:
    """Make the page's own canonical agree with what the sitemap will list.

    Previously this script only rstrip()'d the slash for its own output, leaving
    the page still declaring the trailing-slash variant — the exact sitemap-vs-
    canonical split the script exists to prevent. Rewriting the tag closes it.
    """
    html = path.read_text(encoding="utf-8", errors="ignore")
    new = re.sub(
        r'(<link rel="canonical" href=")([^"]+)(")',
        lambda m: m.group(1) + url + m.group(3),
        html, count=1,
    )
    if new != html:
        path.write_text(new, encoding="utf-8")
        return True
    return False


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
    skipped_ignored = skipped_redirect = skipped_unroutable = 0
    fixed_canonicals: list[str] = []

    cfg = _vercel_cfg()
    ignored = vercelignored()
    redirects = redirect_sources(cfg)
    rewrites = rewrite_matchers(cfg)

    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if set(rel.parts[:-1]) & SKIP_DIRS or rel.parts[0] in SKIP_DIRS:
            continue
        if rel.name in SKIP_FILES:
            continue
        if str(rel) in ignored or rel.parts[0] in ignored:
            skipped_ignored += 1
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
        if url[len(BASE):] in redirects:
            skipped_redirect += 1          # 301s must not be advertised
            continue
        if not is_routable(url, p, rewrites):
            skipped_unroutable += 1        # no dir twin and no rewrite -> 404
            continue
        # Keep the page's declared canonical identical to the sitemap entry.
        if normalize_declared_canonical(p, url):
            fixed_canonicals.append(str(rel))
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

    # Write main sitemap
    (REPO / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml: {len(found)} URLs")

    # Regenerate image sitemap in sync with main sitemap
    img_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for url in sorted(found):
        img_lines.append("  <url>")
        img_lines.append(f"    <loc>{url}</loc>")
        img_lines.append("      <image:image>")
        img_lines.append(f"        <image:loc>{BASE}/og.png</image:loc>")
        img_lines.append("        <image:title>ChurnLens</image:title>")
        img_lines.append("      </image:image>")
        img_lines.append("  </url>")
    img_lines.append("</urlset>")
    (REPO / "image-sitemap.xml").write_text("\n".join(img_lines) + "\n", encoding="utf-8")
    print(f"image-sitemap.xml: {len(found)} URLs")
    print(f"  skipped noindex:        {skipped_noindex}")
    print(f"  skipped (no canonical): {skipped_nocanon}")
    print(f"  skipped .vercelignore'd:{skipped_ignored}")
    print(f"  skipped (has 301):      {skipped_redirect}")
    print(f"  skipped (unroutable):   {skipped_unroutable}")
    print(f"  canonicals normalized:  {len(fixed_canonicals)}")
    for f in fixed_canonicals:
        print(f"      fixed canonical: {f}")


if __name__ == "__main__":
    main()
