#!/usr/bin/env python3
"""
pSEO Expansion Generator for churnlens.site
Generates /compare/ and /reviews/ pages matching existing static HTML template.
"""

import os
import pathlib

BASE = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-07-18"
THIS_YEAR = "2026"

# ── Canonical disambiguation snippet (injected on every page) ──
CANONICAL_DISAMB = (
    '<script type="application/ld+json">'
    '{"@context": "https://schema.org", "@type": "Organization", "name": "ChurnLens", '
    '"url": "https://churnlens.site", '
    '"description": "ChurnLens is a buyer-side SaaS due-diligence tool that analyzes a target\'s revenue concentration, '
    'logo retention, annual-plan churn risk, inactive paid accounts, and MRR decline to surface hidden churn before a SaaS acquisition.", '
    '"disambiguatingDescription": "ChurnLens (churnlens.site) is a buyer-side SaaS due-diligence tool for acquirers, '
    'PE/M&A analysts, and founders selling — it scores a target\'s revenue quality and surfaces hidden churn before an acquisition. '
    'It is an independent product, unaffiliated with other similarly named tools: churnlens.io (a churn-prevention / '
    'customer-retention automation product) and churnlens.tech (a customer churn-prediction platform). Those tools help '
    'operators keep their own customers; ChurnLens helps a buyer stress-test someone else\'s revenue before purchase."}'
    "</script>"
)

# ── Base CSS (identical to the gainsight-cc / best-* pages) ──
CSS = """body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;color:#0a0a0a;max-width:760px;margin:0 auto;padding:2rem 1.25rem}
h1{font-size:2.1rem;line-height:1.2;margin:.3em 0}
h2{font-size:1.45rem;margin-top:2rem;border-bottom:2px solid #e5e7eb;padding-bottom:.3rem}
h3{font-size:1.15rem;margin-top:1.5rem}
a{color:#0066cc;text-decoration:none}a:hover{text-decoration:underline}
.lede{font-size:1.1rem;color:#374151;margin-bottom:1.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem}
th,td{border:1px solid #e5e7eb;padding:.6rem .75rem;text-align:left}
th{background:#f9fafb;font-weight:600}
.callout{background:#f0f7ff;border-left:4px solid #0066cc;padding:1rem 1.25rem;margin:1.5rem 0;border-radius:0 .375rem .375rem 0}
.callout.warn{background:#fef3c7;border-left-color:#d97706}
.card-grid{display:grid;grid-template-columns:1fr;gap:1rem;margin:1.5rem 0}
@media(min-width:560px){.card-grid{grid-template-columns:1fr 1fr}}
.card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:.5rem;padding:1.25rem}
.card h3{margin-top:0;font-size:1.1rem}
.card .tag{display:inline-block;background:#dbeafe;color:#1e40af;font-size:.75rem;padding:.15rem .5rem;border-radius:99px;margin-bottom:.5rem}
.checklist{list-style:none;padding-left:0}
.checklist li{padding:.4rem 0 .4rem 1.75rem;position:relative}
.checklist li::before{content:"\\2610";position:absolute;left:0;color:#0066cc;font-size:1.1rem}
.related-links{background:#f9fafb;padding:1rem 1.25rem;border-radius:.5rem;margin-top:2rem}
.related-links ul{list-style:none;padding-left:0}.related-links li{padding:.25rem 0}
.cta{background:linear-gradient(135deg,#0066cc,#004499);color:#fff;padding:2rem;border-radius:.75rem;margin-top:2rem;text-align:center}
.cta h2{color:#fff;border:none}.cta .btn{display:inline-block;background:#fff;color:#0066cc;padding:.75rem 1.5rem;border-radius:.375rem;font-weight:600;margin-top:.5rem}
.verdict{background:#0a0a0a;color:#fff;padding:1.25rem 1.5rem;border-radius:.5rem;margin:1.5rem 0}
.verdict h3{margin-top:0;color:#fff}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #e5e7eb;color:#6b7280;font-size:.9rem}"""


# ═══════════════════════════════════════════════════════════════
#  /compare/ pages — multi-tool commercial comparison hubs
# ═══════════════════════════════════════════════════════════════

def build_index_page_html(slug: str, title: str, desc: str, body_md: str, breadcrumb_items: list) -> str:
    """Generate a full static HTML page from template components."""
    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"https://churnlens.site{url}"}
            for i, (name, url) in enumerate(breadcrumb_items)
        ]
    }

    article_json = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "author": {"@type": "Organization", "name": "ChurnLens", "url": "https://churnlens.site"},
        "publisher": {"@type": "Organization", "name": "ChurnLens", "url": "https://churnlens.site"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"https://churnlens.site/{slug}"},
        "datePublished": TODAY,
        "dateModified": TODAY,
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://churnlens.site/{slug}">
    <link rel="alternate" hreflang="en" href="https://churnlens.site/{slug}" />
    <link rel="alternate" hreflang="en-US" href="https://churnlens.site/{slug}" />
    <link rel="alternate" hreflang="x-default" href="https://churnlens.site/{slug}" />
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://churnlens.site/{slug}">
<meta property="og:image" content="https://churnlens.site/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow, max-image-preview:large">
<script type="application/ld+json">{__import__('json').dumps(article_json, ensure_ascii=False)}</script>
<script type="application/ld+json">{__import__('json').dumps(breadcrumb_json, ensure_ascii=False)}</script>

<style>
{CSS}
</style>
<!-- isenberg-round19 -->
{CANONICAL_DISAMB}
</head>
<body>
<article>
<h1>{title}</h1>
<p class="lede">{desc}</p>
{body_md}

