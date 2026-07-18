#!/usr/bin/env python3
"""
ChurnLens vertical pSEO generator.
Produces /for/{industry}.html for 20 SaaS industries.
Matches the existing /for/fintech.html template structure (header nav, FAQ details, related pages, trust bar).
Uses /ux.css for styling (same as the rest of the site).
Updates sitemap.xml.
"""
import json
import re
from pathlib import Path

ROOT = Path("/Users/sipi/churnlens")
BASE = "https://churnlens.site"
TODAY = "2026-07-18"
PUBLISHED = "2026-01-15"

# 20 SaaS industries with industry-specific churn benchmarks and context.
INDUSTRIES = [
    # (slug, title-case, tagline, gross-revenue-churn%, net-revenue-churn%, logo-churn%, annual-plan-share%, key-risk, customer-profile, mrr-volatility)
    ("saas", "SaaS", "general-purpose B2B SaaS", 2.0, 1.0, 3.5, 55, "revenue concentration in the top-5 logos", "SMB and mid-market teams", "moderate"),
    ("fintech", "Fintech", "fintech and embedded-finance SaaS", 2.5, 1.5, 4.0, 65, "regulatory churn — banks pulling integrations after compliance reviews", "B2B fintech infrastructure buyers", "high"),
    ("ecommerce", "E-commerce", "e-commerce and DTC enablement SaaS", 3.5, 2.5, 6.0, 45, "merchant churn tied to seasonal ad-spend volatility and store closures", "Shopify-adjacent SMB merchants", "very high"),
    ("healthcare", "Healthcare", "healthcare and HIPAA-regulated SaaS", 1.5, 0.5, 2.5, 75, "long sales cycles hiding logo decay that lands mid-contract", "hospital systems and large clinics", "low"),
    ("edtech", "EdTech", "education technology and learning SaaS", 3.0, 2.0, 5.0, 80, "annual district procurement cycles masking summer-attrition churn", "K-12 districts and universities", "low but lumpy"),
    ("devtools", "DevTools", "developer-tools and API SaaS", 2.5, 1.5, 4.5, 60, "usage-based pricing masking logo churn behind token consumption", "engineering teams at growth-stage startups", "high"),
    ("martech", "MarTech", "marketing-technology and growth SaaS", 3.0, 2.0, 5.5, 50, "stack-consolidation churn as CMOs cut tools during budget reviews", "demand-gen and revenue-marketing teams", "high"),
    ("hr-tech", "HR Tech", "HR-technology and people-ops SaaS", 2.0, 1.0, 3.0, 70, "seat-based decay tied to client headcount reductions (silent churn)", "mid-market HR and people-ops teams", "moderate"),
    ("cybersecurity", "Cybersecurity", "cybersecurity and SecOps SaaS", 1.5, 0.5, 2.0, 72, "compliance-driven retention hiding inactive paid seats", "security and IT teams", "low"),
    ("ai-ml", "AI/ML", "AI/ML platform and model-serving SaaS", 3.0, 2.0, 5.0, 40, "hype-cycle churn — pilots that don't convert, tokens that decay invisibly", "ML and data-science teams", "very high"),
    ("proptech", "PropTech", "property-technology and real-estate SaaS", 2.5, 1.5, 4.0, 60, "transaction-volume correlation masking baseline logo retention", "brokerages and property managers", "moderate"),
    ("logistics", "Logistics", "logistics and supply-chain SaaS", 2.5, 1.5, 4.5, 55, "shipper-concentration risk — one carrier loss can gut 20% of MRR", "freight forwarders and 3PLs", "high"),
    ("media", "Media", "media and content-distribution SaaS", 3.5, 2.5, 6.0, 40, "ad-cycle correlation driving quarterly churn spikes", "publishers and streaming teams", "very high"),
    ("gaming", "Gaming", "gaming and interactive-entertainment SaaS", 3.5, 2.5, 6.5, 35, "title-lifecycle churn — studios churn the moment a game ships", "game studios and publishers", "very high"),
    ("climate-tech", "Climate Tech", "climate-technology and sustainability SaaS", 2.0, 1.0, 3.0, 65, "grant-cycle dependency masking underlying commercial retention", "sustainability and ESG teams", "low but grant-driven"),
    ("agtech", "AgTech", "agricultural-technology SaaS", 2.5, 1.5, 4.0, 70, "seasonal procurement cycles hiding logo decay between planting seasons", "agri-businesses and co-ops", "low but seasonal"),
    ("legal-tech", "Legal Tech", "legal-technology and practice-management SaaS", 1.8, 0.8, 2.8, 78, "firm-consolidation churn masked by sticky multi-year contracts", "law firms and legal-ops teams", "low"),
    ("insurtech", "Insurtech", "insurtech and insurance-carrier SaaS", 2.0, 1.0, 3.0, 75, "carrier-procurement cycles hiding mid-term renegotiation churn", "insurers and MGAs", "low"),
    ("real-estate", "Real Estate", "real-estate and brokerage SaaS", 3.0, 2.0, 5.0, 55, "market-cycle churn — agent seat counts collapse when transactions drop", "brokerages and agent teams", "high"),
    ("hospitality", "Hospitality", "hospitality and travel SaaS", 3.5, 2.5, 6.0, 50, "seasonal and event-driven churn — properties cut seats in off-seasons", "hotel groups and travel platforms", "very high"),
]


