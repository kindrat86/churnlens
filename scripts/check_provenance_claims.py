#!/usr/bin/env python3
"""
Fail on first-party-data claims this site cannot back.

WHY THIS EXISTS
---------------
churnlens.site has now had THREE waves of the same defect: pages asserting that
benchmark figures were measured from ChurnLens's own customers.
  wave 1  "2,400+ SaaS companies" / "analysis of thousands of SaaS businesses"
  wave 2  "aggregated anonymized user data. Updated quarterly"
  wave 3  "ChurnLens analysis of buyer-side CSV uploads, 2024-2026" (+ the CC BY
          CSV, and "thousands of buyer-side CSV uploads processed through
          ChurnLens")

There is no first-party corpus and there cannot be one: api/ has no upload
endpoint, and the free analyzer reads the file with FileReader and makes zero
fetch/XHR/sendBeacon calls, so an uploaded CSV never leaves the browser.

Wave 3 survived the wave-1/2 cleanup for two reasons, both fixed here:
  * scripts/fix_benchmark_provenance.py globbed only `benchmarks/*.html`; the
    flagship page and the CSV live at the REPO ROOT and were never in scope.
  * the documented gate matched only the literal strings "2,400" and "thousands
    of SaaS", so "thousands of buyer-side CSV uploads" sailed straight through.

DESIGN NOTE - why these patterns are assertion-shaped, not keywords
-------------------------------------------------------------------
The honest replacement copy legitimately contains "uploaded CSVs", "customer
data" and "ChurnLens", e.g.:

    "not measured from ChurnLens customer data or uploaded CSVs"

A keyword gate on those words would fire on the disclaimer that fixes the bug -
the worst possible failure mode, because it trains people to add exceptions.
So every pattern below matches a CLAIM OF MEASUREMENT ("we've observed", "our
analysis of", "aggregated data from"), never a subject noun. Denials are
additionally skipped via NEGATED_BY.

Usage:
    python3 scripts/check_provenance_claims.py            # scan served surfaces
    python3 scripts/check_provenance_claims.py --root DIR # scan an export
Exit 0 = clean, 1 = a claim was found.
"""
import argparse
import re
import sys
from pathlib import Path

# Directories that are never served (.vercelignore) - scanning them produces
# noise, not risk. i18n IS scanned: it feeds any future localized build.
SKIP_DIRS = {".git", "node_modules", "dist", ".vercel", "i18n_out"}

SCAN_SUFFIXES = {".html", ".csv", ".json", ".md", ".txt"}
# Internal docs legitimately DISCUSS the fabrications (audits, this repo's own
# CLAUDE.md, task files). They are .vercelignore'd and never served.
SKIP_NAMES = re.compile(
    r"^(CLAUDE\.md|HERMES_.*\.md|REPORT_.*\.md|OWNER_.*\.md|.*AUDIT.*\.md|"
    r".*SCORECARD.*\.md|.*\.py)$"
)

# A claim only counts if it is NOT inside a denial. "not measured from X",
# "never derived from X", "no first-party data" are the honest form.
NEGATED_BY = re.compile(
    r"\b(not|never|no|without|isn't|aren't|rather than|instead of)\b[^.]{0,80}$",
    re.IGNORECASE,
)

PATTERNS = [
    # --- claims of first-party observation --------------------------------
    (r"we(?:'ve| have| had)? observed", "claims first-party observation"),
    (r"\bwe analy[sz]ed\b", "claims first-party analysis"),
    # NOT a bare "our analysis of" - that is how the site cross-links its own
    # articles ("See our analysis of inactive paid accounts"). Only fire when
    # the object is DATA-shaped.
    (
        r"\b(?:our|ChurnLens'?s?) analysis of\s+(?:[\d,]+|thousands|hundreds|buyer-side|"
        r"customer|user|subscription|uploaded|anonymi|aggregated)",
        "claims first-party analysis of a data corpus",
    ),
    (r"\banalysis of thousands\b", "claims first-party analysis at volume"),
    (r"\bprocessed through Churn ?Lens\b", "claims a processing corpus"),
    (r"\bour (?:dataset|data set|corpus|customer base|user base)\b", "claims a first-party corpus"),
    (r"\bour proprietary\b", "claims proprietary data"),
    # NOT a bare "across our" - the portfolio pages legitimately say "across our
    # portfolio ecosystem". Only fire on a POPULATION noun.
    (
        r"\bacross our\s+(?:customers|users|accounts|dataset|data set|corpus|"
        r"customer base|user base|uploads)\b",
        "claims a first-party population",
    ),
    # --- aggregate-volume claims ------------------------------------------
    (r"\baggregated (?:anonymi[sz]ed|data|figures)", "claims aggregated first-party data"),
    (r"\bbased on (?:aggregated|data from|our)\b", "claims a measured basis"),
    (r"\bdrawn from (?:our|thousands|hundreds)\b", "claims a measured basis"),
    (r"\bdata from (?:over |more than )?[\d,]+\+?\s*(?:SaaS|compan|business|team|customer)", "cites an invented sample size"),
    # Deliberately NOT a bare "N+ SaaS": review pages legitimately state a
    # THIRD party's customer count ("Baremetrics ... used by 900+ SaaS
    # companies"). That is a sourcing question, not a first-party-data claim.
    # Only the wave-1 literal is kept, as a named regression guard.
    (r"2,400\+?\s*(?:SaaS|compan|business)", "wave-1 fabricated sample size"),
    (r"\bthousands of\s+(?:SaaS|compan|business|buyer-side|CSV|upload|customer)", "claims volume it cannot have"),
    (r"\b(?:hundreds|thousands) of (?:uploads|files|datasets)\b", "claims volume it cannot have"),
    # --- specific literals from prior waves (keep: cheap regression guard) --
    (r"\btrusted by\b", "unearned social proof"),
    (r"\bupdated quarterly\b", "implies an ongoing measurement cadence"),
    (r"\banonymi[sz]ed user data\b", "claims first-party user data"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), why) for p, why in PATTERNS]


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if SKIP_NAMES.match(p.name):
            continue
        yield p


def scan(root: Path):
    hits = []
    for f in iter_files(root):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for rx, why in COMPILED:
                for m in rx.finditer(line):
                    before = line[: m.start()]
                    if NEGATED_BY.search(before):
                        continue  # "not measured from ..." - the honest form
                    hits.append((f.relative_to(root), lineno, m.group(0).strip(), why))
                    break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    hits = scan(root)
    if not hits:
        print("[check_provenance_claims] OK - no unbacked first-party-data claims")
        return 0

    print(f"[check_provenance_claims] FAIL - {len(hits)} claim(s) this site cannot back:\n")
    for path, lineno, match, why in hits:
        print(f"  {path}:{lineno}\n      matched {match!r} - {why}")
    print(
        "\nThere is no first-party corpus: api/ has no upload endpoint and the free\n"
        "analyzer never transmits the file. Either cite a real external source with a\n"
        "link, or label the figure an editorial estimate. See\n"
        "scripts/fix_uploads_corpus_provenance.py for the wave-3 fix shape."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
