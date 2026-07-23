# Hermes Autonomous Execution Brief — churnlens.site AEO/SEO Remediation

**Target repo:** `~/churnlens` (branch `main`, HEAD at time of writing: `c0314d7`)
**Live domain:** https://churnlens.site (Vercel project `churnlens`, static site — no build step, `vercel.json` has `outputDirectory: "."` and no `buildCommand`)
**Deploy command:** `vercel --prod --yes` from `~/churnlens` (plain static deploy, no framework build)
**Source audit:** 10-site portfolio AEO/SEO audit, 2026-07-21, churnlens.site scored 78/100, 0 critical + 2 high + 3 medium + 2 low findings.
**Executor:** Hermes Agent (autonomous, DeepSeek v4 Pro). This document is your complete task spec — do not improvise scope beyond what's written here.

**Important methodology note:** every task below was re-verified directly against the current repo and, for the top finding, against this site's shared growth-engine generator before being written into this brief. What looked like "the sourced-benchmark-data fix just isn't deployed yet" turned out to be something more specific and more interesting — see TASK-01's root cause writeup. One low-severity audit finding did not reproduce at all (§3). Trust the file/line citations here over the original audit summary, and re-verify yourself if HEAD has moved since `c0314d7`.

---

## 0. Read this whole section before touching anything

### 0.1 Collision check — mandatory first step, every run

```bash
ps aux | grep -i hermes | grep -v grep
cd ~/churnlens && git status --short && git log -1 --format='%H %ci'
vercel ls churnlens --scope sales-3429s-projects | head -5
```

**At brief-writing time this repo's tree was NOT clean**: `dream100.html`, `pricing.html`, and `vercel.json` were modified, plus several untracked new files/dirs (`7-revenue-churn-red-flags.html`, `affiliate.html`, `data/`, `dream-100/`). This looks like an in-progress edit from another process (possibly the portfolio Hermes cron). Given that:

- **Do not run `git add -A` or any broad-stage command** — only ever `git add` the exact files each task below names.
- If a Hermes process is running against `~/churnlens`, or a deploy landed in the last ~30 minutes, wait and re-check every 10 minutes.
- If the dirty files listed above are still dirty when you start, that's a pre-existing condition noted here, not something you caused — leave them alone unless a task below explicitly names one of them. None of the tasks in this brief touch `dream100.html`, `pricing.html`, `affiliate.html`, or `data/`.
- `vercel.json` being modified is worth a closer look before you deploy anything, since your own tasks may also touch files under its purview indirectly — diff it yourself (`git diff vercel.json`) and confirm you understand what changed before your deploy ships it as part of your commit, even though none of your tasks edit it directly.

### 0.2 This repo has no blank-screen CSP landmine — confirmed, no shim needed here

Unlike several sibling sites in this portfolio, churnlens.site's CSP does **not** contain `require-trusted-types-for` — confirmed via live header inspection. No task below needs to guard against that specific failure mode on this site.

### 0.3 Known do-not-confuse: churnlens.site vs churnlens.io vs churnlens.tech

This site's entity-disambiguation work (llms.txt canonical-attribution section, `disambiguatingDescription` in Organization schema) exists specifically because `churnlens.io` and `churnlens.tech` are **different businesses this owner does not own** — confirmed live and correct, do not touch or "simplify" the disambiguation language in any task below; it's load-bearing.

### 0.4 Guardrails you must never bypass

- Never use `git commit --no-verify`. Always create new commits; never `git commit --amend` on a pushed/deployed commit. Never `git push --force` to `main`.
- This repo has no `guard-positioning`-style script of its own to run — your own verification commands in each task are the only gate. Run them.

### 0.5 What you are NOT authorized to change autonomously

See §6 "Owner-gated — do not execute" at the bottom. Anything not explicitly listed as a task in §1–§2 is out of scope.

---

## 1. P1 — HIGH

### TASK-01: Restore real, sourced benchmark data to the 3 live `/benchmarks/*` pages that can be fixed with existing content

**Files:** `~/churnlens/benchmarks/saas-churn-rate.html`, `~/churnlens/benchmarks/revenue-concentration-benchmarks.html`, `~/churnlens/benchmarks/logo-retention-benchmarks.html`

