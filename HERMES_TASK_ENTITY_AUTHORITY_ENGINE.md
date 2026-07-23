# HERMES TASK — churnlens.site: Entity & Knowledge-Graph Authority Engine

> **Runbook for:** Hermes Agent running DeepSeek v4 Pro
> **Mode:** AUTONOMOUS — build, validate, commit, deploy without human intervention, subject to the fail-safes in §1.
> **Repo:** `~/churnlens` (static HTML site, `outputDirectory: "."`, ~923 pages). Deploy via Vercel CLI.
> **Deploy:** `npx vercel deploy --prod --archive=tgz --yes` (project `churnlens`, org `team_VqIhc5enyfXN91ZlfQhyz2bC`).
> **Author of runbook:** Claude (2026-07-21), grounded in a live audit.

---

## 0. What you are building and why

ChurnLens (churnlens.**site**) is **buyer-side SaaS due diligence** — acquirers, PE, and M&A analysts upload a target's subscription CSVs and get a churn/revenue-quality risk report. The site is technically clean with ~923 pages, but every audit reaches the same verdict: **0 citations despite clean pages — the gap is entity/authority, not content.** AI engines and search don't confidently know *what ChurnLens is*, so it never gets surfaced or cited for its winnable, unclaimed wedge: **"SaaS due diligence for acquirers."**

The audit found the entity layer is present but **broken and self-contradicting**, which actively prevents recognition:
- `knowledge-graph.json` has **`sameAs: []`**, a **generic "churn-prediction platform" description** (not the acquirer-DD positioning), and the **two-word "Churn Lens"** brand (the brand is one-word "ChurnLens"). The machine-readable entity file tells AI engines the wrong thing.
- On-page `sameAs` is just `["https://github.com/kindrat86"]` — an **entity island**: no founder `Person`, no corroboration, no link to the sibling product network.
- Three same-name namesakes exist (churnlens.**io**, churnlens.**tech**) that ChurnLens.site must be disambiguated from — or AI conflates them.

You will ship the **Entity & Knowledge-Graph Authority Engine**: one canonical entity source of truth, injected consistently across all pages, with the machine-readable files aligned, a founder `Person` for E-E-A-T, corroborating `sameAs`, `SoftwareApplication` + real `Offer`, and hard namesake disambiguation. This is the reliable 2026 GEO/AEO lever for **owning an entity** — the prerequisite to being the cited answer for "best SaaS due diligence tool for acquirers."

---

## 1. 🚨 GUARDRAILS + FAIL-SAFES — READ FIRST

### 1a. NEVER fabricate. Two live issues to respect.
- **`sameAs` must contain only VERIFIED-LIVE URLs.** Today that's `https://github.com/kindrat86`. Do NOT add directory-listing URLs (G2/Capterra/etc.) that aren't live yet — a `sameAs` pointing at a 404 is a negative signal. Leave an owner-TODO to add them once the listings (`~/churnlens-directory-packets/`) are submitted.
- **The founder `Person` needs a real name the owner must supply.** Do NOT invent a founder name. Ship the `Person` node with a placeholder + owner-TODO, or omit it until provided. Never fabricate identity.
- **No fake reviews, ratings, or `aggregateRating`.**

### 1b. FABRICATION CLEANUP is a required gate (existing live issue).
- These pages still contain fabricated volume claims ("2,400+", "thousands of SaaS", "analysis of thousands"): `reviews/profitwell-review-for-acquirers.html` (+ `/index.html`), `reviews/chartmogul-review-for-acquirers.html` (+ `/index.html`).
- **Fix them:** open each, locate the fabricated quantity claim, and **remove/neutralize it** — replace with an honest statement that cites **no invented number** (e.g. "based on the metrics acquirers scrutinize in diligence"). Do NOT substitute a different made-up number.
- **Gate:** after cleanup, `grep -rl "2,400\|thousands of SaaS\|analysis of thousands" . --include='*.html'` (excluding node_modules) MUST be empty. If not empty, the deploy does not proceed.

