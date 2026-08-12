#!/usr/bin/env python3
"""Release gate: a CTA must not promise something different from where it goes.

Two failures shipped to production and stayed live for weeks, and neither is
visible to a link checker, because both links returned HTTP 200:

1. **Label/destination mismatch.** 418 anchors across 194 deployed pages
   promised the lead magnet ("Get the Free Checklist →", 343 of them containing
   the word *free*) and linked to a Stripe card form for "ChurnLens Churn
   Analysis — one-time, $9.00". Cold traffic was asked for a card on first
   click, the squeeze page got zero inbound links from the pSEO body of the
   site, and the email list stayed empty. Nothing was broken — every component
   worked, and the funnel was simply routed around.

2. **A second payment link for the same offer.** /sample-churn-risk-report — the
   highest-intent page in the funnel — carried `5kQdR8ax52d20W25rO0x20v`, which
   Stripe answers with "The link is no longer active." Everyone who read the
   proof asset and decided to buy hit a wall. Two links for one $9 offer also
   means a payment cannot be attributed, because there is no webhook.

So this gate asserts two things about the deployed tree:

  A. Every `buy.stripe.com` anchor names its price. If the visible text does not
     contain a price, the anchor is selling something the label does not admit
     to, and it belongs on /get-the-checklist instead.
  B. Exactly one distinct payment link id exists sitewide (ALLOWED_LINKS).

Deliberately NOT checked here: whether the link is live at Stripe. That needs a
network call and would make the gate flaky offline; use the browser or the
Stripe API for that. What this catches is the structural mistake that let a dead
link sit unnoticed — having two of them.

Exit 1 on any violation. Wire into scripts/qa-check.sh.
"""
import os
import re
import sys

# The one live payment link: "ChurnLens Churn Analysis — one-time", $9.00.
ALLOWED_LINKS = {"14AcN4eNl7xmfQW8E00x20w"}

# Not deployed (see .vercelignore), so not this gate's business.
EXCLUDE_DIRS = {".git", "node_modules", ".vercel", ".claude", "dist", "i18n", "i18n_out", "scripts"}

ANCHOR = re.compile(
    r'<a\b[^>]*href="https://buy\.stripe\.com/(?P<id>[^"?/]+)[^"]*"[^>]*>(?P<body>.*?)</a>',
    re.S | re.I,
)
LINK_ID = re.compile(r"buy\.stripe\.com/([A-Za-z0-9_]+)")
# A price the visitor can actually read: "$9", "$ 9", "&#36;9", "— $9 →".
NAMES_A_PRICE = re.compile(r"(\$|&#36;|&dollar;)\s*\d", re.I)


def visible_text(body: str) -> str:
    txt = re.sub(r"<[^>]+>", "", body)
    for ent, ch in (("&mdash;", "—"), ("&rarr;", "→"), ("&nbsp;", " "), ("&amp;", "&")):
        txt = txt.replace(ent, ch)
    return re.sub(r"\s+", " ", txt).strip()


def main() -> int:
    mismatches, unknown_links = [], {}
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            # errors="ignore": free/saas-churn-analyzer/index.html contains a NUL
            # byte inside legitimate JS (a map-key separator), which makes grep
            # treat it as binary and silently skip it.
            try:
                html = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "buy.stripe.com" not in html:
                continue

            for lid in set(LINK_ID.findall(html)):
                if lid not in ALLOWED_LINKS:
                    unknown_links.setdefault(lid, []).append(path)

            for m in ANCHOR.finditer(html):
                txt = visible_text(m.group("body"))
                if not NAMES_A_PRICE.search(txt):
                    mismatches.append((path, txt or "(no visible text)"))

    problems = 0

    if mismatches:
        problems += len(mismatches)
        print("[check_payment_links] FAIL - %d checkout link(s) whose label hides the price:\n"
              % len(mismatches))
        for path, txt in mismatches[:25]:
            print("  %s\n      label: %r" % (path, txt[:70]))
        if len(mismatches) > 25:
            print("  ... and %d more" % (len(mismatches) - 25))
        print("\n  A CTA that sends a visitor to a card form must say so. If the label"
              "\n  promises the free checklist, point it at /get-the-checklist instead.\n")

    if unknown_links:
        problems += len(unknown_links)
        print("[check_payment_links] FAIL - %d payment link id(s) not in the allowlist:\n"
              % len(unknown_links))
        for lid, paths in unknown_links.items():
            print("  %s  (%d file(s), e.g. %s)" % (lid, len(paths), paths[0]))
        print("\n  One offer, one link. A second link for the same offer is how"
              "\n  5kQdR8ax52d20W25rO0x20v went dead on /sample-churn-risk-report"
              "\n  without anyone noticing. Add it to ALLOWED_LINKS only if it is a"
              "\n  genuinely different, live product.\n")

    if problems:
        return 1
    print("[check_payment_links] OK - every checkout CTA names its price; one payment link sitewide")
    return 0


if __name__ == "__main__":
    sys.exit(main())
