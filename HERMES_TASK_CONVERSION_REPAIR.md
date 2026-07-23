# HERMES TASK — churnlens.site Conversion Repair

**Target site:** churnlens.**site** (buyer-side churn due-diligence) — **not** churnlens.io / churnlens.tech, which are unrelated namesakes
**Repo:** `~/churnlens` — static HTML site (no build step), branch **`entity-authority-engine`**
**Vercel project:** `churnlens` (no `rootDirectory`)
**Authored:** 2026-07-22
**Executor:** Hermes Agent (DeepSeek v4 Pro), autonomous
**Real data (90 days):** 138 pageviews · 120 visitors · 134 sessions · **97.8% bounce**

**Objective:** The pricing page has a checkout bug where **button labels are shifted one tier off the cards they sit on**, and the **same Stripe link is used for both the $9 one-time product and the $49/mo Pro card**. That bug is the highest-impact item on this site — **but it is BLOCKED on a fact you probably cannot obtain (Section 2.1). Read Rule 1 before touching pricing.html.** Everything else in this document is safe and unambiguous; do that work regardless.

---

## 0. READ THIS FIRST — SIX HARD RULES

### RULE 1 — DO NOT "FIX" THE PRICING BUTTONS BY GUESSING. YOU CAN MAKE THIS MUCH WORSE.

`pricing.html` currently reads:

| Line | Card | Price | Button label | Stripe link |
|---|---|---|---|---|
| 349-356 | **Pro** | $49/mo | **"Start Starter →"** | `7sYdR834D2d2fQWaM80x20m` (**link A**) |
| 372-379 | **Dealmaker** | $199/mo | **"Start Pro →"** | `5kQaEW6gP3h6gV02fC0x20n` (**link B**) |
| 397-398 | tripwire | $9 one-time | "Run my first analysis →" | **link A again** |

**Link A is used for both the $9 one-time product and the $49/mo subscription card.** One link cannot be both. There are exactly two possibilities and they have opposite fixes:

- **If link A charges $9:** the $49/mo Pro card silently sells a $9 one-time product. That is an **undercharge** — lost revenue, no subscription created. Annoying, not dangerous.
- **If link A charges $49/mo:** the "$9, one-time, no subscription" tripwire silently enrolls buyers in a **$49/month recurring subscription**. That is an **overcharge against an explicit written promise** — chargeback and consumer-protection territory.

**You cannot tell which from the repo, and you cannot tell from `curl`** — Stripe payment pages render their price client-side, so fetching the URL returns only `<title>Stripe Checkout</title>`. This was verified on 2026-07-22.

Therefore:
- **Do NOT swap the labels.** If the labels are wrong but the links are right, relabelling "fixes" the text and leaves the wrong product attached.
- **Do NOT change, reorder, or reassign any `buy.stripe.com` URL.**
- **Do NOT invent a new Stripe link** for the $199 Dealmaker tier (which currently has no unambiguous link of its own).
- **Follow the decision tree in Step 3.1.** If you cannot verify prices by rendering the page, your only permitted action is to **escalate**, precisely and loudly.

### RULE 2 — NEVER FABRICATE. THIS SITE HAS A DOCUMENTED FABRICATION HISTORY.
The `/benchmarks/` pages previously carried invented figures ("2,400+ SaaS companies", "thousands of SaaS"). That was cleaned at source. **Do not reintroduce any unsourced number, testimonial, customer count, or logo.** A verification grep must stay empty (Section 4).

### RULE 3 — DO NOT BARE-REGENERATE PAGES
The base page template in this repo is **bare**: regenerating a page from it **strips PostHog and hreflang tags**. Always **edit/inject into the existing HTML**. Never regenerate a page wholesale from the template.

### RULE 4 — BRAND IS ONE WORD: **ChurnLens**
Never "Churn Lens". Also never conflate this site with **churnlens.io** or **churnlens.tech** — those are unrelated third parties, not ours. Do not link to them, cite them, or copy their positioning.

### RULE 5 — DEPLOY IS OWNER-GATED
Deployment of this site has been **owner-gated**. Assume you may be unable to publish. Commit locally, write the report, and state clearly whether the fix is live or merely committed. **Do not attempt to bypass an auth/SSO block.**

