#!/usr/bin/env python3
"""Fail loudly if the /vs/ comparison pages get flattened again.

These pages have been destroyed twice by generator runs. The mechanism is in
~/.growth-engine/isenberg-pseo-round15.py: its skip-guard reads the DIRECTORY twin

    <repo>/vs/<slug>/index.html

and only skips when that file exists AND contains "<!-- isenberg-round15 -->".
Its write_page() is otherwise unconditional and rewrites both twins. round16/18/19
use the opposite polarity -- they skip any page that does NOT carry their own
marker -- so those markers must stay absent.

This guard asserts the invariants that keep the pages alive. Run it before any
deploy; exits non-zero with a specific reason on failure.

    python3 scripts/guard_comparison_depth.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KEEP_MARKER = "<!-- isenberg-round15 -->"
FORBID_MARKERS = ("<!-- isenberg-round16 -->", "<!-- isenberg-round18 -->", "<!-- isenberg-round19 -->")
WORD_FLOOR = 900

# The comparison pages that must stay deep. Slug -> minimum words.
# baremetrics/chartmogul/profitwell/churnzero absorbed the former
# /alternatives-to/<slug> content during the 2026-07-25 consolidation and carry
# an anchor id that vercel.json redirects point at, so they have a higher floor.
PAGES = {
    "baremetrics": 1800,
    "chartmogul": 1800,
    "profitwell": 1800,
    "churnzero": 1800,
    "saasoptics": WORD_FLOOR,
}

# vercel.json redirects land on these fragment ids; if the id disappears the
# redirect silently drops the visitor at the top of the page instead.
REQUIRED_ANCHORS = {
    "baremetrics": "baremetrics-alternatives-for-saas-acquisition-due-diligence",
    "chartmogul": "chartmogul-alternatives-for-saas-acquisition-due-diligence",
    "profitwell": "profitwell-alternatives-for-saas-acquisition-due-diligence",
    "churnzero": "churnzero-alternatives-for-saas-acquisition-due-diligence",
}


def visible_words(html: str) -> int:
    h = re.sub(r"(?is)<script.*?</script>", " ", html)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = re.sub(r"(?is)<nav.*?</nav>", " ", h)
    h = re.sub(r"(?is)<footer.*?</footer>", " ", h)
    return len(re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", h)).split())


def main() -> int:
    failures: list[str] = []

    for slug, floor in PAGES.items():
        flat = REPO / "vs" / f"{slug}.html"
        twin = REPO / "vs" / slug / "index.html"

        if not flat.exists():
            failures.append(f"vs/{slug}.html is MISSING (page was deleted)")
            continue
        if not twin.exists():
            failures.append(
                f"vs/{slug}/index.html is MISSING — round15's skip-guard reads this exact path, "
                f"so without it the next generator run overwrites the page"
            )
            continue

        for label, p in (("flat", flat), ("twin", twin)):
            html = p.read_text(encoding="utf-8", errors="ignore")
            rel = p.relative_to(REPO)

            words = visible_words(html)
            if words < floor:
                failures.append(f"{rel}: {words} visible words, floor is {floor} — page was flattened")

            if KEEP_MARKER not in html:
                failures.append(f"{rel}: missing {KEEP_MARKER} — round15 will overwrite this page")

            for bad in FORBID_MARKERS:
                if bad in html:
                    failures.append(f"{rel}: carries {bad}, which invites that generator to overwrite it")

            m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if not m:
                failures.append(f"{rel}: no canonical tag")
            else:
                want = f"https://churnlens.site/vs/{slug}"
                if m.group(1).rstrip("/") != want:
                    failures.append(f"{rel}: canonical is {m.group(1)}, expected {want}")

            # FAQ schema must stay in sync with the visible FAQ
            visible_q = re.findall(r"<summary>(.*?)</summary>", html, re.S)
            schema_q: list[str] = []
            for block in re.findall(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html):
                try:
                    data = json.loads(block)
                except ValueError:
                    failures.append(f"{rel}: invalid JSON-LD block")
                    continue
                if isinstance(data, dict) and data.get("@type") == "FAQPage":
                    schema_q = [q.get("name", "") for q in data.get("mainEntity", [])]
            if schema_q and visible_q:
                stripped = [re.sub(r"<[^>]+>", "", q).strip() for q in visible_q]
                if len(schema_q) != len(stripped):
                    failures.append(
                        f"{rel}: FAQPage schema has {len(schema_q)} questions but {len(stripped)} are visible"
                    )

            if label == "flat" and slug in REQUIRED_ANCHORS:
                anchor = REQUIRED_ANCHORS[slug]
                if f'id="{anchor}"' not in html:
                    failures.append(
                        f"{rel}: missing id=\"{anchor}\" — vercel.json redirects /alternatives-to/{slug} "
                        f"to this fragment"
                    )

    # redirect hygiene
    try:
        cfg = json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
        redirects = cfg.get("redirects", [])
        for r in redirects:
            if r.get("source") == r.get("destination"):
                failures.append(f"vercel.json: {r['source']} redirects to itself")
        sources: dict[str, int] = {}
        for r in redirects:
            sources[r.get("source", "")] = sources.get(r.get("source", ""), 0) + 1
        for src, n in sources.items():
            if n > 1:
                failures.append(f"vercel.json: duplicate redirect source {src} ({n} entries)")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"vercel.json unreadable: {exc}")

    if failures:
        print("GUARD FAILED — comparison pages regressed:\n")
        for f in failures:
            print(f"  ✗ {f}")
        print(f"\n{len(failures)} problem(s). Do not deploy until resolved.")
        return 1

    print(f"GUARD PASSED — {len(PAGES)} comparison pages deep, marker-protected and consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
