#!/usr/bin/env python3
"""Move the free-tool opt-in from the page footer to the moment the result lands.

scripts/inject_freetool_optin.py placed the block immediately before <footer>,
which on these pages is roughly 70% down a very long article. Measured live on
/free/churn-calculator: the result renders at ~y=755 and the opt-in sat at
y=10,850 on a 15,561px page — about ten screens after the reader got the number
they came for. The block's own eyebrow reads "You just ran the numbers", which is
simply false that far down.

The ask belongs where belief peaks: directly under the tool's output, before the
long-form SEO body starts.

Each of these ten tools is hand-built with its own markup, so there is no single
selector that works everywhere. The anchor is resolved per tool, in order:

  1. `<div class="cta">`  — five tools already have a post-tool CTA block sitting
     exactly where we want to be; insert immediately before it.
  2. an explicit per-tool anchor (below) for the rest.

Anything not matched is left alone and reported rather than guessed at.

Usage:  python3 scripts/move_freetool_optin_to_result.py [--apply]
"""
import glob
import os
import re
import sys

OPEN_SECTION = '<section class="cl-tool-optin"'
END_SECTION = "</section>"

# Tools without a `.cta` block. Value = a literal that begins the first element
# AFTER the interactive area; the opt-in is inserted immediately before it.
EXPLICIT_ANCHORS = {
    # The export/print button row ends the analyzer; "How to use it" starts the prose.
    "saas-churn-analyzer": '<h2 id="howto">',
    # The simulator's own bottom CTA sits right after the last result card
    # (#actionsCard); it is named cta-bottom, so the generic `class="cta"` probe
    # does not match it.
    "due-diligence-simulator": '<div class="cta-bottom"',
    "ltv-calculator": None,   # resolved dynamically from the results container
    "mrr-health-check": None,
}

# For the two calculators whose output is a bare hero div, close the div that
# holds the hero and insert after it.
HERO_IDS = {"ltv-calculator": "ltvHero", "mrr-health-check": "mrrHero"}


def extract_block(html):
    """Cut the opt-in section out; return (html_without, block) or (html, None)."""
    s = html.find(OPEN_SECTION)
    if s == -1:
        return html, None
    # The block is section + its trailing <script>. Take through the script close.
    e = html.find(END_SECTION, s)
    if e == -1:
        return html, None
    e += len(END_SECTION)
    script_start = html.find("<script>", e)
    if script_start != -1 and script_start - e < 8:
        e = html.find("</script>", script_start) + len("</script>")
    # Include the leading HTML comment the injector wrote.
    c = html.rfind("<!-- cl-tool-optin", 0, s)
    if c != -1 and s - c < 400:
        s = c
    return html[:s] + html[e:], html[s:e]


def close_of_div(html, open_idx):
    """Index just past the </div> matching the <div ...> starting at open_idx."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[open_idx:]):
        if m.group(0) == "</div>":
            depth -= 1
            if depth == 0:
                return open_idx + m.end()
        else:
            depth += 1
    return -1


def anchor_for(slug, html):
    """Byte offset at which the opt-in should be inserted, or -1."""
    cta = html.find('<div class="cta"')
    if cta != -1:
        return cta
    if slug in HERO_IDS:
        hid = HERO_IDS[slug]
        m = re.search(r'<div[^>]*id="%s"' % re.escape(hid), html)
        if m:
            # step out to the enclosing card so we land after the whole result
            end = close_of_div(html, m.start())
            if end != -1:
                return end
    lit = EXPLICIT_ANCHORS.get(slug)
    if lit:
        i = html.find(lit)
        if i != -1:
            return i
    return -1


def main():
    apply = "--apply" in sys.argv
    moved, skipped = [], []
    for path in sorted(glob.glob("free/*/index.html")):
        slug = os.path.basename(os.path.dirname(path))
        html = open(path, encoding="utf-8").read()
        if OPEN_SECTION not in html:
            continue
        stripped, block = extract_block(html)
        if not block:
            skipped.append((slug, "could not isolate block"))
            continue
        at = anchor_for(slug, stripped)
        if at == -1:
            skipped.append((slug, "no anchor found — left in place"))
            continue
        was = html.find(OPEN_SECTION)
        new = stripped[:at] + block + "\n\n" + stripped[at:]
        moved.append((slug, was, at, was - at))
        if apply:
            open(path, "w", encoding="utf-8").write(new)

    print("MODE:", "APPLY" if apply else "DRY RUN")
    print("\n%-32s %8s %8s %10s" % ("TOOL", "WAS@", "NOW@", "MOVED UP"))
    for slug, was, now, delta in moved:
        print("%-32s %8d %8d %10d" % (slug, was, now, delta))
    if skipped:
        print("\nNOT MOVED:")
        for slug, why in skipped:
            print("  %-30s %s" % (slug, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