**Root cause (confirmed, and more specific than "the fix isn't deployed"):** A prior fix (commit `1c41ef7`, 2026-07-18) did add real, cited benchmark data with named sources (SaaS Capital, Benchmarkit, FE International, Recurly, Wall Street Prep) — but it targeted a different set of page slugs (`saas-churn-rate-benchmarks-2026`, etc.) that were later **deleted** by a subsequent bulk pSEO expansion (commit `1d6510a`, "+55 pages"), which created **brand-new files** at the current live slugs (`saas-churn-rate.html`, `revenue-concentration-benchmarks.html`, `logo-retention-benchmarks.html`, `saas-valuation-multiples.html`) from a bare template that never inherited the sourced-data fix. So it's not that a fix is sitting undeployed — the page that had the fix was deleted and replaced by a newer, unrelated page under a different filename that happens to serve the same live URL family. Confirmed via `git log --diff-filter=A` on each current file: all 4 were created fresh by `1d6510a`, none by `1c41ef7`.

The good news: the real sourced content was never lost — it still lives in the shared growth-engine generator at `~/.growth-engine/pseo-generator.py`, in a dict called `CHURNLENS_BENCHMARK_DATA`, keyed by the *old* slugs. Three of its four keys map cleanly by topic to three of the four current live pages. The fourth current page (`saas-valuation-multiples.html`) has **no corresponding entry** in that dict — there is no pre-existing sourced content for it (see TASK-02).

**Fix — replace the unsourced paragraph in each file with the exact, already-approved sourced HTML from the generator dict.** Do not paraphrase or re-derive this content — use it byte-for-byte as extracted below, so there's no risk of a citation, number, or link getting garbled in transcription.

**1. `benchmarks/saas-churn-rate.html`** — find and replace this exact paragraph (currently the sole line 74):
```html
<p>SaaS churn rates vary dramatically by segment. B2B enterprise typically sees 3-5% annual churn, while SMB SaaS can see 3-7% monthly churn. Industry benchmarks: Healthcare SaaS averages 4.5% monthly, Martech 5.2%, DevTools 3.8%. These are industry aggregates — treat them as context, not targets.</p>
```
with:
```html
<h3 style="font-size:1.15em;font-weight:700;margin:1.6em 0 .4em">What the benchmarks show</h3><p>Across private B2B SaaS, the median company keeps about <strong>91% of revenue year over year</strong> — roughly <strong>9% gross revenue churn</strong> — and a median net revenue retention of 102% once expansion is counted. Churn is consistently heavier at low ACV and lighter at high ACV.</p><table style="width:100%;border-collapse:collapse;margin:1em 0;font-size:.95em"><thead><tr><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">Annual contract value (ACV)</th><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">Median gross revenue retention</th><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">≈ Annual gross revenue churn</th></tr></thead><tbody><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">Under $12K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">90%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~10%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">$12K–$25K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">90%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~10%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">$25K–$50K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">92%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~8%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">$50K–$100K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">93%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~7%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">$100K–$250K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">93%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~7%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">Over $250K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">93%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~7%</td></tr></tbody></table><p style="font-size:.82em;color:#888;margin:-.3em 0 1.4em">Source: SaaS Capital, <a style="color:#888" href="https://www.saas-capital.com/wp-content/uploads/2023/05/RB28WS1-2023-B2B-SaaS-Retention-Benchmarks.pdf">2023 B2B SaaS Retention Benchmarks</a> (~1,500 private B2B SaaS companies). Most recent: Benchmarkit's 2025 report puts FY2024 median gross retention at 88% and net retention at 101%.</p><p><strong>Growth stage:</strong> young companies often post inflated gross retention (~92%) that settles near 90% as customer cohorts mature. <strong>Monthly note:</strong> Recurly reports ~3.3% average <em>monthly</em> subscriber churn (3.8% for software &amp; business services), but that dataset skews to self-serve/consumer subscriptions and is not comparable to annual B2B logo churn — <a style="color:#888" href="https://recurly.com/research/churn-rate-benchmarks/">Recurly</a>.</p>
```