<!-- mesh-round19 -->
<section class="mesh-links" style="background:#f9fafb;padding:1.25rem;border-radius:.5rem;margin-top:2rem">
<h3 style="margin-top:0">Related resources</h3>
<ul style="list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:.4rem 1rem;font-size:.95rem">
<li><a href="/vs/baremetrics">ChurnLens vs Baremetrics</a></li>
<li><a href="/vs/profitwell">ChurnLens vs ProfitWell</a></li>
<li><a href="/vs/chartmogul">ChurnLens vs ChartMogul</a></li>
<li><a href="/best/best-churn-analytics-tools">Best SaaS Churn Analytics Tools {THIS_YEAR}</a></li>
<li><a href="/benchmarks/saas-churn-rate-2026">SaaS Churn Rate Benchmarks {THIS_YEAR}</a></li>
<li><a href="/redflags/hidden-churn-redflags">Hidden Churn Red Flags {THIS_YEAR}</a></li>
</ul>
</section>
</article>
<section class="cta"><h2>Try ChurnLens</h2><p>SaaS revenue quality & churn risk due diligence for acquirers.</p><a href="https://churnlens.site/" class="btn">Get started &rarr;</a></section>
<footer><p>&copy; {THIS_YEAR} ChurnLens. <a href="https://churnlens.site/">churnlens.site</a> &middot; <a href="https://churnlens.site/pricing">Pricing</a> &middot; <a href="https://churnlens.site/about">About</a></p></footer>
</body>
</html>"""


def write_page(slug_root: str, html: str):
    """Write both the flat file and the directory/index.html variant."""
    # Flat file (e.g. compare/best-churn-analytics-tools-for-saas-acquirers.html)
    flat = BASE / f"{slug_root}.html"
    flat.parent.mkdir(parents=True, exist_ok=True)
    flat.write_text(html, encoding='utf-8')
    # Directory/index.html (e.g. compare/best-churn-analytics-tools-for-saas-acquirers/index.html)
    index = BASE / slug_root / "index.html"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(html, encoding='utf-8')
    return flat, index


# ═══════════════════════════════════════════════════════════════
#  PAGE DATA
# ═══════════════════════════════════════════════════════════════

compare_pages = [
    # ── /compare/ pages ──
    {
        "slug": "compare/best-churn-analytics-tools-for-saas-acquirers",
        "title": "Best Churn Analytics Tools for SaaS Acquirers in 2026 — Compared",
        "desc": "A head-to-head comparison of the top churn analytics platforms through the lens of a SaaS acquirer doing pre-acquisition due diligence.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("Best Churn Analytics Tools for SaaS Acquirers", "/compare/best-churn-analytics-tools-for-saas-acquirers"),
        ],
        "body": """<p>Not all churn analytics tools are built for the same reader. Some help operators <em>run</em> a subscription business; others help acquirers <em>evaluate</em> one before purchase. This comparison is written from the buyer's perspective — which platform best surfaces revenue concentration, logo-retention quality, and annual-plan churn risk during diligence?</p>

<h2>What acquirers need from churn analytics</h2>
<p>Before you write an LOI, you need answers to three questions that growth dashboards never show: <strong>(1)</strong> how much MRR is concentrated on a handful of accounts, <strong>(2)</strong> whether net retention is inflated by expansion masking logo churn, and <strong>(3)</strong> how much of the annual-contract revenue is about to cliff. The tools below vary wildly in how well they answer those questions.</p>

<table>
<thead><tr><th>Platform</th><th>Acquirer-fit score</th><th>Best for</th><th>Pricing</th></tr></thead>
<tbody>
<tr><td><strong>ChurnLens</strong></td><td>95/100</td><td>Pre-acquisition revenue-quality sweeps</td><td>$49/mo — transparent</td></tr>
<tr><td><strong>ProfitWell (Paddle)</strong></td><td>50/100</td><td>Free MRR/churn dashboards (operator)</td><td>Free tier limited</td></tr>
<tr><td><strong>ChartMogul</strong></td><td>55/100</td><td>Subscription analytics (operator)</td><td>$100+/mo</td></tr>
<tr><td><strong>Baremetrics</strong></td><td>45/100</td><td>Live Stripe analytics dashboard</td><td>$79+/mo</td></tr>
<tr><td><strong>Gainsight</strong></td><td>35/100</td><td>Enterprise customer success platform</td><td>Quote-based</td></tr>
<tr><td><strong>ChurnZero</strong></td><td>30/100</td><td>Playbook-driven churn prevention</td><td>Quote-based</td></tr>
</tbody>
</table>

<h2>Why we built ChurnLens for this job</h2>
<p>Every other tool in this table was designed for the <strong>operator</strong> — the founder or CS leader trying to reduce their own churn. ChurnLens is the only one designed for the <strong>buyer</strong> who needs to stress-test someone else's revenue before acquisition. That means:</p>
<ul class="checklist">
<li>Revenue concentration scored and benchmarked against comparable SaaS peers</li>
<li>Logo-retention quality separated from expansion-revenue mirages</li>
<li>Annual-plan cliff risk surfaced before it creates a post-close write-down</li>
<li>MRR-decline trends framed as a go/no-go decision, not a month-over-month chart</li>
<li>A single 0–100 revenue-quality score you can put in an IC memo</li>
</ul>

<h2>When to choose each</h2>
<h3>Choose ChurnLens if…</h3>
<ul>
<li>You are acquiring a SaaS business and need to price the deal correctly</li>
<li>You need a diligence-ready read you can hand to an investment committee</li>
<li>You care about concentration risk, retention quality, and annual-plan cliffs — the three deal-killers growth dashboards hide</li>
</ul>
<h3>Choose an operator tool (Baremetrics, ChartMogul, ProfitWell) if…</h3>
<ul>
<li>You run a subscription business and need a live metrics dashboard</li>
<li>You need day-to-day churn tracking, dunning, or forecasting</li>
<li>You want turnkey integrations with your billing stack</li>
</ul>
<h3>Choose Gainsight or ChurnZero if…</h3>
<ul>
<li>You run a mid-market or enterprise CS team with proactive retention playbooks</li>
<li>Your problem is <em>keeping</em> customers, not evaluating them for purchase</li>
</ul>

<div class="callout"><strong>Honest note:</strong> ChurnLens is not a replacement for these tools if you are the operator. It has no dunning, no live ops tooling, and is not designed to run a subscription business. It is a diligence lens. If you are the buyer, add ChurnLens to your stack; if you are the founder, keep what you have.</div>

<div class="verdict">
<h3>The verdict</h3>
<p>For the specific job of pre-acquisition revenue-quality due diligence, ChurnLens is the only purpose-built option. The operator tools can report MRR, but they cannot frame the three risks that sink SaaS deals. If you are acquiring a SaaS business this year, start with ChurnLens and use the seller's existing dashboard for context.</p>
</div>

