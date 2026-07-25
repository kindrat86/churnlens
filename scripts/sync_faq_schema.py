#!/usr/bin/env python3
"""Deduplicate the visible FAQ on the /vs/ comparison pages and regenerate the
FAQPage JSON-LD from what is actually on the page.

The 2026-07-25 consolidation folded the old /alternatives-to/<slug> content into
/vs/<slug>. Both sources carried an FAQ, so the merged pages ended up with the
same questions twice (8 visible <details> where 3 were verbatim repeats) while the
FAQPage schema still declared only 4. That is both a duplicate-content problem and
a structured-data mismatch: Google requires FAQPage markup to correspond to
FAQ content visible on the page.

This script keeps the first occurrence of each question, drops later repeats, and
rebuilds the FAQPage block from the surviving set so the two cannot disagree.

Idempotent.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SLUGS = ["baremetrics", "chartmogul", "profitwell", "churnzero", "saasoptics"]

DETAILS_RE = re.compile(
    r"<details>\s*<summary>(?P<q>.*?)</summary>\s*(?P<body>.*?)</details>",
    re.S,
)


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


def process(path: Path) -> tuple[int, int, int]:
    html = path.read_text(encoding="utf-8")

    seen: set[str] = set()
    kept: list[tuple[str, str]] = []
    removed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal removed
        q = plain(m.group("q"))
        key = q.lower()
        if key in seen:
            removed += 1
            return ""  # drop the repeat entirely
        seen.add(key)
        kept.append((q, plain(m.group("body"))))
        return m.group(0)

    html = DETAILS_RE.sub(repl, html)

    # collapse any now-empty duplicate FAQ heading left behind
    html = re.sub(
        r"(?is)<h2>\s*(?:Frequently asked questions|FAQ)\s*</h2>\s*(?=<h2>|<div class=\"cta\")",
        "",
        html,
    )
    # tidy the blank run left by removed <details>
    html = re.sub(r"\n{3,}", "\n\n", html)

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in kept
        ],
    }
    block = (
        '<script type="application/ld+json">'
        + json.dumps(schema, ensure_ascii=False)
        + "</script>"
    )

    pattern = r'<script type="application/ld\+json">\s*\{(?:(?!</script>).)*?"@type"\s*:\s*"FAQPage".*?</script>'
    if re.search(pattern, html, flags=re.S):
        html = re.sub(pattern, block, html, count=1, flags=re.S)
    else:
        html = html.replace("</head>", block + "\n</head>", 1)
    # any *additional* FAQPage blocks are now stale duplicates -> remove them
    parts = re.split(pattern, html, flags=re.S)
    if len(parts) > 1:
        html = parts[0] + block + "".join(parts[1:])

    path.write_text(html, encoding="utf-8")
    return len(kept), removed, len(schema["mainEntity"])


def main() -> None:
    for slug in SLUGS:
        for p in (REPO / "vs" / f"{slug}.html", REPO / "vs" / slug / "index.html"):
            if not p.exists():
                continue
            kept, removed, n = process(p)
            print(f"  {p.relative_to(REPO)}: {kept} unique Q kept, {removed} repeats removed, schema={n}")


if __name__ == "__main__":
    main()
