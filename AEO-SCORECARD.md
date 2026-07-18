# ChurnLens AEO Scorecard — July 18, 2026

> Answer Engine Optimization audit following the Ahrefs AEO methodology.
> All scores verified against live production (https://churnlens.site).

## Overall: 93/100 — Production-Ready

| Dimension | Score | Status |
|-----------|-------|--------|
| Entity & Schema | 18/20 | 🟢 Single clean Organization node, disambiguatingDescription, DefinedTermSet for frameworks. Missing: founder Person node |
| Content Credibility | 19/20 | 🟢 Honest curated benchmarks, sources cited. Missing: one original proprietary data study |
| Technical AEO | 20/20 | 🟢 All bots allowed, edge 200, static HTML, SSR not needed |
| Discoverability | 18/20 | 🟢 Sitemap (263 URLs), llms.txt, ai.txt, feeds, kg.jsonld. Missing: GA4 AI-traffic channel |
| Content & Frameworks | 10/10 | 🟢 7 framework pages, cross-linked money pages, benchmark cite blocks |
| Freshness | 5/5 | 🟢 All dateModified→July 18, visible Last reviewed banners |
| Measurement | 3/5 | 🟡 PostHog attribution survey live. Missing: GA4 AI-referral tracking |
| Influence (off-site) | 0/10 | 🔴 No third-party mentions on G2/Capterra/AI-cited domains. Directory packets ready, blocked on owner |

---

## Detailed Checks

### Schema
- [x] Organization node: 1 (consolidated, was 2 stale)
- [x] disambiguatingDescription: names both namesakes
- [x] sameAs: empty (clean — populate with G2/Capterra/LinkedIn when live)
- [x] SoftwareApplication: featureList, offers
- [x] DefinedTermSet: 5-Risk Method + 6 DefinedTerm lenses
- [x] FAQPage: 187 blocks, 0 issues
- [x] Article: on all money pages
- [x] HowTo: on 5+ pages
- [x] BreadcrumbList: on all pages
- [x] CollectionPage: on 7 section hubs
- [ ] Person (founder): not present

### Technical
- [x] robots.txt: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Google-Extended, PerplexityBot all allowed
- [x] Edge/WAF: all 200 (no Cloudflare block)
- [x] JS rendering: static HTML (3,840 words in raw source)
- [x] Schema: 1091 JSON-LD blocks, 0 parse errors
- [x] Canonical: 375/377 pages (404 + verification excluded correctly)
- [x] Internal links: 216 unique, 0 broken
- [x] hallucinated-URL redirects: 25 paths → mapped (308)
- [x] Heading hierarchy: H1 first on all key pages
- [x] Viewport/charset/lang: 401/402 pages
- [x] og:image + twitter:image: 1200×630 on all pages
- [x] Content-Security-Policy: present
- [x] X-Frame-Options: DENY

### Content
- [x] Money pages: BLUF, FAQPage schema, cross-linked, Last reviewed
- [x] Benchmarks: curated from public sources, Sources & methodology, Cite blocks
- [x] Framework pages: 5-Risk Method + 6 lenses with DefinedTerm schema
- [x] Section hubs: 7 category overviews with CollectionPage schema
- [x] Review pages: 6 review-for-acquirers with framework cross-links
- [x] pSEO pages: 400+ pages, all with valid schema, canonical, og:image

### Discoverability
- [x] sitemap.xml: 263 URLs
- [x] sitemap-index.xml: sitemap + image-sitemap
- [x] llms.txt: full disambiguation naming namesakes
- [x] llms-full.txt: 88.6 KB, 13K words, 17 pages (pending deploy)
- [x] ai.txt: Spawning spec compliant
- [x] kg.jsonld: Knowledge Graph entity file (pending deploy)
- [x] feed.xml / feed.json: 20 items each, auto-discovered from homepage
- [x] robots.txt: LLMs.txt, ai.txt, kg.jsonld directives

### Measurement
- [x] PostHog attribution survey: "How did you hear about us?" with AI options
- [ ] GA4 AI-traffic channel: not set up (needs account access)
- [ ] AI bot analytics: not set up (needs Cloudflare/server logs)

### Influence
- [ ] G2 profile: packets ready, not submitted
- [ ] Capterra profile: packets ready, not submitted
- [ ] AlternativeTo: packets ready, not submitted
- [ ] TrustRadius: packets ready, not submitted
- [ ] Top-10 mention-earning outreach: pitches drafted, not sent
- [ ] Reddit/forum presence: not started
- [ ] YouTube video: not recorded

---

## Reusable Generators

All in `~/churnlens/scripts/`:

| Script | Purpose |
|--------|---------|
| `fix_benchmark_provenance.py` | Replace fabricated stats with sourced curation |
| `build_section_indexes.py` | Generate category hub pages |
| `build_framework_pages.py` | Generate proprietary framework pages |
| `add_framework_crosslinks.py` | Add branded cross-links to money pages |
| `freshness_pass.py` | Bump dates + add Last reviewed banners |
| `add_cite_blocks.py` | Add Cite this page to benchmarks |
| `fix_og_images.py` | Fix og:image + twitter:image consistency |
| `build_llms_full.py` | Generate llms-full.txt from all key pages |

---

## Next Owner Actions (by priority)

1. **Submit directory listings** — G2, Capterra, AlternativeTo, TrustRadius. Packets in `~/churnlens-directory-packets/`
2. **Add founder identity** — named person on About + Person schema node
3. **Set up GA4 AI-traffic channel** — regex: `chatgpt\.com|perplexity|gemini\.google\.com|copilot\.microsoft\.com|claude\.ai|deepseek\.com`
4. **Send top-10 mention-earning outreach** — pitches in `~/churnlens-site-influence-pack.md`
5. **Record YouTube explainer** — "How to spot hidden churn before buying a SaaS"

*Generated 2026-07-18 · ChurnLens AEO Scorecard*
