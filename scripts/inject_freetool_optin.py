#!/usr/bin/env python3
"""Add a lead-capture step to the free calculators.

WHY
---
Ten free tools compute a real answer for a buyer mid-diligence — zombie MRR,
NRR, concentration, revenue health — and then ask for nothing. Before this,
exactly ONE page on the whole site had an email field (`/get-the-checklist`).
Everything else either dead-ended or pushed straight to a $9 card form.

In DotCom Secrets terms these tools ARE the bait (Secret 13) and they were being
given away with no hook, so the owned list (Secret 5) could never grow and the
follow-up sequence (Secret 7) had nobody to talk to.

WHAT THIS ADDS
--------------
One self-contained block, injected immediately before the page footer:
result → "where do I send the checklist" → opt-in → OTO for the $9 analysis.
Posts to the existing `/api/subscribe` (which adds the contact to the Resend
audience the drip engine reads), with `source` set per tool so attribution is
visible in the logs and in PostHog.

STYLING
-------
The block declares its OWN complete colour pair and never inherits. Nine of the
ten tools are dark (`--bg:#0a0a0a`), `saas-churn-analyzer` is light, and the
portfolio has been burned twice by blocks that inherited a theme variable that
did not exist on the page (see `uxcss-color-revert-portfolio-bug` and
`churnlens-hardcoded-colour-theme-breaks`). Explicit colours on every element,
including anchors and the button, so a UA or ux.css rule cannot repaint them.

No claim in this block is a first-party performance claim, so it passes
`scripts/check_provenance_claims.py`.

Usage:  python3 scripts/inject_freetool_optin.py [--apply]
"""
import os
import re
import sys

MARKER = "cl-tool-optin"