### 1c. Brand + positioning are fixed.
- Brand is **one-word "ChurnLens"** everywhere. Fix any "Churn Lens". Do not add it to `alternateName`.
- Positioning is **buyer-side / acquirer due diligence**, NOT generic "churn-prevention/retention platform." Use the acquirer-DD description (below), not the stale generic one.
- **Namesake disambiguation is mandatory** in the entity: ChurnLens.site is independent and unaffiliated with churnlens.io (retention automation) or churnlens.tech (churn prediction).

### 1d. Uncommitted-work hazard.
- The working tree has **pre-existing uncommitted changes** (real benchmark/data work per project state: `M pricing.html dream100.html vercel.json`, `?? data/ 7-revenue-churn-red-flags.html affiliate.html …`). These are legitimate, finished work. Your deploy WILL include them (this is a static site; deploy uploads the tree). That is acceptable for churnlens — but you must NOT ship anything unfinished. The **fabrication gate (§1b)** and the **render check (§6)** are your safety net. If either fails, do not deploy.
- `git add` your OWN files explicitly; leave the pre-existing changes as-is (do not revert them — they're wanted).

### 1e. Same-@id enrichment, not duplication.
- Inject the canonical graph using **consistent @ids** (`#organization`, `#software`, `#website`, `#founder`). Search engines **merge nodes with the same @id** — so a page that already has `#organization` gets *enriched* (union of properties), not duplicated. This is safe. (Only *different* @ids for the same entity — e.g. `#org` vs `#organization` — cause the conflict bug; if you find a stray `#org`, align it to `#organization`.)

### 1f. git author + idempotency.
- `git config user.email` must be `sales@sipiteno.com` before deploy (Vercel blocks non-team authors).
- All scripts idempotent (marker-based); safe to re-run.

---

## 2. Deliverable A — `entity.json` (canonical source of truth)

Create `entity.json` at repo root. Fill `PRICE_*` from the real tiers in `pricing.html` (read it: today it shows Free $0 and $49/mo — verify and use the actual current tiers). Leave the founder name as an owner-TODO.

```json
{
  "brand": "ChurnLens",
  "url": "https://churnlens.site",
  "description": "ChurnLens is a buyer-side SaaS due-diligence tool. Acquirers, private-equity firms, and M&A analysts upload a target company's subscription CSVs and get a revenue-quality and churn-risk report in minutes — hidden churn, revenue concentration, revenue decay, and a benchmarked revenue-quality score.",
  "disambiguatingDescription": "ChurnLens at churnlens.site is an independent buyer-side due-diligence tool used by acquirers and PE/M&A analysts to assess a SaaS target's revenue and churn quality before purchase. It is unaffiliated with the similarly named churnlens.io (retention automation) or churnlens.tech (churn prediction).",
  "knowsAbout": ["SaaS due diligence","buyer-side due diligence","revenue quality analysis","customer churn risk","revenue concentration risk","revenue decay","MRR/ARR analysis","SaaS acquisitions","quality of earnings","M&A diligence"],
  "sameAs": ["https://github.com/kindrat86"],
  "sameAs_owner_todo": "Add the live G2 / Capterra / AlternativeTo / TrustRadius profile URLs here once the listings in ~/churnlens-directory-packets/ are submitted. Only add URLs that resolve 200.",
  "founder": { "name": "OWNER_TODO_FOUNDER_NAME", "sameAs": ["https://github.com/kindrat86"] },
  "offers": [
    { "name": "Free", "price": "0", "priceCurrency": "USD" },
    { "name": "Pro", "price": "49", "priceCurrency": "USD", "unit": "MONTH" }
  ],
  "contactEmail": "hello@churnlens.site"
}
```
> Confirm the offer tiers against `pricing.html` before writing — if the live tiers differ, use the live ones. Never invent a price.

---

## 3. Deliverable B — `scripts/inject_entity_graph.py` (sitewide canonical @graph)

Mirror the repo's existing `inject_enhance.py` pattern. Builds the canonical `@graph` from `entity.json` and injects it (idempotent, marker-based) into every `.html`. Consistent @ids → enrichment, not duplication.

```python
#!/usr/bin/env python3
"""
inject_entity_graph.py — inject ONE canonical entity @graph into every page.
Consistent @ids (#organization/#software/#website/#founder) so engines MERGE
(enrich) rather than duplicate. Idempotent (marker). Never fabricates.
"""
import json, os, re, sys

ROOT = os.getcwd()
MARKER = "<!-- entity-graph -->"
E = json.load(open(os.path.join(ROOT, "entity.json"), encoding="utf-8"))

org = {
    "@type": "Organization", "@id": E["url"] + "/#organization",
    "name": E["brand"], "url": E["url"],
    "description": E["description"], "disambiguatingDescription": E["disambiguatingDescription"],
    "knowsAbout": E["knowsAbout"], "sameAs": E["sameAs"],
    "logo": {"@type": "ImageObject", "url": E["url"] + "/og.png"},
    "contactPoint": {"@type": "ContactPoint", "email": E["contactEmail"], "contactType": "customer support"},
}
software = {
    "@type": "SoftwareApplication", "@id": E["url"] + "/#software",
    "name": E["brand"], "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
    "url": E["url"], "description": E["description"], "publisher": {"@id": E["url"] + "/#organization"},
    "offers": [{"@type": "Offer", "name": o["name"], "price": o["price"], "priceCurrency": o["priceCurrency"]} for o in E["offers"]],
}
website = {"@type": "WebSite", "@id": E["url"] + "/#website", "url": E["url"], "name": E["brand"], "publisher": {"@id": E["url"] + "/#organization"}}
graph = [org, software, website]

# Founder Person — only if a real name is present (never fabricate)
fname = E.get("founder", {}).get("name", "")
if fname and "OWNER_TODO" not in fname:
    person = {"@type": "Person", "@id": E["url"] + "/#founder", "name": fname, "sameAs": E["founder"].get("sameAs", []), "worksFor": {"@id": E["url"] + "/#organization"}}
    graph.append(person)
    org["founder"] = {"@id": E["url"] + "/#founder"}
else:
    print("  NOTE: founder name is an owner-TODO — Person node omitted (no fabrication).")

block = MARKER + '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")) + "</script>"
block_re = re.compile(re.escape(MARKER) + r'<script type="application/ld\+json">.*?</script>', re.S)

SKIP = {"node_modules", ".git", ".vercel", ".well-known"}
count = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP]
    for fn in filenames:
        if not fn.endswith(".html"): continue
        p = os.path.join(dirpath, fn)
        try: t = open(p, encoding="utf-8").read()
        except Exception: continue
        if "</head>" not in t: continue
        new = block_re.sub(block, t) if MARKER in t else t.replace("</head>", block + "\n</head>", 1)
        # align stray #org -> #organization (turn-1 dup-node bug), leaving other schema intact
        new = new.replace('"@id": "' + E["url"] + '/#org"', '"@id": "' + E["url"] + '/#organization"')
        if new != t:
            open(p, "w", encoding="utf-8").write(new); count += 1
print(f"✓ entity graph injected/updated on {count} pages")
```

---

## 4. Deliverable C — align the machine-readable files

### 4a. Rewrite `knowledge-graph.json` to match `entity.json`
Replace the stale content so it carries the **acquirer-DD description**, **one-word brand** (drop "Churn Lens" from `alternateName`), the **real `sameAs`** (github only for now), `knowsAbout` (acquirer-DD terms), the namesake `disambiguatingDescription`, `SoftwareApplication` with the real `offers`, and the founder ref (only if a real name exists). It must be internally consistent with the injected on-page graph (same @ids, same values).

### 4b. Update the entity block in `llms.txt` (and `llms-full.txt`)
Ensure the top-of-file summary uses the acquirer-DD positioning, one-word brand, and the namesake disambiguation sentence. AI crawlers read this first — it must say the same thing as the schema.

---

## 5. Deliverable D — fabrication cleanup (required, §1b)
Fix `reviews/profitwell-review-for-acquirers.html` (+`/index.html`) and `reviews/chartmogul-review-for-acquirers.html` (+`/index.html`): remove the "2,400+/thousands of SaaS/analysis of thousands" claims, replacing with an honest statement carrying no invented number. Re-verify the grep is empty (§6).

---

## 6. RUN + VALIDATE (before deploy) — all must pass

```bash
cd ~/churnlens
python3 scripts/inject_entity_graph.py

# a) entity.json valid + graph injected widely
node -e "JSON.parse(require('fs').readFileSync('entity.json','utf8'));console.log('✓ entity.json valid')"
grep -rl "entity-graph" . --include='*.html' | grep -v node_modules | wc -l    # expect hundreds

# b) injected JSON-LD parses on a sample page
node -e "const h=require('fs').readFileSync('index.html','utf8');const m=h.match(/<!-- entity-graph --><script type=\"application\/ld\+json\">([\s\S]*?)<\/script>/);JSON.parse(m[1]);console.log('✓ entity @graph parses')"

# c) knowledge-graph.json aligned (acquirer-DD desc, non-empty sameAs, one-word brand)
node -e "const k=require('./knowledge-graph.json');if(JSON.stringify(k).includes('Churn Lens'))throw'two-word brand still present';if(!/(due diligence|acquirer|buyer-side)/i.test(JSON.stringify(k)))throw'stale generic description';console.log('✓ knowledge-graph aligned')"

# d) FABRICATION GATE (must be empty)
if grep -rl "2,400\|thousands of SaaS\|analysis of thousands" . --include='*.html' | grep -v node_modules; then echo "FAIL: fabricated claims remain"; exit 1; else echo "✓ no fabricated claims"; fi

# e) no fabricated sameAs (only verified-live URLs); founder not fabricated
node -e "const e=require('./entity.json');if(e.sameAs.some(u=>!u.startsWith('https://github.com/')&&!u.startsWith('https://www.linkedin.com/')&&!u.startsWith('https://www.crunchbase.com/')))console.log('REVIEW sameAs manually');if((e.founder.name||'').includes('OWNER_TODO'))console.log('✓ founder left as owner-TODO (no fabrication)')"

# f) namesake disambiguation present
grep -c "churnlens.io" index.html   # expect >=1 (disambiguation shipped)
```
If (d) fails, STOP and finish §5. If (b)/(c) fail, fix and re-run.

---

## 7. DEPLOY (autonomous)

```bash
cd ~/churnlens
git config user.email    # must be sales@sipiteno.com; if blank: git config user.email sales@sipiteno.com
git checkout -b entity-authority-engine
git add entity.json scripts/inject_entity_graph.py knowledge-graph.json llms.txt llms-full.txt \
        reviews/profitwell-review-for-acquirers.html reviews/profitwell-review-for-acquirers/index.html \
        reviews/chartmogul-review-for-acquirers.html reviews/chartmogul-review-for-acquirers/index.html \
        $(grep -rl "entity-graph" . --include='*.html' | grep -v node_modules)
git commit -m "Add entity & knowledge-graph authority layer + fix fabricated review stats"

# Static prebuilt deploy with archive flag (923 pages)
npx vercel deploy --prod --archive=tgz --yes

# --- Verify live ---
sleep 20
curl -s https://churnlens.site/ | grep -c "entity-graph"                     # expect >=1
curl -s https://churnlens.site/knowledge-graph.json | grep -c "due diligence" # expect >=1
curl -s https://churnlens.site/ | grep -c "churnlens.io"                      # expect >=1 (namesake disambig live)
# render sanity: homepage not blank
test $(curl -s https://churnlens.site/ | wc -c) -gt 5000 && echo "✓ homepage renders"
```
If the deploy errors on auth (memory: churnlens deploys have been owner-gated), report it and stop — do not force.

---

## 8. POST-DEPLOY — the corroboration multiplier (owner-gated)

On-site entity is the **prerequisite**; citations compound when the entity is **corroborated off-site**. The packets are ready:
1. **Submit the directory listings** in `~/churnlens-directory-packets/` (G2, Capterra, AlternativeTo, TrustRadius) — each is both a backlink and a `sameAs` corroboration. Update `entity.json` `sameAs` + `knowledge-graph.json` with the live profile URLs afterward, then re-run the injector + redeploy.
2. **Founder identity:** provide the real founder name so the `Person` node ships (strong E-E-A-T signal).
3. **Google Search Console:** request re-indexing of the homepage + key hub pages so the corrected entity is re-read.
4. Validate the entity in Google's Rich Results Test.

---

## 9. Expected results (honest, mechanism-based — estimates, not guarantees)

**This is the entity/identity layer — the documented #1 gap.** It doesn't add pages; it makes AI engines and search *correctly identify and trust* ChurnLens as the buyer-side SaaS DD entity, which is the prerequisite for the "0 citations" problem to move.

| Effect | Mechanism | Realistic outcome | When |
|---|---|---|---|
| **Correct entity recognition** | Consistent, deduped @graph + aligned `knowledge-graph.json`/`llms.txt` (no more contradictory "churn-prevention platform" / two-word brand) | AI engines and Google stop conflating ChurnLens.site with churnlens.io/.tech; brand SERP consolidates | 4–10 weeks |
| **AI-engine citation for the wedge** | Corroborated entity + clear "buyer-side SaaS due diligence for acquirers" positioning + machine-readable facts | Move from **0 → being named** for "SaaS due diligence tool / revenue-quality assessment for acquirers" — the unclaimed wedge | 8–16 weeks (compounds with §8) |
| **Rich-results eligibility** | `SoftwareApplication` + real `Offer` | Eligible for product rich results / AI product recommendations | 2–6 weeks |
| **Trust/quality** | Removing fabricated stats | Removes a suppression/trust risk on the review pages | immediate |

**Straight talk:**
- On-site entity is **table-stakes, not a standalone skyrocket** — the compounding citation growth comes from pairing it with the **off-site corroboration in §8** (the ready directory packets). This runbook does the on-site half fully and autonomously and hands you the off-site half (owner-gated) as a concrete, ready checklist.
- For a technically-clean 923-page site stuck at 0 citations, *fixing the broken/contradictory entity* is the single highest-leverage on-site change — a mislabeled entity can't be cited correctly no matter how good the content is.
- Measure: brand-name SERP completeness, AI-answer mentions for "SaaS due diligence for acquirers" (manual prompt checks in ChatGPT/Perplexity monthly), and referring domains after §8.

---

## 10. Rollback
Additive (entity.json + injector + injected `<!-- entity-graph -->` blocks + aligned JSON files + review-page text fixes). Roll back: `git revert` the commit, redeploy. The injector is marker-scoped, so reverting cleanly removes the injected blocks.

### Definition of done
- [ ] `entity.json` created with correct acquirer-DD positioning, one-word brand, real `sameAs` (github only), founder owner-TODO, real `offers` from `pricing.html`.
- [ ] `inject_entity_graph.py` created; canonical @graph injected on all pages (consistent @ids; stray `#org` aligned).
- [ ] `knowledge-graph.json` + `llms.txt`/`llms-full.txt` aligned (acquirer-DD desc, non-empty sameAs, one-word brand, namesake disambig).
- [ ] **Fabrication gate passes** — no "2,400+/thousands of SaaS" anywhere.
- [ ] All §6 checks green; committed to a branch; deployed via Vercel prebuilt `--archive=tgz`; live checks pass.
- [ ] §8 corroboration steps handed to owner. Zero fabricated `sameAs`/founder/reviews/prices.
```