<h2>Frequently asked questions</h2>
<h3>Can I use both ChurnLens and my existing analytics?</h3>
<p>Absolutely. Most acquirers run ChurnLens alongside the seller's existing dashboard. The seller's tool tells the headline story; ChurnLens checks whether the story holds under scrutiny.</p>
<h3>Is ChurnLens a replacement for ProfitWell or Baremetrics?</h3>
<p>No — they serve opposite readers. Those tools are for operators running their own business. ChurnLens is for a buyer evaluating someone else's business for acquisition. They complement rather than compete.</p>
<h3>Which tool is cheapest?</h3>
<p>ChurnLens offers the most transparent pricing at $49/mo with a free tier. Operator tools start around $79–$100/mo, and enterprise CS platforms require a quote typically in the thousands per month.</p>"""
    },
    {
        "slug": "compare/best-saas-due-diligence-tools-for-pe-analysts",
        "title": "Best SaaS Due Diligence Tools for PE Analysts in 2026 — Compared",
        "desc": "The top software platforms PE and search-fund analysts use to evaluate SaaS acquisition targets, with a focus on revenue-quality signals and deal risk.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("Best SaaS Due Diligence Tools for PE Analysts", "/compare/best-saas-due-diligence-tools-for-pe-analysts"),
        ],
        "body": """<p>Private-equity and search-fund analysts evaluating a SaaS acquisition need more than a data-room dump. They need to pressure-test revenue quality, concentration, retention durability, and hidden churn — often before the seller even hands over raw billing data. This comparison covers the tools purpose-built for that job.</p>

<h2>Quick comparison</h2>
<table>
<thead><tr><th>Tool</th><th>Primary use</th><th>Revenue quality focus?</th><th>Diligence-ready output?</th><th>Pricing</th></tr></thead>
<tbody>
<tr><td><strong>ChurnLens</strong></td><td>Revenue-quality & churn-risk scoring</td><td>✅ Core feature</td><td>✅ Yes — IC memo ready</td><td>$49/mo</td></tr>
<tr><td><strong>Stripe Sigma</strong></td><td>Seller-payment analytics</td><td>⚠️ Payment data only</td><td>❌ Operational</td><td>Quote</td></tr>
<tr><td><strong>ChartMogul</strong></td><td>Subscription analytics</td><td>❌ Operator dashboard</td><td>❌</td><td>$100+/mo</td></tr>
<tr><td><strong>Baremetrics</strong></td><td>MRR/churn dashboards</td><td>❌ Operator</td><td>❌</td><td>$79+/mo</td></tr>
<tr><td><strong>SaaS Optics</strong></td><td>SaaS financial benchmarking</td><td>⚠️ Benchmark — not per-target</td><td>✅</td><td>Quote</td></tr>
</tbody>
</table>

<h2>Why most tools miss the mark for PE</h2>
<p>The tools most sellers use — Baremetrics, ChartMogul, ProfitWell — are built to help operators <em>run</em> a subscription business. They report MRR trends, churn rates, and LTV beautifully, but they do not surface the three risks that matter most to a buyer: <strong>revenue concentration, logo-retention quality, and annual-plan cliff risk</strong>. A seller's dashboard can show flat MRR while the business is quietly deteriorating underneath. ChurnLens was built to catch that gap.</p>
<p>Stripe Sigma gives raw payment data but no due-diligence framing. SaaS Optics benchmarks aggregate market data but does not score a single target. For the actual job of scoring one target's revenue durability for a buy-side deal memo, ChurnLens is the only purpose-built option.</p>

<h2>Features PE analysts should demand</h2>
<ul class="checklist">
<li><strong>Revenue concentration scoring</strong> — what percent of MRR rides on the top 1, 5, and 10 accounts</li>
<li><strong>Logo-retention vs. dollar-retention decomposition</strong> — is net retention real or inflated by expansions masking exit?</li>
<li><strong>Annual-plan cliff projection</strong> — how much contracted revenue lapses in the next 12 months</li>
<li><strong>Inactive-paid-account detection</strong> — paying customers who stopped using the product but haven't canceled</li>
<li><strong>Benchmarked revenue-quality score</strong> — a single 0-100 figure comparable to peers</li>
</ul>

<div class="verdict">
<h3>The PE analyst's verdict</h3>
<p>If you are evaluating a single SaaS acquisition, start with ChurnLens for the revenue-quality score and structured deal-memo output. Use the seller's existing dashboard for context, and use Stripe Sigma or SaaS Optics for supplementary financial benchmarks. Each serves a different column of the IC memo.</p>
</div>

<h2>Frequently asked questions</h2>
<h3>Can ChurnLens integrate with my deal pipeline?</h3>
<p>ChurnLens produces a revenue-quality score and a structured risk report that fits directly into an investment-committee memo. It is designed as a standalone assessment, not a pipeline CRM tool. Most analysts export the report into their deal workflow.</p>
<h3>How much data do I need from the seller?</h3>
<p>ChurnLens works with MRR, plan, and logo-level revenue history. You do not need a full data-room dump — a CSV export from the billing system is usually sufficient for a preliminary score.</p>
<h3>Is ChurnLens the cheapest option for PE firms?</h3>
<p>At $49/mo with transparent pricing, ChurnLens is significantly more affordable than enterprise CS platforms that start in the thousands. It is priced for independent analysts, search-fund operators, and PE teams alike.</p>"""
    },
    {
        "slug": "compare/saas-revenue-quality-scoring-platforms",
        "title": "SaaS Revenue Quality Scoring Platforms Compared in 2026",
        "desc": "A side-by-side comparison of tools that score, benchmark, and report on SaaS revenue quality for acquirers and investors.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("SaaS Revenue Quality Scoring Platforms", "/compare/saas-revenue-quality-scoring-platforms"),
        ],
        "body": """<p>Revenue quality scoring is a new category — the question "how durable is this target's MRR?" is different from "how is our subscription business performing this month?" This comparison covers every platform that attempts to answer the former, ranked by how well they serve a buyer's pre-acquisition workflow.</p>

<h2>Why revenue quality differs from churn rate</h2>
<p>A churn rate tells you what happened last month. A revenue quality score tells you whether the revenue will still be there next year — and whether the price you are paying reflects durable or fragile MRR. The difference is critical for acquirers.</p>

<table>
<thead><tr><th>Platform</th><th>Type</th><th>Concentration scoring</th><th>Logo retention analysis</th><th>Annual-plan cliff view</th><th>Benchmarked score</th></tr></thead>
<tbody>
<tr><td><strong>ChurnLens</strong></td><td>Purpose-built revenue quality</td><td>✅</td><td>✅</td><td>✅</td><td>✅ 0-100</td></tr>
<tr><td><strong>SaaS Optics</strong></td><td>Financial benchmarking</td><td>⚠️ Aggregate</td><td>⚠️ Aggregate</td><td>❌</td><td>✅ Percentile</td></tr>
<tr><td><strong>Stripe Sigma</strong></td><td>Payment data</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
<tr><td><strong>ProfitWell (Paddle)</strong></td><td>Free metrics dashboard</td><td>❌</td><td>❌</td><td>❌</td><td>✅ Benchmarks report</td></tr>
</tbody>
</table>