BLOCK = """
<!-- {marker}: lead capture. The tool gives the answer; this asks where to send
     the checklist that tells them what to do about it. Injected by
     scripts/inject_freetool_optin.py — re-running is idempotent. -->
<section class="{marker}" id="{marker}" aria-labelledby="{marker}-h">
  <style>
    .{marker} {{
      /* Owns its palette end-to-end: this block sits on both the dark tools
         (--bg:#0a0a0a) and the light saas-churn-analyzer. Inheriting would
         make it unreadable on one of them. */
      background: #0f172a; border: 1px solid #1e293b; border-radius: 14px;
      padding: 28px 24px; margin: 48px 0 32px; max-width: 720px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #e2e8f0; line-height: 1.6;
    }}
    .{marker} .cl-eyebrow {{
      color: #38bdf8; font-size: 0.78rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 8px;
    }}
    .{marker} h2 {{
      color: #f8fafc; font-size: 1.35rem; line-height: 1.3;
      margin: 0 0 10px; font-weight: 700;
    }}
    .{marker} p {{ color: #cbd5e1; margin: 0 0 14px; font-size: 0.95rem; }}
    .{marker} ul {{ margin: 0 0 18px; padding-left: 1.1rem; color: #cbd5e1; font-size: 0.92rem; }}
    .{marker} li {{ margin-bottom: 5px; }}
    .{marker} form {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0; }}
    .{marker} input[type="email"] {{
      flex: 1 1 240px; min-width: 0; padding: 13px 15px; border-radius: 10px;
      border: 2px solid #334155; background: #0b1220; color: #f8fafc;
      font-size: 1rem; font-family: inherit; outline: none;
    }}
    .{marker} input[type="email"]::placeholder {{ color: #64748b; }}
    .{marker} input[type="email"]:focus {{ border-color: #38bdf8; }}
    .{marker} button {{
      padding: 13px 26px; border-radius: 10px; border: none; cursor: pointer;
      background: #2563eb; color: #ffffff; font-size: 1rem; font-weight: 700;
      font-family: inherit; min-height: 48px;
    }}
    .{marker} button:hover {{ background: #1d4ed8; }}
    .{marker} button[disabled] {{ opacity: 0.6; cursor: default; }}
    .{marker} .cl-fineprint {{ color: #94a3b8; font-size: 0.8rem; margin: 12px 0 0; }}
    .{marker} a {{ color: #7dd3fc; text-decoration: underline; }}
    .{marker} .cl-done {{ display: none; }}
    .{marker}.is-done .cl-ask {{ display: none; }}
    .{marker}.is-done .cl-done {{ display: block; }}
    .{marker} .cl-oto {{
      margin-top: 16px; padding-top: 16px; border-top: 1px dashed #334155;
    }}
    .{marker} .cl-oto-cta {{
      display: inline-block; margin-top: 10px; padding: 12px 24px;
      border-radius: 10px; background: #f59e0b; color: #1c1207;
      font-weight: 700; text-decoration: none; font-size: 0.95rem;
    }}
    .{marker} .cl-err {{ color: #fca5a5; font-size: 0.85rem; margin: 10px 0 0; }}
  </style>

  <div class="cl-ask">
    <p class="cl-eyebrow">You just ran the numbers</p>
    <h2 id="{marker}-h">The number is only half the job. Here's what to ask the seller next.</h2>
    <p>
      This tool tells you what the data says. The <strong>23-point buyer-side churn
      audit checklist</strong> tells you what to request, in what order, and which
      answers are red flags &mdash; the list to work through before you sign an LOI.
    </p>
    <ul>
      <li>The 23-point pre-LOI checklist</li>
      <li>The 7 hidden-churn tricks cheat sheet</li>
      <li>A full sample risk report on a synthetic $48K MRR target</li>
    </ul>
    <form novalidate>
      <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"
             style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0" />
      <label for="{marker}-email" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden">Email address</label>
      <input type="email" id="{marker}-email" name="email" placeholder="your@email.com" required autocomplete="email" inputmode="email" />
      <button type="submit">Send me the checklist</button>
    </form>
    <p class="cl-err" hidden></p>
    <p class="cl-fineprint">
      Free, no card, sent immediately. One-click unsubscribe on everything I send.
    </p>
  </div>

  <div class="cl-done">
    <p class="cl-eyebrow">Check your inbox</p>
    <h2>It's on the way.</h2>
    <p>
      If it isn't there in a minute, look in Promotions or spam and drag it across.
    </p>
    <div class="cl-oto">
      <p>
        <strong style="color:#f8fafc">Got a target on your desk right now?</strong>
        The checklist is the manual route: two to four hours in a spreadsheet per
        target. Or send the subscription CSV once and get all five risks computed
        and human-reviewed for you &mdash; $9, one-time, no subscription, report in
        2 business days.
      </p>
      <a class="cl-oto-cta" href="https://buy.stripe.com/14AcN4eNl7xmfQW8E00x20w"
         onclick="if(window.posthog){{posthog.capture('analysis_checkout_clicked',{{tier:'one-time',price:9,source:'free-tool:{slug}'}})}}">Run one analysis &mdash; $9 &rarr;</a>
      <p class="cl-fineprint">
        Or <a href="/sample-churn-risk-report">read the sample report first</a> and
        judge the analysis before you pay anything.
      </p>
    </div>
  </div>
</section>
<script>
(function() {{
  var root = document.getElementById('{marker}');
  if (!root) return;
  var form = root.querySelector('form');
  var btn = root.querySelector('button[type="submit"]');
  var err = root.querySelector('.cl-err');
  form.addEventListener('submit', async function(e) {{
    e.preventDefault();
    var email = root.querySelector('input[type="email"]').value.trim();
    if (!email) return;
    err.hidden = true;
    btn.disabled = true;
    btn.textContent = 'Sending...';
    try {{
      var resp = await fetch('/api/subscribe', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          email: email,
          source: 'free-tool:{slug}',
          website: root.querySelector('input[name="website"]').value
        }})
      }});
      var data = await resp.json();
      if (!resp.ok || !data.ok) throw new Error(data.error || 'Server error');
    }} catch (ex) {{
      // Leave the form up so the address is not lost on a transient failure.
      err.textContent = 'That did not go through. Try again, or email hello@churnlens.site.';
      err.hidden = false;
      btn.disabled = false;
      btn.textContent = 'Send me the checklist';
      return;
    }}
    root.classList.add('is-done');
    if (window.posthog) {{
      posthog.capture('lead_optin', {{ source: 'free-tool:{slug}' }});
      posthog.capture('oto_shown', {{ source: 'free-tool:{slug}' }});
    }}
  }});
}})();
</script>
"""

# embed-widget is an embed-code page, not a calculator with a result — nothing to
# capture against, and it has no footer to anchor to.
SKIP = {"embed-widget"}


def main():
    apply = "--apply" in sys.argv
    done = []
    for path in sorted(__import__("glob").glob("free/*/index.html")):
        slug = os.path.basename(os.path.dirname(path))
        if slug in SKIP:
            print("skip (no result surface):", slug)
            continue
        html = open(path, encoding="utf-8").read()
        if MARKER in html:
            print("already present:", slug)
            continue
        idx = html.find("<footer")
        if idx == -1:
            print("NO FOOTER ANCHOR, skipping:", slug)
            continue
        block = BLOCK.format(marker=MARKER, slug=slug)
        new = html[:idx] + block + "\n" + html[idx:]
        done.append(slug)
        if apply:
            open(path, "w", encoding="utf-8").write(new)
    print()
    print("MODE:", "APPLY" if apply else "DRY RUN")
    print("tools given a capture step (%d):" % len(done), ", ".join(done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
