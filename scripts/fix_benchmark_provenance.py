#!/usr/bin/env python3
"""
Fix fabricated provenance + corrupted JSON-LD in /benchmarks pSEO pages.

Two problems introduced by the pSEO generator (now caught pre-deploy):
1. JSON-LD @context can be corrupted: "@context":"https://***@type":"Article"... (invalid JSON)
   (invalid JSON - every crawler fails to parse the block, losing all schema).
2. Pages claim fabricated proprietary data: "aggregated data from over 500 SaaS
   companies", "based on teams using churn due diligence tool workflows".
   For a due-diligence brand, unsourced stats are an existential credibility risk.

This script fixes both, site-wide. Run from ~/churnlens.
"""
import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ~/churnlens
BENCH = ROOT / "benchmarks"

# --- 1. Fix corrupted JSON-LD @context ---
# Pattern: "@context":"https://***@type":"Article"  ->  "@context":"https://schema.org","@type":"Article"
CORRUPTED_RE = re.compile(r'"@context":"https://\*\*\*@type":"([^"]+)"')
CORRUPTED_FIX = r'"@context":"https://schema.org","@type":"\1"'

# --- 2. Replace fabricated provenance ---
FABRICATED_PATTERNS = [
    # Lede paragraph variants
    (
        re.compile(
            r"(These benchmarks are based on )aggregated data from over \d+ SaaS companies across B2B and B2C segments\.?",
            re.IGNORECASE,
        ),
        r"\1public SaaS benchmarking research (SaaS Capital, Recurly, Benchmarkit) and curated for buyer-side due diligence. Each figure should be verified against its primary source at decision time.",
    ),
    # "based on aggregated data from teams using X workflows" body paragraph
    (
        re.compile(
            r"This benchmark is based on aggregated data from teams using [^.]+\.",
            re.IGNORECASE,
        ),
        "This figure is a curated reference point drawn from public SaaS benchmarking research, not original ChurnLens data. Verify against the primary source (SaaS Capital, Recurly, Benchmarkit, or comparable) before relying on it in a deal.",
    ),
]

# --- 3. FAQ "The benchmark value is X" -> add source caveat ---
FAQ_VALUE_RE = re.compile(
    r'("text":")(The benchmark value is[^"]+?)( )(")',
)
FAQ_FIX = (
    lambda m: f'{m.group(1)}{m.group(2)} These are commonly cited industry reference points (SaaS Capital, Recurly, Benchmarkit), not ChurnLens proprietary data. {m.group(4)}'
)

SOURCES_BLOCK = """
<h2>Sources &amp; methodology</h2>
<p>The benchmarks on this page are <strong>curated reference points</strong> drawn from public SaaS benchmarking research &mdash; not original ChurnLens data. Primary sources include:</p>
<ul>
<li><strong>SaaS Capital</strong> &mdash; annual private B2B SaaS retention &amp; metrics survey (revenue churn, NRR by ARR band).</li>
<li><strong>Recurly</strong> &mdash; recurring Churn Report (logo vs revenue churn, voluntary vs involuntary split).</li>
<li><strong>Benchmarkit</strong> &mdash; B2B SaaS Performance Metrics (NRR, CAC payback, growth by ACV).</li>
<li><strong>High Alpha / First Page Sage</strong> &mdash; SaaS benchmarks reports (retention and efficiency by stage).</li>
</ul>
<p>Distinguish <em>logo churn</em> from <em>revenue churn</em>, and <em>monthly</em> from <em>annual</em>, when comparing &mdash; conflating them is the most common benchmark error (and the exact gap ChurnLens surfaces in a target&rsquo;s CSV). Figures shift year over year; re-verify against the primary source before relying on a number in diligence. <em>Last reviewed July 2026.</em></p>
"""


def insert_sources_block(html: str) -> str:
    """Insert the Sources & methodology section before the closing </article>."""
    if "Sources & methodology" in html or "Sources &amp; methodology" in html:
        return html  # already present
    # Prefer to insert before </article>; fall back to before the CTA section
    if "</article>" in html:
        return html.replace("</article>", SOURCES_BLOCK.strip() + "\n</article>", 1)
    return html.replace('<section class="cta">', SOURCES_BLOCK.strip() + '\n<section class="cta">', 1)


def process_file(path: Path) -> dict:
    orig = path.read_text(encoding="utf-8")
    out = orig
    stats = {"corrupted_jsonld": 0, "fabricated_replaced": 0, "faq_tagged": 0, "sources_added": False}

    # 1. JSON-LD corruption
    new_out, n = CORRUPTED_RE.subn(CORRUPTED_FIX, out)
    stats["corrupted_jsonld"] = n
    out = new_out

    # 2. Fabricated provenance
    for pat, repl in FABRICATED_PATTERNS:
        out, n = pat.subn(repl, out)
        stats["fabricated_replaced"] += n

    # 3. FAQ caveat
    new_out, n = FAQ_VALUE_RE.subn(FAQ_FIX, out)
    stats["faq_tagged"] = n
    out = new_out

    # 4. Sources block
    if "Sources &amp; methodology" not in out:
        out = insert_sources_block(out)
        stats["sources_added"] = True

    if out != orig:
        path.write_text(out, encoding="utf-8")
        stats["written"] = True
    else:
        stats["written"] = False
    return stats


def main():
    if not BENCH.exists():
        print(f"ERROR: {BENCH} not found", file=sys.stderr)
        return 1

    # All .html files directly under benchmarks/ (the primary pages)
    files = sorted(BENCH.glob("*.html"))
    # Plus the twin index.html pages one level down
    files += sorted(BENCH.glob("*/index.html"))

    total = {"files": 0, "changed": 0, "corrupted_jsonld": 0, "fabricated": 0, "faq": 0, "sources": 0}
    for f in files:
        if not f.is_file():
            continue
        total["files"] += 1
        s = process_file(f)
        if s.get("written"):
            total["changed"] += 1
        total["corrupted_jsonld"] += s["corrupted_jsonld"]
        total["fabricated"] += s["fabricated_replaced"]
        total["faq"] += s["faq_tagged"]
        total["sources"] += 1 if s["sources_added"] else 0
        marker = "✓ fixed" if s.get("written") else "  ok "
        print(f"  {marker}  {f.relative_to(ROOT)}  "
              f"(jsonld={s['corrupted_jsonld']} fab={s['fabricated_replaced']} "
              f"faq={s['faq_tagged']} sources={'+' if s['sources_added'] else '-'})")

    print()
    print(f"Scanned {total['files']} files. Changed {total['changed']}.")
    print(f"  Corrupted JSON-LD @context fixed: {total['corrupted_jsonld']}")
    print(f"  Fabricated provenance claims replaced: {total['fabricated']}")
    print(f"  FAQ answers tagged with source caveat: {total['faq']}")
    print(f"  Sources & methodology sections added: {total['sources']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