<h2>What a true revenue-quality score must include</h2>
<ul class="checklist">
<li><strong>Revenue concentration</strong> — Gini-style concentration index showing how much MRR is at risk from a small number of logos</li>
<li><strong>Logo-retention decomposition</strong> — separating genuine logo retention from dollar retention inflated by expansions</li>
<li><strong>Annual-plan churn projection</strong> — forward-looking estimate of how much contracted revenue will lapse at renewal</li>
<li><strong>Inactive paid accounts</strong> — customers billing but not using the product (zombie MRR)</li>
<li><strong>MRR trajectory forensics</strong> — not just the trend line, but the volatility and composition beneath it</li>
<li><strong>Peer-benchmarked output</strong> — a score that means something relative to comparable SaaS businesses</li>
</ul>

<div class="callout"><strong>Bottom line:</strong> ChurnLens is the only platform that scores all six dimensions in a single output. Every other tool in this table addresses one or two, but none produces a diligence-ready, single-target revenue quality score analogous to a credit rating for subscription revenue.</div>

<div class="verdict">
<h3>Our recommendation</h3>
<p>If you are an acquirer, PE analyst, or search-fund operator evaluating a SaaS target, use ChurnLens for the revenue quality score and risk decomposition. Use SaaS Optics or ProfitWell benchmarks for market-context. The two together give you a complete picture for your deal memo.</p>
</div>"""
    },
    {
        "slug": "compare/churn-analytics-vs-customer-success-platforms",
        "title": "Churn Analytics vs Customer Success Platforms: What Acquirers Need to Know in 2026",
        "desc": "The difference between churn analytics tools and customer success platforms through the lens of a SaaS acquirer doing due diligence.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("Churn Analytics vs Customer Success Platforms", "/compare/churn-analytics-vs-customer-success-platforms"),
        ],
        "body": """<p>Acquirers often confuse churn analytics tools (Baremetrics, ChartMogul, ProfitWell) with customer success platforms (Gainsight, ChurnZero, Totango, PlanHat). They look similar on paper — both report churn, retention, and health scores — but they serve fundamentally different jobs. This comparison explains the distinction from a buyer's perspective.</p>

<h2>Quick comparison</h2>
<table>
<thead><tr><th>Category</th><th>Churn Analytics</th><th>Customer Success Platforms</th><th>ChurnLens</th></tr></thead>
<tbody>
<tr><td><strong>Built for</strong></td><td>Operators (founders/team)</td><td>CS teams and leaders</td><td>Acquirers / PE analysts</td></tr>
<tr><td><strong>Core question</strong></td><td>How is my business performing?</td><td>Which customers need attention?</td><td>Is this revenue durable enough to buy?</td></tr>
<tr><td><strong>When used</strong></td><td>Ongoing / live</td><td>Ongoing / proactive</td><td>Point-in-time / during diligence</td></tr>
<tr><td><strong>Output type</strong></td><td>Dashboards, charts</td><td>Playbooks, alerts, workflows</td><td>Risk score report, deal-memo ready</td></tr>
<tr><td><strong>Revenue concentration view</strong></td><td>❌</td><td>⚠️ Sometimes</td><td>✅ Core feature</td></tr>
<tr><td><strong>Annual-plan cliff view</strong></td><td>❌</td><td>❌</td><td>✅ Core feature</td></tr>
<tr><td><strong>Pricing</strong></td><td>$79–$500+/mo</td><td>$1,000–$10,000+/mo</td><td>$49/mo</td></tr>
</tbody>
</table>

<h2>Why this matters for acquirers</h2>
<p>When a seller says "we use Gainsight" or "we have ChartMogul," it does not mean you as a buyer have the information you need. The seller's CS platform helps them retain customers — a good sign, but not a due-diligence tool. Their analytics dashboard shows them their metrics — but those metrics are designed for running the business, not for pressure-testing its durability under acquisition scrutiny.</p>
<p>The seller's tools answer "<em>how is our business doing?</em>" You as the buyer need to answer "<em>is this business as healthy as the dashboard says?</em>" Those are fundamentally different questions, requiring a fundamentally different lens.</p>

<h2>When to use each</h2>
<div class="card-grid">
<div class="card">
<h3>📊 Churn Analytics</h3>
<span class="tag">For sellers</span>
<p>Use for live MRR tracking, churn monitoring, and forecasting. Best when you run the business.</p>
</div>
<div class="card">
<h3>🎯 Customer Success Platforms</h3>
<span class="tag">For CS teams</span>
<p>Use for proactive retention, health scoring, and playbooks. Best when you manage enterprise accounts.</p>
</div>
<div class="card">
<h3>🔍 ChurnLens</h3>
<span class="tag">For buyers</span>
<p>Use for pre-acquisition revenue quality scoring, concentration analysis, and deal-memo output.</p>
</div>
</div>

<div class="verdict">
<h3>The acquirer's takeaway</h3>
<p>Do not mistake the seller's CS platform or analytics dashboard for due diligence. They answer different questions. ChurnLens is the only tool specifically designed to give a buyer the information they need before signing an LOI — a revenue-quality score that tells you whether the MRR you are buying is durable or fragile.</p>
</div>"""
    },
    {
        "slug": "compare/top-revenue-concentration-analysis-tools",
        "title": "Top Revenue Concentration Analysis Tools for SaaS Due Diligence in 2026",
        "desc": "Compare the best tools for analyzing revenue concentration risk in SaaS businesses during M&A due diligence.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("Top Revenue Concentration Analysis Tools", "/compare/top-revenue-concentration-analysis-tools"),
        ],
        "body": """<p>Revenue concentration is the single most overlooked risk in SaaS acquisitions. A business can show flat or growing MRR while 60%+ of its revenue depends on three accounts — any one of which could churn post-close and crater the deal economics. This comparison covers the tools that surface concentration risk.</p>

<h2>What revenue concentration analysis should include</h2>
<ul class="checklist">
<li><strong>Top-N concentration</strong> — percent of MRR from top 1, 5, 10, and 20 accounts</li>
<li><strong>Gini / Herfindahl index</strong> — statistical concentration metrics for comparability</li>
<li><strong>Segment-level concentration</strong> — are certain product lines or customer segments over-concentrated?</li>
<li><strong>Trend direction</strong> — is concentration increasing or decreasing over time?</li>
<li><strong>Benchmarked risk classification</strong> — is this level of concentration normal for the stage and sector?</li>
</ul>