**2. `benchmarks/revenue-concentration-benchmarks.html`** — find and replace this exact paragraph (currently the sole line 74):
```html
<p>Early-stage SaaS often has high concentration (one customer = 20%+ of revenue). This is normal below $2M ARR. Above $5M ARR, no single customer should exceed 15%. Above $10M ARR, top-3 customers should account for <25% combined. These are acquisition-readiness thresholds.</p>
```
with:
```html
<h3 style="font-size:1.15em;font-weight:700;margin:1.6em 0 .4em">What the benchmarks show</h3><p>There is no single "safe" number, but M&amp;A diligence practice converges on thresholds for how much revenue can sit with one customer before it becomes a deal risk.</p><table style="width:100%;border-collapse:collapse;margin:1em 0;font-size:.95em"><thead><tr><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">Largest customer's share of revenue / ARR</th><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">How diligence typically treats it</th></tr></thead><tbody><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">Under 10%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">Healthy — generally not a concentration flag</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">10–20%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">Caution — disclose, diligence, and often price in</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">Over 20%</td><td style="padding:6px 8px;border-bottom:1px solid #eee">High-risk — material dependency; may drive holdbacks or earnouts</td></tr></tbody></table><p style="font-size:.82em;color:#888;margin:-.3em 0 1.4em">Risk-zone framing: Website Closers; the 15–20% single-customer "price-it-in" threshold: FE International, <a style="color:#888" href="https://www.feinternational.com/blog/saas-due-diligence-checklist-buyers">SaaS Due Diligence Checklist</a>.</p><p><strong>Why 10% is the line:</strong> US GAAP (FASB ASC 280) requires public companies to disclose any single customer at ≥ 10% of revenue — the origin of the 10% materiality threshold used in quality-of-earnings reviews. <strong>Top 5:</strong> the five largest customers exceeding ~25% of revenue is a commonly cited red flag — <a style="color:#888" href="https://www.wallstreetprep.com/knowledge/customer-concentration/">Wall Street Prep</a>.</p>
```

**3. `benchmarks/logo-retention-benchmarks.html`** — find and replace this exact paragraph (currently the sole line 74):
```html
<p>Seed-stage SaaS averages 60-70% annual logo retention. Series A improves to 75-85%. Growth-stage targets 85-95%. If a Series A company claims 95% logo retention, verify — it's possible but uncommon. Benchmarks help acquirers calibrate expectations before diligence.</p>
```
with:
```html
<h3 style="font-size:1.15em;font-weight:700;margin:1.6em 0 .4em">What the benchmarks show</h3><p>Primary benchmarking sources report <em>revenue</em> retention rather than count-based "logo" retention. The clearest published signal is that gross revenue retention rises with ACV, longer contract terms, and company maturity.</p><table style="width:100%;border-collapse:collapse;margin:1em 0;font-size:.95em"><thead><tr><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">Segment</th><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #1a1a1a">Median gross revenue retention</th></tr></thead><tbody><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">ACV under $25K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">90%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">ACV over $25K</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~93%</td></tr><tr><td style="padding:6px 8px;border-bottom:1px solid #eee">Overall private B2B SaaS</td><td style="padding:6px 8px;border-bottom:1px solid #eee">~91%</td></tr></tbody></table><p style="font-size:.82em;color:#888;margin:-.3em 0 1.4em">Source: SaaS Capital, <a style="color:#888" href="https://www.saas-capital.com/wp-content/uploads/2023/05/RB28WS1-2023-B2B-SaaS-Retention-Benchmarks.pdf">2023 B2B SaaS Retention Benchmarks</a>.</p><p><strong>Contract terms:</strong> companies on month-to-month and annual terms show similar median gross retention (~90%); multi-year contracts retain materially better. <strong>Company stage:</strong> gross retention is inflated (~92%) at young companies and stabilizes near 90% as cohorts age.</p>
```

Also update each file's FAQ answer to "Where does this benchmark data come from?" (currently the generic "compiled from publicly available SaaS industry reports, operator surveys, and aggregated anonymized data from SaaS analytics platforms") to name the actual sources now cited in the body — e.g. *"Compiled from named public sources including SaaS Capital, Benchmarkit, Recurly, FE International, and Wall Street Prep — see citations in the section above."* — so the FAQ schema doesn't contradict the more specific sourced content now sitting above it on the same page.

**Verification (before commit, per file):**
```bash
cd ~/churnlens
for f in saas-churn-rate revenue-concentration-benchmarks logo-retention-benchmarks; do
  grep -q "SaaS Capital" "benchmarks/$f.html" && echo "$f: OK, source citation present" || echo "$f: FAIL, no citation found"
done
python3 -c "
import re
for f in ['benchmarks/saas-churn-rate.html','benchmarks/revenue-concentration-benchmarks.html','benchmarks/logo-retention-benchmarks.html']:
    html = open(f, encoding='utf-8').read()
    # crude well-formedness check: tag counts roughly balance
    for tag in ['table','tr','td','th']:
        opens = len(re.findall(f'<{tag}[ >]', html))
        closes = len(re.findall(f'</{tag}>', html))
        assert opens == closes, f'{f}: unbalanced <{tag}> tags ({opens} open vs {closes} close)'
    print(f, 'OK — table tags balanced')
"
```