### RULE 6 — SCOPE: THE TREE HAS IN-FLIGHT WORK. NEVER `git add -A`.
Currently uncommitted, from a different task:
```
 M vercel.json
?? HERMES_TASKS_CHURNLENS_AEO.md
?? HERMES_TASK_ENTITY_AUTHORITY_ENGINE.md
?? data/feed.json
?? data/saas-churn-benchmarks/data.{csv,json}
?? data/saas-retention-by-segment/data.{csv,json}
```
That is the entity-authority / benchmark-provenance work. **Stage only files you personally edited, by explicit path.**

---

## 1. PRE-FLIGHT (abort conditions)

```bash
cd ~/churnlens
```

**1.1 — Branch, tree, rollback point.**
```bash
git branch --show-current   # expect: entity-authority-engine
git status --short          # expect exactly the 8 entries listed in RULE 6
git rev-parse HEAD          # RECORD — rollback target
```
**ABORT** if `pricing.html` or `index.html` already have uncommitted edits.

**1.2 — Another agent active?**
```bash
ps aux | grep -i hermes | grep -v grep
```
**ABORT** if anything references `churnlens` or a `vercel` deploy in flight.

**1.3 — Author.**
```bash
git config user.email   # MUST be sales@sipiteno.com
```

**1.4 — Reproduce the before-state.**
```bash
grep -n "Start Starter\|Start Pro" pricing.html
grep -rho "https://buy\.stripe\.com/[A-Za-z0-9]*" --include="*.html" . | sort | uniq -c
```

---

## 2. THE DIAGNOSIS

### 2.1 — P0 (BLOCKED): the pricing checkout bug
See RULE 1. This is the highest-impact defect on the site and the **lowest-effort to type** — which is exactly why it is dangerous. It is blocked on one fact: **what does link A actually charge?**

### 2.2 — A dead, tokenless Stripe URL exists somewhere
The link inventory shows one bare `https://buy.stripe.com/` with **no token** — a button that leads nowhere. Locate it:
```bash
grep -rn 'https://buy\.stripe\.com/[^A-Za-z0-9]' --include="*.html" . | head
```

### 2.3 — P1: The lead magnet has two different names
The free checklist is called **"23-point"** in some places and **"47-point"** in others:
```
23-point: why.html, logo-retention-churn.html, about.html (x2), index.html (x2), saas-buyer-risk-assessment.html
47-point: why.html, about.html, saas-buyer-risk-assessment.html, customer-concentration-risk.html, pricing.html
```
Several pages contain **both**. For an M&A-analyst audience that reads carefully, this is a visible credibility hit.

### 2.4 — P1: Two resource links point at the wrong page
"Stripe Sigma alternatives" and "GainSight alternatives" **both** link to `/alternatives-to/profitwell`.
```bash
grep -rn "Stripe Sigma alternatives\|GainSight alternatives" --include="*.html" .
```

### 2.5 — P1: The network widget contradicts the page it sits on
The cross-site "Explore Our Network" widget describes ChurnLens as *"Churn analytics that predict, not just report"* — while the page's own disclaimer states it is **not** a churn-prediction product. A direct self-contradiction visible in the same viewport.

### 2.6 — P2: Email capture fails as often as it succeeds
Portfolio-wide: `email_captured` = 3 vs `squeeze_email_capture_failed` = 3. The lead magnet is the site's primary conversion goal and roughly half of all attempts error.

### 2.7 — P2: No reachable product, no social proof, four competing asks
Every CTA leads to either an email capture or a Stripe page — **no visible link anywhere reaches an actual CSV-upload surface**, including for the free Starter tier ("1 CSV analysis per month, no credit card"). There are no testimonials, logos, or usage numbers — only the anonymous "The Data Nerd" narrative.

### 2.8 — Things that are RIGHT — do not "fix" them
- The **"not a churn-prediction product"** disclaimer is honest and correct. Keep it; fix the widget to match (2.5), not the disclaimer.
- The benchmark fabrication cleanup appears **complete** — a grep for `2,400+` / `thousands of SaaS` in the HTML returns nothing. Keep it that way.
- The epiphany-bridge story and 5-Risk framework are well written. This is not a rewrite task.

---

## 3. EXECUTION