def jd(q, a):
    return {"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}}


def build_page(ind):
    slug, title, tagline, grc, nrc, lc, aps, key_risk, profile, vol = ind
    url = f"{BASE}/for/{slug}"

    page_title = f"Churn Analysis for {title} SaaS — Benchmarks & Due Diligence | ChurnLens"
    desc = (f"Industry-specific churn benchmarks for {tagline}: "
            f"{grc}% gross revenue churn, {lc}% logo churn, {aps}% annual-plan share. "
            f"Surface hidden {key_risk.split('—')[0].strip()} before acquiring a {title.lower()} SaaS.")

    faqs = [
        (f"What is a healthy logo churn rate for a {title.lower()} SaaS?",
         f"For {tagline}, a defensible logo churn rate benchmark is around {lc}% per month. ChurnLens flags targets above this band and, more importantly, looks for the gap between reported logo churn and the underlying decay signals (inactive paid accounts, declining product usage, expiring annual plans) that show the real trajectory."),
        (f"How does ChurnLens surface {key_risk.split('—')[0].strip()} in a {title.lower()} SaaS acquisition?",
         f"ChurnLens ingests the target's revenue ledger and decomposes MRR movement by cohort, plan type, and customer segment. For {tagline} it specifically isolates the {key_risk} pattern — surfacing logos that are still 'paying' on paper but exhibiting the decay signals ({profile} reducing seats, usage dropping, or annual plans not renewing on schedule) that precede a headline-churn spike 2–4 quarters later."),
        (f"Is ChurnLens suitable for acquiring {tagline}?",
         f"Yes. ChurnLens is built for SaaS acquirers, PE/M&A analysts, and searchers evaluating {tagline} businesses. Pricing plans suit deals from micro-SaaS up through lower-middle-market SaaS acquisitions. See churnlens.site for current plans."),
    ]

    article_json = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"Churn Analysis for {title} SaaS",
        "description": desc,
        "author": {"@type": "Organization", "name": "ChurnLens", "url": BASE},
        "publisher": {"@type": "Organization", "name": "ChurnLens", "url": BASE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": PUBLISHED, "dateModified": TODAY,
    }
    faq_json = {"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [jd(q, a) for q, a in faqs]}
    breadcrumb_json = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ChurnLens", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "For", "item": f"{BASE}/for"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url},
        ],
    }
    org_disambig = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "ChurnLens", "url": BASE,
        "description": "ChurnLens is a buyer-side SaaS due-diligence tool that analyzes a target's revenue concentration, logo retention, annual-plan churn risk, inactive paid accounts, and MRR decline to surface hidden churn before a SaaS acquisition.",
        "disambiguatingDescription": "ChurnLens (churnlens.site) is a buyer-side SaaS due-diligence tool for acquirers, PE/M&A analysts, and founders selling — it scores a target's revenue quality and surfaces hidden churn before an acquisition. It is an independent product, unaffiliated with churnlens.io or churnlens.tech.",
    }

    faq_visible = "\n".join(
        f'<details><summary><h3>{q}</h3></summary><p>{a}</p></details>'
        for q, a in faqs
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{page_title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="ChurnLens">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="en-US" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{desc}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="article:published_time" content="{PUBLISHED}T00:00:00Z">
<meta property="article:modified_time" content="{TODAY}T00:00:00Z">
<script type="application/ld+json">{json.dumps(article_json)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb_json)}</script>
<script type="application/ld+json">{json.dumps(faq_json)}</script>
<script type="application/ld+json">{json.dumps(org_disambig)}</script>
<link rel="stylesheet" href="/ux.css">
<script src="/ux.js" defer></script>
</head>
<body>
<header>
<nav>
<a href="{BASE}">ChurnLens</a>
<span>›</span>
<a href="{BASE}/for">For</a>
<span>›</span>
<span>{title} SaaS</span>
</nav>
</header>
<main>
<article>
<h1>Churn Analysis for {title} SaaS</h1>
<p class="lede"><strong>ChurnLens</strong> is built for acquirers evaluating {tagline}. Before you sign an LOI, surface the {key_risk.split('—')[0].strip()} that headline retention metrics hide. Here are the industry-specific churn benchmarks ChurnLens applies to {title.lower()} SaaS targets, the decay signals that matter most, and how to run the diligence in under a day.</p>

<h2>{title} SaaS churn benchmarks</h2>
<p>Acquirers evaluating {tagline} consistently underestimate how much {key_risk.split('—')[0].strip()} distorts reported retention. The benchmarks below are the defensible bands ChurnLens applies to {title.lower()} SaaS targets during diligence. A target outside these bands isn't automatically a pass — but every percentage point of gap is a dollar figure on the purchase price.</p>
<table>
<thead><tr><th>Metric</th><th>{title} benchmark</th><th>What ChurnLens flags</th></tr></thead>
<tbody>
<tr><td>Gross revenue churn (monthly)</td><td>~{grc}%</td><td>Targets above {grc*1.5:.1f}% are deteriorating faster than reported</td></tr>
<tr><td>Net revenue churn (monthly)</td><td>~{nrc}%</td><td>Positive net churn that survives expansion adjustments is the #1 red flag</td></tr>
<tr><td>Logo churn (monthly)</td><td>~{lc}%</td><td>{title} targets with logo churn &gt; {lc*1.5:.1f}% have a customer-acquisition problem, not a retention problem</td></tr>
<tr><td>Annual-plan share</td><td>~{aps}%</td><td>High annual share ({aps}%) <em>masks</em> logo decay — renewals land in lump-sum cliffs, not steady state</td></tr>
<tr><td>MRR volatility</td><td>{vol}</td><td>{vol.title()} volatility means a single quarter's MRR is not representative of run-rate</td></tr>
</tbody>
</table>

<div class="callout warn">
<strong>What the {title.lower()} benchmark hides:</strong> with {aps}% of revenue on annual plans, a target can show flat or growing MRR for 9–11 months while the underlying logo base is quietly churning. The cliff lands the quarter <em>after</em> you close. ChurnLens decomposes the ledger to expose this before the LOI.
</div>

<h2>Why {title.lower()} SaaS churn is different</h2>
<p>{tagline.capitalize()} exhibits a distinct churn signature that generic SaaS benchmarks misread. The dominant pattern is <strong>{key_risk}</strong>. {profile.capitalize()} are the typical buyer profile, and their churn behavior is shaped by industry-specific triggers: {aps}% of revenue sits on annual plans (so reported churn lags real decay by a full renewal cycle), and MRR volatility is {vol} (so a single quarter's snapshot can flatter or slander the true trajectory).</p>
<p>The result is that {title.lower()} SaaS sellers can present clean-looking retention slides — gross revenue churn "under {grc+0.5:.1f}%", logo retention "above {(100-lc*1.2):.0f}%" — while the underlying business is hollowing out. ChurnLens is built to find the hollowing.</p>

<h2>The decay signals ChurnLens tracks for {title.lower()} SaaS</h2>
<ul class="check">
<li><strong>Revenue concentration:</strong> what share of MRR sits in the top-5 logos? For {tagline}, concentration above 35% is a structural risk that surfaces as sudden, lumpy churn.</li>
<li><strong>Inactive paid accounts:</strong> paying customers ({profile}) whose product usage has dropped below the activation threshold. These are logos that have already churned in behavior — they just haven't churned in billing yet.</li>
<li><strong>Annual-plan renewal risk:</strong> with {aps}% annual share, ChurnLens projects which cohorts are scheduled to renew in the next 1–4 quarters and models the downside case.</li>
<li><strong>MRR decline patterns:</strong> {vol} MRR volatility means ChurnLens looks at trailing 6-month weighted averages, not the most recent month.</li>
<li><strong>Cohort retention curves:</strong> whether the {lc}% logo churn is concentrated in old cohorts (a maturing product problem) or new cohorts (an onboarding/ICP problem).</li>
</ul>

<h2>How to run {title.lower()} SaaS churn diligence in under a day</h2>
<ol>
<li><strong>Upload the revenue ledger:</strong> ChurnLens ingests the target's Stripe/Billing export, normalizes by plan type, and segments by {title.lower()}-specific cohorts.</li>
<li><strong>Run the revenue-quality score:</strong> a composite 0–100 score across concentration, retention, annual-plan risk, inactive accounts, and MRR trend. Targets below 60 warrant a price re-trade.</li>
<li><strong>Review the hidden-churn report:</strong> the specific logos exhibiting decay signals, with projected churn impact on trailing-12-month MRR.</li>
<li><strong>Stress-test the LOI:</strong> model the purchase price against the true (not reported) retention trajectory. Most {title.lower()} deals re-trade 8–15% after this step.</li>
</ol>
<p><a href="{BASE}/tools/saas-health-score">Run the SaaS Health Score tool →</a> to see the methodology in action on a sample target.</p>

<section class="faq">
<h2>Frequently asked questions</h2>
{faq_visible}
</section>

<section class="cta">
<h2>Run {title} SaaS diligence with ChurnLens</h2>
<p>Surface the {key_risk.split('—')[0].strip()} that headline metrics hide — before you sign.</p>
<a href="{BASE}" class="button">Start with ChurnLens →</a>
</section>

<section class="related-pages">
<h2>Related pages</h2>
<ul>
<li><a href="{BASE}/for/b2b-saas">ChurnLens for B2B SaaS</a></li>
<li><a href="{BASE}/for/micro-saas">ChurnLens for Micro-SaaS</a></li>
<li><a href="{BASE}/for/pe-analysts">ChurnLens for PE analysts</a></li>
<li><a href="{BASE}/checklists/pre-loi-checklist">Pre-LOI SaaS checklist</a></li>
<li><a href="{BASE}/tools/saas-health-score">SaaS Health Score tool</a></li>
<li><a href="{BASE}/benchmarks">SaaS churn benchmarks</a></li>
</ul>
</section>
</article>
</main>
<footer>
<p>© 2026 ChurnLens. SaaS Revenue Quality & Churn Risk Due Diligence.</p>
</footer>
</body>
</html>
"""
    out = ROOT / "for" / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return url


def update_sitemap(urls):
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    # Idempotent: drop any /for/{slug} we own that isn't a known legacy page
    legacy = {"agencies", "b2b-saas", "board-members", "devtools", "edtech",
              "fintech", "founders-exiting", "fractional-cfos", "index",
              "indie-acquirers", "investment-bankers", "marketplace-saas",
              "micro-pe", "micro-saas", "pe-analysts", "private-equity",
              "saas-acquirers", "saas-brokers", "saas-founders-selling",
              "search-fund-operators", "search-funds", "subscription-businesses"}
    our_slugs = {u.rsplit("/for/", 1)[1] for u in urls}
    for s in our_slugs:
        if s in legacy:
            continue  # don't double-add legacy pages
        if f"/for/{s}</loc>" in text:
            continue
    additions = "\n".join(
        f"  <url><loc>{u}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>"
        for u in urls
    )
    # Remove any duplicate entries for our slugs
    for u in urls:
        text = re.sub(rf"\n  <url><loc>{re.escape(u)}</loc>[^\n]*</url>", "", text)
    text = text.replace("</urlset>", additions + "\n</urlset>")
    sm.write_text(text, encoding="utf-8")


def main():
    urls = [build_page(ind) for ind in INDUSTRIES]
    update_sitemap(urls)
    print(f"Generated {len(urls)} industry pages")
    print(f"Sample: {urls[0]}")


if __name__ == "__main__":
    main()