### TASK-02: `saas-valuation-multiples.html` — flag only, do not fabricate a source

Unlike the three pages above, `benchmarks/saas-valuation-multiples.html`'s claim ("A SaaS company with <5% annual churn and diversified revenue typically commands 6-10x ARR...2-4x...") has **no corresponding entry** in `CHURNLENS_BENCHMARK_DATA` — there is no pre-existing sourced version of this content to restore. Do not write a source citation you cannot verify, and do not remove the existing copy (it's directionally plausible SaaS-multiple commentary, just unsourced, not fabricated-sounding in the way the other three were). Flag this in your execution log as a real content gap for the owner: this page needs actual valuation-multiple research (e.g. SaaS Capital's or Bessemer's public multiples data) added by a future pass, same pattern as the other three once sourced.

### TASK-03: Add contextual "Related comparisons" links to the 4 `/alternatives-to/*` pages

**Files:** `~/churnlens/alternatives-to/baremetrics.html`, `chartmogul.html`, `churnzero.html`, `profitwell.html` (4 leaf pages total — confirmed exact count via `ls alternatives-to/*.html`, excluding `index.html`)

**Root cause (confirmed):** Each of these 4 pages has only 7 total internal links, all from the global nav/footer — zero in-body contextual links to sibling comparison pages, despite there being 3 obvious topically-related siblings for each one.

**Fix:** Insert a "Related comparisons" block immediately before the `<footer>` tag in each file, linking to the other 3 sibling pages plus the `/benchmarks` hub. Use this exact pattern (adjust which 3 siblings are listed per file — never link a page to itself):

```html
<h2>Related Comparisons</h2>
<ul>
<li><a href="https://churnlens.site/alternatives-to/chartmogul">ChurnLens vs ChartMogul</a></li>
<li><a href="https://churnlens.site/alternatives-to/churnzero">ChurnLens vs ChurnZero</a></li>
<li><a href="https://churnlens.site/alternatives-to/profitwell">ChurnLens vs ProfitWell</a></li>
<li><a href="https://churnlens.site/benchmarks">SaaS Benchmarks for Due Diligence</a></li>
</ul>
```
(shown for `baremetrics.html` — swap in the correct 3 non-self siblings for each of the other 3 files).

**Verification (before commit):**
```bash
cd ~/churnlens
for f in baremetrics chartmogul churnzero profitwell; do
  count=$(grep -o 'href="https://churnlens.site/alternatives-to/[a-z]*"' "alternatives-to/$f.html" | grep -v "/alternatives-to/$f\"" | grep -c "alternatives-to")
  echo "$f: $count sibling links (expect 3)"
done
```

---

## 2. P2 — MEDIUM

### TASK-04: Populate the empty Organization `sameAs` array

**File:** `~/churnlens/index.html` (and check if the Organization block is duplicated on other pages — `grep -rl '"@type": "Organization"' *.html`), `sameAs` array currently `[]`.

Only add real, already-owned, already-verifiable profile URLs — do not fabricate. Check whether any of the churnlens directory-listing submissions (G2/Capterra/AlternativeTo/TrustRadius, referenced in prior portfolio memory as submitted/rebased to churnlens.site) have gone live and produced a real public profile URL; if so, add those. If the only asset available is a GitHub org or X/Twitter handle already linked elsewhere on the site (check the footer/nav for any existing social links you can reuse), add that. If nothing genuinely real and owned can be confirmed, leave `sameAs` empty rather than inventing an entry — flag the gap in your execution log instead.

**Verification (before commit):**
```bash
cd ~/churnlens
grep -A5 '"sameAs"' index.html   # manually confirm every URL added is real and was found elsewhere on the live site, not invented
```

---

## 3. Findings from the source audit that did NOT reproduce — corrected here

- **"Two `<script src=\"/ux.js\">` tags load without defer/async"** — false as stated. Both occurrences (`index.html` lines 168 and 535) already have `defer` set: `<script src="/ux.js" defer></script>`. No action needed.