Do **Steps 3.2 – 3.6 first** — they are safe and unambiguous. Step 3.1 is gated.

### STEP 3.1 — The pricing bug: verify, or escalate. Never guess.

**3.1a — Attempt verification by rendering (read-only).**
Open each link in a real browser engine and **read the displayed product name, amount, currency, and whether it says "per month"**:
- link A — `https://buy.stripe.com/7sYdR834D2d2fQWaM80x20m`
- link B — `https://buy.stripe.com/5kQaEW6gP3h6gV02fC0x20n`

**Never enter card details. Never complete a purchase. Read the rendered price and close the page.**

**3.1b — Decision tree.**

- **If both prices render unambiguously:**
  - Make each card's **button label** match its **card's own tier and price**.
  - Ensure each card's link is the one that charges that card's price. If a card has **no** correct link available in the repo, **remove the button** and replace it with a "Contact us to start" mailto/contact link — **do not attach a link that charges a different amount.**
  - If link A charges **$49/mo**, the **$9 tripwire is the emergency**: it promises "one-time, no subscription" and would enrol a subscription. Either remove the tripwire CTA entirely or point it at a genuine $9 link. Flag it at the top of your report.
  - If link A charges **$9**, the $49 Pro card and $199 Dealmaker card are undercharging. Remove those buttons (or point them at correct links if they exist) and escalate for the owner to create the missing subscription links.

- **If you cannot render the prices (headless, blocked, ambiguous):**
  **STOP. Change nothing in `pricing.html`.** Do all other steps, then escalate with this exact content in the report:
  > `pricing.html` line 356 — Pro card ($49/mo) → label "Start Starter →" → link A `7sYdR834D2d2fQWaM80x20m`
  > `pricing.html` line 379 — Dealmaker card ($199/mo) → label "Start Pro →" → link B `5kQaEW6gP3h6gV02fC0x20n`
  > `pricing.html` line 398 — $9 one-time tripwire → **link A again**
  > Link A cannot be both $9 one-time and $49/mo. **Owner must open the Stripe Dashboard and state what each link charges.** Until then no safe edit is possible.

**Gate 3.1:** either (a) you verified prices and every button now matches its card, or (b) `git diff --stat pricing.html` is **empty** and the escalation is written. **A partial guess is a failure.**

---

### STEP 3.2 — Remove the dead, tokenless Stripe URL

Locate it (2.2) and either point it at a **verified existing** link or remove the button. **Do not fabricate a token.**

**Gate 3.2:**
```bash
grep -rn 'https://buy\.stripe\.com/[^A-Za-z0-9]' --include="*.html" . | wc -l   # MUST be 0
grep -rho "https://buy\.stripe\.com/[A-Za-z0-9]*" --include="*.html" . | sort -u
# MUST contain ONLY: 7sYdR834D2d2fQWaM80x20m and 5kQaEW6gP3h6gV02fC0x20n
```
**If a third token appears, you invented one — revert immediately.**

---

### STEP 3.3 — Settle the checklist on ONE number

Determine the truth by opening the actual lead magnet and **counting the items**. Whatever the real count is, use it everywhere.

```bash
grep -rln "23-point\|47-point" --include="*.html" .
```
Update every occurrence — including pages that contain **both** (`why.html`, `about.html`, `saas-buyer-risk-assessment.html`) — plus the exit-intent modal and footer copy.

**If you cannot determine the real count, use the number the deliverable itself uses**; if the deliverable is unreachable, pick the value already used in the hero (`23-point`), make it consistent, and record the uncertainty. **Never split the difference or invent a third number.**

**Gate 3.3:** exactly one of `23-point` / `47-point` appears anywhere:
```bash
grep -rc "23-point" --include="*.html" . | grep -v ":0" | wc -l
grep -rc "47-point" --include="*.html" . | grep -v ":0" | wc -l   # one of these two MUST be 0
```

---

### STEP 3.4 — Fix the two mis-pointed resource links

"Stripe Sigma alternatives" and "GainSight alternatives" both go to `/alternatives-to/profitwell`. Point each at its correct page **only if that page exists**:
```bash
ls alternatives-to/ | head -20
```
If `alternatives-to/stripe-sigma` or `alternatives-to/gainsight` does **not** exist, **remove the link** rather than creating a 404 or inventing a page.

