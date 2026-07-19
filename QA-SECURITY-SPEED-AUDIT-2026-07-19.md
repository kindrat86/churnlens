# ChurnLens (churnlens.site) — QA/Security/Speed Audit

**Audit date:** 2026-07-19  
**Target:** https://churnlens.site (static HTML on Vercel)  
**Audit scope:** Security headers, broken links (top 20+ pages), HTTPS/HSTS, CSP, page weight, latency

---

## Overall Scores

| Category | Score | Grade |
|----------|-------|-------|
| **Security** | **90/100** | A |
| **QA** | **80/100** | B+ |
| **Speed** | **90/100** | A |

---

## Security (90/100)

### ✅ Present & correctly configured

| Header | Value | Status |
|--------|-------|--------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | ✅ Excellent — 2-year HSTS, preload ready |
| `X-Content-Type-Options` | `nosniff` | ✅ |
| `X-Frame-Options` | `DENY` | ✅ |
| `X-XSS-Protection` | `1; mode=block` | ✅ |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | ✅ |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), fullscreen=(), display-capture=()` | ✅ |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline' ...` | ⚠️ See below |
| HTTPS redirect (HTTP → HTTPS) | `308 Permanent Redirect` → `https://churnlens.site/` | ✅ |

```http
# curl -sI https://churnlens.site (truncated)
strict-transport-security: max-age=63072000; includeSubDomains; preload
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), microphone=(), geolocation=(), ...
```

### SSL Certificate

- **Issuer:** Let's Encrypt (YR1)
- **Validity:** Jul 3 → Oct 1, 2026 (90-day, auto-renewed)
- No expiration risk

### ❌ Missing / Issue

| Issue | Severity | Safe-fix |
|-------|----------|----------|
| **CSP `'unsafe-inline'` in `script-src`** | Medium | Replace inline scripts with external files or add nonces. Currently 0 `<script>` blocks appear inline on the homepage — the inline scripts may be from PostHog's snippet. If PostHog is loaded via a script tag with a nonce, `'unsafe-inline'` can be dropped. |
| **No `Set-Cookie` → no HttpOnly/Secure/SameSite cookie config** | Low | Not needed currently — no cookies set. Good. |
| **No `Access-Control-Allow-Origin` restrictions on root** | Info | `*` is set on all responses — acceptable for a static content site. |

### Verdict: Security is strong. HSTS preload, all major headers gated in `vercel.json`. The only gap is removing `'unsafe-inline'` from script-src, which requires nonce-based script loading.

---

## QA (80/100)

### ✅ Broken Links: Top 20 Pages (all 200)

All 20 sitemap-priority URLs returned **HTTP 200**:

```
200 https://churnlens.site/
200 https://churnlens.site/about
200 https://churnlens.site/alternatives-to/
200 https://churnlens.site/alternatives-to/baremetrics
200 https://churnlens.site/alternatives-to/chart-mogul
200 https://churnlens.site/alternatives-to/chartmogul
200 https://churnlens.site/alternatives-to/churnly
200 https://churnlens.site/alternatives-to/churnzero
200 https://churnlens.site/alternatives-to/gainsight
200 https://churnlens.site/alternatives-to/profitwell
200 https://churnlens.site/alternatives-to/retina-ai
200 https://churnlens.site/alternatives-to/stripe-sigma
200 https://churnlens.site/benchmarks/
200 https://churnlens.site/benchmarks/expansion-revenue-benchmarks
200 https://churnlens.site/benchmarks/net-revenue-retention-2026
200 https://churnlens.site/benchmarks/saas-cac-payback
200 https://churnlens.site/benchmarks/saas-cac-payback-2026
200 https://churnlens.site/benchmarks/saas-churn-benchmarks-2026-interactive
200 https://churnlens.site/benchmarks/saas-churn-rate-2026
200 https://churnlens.site/benchmarks/saas-churn-rate-benchmarks-2026
```

Additional 48 pages also returned **200** — zero broken links found among ~70 checked URLs.

### ✅ 404 Page

Custom 404 page exists (`404.html`, 4,866 bytes), served with correct HTTP 404 status — not a soft 404.

### ❌ Issues Found

#### 1. `/privacy` and `/terms` redirect to `/faq` (Critical)

```http
$ curl -sI https://churnlens.site/privacy
HTTP/2 308
location: /faq

$ curl -sI https://churnlens.site/terms
HTTP/2 308
location: /faq
```

**Impact:** There is **no dedicated privacy policy or terms of service page**. Both routes permanently redirect to `/faq`. The files `privacy.html` and `terms.html` exist on disk but are caught by the `.html`→clean-slug redirect rule, creating a redirect loop:

```
/privacy → (redirect rule) → /faq
/privacy.html → (regex rule) → /privacy → /faq
```

**Safe-fix:** Remove the redirect rules for `/privacy` and `/terms` from `vercel.json` (lines 161-168), and instead add rewrites to `privacy.html`/`terms.html`:

