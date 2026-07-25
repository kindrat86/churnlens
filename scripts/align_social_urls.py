#!/usr/bin/env python3
"""Align og:url / twitter:url with each page's declared <link rel="canonical">.

Companion to regen_sitemap_from_canonicals.py, closing the last gap left by the
2026-07-25 canonical fix (5345927). That commit repointed 19 canonicals to the
no-slash sitemap form and added canonicals to 10 pages that had none — but the
10 newly-canonicalised pages kept their pre-existing trailing-slash og:url, so
they shipped a page declaring two different URLs for itself:

    <link rel="canonical" href="https://churnlens.site/free/churn-calculator"/>
    <meta property="og:url" content="https://churnlens.site/free/churn-calculator/"/>

That matters more here than it looks. All five affected pages are the free
calculators — the site's only natural linkable assets. og:url is what social
platforms and several crawlers use to dedupe a shared URL, so inbound shares and
links were accruing to the trailing-slash variant while the canonical pointed at
the other one, splitting the little link equity this site has.

Derives from the canonical rather than re-deriving from the filename, for the
same reason the sitemap regenerator does: one source of truth per page makes the
drift structurally impossible instead of something to re-fix by hand.

Safe to re-run; only rewrites tags that actually disagree.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Mirrors regen_sitemap_from_canonicals.py. `public/` is excluded because every
# /public/* path 308s to its root-level twin (vercel.json redirect) — those files
# are never served, so rewriting them is diff noise, not a fix.
SKIP_DIRS = {"i18n", "i18n_out", "dist", ".vercel", ".git", "node_modules",
             "scripts", "public"}

BASE = "https://churnlens.site"

CANONICAL_RE = re.compile(r'(<link rel="canonical" href=")([^"]+)(")')
TAGS = (
    ("og:url", re.compile(r'(<meta property="og:url" content=")([^"]*)(")')),
    ("twitter:url", re.compile(r'(<meta name="twitter:url" content=")([^"]*)(")')),
)


def normalise(url: str) -> str:
    """Same rule regen_sitemap_from_canonicals.py applies when building <loc>.

    That script strips the trailing slash to form the sitemap URL but leaves the
    page's own canonical tag untouched, so any page declaring a trailing-slash
    canonical silently reproduces the exact mismatch 5345927 set out to remove
    (seen on /free/due-diligence-simulator and /7-revenue-churn-red-flags after
    a later regeneration). Normalising the tag itself is what actually closes
    the class: canonical, og:url, twitter:url and <loc> then agree by
    construction rather than by a hand-fix that has to be repeated.

    The homepage keeps its slash — BASE alone is not a valid URL path.
    """
    stripped = url.rstrip("/") or BASE
    return BASE + "/" if stripped == BASE else stripped


def main() -> int:
    dry = "--dry-run" in sys.argv
    changed_files = 0
    changed_tags = 0
    no_canonical = 0

    for path in sorted(REPO.rglob("*.html")):
        rel = path.relative_to(REPO)
        if set(rel.parts) & SKIP_DIRS:
            continue

        html = path.read_text(encoding="utf-8", errors="ignore")
        m = CANONICAL_RE.search(html)
        if not m:
            no_canonical += 1
            continue
        canonical = normalise(m.group(2))

        updated = html
        hits = 0

        # Normalise the canonical tag itself first, so og:url/twitter:url below
        # align to the same value the sitemap will carry.
        if m.group(2) != canonical:
            updated = CANONICAL_RE.sub(
                lambda mo: mo.group(1) + canonical + mo.group(3), updated, count=1)
            hits += 1
        for _name, pattern in TAGS:
            def repl(mo, _c=canonical):
                nonlocal hits
                if mo.group(2) == _c:
                    return mo.group(0)
                hits += 1
                return mo.group(1) + _c + mo.group(3)
            updated = pattern.sub(repl, updated)

        if hits:
            changed_files += 1
            changed_tags += hits
            if not dry:
                path.write_text(updated, encoding="utf-8")
            print(f"  {'would fix' if dry else 'fixed'} {hits} tag(s): {rel}")

    verb = "would change" if dry else "changed"
    print(f"\n{verb} {changed_tags} tag(s) across {changed_files} file(s); "
          f"{no_canonical} file(s) had no canonical to align to")
    return 0


if __name__ == "__main__":
    sys.exit(main())