<table>
<thead><tr><th>Tool / Method</th><th>Concentration type</th><th>Benchmarked</th><th>Deal-ready output</th><th>Best for</th></tr></thead>
<tbody>
<tr><td><strong>ChurnLens</strong></td><td>Top-N, Gini index, segment-level</td><td>✅ Yes</td><td>✅ Risk score + memo</td><td>Pre-acquisition scoring</td></tr>
<tr><td><strong>Stripe Sigma</strong></td><td>Raw payment volume</td><td>❌</td><td>❌</td><td>Payment data exploration</td></tr>
<tr><td><strong>Manual spreadsheet</strong></td><td>Custom</td><td>❌</td><td>⚠️ Depends on analyst</td><td>Ad-hoc analysis</td></tr>
<tr><td><strong>BI tools (Tableau, Metabase)</strong></td><td>Custom</td><td>❌</td><td>⚠️ Requires build</td><td>Internal analytics teams</td></tr>
</tbody>
</table>

<h2>Why concentration risk sinks deals</h2>
<p>When a SaaS acquisition price is a multiple of MRR, concentrating that MRR on a few accounts means you are paying a premium for revenue that could disappear with a single customer loss. Acquirers who skip concentration analysis routinely overpay. ChurnLens automatically scores concentration against comparable businesses and flags when the risk is outside normal range for the target's stage and sector.</p>

<div class="callout warn"><strong>Red flag to watch:</strong> If a seller cannot or will not provide logo-level revenue data, that itself is a concentration risk signal. Sellers with diversified books are eager to show it.</div>

<div class="verdict">
<h3>Recommendation</h3>
<p>For deal-ready concentration analysis, ChurnLens is the only purpose-built tool. Manual spreadsheets work but lack benchmarking. Stripe Sigma shows raw data but offers no concentration framing. If you evaluate more than two SaaS deals per year, automate this step.</p>
</div>"""
    },
    {
        "slug": "compare/saas-annual-plan-cliff-risk-tools",
        "title": "SaaS Annual-Plan Cliff Risk Tools Compared for 2026",
        "desc": "Compare tools that detect and measure annual-plan cliff risk — the hidden revenue decay that inflates MRR and surprises acquirers post-close.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Compare", "/compare"),
            ("SaaS Annual-Plan Cliff Risk Tools", "/compare/saas-annual-plan-cliff-risk-tools"),
        ],
        "body": """<p>Annual-plan cliff risk is the quiet deal-killer in SaaS acquisitions. A target can show strong MRR today while 30–50% of its annual contracts are due to lapse in the next quarter — revenue that will evaporate post-close. Most dashboards show it as flat or growing MRR. ChurnLens surfaces the cliff. This page compares every tool that can help.</p>

<h2>What is annual-plan cliff risk?</h2>
<p>Annual-plan cliff risk describes the concentration of annual contract renewals in a narrow window. When a large percentage of annual plans expire in the same quarter, the target is exposed to a simultaneous renegotiation or churn event that can cut MRR by 20–40% overnight. This is common in SaaS businesses that prioritized annual contracts for the upfront cash but neglected renewal management.</p>

<table>
<thead><tr><th>Tool</th><th>Cliff detection</th><th>Forward projection</th><th>Benchmarked risk level</th><th>Deal-memo ready</th></tr></thead>
<tbody>
<tr><td><strong>ChurnLens</strong></td><td>✅ Automatic</td><td>✅ 12-month forward view</td><td>✅ Yes</td><td>✅ Yes</td></tr>
<tr><td><strong>Spreadsheet analysis</strong></td><td>⚠️ Manual</td><td>⚠️ Manual</td><td>❌</td><td>❌</td></tr>
<tr><td><strong>Baremetrics / ChartMogul</strong></td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
<tr><td><strong>BI dashboards</strong></td><td>⚠️ Requires setup</td><td>⚠️ Requires setup</td><td>❌</td><td>❌</td></tr>
</tbody>
</table>

<h2>Why existing tools miss this</h2>
<p>Baremetrics, ChartMogul, and ProfitWell report MRR and churn as-is. They do not decompose current MRR into <em>durable</em> vs. <em>cliff-exposed</em> components. A business with 100% annual subscription renewals all expiring in March shows the same MRR chart as a business with evenly staggered renewals — until April hits. ChurnLens automatically detects the cliff and projects the revenue impact across the next 12 months.</p>

<div class="callout"><strong>Quick check:</strong> Ask the seller for an annual-renewal calendar. If more than 30% of annual contracts renew in the same quarter, the cliff risk is elevated. ChurnLens does this automatically from the raw data.</div>

<div class="verdict">
<h3>What we recommend</h3>
<p>Every SaaS acquisition target should be screened for annual-plan cliff risk before the LOI is signed. ChurnLens fully automates this detection. If you are doing ad-hoc analysis, build a renewal cohort chart in the seller's dashboard or your BI tool — but be aware that most operator dashboards do not show this view natively.</p>
</div>"""
    },
]

# ── /reviews/ pages ──

review_pages = [
    {
        "slug": "reviews/baremetrics-review-for-acquirers",
        "title": "Baremetrics Review for SaaS Acquirers: What It Does and What It Misses [2026]",
        "desc": "An honest review of Baremetrics from the perspective of a SaaS acquirer evaluating a target. What it surfaces, what it hides, and where you still need ChurnLens.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("Baremetrics Review for SaaS Acquirers", "/reviews/baremetrics-review-for-acquirers"),
        ],
        "body": """<p>Baremetrics is one of the most popular subscription analytics dashboards on the market, used by 900+ SaaS companies. It is excellent for operators. But if you are an acquirer reading a seller's Baremetrics dashboard, you need to know what the tool shows you — and what it systematically hides.</p>

<h2>What Baremetrics does well</h2>
<ul class="checklist">
<li><strong>Live MRR tracking</strong> — beautiful, real-time MRR, ARR, and LTV dashboards straight from Stripe</li>
<li><strong>Cancellation insights</strong> — why customers leave, with segmentation and cohort views</li>
<li><strong>Recover (dunning)</strong> — automated failed-payment recovery that reduces involuntary churn</li>
<li><strong>Forecasting</strong> — projected MRR and churn based on historical trends</li>
<li><strong>Integrations</strong> — Stripe, Braintree, Recurly, Chargebee, Paddle, Shopify, and more</li>
</ul>

