# OWNER_ACTIONS_CHURNLENS.md

Date: 2026-07-23 | Executed by Hermes Agent

## 1. Deploy Status: ✅ DEPLOYED

Vercel deployed successfully to `https://churnlens.site` (commit `8f683cf` on branch `entity-authority-engine`).

## 2. SEARCH CONSOLE — DO NOW

```bash
# GSC: Verify site ownership (if not already), submit sitemap
# Sitemap URL: https://churnlens.site/sitemap.xml
# GSC URL: https://search.google.com/search-console

# Bing WMT: Import the sitemap
# URL: https://www.bing.com/webmasters
# Sitemap: https://churnlens.site/sitemap.xml
```

## 3. SUBMIT DIRECTORY PACKETS — HIGHEST PRIORITY

The refreshed packets are in `~/churnlens-directory-packets/`. This is the #1 traffic action — churnlens.site currently has 0 AI citations. Getting listed on just AlternativeTo + G2 will seed the first citations.

Priority order (see `00-RUN-SHEET.md`):
1. **AlternativeTo** (`03-alternativeto.md`) — fastest, best fit for "alternatives to" queries
2. **G2** (`01-g2.md`) — highest AI-citation authority (DR ≈90)
3. **Capterra** (`02-capterra.md`) — auto-feeds GetApp + Software Advice
4. **SaaSworthy** (`05-secondary.md`)
5. **SourceForge/Slashdot** (`05-secondary.md`)
6. **Product Hunt** (`05-secondary.md`) — launch when 2-3 real users lined up
7. **TrustRadius** (`04-trustradius.md`) — deferred until ≥100 customers

Packet files in `~/churnlens-directory-packets/`:
- `00-RUN-SHEET.md` — strategy + priority
- `SHARED-listing-content.md` — canonical copy (source of truth)
- `CHECKLIST.md` — fill-once tracker
- `01-g2.md`, `02-capterra.md`, `03-alternativeto.md`, `04-trustradius.md`, `05-secondary.md`
- `06-review-seeding-plan.md` — how to get real reviews
- `07-schema-and-about-fixes.md`

All packets have been refreshed: one-word "ChurnLens", buyer-side/acquirer-DD positioning, current URL, hello@churnlens.site contact email, owner-fill fields preserved.

## 4. sameAs GAPS (from T2 entity layer audit)

Current `knowledge-graph.json` sameAs: `["https://github.com/kindrat86"]` (verified — returns 200).

Missing profiles — create these, then add to `sameAs` and re-deploy:
- **LinkedIn company page**: Create for ChurnLens (churnlens.site). Strongest disambiguation signal vs. namesakes (.io, .tech). Required by TrustRadius.
- **Crunchbase**: Create company profile for churnlens.site
- **G2 listing URL** — once profile is live
- **Capterra listing URL** — once profile is live
- **AlternativeTo listing URL** — once profile is live

After directory profiles are live, update `~/churnlens/knowledge-graph.json` sameAs array and re-deploy.

## 5. GET 3-5 REAL REVIEWS

Once G2 + Capterra profiles exist, use `06-review-seeding-plan.md` to request honest reviews from 5-10 real users/buyers/PE analysts. Target 3-5 approved reviews on G2 and Capterra each. **Never fabricate reviews.**

## 6. Ready-to-Ship State

All changes committed on branch `entity-authority-engine` (commit `8f683cf`). Deployed to Vercel production.

Backup branch: `backup-pre-traffic-20260723` created before any changes.

Uncommitted pre-existing work (NOT touched — do not accidentally commit):
- ~80+ modified files across dist/, public/, best/, integrations/, learn/, etc. (benchmark data work)
- New untracked files: HERMES_REPORT_*, HERMES_TASK_*, data/feed.json, data/saas-churn-benchmarks/, data/saas-retention-by-segment/, ux.css.bak-conv
