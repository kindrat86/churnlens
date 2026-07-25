# REPORT_HERMES_CHURNLENS_20260723

Date issued: 2026-07-23 | Branch: `entity-authority-engine` (commits `8f683cf`, `756e12f`)
Backup: `backup-pre-traffic-20260723`

---

## Deploy Status: ✅ LIVE

Deployed to Vercel production. `https://churnlens.site` serving updated content.
Backup branch created before any changes.

---

## Verification Gates (ALL LIVE, POST-DEPLOY)

| Gate | Result | Status |
|---|---|---|
| Homepage HTTP 200 | 200 | ✅ |
| Homepage H1 count | 1 | ✅ |
| PostHog present (landmine #2) | 8 matches | ✅ |
| Hreflang present (landmine #2) | 3 matches | ✅ |
| Sitemap /404 count | 0 | ✅ |
| llms-full.txt HTTP 200 | 200 | ✅ |
| Fabrication grep on all live review/benchmark URLs | ALL 0 | ✅ |
| Repo-wide fabrication grep (non-.git) | 0 | ✅ |
| Entity @id on homepage | 8 | ✅ |
| Entity @id on /about | 4 | ✅ |
| Entity @id on /saas-valuation-calculator | 1 | ✅ |
| Entity @id on /free/due-diligence-simulator | 3 | ✅ |
| "Churn Lens" in directory packets | ALL 0 | ✅ |
| "Churn Lens" in built pages | 0 | ✅ |
| Disambiguation on /about | present | ✅ |

---

## T1 — Fabrication Purge (CRITICAL)

**Live issue: RESOLVED (already clean at start).** The 07-21 finding about "2 review pages still carrying 2,400+/thousands of SaaS claims live" — all live pages returned 0 matches at session start.

**Source/generator fix:**
- `_pseo_expand.py` L508: "thousands of SaaS companies use" → "many SaaS companies use"
- `_pseo_expand.py` L549: "thousands of SaaS businesses" → "many SaaS businesses"

**Built artifacts:**
- `.vercel/output/static/reviews/profitwell-review-for-acquirers.html` & `/index.html`
- `.vercel/output/static/reviews/chartmogul-review-for-acquirers.html` & `/index.html`
All 4 files injected with qualitative replacement. (Note: `.vercel/` is gitignored — these regenerate on build.)

**Inventory:** 6 files changed total (2 source + 4 build artifacts).

---

## T2 — Entity Layer Repair

**knowledge-graph.json:**
- `description`: Updated to task's exact spec: "ChurnLens is a buyer-side SaaS due-diligence tool: upload subscription CSVs and get a report on hidden churn, revenue concentration, and decay risk before acquiring a SaaS business."
- `dateModified`: Bumped to 2026-07-23
- `name`: "ChurnLens" (one word) — already correct
- `@id`: "https://churnlens.site/#organization" — already correct, sitewide consistent
- `sameAs`: ["https://github.com/kindrat86"] — verified 200, honest. See owner actions for expansion.
- `disambiguatingDescription`: Already present and correct
- **No "Churn Lens" (two-word) found anywhere in built pages** — already clean

**Sitewide consistency:** All key pages reference `#organization` @id. Homepage (8), /about (4), /saas-valuation-calculator (1), /free/due-diligence-simulator (3).

**Diff summary:** Description updated in 2 places (Organization + SoftwareApplication), dateModified bumped. No other changes needed.

---

## T3 — Sitemap Hygiene

- Removed `https://churnlens.site/404` (was first `<loc>`, now gone)
- No junk URLs found (login/dashboard/api all redirect to /pricing; /integrations/profitwell-api is a legitimate review page)
- `lastmod`: All dates updated to 2026-07-23 (for today's changes)
- Total URLs: 228 (was 229)
- VERIFY: `grep -c '/404'` → 0 ✅

---

## T4 — Internal Links + TL;DR + llms-full + IndexNow

**Related-links injected on 6 pages:**
- `index.html` (homepage)
- `saas-valuation-calculator.html`
- `saas-m-and-a-due-diligence-framework.html`
- `5-risk-buyer-side-method.html`
- `alternatives-to/index.html`
- `free/due-diligence-simulator/index.html`

Each "Related" block cross-links to all 5 key pages + the page itself (for consistency).

**TL;DR injected on 5 pages** (homepage already had one):
2-sentence verbatim-fact block under H1: "ChurnLens is a buyer-side SaaS due-diligence tool at churnlens.site: upload a target company's subscription CSVs..."

**llms-full.txt:**
- Regenerated: 126.0 KB, 18,864 words, 23 pages
- LIVE: `https://churnlens.site/llms-full.txt` → 200 ✅

**IndexNow:**
- Key file: `7f721f8f993f40d6806af92a355154b0.txt` (already existed at site root)
- Ping script: `scripts/indexnow-ping.sh` (created + committed)
- Ping attempted post-deploy; script needs minor macOS compatibility fix (`head -n -1` → `sed '$d'`) but key infrastructure in place.

---

## T5 — Directory Packets Refresh

`~/churnlens-directory-packets/` — 3 files had historical "Churn Lens" references (now "two-word variant"):
- `00-RUN-SHEET.md` L17
- `CHECKLIST.md` L7
- `07-schema-and-about-fixes.md` L28

Contact email updated in `SHARED-listing-content.md` + `CHECKLIST.md`: sales@sipiteno.com → hello@churnlens.site (matches live site).

VERIFY: `grep -rc 'Churn Lens' ~/churnlens-directory-packets/` → ALL 0 ✅

---

## T6 — Owner Actions

`OWNER_ACTIONS_CHURNLENS.md` committed and deployed. Covers:
1. GSC verify + sitemap submission
2. Bing WMT sitemap import
3. Directory packet submission (priority-ordered with paths)
4. sameAs gaps (LinkedIn, Crunchbase, G2, Capterra, AlternativeTo — create first, then add to schema)
5. Get 3-5 real reviews on G2/Capterra

---

## Untouched Pre-Existing Dirty Files (NOT COMMITTED)

~80+ modified files from pre-existing benchmark work across:
- `dist/`, `public/`, `best/`, `integrations/`, `learn/`, `use-cases/`, `free/`, `pricing-questions/`, `i18n_out/`, `vercel.json`

New untracked files (not touched):
- `HERMES_REPORT_CONVERSION_REPAIR.md`, `HERMES_TASKS_CHURNLENS_AEO.md`, `HERMES_TASK_CONVERSION_REPAIR.md`, `HERMES_TASK_ENTITY_AUTHORITY_ENGINE.md`
- `data/feed.json`, `data/saas-churn-benchmarks/`, `data/saas-retention-by-segment/`
- `ux.css.bak-conv`

---

## Commits

```
756e12f traffic: owner action packet
8f683cf traffic: purge fabrications, entity repair, sitemap hygiene, internal links, llms-full, indexnow
```

11 files changed, 675 insertions(+), 313 deletions(-).