---

## 4. Deploy protocol — follow exactly, in order

1. Re-run the §0.1 collision check. If clear, proceed. Given the dirty tree noted there, re-check immediately before your final commit too.
2. Make TASK-01, TASK-03, and (if a real profile URL was found) TASK-04 edits.
3. Run every verification command from each task. All must pass before committing.
4. Commit (stage only the specific files each task names — do not sweep up the pre-existing dirty files from §0.1):
   ```bash
   cd ~/churnlens
   git add benchmarks/saas-churn-rate.html benchmarks/revenue-concentration-benchmarks.html benchmarks/logo-retention-benchmarks.html alternatives-to/baremetrics.html alternatives-to/chartmogul.html alternatives-to/churnzero.html alternatives-to/profitwell.html
   git commit -m "fix: restore sourced benchmark data (SaaS Capital/Benchmarkit/FE International/Recurly/Wall Street Prep) to 3 live benchmark pages + add contextual related-comparison links to alternatives-to pages"
   ```
   (Add `index.html` to this commit only if TASK-04 found a real profile URL to add.)
5. Deploy (static site, no build step):
   ```bash
   vercel --prod --yes --scope sales-3429s-projects
   ```

**If any step fails, do not proceed to the next step and do not force through it.** Report the exact error in your execution log (§7) and stop.

---

## 5a. Post-deploy verification — mandatory

```bash
# 1. Confirm sourced benchmark content is live
for f in saas-churn-rate revenue-concentration-benchmarks logo-retention-benchmarks; do
  curl -s "https://churnlens.site/benchmarks/$f" | grep -c "SaaS Capital\|Benchmarkit\|FE International\|Recurly\|Wall Street Prep"
done   # each must be >=1

# 2. Confirm related-comparison links are live on all 4 alternatives-to pages
for f in baremetrics chartmogul churnzero profitwell; do
  curl -s "https://churnlens.site/alternatives-to/$f" | grep -c "Related Comparisons"
done   # each must be 1

# 3. Confirm no unrelated regression — spot-check homepage and a few other routes
for path in / /benchmarks /alternatives-to /about /faq; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://churnlens.site$path")
  echo "$path: $code"
done   # all must be 200
```

## 5b. Rollback plan — use immediately if §5a verification fails

```bash
# Option A — instant: roll the Vercel alias back to the last known-good deployment
vercel rollback --scope sales-3429s-projects

# Option B — revert and redeploy clean
cd ~/churnlens
git revert --no-edit HEAD
vercel --prod --yes --scope sales-3429s-projects
```

---

## 7. Execution log — append your results here as you work

```
### 2026-07-21 run
- TASK-01: done — restored sourced content (with real citations) to 3 of 4 benchmark pages, verified live
- TASK-02: flagged for owner — saas-valuation-multiples.html has no pre-existing sourced data to restore, needs fresh research
- TASK-03: done — added Related Comparisons block (3 sibling links + benchmarks hub) to all 4 alternatives-to pages, verified live
- TASK-04: [outcome — real profile URL found and added / no real profile found, left empty and flagged]
- Confirmed already-correct (no action taken): ux.js already has defer on both occurrences
- Deploy: vercel --prod --yes succeeded
- Post-deploy verification: all checks passed
- No rollback needed
```

---

## 6. Owner-gated — do not execute autonomously

- **CSP `unsafe-inline` → nonce/hash migration** — the audit's own fix note explicitly says "test carefully in a preview deploy before promoting to prod" and warns against introducing `require-trusted-types-for` while doing so (the exact landmine that blanked two sibling sites). This is real security-hardening work with real regression risk on a static site with no build pipeline to catch mistakes before they're live — not something to attempt autonomously in this brief.
- **Named founder bio on `/about`** — the E-E-A-T finding about missing founder credentials/LinkedIn is real, but writing biographical copy about a real person is not something this brief authorizes.
- **`saas-valuation-multiples.html` sourcing** (TASK-02) — flag only, don't fabricate a citation.
- **`sameAs` population** (TASK-04) — only with confirmed-real URLs; if none found, leave empty rather than inventing.
- Anything not listed as a numbered TASK above.

---

**End of brief.** Work top to bottom (P1 → P2), verify after the deploy per §5a before considering the run complete, and re-run the §0.1 collision check both before starting and immediately before your final commit given this repo's tree was found dirty at brief-writing time.