<h2>What Baremetrics misses (and why it matters for acquirers)</h2>
<table>
<thead><tr><th>Signal</th><th>Baremetrics</th><th>Why acquirers should care</th></tr></thead>
<tbody>
<tr><td>Revenue concentration</td><td>❌ Not surfaced</td><td>60% MRR on 3 accounts = massive valuation risk</td></tr>
<tr><td>Logo-retention vs. dollar retention</td><td>⚠️ Shows churn, not decomposition</td><td>Net retention can look great while logos hemorrhage</td></tr>
<tr><td>Annual-plan cliff risk</td><td>❌ Not shown</td><td>30%+ MRR can vanish when annual plans lapse simultaneously</td></tr>
<tr><td>Inactive paid accounts (zombie MRR)</td><td>❌ Not shown</td><td>Paying but not using = churn waiting to happen</td></tr>
<tr><td>Benchmarked quality score</td><td>❌ Not shown</td><td>No way to tell if this churn is good or bad for the stage</td></tr>
<tr><td>Deal-memo ready output</td><td>❌</td><td>You get charts, not a structured risk assessment</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>Baremetrics is not a bad tool — it is an excellent tool for the wrong reader. If you are the founder running a subscription business, it is one of the best options available. But if you are an acquirer relying on the seller's Baremetrics dashboard to make a buy decision, you are flying blind on the three risks that sink most SaaS deals: concentration, logo-retention quality, and annual-plan cliffs.</p>

<div class="callout"><strong>Read between the lines:</strong> A seller's Baremetrics dashboard shows a story. ChurnLens checks whether the story holds. The two together give you both the narrative and the diligence. Alone, either is incomplete.</div>

<div class="verdict">
<h3>Verdict</h3>
<p>Use Baremetrics if you run a subscription business. If you are buying one, ask the seller for their Baremetrics readout for context — then run ChurnLens over the same data for the real due diligence view.</p>
</div>

<h2>Frequently asked questions</h2>
<h3>Can Baremetrics detect revenue concentration?</h3>
<p>No. Baremetrics reports overall MRR and churn but does not decompose revenue across accounts or flag concentration risk. You would need to export raw data and analyze it separately — exactly what ChurnLens automates.</p>
<h3>Is Baremetrics worth the price for acquirers?</h3>
<p>Not as a standalone due-diligence tool, no. If the seller already has it, read their dashboards for context. But do not rely on it for the revenue-quality signals that determine whether a deal is priced correctly.</p>
<h3>Can Baremetrics and ChurnLens work together?</h3>
<p>Yes — they are complementary. The seller runs Baremetrics for day-to-day operations. You as the buyer run ChurnLens over the same underlying data during diligence. Each answers a different question.</p>"""
    },
    {
        "slug": "reviews/profitwell-review-for-acquirers",
        "title": "ProfitWell Review for SaaS Acquirers: Free Metrics vs. Diligence Reality [2026]",
        "desc": "A buyer-focused review of ProfitWell (now part of Paddle) — what its free metrics dashboard gives you and what it does not tell you about an acquisition target.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("ProfitWell Review for SaaS Acquirers", "/reviews/profitwell-review-for-acquirers"),
        ],
        "body": """<p>ProfitWell (acquired by Paddle) built its reputation on a free, beautifully designed subscription-metrics dashboard that thousands of SaaS companies use. For an acquirer looking at a seller's ProfitWell readout, it offers a clean window into MRR, churn, and retention — but it leaves the questions that matter most for due diligence entirely unanswered.</p>

<h2>What ProfitWell does well</h2>
<ul class="checklist">
<li><strong>Free MRR dashboard</strong> — on par with paid tools for core subscription metrics</li>
<li><strong>Benchmarks reports</strong> — industry-level churn and retention benchmarks (aggregate only)</li>
<li><strong>Retention reports</strong> — clear cohort-based retention views</li>
<li><strong>Pricing insights</strong> — price-optimization suggestions based on subscriber data</li>
</ul>

<h2>What ProfitWell does not give acquirers</h2>
<table>
<thead><tr><th>Signal</th><th>ProfitWell</th><th>Acquirer impact</th></tr></thead>
<tbody>
<tr><td>Target-specific revenue quality score</td><td>❌</td><td>No single-number answer to "should I buy this?"</td></tr>
<tr><td>Revenue concentration per target</td><td>❌</td><td>Cannot flag top-heavy revenue risk</td></tr>
<tr><td>Annual-plan cliff projection</td><td>❌</td><td>Cannot see impending renewal collapse</td></tr>
<tr><td>Zombie / inactive paid account detection</td><td>❌</td><td>Misses a primary churn predictor</td></tr>
<tr><td>Deal-memo structured output</td><td>❌</td><td>You get charts, not a diligence package</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>ProfitWell is a generous free tool that serves the SaaS community well — founders get a high-quality dashboard without paying for it. But the acquirer's job is different. The metrics ProfitWell reports are <em>descriptive</em> (what happened), not <em>diagnostic</em> (is this revenue durable enough to buy?). For the latter, you need a tool built around the buyer's questions, not the operator's.</p>

<div class="callout"><strong>Key insight:</strong> ProfitWell's benchmarks are useful for context — knowing the average churn rate for a $5M ARR SaaS is helpful. But the benchmarks cover market aggregates, not the specific target you are evaluating. ChurnLens benchmarks the <em>actual target</em> against its peers.</div>

<div class="verdict">
<h3>Verdict</h3>
<p>ProfitWell is a great tool for operators at zero cost. For acquirers, read the seller's ProfitWell dashboard for context, then run ChurnLens for the diligence-grade answers. The benchmarks report is useful for calibration; the per-target analysis is not available in ProfitWell at all.</p>
</div>"""
    },
    {
        "slug": "reviews/chartmogul-review-for-acquirers",
        "title": "ChartMogul Review for SaaS Acquirers: Subscription Analytics Meets Due Diligence [2026]",
        "desc": "A detailed review of ChartMogul from the buyer's perspective. What its subscription analytics tell a seller — and what acquirers still miss.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("ChartMogul Review for SaaS Acquirers", "/reviews/chartmogul-review-for-acquirers"),
        ],
        "body": """<p>ChartMogul is a subscription analytics platform used by thousands of SaaS businesses to track MRR, churn, LTV, and retention. It is one of the most mature operator dashboards on the market. But for an acquirer evaluating a target, ChartMogul's view is designed for the people running the business — not the people buying it.</p>