**Gate 3.4:** every `alternatives-to/...` href in those two link texts resolves to a file that exists on disk.

---

### STEP 3.5 — Make the network widget stop contradicting the page

Change the widget's ChurnLens description from *"Churn analytics that predict, not just report"* to language matching the site's actual positioning — buyer-side / acquirer due-diligence, verifying a seller's churn claims. **Do not weaken the on-page "not a prediction product" disclaimer** (RULE, 2.8).

Note this widget is cross-site boilerplate: check whether it is injected from a shared source before editing 100 copies.
```bash
grep -rln "Explore Our Network" --include="*.html" . | wc -l
grep -rn "predict, not just report" --include="*.html" . | head -3
```
If it appears on many pages, fix it consistently across all of them (edit/inject — **never bare-regenerate**, RULE 3).

**Gate 3.5:** `grep -rn "predict, not just report" --include="*.html" . | wc -l` → `0`.

---

### STEP 3.6 — Diagnose the failing email capture

`squeeze_email_capture_failed` fires as often as success. Find the capture path and the failure branch:
```bash
grep -rn "squeeze_email_capture_failed\|email_captured" --include="*.html" --include="*.js" . | head
```
Identify the endpoint it posts to and confirm (a) the endpoint is reachable, (b) it is allowed by `connect-src` in `vercel.json`'s CSP, and (c) the failure branch is not swallowing a real error.

**Do not modify `vercel.json`** — it already has uncommitted changes from the entity-authority task (RULE 6). If the cause is a CSP `connect-src` omission, **record it for that task's owner** rather than editing the file here.

**Gate 3.6:** either a fix in the page's own JS, or a written diagnosis naming the endpoint and the exact failure cause.

---

## 4. VALIDATION (before deploy)

```bash
cd ~/churnlens

# 4.1 No invented Stripe tokens; no dead tokenless URL
grep -rho "https://buy\.stripe\.com/[A-Za-z0-9]*" --include="*.html" . | sort -u
grep -rn 'https://buy\.stripe\.com/[^A-Za-z0-9]' --include="*.html" . | wc -l    # 0

# 4.2 No fabricated stats reintroduced (RULE 2) — MUST all be 0
grep -rn "2,400+\|2400+\|thousands of SaaS" --include="*.html" . | wc -l
grep -rniE "join [0-9,]+ (buyers|acquirers|investors)|[0-9,]+\+ (companies|firms) (trust|use)" --include="*.html" . | wc -l

# 4.3 Brand is one word (RULE 4)
grep -rn "Churn Lens" --include="*.html" . | wc -l    # MUST be 0

# 4.4 Checklist count consistent
grep -rc "23-point" --include="*.html" . | grep -v ":0" | wc -l
grep -rc "47-point" --include="*.html" . | grep -v ":0" | wc -l    # one MUST be 0

# 4.5 PostHog + hreflang survived (RULE 3 — proof you didn't bare-regenerate)
grep -c "posthog" index.html pricing.html          # MUST be >= 1 each
grep -c "hreflang" index.html                       # MUST be >= 1

# 4.6 vercel.json untouched by you
git diff --name-only | grep -c "vercel.json"        # MUST be 0 (its existing change is not yours)

# 4.7 Nothing unintended staged
git status --short
```

---

## 5. COMMIT & DEPLOY

**5.1 — Stage explicitly (never `git add -A`).**
```bash
git add <only the .html files you actually edited>
git status --short   # REVIEW: no vercel.json, no data/, no HERMES_*.md
```

**5.2 — Commit.**
```bash
git commit -m "fix(churnlens): resolve checkout dead link, checklist count, mis-pointed links, widget contradiction

- Remove tokenless buy.stripe.com button
- Settle the free checklist on a single point-count across all pages
- Point 'Stripe Sigma' / 'GainSight' alternatives links at correct pages
- Network widget no longer describes ChurnLens as a prediction tool,
  contradicting the page's own disclaimer

Pricing-card buttons deliberately NOT changed: the \$49 Pro card and the \$9
one-time tripwire share one Stripe link, and the amounts cannot be verified
without the Stripe Dashboard. Guessing risks charging \$49/mo against an
explicit 'one-time, no subscription' promise. Escalated to owner."
```
(If Step 3.1 **was** verified and fixed, replace that last paragraph with the verified mapping.)

