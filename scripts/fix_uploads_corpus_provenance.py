#!/usr/bin/env python3
"""
Fix the "buyer-side CSV uploads" provenance fabrication on the flagship
benchmarks page + its CC BY 4.0 dataset.

WHY THIS SURVIVED THE EARLIER CLEANUP
-------------------------------------
scripts/fix_benchmark_provenance.py (2026-07) fixed this same defect class, but
it globbed only `benchmarks/*.html` and `benchmarks/*/index.html`. The flagship
page lives at the repo ROOT (saas-churn-rate-benchmarks.html + its served
directory twin) and the CSV at the root too, so both were out of that script's
scope and kept their fabricated provenance.

WHAT WAS FALSE
--------------
Three claims, all asserting a measured upload corpus that does not exist:

  1. CSV footer:  "Source: ChurnLens analysis of buyer-side CSV uploads,
                   2024-2026."
  2. Page body:   "These are the medians we've observed across thousands of
                   buyer-side CSV uploads processed through ChurnLens."
  3. Page TL;DR:  "ChurnLens benchmarks every uploaded CSV against 14 industry
                   verticals automatically."

Evidence that no such corpus exists or could exist:
  * No upload endpoint. api/ is a2a, mcp, nlweb, oembed, subscribe, unsubscribe.
    The only inbound data path is an email opt-in to Resend.
  * The free analyzer (free/saas-churn-analyzer/index.html) contains zero
    fetch/XHR/sendBeacon calls - uploaded CSVs never leave the browser, so they
    are not observable server-side even in principle.
  * Organization JSON-LD foundingDate is 2026-01-15. A "2024-2026" analysis
    window predates the company by two years.
  * The CSV was hand-authored in a single commit (5b645fd, +16 lines). The 14
    sector bands appear nowhere else in the repo - no pipeline, no raw data, no
    computation produces them.
  * Claim 3 is unbacked by any product surface: the analyzer has no sector
    benchmarking logic at all ("14 industry verticals" appears only in the two
    copies of this one sentence).

THE FIX
-------
The ranges stay - they are defensible as editorial estimates. Only the
attribution changes: from "measured from our uploads" to "editorial estimates
compiled from public benchmarking research", with the two source URLs already
used elsewhere in this repo (both verified 200 on 2026-07-25).

Deliberately NOT attributed wholesale to those sources: no public source
publishes monthly churn for all 14 of these segments (Proptech, Compliance /
LegalTech, EdTech B2B are not standard published cuts). Claiming they were
"derived from SaaS Capital / Recurly" would swap one fabrication for another, so
the copy says plainly which parts are judgement.

Idempotent. Run from ~/churnlens: python3 scripts/fix_uploads_corpus_provenance.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RECURLY = "https://recurly.com/research/churn-rate-benchmarks/"
SAAS_CAPITAL = (
    "https://www.saas-capital.com/wp-content/uploads/2023/05/"
    "RB28WS1-2023-B2B-SaaS-Retention-Benchmarks.pdf"
)
REVIEWED = "25 July 2026"

PAGES = ["saas-churn-rate-benchmarks.html", "saas-churn-rate-benchmarks/index.html"]
CSV = "saas-churn-benchmarks-2026.csv"

# --- 1. page body sentence (claim 2) ---------------------------------------
# `we\'ve` appears in i18n/all_keys.py (apostrophe backslash-escaped inside a
# triple-quoted Python string), so the apostrophe match must tolerate a
# preceding backslash or it silently misses that file.
BODY_RE = re.compile(
    r"These are the medians we\\?'ve observed across thousands of buyer-side "
    r"CSV uploads processed through Churn ?Lens\."
)
BODY_FIX = (
    "The bands below are <strong>ChurnLens editorial estimates</strong> "
    "&mdash; indicative sector ranges compiled from public SaaS benchmarking "
    "research, <em>not</em> measured from ChurnLens customer data or uploaded "
    'CSVs. See <a href="#sources">Sources &amp; methodology</a>.'
)
# plain-text variant for i18n JSON (no markup in translation strings)
BODY_FIX_TEXT = (
    "The bands below are ChurnLens editorial estimates - indicative sector "
    "ranges compiled from public SaaS benchmarking research, not measured from "
    "ChurnLens customer data or uploaded CSVs."
)

# --- 2. page TL;DR sentence (claim 3) -------------------------------------
TLDR_RE = re.compile(
    r"Churn ?Lens benchmarks every uploaded CSV against 14 industry verticals "
    r"automatically\."
)
TLDR_FIX = (
    "The 14 sector bands on this page are editorial estimates compiled from "
    "public research, not measured ChurnLens data."
)

# --- 3. Dataset JSON-LD: state the method machine-readably ----------------
LICENSE_KEY = '"license":"https://creativecommons.org/licenses/by/4.0/"'
JSONLD_PROVENANCE = (
    '"measurementTechnique":"Editorial estimate compiled from public SaaS '
    'benchmarking research; not measured from customer data or uploaded files",'
    '"citation":['
    '{"@type":"CreativeWork","name":"Recurly - Churn Rate Benchmarks","url":"'
    + RECURLY
    + '"},'
    '{"@type":"CreativeWork","name":"SaaS Capital - B2B SaaS Retention '
    'Benchmarks","url":"' + SAAS_CAPITAL + '"}'
    "],"
)

# --- 4. Sources & methodology block ---------------------------------------
SOURCES_BLOCK = f"""    <!-- Sources & methodology -->
    <div id="sources" style="max-width:720px;margin:2rem auto;padding:1.25rem 1.5rem;background:#1e293b;border:1px solid #334155;border-radius:0.75rem;font-size:0.9rem;color:#94a3b8;line-height:1.7;">
      <strong style="color:#e2e8f0;">Sources &amp; methodology</strong>
      <p style="margin:0.75rem 0 0;">The sector bands on this page and in the downloadable CSV are <strong style="color:#e2e8f0;">ChurnLens editorial estimates</strong>: indicative ranges compiled and rounded from publicly available SaaS benchmarking research, then grouped into the 14 buyer-side segments we use in due diligence. They are <em>not</em> derived from ChurnLens customer data and <em>not</em> from uploaded CSVs &mdash; the <a href="/free/saas-churn-analyzer" style="color:var(--cl-blue-light);">free analyzer</a> runs entirely in your browser and never transmits a file.</p>
      <p style="margin:0.75rem 0 0.25rem;">Primary public references:</p>
      <ul style="margin:0 0 0.75rem;padding-left:1.25rem;">
        <li><a href="{RECURLY}" rel="nofollow noopener" target="_blank" style="color:var(--cl-blue-light);">Recurly &mdash; Churn Rate Benchmarks</a> &mdash; logo vs revenue churn, voluntary vs involuntary split.</li>
        <li><a href="{SAAS_CAPITAL}" rel="nofollow noopener" target="_blank" style="color:var(--cl-blue-light);">SaaS Capital &mdash; B2B SaaS Retention Benchmarks</a> &mdash; retention and revenue churn by ARR band.</li>
      </ul>
      <p style="margin:0;">No public source publishes monthly churn for every one of these 14 segments; where direct data was unavailable the band reflects our own judgement and is widened to show that uncertainty. Distinguish <em>logo churn</em> from <em>revenue churn</em>, and <em>monthly</em> from <em>annual</em>, when comparing &mdash; conflating them is the most common benchmark error. Treat any figure here as a starting hypothesis to verify against a primary source, never as a measured value. <em>Last reviewed {REVIEWED}.</em></p>
    </div>