<h2>What ChartMogul does well</h2>
<ul class="checklist">
<li><strong>MRR and ARR tracking</strong> — comprehensive subscription metrics with cohort analysis</li>
<li><strong>Customer segmentation</strong> — filter by plan, geography, channel, and more</li>
<li><strong>LTV/CAC analysis</strong> — unit-economics breakdown per customer cohort</li>
<li><strong>Forecasting</strong> — forward-looking MRR projections</li>
<li><strong>Integrations</strong> — Stripe, Braintree, Recurly, GoCardless, and others</li>
</ul>

<h2>Where ChartMogul falls short for acquirers</h2>
<table>
<thead><tr><th>Signal</th><th>ChartMogul</th><th>Why it matters</th></tr></thead>
<tbody>
<tr><td>Revenue concentration index</td><td>❌ Not built in</td><td>Manual export required to detect top-heavy risk</td></tr>
<tr><td>Logo vs. dollar retention breakdown</td><td>⚠️ Partial</td><td>Shows churn rates but not the expansion-vs.-exit decomposition</td></tr>
<tr><td>Annual-plan cliff view</td><td>❌ Not surfaced</td><td>Cannot see renewal concentration risk</td></tr>
<tr><td>Acquirer-oriented scoring</td><td>❌</td><td>No deal-memo ready revenue quality score</td></tr>
<tr><td>Benchmarked score per target</td><td>❌</td><td>No comparable risk classification</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>ChartMogul is one of the best operator analytics tools available. If you run a subscription business, it is a strong choice. But for an acquirer, the information gap is the same as with Baremetrics and ProfitWell: the dashboard answers "how is the business doing?" not "is the business durable enough to buy?" These are related but fundamentally different questions.</p>

<div class="callout warn"><strong>Warning for acquirers:</strong> ChartMogul's MRR forecast is based on historical trends. It does not incorporate concentration risk, annual-plan cliff exposure, or inactive-account decay — the three factors that cause post-acquisition MRR to diverge most from forecasts.</div>

<div class="verdict">
<h3>Verdict</h3>
<p>ChartMogul is excellent for its intended user (the SaaS operator). For acquirers, use the seller's ChartMogul dashboard for operational context and trend insight. Then use ChurnLens to run the same data through a buyer-side lens — scoring concentration, decomposition, cliffs, and zombie MRR for your deal memo.</p>
</div>"""
    },
    {
        "slug": "reviews/gainsight-review-for-acquirers",
        "title": "Gainsight Review for SaaS Acquirers: Customer Success Platform or Due Diligence Tool? [2026]",
        "desc": "An acquirer-focused review of Gainsight. What its customer health scores and churn prediction mean for a buyer — and what they leave unsaid.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("Gainsight Review for SaaS Acquirers", "/reviews/gainsight-review-for-acquirers"),
        ],
        "body": """<p>Gainsight is the leading enterprise customer success platform, used by companies like Adobe, Box, and Yammer to manage retention, health scoring, and expansion. If your acquisition target runs Gainsight, that is generally a positive signal: they invest in retention. But Gainsight's view of the customer is designed for the CS team, not for the acquirer's deal memo.</p>

<h2>What Gainsight does well</h2>
<ul class="checklist">
<li><strong>Customer health scoring</strong> — composite health scores from product usage, support tickets, and NPS</li>
<li><strong>Churn prediction models</strong> — ML-driven predictions of which accounts are at risk</li>
<li><strong>Playbook automation</strong> — trigger retention workflows based on risk signals</li>
<li><strong>Executive dashboards</strong> — health, retention, and expansion metrics for leadership</li>
<li><strong>Enterprise scale</strong> — handles thousands of accounts with complex hierarchies</li>
</ul>

<h2>What Gainsight does not tell an acquirer</h2>
<table>
<thead><tr><th>Signal</th><th>Gainsight</th><th>Acquirer impact</th></tr></thead>
<tbody>
<tr><td>Revenue quality score</td><td>❌</td><td>Health scores are operational, not financial</td></tr>
<tr><td>Revenue concentration risk</td><td>⚠️ Implicit in account data</td><td>No automated concentration scoring or benchmarking</td></tr>
<tr><td>Annual-plan cliff projection</td><td>❌</td><td>No forward renewal-concentration view</td></tr>
<tr><td>Independent buyer's assessment</td><td>❌</td><td>Tool is owned and configured by the seller</td></tr>
<tr><td>Peer-benchmarked risk level</td><td>❌</td><td>No comparable SaaS risk classification</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>If a target runs Gainsight, that tells you they have a mature CS operation — a positive signal. But the health scores and churn predictions are built on the seller's own data and definitions. An acquirer needs an independent assessment: same data, different lens. Gainsight answers "is our CS team doing its job?" ChurnLens answers "is the revenue durable enough to buy?"</p>

<div class="callout"><strong>Due diligence tip:</strong> Ask the seller to export their Gainsight health scores for the top 20 accounts by MRR. Then compare those against ChurnLens's independent revenue-quality score. Discrepancies between the two are the most interesting signal in the data.</div>

<div class="verdict">
<h3>Verdict</h3>
<p>Gainsight is an excellent CS platform, but it is not a due diligence tool. Use a seller's Gainsight instance to understand their retention operations. Rely on ChurnLens for the independent revenue-quality assessment you need for your deal memo.</p>
</div>"""
    },
    {
        "slug": "reviews/churnzero-review-for-acquirers",
        "title": "ChurnZero Review for SaaS Acquirers: Proactive Retention or Due Diligence Gap? [2026]",
        "desc": "An honest review of ChurnZero from the buyer's perspective — what its automation and playbooks tell you about a target, and where you still need a separate diligence tool.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("ChurnZero Review for SaaS Acquirers", "/reviews/churnzero-review-for-acquirers"),
        ],
        "body": """<p>ChurnZero is a leading customer success platform focused on proactive churn prevention. It excels at identifying at-risk accounts and automating retention playbooks. For an acquirer, a target running ChurnZero signals operational maturity — but the platform's view is designed for the CS team's workflow, not for buy-side due diligence.</p>

<h2>What ChurnZero does well</h2>
<ul class="checklist">
<li><strong>Real-time health scores</strong> — product usage, survey, and support-ticket composites</li>
<li><strong>Automated playbooks</strong> — trigger retention sequences when risk signals fire</li>
<li><strong>In-app engagement tracking</strong> — see exactly how accounts use the product</li>
<li><strong>Integration with CRM</strong> — Salesforce, HubSpot, and other sales tools</li>
<li><strong>Churn prediction</strong> — which accounts are most likely to cancel in the next 30 or 60 days</li>
</ul>