**5.3 — Deploy — ⚠ OWNER-GATED (RULE 5).**
```bash
npx vercel --prod --yes
```
If this fails with an authentication/SSO/permission error: **do not retry with different credentials, do not attempt a workaround.** Commit locally, write the report, and state that the fix is **committed but NOT live**.

---

## 6. POST-DEPLOY VERIFICATION (only if the deploy succeeded)

```bash
sleep 45

# 6.1 Routes healthy
for u in / /pricing /get-the-checklist /about; do
  printf "%-22s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' https://churnlens.site$u)"
done   # ALL 200

# 6.2 Checklist count consistent on the live site
curl -s https://churnlens.site/ | grep -c "23-point"
curl -s https://churnlens.site/ | grep -c "47-point"    # one MUST be 0

# 6.3 Widget contradiction gone
curl -s https://churnlens.site/ | grep -c "predict, not just report"   # MUST be 0

# 6.4 No fabricated stats live
curl -s https://churnlens.site/ | grep -c "2,400+"      # MUST be 0

# 6.5 Tracking survived (RULE 3)
curl -s https://churnlens.site/ | grep -c "posthog"      # MUST be >= 1
```

**6.6 — Rendered check:** open `/pricing` in a fresh incognito window and confirm the tier cards render correctly and no button leads to a blank Stripe page.

**Rollback:** `git revert --no-edit HEAD` then redeploy (subject to the same owner gate).

---

## 7. REPORT (write this file, always — even on abort)

Write `~/churnlens/HERMES_REPORT_CONVERSION_REPAIR.md` with:

1. **THE PRICING ESCALATION — put this first, in full.** State whether you verified the two Stripe links. If not, reproduce the exact block from Step 3.1b verbatim so the owner can act on it without re-deriving anything. Name the risk explicitly: *if link A is the $49/mo subscription, the $9 "one-time, no subscription" tripwire is enrolling buyers in a recurring charge against a written promise.*
2. **Whether the deploy succeeded or was owner-gated.** If gated, say plainly: *"committed locally, NOT live."*
3. **Checklist count** — which number is correct, how you determined it, and how many files changed.
4. **Links fixed / removed**, and confirmation no page was invented to satisfy a link.
5. **Email-capture diagnosis** — the endpoint, the failure cause, and whether the fix is in-page or needs the `vercel.json` CSP (which you must not edit here).
6. **Confirmation** that no fabricated stat was reintroduced, brand stayed one-word, and PostHog/hreflang survived.
7. **Escalate to owner:**
   - **The $199 Dealmaker tier appears to have no unambiguous Stripe link of its own.** It may be unsellable.
   - **There is no reachable product surface.** The free Starter tier promises "1 CSV analysis per month, no credit card", but no link on the site reaches a CSV-upload app. Until that exists there is no activation, no PLG loop, and no upgrade path — every CTA is either an email capture or a payment page.
   - **Zero third-party social proof** for a due-diligence buyer persona. Given this site's fabrication history, real testimonials must be earned, never written.

---

## 8. WHAT SUCCESS LOOKS LIKE

- **Either** every pricing button verifiably matches its card, **or** `pricing.html` is untouched and the escalation is written in full. Nothing in between.
- Exactly **two** Stripe tokens exist across the repo; no tokenless URL; no invented token.
- The checklist has **one** point-count sitewide.
- No link points at a page that does not exist.
- The network widget no longer contradicts the page's own disclaimer.
- No fabricated statistic reintroduced; brand is one-word **ChurnLens**; PostHog and hreflang tags still present (proof of no bare-regeneration).
- `vercel.json`, `data/`, and the two in-flight `HERMES_*.md` files were **never staged**.

**The deepest point:** the highest-scoring fix on this site is also the one you are most likely to get wrong. A one-word label swap looks trivial and takes ten seconds — but the $49 card and the $9 "one-time, no subscription" tripwire share a single Stripe link, so one of those two placements is already charging the wrong amount, and changing the labels without knowing which will lock in the error rather than fix it. The professional move here is to fix the five things that are unambiguous, leave the sixth strictly alone, and hand the owner a precise, actionable question. An honest escalation is worth more than a confident guess at a payment page.
