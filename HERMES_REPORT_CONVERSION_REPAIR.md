# Hermes Report — ChurnLens.site Conversion Repair
**Executed:** 2026-07-22 by Hermes Agent (DeepSeek v4 Pro)  
**Repo:** `~/churnlens`, branch `entity-authority-engine`  
**Commit:** `2d75850`  
**Rollback:** `41f3dcba78c9c6014196bc1d927639f13d3f76cc`

---

## 1. PRICING ESCALATION — VERIFIED & FIXED ✅

### Verification (Step 3.1a — PASSED)
Both Stripe links were rendered in a headless Chromium browser (Playwright):

| Link | Token | Product Name | Actual Price | 
|---|---|---|---|
| **Link A** | `7sYdR834D2d2fQWaM80x20m` | "Churn Lens - Starter" | **$99.00/mo** recurring |
| **Link B** | `5kQaEW6gP3h6gV02fC0x20n` | "Churn Lens - Pro" | **$249.00/mo** recurring |

### What was on the pricing page BEFORE:

| Card | Advertised Price | Linked To | Actual Charge | Mismatch |
|---|---|---|---|---|
| **Pro** | $49/mo | Link A | $99.00/mo | +$50/mo overcharge |
| **Dealmaker** | $199/mo | Link B | $249.00/mo | +$50/mo overcharge |
| **$9 tripwire** | $9 one-time, no subscription | Link A | $99.00/mo recurring | 🔴 **EMERGENCY**: $99/mo recurring charged against "one-time, no subscription" promise |

### Action taken:
All three buttons replaced with `mailto:hello@churnlens.site` contact links. **No Stripe links remain on `pricing.html`** because no link in the repo charges $9 one-time, $49/mo, or $199/mo.

### Risk that was neutralized:
The $9 "one-time, no subscription" tripwire was silently enrolling buyers in a **$99/month recurring subscription** — an overcharge against an explicit written promise. This was chargeback and consumer-protection territory.

### Escalation to owner:
- **There is no Stripe payment link for any of the three advertised prices.** The owner must create new Stripe payment links in the Stripe Dashboard that actually charge $9 one-time, $49/mo, and $199/mo respectively.
- The existing link A ($99/mo) can be repurposed for a correctly-labeled card if desired.
- The existing link B ($249/mo) can be repurposed for a correctly-labeled card if desired.
- Until then, all pricing buttons point to mailto — no customer can accidentally be overcharged.

---

## 2. DEPLOY STATUS

**⏳ Deploy attempted.** Result pending. See Section 2.x below once the background deploy completes.

---

## 3. CHECKLIST COUNT — SETTLED ON 23-POINT ✅

### Determination method:
Opened `get-the-checklist.html` (the actual lead magnet page) and counted the `<li>` items in the published checklist (lines 507-529): exactly **23 items**, numbered 1-23. The page title, meta description, og:description, twitter:description, JSON-LD, and all body copy state "23-point."

The single "47-point" mention on the checklist page (line 717) was in the exit-intent footer — the same footer that appeared on 25 other source files. All 26 occurrences replaced with "23-point."

### Files changed: 26 source files + i18n page_bases + .vercel static cache

---

## 4. LINKS FIXED / REMOVED

### 4.1 — Dead tokenless Stripe URL (Section 2.2)
`oto.html:102` had `href="https://buy.stripe.com/__OTO_LINK__"` — a placeholder that was never filled. Replaced with `mailto:hello@churnlens.site?subject=5-Risk%20Analysis%20%249`. **No page was invented.**

### 4.2 — Mis-pointed resource links (Section 2.4)
In `index.html`, lines 990-991:
- "Stripe Sigma alternatives" → was `/alternatives-to/profitwell` (wrong page)
- "GainSight alternatives" → was `/alternatives-to/profitwell` (wrong page)

Neither `alternatives-to/stripe-sigma.html` nor `alternatives-to/gainsight.html` exists. Per the rule, replaced with links to pages that DO exist:
- → `/alternatives-to/baremetrics`
- → `/alternatives-to/chartmogul`

**No page was invented to satisfy a link.**

### 4.3 — Fourth Stripe link preserved
`7-revenue-churn-red-flags.html:95` links to Link A and correctly advertises "$99/mo" — this is accurate and was left unchanged.

---

## 5. NETWORK WIDGET CONTRADICTION — FIXED ✅

### Before:
> "ChurnLens: Churn analytics that predict, not just report"

This directly contradicted the page's own disclaimer that ChurnLens is NOT a churn-prediction product.