"""
CITE_ANCHOR = "    <!-- Cite this data -->"

# --- 5. CSV footer (claim 1) ---------------------------------------------
CSV_OLD_PREFIX = "Source: ChurnLens analysis of buyer-side CSV uploads"
CSV_NEW = (
    '"Source: ChurnLens editorial estimates - indicative sector bands compiled '
    "from public SaaS benchmarking research (Recurly, "
    + RECURLY
    + "; SaaS Capital, "
    + SAAS_CAPITAL
    + "). NOT measured from ChurnLens customer data or uploaded CSVs. No public "
    "source covers all 14 segments; where direct data was unavailable the band "
    "is editorial judgement. Verify against a primary source before use. Last "
    "reviewed 2026-07-25. Methodology: "
    'https://churnlens.site/saas-churn-rate-benchmarks#sources"\n'
    '"Licence: CC BY 4.0 - cite as ChurnLens (churnlens.site), ""SaaS Churn '
    'Rate Benchmarks by Industry"", 2026."\n'
)


def fix_page(path: Path) -> list:
    orig = path.read_text(encoding="utf-8")
    out, done = orig, []

    out, n = BODY_RE.subn(BODY_FIX, out)
    if n:
        done.append(f"body claim x{n}")
    out, n = TLDR_RE.subn(TLDR_FIX, out)
    if n:
        done.append(f"tldr claim x{n}")

    if '"measurementTechnique"' not in out and LICENSE_KEY in out:
        out = out.replace(LICENSE_KEY, JSONLD_PROVENANCE + LICENSE_KEY, 1)
        done.append("jsonld provenance")

    if 'id="sources"' not in out and CITE_ANCHOR in out:
        out = out.replace(CITE_ANCHOR, SOURCES_BLOCK + CITE_ANCHOR, 1)
        done.append("sources block")

    if out != orig:
        path.write_text(out, encoding="utf-8")
    return done


def fix_csv(path: Path) -> list:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [ln for ln in lines if CSV_OLD_PREFIX not in ln]
    if len(kept) == len(lines):
        return []
    if not kept[-1].endswith("\n"):
        kept[-1] += "\n"
    path.write_text("".join(kept) + CSV_NEW, encoding="utf-8")
    return ["csv footer"]


def fix_i18n(root: Path) -> list:
    """Replace the claim in translation sources so it cannot resurface in a
    localized build. i18n/ is .vercelignore'd today, but these files are the
    input to any future localized page."""
    changed = []
    targets = sorted(root.glob("i18n/locales/*/*.json"))
    targets += [
        root / "i18n/translations/_en_reference.json",
        root / "i18n/all_keys.txt",
        root / "i18n/all_keys.py",
        root / "i18n/en_flat.txt",
        root / "i18n_out/en/saas-churn-rate-benchmarks.html",
    ]
    for f in targets:
        if not f.is_file():
            continue
        orig = f.read_text(encoding="utf-8")
        # JSON/py/txt carry the sentence escaped or bare; the regex is markup-free
        repl = BODY_FIX if f.suffix == ".html" else BODY_FIX_TEXT
        out, n = BODY_RE.subn(repl, orig)
        out, n2 = TLDR_RE.subn(TLDR_FIX, out)
        if out != orig:
            f.write_text(out, encoding="utf-8")
            changed.append(f"{f.relative_to(root)} (body x{n}, tldr x{n2})")
    return changed


def main() -> int:
    total = 0
    for rel in PAGES:
        p = ROOT / rel
        if not p.is_file():
            print(f"  MISSING  {rel}", file=sys.stderr)
            return 1
        done = fix_page(p)
        total += len(done)
        print(f"  {'fixed' if done else 'ok   '}  {rel}  {', '.join(done) or '(already clean)'}")

    p = ROOT / CSV
    done = fix_csv(p)
    total += len(done)
    print(f"  {'fixed' if done else 'ok   '}  {CSV}  {', '.join(done) or '(already clean)'}")

    i18n = fix_i18n(ROOT)
    total += len(i18n)
    print(f"\n  i18n translation sources cleaned: {len(i18n)}")
    for c in i18n:
        print(f"    - {c}")

    # verification: the fabricated phrases must be gone from served surfaces
    leaks = []
    for rel in PAGES + [CSV]:
        t = (ROOT / rel).read_text(encoding="utf-8")
        if "buyer-side CSV uploads" in t or "14 industry verticals" in t:
            leaks.append(rel)
    if leaks:
        print(f"\nFAIL: claim still present in {leaks}", file=sys.stderr)
        return 1
    print(f"\nOK - {total} edits. No upload-corpus claim remains on served surfaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