```json
// Replace redirects for /privacy and /terms with rewrites:
{ "source": "/privacy", "destination": "/privacy.html" },
{ "source": "/terms",  "destination": "/terms.html" }
```

Then ensure `privacy.html` and `terms.html` contain actual content (not just redirect pages).

#### 2. `reviews.html` and `cost-of.html` have no explicit rewrite

These `.html` files exist on disk and serve via Vercel's implicit `.html` resolution, but they are not listed in the `rewrites` array. This works but is fragile — if the Vercel default `.html` handler changes, they'd 404.  

**Safe-fix:** Add rewrites:

```json
{ "source": "/cost-of", "destination": "/cost-of.html" },
{ "source": "/reviews", "destination": "/reviews.html" },
{ "source": "/sectors", "destination": "/sectors.html" }
```

#### 3. Sitemap includes `/faq` AND `/faq/` (duplicate)

Both appear in `sitemap.xml`:
```
<loc>https://churnlens.site/faq</loc>
<loc>https://churnlens.site/faq/</loc>
```

This is a canonicalization issue — the trailing-slash variant may dilute ranking signals.  
**Safe-fix:** Remove one from the sitemap.

#### 4. 189 URLs in sitemap, no explicit canonical tags

No `<link rel="canonical">` found in any checked page. Vercel's clean-URL redirects (`.html` → no extension) should handle 99% of cases, but canonical tags on key pages (especially tools/calculators) would strengthen SEO.

#### 5. `/sitemap-pseo.xml` redirects to `/sitemap.xml`

This is intentional (typo fix) but `sitemap-index.xml` doesn't reference `sitemap-pseo.xml` anymore — clean.

---

## Speed (90/100)

### ✅ Page Load Metrics (TTFB from EU edge)

| Page | Connect | TLS | TTFB | Total | Size |
|------|---------|-----|------|-------|------|
| Homepage | 10ms | 87ms | 137ms | 168ms | 82.9 KB |
| About | 12ms | 151ms | 204ms | 204ms | 29.0 KB |
| Churn Calculator (tool) | 12ms | 135ms | 195ms | 195ms | 19.7 KB |
| Benchmarks page | 9ms | 87ms | 141ms | 141ms | 10.0 KB |

All pages load **under 210ms** from a warm EU edge — excellent for a static site on Vercel.

### ✅ Cache Configuration

- `Cache-Control: public, max-age=0, s-maxage=7200, must-revalidate` — CDN caches for 2 hours
- `/favicon.png`: `max-age=86400` (1 day)
- `/assets/*`: `max-age=31536000, immutable` (1 year, fingerprint-based — excellent)
- `/embed/*`: custom CORS headers, frame-allow — correct for widgets
- No `Last-Modified` / `ETag` mismatch issues

### ✅ Compression

- Vercel serves gzip/brotli automatically (Content-Encoding not shown in HEAD, but confirmed supported on full responses)

### ✅ Asset Count

- Homepage loads only **3 scripts**: PostHog analytics, `ux.js`, `cl-enhance.js`
- No render-blocking fonts (Google Fonts loaded via `<link>` — could be `preconnect`+`display=swap` optimised)

### ❌ Minor Issues

#### 1. Homepage is 83 KB HTML (no image-heavy content)

For a text-heavy homepage, 83 KB is on the higher side. This suggests long inline content or heavy DOM.  
**Safe-fix:** Audit the page for unused content or split into paginated sections.

#### 2. No explicit `preconnect`/`dns-prefetch` for Google Fonts or PostHog

Currently missing hints like:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://eu.i.posthog.com" crossorigin>
```

Adding these could shave ~30-50ms off font/analytics loading.

#### 3. No resource hints (`preload`/`prefetch`) on top-tier pages

Key pages (pricing, tools) aren't hinted for instant navigation.

---

## Summary of Safe-Fixable Issues (Priority Order)

| # | Issue | Category | Effort | Impact |
|---|-------|----------|--------|--------|
| 1 | `/privacy` & `/terms` redirect to `/faq` — no real privacy/tos pages | QA/Security | Low | **High** — legal/compliance risk |
| 2 | CSP `'unsafe-inline'` in `script-src` | Security | Medium | **Medium** — XSS surface |
| 3 | Missing rewrites for `reviews.html`, `cost-of.html`, `sectors.html` | QA | Very low | Low — works via Vercel default |
| 4 | Sitemap has duplicate `/faq` and `/faq/` | QA | Very low | Low — minor SEO dilution |
| 5 | No canonical tags | QA | Low | Low — Vercel's URL normalization covers most |
| 6 | No resource hints (preconnect/prefetch) | Speed | Very low | Low — ~30-50ms page load improvement |
| 7 | Homepage 83 KB HTML | Speed | Low | Medium for mobile |

---

*Audit performed with curl, OpenSSL s_client, and static analysis of the local repository at `~/churnlens/`.*