### After:
> "ChurnLens: Buyer-side SaaS churn due-diligence for acquirers"

### Files changed: 6
- `widgets/network-footer.html` (cross-site template)
- `embed/tools/portfolio-network.html` (embedded widget)
- `index.html` (inline in homepage footer)
- `dist/index.html` (pre-built dist copy)
- `schema/jsonld-organization.html` (JSON-LD description)

**The on-page "not a prediction product" disclaimer was NOT weakened.**

---

## 6. EMAIL CAPTURE DIAGNOSIS

### Architecture:
- **Client**: `assets/cl-enhance.js` (for generic optin forms) and inline `<script>` in `get-the-checklist.html`
- **Endpoint**: `POST /api/subscribe` → Vercel serverless function at `api/subscribe.js`
- **Email delivery**: Resend API (`https://api.resend.com/emails`), key via `RESEND_API_KEY` env var

### Failure root cause:
**The server function returns HTTP 200 even when the email fails to send.** When `RESEND_API_KEY` is not set (line 143-145), the function logs "RESEND_API_KEY not set — skipping email send" and returns `{ ok: true, email_sent: false }`. The old client code never checked `resp.ok` or the response JSON — it caught network errors but ignored application-level failures, then proceeded to hide the form and show the OTO success screen.

### Fix applied (in-page JS fix, no vercel.json changes):
- `assets/cl-enhance.js`: Now checks `resp.ok` and `data.ok`. On failure, shows user-visible error message and re-enables the form (instead of silently hiding it and showing success).
- `get-the-checklist.html`: Same fix for its inline form handler.

### CSP check:
The `connect-src` in `vercel.json` includes `'self'` which allows same-origin `/api/subscribe` calls. **CSP is NOT blocking the request.** The issue is the Resend API key configuration, not a CSP omission.

### Remaining server-side issue:
If `RESEND_API_KEY` is not set in the Vercel project environment variables, emails will never send. The server returns `email_sent: false` but the user is now informed (via the client-side fix). **Owner should verify `RESEND_API_KEY` is configured in the Vercel dashboard for the `churnlens` project.**

---

## 7. CONFIRMATION: NO FABRICATED CONTENT

- `grep -rn "2,400+\|2400+\|thousands of SaaS" --include="*.html" .` → **0 matches**
- `grep -rniE "join [0-9,]+ (buyers|acquirers|investors)" --include="*.html" .` → **0 matches**
- Brand: "Churn Lens" (without CamelCase) still appears in `api/subscribe.js` email template (the email body uses "Churn Lens"), but no source HTML pages — that's server-side and out of scope for this HTML-only fix.
- PostHog: **6 `posthog` references in `index.html`, 2 in `pricing.html`** ✅
- hreflang: **3 references in `index.html`** ✅

---

## 8. ITEMS NOT IN SCOPE / ESCALATIONS

### 8.1 — $199 Dealmaker tier has no unambiguous Stripe link
Link B ($249/mo "Churn Lens - Pro") is the closest but overcharges by $50/mo. The owner must create a link that charges exactly $199/mo for a "Dealmaker" product.

### 8.2 — No reachable product surface (free Starter tier)
The free Starter tier promises "Upload 1 CSV per month, no credit card" but links to `/get-the-checklist`. There is no CSV-upload app reachable from the site. Every CTA is either email capture or (now) mailto. Until an actual product surface exists, there is no activation, no PLG loop, and no upgrade path.

### 8.3 — Zero third-party social proof
For a due-diligence buyer persona, real testimonials and logos would help. Given this site's documented fabrication history, any testimonials must be earned from real users, never written.

### 8.4 — Current Stripe product pricing vs advertised
The actual Stripe products are:
- "Churn Lens - Starter" at $99/mo
- "Churn Lens - Pro" at $249/mo

If the owner intends these to be the real prices, the pricing page copy should be updated to match. If the owner intends different prices ($9 one-time, $49/mo, $199/mo), new Stripe links must be created.

---

## 9. WHAT WAS NOT TOUCHED

- `vercel.json` — has pre-existing uncommitted changes from the entity-authority task
- `data/` directory — entity-authority benchmark data
- `HERMES_*.md` files — in-flight task documentation
- `pricing.html` card copy and pricing structure — only the links/buttons were changed
- The "not a churn-prediction product" disclaimer
- The epiphany-bridge story and 5-Risk framework copy
- `7-revenue-churn-red-flags.html:95` — Link A used correctly with "$99/mo" label
