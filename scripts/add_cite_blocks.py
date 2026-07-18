#!/usr/bin/env python3
"""
Add a "Cite this page" block to every benchmark page.

Each block shows a suggested citation format + copyable snippet. Turns
each benchmark from a wall of text into a citable reference — critical
for earning third-party links and AI citations (the benchmarks-reframe.md
explicitly calls for this: 'Package each benchmark as a linkable, quotable
stat card... Add a cite this / embed this block').

Run from ~/churnlens. Idempotent — skips pages already having the block.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CITATION_BLOCK = """
<section class=\"cite-this\" style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:1.25rem;margin:2rem 0;font-size:0.9rem;line-height:1.6\">
<h2 style=\"font-size:1.1rem;border:none;margin-top:0\">📎 Cite this page</h2>
<p style=\"margin:0 0 0.5rem;color:#64748b;font-size:0.85rem\">Copy the citation below or link to this page. These benchmarks are curated from public SaaS research, not original ChurnLens data — attribute the primary source when citing specific figures.</p>
<div style=\"background:white;border:1px solid #e2e8f0;border-radius:6px;padding:0.75rem 1rem;font-family:monospace;font-size:0.82rem;color:#334155;overflow-x:auto;white-space:pre-wrap;word-break:break-all\">
ChurnLens. ({YEAR}). <em>{TITLE}</em>. Retrieved from {URL}
</div>
<button onclick=\"navigator.clipboard.writeText(this.previousElementSibling.innerText)\" style=\"margin-top:0.5rem;padding:6px 14px;font-size:0.8rem;background:#0066cc;color:white;border:none;border-radius:6px;cursor:pointer\">📋 Copy citation</button>
<span class=\"copy-msg\" style=\"display:none;margin-left:8px;color:#16a34a;font-size:0.8rem\">Copied!</span>
<script>(function(b){{b.addEventListener('click',function(){{var s=b.nextElementSibling;s.style.display='inline';setTimeout(function(){{s.style.display='none'}},2000)}})}})(document.currentScript.previousElementSibling)</script>
</section>
"""


def get_page_title(path: Path) -> str:
    """Extract the <title> or <h1> text."""
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
        if m:
            t = m.group(1).strip()
            # Strip common suffixes
            t = re.sub(r'\s*\[\d{4}.*?\]\s*$', '', t)
            t = re.sub(r'\s*\|\s*ChurnLens\s*$', '', t, flags=re.IGNORECASE)
            return t
        m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return path.stem.replace("-", " ").title()


def get_url(path: Path) -> str:
    """Derive URL from file path."""
    rel = str(path.relative_to(ROOT))
    # Remove index.html or .html
    rel = re.sub(r"/index\.html$", "/", rel)
    rel = re.sub(r"\.html$", "", rel)
    return f"https://churnlens.site/{rel}"


def process_file(path: Path) -> bool:
    if "Cite this page" in path.read_text(encoding="utf-8", errors="ignore"):
        return False  # already done

    title = get_page_title(path)
    url = get_url(path)
    year = "2026"

    block = CITATION_BLOCK.format(TITLE=title, URL=url, YEAR=year)

    html = path.read_text(encoding="utf-8", errors="ignore")

    # Insert before </article> or before <footer> or at end of <body>
    if "</article>" in html:
        html = html.replace("</article>", block + "\n</article>", 1)
    elif "<footer>" in html:
        html = html.replace("<footer>", block + "\n<footer>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", block + "\n</body>", 1)
    else:
        return False

    path.write_text(html, encoding="utf-8")
    return True


def main():
    bench_dir = ROOT / "benchmarks"
    if not bench_dir.exists():
        print("benchmarks/ directory not found")
        return 1

    done = 0
    skipped = 0
    for f in sorted(bench_dir.glob("*.html")):
        if process_file(f):
            print(f"  ✓  {f.relative_to(ROOT)}")
            done += 1
        else:
            skipped += 1

    print(f"\nAdded cite block to {done} pages. {skipped} already had it or were skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
