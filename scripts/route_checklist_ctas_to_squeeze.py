#!/usr/bin/env python3
"""Route checklist CTAs to the squeeze page instead of the paid Stripe checkout.

WHY
---
436 anchors across the deployed tree pointed at the $9 Stripe payment link
(`14AcN4eNl7xmfQW8E00x20w`). 343 of them were labelled with the word *free*
("Get the Free Checklist", "Free Checklist", "Get the free 23-point checklist"),
and another 75 promised "the checklist" without naming a price. Clicking any of
them landed the visitor on a card form for "ChurnLens Churn Analysis — one-time,
$9.00".

Meanwhile `/get-the-checklist` — the squeeze page that actually delivers the
checklist for an email address, adds the contact to the Resend audience, and
starts the 10-email sequence — received **zero** inbound links from the pSEO
body of the site. Only the homepage linked to it.

That is the whole lead-capture engine bypassed: no opt-ins, so no list, so the
soap-opera sequence never fires, so nothing ever ascends the value ladder. It
also asks cold organic traffic for a card on first click.

The same URL was pasted as plain text into affiliate/partner swipe copy
("The tool is free to start: https://buy.stripe.com/...") and into a JSON-LD
FAQ answer ("Download it at buy.stripe.com/...") that is served to Google and
AI answer engines. Those are rewritten too.

WHAT THIS CHANGES
-----------------
* Anchor whose text names the price or the paid deliverable ($9 / "analysis")
  -> KEPT on Stripe. That CTA is honest and is the self-liquidating offer.
* Every other checklist anchor -> `/get-the-checklist`.
* Plain-text/JSON-LD mentions of the payment URL -> `https://churnlens.site/get-the-checklist`.
* The dead payment link `5kQdR8ax52d20W25rO0x20v` (Stripe returns "The link is
  no longer active") on /sample-churn-risk-report -> the live `$9` link. That
  page's CTA reads "Get your analysis — $9", so it stays a paid CTA; it just
  has to point at a link that still works.

Edits are surgical in-place `href` swaps. Nothing is regenerated from a template
(bare regeneration strips PostHog + hreflang — see CLAUDE.md).

Usage:  python3 scripts/route_checklist_ctas_to_squeeze.py [--apply]
Default is a dry run.
"""
import os
import re
import sys
import collections

LIVE_PAY = "https://buy.stripe.com/14AcN4eNl7xmfQW8E00x20w"
DEAD_PAY = "https://buy.stripe.com/5kQdR8ax52d20W25rO0x20v"
SQUEEZE = "/get-the-checklist"
SQUEEZE_ABS = "https://churnlens.site/get-the-checklist"

# Directories that are never deployed (see .vercelignore) or are not ours.
EXCLUDE_DIRS = {".git", "node_modules", ".vercel", ".claude", "dist"}
# i18n sources are not deployed, but they are the templates future pages are
# generated from, so they are rewritten too — otherwise the bug regenerates.
TEMPLATE_DIRS = {"i18n", "i18n_out"}

ANCHOR = re.compile(
    r'<a\b(?P<attrs>[^>]*?)href="(?P<href>https://buy\.stripe\.com/[^"]+)"(?P<rest>[^>]*)>(?P<body>.*?)</a>',
    re.S | re.I,
)
# The anchor text that legitimately sells the paid one-off analysis.
PAID_INTENT = re.compile(r"\$\s*9|&#36;\s*9|\banalys(is|e)\b", re.I)
# Untranslated i18n placeholders carry no text to judge; keep them on Stripe
# only when the English base for that slot is a paid CTA. Handled by caller.
PLACEHOLDER = re.compile(r"^__TR_[\w.\-]+__$")


def anchor_text(body: str) -> str:
    txt = re.sub(r"<[^>]+>", "", body)
    txt = txt.replace("&mdash;", "—").replace("&rarr;", "→").replace("&#36;", "$")
    return re.sub(r"\s+", " ", txt).strip()


# Paid CTAs we deliberately keep are parked behind this sentinel while the
# plain-text pass runs, then restored. Without it, the blanket URL replace below
# would strip the $9 checkout off /oto, /pricing, the squeeze page's inline OTO
# and the sample report — i.e. it would delete the only working checkout on the
# site while "fixing" the CTAs.
KEEP_SENTINEL = "\x00CHURNLENS_KEEP_PAID\x00"


def rewrite(html: str, stats: collections.Counter, path: str):
    """Return (new_html, changed_count)."""
    changed = 0

    def sub_anchor(m):
        nonlocal changed
        txt = anchor_text(m.group("body"))
        href = m.group("href")
        paid = bool(PAID_INTENT.search(txt))
        if PLACEHOLDER.match(txt):
            # Untranslated slot. The English bases for these are checklist CTAs
            # (verified: every __TR_ slot on a stripe anchor renders a checklist
            # label in i18n_out/en), so they route to the squeeze page.
            paid = False
            stats["placeholder"] += 1
        if paid:
            if href == DEAD_PAY:
                changed += 1
                stats["dead_link_revived"] += 1
            stats["kept_paid"] += 1
            return m.group(0).replace('href="%s"' % href, 'href="%s"' % KEEP_SENTINEL, 1)
        changed += 1
        stats["routed_to_squeeze"] += 1
        stats["label:" + txt[:48]] += 1
        return m.group(0).replace('href="%s"' % href, 'href="%s"' % SQUEEZE, 1)

    html = ANCHOR.sub(sub_anchor, html)

    # Plain-text / JSON-LD mentions left over (swipe copy, FAQ answers, og tags).
    for url in (LIVE_PAY, DEAD_PAY):
        bare = url.replace("https://", "")
        if url in html:
            n = html.count(url)
            html = html.replace(url, SQUEEZE_ABS)
            changed += n
            stats["plaintext_url"] += n
        if bare in html:
            n = html.count(bare)
            html = html.replace(bare, "churnlens.site/get-the-checklist")
            changed += n
            stats["plaintext_url"] += n

    html = html.replace(KEEP_SENTINEL, LIVE_PAY)
    return html, changed


def main():
    apply = "--apply" in sys.argv
    stats = collections.Counter()
    touched = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            try:
                html = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "buy.stripe.com" not in html:
                continue
            new, changed = rewrite(html, stats, path)
            if changed:
                touched.append((path, changed))
                if apply:
                    open(path, "w", encoding="utf-8").write(new)

    print("MODE:", "APPLY" if apply else "DRY RUN")
    print("files changed:", len(touched))
    print("anchors routed to squeeze page:", stats["routed_to_squeeze"])
    print("paid $9 CTAs kept on Stripe:", stats["kept_paid"])
    print("dead-link CTAs repointed to the live $9 link:", stats["dead_link_revived"])
    print("plain-text / JSON-LD URL mentions rewritten:", stats["plaintext_url"])
    print("untranslated __TR_ slots routed:", stats["placeholder"])
    print()
    print("labels routed (top 20):")
    for k, v in stats.most_common():
        if k.startswith("label:"):
            print("  %4d  %s" % (v, k[6:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