<h2>What ChurnZero does not provide acquirers</h2>
<table>
<thead><tr><th>Signal</th><th>ChurnZero</th><th>Why it matters</th></tr></thead>
<tbody>
<tr><td>Revenue concentration risk</td><td>❌ Not surfaced</td><td>Health score for each account, but no portfolio-level concentration view</td></tr>
<tr><td>Logo retention vs. dollar retention decomposition</td><td>⚠️ Partial</td><td>Tracks individual accounts but does not decompose the aggregate retention drivers</td></tr>
<tr><td>Annual-plan cliff view</td><td>❌</td><td>No forward-looking renewal concentration analysis</td></tr>
<tr><td>Zombie / inactive paid account detection</td><td>⚠️ Usage-based health</td><td>Shows low-usage accounts but does not frame as acquisition risk</td></tr>
<tr><td>Independent buy-side score</td><td>❌</td><td>Tool is seller-configured; scores reflect seller's priorities</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>ChurnZero is a powerful tool for CS teams actively managing retention. If the target has it, that is a net positive — it means they have visibility into account health. But the health scores reflect the seller's own criteria, not an independent acquisition-risk framework. An acquirer needs to ask: "does this revenue hold together under independent scrutiny, not just under the seller's health model?"</p>

<div class="verdict">
<h3>Verdict</h3>
<p>ChurnZero is a strong CS platform for operators managing retention. For acquirers, use a seller's ChurnZero data for operational context on account health. Use ChurnLens for the independent revenue-quality scoring and risk decomposition needed for a structured deal assessment.</p>
</div>"""
    },
    {
        "slug": "reviews/stripe-sigma-review-for-acquirers",
        "title": "Stripe Sigma Review for SaaS Acquirers: Raw Payment Data vs. Revenue Quality Analysis [2026]",
        "desc": "A review of Stripe Sigma from the perspective of a SaaS acquirer — what its payment data gives you and what it cannot tell you about revenue durability.",
        "breadcrumb": [
            ("ChurnLens", "/"),
            ("Reviews", "/reviews"),
            ("Stripe Sigma Review for SaaS Acquirers", "/reviews/stripe-sigma-review-for-acquirers"),
        ],
        "body": """<p>Stripe Sigma is Stripe's data-querying tool that lets you run custom SQL on your Stripe transaction data. For an acquirer who can get a seller to share Sigma-level access, it offers a raw, unfiltered view of payment activity. But raw payment data is not the same as a revenue-quality assessment — and confusing the two is one of the most common diligence mistakes.</p>

<h2>What Stripe Sigma does well</h2>
<ul class="checklist">
<li><strong>Raw transaction data</strong> — every charge, refund, subscription event, and invoice in SQL-queryable form</li>
<li><strong>Custom queries</strong> — build any report you can imagine from the Stripe data schema</li>
<li><strong>Revenue charting</strong> — MRR, churn, and subscription trends from the source</li>
<li><strong>Data export</strong> — pull any query result into CSV for further analysis</li>
</ul>

<h2>What Stripe Sigma does not give acquirers</h2>
<table>
<thead><tr><th>Signal</th><th>Stripe Sigma</th><th>Acquirer impact</th></tr></thead>
<tbody>
<tr><td>Revenue concentration analysis</td><td>❌ Requires custom SQL</td><td>Sigma gives you the data, but you build the analysis from scratch</td></tr>
<tr><td>Logo-retention decomposition</td><td>❌ Requires custom query</td><td>You define what "retained" means and build the query yourself</td></tr>
<tr><td>Annual-plan cliff projection</td><td>❌ Requires custom SQL</td><td>No prepackaged view of renewal-concentration risk</td></tr>
<tr><td>Benchmarked risk classification</td><td>❌</td><td>No comparison against peer businesses</td></tr>
<tr><td>Deal-memo ready output</td><td>❌</td><td>You get raw data tables, not a structured risk report</td></tr>
</tbody>
</table>

<h2>Our honest assessment</h2>
<p>Stripe Sigma is a powerful raw-data tool — if you know exactly what queries to run and how to interpret the results. The gap is that most acquirers do not know which queries map to deal-killing risks (concentration, cliff, zombie MRR) without a framework. Sigma gives you the ingredients; ChurnLens gives you the recipe and the finished dish.</p>

<div class="callout"><strong>Best practice:</strong> Ask the seller for Stripe Sigma read-only access to validate the raw data. Then run ChurnLens over the same data to get the structured revenue-quality assessment. Sigma for data integrity verification; ChurnLens for risk analysis and deal-memo output.</div>

<div class="verdict">
<h3>Verdict</h3>
<p>Stripe Sigma is excellent for data verification and custom analysis if you have the SQL skills. For deal-ready revenue quality scoring with benchmarking, concentration analysis, and structured output, ChurnLens provides what Sigma leaves as an exercise for the analyst.</p>
</div>"""
    },
]


def main():
    generated = []
    errors = []

    # Generate /compare/ pages
    for page in compare_pages:
        try:
            html = build_index_page_html(
                slug=page["slug"],
                title=page["title"],
                desc=page["desc"],
                body_md=page["body"],
                breadcrumb_items=page["breadcrumb"],
            )
            flat, index = write_page(page["slug"], html)
            generated.append(flat)
            generated.append(index)
            print(f"  ✅ {page['slug']}")
        except Exception as e:
            errors.append(f"  ❌ {page['slug']}: {e}")
            print(f"  ❌ {page['slug']}: {e}")

    # Generate /reviews/ pages
    for page in review_pages:
        try:
            html = build_index_page_html(
                slug=page["slug"],
                title=page["title"],
                desc=page["desc"],
                body_md=page["body"],
                breadcrumb_items=page["breadcrumb"],
            )
            flat, index = write_page(page["slug"], html)
            generated.append(flat)
            generated.append(index)
            print(f"  ✅ {page['slug']}")
        except Exception as e:
            errors.append(f"  ❌ {page['slug']}: {e}")
            print(f"  ❌ {page['slug']}: {e}")

    print(f"\n{'='*50}")
    print(f"Total HTML files generated: {len(generated)}")
    print(f"Unique pages generated: {len(compare_pages) + len(review_pages)}")
    print(f"  /compare/: {len(compare_pages)}")
    print(f"  /reviews/: {len(review_pages)}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  {e}")

    return len(generated), len(compare_pages) + len(review_pages), errors


if __name__ == "__main__":
    main()
